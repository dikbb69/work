# -*- coding: utf-8 -*-
"""価格の構造モデル（メリットオーダー＋連系線、著者の決定 2026-10-26。notes/45）

各時間について:
  1. 火力に要る量 q ＝ 需要＋充電−放電 −（原子力・水力・揚水・地熱・バイオマス・対象外の火力・太陽光・風力）。北本は入れない
  2. その日に起動したユニット（日ごとの規則）は「通常時の最低出力」（実績の比）まで動き続ける。マストランは常に起動
  3. 最低出力より上の分と毎日起動停止のユニットを燃料費の安い順に並べる（メリットオーダー）
  4. 連系線: 東北の価格 pT で、東北へは E まで、北海道へは M まで売買できる
     - 北海道の限界の燃料費 ＞ pT なら受電。受電が M に届かなければ価格は pT、届けば北海道の限界の燃料費
     - 北海道の限界の燃料費 ≦ pT なら送電。送電が E に届かなければ価格は pT、届けば北海道の限界の燃料費
     - 通常時の最低出力でも、E まで送っても余るときは、北海道が余る時間: 価格0.01円、火力は技術的な最低出力まで下げ、
       対象外の火力を下げ、残りは太陽光・風力を抑制する（東北も0.01円なら送電0）
  5. 価格は q（需要）と pT から一意に決まる。北本の流れも価格差から決まる
スポット回収の場合: p ＝ p0 ＋ (α−1)·max(p0 − v, 0)（燃料費の指標 v を超える部分に上乗せ。全国で同じ制度の近似なので、東北の価格で決まる時間にも掛ける）
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from . import params as PR
from . import data as DT
from . import balance as B

EPS = 1e-9
NORMAL_MIN_ON = True                                           # 変種（通常時の最低出力なし）で False にする


# ---------------------------------------------------------------- 燃料費の土台（将来）
@lru_cache(None)
def fuel_basis():
    """将来の燃料費: FY2024〜25（較正の期間）の暦月ごとの平均。行は1〜12月"""
    F = DT.fuel()
    F = F[(F.index >= "2024-04-01") & (F.index < "2026-04-01")]
    return F.groupby(F.index.month)[["vc_coal", "vc_lng", "vc_oil", "idx"]].mean()


def unit_vc_future(u, month):
    """将来のユニットの燃料費（日×24）。暦月の土台×ユニットの比"""
    fb = fuel_basis()
    col, base = {"石炭": ("vc_coal", 10.4), "LNG": ("vc_lng", 13.0), "石油": ("vc_oil", 27.8)}[u[1]]
    return fb[col].reindex(range(1, 13)).to_numpy()[month - 1] / base * u[4]


def v_future(month):
    return fuel_basis()["idx"].reindex(range(1, 13)).to_numpy()[month - 1]


def tohoku_future(p_th_hist, v_hist, month, fuel_scale=1.0):
    """東北の価格を、その年の燃料費の指標との差（上乗せ）を保ったまま、将来の燃料費の水準に移す。0.01円の時間は0.01円のまま。
    fuel_scale: 将来の燃料費の土台に掛ける倍率（頑健性）"""
    p = p_th_hist - v_hist + fuel_scale * v_future(month)
    return np.where(p_th_hist <= PR.FLOOR + 0.001, PR.FLOOR, np.maximum(p, PR.FLOOR))


# ---------------------------------------------------------------- 東北の価格の、北海道の再エネとの連動（頑健性の確認 B）
BLOCKS = [(0, 6), (6, 10), (10, 15), (15, 17), (17, 21), (21, 24)]


@lru_cache(None)
def tohoku_comove_coefs():
    """東北の価格が、北海道の太陽光・風力（抑制前、GWh/日）とどれだけ一緒に動くか。日次の回帰（FY2024〜25、時間帯ごと、需要・年月・曜日の固定効果）。
    戻り値: 時刻ごとの (太陽光の係数, 風力の係数)（円/kWh per GWh/日）"""
    import statsmodels.api as sm
    P = DT.panel()
    P = P[P["fy"].isin(PR.CALIB_FY)].copy()
    P["S_pre"] = P["solar"].fillna(0) + P["solar_curt"].fillna(0)
    P["W_pre"] = P["wind"].fillna(0) + P["wind_curt"].fillna(0)
    P["date"] = P.index.normalize()
    h = P.index.hour
    d = P.groupby("date").agg(S=("S_pre", "sum"), W=("W_pre", "sum"), D=("demand", "sum"))
    for c in ("S", "W", "D"):
        d[c] = d[c] / 1e3
    for a, b in BLOCKS:
        d[f"p{a}"] = P[(h >= a) & (h < b)].groupby("date")["p_tohoku"].mean()
    d = d.dropna()
    d["ym"] = d.index.to_period("M").astype(str)
    d["dow"] = d.index.weekday
    X = sm.add_constant(pd.concat([d[["S", "W", "D"]], pd.get_dummies(d[["ym", "dow"]].astype(str), drop_first=True).astype(float)], axis=1))
    out = np.zeros((24, 2))
    for a, b in BLOCKS:
        r = sm.OLS(d[f"p{a}"], X).fit()
        out[a:b, 0], out[a:b, 1] = r.params["S"], r.params["W"]
    return out


# ---------------------------------------------------------------- 通常時の最低出力
@lru_cache(None)
def normal_min_ratio():
    """通常時の最低出力の比（ユニット別）: 東北の価格が燃料費より0.5円以上安いのに動いていた時間（出力制御なし）の、出力÷運転できる容量の分位点（PR.NORMAL_MIN_Q）。
    FY2024〜25。観測が50時間未満のユニットは技術的な最低出力の比"""
    C = DT.calib()
    P = DT.panel()
    names = [u[0] for u in C["units"]]
    acc = {}
    for fy in PR.CALIB_FY:
        I = B.inputs_actual(fy)
        units = B.fleet(fy)
        cap = B.avail_cap(units, I["month"], I)
        months = np.repeat(I["days"].values[:, None], 24, 1).ravel()
        r = C["fy"] == fy
        pT = np.nan_to_num(DT._grid(P["p_tohoku"], I["days"]), nan=10.0)
        curt = I["curt_act"] > 0
        for j, u in enumerate(units):
            if u[0] not in names:
                continue
            g = C["G"][r][:, :, names.index(u[0])]
            vc = DT.unit_vc(u, months).reshape(g.shape)
            sel = (pT < vc - 0.5) & (g > 1.0) & ~curt
            acc.setdefault(u[0], []).extend(list(np.clip(g[sel] / np.maximum(cap[:, :, j][sel], 1.0), 0.0, 1.0)))
    out = {}
    for u in PR.UNITS:
        v = acc.get(u[0], [])
        out[u[0]] = float(np.quantile(v, PR.NORMAL_MIN_Q)) if len(v) >= 50 else u[3] / u[2]
    return out


# ---------------------------------------------------------------- 連系線
def link_caps(year, scenario_share=None):
    """東北へ送れる量 E と北海道へ受けられる量 M（MW）。E ＝ 運用容量（東北向）×比、M ＝ 運用容量（北海道向）"""
    share = PR.LINK_EXPORT_SHARE if scenario_share is None else scenario_share
    east = PR.interp_year(PR.OPCAP_EAST, year)
    west = PR.interp_year(PR.OPCAP_WEST, year)
    E = share * east if share <= 2.0 else share                 # 2 を超える値は MW の固定値
    return float(E), float(west)


# ---------------------------------------------------------------- 起動の判断と給電
def commit(I, units, chg, dis):
    """日ごとの運転台数: その日の火力に要る量（北本なし）の最大×1.02＋最大機−予備力の外部の分を満たすまで、マストラン→燃料費の順に起動"""
    nd = I["D"].shape[0]
    cap = B.avail_cap(units, I["month"], I)
    must = np.array([u[6] for u in units])
    dss = np.array([u[5] for u in units])
    O = B.other_profile()[I["month"], np.arange(24)[None, :]]
    fixed = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O + I["pump"]
    T_req = I["D"] + chg - dis - fixed - I["S"] - I["W"]
    need = T_req.max(1) * (1 + PR.COMMIT_RESERVE["margin"]) + I["largest"].max(1) - PR.COMMIT_RESERVE["credit"]
    on = np.zeros((nd, len(units)), bool)
    on[:, must] = True
    have = cap[:, :, must].max(1).sum(1) + (cap[:, :, dss].max(1).sum(1) if dss.any() else 0.0)
    rest = need - have
    for i in [i for i in np.argsort([u[4] for u in units]) if not must[i] and not dss[i]]:
        add = rest > 0
        on[add, i] = True
        rest = rest - np.where(add, cap[:, :, i].max(1), 0.0)
    return on, cap


def dispatch(I, units, chg=None, dis=None, link=None):
    """需給と基準の価格 p0（α＝1）を解く。link＝(E, M)。戻り値は需給の構造モデルと同じ形の辞書"""
    nd = I["D"].shape[0]
    n = nd * 24
    chg = np.zeros((nd, 24)) if chg is None else chg
    dis = np.zeros((nd, 24)) if dis is None else dis
    E, M = link if link is not None else I["link"]
    E = np.broadcast_to(np.asarray(E, float), (nd, 24)).ravel()
    on, cap = commit(I, units, chg, dis)
    nu = len(units)
    dss = np.array([u[5] for u in units])
    tmin_u = np.array([u[3] for u in units], float)
    nr = normal_min_ratio()
    nmin_r = np.array([max(nr.get(u[0], u[3] / u[2]), u[3] / u[2]) if NORMAL_MIN_ON else u[3] / u[2] for u in units])
    live = on[:, None, :] & ~dss[None, None, :]
    tmin = np.where(live, np.minimum(tmin_u[None, None, :], cap), 0.0)
    nmin = np.where(live, np.minimum(np.maximum(nmin_r[None, None, :] * cap, tmin), cap), 0.0)
    head = np.where(on[:, None, :], cap - nmin, 0.0)
    head = np.where(dss[None, None, :], cap, head)
    vc = I["vc_fn"](units)
    O = B.other_profile()[I["month"], np.arange(24)[None, :]]
    O_low = np.minimum(O, B.other_floor_min()[I["month"]])
    fixed = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O + I["pump"]
    q = (I["D"] + chg - dis - fixed - I["S"] - I["W"]).ravel()
    pT = I["pT"].ravel()
    th_floor = pT <= PR.FLOOR + 0.001
    Gn = nmin.sum(2).ravel()
    Gt = tmin.sum(2).ravel()
    qf = q - Gn
    hf = head.reshape(n, nu)
    vf = vc.reshape(n, nu)
    o = np.argsort(vf, 1)
    hs = np.take_along_axis(hf, o, 1)
    vs = np.take_along_axis(vf, o, 1)
    cs = hs.cumsum(1)
    tot = cs[:, -1]

    def mc(x):
        idx = (cs < x[:, None] - 1e-9).sum(1)
        out = np.where(idx >= nu, PR.PRICE_CAP, vs[np.arange(n), np.minimum(idx, nu - 1)])
        return np.where(x <= EPS, PR.FLOOR, out)
    below = np.where(th_floor, 0.0, np.where(vs <= pT[:, None], cs, 0.0).max(1))
    Ee = np.where(th_floor, 0.0, E)
    need_imp = qf > below
    imp = np.where(need_imp, np.minimum(M, qf - below), 0.0)
    exp = np.where(~need_imp, np.minimum(Ee, below - qf), 0.0)
    F = np.where(need_imp, qf - imp, qf + exp)                 # 最低出力より上の火力
    p0 = np.where(need_imp, np.where(qf - below <= M + EPS, pT, mc(F)), np.where(below - qf <= Ee + EPS, pT, np.maximum(mc(F), PR.FLOOR)))
    p0 = np.where(th_floor & ~need_imp, PR.FLOOR, p0)
    short = np.maximum(F - tot, 0.0)
    F = np.minimum(F, tot)
    # 北海道が余る時間（通常時の最低出力でも、送れるだけ送っても余る）
    sur = qf + Ee < -EPS
    exp = np.where(sur, Ee, exp)
    imp = np.where(sur, 0.0, imp)
    F = np.where(sur, 0.0, F)
    rem = np.where(sur, q + Ee - Gt, 0.0)                      # 技術的な最低出力まで下げた後の不足（正）か余り（負）
    mins = np.where(sur.reshape(nd, 24)[:, :, None], tmin, nmin)
    thermal_extra = np.where(sur, np.maximum(rem, 0.0), 0.0)   # 技術的な最低出力より上で動く分（余りを吸収しきれた場合）
    excess = np.where(sur, np.maximum(-rem, 0.0), 0.0)
    Ored = np.minimum((O - O_low).ravel(), excess)
    excess = excess - Ored
    flex_vre = ((I["S"] - I["U"]) + I["W"]).ravel()
    curt = np.minimum(excess, flex_vre)
    unabs = excess - curt
    # 価格: 太陽光・風力の抑制が要る時間だけ0.01円。余りを技術的な最低出力と対象外の火力で吸収できる時間は、
    # 東北へ送れるだけ送って北海道が切り離されているので、運転中の最も安い火力の燃料費（東北も0.01円なら0.01円）
    vmin_on = np.where(on[:, None, :] & ~dss[None, None, :], vc, np.inf).min(2).ravel()
    band = sur & (curt + unabs <= EPS)
    p0 = np.where(sur, np.where(band & ~th_floor, np.where(np.isfinite(vmin_on), np.minimum(vmin_on, pT), PR.FLOOR), PR.FLOOR), p0)
    # ユニット別の出力: 最低出力＋（燃料費の順に）上の分
    add_total = np.where(sur, thermal_extra, F)
    gadd = np.zeros((n, nu))
    rem_t = add_total.copy()
    head_s = np.where(sur[:, None], (np.where(on[:, None, :], cap - tmin, 0.0)).reshape(n, nu), hf)
    hs2 = np.take_along_axis(head_s, o, 1)
    for k in range(nu):
        qk = np.minimum(hs2[:, k], rem_t)
        np.put_along_axis(gadd, o[:, k:k + 1], qk[:, None], 1)
        rem_t = rem_t - qk
    g = mins + gadd.reshape(nd, 24, nu)
    X = (exp - imp).reshape(nd, 24)
    O_out = O - Ored.reshape(nd, 24)
    fixed_out = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O_out + I["pump"]
    supply = fixed_out + I["S"] + I["W"] - curt.reshape(nd, 24) + g.sum(2) + dis
    use = I["D"] + X + chg + unabs.reshape(nd, 24)
    hk_sets = ((need_imp & (qf - below > M + EPS)) | (~need_imp & (below - qf > Ee + EPS))) & ~sur
    return dict(on=on, g=g, vc=vc, other_out=O_out, curt=curt.reshape(nd, 24), unabs=unabs.reshape(nd, 24), surplus=sur.reshape(nd, 24),
                X=X, X_incr=np.zeros((nd, 24)), short=short.reshape(nd, 24), p0=p0.reshape(nd, 24), hk_sets=hk_sets.reshape(nd, 24),
                residual_check=(supply + short.reshape(nd, 24) - use), units=units, gmin=mins, link=(E, M), pT=I["pT"])


def tight(p0, v):
    """上乗せを掛ける部分: 燃料費の指標を超える部分（0.01円の時間は0）"""
    return np.where(p0 <= PR.FLOOR + 0.001, 0.0, np.maximum(p0 - v, 0.0))


# ---------------------------------------------------------------- 入力の準備
def _vc_actual(I):
    months = np.repeat(I["days"].values[:, None], 24, 1).ravel()
    nd = I["D"].shape[0]
    return lambda units: np.stack([DT.unit_vc(u, months).reshape(nd, 24) for u in units], 2)


def _vc_future(I, fuel_scale=1.0):
    return lambda units: fuel_scale * np.stack([unit_vc_future(u, I["month"]) for u in units], 2)


def inputs_actual(fy, share=None):
    """実績の年度（検証用）: 燃料費・東北の価格は実績。連系線は運用容量（東北向は月別、FY2025 の6〜11月は900MW）×比、北海道向900MW"""
    I = B.inputs_actual(fy)
    P = DT.panel()
    I["pT"] = np.nan_to_num(DT._grid(P["p_tohoku"], I["days"]), nan=float(np.nanmean(DT._grid(P["p_tohoku"], I["days"]))))
    I["vc_fn"] = _vc_actual(I)
    opcap = I["exp_full"] + 300.0                                # 運用容量（東北向）
    sh = PR.LINK_EXPORT_SHARE if share is None else share
    E = sh * opcap if sh <= 2.0 else np.full_like(opcap, sh)
    I["link"] = (E, float(PR.OPCAP_WEST[min(PR.OPCAP_WEST)]))
    return I


def inputs_future(sc_y, sc=None, pT_shift=0.0, fuel_scale=1.0):
    """将来: 気象年の形に、その年の需要・設備を当てる。燃料費は FY2024〜25 の暦月の平均（fuel_scale 倍）、東北の価格はその土台に移す"""
    I = B.inputs_future(sc_y)
    W = DT.weather()
    v_hist = I["v"]
    I["v"] = fuel_scale * v_future(I["month"])
    pT = tohoku_future(W["p_th"], v_hist, I["month"], fuel_scale)
    sc = sc or {}
    if sc.get("tohoku_comove"):                                 # 頑健性の確認 B: 北海道の太陽光・風力の増分に合わせて東北の価格も動く
        cf = tohoku_comove_coefs()
        dS = (I["S"].sum(1) - W["S_pre"].sum(1)) / 1e3
        dW = (I["W"].sum(1) - W["W_pre"].sum(1)) / 1e3
        pT = np.where(pT <= PR.FLOOR + 0.001, pT, np.maximum(pT + cf[None, :, 0] * dS[:, None] + cf[None, :, 1] * dW[:, None], PR.FLOOR))
    I["pT"] = np.where(pT <= PR.FLOOR + 0.001, pT, np.maximum(pT + pT_shift, PR.FLOOR))
    I["vc_fn"] = _vc_future(I, fuel_scale)
    y = sc_y["year"] if sc.get("link_upgrade", sc.get("export_increment", True)) else min(sc_y["year"], 2027)
    I["link"] = link_caps(y, sc.get("link_share"))
    return I


def make_whole(R, p, w):
    """運転の赤字の補填（円/年）: ユニットごとに、その日の（燃料費−価格）×出力の合計が正なら、その額を市場の外で補填する（米国の市場のメイクホール支払いに近い）"""
    x = ((R["vc"] - p[:, :, None]) * R["g"] * w).sum(1)        # 日×ユニット
    yrs = x.shape[0] / 365.25
    return float(np.maximum(x, 0.0).sum() * 1_000 / yrs)


def solve_alpha_mw(p0, f, R, w, req, iters=8):
    """運転の赤字は補填する前提で、対象の火力の「スポットの粗利＋補填」が要件に届く α を解く。
    粗利は α について線形、補填は価格が上がると減るので、繰り返しで解く。戻り値: (α, α＝1 の粗利, 固定費の不足額, 上限に張り付いたか, α＝1 の補填, その α での補填)"""
    g = (R["g"] * w).sum(2)
    vg = (R["g"] * R["vc"] * w).sum(2)
    yrs = g.shape[0] / 365.25
    gm1 = ((p0 * g - vg).sum()) * 1_000 / yrs
    slope = (f * g).sum() * 1_000 / yrs
    mw1 = make_whole(R, p0, w)
    a, mw = 1.0, mw1
    for _ in range(iters):
        a_new = 1.0 + (req - gm1 - mw) / slope if slope > 0 else ALPHA_MAX
        a_new = float(min(max(a_new, 1.0), ALPHA_MAX))
        mw = make_whole(R, price(p0, f, a_new), w)
        if abs(a_new - a) < 1e-4:
            a = a_new
            break
        a = a_new
    capped = bool(a >= ALPHA_MAX - 1e-9)
    return a, gm1, max(req - gm1 - mw1, 0.0), capped, mw1, mw


def solve_alpha(p0, f, R, w, req):
    """対象の火力の粗利が要件 req（円/年）に届く α（下限1、上限 ALPHA_MAX）。p ＝ p0 ＋ (α−1)·f。戻り値: (α, α＝1 の粗利, 不足額, 上限に張り付いたか)"""
    g = (R["g"] * w).sum(2)
    vg = (R["g"] * R["vc"] * w).sum(2)
    yrs = g.shape[0] / 365.25
    gm1 = ((p0 * g - vg).sum()) * 1_000 / yrs
    slope = (f * g).sum() * 1_000 / yrs
    a = 1.0 + (req - gm1) / slope if slope > 0 else ALPHA_MAX
    capped = bool(a > ALPHA_MAX)
    return float(min(max(a, 1.0), ALPHA_MAX)), gm1, max(req - gm1, 0.0), capped


ALPHA_MAX = 40.0


def price(p0, f, alpha):
    return np.where(p0 <= PR.FLOOR + 0.001, PR.FLOOR, np.minimum(p0 + (alpha - 1.0) * f, PR.PRICE_CAP))


# ---------------------------------------------------------------- 運転の赤字もスポットで回収する場合（足元の慣行）と、入札での回収
def gm(R, p, w):
    """対象の火力のスポットの粗利（円/年、運転の赤字を差し引いた正味）"""
    yrs = p.shape[0] / 365.25
    return float(((p[:, :, None] - R["vc"]) * R["g"] * w).sum() * 1_000 / yrs)


def solve_alpha_gm(p0, f, R, w, target, iters=50):
    """運転の赤字も上乗せで回収する前提で、対象の火力のスポットの正味の粗利が target（円/年）に届く α を解く（上限価格を入れて二分法）。
    戻り値: (α, 上限に張り付いたか)"""
    if gm(R, p0, w) >= target:
        return 1.0, False
    if gm(R, price(p0, f, ALPHA_MAX), w) < target:
        return ALPHA_MAX, True
    lo, hi = 1.0, ALPHA_MAX
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if gm(R, price(p0, f, mid), w) >= target else (mid, hi)
    return hi, False


def bid_room(R):
    """北海道の火力だけが入札に上乗せするとき、価格を上げられる時間と、その天井。
    上乗せするのは、北海道の火力が稼げる時間（北海道が余らず、最低出力より上の火力が出力を上げ下げして価格を決める時間）だけ。
    北海道が余る時間（0.01円の時間と、火力を最低出力より下げて吸収する時間）は、火力は事前に稼げないとわかっているので上乗せしない。
    東北の価格より高く入札すると北本からの受電に置き換わるので、上乗せは東北の価格まで（北海道が東北より安い時間だけ上げられる）。
    燃料費が東北の価格を超える火力は燃料費で入札する（受電が満杯で北海道が東北より高い時間にも上乗せしない）。東北と同じ価格の時間は上げられない"""
    p0, pT = R["p0"], R["pT"]
    below = (p0 > PR.FLOOR + 0.001) & ~R["surplus"] & (p0 < pT - 1e-6)
    return below, np.where(below, pT, p0)


def bid_price(p0, room, ceil, m):
    """入札に1kWh あたり m 円（日×24 の配列か数）を上乗せしたときの価格。どの電源が動くかと北本の流れは変わらない（入札が天井を超えないため）"""
    return np.where(room, np.minimum(p0 + m, ceil), p0)


def daily_loss(R, p, w):
    """日ごとの運転の赤字（ユニットごとに、その日の（燃料費−価格）×出力の合計の正の部分。単位は粗利と同じ）"""
    x = ((R["vc"] - p[:, :, None]) * R["g"] * w).sum(1)
    return np.maximum(x, 0.0).sum(1)


def _daily_markup(p0, room, ceil, G, L, md_max, iters=40):
    """日ごとに、その日の稼げる時間に一律 m_d を上乗せして増える粗利が L_d に届く m_d（二分法、日ごとに並べて解く）。
    m_d の上限は、その日の稼げる時間をすべて東北の価格まで上げる幅（md_max）。届かない日はその上限"""
    lo, hi = np.zeros(len(L)), md_max.copy()
    gain = lambda m: ((bid_price(p0, room, ceil, m[:, None]) - p0) * G).sum(1)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        ok = gain(mid) >= L
        lo, hi = np.where(ok, lo, mid), np.where(ok, mid, hi)
    return np.where(L <= 1e-9, 0.0, np.where(gain(md_max) < L, md_max, hi))


def solve_bid(R, w, target, losses_outside):
    """北海道の火力だけが、入札への上乗せで回収する（東北の価格は動かない）。回収の規則:
      - 運転の赤字（losses_outside が False のとき）: 前日に翌日の余剰の時間がわかる前提で、その日の赤字を、その日の稼げる時間に1kWh あたり一律に上乗せする
      - 残り（固定費の不足）: 年でならして、稼げる時間に1kWh あたり一律 μ を上乗せする
    target は、losses_outside が True なら「スポットの粗利＋補填」、False なら「スポットの正味の粗利」の要件（円/年）。
    戻り値: (価格, 情報の辞書: μ（天井に張り付いたときは空欄）, 天井に張り付いたか, 上乗せの平均, 回収しきれない額, 運転の赤字の分の比 θ)"""
    p0 = R["p0"]
    room, ceil = bid_room(R)
    G = (R["g"] * w).sum(2)
    gap = np.where(room, ceil - p0, 0.0)                        # 東北の価格までの幅。上乗せはこれを超えない
    md_max, mu_max = gap.max(1), float(gap.max()) if room.any() else 0.0
    rev = (lambda p: gm(R, p, w) + make_whole(R, p, w)) if losses_outside else (lambda p: gm(R, p, w))
    md = np.zeros(p0.shape[0])
    if not losses_outside:                                      # 前日にわかる、その日の（基準の価格での）赤字を、その日の稼げる時間に一律に上乗せして回収する
        md = _daily_markup(p0, room, ceil, G, daily_loss(R, p0, w), md_max)
    price_at = lambda th, mu: bid_price(p0, room, ceil, th * md[:, None] + mu)
    theta, mu, at_ceiling = (0.0 if losses_outside else 1.0), 0.0, False
    r0 = rev(price_at(theta, 0.0))
    if r0 >= target:                                            # 赤字の分だけで要件を超える（または上乗せが要らない）: 赤字の分を θ＜1 に縮める
        if not losses_outside and rev(price_at(0.0, 0.0)) < target:
            lo, hi = 0.0, 1.0
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                lo, hi = (lo, mid) if rev(price_at(mid, 0.0)) >= target else (mid, hi)
            theta = hi
        elif not losses_outside:
            theta = 0.0
    else:
        if rev(price_at(theta, mu_max)) < target:              # 稼げる時間をすべて東北の価格まで上げても届かない
            mu, at_ceiling = mu_max, True
        else:
            lo, hi = 0.0, mu_max
            for _ in range(50):
                mid = 0.5 * (lo + hi)
                lo, hi = (lo, mid) if rev(price_at(theta, mid)) >= target else (mid, hi)
            mu = hi
    p = price_at(theta, mu)
    yrs = p0.shape[0] / 365.25
    sel = room & (G > 0)
    info = {"mu": float("nan") if at_ceiling else float(mu), "at_ceiling": at_ceiling, "theta": float(theta), "unrecovered": max(target - rev(p), 0.0),
            "markup_avg": float(((p - p0) * G)[sel].sum() / max(G[sel].sum(), 1e-9)),
            "room_hours": float(room.sum() / yrs), "headroom": float((gap * G).sum() * 1_000 / yrs)}
    return p, info
