# -*- coding: utf-8 -*-
"""価格の構造モデル

推定（FY2024〜25）: 価格−燃料費の指標 v ＝ γ_{季節,時刻} ＋ c1・τ ＋ c2・τ²（0.01円の時間を除く、HAC）。c2＞0 は供給曲線の凸性
価格: p ＝ v ＋ min(m,0) ＋ α・max(m,0)、m ＝ γ＋c1・τ＋c2・τ²。0.01円になるのは (1) 北海道の需給の余剰の時間、
  (2) 本州側の余剰の時間（過去に東北の価格が0.01円だった時間。本州側の形 γ と同じく過去の値で固定する）
スポット回収の場合は α を火力の粗利の要件から解く。容量回収の場合は α＝1
"""
import numpy as np
import statsmodels.api as sm

from . import params as PR
from . import data as DT
from . import balance as B

FLOOR = PR.FLOOR


def tau_hist():
    """過去の逼迫度（実績の需給、抑制後）。分母は需給の構造モデルと同じ（運転できる火力＋対象外の火力の月×時刻の平均）"""
    C = DT.calib()
    net = C["D"] - C["S"] - C["W"] - C["N"] - C["Hy"] - C["Geo"] - C["Bm"]
    den = np.zeros_like(net)
    for fy in PR.CALIB_FY:
        r = C["fy"] == fy
        I = dict(month=C["month"][r], avail=DT.hjks_availability(C["days"][r], [u[0] for u in PR.UNITS if u[9] is not None]))
        den[r] = B.tau_den(I, B.fleet(fy))
    return net / den


def estimate(maxlags=24, cluster_day=False, linear=False):
    """maxlags: HAC のラグ（時間）。cluster_day: 日をクラスターにした標準誤差（凸性の係数の頑健性の確認）。linear: τ² を入れない（変種）"""
    C = DT.calib()
    tau = tau_hist()
    nf = C["p"] > FLOOR + 0.001
    hs = C["season"] * 24 + C["hour"]
    t = tau.ravel()
    X = np.column_stack([t, np.zeros_like(t) if linear else t ** 2, np.eye(96)[hs.ravel()]])
    if linear:
        X = np.delete(X, 1, axis=1)
    y = (C["p"] - C["v"]).ravel()
    if cluster_day:
        day = np.repeat(np.arange(C["p"].shape[0])[:, None], 24, 1).ravel()
        r = sm.OLS(y[nf.ravel()], X[nf.ravel()]).fit(cov_type="cluster", cov_kwds={"groups": day[nf.ravel()]})
    else:
        r = sm.OLS(y[nf.ravel()], X[nf.ravel()]).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    if linear:
        return dict(c1=float(r.params[0]), c2=0.0, gamma=r.params[1:].reshape(4, 24), t_c1=float(r.tvalues[0]), t_c2=np.nan,
                    n=int(nf.sum()), tau=tau)
    return dict(c1=float(r.params[0]), c2=float(r.params[1]), gamma=r.params[2:].reshape(4, 24), t_c1=float(r.tvalues[0]),
                t_c2=float(r.tvalues[1]), n=int(nf.sum()), tau=tau)


def markup(est, tau, season, hour):
    return est["gamma"][season, hour] + est["c1"] * tau + est["c2"] * tau ** 2


def tight(est, tau):
    """北海道の逼迫の部分 f(τ)＝max(c1・τ＋c2・τ², 0)。上乗せはこの部分にだけ掛ける"""
    return np.maximum(est["c1"] * tau + est["c2"] * tau ** 2, 0.0)


def price(v, m, alpha, floor_mask, theta=-np.inf, f=None, cap=None):
    """p＝v＋m＋(α−1)·f。f を渡さないときは試作の形（正の m 全体に α）。余剰・本州側の余剰の時間は0.01円"""
    if f is None:
        p = v + np.minimum(m, 0.0) + alpha * np.maximum(m, 0.0)
    else:
        p = v + m + (alpha - 1.0) * f
    if cap is not None:
        p = np.minimum(p, cap)
    return np.where(floor_mask | (v + m < theta), FLOOR, np.maximum(p, FLOOR))


def daily_value(p, eta=PR.ETA):
    """1kW の4時間の蓄電池が、各日の最安4時間に充電・最高4時間に放電したときの年の粗利（円/kW-年）。完全予見の上限"""
    s = np.sort(p, 1)
    m = eta * s[:, -4:].sum(1) - s[:, :4].sum(1)
    return np.maximum(m, 0.0)


def strategy_c(p, days, eta=PR.ETA):
    """実行できる戦略（戦略c）: 過去28日の同じ曜日区分（平日・土日）の時刻別の平均価格で充放電の4時間を決め、実際の価格で精算する。
    実績の価格では完全予見の0.833を取る（FY2024〜25）。戻り値は日ごとの粗利（円/kW-日）。最初の28日は完全予見で代用"""
    f = forecast_c(p, days)
    o = np.argsort(f, 1)
    lo, hi = o[:, :4], o[:, -4:]
    val = eta * np.take_along_axis(p, hi, 1).sum(1) - np.take_along_axis(p, lo, 1).sum(1)
    fval = eta * np.take_along_axis(f, hi, 1).sum(1) - np.take_along_axis(f, lo, 1).sum(1)
    out = np.where(fval > 0, val, 0.0)
    out[:28] = daily_value(p[:28], eta)
    return out


def _strategy_c_loop(p, days, eta=PR.ETA):
    """（確認用）元の逐次の実装"""
    wk = np.asarray(days.weekday < 5)
    out = daily_value(p, eta).copy()
    for i in range(28, p.shape[0]):
        same = np.where(wk[i - 28:i] == wk[i])[0] + i - 28
        f = p[same].mean(0)
        o = np.argsort(f)
        val = eta * p[i, o[-4:]].sum() - p[i, o[:4]].sum()
        fval = eta * f[o[-4:]].sum() - f[o[:4]].sum()
        out[i] = val if fval > 0 else 0.0
    return out


def forecast_c(p, days):
    """戦略c の予測: 各日について、過去28日のうち同じ曜日区分（平日・土日）の日の時刻別の平均価格。最初の28日は実際の価格"""
    wk = np.asarray(days.weekday < 5)
    n = p.shape[0]
    f = p.copy()
    cs = {c: np.vstack([np.zeros((1, 24)), np.cumsum(p * (wk == c)[:, None], 0)]) for c in (True, False)}
    cn = {c: np.concatenate([[0], np.cumsum(wk == c)]) for c in (True, False)}
    for c in (True, False):
        idx = np.where((wk == c) & (np.arange(n) >= 28))[0]
        tot = cs[c][idx] - cs[c][idx - 28]
        cnt = (cn[c][idx] - cn[c][idx - 28])[:, None]
        f[idx] = tot / np.maximum(cnt, 1)
    return f


def annual(x_daily, fy):
    return float(np.mean([x_daily[fy == y].sum() for y in np.unique(fy)]))


def gm(R, p, target, days_mask=None, floor_only=False):
    """対象のユニットの粗利（円/年）。R は需給の結果、target はユニットの重み（真偽でもよい。アンモニア混焼の落札分は1未満）。
    floor_only: 0.01円の時間だけの粗利（最低出力で動く損失）"""
    w = np.asarray(target, float)
    x = ((p[:, :, None] - R["vc"]) * R["g"] * w).sum(2)
    if floor_only:
        x = np.where(p <= FLOOR + 0.001, x, 0.0)
    yrs = x.shape[0] / 365.25 if days_mask is None else days_mask.sum() / 365.25
    return float((x if days_mask is None else x[days_mask]).sum() * 1_000 / yrs)


ALPHA_MAX = 40.0


def solve_alpha(v, m, floor_mask, R, target, req, f=None, theta=-np.inf):
    """火力の粗利が要件 req（円/年）に届く α（下限1、上限 ALPHA_MAX）。戻り値: (α, α＝1 での粗利, 不足額, 上限に張り付いたか)。
    f を渡すと上乗せは (α−1)·f、渡さないと試作の形（正の m 全体に α）。target はユニットの重み"""
    w = np.asarray(target, float)
    g = (R["g"] * w).sum(2)
    vg = (R["g"] * R["vc"] * w).sum(2)
    yrs = g.shape[0] / 365.25
    fl = floor_mask | (v + m < theta)
    p1 = np.where(fl, FLOOR, np.maximum(v + m, FLOOR))
    gm1 = ((p1 * g - vg).sum()) * 1_000 / yrs
    if f is None:
        low = np.where(fl, FLOOR, np.maximum(v + np.minimum(m, 0.0), FLOOR))
        pos = np.where(fl, 0.0, np.maximum(m, 0.0))
        base = ((low * g - vg).sum()) * 1_000 / yrs
        slope = (pos * g).sum() * 1_000 / yrs
        a = (req - base) / slope if slope > 0 else ALPHA_MAX
    else:
        slope = (np.where(fl, 0.0, f) * g).sum() * 1_000 / yrs
        a = 1.0 + (req - gm1) / slope if slope > 0 else ALPHA_MAX
    capped = bool(a > ALPHA_MAX)
    a = float(min(max(a, 1.0), ALPHA_MAX))
    return a, gm1, max(req - gm1, 0.0), capped
