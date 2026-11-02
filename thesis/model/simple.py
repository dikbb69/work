# -*- coding: utf-8 -*-
"""簡素版のモデル（著者の決定 2026-10-27）: 次の4段だけで組む

① コマごとの価格はメリットオーダーで決まる。運転の制約は2つ:
   - マストラン3台（石狩湾新港1・苫東厚真4・知内2）は常に起動する（北電NW の運用ルール。知内2 は北本の他励式のための道南の同期発電機。notes/51）
   - 毎日、その日の火力に要る量の最大＋予備力を満たすまで、ほかの号機を燃料費の安い順に起動し、起動した号機はその日は通常時の最低出力より
     下げない（充電のためだけには起動しない）
   東北とは連系線の範囲で東北の価格で売買する（連系線・東北の価格・最低出力・予備力の置き方は今のモデルと同じ）。
   頑健性: マストランなし、マストラン2台（知内2 を外す）、運転の制約もなし
② 火力の入札＝燃料費に1kWh あたり一律の上乗せ μ を足したもの（著者の決定 2026-10-27）。発電事業者は、年間で回収できない固定費と
   運転の赤字を、年間の約定量（完全予見）で割った額を入札に足す。北海道電力の火力全体で1つの額とし、0.01円の時間を除くすべての
   約定コマに乗せる。全国の火力が同じ考え方で入札するので、東北の価格にも同じ額が乗る。燃料費の順番は変わらないので、どの号機が
   動くかは μ によらない。マストランの運転の赤字（価格が燃料費を下回る時間も動く分）も、最終需要家が負担するものとしてスポットの
   上乗せで回収する（著者の決定 2026-10-27）。
   頑健性: 比例の上乗せ（燃料費の指標 v を超える部分に同じ比率 α、入札＝v＋α×(燃料費−v)）、赤字はスポットの外で精算する
   （日ごとの赤字を補填し、上乗せは固定費の不足だけ）
③ 必要な収入＝足元（FY2024〜25）の1kW あたりのスポットの粗利＋容量収入。将来の容量収入を引いた残りを、残っている火力全体で
   スポットから得るように α を決める（LTDA の火力は契約で固定費を回収するので対象外）
④ 1年間（3つの気象年のどれでも）一度も動かない（起動しない）号機は退出する。動かない号機は需給に効かないので、
   退出が変えるのは③の対象だけ（LTDA の火力は契約で残る。マストランは毎日動くので退出しない）
"""
from functools import lru_cache

import numpy as np
import pandas as pd

from . import params as PR
from . import data as DT
from . import balance as B
from . import price as PZ
from . import calibrate as CB
from . import merit as MO
from . import battery as BT

EPS = 1e-9
P_SCHED = 14_972.0                                             # 蓄電池の充放電の時間を決める価格の容量価格（主）
MUSTRUN = PR.SIMPLE_MUSTRUN                                    # マストラン（主）
SHAPE = PR.SIMPLE_SHAPE                                        # 上乗せの形（主は一律の額）
K_GRID = np.array(list(range(0, 101, 5)) + list(range(110, 301, 10)) + list(range(325, 801, 25)), float)   # 蓄電池の量の格子（万kW）


def k_step(K):
    """蓄電池を増やす刻み（万kW）: 100万kW までは1、400万kW までは5、その先は10"""
    return 1.0 if K < 100 - 1e-9 else (5.0 if K < 400 - 1e-9 else 10.0)


def commit(I, units, chg, dis):
    """日ごとの起動: マストランは常に起動し、その日の火力に要る量（北本なし）の最大×1.02＋最大機−予備力の外部の分を満たすまで、
    ほかの号機を燃料費の安い順に起動する（毎日起動停止できる号機も燃料費の順に数える）。
    要る量には蓄電池の放電は入れ、充電は入れない（充電のためだけに火力を起動しない。入れると、大量の蓄電池が夜に一斉に充電して
    石油火力まで起動し、その損失を上乗せで回収する不自然な動きが出る）"""
    nd = I["D"].shape[0]
    cap = B.avail_cap(units, I["month"], I)
    O = B.other_profile()[I["month"], np.arange(24)[None, :]]
    fixed = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O + I["pump"]
    need = (I["D"] - dis - fixed - I["S"] - I["W"]).max(1) * (1 + PR.COMMIT_RESERVE["margin"]) + I["largest"].max(1) - PR.COMMIT_RESERVE["credit"]
    must = np.array([bool(u[6]) for u in units])
    on = np.zeros((nd, len(units)), bool)
    on[:, must] = True
    rest = need - (cap[:, :, must].max(1).sum(1) if must.any() else 0.0)
    for i in np.argsort([u[4] for u in units], kind="stable"):
        if must[i]:
            continue
        add = rest > 0
        on[add, i] = True
        rest = rest - np.where(add, cap[:, :, i].max(1), 0.0)
    return on, cap


def with_mustrun(units, mustrun=None):
    """マストランの印を付け直す（mustrun: 号機の名前のタプル。None なら主の3台）"""
    mr = MUSTRUN if mustrun is None else tuple(mustrun)
    return [tuple(list(u[:6]) + [u[0] in mr] + list(u[7:])) for u in units]


def dispatch(I, units, chg=None, dis=None, link=None, mode="commit", mustrun=None, commit_fn=None):
    """需給と基準の価格 p0（α＝1）。mode: 'commit'（主、マストランと日ごとの起動と通常時の最低出力）、'pure'（頑健性、運転の制約なし）。
    commit_fn: 日ごとの起動の規則（None なら commit）"""
    if mode == "commit":
        return MO.dispatch(I, with_mustrun(units, mustrun), chg, dis, link, commit_fn=commit_fn or commit)
    return _merit(I, units, np.zeros((I["D"].shape[0], 24, len(units))), chg, dis, link)


def _merit(I, units, gmin, chg=None, dis=None, link=None):
    """最低出力 gmin を先に置いたメリットオーダー（頑健性の版は gmin＝0）"""
    nd = I["D"].shape[0]
    n = nd * 24
    chg = np.zeros((nd, 24)) if chg is None else chg
    dis = np.zeros((nd, 24)) if dis is None else dis
    E, M = link if link is not None else I["link"]
    E = np.broadcast_to(np.asarray(E, float), (nd, 24)).ravel()
    nu = len(units)
    cap = B.avail_cap(units, I["month"], I)
    vc = I["vc_fn"](units)
    O = B.other_profile()[I["month"], np.arange(24)[None, :]]
    O_low = np.minimum(O, B.other_floor_min()[I["month"]])
    fixed = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O + I["pump"]
    q = (I["D"] + chg - dis - fixed - I["S"] - I["W"] - gmin.sum(2)).ravel()   # 最低出力より上の火力と北本で埋める量
    pT = I["pT"].ravel()
    th_floor = pT <= PR.FLOOR + 0.001
    hf = (cap - gmin).reshape(n, nu)
    vf = vc.reshape(n, nu)
    o = np.argsort(vf, 1, kind="stable")
    hs = np.take_along_axis(hf, o, 1)
    vs = np.take_along_axis(vf, o, 1)
    cs = hs.cumsum(1)
    tot = cs[:, -1]

    def mc(x):
        idx = (cs < x[:, None] - 1e-9).sum(1)
        out = np.where(idx >= nu, PR.PRICE_CAP, vs[np.arange(n), np.minimum(idx, nu - 1)])
        return np.where(x <= EPS, PR.FLOOR, out)
    below = np.where(th_floor, 0.0, np.where(vs <= pT[:, None], cs, 0.0).max(1))   # 東北の価格以下の火力
    Ee = np.where(th_floor, 0.0, E)
    need_imp = q > below
    imp = np.where(need_imp, np.minimum(M, q - below), 0.0)
    exp = np.where(~need_imp, np.minimum(Ee, below - q), 0.0)
    F = np.where(need_imp, q - imp, q + exp)
    p0 = np.where(need_imp, np.where(q - below <= M + EPS, pT, mc(F)), np.where(below - q <= Ee + EPS, pT, np.maximum(mc(F), PR.FLOOR)))
    p0 = np.where(th_floor & ~need_imp, PR.FLOOR, p0)
    short = np.maximum(F - tot, 0.0)
    F = np.minimum(np.maximum(F, 0.0), tot)
    # 北海道が余る時間（送れるだけ送っても余る）: 対象外の火力を下げられない分まで下げ、残りは太陽光・風力を抑制する。価格は0.01円
    # （最低出力で動く号機があり、抑制まではいかない時間は、その号機の燃料費か東北の価格の低い方）
    sur = q + Ee < -EPS
    vmin_on = np.where(gmin > 0, vc, np.inf).min(2).ravel()
    p_band = np.where(np.isfinite(vmin_on), np.minimum(vmin_on, np.where(th_floor, np.inf, pT)), PR.FLOOR)
    exp = np.where(sur, Ee, exp)
    imp = np.where(sur, 0.0, imp)
    F = np.where(sur, 0.0, F)
    excess = np.where(sur, -(q + Ee), 0.0)
    Ored = np.minimum((O - O_low).ravel(), excess)
    excess = excess - Ored
    curt = np.minimum(excess, ((I["S"] - I["U"]) + I["W"]).ravel())
    unabs = excess - curt
    p0 = np.where(sur, np.where((curt + unabs <= EPS) & ~th_floor, p_band, PR.FLOOR), p0)
    g = np.zeros((n, nu))
    rem = F.copy()
    for k in range(nu):
        qk = np.minimum(hs[:, k], rem)
        np.put_along_axis(g, o[:, k:k + 1], qk[:, None], 1)
        rem = rem - qk
    g = g.reshape(nd, 24, nu) + gmin
    X = (exp - imp).reshape(nd, 24)
    O_out = O - Ored.reshape(nd, 24)
    supply = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O_out + I["pump"] + I["S"] + I["W"] - curt.reshape(nd, 24) + g.sum(2) + dis
    use = I["D"] + X + chg + unabs.reshape(nd, 24)
    return dict(g=g, vc=vc, cap=cap, gmin=gmin, other_out=O_out, curt=curt.reshape(nd, 24), unabs=unabs.reshape(nd, 24),
                surplus=sur.reshape(nd, 24), X=X, short=short.reshape(nd, 24), p0=p0.reshape(nd, 24), pT=I["pT"], units=units,
                residual_check=supply + short.reshape(nd, 24) - use)


@lru_cache(None)
def calibration(mode="commit", mustrun=None):
    """FY2024〜25: 粗利の換算比 k（モデルの粗利÷実績の粗利、過去のユニット）と当てはまり。実行できる比と足元の粗利は今の較正と同じ（実績の価格から）"""
    base = CB.calibration(0.0)
    C = DT.calib()
    hist = [u[0] for u in C["units"]]
    gm_mod, fit = {}, {}
    for fy in PR.CALIB_FY:
        I = MO.inputs_actual(fy)
        R = dispatch(I, B.fleet(fy), mode=mode, mustrun=mustrun)
        p, pa = R["p0"], I["p_act"]
        gm_mod[fy] = PZ.gm(R, p, np.array([u[0] in hist for u in R["units"]]))
        ok = ~np.isnan(pa)
        a, b = pa[ok], p[ok]
        spread = lambda x: float(np.nanmean(np.sort(x, 1)[:, -4:].mean(1) - np.sort(x, 1)[:, :4].mean(1)))
        fit[fy] = {"R²": 1 - ((a - b) ** 2).sum() / ((a - a.mean()) ** 2).sum(), "MAE": float(np.abs(a - b).mean()),
                   "平均 実績": float(a.mean()), "平均 モデル": float(b.mean()),
                   "0.01円の時間 実績": int((pa <= PR.FLOOR + 0.001).sum()), "0.01円の時間 モデル": int((p <= PR.FLOOR + 0.001).sum()),
                   "日の値幅 実績": spread(pa), "日の値幅 モデル": spread(p),
                   "完全予見の粗利 実績": float(PZ.daily_value(np.nan_to_num(pa, nan=float(np.nanmean(pa)))).sum()),
                   "完全予見の粗利 モデル": float(PZ.daily_value(p).sum()),
                   "抑制(GWh) 実績": float(I["curt_act"].sum() / 1e3), "抑制(GWh) モデル": float(R["curt"].sum() / 1e3),
                   "火力の粗利(億円) 実績": base["gm_act"][fy] / 1e8, "火力の粗利(億円) モデル": gm_mod[fy] / 1e8}
    k = np.mean(list(gm_mod.values())) / np.mean(list(base["gm_act"].values()))
    return dict(base, k=float(k), gm_mod=gm_mod, fit=fit, mode=mode, mustrun=mustrun)


def requirement(cal, year, P, w, units, req_scale=1.0):
    """残っている火力全体のスポットの粗利の要件（円/年）。1kW あたりの要件（③）×対象の火力（MW）"""
    cap = float(sum(u[2] * x for u, x in zip(units, w)))
    return CB.spot_requirement_per_kw(cal, year, P, req_scale=req_scale) * cap * 1_000, cap


def solve_price(R, I, cal, P, w, standard=False, req_scale=1.0, losses="spot", shape=None, fixed=None):
    """② の上乗せと価格。standard: 一般的な方法（燃料費で入札、上乗せなし）。
    shape: 'flat'（主、0.01円の時間を除く約定コマに1kWh あたり一律の μ）、'prop'（頑健性、燃料費の指標を超える部分に比率 α）。
    losses: 'spot'（主、運転の赤字もスポットの上乗せで回収）、'outside'（頑健性、日ごとの赤字は市場の外で補填し、上乗せは固定費の不足だけ）。
    どの号機が動くかは上乗せによらないので、粗利は上乗せについて線形（上限価格にかからなければ解は閉じた形）。
    fixed: (印, 価格) 蓄電池が値を決める時間（BT.battery_set_prices）。その時間の価格は蓄電池の入札で、上乗せを足さない"""
    shape = shape or SHAPE
    if shape == "flat":
        return _solve_flat(R, I, cal, P, w, standard, req_scale, losses, fixed)
    p0 = R["p0"]
    f = MO.tight(p0, I["v"])
    if fixed is not None:
        p0, f = np.where(fixed[0], fixed[1], p0), np.where(fixed[0], 0.0, f)
    req, cap = requirement(cal, I["year"], P, w, R["units"], req_scale)
    gm1 = MO.gm(R, p0, w)
    a, capped, mw = 1.0, False, 0.0
    if losses == "outside":
        if not standard:
            a, gm1, _, capped, _, mw = MO.solve_alpha_mw(p0, f, R, w, req)
        else:
            mw = MO.make_whole(R, p0, w)
        p = MO.price(p0, f, a)
        return p, dict(α=a, μ=np.nan, capped=capped, req=req, gm1=gm1, gm=MO.gm(R, p, w), cap=cap, mw=mw)
    if not standard and gm1 < req:
        g = (R["g"] * w).sum(2)
        slope = float((f * g).sum() * 1_000 / (p0.shape[0] / 365.25))
        a = 1.0 + (req - gm1) / slope if slope > 0 else MO.ALPHA_MAX
        if a > MO.ALPHA_MAX or (p0 + (a - 1.0) * f).max() > PR.PRICE_CAP:
            a, capped = MO.solve_alpha_gm(p0, f, R, w, req)
    p = MO.price(p0, f, a)
    return p, dict(α=a, μ=np.nan, capped=capped, req=req, gm1=gm1, gm=MO.gm(R, p, w), cap=cap, mw=mw)


def _solve_flat(R, I, cal, P, w, standard=False, req_scale=1.0, losses="spot", fixed=None):
    """一律の上乗せ μ（円/kWh）: 要件に届かない額（固定費の不足と運転の赤字）÷ 0.01円の時間を除く対象の火力の約定量（完全予見）。
    fixed: 蓄電池が値を決める時間の (印, 価格)。その時間は上乗せを足さない"""
    p0 = R["p0"] if fixed is None else np.where(fixed[0], fixed[1], R["p0"])
    req, cap = requirement(cal, I["year"], P, w, R["units"], req_scale)
    gm1 = MO.gm(R, p0, w)
    on = (p0 > PR.FLOOR + 0.001) & (True if fixed is None else ~fixed[0])
    off = not I.get("mu_tohoku", True)
    if off:                                                     # 感応度（notes/38 §3 (b)）: 東北の価格に μ を足さない（全国の火力は上乗せしない）。
        pT = I["pT"]                                            # 北海道の価格が東北の価格に等しい時間は上乗せなし。北海道が安い側（東北へ送れるだけ送る・余る時間）は
        on = on & (np.abs(p0 - pT) > 1e-6)                      # 上乗せしても東北の価格で頭打ち（東北の電気に置き換わるので。送電量は変えない近似）
        ceil = np.where(p0 < pT, pT, PR.PRICE_CAP)
    else:
        ceil = PR.PRICE_CAP
    price = lambda mu: np.where(on, np.minimum(p0 + mu, ceil), p0)
    rev = (lambda p: MO.gm(R, p, w) + MO.make_whole(R, p, w)) if losses == "outside" else (lambda p: MO.gm(R, p, w))
    mu, capped = 0.0, False
    if I.get("mu_fixed") is not None and not standard:          # 感応度: μ を外から与える（要件に届かなくてもよい。notes/38 §3 (b) の μ を主の値に固定する置き方）
        mu = float(I["mu_fixed"])
    elif not standard and rev(p0) < req:
        if losses == "spot":
            g = (R["g"] * w).sum(2)
            vol = float((on * g).sum() * 1_000 / (p0.shape[0] / 365.25))   # 約定量（円/年 を円/kWh で割るための kWh/年）
            mu = (req - gm1) / vol if vol > 0 else PR.PRICE_CAP
        if losses == "outside" or off or (p0[on] + mu).max() > PR.PRICE_CAP or not np.isfinite(mu):   # 頭打ちがあると粗利は μ について線形でないので二分法
            lo, hi = 0.0, PR.PRICE_CAP
            if rev(price(hi)) < req:
                mu, capped = hi, True
            else:
                for _ in range(40):
                    mid = 0.5 * (lo + hi)
                    lo, hi = (lo, mid) if rev(price(mid)) >= req else (mid, hi)
                mu = hi
    p = price(mu)
    mw = MO.make_whole(R, p, w) if losses == "outside" else 0.0
    return p, dict(α=1.0, μ=mu, capped=capped, req=req, gm1=gm1, gm=MO.gm(R, p, w), cap=cap, mw=mw)


def markup_curve(V, info, I, shape=None):
    """価格の階段 V（基準の価格）に、② の上乗せを掛ける（solve_price と同じ掛け方。μ・α は info から）"""
    on = V > PR.FLOOR + 0.001
    ceil = PR.PRICE_CAP
    if not I.get("mu_tohoku", True):                            # 感応度: 東北の価格の区間（V の 2＋号機数 列目、MO.supply_curve）には上乗せを足さず、
        nu = (V.shape[-1] - 4) // 2                             # それより安い区間（1〜1＋号機数 列目: 余る時間の帯、東北の価格より安い号機）は東北の価格で頭打ち
        col = np.arange(V.shape[-1])
        on = on & (col != 2 + nu)
        ceil = np.where((col >= 1) & (col <= 1 + nu), V[..., 2 + nu:3 + nu], PR.PRICE_CAP)
    if (shape or SHAPE) == "flat":
        mu = 0.0 if not np.isfinite(info["μ"]) else info["μ"]
        return np.where(on, np.minimum(V + mu, ceil), V)
    return MO.price(V, np.where(on, np.maximum(V - I["v"][..., None], 0.0), 0.0), info["α"])


def run_year(I, cal, Ks=K_GRID, P_list=(14_972.0,), standard=False, mode="commit", step=None, req_scale=1.0, keep_prices=(),
             p_sched=P_SCHED, drop=(), exit_idle=True, return_state=False, mustrun=None, losses="spot", shape=None, rule=None):
    """格子の各 K で（④の退出、②③の α、π、蓄電池の動き）を記録する。充放電は容量価格 p_sched の価格で決める
    （sequential では、α は日の中の価格の順番を変えないので、ほかの容量価格でもほぼ同じ。0.01円の時間と上限価格の時間を除く。
    equilibrium では上乗せの額が蓄電池全体の充放電と蓄電池が値を決める価格を変えるので、P_list は p_sched だけにする）。
    rule: 蓄電池全体の運用（None なら PR.BATTERY_DISPATCH）。'equilibrium'＝量ごとに全体の充放電を一度に決め直す（主、BT.fleet_schedule）、
    'sequential'＝1〜10万kW ずつ足し、足した分はその時点の価格の最安4時間に充電・最高4時間に放電し、前の分の時間は固定（前の主）。
    drop: 前の年までに退出した号機（退出は1度きりで、戻らない）。exit_idle: False なら動かない号機も③の対象に残す（頑健性）。
    return_state: True なら最後の格子の点の需給・価格・充放電も返す。step: sequential で増やす刻み（None なら k_step）。
    mustrun: マストランの号機（None なら主の3台）。losses: マストランなどの運転の赤字の払い方、shape: 上乗せの形（solve_price）"""
    rule = rule or PR.BATTERY_DISPATCH
    if rule == "equilibrium" and mode != "commit":
        raise ValueError("蓄電池全体の運用（equilibrium）は需給の mode='commit' だけ")
    if rule == "equilibrium" and any(P != p_sched for P in P_list):
        raise ValueError("equilibrium では容量価格ごとに p_sched＝P として解き直す（P_list は p_sched だけ）")
    shape = shape or SHAPE
    units = B.fleet(I["year"], drop=tuple(drop) + tuple(u for u in I.get("retire", ()) if u not in drop))
    names = [u[0] for u in units]
    nd = I["D"].shape[0]
    yrs = nd / 365.25
    chg, dis = np.zeros((nd, 24)), np.zeros((nd, 24))
    rr = np.arange(nd)[:, None]
    grid = sorted(float(k) for k in Ks)
    w_all = BT.target_weights(units, I["year"])
    ltda = np.array([u[0] in PR.LTDA_UNITS for u in units])
    rows, prices, state = [], {}, None
    gi, done, iters = 0, 0.0, 0

    um = with_mustrun(units, mustrun)
    fixed = None                                                # 蓄電池が値を決める時間の (印, 価格)

    def solve(chg, dis, commit_fn=None, fixed=None):
        R = dispatch(I, units, chg, dis, mode=mode, mustrun=mustrun, commit_fn=commit_fn)
        alive = (R["g"].sum((0, 1)) > 1e-6) | ltda | (not exit_idle)
        p_s, info_s = solve_price(R, I, cal, p_sched, w_all * alive, standard, req_scale, losses, shape, fixed)
        return R, alive, p_s, info_s

    R, alive, p_s, info_s = solve(chg, dis)
    info0 = info_s
    while gi < len(grid):
        if rule == "equilibrium":
            done = grid[gi]
            P_mw = done * 10.0
            chg, dis, info_s = np.zeros((nd, 24)), np.zeros((nd, 24)), info0   # どの K も蓄電池0 の状態から解く（結果が格子によらない）
            hist, frozen, on_frz = [], np.zeros(nd, bool), None

            def commit_k(I_, u_, c_, d_):                       # 行き来する日は起動を固定する
                on, cap = commit(I_, u_, c_, d_)
                return (np.where(frozen[:, None], on_frz, on) if on_frz is not None else on), cap
            for iters in range(1, PR.EQ_ITERS + 1):            # 起動・上乗せは充放電で変わるので、交互に解き直す
                on_now, _ = commit_k(I, um, chg, dis)
                if len(hist) >= 2:                              # 前の回のどれかと同じ起動に戻った日（行き来）は、その間に起動した号機をすべて起動したままにする
                    flip, union = np.zeros(nd, bool), on_now.copy()
                    for h in range(len(hist) - 2, -1, -1):
                        back = ~frozen & ~flip & (on_now == hist[h]).all(1) & (on_now != hist[-1]).any(1)
                        if back.any():
                            u = np.logical_or.reduce([on_now] + hist[h:])
                            union = np.where(back[:, None], u, union)
                            flip |= back
                    if flip.any():
                        on_frz = np.where(flip[:, None], union, on_now if on_frz is None else on_frz)
                        frozen = frozen | flip
                        on_now, _ = commit_k(I, um, chg, dis)
                hist.append(on_now)
                q0, edges, V = MO.supply_curve(I, um, dis, commit_fn=commit_k, chg=chg)
                key = "α" if shape == "prop" else "μ"
                if iters > 1 and np.isfinite(info_s[key]):        # 上乗せは前の回と交互に振れるので、前に使った値との平均を使う
                    info_s = {**info_s, key: 0.5 * (info_s[key] + used)}
                used = info_s[key]
                Vm = markup_curve(V, info_s, I, shape)
                c, d, th_c, th_d = BT.fleet_schedule(q0, edges, Vm, P_mw, return_theta=True)
                fixed = BT.battery_set_prices(q0, edges, Vm, c, d, th_c, th_d, P_mw)
                moved = max(np.abs(c - chg).max(), np.abs(d - dis).max())
                chg, dis = c, d
                R, alive, p_s, info_s = solve(chg, dis, commit_k, fixed)
                if moved < 1.0 and not abs(info_s[key] - used) > 1e-3:
                    break
        else:
            R, alive, p_s, info_s = solve(chg, dis)
        w = w_all * alive
        gen = R["g"].sum((0, 1))
        if abs(done - grid[gi]) < 1e-9:
            c4, d4, ok = BT._schedule(p_s, I["days"], "share")
            top, bot = np.sort(p_s, 1)[:, -4:].mean(1), np.sort(p_s, 1)[:, :4].mean(1)
            batt = {"放電(TWh)": float(dis.sum() / yrs / 1e6), "充電(TWh)": float(chg.sum() / yrs / 1e6),
                    "1kW あたりの放電(kWh/kW-年)": float(dis.sum() / yrs / (done * 10.0)) if done > 0 else np.nan,
                    "追加の1kW が充放電する日(日/年)": float(ok.sum() / yrs),
                    "日の値幅 高い4時間−安い4時間(円/kWh)": float((top - bot).mean()),
                    "高い4時間の平均(円/kWh)": float(top.mean()), "安い4時間の平均(円/kWh)": float(bot.mean()),
                    "蓄電池の運用": rule, "運用の繰り返し(回)": iters if rule == "equilibrium" else np.nan,
                    "蓄電池が値を決める時間(h/年)": float(fixed[0].sum() / yrs) if fixed is not None else 0.0,
                    "起動を固定した日(日/年)": float(frozen.sum() / yrs) if rule == "equilibrium" else np.nan}
            mr = np.array([bool(u[6]) for u in R["units"]])
            p_a1 = R["p0"] if fixed is None else np.where(fixed[0], fixed[1], R["p0"])    # 上乗せなしの価格（蓄電池が値を決める時間はその価格）
            loss_mr = float(np.maximum((R["vc"] - p_a1[:, :, None]) * R["g"], 0.0)[:, :, mr].sum() * 1_000 / yrs / 1e8) if mr.any() else 0.0
            base = {"K(万kW)": done, **batt, "マストランの運転の赤字 α＝1(億円/年)": loss_mr, "残る号機": "・".join(n for n, a in zip(names, alive) if a),
                    "退出する号機": "・".join(n for n, a in zip(names, alive) if not a),
                    "残る火力(MW)": float(sum(u[2] for u, a in zip(units, alive) if a)), "対象の火力(MW)": info_s["cap"],
                    "抑制(TWh)": float(R["curt"].sum() / yrs / 1e6), "下げ代不足(TWh)": float(R["unabs"].sum() / yrs / 1e6), "火力の発電量(TWh)": float(gen.sum() / yrs / 1e6),
                    "北本 送電(TWh)": float(np.maximum(R["X"], 0).sum() / yrs / 1e6), "北本 受電(TWh)": float(np.maximum(-R["X"], 0).sum() / yrs / 1e6),
                    "供給力不足(MWh/年)": float(R["short"].sum() / yrs), "収支のずれ(MWh/年)": float(np.abs(R["residual_check"]).sum() / yrs),
                    **{f"発電量 {n}(GWh)": float(x / yrs / 1e3) for n, x in zip(names, gen)},
                    **{f"動いた時間 {n}(h)": float((R["g"][:, :, j] > 1e-6).sum() / yrs) for j, n in enumerate(names)}}
            for P in P_list:
                p, info = (p_s, info_s) if P == p_sched else solve_price(R, I, cal, P, w, standard, req_scale, losses, shape, fixed)
                rows.append({**base, "容量価格(円/kW)": P, "α": info["α"], "上乗せ μ(円/kWh)": info["μ"], "上乗せが上限": info["capped"],
                             "市場の外の補填(億円/年)": info["mw"] / 1e8,
                             "要件(億円/年)": info["req"] / 1e8, "α＝1 の粗利(億円/年)": info["gm1"] / 1e8, "粗利(億円/年)": info["gm"] / 1e8,
                             "π(円/kW-年)": BT.value(p, I["days"], I["fy"], cal, "share"),
                             "完全予見の粗利(円/kW-年)": PZ.annual(PZ.daily_value(p), I["fy"]),
                             "平均価格（需要加重）": float((p * I["D"]).sum() / I["D"].sum()), "0.01円の時間(h/年)": float((p <= PR.FLOOR + 0.001).sum() / yrs),
                             "夕17〜21時": float(p[:, 17:21].mean()), "昼10〜15時": float(p[:, 10:15].mean()), "夜0〜6時": float(p[:, :6].mean())})
                if (done, P) in keep_prices:
                    prices[(done, P)] = p.copy()
            if return_state and gi == len(grid) - 1:
                state = dict(R=R, p=p_s, chg=chg.copy(), dis=dis.copy(), alive=alive, info=info_s, fixed=fixed)
            gi += 1
            if gi == len(grid) or rule == "equilibrium":
                continue
        st = min(step or k_step(done), grid[gi] - done)
        c4, d4, ok = BT._schedule(p_s, I["days"], "share")
        chg[rr[ok], c4[ok]] += st * 10.0
        dis[rr[ok], d4[ok]] += st * 10.0 * PR.ETA
        done += st
    if return_state:
        return pd.DataFrame(rows), prices, state
    return pd.DataFrame(rows), prices


def exit_years(cal, sc, years=PR.YEARS, mode="commit", P=P_SCHED, mustrun=None, losses="spot", shape=None):
    """退出の年: 先に入っている蓄電池（既設＋LTDA）の量の経路で年を順に解き、1年間一度も動かない号機をその年に退出させる（以後は戻らない）。
    戻り値: {年: その年より前に退出した号機の名前のタプル}、{号機: 退出の年}"""
    from . import entry as EN
    gone, when, before = [], {}, {}
    for y in years:
        before[y] = tuple(gone)
        I = MO.inputs_future(PR.scenario_year(y, sc), sc)
        T, _ = run_year(I, cal, Ks=[EN.preset_stock(y)], P_list=(P,), mode=mode, p_sched=P, drop=gone, mustrun=mustrun, losses=losses,
                        shape=shape)
        for n in [x for x in str(T.iloc[0]["退出する号機"]).split("・") if x and x != "nan"]:
            if n not in gone:
                gone.append(n)
                when[n] = y
    return before, when
