# -*- coding: utf-8 -*-
"""需給の構造モデル（時間別）。日×24時間の配列で計算する（設計レビュー 2026-10-25 を反映）

各時間:
  固定の供給 ＝ 原子力（定検の周期つき）＋水力＋揚水（気象年の実績、混合揚水の自然流入を含む）＋地熱＋バイオマス（実績＋新設）
              ＋対象外の火力（月×時刻の実績の平均）＋制御できない太陽光
  北本の流れ ＝ 気象年の実績（送電が正）。北本の増強分（FY2028〜、300MW）は、気象年で北海道が東北より安かった時間だけ送電に足す
  余り E ＝ 固定の供給＋運転中の火力の最低出力＋制御できる太陽光・風力＋蓄電池の放電−需要−送電−蓄電池の充電
  E＞0 の時間（余剰）: 東北も0.01円なら送電0（過去に両方0.01円だった時間の流れの中央値は約25MW）。
                      それ以外は、余りを「北海道が東北より安い時間の実績の送電の中央値（約330MW）＋増強分（FY2028〜300MW）」まで東北へ送る
                      （北海道だけが余る時間は価格が分かれ、連系線が東北向きに混む。FY2024〜26 の実績）。変種: 90%点（約580MW）、過去の流れのまま
                      それでも残る分は太陽光・風力を抑制する。抑制しきれない分は下げ代不足
  E≦0 の時間: 火力（運転中のユニットの最低出力より上、毎日起動停止のユニット）を燃料費の順に給電する
日ごとの運転台数: その日の火力の最大の必要量×1.02＋最大機を満たすまで、マストラン→燃料費の安い順に起動する（毎日起動停止のユニットは除く）
"""
import numpy as np
import pandas as pd

from . import params as PR
from . import data as DT

EPS = 1e-9
MARGIN_TIE, UTIL = 300.0, 0.55


def fleet(year, drop=()):
    return [u for u in PR.UNITS if u[7] <= year <= u[8] and u[0] not in drop]


def avail_cap(units, month, I=None):
    """日×24×ユニットの運転できる容量。実績の年度は HJKS の停止・低下の記録から時間別に、将来はユニット×月の比（data.unit_avail_profile）"""
    prof = DT.unit_avail_profile()
    av = (I or {}).get("avail", {})
    return np.stack([u[2] * (av[u[0]] if u[0] in av else prof[u[0]][month - 1]) for u in units], 2)


_OTHER = None
_OTHER_MIN = None


def other_floor_min():
    """対象外の火力の下げられない分: 値崩れの時間（0.01円）の月別の平均（FY2024〜25）。データがない月は全体の平均"""
    global _OTHER_MIN
    if _OTHER_MIN is None:
        C = DT.calib()
        fl = C["p"] <= PR.FLOOR + 0.001
        allm = float(C["other"][fl].mean())
        _OTHER_MIN = np.array([allm] + [float(C["other"][fl & (C["month"] == m)].mean()) if (fl & (C["month"] == m)).sum() >= 5 else allm
                                        for m in range(1, 13)])
    return _OTHER_MIN


def other_profile():
    """対象外の火力（エリアの火力−ユニット別の合計。音別 GT・室蘭・釧路・自家発などを含む）の月×時刻の平均（FY2024〜25）"""
    global _OTHER
    if _OTHER is None:
        C = DT.calib()
        prof = np.zeros((13, 24))
        for m in range(1, 13):
            for h in range(24):
                prof[m, h] = C["other"][(C["month"] == m) & (C["hour"] == h)].mean()
        _OTHER = prof
    return _OTHER


def _v_season(days, month):
    F = DT.fuel().reindex(days.to_period("M").to_timestamp()).ffill().bfill()
    v = np.repeat(F["idx"].to_numpy()[:, None], 24, 1)
    return v, np.vectorize(PR.SEASON_OF_MONTH.get)(month)


def nuclear_series(days, fy_scen, units):
    """原子力の出力（日×24）。気象年の日付を、シナリオの年度の同じ月日に置き換えて、運転開始と定検の周期を当てる。
    定検の時期は分からないので、気象年ごとに周期を1/3ずつずらす（3つの気象年の平均が、定検の時期についての平均になる。結果のレビュー 2026-10-25）"""
    o = PR.NUC_OUTAGE
    cyc = o["run_days"] + o["stop_days"]
    out = np.zeros((len(days), 24))
    wfy = np.asarray(days.year - (days.month < 4))
    shift = {fy: int(round(j * cyc / len(PR.WEATHER_FY))) for j, fy in enumerate(PR.WEATHER_FY)}
    s3 = pd.Timestamp(*PR.NUC_START["泊3号"], 1)                # 周期の位置は両基とも泊3号の運転開始の日から数える（停止が重ならない）
    for u, start_month in units:
        sy, sm = PR.NUC_START[u]
        s = pd.Timestamp(sy, sm, 1)
        for i, d in enumerate(days):
            ph = o["phase"].get(u, 0) + shift.get(int(wfy[i]), 0)
            yy = fy_scen + (1 if d.month < 4 else 0)
            dd = min(d.day, 28) if d.month == 2 else d.day
            sd = pd.Timestamp(yy, d.month, dd)
            if sd < s:
                continue
            if (sd - s).days < o["run_days"] or ((sd - s3).days + ph) % cyc < o["run_days"]:   # 再稼働の後の最初の運転は383日続ける
                out[i, :] += PR.NUC[u]
    return out


def _common(D, S, Wd, cf_S, N, Hy, G, Bm, pump, X, p_hk, p_th, days, month, fy, year, opcap, incr, surplus_export="market"):
    v, season = _v_season(days, month)
    return dict(year=year, v=v, season=season, D=D, S=S, W=Wd, U=np.minimum(PR.U_SOLAR * cf_S, S), N=N, Hy=Hy, G=G, Bm=Bm,
                pump=pump, X=X, nat_floor=p_th <= PR.FLOOR + 0.001, hk_cheaper=p_hk < p_th - 0.01, month=month, days=days, fy=fy,
                exp_cap=UTIL * (opcap - MARGIN_TIE), exp_full=opcap - MARGIN_TIE, export_incr=incr, surplus_export=surplus_export,
                largest=np.where(N >= PR.NUC["泊3号"] - EPS, PR.NUC["泊3号"], PR.COMMIT_RESERVE["largest"]))


def inputs_future(sc_y):
    """気象年の形に、その年の需要・設備を当てる"""
    W = DT.weather()
    D = np.zeros_like(W["D"])
    for fy in PR.WEATHER_FY:
        r = W["fy"] == fy
        e_hist = W["D"][r].sum() / 1e3
        k = (sc_y["demand_gwh"] - sc_y["dc_gwh"]) / e_hist
        D[r] = W["D"][r] * k + sc_y["dc_gwh"] * 1e3 / (r.sum() * 24)
    D = D - sc_y["selfcons_mw"] * W["cf_S"] * 0.85
    N = nuclear_series(W["days"], sc_y["year"], sc_y["nuclear"])
    return _common(D, sc_y["solar_mw"] * W["cf_S"], sc_y["wind_mw"] * W["cf_W"], W["cf_S"], N, W["Hy"], W["G"] + sc_y["geo_add_mw"],
                   W["Bm"] + sc_y["biomass_add_mw"], W["pump"], W["X"], W["p"], W["p_th"], W["days"], W["month"], W["fy"],
                   sc_y["year"], sc_y["export_opcap"], sc_y["export_increment_mw"], sc_y.get("surplus_export", "market"))


def inputs_actual(fy):
    """実績の年度（検証用）。太陽光・風力は抑制前"""
    P = DT.panel()
    days = DT._days((fy,))
    g = lambda c: DT._grid(P[c].fillna(0.0), days)
    month = np.repeat(days.month.to_numpy()[:, None], 24, 1)
    S = g("solar") + g("solar_curt")
    cap = DT._capacity_daily(days)
    cf_S = S / cap["solar_kw"].to_numpy()[:, None]
    opcap = np.where(np.isin(month, [6, 7, 8, 9, 10, 11]) & (fy == 2025), 900.0, 700.0)
    I = _common(g("demand"), S, g("wind") + g("wind_curt"), cf_S, g("nuclear"), g("hydro"), g("geothermal"), g("biomass"), g("pumped"),
                -g("interconn"), DT._grid(P["p_hokkaido"].fillna(99.0), days), DT._grid(P["p_tohoku"].fillna(99.0), days), days, month,
                (days.year - (days.month < 4)).to_numpy(), fy, opcap, 0.0)
    I["curt_act"] = g("solar_curt") + g("wind_curt")
    I["p_act"] = DT._grid(P["p_hokkaido"], days)
    if fy >= PR.HJKS_FROM:                                     # HJKS の記録は FY2024 から。それより前はユニット×月の比
        I["avail"] = DT.hjks_availability(days, [u[0] for u in PR.UNITS if u[9] is not None or u[0] in DT.HJKS_ONLY])
    return I


def residual(I):
    """残余需要（需要−原子力・水力・地熱・バイオマス・太陽光・風力）。価格の逼迫度の分子"""
    return I["D"] - I["N"] - I["Hy"] - I["G"] - I["Bm"] - I["S"] - I["W"]


def tau_den(I, units):
    """逼迫度の分母: 運転できる火力＋対象外の火力の月×時刻の平均"""
    return avail_cap(units, I["month"], I).sum(2) + other_profile()[I["month"], np.arange(24)[None, :]]


def run(I, units, chg=None, dis=None, delta=0.0, **_):
    nd = I["D"].shape[0]
    chg = np.zeros((nd, 24)) if chg is None else chg
    dis = np.zeros((nd, 24)) if dis is None else dis
    hrs = np.arange(24)[None, :]
    O = other_profile()[I["month"], hrs]
    cap = avail_cap(units, I["month"], I)
    mins = np.array([u[3] for u in units], float)
    months = np.repeat(I["days"].values[:, None], 24, 1).ravel()
    vc = np.stack([DT.unit_vc(u, months).reshape(nd, 24) for u in units], 2)
    must = np.array([u[6] for u in units])
    dss = np.array([u[5] for u in units])
    X_incr = np.where(I["hk_cheaper"], I["export_incr"], 0.0)
    X_ns = I["X"] + X_incr                                    # 余剰でない時間の北本の流れ（送電が正）
    fixed = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O + I["pump"]
    # 日ごとの運転台数
    T_req = I["D"] + X_ns + chg - dis - fixed - I["S"] - I["W"]
    need = T_req.max(1) * (1 + PR.COMMIT_RESERVE["margin"]) + I["largest"].max(1) - PR.COMMIT_RESERVE["credit"]
    on = np.zeros((nd, len(units)), bool)
    on[:, must] = True
    have = cap[:, :, must].max(1).sum(1) + (cap[:, :, dss].max(1).sum(1) if dss.any() else 0.0)
    rest = need - have
    for i in [i for i in np.argsort([u[4] for u in units]) if not must[i] and not dss[i]]:
        add = rest > 0
        on[add, i] = True
        rest = rest - np.where(add, cap[:, :, i].max(1), 0.0)
    gmin = np.where(on[:, None, :] & ~dss[None, None, :], np.minimum(mins[None, None, :], cap), 0.0)
    gs = gmin.sum(2, keepdims=True)
    gmin = np.minimum(np.where(gs > 0, gmin * (1 + delta / np.maximum(gs, EPS)), 0.0), cap)
    # 余り（余剰の時間は、対象外の火力を下げられない分まで下げる）
    E_ns = fixed + gmin.sum(2) + I["S"] + I["W"] + dis - I["D"] - chg - X_ns
    O_low = np.minimum(O, other_floor_min()[I["month"]])
    O_red = np.where(E_ns > 0, np.minimum(O - O_low, E_ns), 0.0)   # 必要な分だけ下げる
    E_ns = E_ns - O_red
    O = O - O_red
    fixed = I["N"] + I["Hy"] + I["G"] + I["Bm"] + O + I["pump"]
    surplus_pre = E_ns > 0
    mode = I.get("surplus_export", "market")
    if mode in ("market", "high"):                              # 主: 東北も0.01円なら0。それ以外は余りを、北海道が安い時間の実績の送電（中央値・変種は90%点）＋増強分まで東北へ送る
        cap_x = PR.SURPLUS_EXPORT_MW[mode] + I["export_incr"]
        X_s = np.where(I["nat_floor"], 0.0, X_ns + np.minimum(np.maximum(E_ns, 0.0), np.maximum(cap_x - X_ns, 0.0)))
    elif mode in ("full", "official"):                          # 照合用: 余りを上限（使える容量いっぱい、または公式並み770MW）まで送電に足す
        cap_x = np.broadcast_to(np.asarray(I["exp_full"] if mode == "full" else 770.0, float), I["X"].shape)
        X_s = X_ns + np.minimum(np.maximum(E_ns, 0.0), np.maximum(cap_x - X_ns, 0.0))
    else:                                                       # 変種（旧の置き方）: 過去の流れのまま
        X_s = np.where(I["X"] < 0, I["X"], np.where(I["nat_floor"], 0.0, np.minimum(I["X"], I["exp_cap"]))) + np.where(I["nat_floor"], 0.0, X_incr)
    X = np.where(surplus_pre, X_s, X_ns)
    E = E_ns + X_ns - X
    pos = np.maximum(E, 0.0)
    flex_vre = (I["S"] - I["U"]) + I["W"]
    curt = np.minimum(pos, flex_vre)
    unabs = pos - curt
    surplus = curt + unabs > EPS
    # 給電
    T_up = np.maximum(-E, 0.0)
    head = np.where(on[:, None, :], cap - gmin, 0.0)
    head = np.where(dss[None, None, :], cap, head)
    gadd = np.zeros_like(head)
    rem_t = T_up.copy()
    ordv = np.argsort(vc, 2)
    for k in range(head.shape[2]):
        ix = ordv[:, :, k][:, :, None]
        hk = np.take_along_axis(head, ix, 2)[:, :, 0]
        q = np.minimum(hk, rem_t)
        np.put_along_axis(gadd, ix, q[:, :, None], 2)
        rem_t = rem_t - q
    short = rem_t
    g_units = gmin + gadd
    supply = fixed + I["S"] + I["W"] - curt + g_units.sum(2) + dis
    use = I["D"] + X + chg + unabs
    net = residual(I)
    den = tau_den(I, units)
    return dict(on=on, g=g_units, vc=vc, other_out=O, curt=curt, unabs=unabs, surplus=surplus, X=X, X_incr=X_incr, short=short,
                tau=(net + chg - dis + X_incr) / den, net=net, den=den, gmin=gmin, residual_check=supply + short - use, units=units,
                delta=delta)
