#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""連系を入れた価格モデルで、蓄電池の収益 π(K)・市場だけで成立する容量 K*・市場外の補填・石炭の採算を求める（2026-10-23 改訂）

価格の決め方（時間 h。気象年 FY2023〜25 と、フリートの履歴の 2023-02〜03）:
  基準: 東北の価格 p_TH（実績）。北海道の正味の送電 X（実績の連系線、送電が正）。北海道の火力の出力 T（実績）。
  シナリオの変化: 原子力・再エネ・水力・揚水・需要の変化 ΔNS で、火力を据え置いたときの送電 X′＝X＋ΔNS。
  局面と価格:
    - 下げ代不足（55 の構造の判定。蓄電池の充電で吸収した後）: 現行0.01円。負の価格のシナリオで −c 円。
    - 再エネの抑制（同）: 0.01円。負の価格の上限のケース（価格に反応しない再エネが多い場合）では −c 円。
    - X′ が送電の上限を超える（北海道が安い）: 主ケースは FY2023〜25 の分断の時間の経験式 p＝a＋b·p_TH（本スクリプトで推定）。
      感応度は道内の燃料費の札（運転中のユニットの最低出力を床に置き、増分を燃料費の順に積む。p≤p_TH）。火力が床を下回るなら0.01円。
    - X′ が受電の上限を下回る（北海道が高い）: 主ケースは経験式。感応度は道内の札（p≥p_TH）。
    - それ以外: p_TH。
  連系の上限: 2035年は公式の前提（北本の送電57万kW、直流連系は＋0.55×容量）を 55 と 59 で同じに使う。受電は1,200−300MW（＋直流）。
    現状は 55 の判定（活用率55%・東北が下限なら0）と実績の潮流の大きい方。
  蓄電池: 充電は下げ代不足・抑制を先に吸収し、それを超えると受電を増やす。放電は送電を増やす。フリートは 41 と同じ増分貪欲。
指標: K*（容量市場の収入あり／なし、LTDA の約51万kW が先行）、市場外の補填（一律の支払い K_T×F(K_T)。足し上げは参考）、
  下限価格のプットの価値 π(−c)−π(0.01)、石炭ユニットの価格の受け手としての粗利。
前提: 往復効率0.90・費用は params_v4、燃料費は月別の輸入価格（60）、容量価格は全国連系（2030年度向け近似、κ＝0.861。旧の北海道ブロック按分は感応度）。
出力: data/processed/coupled_validation.csv、coupled_split_fit.csv、coupled_battery_value.csv、coupled_thermal_unit_economics.csv
"""
import contextlib
import io
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)


def load_head(fn, cut):
    src = open(os.path.join(HERE, fn), encoding="utf-8").read().split(cut)[0]
    ns = {"__file__": os.path.join(HERE, fn), "__name__": "mod_" + fn[:2]}
    _t = pd.DataFrame.to_csv
    pd.DataFrame.to_csv = lambda *a, **k: None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(src, ns)
    finally:
        pd.DataFrame.to_csv = _t
    return ns


m41 = load_head("41_equilibrium_v3.py", "\ncurves = []\n")
C_ACT = P4.set_eta(m41)
ETA = m41["ETA"]
m55 = load_head("55_structural_balance_model.py", "\nSC_ROWS = []\n")
m58 = load_head("58_coupled_price_model.py", "# ---------------------------------------------------------------- (1) 再現の検証")
daily_eval, annual = m41["daily_eval"], m41["annual"]
BLK, RB, W_B, FYB, EVB, DAYS, PACTM = (m41[k] for k in ("BLK", "RB", "W_B", "FYB", "EVB", "DAYS", "PACTM"))
DATES_B = DAYS[BLK]
FLOOR = 0.01
AVAIL, FUELTYPE = m58["AVAIL"], m58["FUELTYPE"]
DELTA = m55["DELTA"]
EVD = np.asarray(EVB)

# ---------------------------------------------------------------- 燃料費（月別、60）
FV = pd.read_csv(os.path.join(PROC, "fuel_vc_monthly.csv"), parse_dates=["month"]).set_index("month")


def vc_matrix(u, dates):
    """ユニット u の燃料費（日×24、円/kWh）。既設ユニットの効率の差は OCCTO の想定の燃種別の比で反映する"""
    col = {"石炭": "vc_coal", "LNG": "vc_lng", "石油": "vc_oil"}[FUELTYPE(u)]
    m = pd.DatetimeIndex(dates).to_period("M").to_timestamp()
    v = FV[col].reindex(m).ffill().bfill().to_numpy() * u[3] / {"石炭": 10.4, "LNG": 13.0, "石油": 27.8}[FUELTYPE(u)]
    return np.repeat(v[:, None], 24, 1)


# ---------------------------------------------------------------- 実績（BLK の日×24）
P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
P["date"], P["hour"] = P["ts"].dt.normalize(), P["ts"].dt.hour
PB = P.set_index(["date", "hour"]).sort_index().reindex(pd.MultiIndex.from_product([DATES_B, range(24)]))
SH = (len(DATES_B), 24)
ACT = {k: PB[k].to_numpy(float).reshape(SH) for k in ("thermal", "interconn", "p_tohoku", "p_hokkaido")}
X_ACT = -ACT["interconn"]
T_ACT = ACT["thermal"]
P_TH = ACT["p_tohoku"]
MONTH = np.repeat(DATES_B.month.to_numpy()[:, None], 24, 1)

# ---------------------------------------------------------------- 分断の時間の経験式（FY2023〜25 で推定、標本外は FY2019〜22・FY2026 4〜6月）
PA = P[(P["ts"] >= "2019-04-01")].copy()
PA["fy"] = PA["ts"].dt.year - (PA["ts"].dt.month < 4)
PA["lo"] = (PA["p_hokkaido"] < PA["p_tohoku"] - 0.01) & (PA["p_hokkaido"] > 0.011)
PA["hi"] = PA["p_hokkaido"] > PA["p_tohoku"] + 0.01
SPLIT, SF = {}, []
for side in ("lo", "hi"):
    tr = PA[PA[side] & PA["fy"].between(2023, 2025)]
    r = sm.OLS(tr["p_hokkaido"], sm.add_constant(tr[["p_tohoku"]])).fit(cov_type="HC1")
    SPLIT[side] = (r.params["const"], r.params["p_tohoku"])
    for lab, te in (("推定（FY2023〜25）", tr), ("標本外 FY2019〜22", PA[PA[side] & PA["fy"].between(2019, 2022)]),
                    ("標本外 FY2026 4〜6月", PA[PA[side] & (PA["fy"] == 2026)])):
        pred = r.params["const"] + r.params["p_tohoku"] * te["p_tohoku"]
        SF.append({"分断": {"lo": "北海道が安い（下限以外）", "hi": "北海道が高い"}[side], "標本": lab, "時間": len(te),
                   "切片": r.params["const"], "傾き": r.params["p_tohoku"], "傾きの t": r.tvalues["p_tohoku"],
                   "R2": 1 - ((te["p_hokkaido"] - pred) ** 2).sum() / ((te["p_hokkaido"] - te["p_hokkaido"].mean()) ** 2).sum(),
                   "MAE": np.abs(te["p_hokkaido"] - pred).mean(), "東北の価格そのままの MAE": np.abs(te["p_hokkaido"] - te["p_tohoku"]).mean()})
SFD = pd.DataFrame(SF)
SFD.round(4).to_csv(os.path.join(PROC, "coupled_split_fit.csv"), index=False, encoding="utf-8-sig")
print("[0] 分断の時間の経験式（北海道の価格＝切片＋傾き×東北の価格）")
print(SFD.round(3).to_string(index=False))

# ---------------------------------------------------------------- シナリオの組み立て
_CACHE = {}


def inputs_cached(sc, current, floor_arr=None):
    key = (repr(sorted(sc.items())) if sc else "current", None if floor_arr is None else round(float(floor_arr.sum()), 3))
    if key not in _CACHE:
        _CACHE[key] = m58["inputs"](sc, current, floor_arr=floor_arr, eps_current=DELTA)
    return _CACHE[key]


def supply(J):
    return J["N"] + J["Hy"] + J["Bm"] + J["G"] + J["U"] + J["V"] + J["Pgen"] - J["P"]


def build(sc, markup_from=None):
    current = sc is None
    year = 2025 if current else sc["year"]
    hv = 0.0 if current else sc.get("hvdc_mw", 0.0)
    Mimp = np.maximum(600.0, -X_ACT) if current else np.full(SH, 900.0 + 0.55 * hv)
    I0 = dict(inputs_cached(sc, current))
    I0["_Mimp_day"] = Mimp.min(1)
    units, on, floor = m58["commit"](I0, year)
    I = dict(inputs_cached(sc, current, floor_arr=pd.Series(floor, index=DATES_B)))
    if current:
        dNS = np.zeros(SH)
        Mexp = np.maximum(I["X"], X_ACT)
    else:
        Ia = inputs_cached(None, True)
        dNS = (supply(I) - supply(Ia)) - (I["D"] - Ia["D"])
        Mexp = I["X"]                                            # 55 と同じ送電の上限（公式の57万kW＋直流）
    caps, bids, vcs = [], [], []
    for k, u in enumerate(units):
        avail = np.array(AVAIL[FUELTYPE(u)])[MONTH - 1] / 100.0
        vc = vc_matrix(u, DATES_B)
        vcs.append(vc)
        if u[5]:                                                 # 毎日起動停止: 全量を燃料費＋起動費の上乗せで
            caps.append(u[1] * avail)
            bids.append(vc + u[4] / (m58["DSS_H"] * m58["DSS_QSHARE"] * u[1] * 1_000))
        else:                                                    # 運転中: 最低出力は床、増分を燃料費で
            caps.append(np.where(on[:, k][:, None], np.maximum(u[1] * avail - u[2], 0.0), 0.0))
            bids.append(np.where(on[:, k][:, None], vc, np.inf))
    B, C = np.stack(bids, 2), np.stack(caps, 2)
    if markup_from is not None:
        # 機会費用の回収の制度（シナリオ）: 日中に止められない石炭・石油（マストランを含む）が、価格が燃料費を下回る時間に最低出力で
        # 出した損失を、その日の夕方（17〜22時、定格×6時間）の札に上乗せする。価格に効くのは道内の札が価格を決める時間だけ
        ev = np.zeros(24, bool)
        ev[17:23] = True
        for k, u in enumerate(units):
            if u[5]:
                continue
            loss = (np.maximum(vcs[k] - markup_from, 0.0) * u[2]).sum(1) * 1_000
            mk = np.where(on[:, k], loss / (u[1] * 1_000 * 6.0), 0.0)
            B[:, :, k] = B[:, :, k] + np.where(ev[None, :], mk[:, None], 0.0)
    o = np.argsort(B, 2)
    BS, CS = np.take_along_axis(B, o, 2), np.take_along_axis(C, o, 2)
    return dict(I=I, units=units, on=on, floor=floor, Mexp=Mexp, Mimp=Mimp, Xp=X_ACT + dNS, BS=BS, CUM=np.cumsum(CS, 2),
                VCS=np.stack(vcs, 2), year=year)


def bid_at(S, above):
    """床より上の火力の出力 above（MW）での限界の札。容量を超えれば希少性の価格"""
    idx = np.argmax(S["CUM"] >= above[:, :, None] - 1e-9, 2)
    b = np.take_along_axis(S["BS"], idx[:, :, None], 2)[:, :, 0]
    return np.where((S["CUM"][:, :, -1] >= above) & np.isfinite(b), b, m58["SCARCITY"])


def price(S, chg, dis, mode="経験式", def_price=FLOOR, neg_scope="下げ代不足のみ"):
    I = S["I"]
    curt0, def0, floor = I["curt"], I["deficit"], S["floor"][:, None]
    rem_def = def0 - chg
    rem_curt = curt0 - np.maximum(chg - def0, 0.0)
    extra = np.maximum(chg - def0 - curt0, 0.0)
    X = S["Xp"] + dis - extra
    hi = X > S["Mexp"]
    lo = X < -S["Mimp"]
    T_new = T_ACT - (X - S["Mexp"])
    T_up = T_ACT + (-S["Mimp"] - X)
    if mode == "経験式":
        p_hi = np.maximum(SPLIT["lo"][0] + SPLIT["lo"][1] * P_TH, FLOOR)
        p_lo = SPLIT["hi"][0] + SPLIT["hi"][1] * P_TH
    else:
        p_hi = np.minimum(bid_at(S, np.maximum(T_new - floor, 0.0)), P_TH)
        p_lo = np.maximum(bid_at(S, np.maximum(T_up - floor, 0.0)), P_TH)
    p = np.where(hi, p_hi, P_TH)
    p = np.where(lo, p_lo, p)
    p = np.where(hi & (T_new < floor), FLOOR, p)                  # 火力が床を下回る: 再エネの抑制
    p = np.where(rem_curt > 1e-9, def_price if neg_scope == "余剰の全時間" else FLOOR, p)
    p = np.where(rem_def > 1e-9, def_price, p)
    return p, hi, lo


K_EVAL = list(range(0, 101)) + list(range(105, 201, 5))


def coal_economics(S, pp):
    """価格の受け手としての粗利: 運転日は、価格が燃料費以上なら定格（補修を差し引く）、下回れば最低出力。起動費は運転の開始ごと"""
    out = []
    for k, u in enumerate(S["units"]):
        if FUELTYPE(u) != "石炭" and not u[6]:
            continue
        vc = S["VCS"][:, :, k]
        capm = u[1] * np.array(AVAIL[FUELTYPE(u)])[MONTH - 1] / 100.0
        onk = S["on"][:, k][:, None]
        q = np.where(onk, np.where(pp >= vc, capm, u[2]), 0.0)
        mg = ((pp - vc) * q)[EVD].sum() / EVD.sum() * 365 * 1_000
        minloss = (np.minimum(pp - vc, 0.0) * np.where(onk, u[2], 0.0))[EVD].sum() / EVD.sum() * 365 * 1_000
        starts = (np.diff(S["on"][:, k].astype(int)) == 1)[EVD[1:]].sum() / EVD.sum() * 365
        out.append({"ユニット": u[0], "燃料": FUELTYPE(u), "設備(MW)": u[1], "運転日の割合": S["on"][EVD][:, k].mean(),
                    "発電量(GWh/年)": q[EVD].sum() / EVD.sum() * 365 / 1_000, "粗利(億円/年)": mg / 1e8,
                    "うち最低出力での損失(億円/年)": minloss / 1e8, "起動費(億円/年)": starts * u[4] / 1e8,
                    "粗利−起動費(円/kW-年)": (mg - starts * u[4]) / (u[1] * 1_000)})
    return out


def run(sc, mode="経験式", def_price=FLOOR, neg_scope="下げ代不足のみ", Ks=K_EVAL, unit_econ=False, S=None):
    S = S or build(sc)
    chg, dis = np.zeros(SH), np.zeros(SH)
    rows, done, ue = [], 0.0, None
    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            pp, _, _ = price(S, chg, dis, mode, def_price, neg_scope)
            oo = np.argsort(pp, 1)
            c4, d4 = oo[:, :4], oo[:, -4:]
            mg = np.take_along_axis(pp, d4, 1).sum(1) * ETA - np.take_along_axis(pp, c4, 1).sum(1)
            a = mg > 0
            chg[RB[a], c4[a]] += st * 10.0
            dis[RB[a], d4[a]] += st * 10.0 * ETA
            done += st
        pp, hi, lo = price(S, chg, dis, mode, def_price, neg_scope)
        d = daily_eval(pp, W_B)
        rows.append({"K(万kW)": K, "c": annual(d["c"], FYB, EVB), "π_PF": annual(d["pf"], FYB, EVB),
                     "北海道が安い割合": hi[EVD].mean(), "北海道が高い割合": lo[EVD].mean(),
                     "負の時間(h/年)": float((pp[EVD] < 0).sum() / EVD.sum() * 365),
                     "下限の時間(h/年)": float((np.abs(pp[EVD] - FLOOR) < 1e-9).sum() / EVD.sum() * 365)})
        if unit_econ and K == Ks[0]:
            ue = coal_economics(S, pp)
    return pd.DataFrame(rows), S, ue


CAPP = pd.read_csv(os.path.join(PROC, "capacity_price_of_k_v3.csv"))
KP = lambda K: np.interp(K, CAPP["K(万kW)"].to_numpy(float), CAPP[P4.KP_COL].to_numpy(float)) * P4.KP_SCALE
KP_OLD = lambda K: np.interp(K, CAPP["K(万kW)"].to_numpy(float), CAPP[P4.KP_COL_OLD].to_numpy(float)) * P4.KP_SCALE   # 感応度（旧の主）
K_LTDA = 51.0                                                    # LTDA で落札済みの北海道の系統用蓄電池（notes/37、2023・2024年度）


def metrics(df, lam):
    K = df["K(万kW)"].to_numpy(float)
    pi = (lam * df["c"] - P4.W_LOSS).clip(lower=0).to_numpy()
    out = {"π(0)": pi[0], "π(20)": float(np.interp(20, K, pi)), "π(50)": float(np.interp(50, K, pi)), "π(80)": float(np.interp(80, K, pi))}

    def cross(slack, start=0.0):
        m = K >= start
        Ks, sl = K[m], slack[m]
        if sl[0] < 0:
            return 0.0
        neg = np.where(sl < 0)[0]
        if len(neg) == 0:
            return float(Ks[-1] - start)
        i = neg[0]
        return float(Ks[i - 1] + (Ks[i] - Ks[i - 1]) * sl[i - 1] / (sl[i - 1] - sl[i]) - start)
    for ck, cv in P4.CAPEX.items():
        cr = P4.c_req(cv)
        out[f"K*（{ck}）"] = cross(pi + KP(K) - cr)
        out[f"K* 容量収入なし（{ck}）"] = cross(pi - cr)
        out[f"K* LTDA 51万kW が先行（{ck}）"] = cross(pi + KP(K) - cr, K_LTDA)
        out[f"K* 容量価格は北海道ブロック按分（旧の主、{ck}）"] = cross(pi + KP_OLD(K) - cr)
        for KT in (50, 80, 100):
            F = max(0.0, cr - float(np.interp(KT, K, pi)) - float(KP(float(KT))))
            out[f"補填 {KT}万kW 一律（{ck}、億円/年）"] = KT * 1e4 * F / 1e8
            ks = np.arange(0, KT)
            out[f"補填 {KT}万kW 足し上げ・参考（{ck}、億円/年）"] = float(np.clip(cr - np.interp(ks, K, pi) - KP(ks.astype(float)), 0, None).sum() * 1e4 / 1e8)
    return out


# ---------------------------------------------------------------- (1) 検証（現状、シナリオの変化0）
V0, S0, _ = run(None, Ks=[0])
p0, _, _ = price(S0, np.zeros(SH), np.zeros(SH))
pa, pm, pt = PACTM[BLK][EVD], p0[EVD], P_TH[EVD]


def stat(pmod):
    sa, sm_ = np.sort(pa, 1), np.sort(pmod, 1)
    return {"平均": pmod.mean(), "上位4h": sm_[:, -4:].mean(), "下位4h": sm_[:, :4].mean(), "相関": np.corrcoef(pa.ravel(), pmod.ravel())[0, 1],
            "R2": 1 - ((pa - pmod) ** 2).sum() / ((pa - pa.mean()) ** 2).sum(), "MAE": np.abs(pa - pmod).mean(),
            "値幅の相関": np.corrcoef(sa[:, -4:].mean(1) - sa[:, :4].mean(1), sm_[:, -4:].mean(1) - sm_[:, :4].mean(1))[0, 1]}


VAL = pd.DataFrame([{"系列": "実績（北海道）", **stat(pa)}, {"系列": "東北の価格そのまま（素朴な基準）", **stat(pt)}, {"系列": "モデル", **stat(pm)}])
VAL["戦略c"] = [annual(daily_eval(PACTM[BLK], W_B)["c"], FYB, EVB), annual(daily_eval(P_TH, W_B)["c"], FYB, EVB), V0["c"].iloc[0]]
LAM = C_ACT / V0["c"].iloc[0]
VAL.round(4).to_csv(os.path.join(PROC, "coupled_validation.csv"), index=False, encoding="utf-8-sig")
print(f"\n[1] 現状の再現（FY2023〜25）。λ＝{LAM:.4f}")
print(VAL.round(3).to_string(index=False))


# ---------------------------------------------------------------- (2) シナリオ
def sc_of(nuc, **kw):
    sc = {**m55["BASE35"], **kw}
    sc.pop("floor_override", None)                              # 床は運転台数の規則で日ごとに決める（55 にも同じ床を渡す）
    names, mw = m55["NUC_SC"][nuc]
    sc["nuclear_mw"], sc["nuc_units"] = mw, [m55["NUC_UNITS"][n] for n in names] or [0.0]
    return sc


HV = {"X_fixed": 570.0 + 0.55 * 2_000.0, "hvdc_mw": 2_000.0}
SCEN = [("現状（FY2023〜25 の実績の需給）", None, {})]
for nuc in ("原子力なし", "泊3号", "泊1・3号", "泊全基"):
    for ds in (0, 600, 1_000):
        SCEN.append((f"2035 {nuc} 自家消費+{ds // 10}万kW", nuc, {"selfcons_mw": float(ds)}))
for nuc in ("泊1・3号", "泊全基"):
    SCEN.append((f"2035 {nuc} 自家消費+100万kW 直流連系+200万kW", nuc, {"selfcons_mw": 1_000.0, **HV}))
for mult in (2.6, 3.0):
    for nuc in ("原子力なし", "泊1・3号"):
        for hv_lab, hv in (("", {}), (" 直流連系+200万kW", HV)):
            SCEN.append((f"2035 エネ基の太陽光×{mult} {nuc}{hv_lab}", nuc, {"solar_mw": 2_360.0 * mult, **hv}))
REGS = [("現行（0.01円）", FLOOR, "下げ代不足のみ"), ("負の価格 −10円（下げ代不足のみ）", -10.0, "下げ代不足のみ"),
        ("負の価格 −10円（余剰の全時間、上限）", -10.0, "余剰の全時間")]
if os.environ.get("RUN59_SCEN", "1") == "1":
    ROWS = []
    for lab, nuc, kw in SCEN:
        sc = None if nuc is None else sc_of(nuc, **kw)
        S = build(sc)
        for mode in ("経験式", "道内の札"):
            for reg, dp, scope in (REGS if nuc is not None else REGS[:1]):
                df, _, _ = run(sc, mode, dp, scope, S=S)
                r = {"シナリオ": lab, "分断の価格": mode, "制度": reg, **metrics(df, LAM),
                     "北海道が安い K=0": df["北海道が安い割合"].iloc[0], "北海道が高い K=0": df["北海道が高い割合"].iloc[0],
                     "負の時間 K=0(h/年)": df["負の時間(h/年)"].iloc[0], "下限の時間 K=0(h/年)": df["下限の時間(h/年)"].iloc[0]}
                ROWS.append(r)
            base = [x for x in ROWS if x["シナリオ"] == lab and x["分断の価格"] == mode]
            print(f"  {lab} / {mode}: π(0) {base[0]['π(0)']:,.0f}" + (f"（−10円 下げ代不足 {base[1]['π(0)']:,.0f}、上限 {base[2]['π(0)']:,.0f}）" if len(base) > 1 else "")
                  + f" π(50) {base[0]['π(50)']:,.0f} 安い {base[0]['北海道が安い K=0']:.2f} 下限 {base[0]['下限の時間 K=0(h/年)']:.0f}h "
                  f"K*（6.8/4.0/2.3）{base[0]['K*（6.8万）']:.1f}/{base[0]['K*（4.0万）']:.1f}/{base[0]['K*（2.3万）']:.1f} "
                  f"容量なし {base[0]['K* 容量収入なし（2.3万）']:.1f} LTDA先行 {base[0]['K* LTDA 51万kW が先行（2.3万）']:.1f} "
                  f"補填80万kW（6.8）{base[0]['補填 80万kW 一律（6.8万、億円/年）']:.0f}億円")
    pd.DataFrame(ROWS).round(4).to_csv(os.path.join(PROC, "coupled_battery_value.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- (3) 石炭の採算（主のシナリオ、経験式と道内の札）
if os.environ.get("RUN59_COAL", "1") == "1":
    UE = []
    for lab, nuc, kw in [SCEN[0]] + [s for s in SCEN if "自家消費+60万kW" in s[0]] + [s for s in SCEN if "自家消費+100万kW 直流" in s[0]]:
        sc = None if nuc is None else sc_of(nuc, **kw)
        S = build(sc)
        for mode in ("経験式", "道内の札"):
            _, _, ue = run(sc, mode, Ks=[0], unit_econ=True, S=S)
            UE += [{"シナリオ": lab, "分断の価格": mode, **u} for u in ue]
    UED = pd.DataFrame(UE)
    UED.round(3).to_csv(os.path.join(PROC, "coupled_thermal_unit_economics.csv"), index=False, encoding="utf-8-sig")
    print("\n[3] 石炭の価格の受け手としての粗利−起動費（円/kW-年）")
    print(UED[UED["燃料"] == "石炭"].pivot_table(index=["シナリオ", "分断の価格"], columns="ユニット", values="粗利−起動費(円/kW-年)", sort=False).round(0).to_string())

# ---------------------------------------------------------------- (4) 機会費用の回収の制度（シナリオ、道内の札の経路）
if os.environ.get("RUN59_OPP", "1") == "1":
    OPP = []
    for lab, nuc, kw in [SCEN[0]] + [s for s in SCEN if "自家消費+60万kW" in s[0]] + [s for s in SCEN if "自家消費+100万kW 直流" in s[0]]:
        sc = None if nuc is None else sc_of(nuc, **kw)
        S = build(sc)
        p_base, _, _ = price(S, np.zeros(SH), np.zeros(SH), "道内の札")
        for reg, SS in (("現行の規律", S), ("機会費用の回収", build(sc, markup_from=p_base))):
            df, _, ue = run(sc, "道内の札", S=SS, unit_econ=True)
            m = metrics(df, LAM)
            coal4 = [x for x in ue if x["ユニット"] == "苫東厚真4"][0]["粗利−起動費(円/kW-年)"]
            OPP.append({"シナリオ": lab, "制度": reg, "π(0)": m["π(0)"], "π(50)": m["π(50)"], "K*（2.3万）": m["K*（2.3万）"],
                        "補填 80万kW 一律（6.8万、億円/年）": m["補填 80万kW 一律（6.8万、億円/年）"], "苫東厚真4 粗利−起動費(円/kW-年)": coal4})
    OPPD = pd.DataFrame(OPP)
    OPPD.round(3).to_csv(os.path.join(PROC, "coupled_oppcost_scenario.csv"), index=False, encoding="utf-8-sig")
    print("\n[4] 機会費用の回収の制度（道内の札の経路）")
    print(OPPD.round(1).to_string(index=False))
