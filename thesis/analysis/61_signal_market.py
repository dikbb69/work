#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""【作業中（2026-10-23）】シグナルが正しい市場で、蓄電池はどこまで増えるか（年ごとの価格と、コホートの自由参入均衡）

著者の主張（2026-10-23）: 蓄電池の導入は市場のシグナルで促されるべきで、市場外の支援はやめるべき。容量市場は残す（市場と補助金の中間）。
  事業者は将来の収益を期待して参入する。
設計（レビュー wf_56a71b5c-284 の推奨を反映。scratchpad/refocus/ideal_market_design.md）:
  「シグナルが正しい市場」＝各時間の価格が社会的な限界費用 λ^E に等しい市場。下側は負の価格を許し、上側は炭素の費用を入れる。
  価格の4本（59 の価格モデルの上に作る。59 は書き換えない）:
    - 現行 p^0: 59 と同じ（0.01円の下限）。回帰テストで 59 と一致を確かめる。
    - 効率 λ^E: 余剰の時間は、社会的費用の札の高い順に止めた最後の札。
        制御できる再エネ（FIT・FIP・非 FIT のすべて）0円、水力の放流（溢水）0円、原子力の出力調整（定格の50%まで。伊方2号の
        1987〜88年の試験で50〜100% が可能と確認、JAEA ATOMICA）0円。これでも吸収できない時間（止められない屋根置き・マストランの
        火力・地熱・バイオマスの最低）は、最後の手段（長期固定電源の抑制指令）の費用 c_LR になる。公的な値がないので、主の表は
        c_LR＝0 とし、「吸収しきれない時間」と「深さ1円あたりの価値」を別に示す。東北が0.01円の時間（東日本に共通の余剰）も0円にする。
    - 効率＋炭素: λ^E に、GX-ETS の炭素の費用を加える（東北の価格の0.01円より上の時間と、道内の火力の燃料費）。
        価格: 2026年度の上限4,300円・下限1,700円/t-CO2、以後実質3%で上がる（排出量取引制度小委員会 2025/12/19、GX グループ 2026/2/13 p.22）。
        主は上下限の中点、感応度は下限・上限。燃料費の転嫁の傾き（60: 約1、共和分で長期に1対1）と同じく、全額が価格に入る（ρ＝1）。
    - 歪み p^D: 余剰の全時間（東北の0.01円の時間を含む）を −10円（出力に連動する支援、送配電事業者が FIT を下限で売る設計）。
        効率との差は、再エネの支援（賦課金）から蓄電池への移転にあたる（T＝π(p^D)−π(λ^E)）。
  価格の決め方の訂正: 59 の経験式 p＝a＋b·p_TH は、北海道の価格が0.01円より上の時間で推定した。東北が0.01円の時間に当てると
    北海道が0.90円になる（標本外への外挿）。新しい設計では、東北が0.01円の時間は余剰の価格にする（現行の回帰テストではこの訂正を外す）。
年: 2026〜2040年を毎年計算する。需要は OCCTO 需要想定（2026年度）の年別の値、太陽光・風力は OCCTO 2026年度供給計画（2026・2030・
  2035年度末）と2040年のシナリオの間を線形、泊・直流連系は年の段差。気象年は FY2023〜25。
  2040年: OCCTO 将来の電力需給シナリオのエリア配賦（第11回検討会 資料3、検討中）。エネ基（1.1〜1.2兆kWh）は11,000億kWh ケースに近い。
  感応度として、エネ基の太陽光の倍率（全国の発電量の倍率を北海道に比例で当てる、×3.0）。
  屋根置き: 2035年より後の太陽光の増加分のうち、2040年の配賦の屋根置き（需要地併設型）の比率の分を自家消費（需要の減少、制御できない）に入れる。
自由参入: コホート τ（年 τ に建設、τ+1〜τ+20 年に運転）の NPV≤0、参入≥0、相補性を、等価な凹計画（Lucas & Prescott 1971）の
  線形計画で解く。2041年以降の収益は2040年の値で一定（感応度で年1% 低下）。
出力: data/processed/signal_market_pi.csv（年×設計×経路の π(0)・π(20)・π(50)）、signal_market_pik.npz（π(K) の全体）、
  signal_market_entry.csv（均衡の K_t の経路）
"""
import contextlib
import io
import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
CUT2 = "# ---------------------------------------------------------------- (2) シナリオ"


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


m59 = load_head("59_coupled_battery_value.py", CUT2)
exec(open(os.path.join(HERE, "59_coupled_battery_value.py"), encoding="utf-8").read().split(CUT2)[1].split("\nSCEN = ")[0], m59)
m55, m58 = m59["m55"], m59["m58"]
LAM, KP, FLOOR = m59["LAM"], m59["KP"], m59["FLOOR"]
SH, RB, ETA, EVD = m59["SH"], m59["RB"], m59["ETA"], m59["EVD"]
P_TH0, T_ACT, X_ACT, MONTH, DATES_B = m59["P_TH"], m59["T_ACT"], m59["X_ACT"], m59["MONTH"], m59["DATES_B"]
SPLIT = m59["SPLIT"]
K_EVAL = np.array(m59["K_EVAL"], float)
TFLOOR = P_TH0 <= 0.011                                            # 東北が0.01円の時間

# ---------------------------------------------------------------- 炭素
# 排出原単位（t-CO2/MWh、送電端）＝炭素排出係数×44/12×3.6÷発電効率÷(1−所内率)。効率・所内率は 60（発電コスト検証WG）。
# 炭素排出係数（tC/GJ、総発熱量）【要照合: 標準発熱量・炭素排出係数一覧】: 輸入一般炭0.0247、LNG 0.0135、C重油0.0195。
EF_C = {"石炭": 0.0247, "LNG": 0.0135, "石油": 0.0195}
EFF = {"石炭": (0.434, 0.056), "LNG": (0.549, 0.022), "石油": (0.390, 0.048)}
EI = {k: EF_C[k] * 44 / 12 * 3.6 / EFF[k][0] / (1 - EFF[k][1]) for k in EF_C}   # t-CO2/MWh
EI_TH = (EI["石炭"] + EI["LNG"]) / 2                             # 東北の価格: 60 の燃料費の指標（石炭と LNG の平均）と同じ重み


def carbon_price(year, case="中点"):
    if year < 2026:
        return 0.0
    lo, hi = 1_700.0 * 1.03 ** (year - 2026), 4_300.0 * 1.03 ** (year - 2026)
    return {"下限": lo, "上限": hi, "中点": (lo + hi) / 2}[case]


# ---------------------------------------------------------------- 年のシナリオ（一次資料の値。notes/37）
DEMAND = {2025: 29_612, 2026: 29_733, 2027: 29_942, 2028: 30_216, 2029: 30_824, 2030: 31_679, 2031: 32_443, 2032: 32_738,
          2033: 32_971, 2034: 33_098, 2035: 33_106}                # GWh、送電端。OCCTO 需要想定（2026年度）
DC = {2025: 0.0, 2030: 2_500.0, 2035: 3_600.0}                     # GWh（55 の DC_FLAT。2035 は PwC の推計）
SOLAR = {2025: 2_360.0, 2026: 2_630.0, 2030: 3_380.0, 2035: 3_560.0}   # MW。OCCTO 2026年度供給計画（年度末）
WIND = {2025: 1_370.0, 2026: 1_440.0, 2030: 2_700.0, 2035: 2_750.0}
Y2040 = {
    "OCCTO 11,000億kWh": dict(demand=47_000.0, dc=8_000.0, solar=4_200.0, roof=1_300.0 / 4_200.0, wind=7_200.0, energy=False),
    "OCCTO 9,000億kWh": dict(demand=35_000.0, dc=4_000.0, solar=3_000.0, roof=600.0 / 3_000.0, wind=3_500.0, energy=False),
    "エネ基の倍率×3.0（需要は11,000億kWh）": dict(demand=47_000.0, dc=8_000.0, solar=2_360.0 * 3.0, roof=1_300.0 / 4_200.0,
                                                  wind=7_200.0, energy=True),
}


def interp_year(table, y):
    ys = sorted(table)
    return float(np.interp(y, ys, [table[k] for k in ys]))


def nuc_of(y, nuc):
    if nuc == "原子力なし" or y < 2027:
        return "原子力なし"
    if y < 2032:
        return "泊3号"                                             # 泊3号: 2027年のできるだけ早期（北海道電力 2026/4/28）
    if nuc == "泊全基（2035〜）" and y >= 2035:
        return "泊全基"
    return "泊1・3号"                                              # 泊1号: 2030年代前半（LTDA 2025年度落札）。2032年度と置く


def sc_year(y, path):
    """path: dict(y2040=Y2040 の鍵, nuc=主|原子力なし|泊全基（2035〜）, hvdc_from=None|年, roof=None|屋根置きの比率の上書き)"""
    p40 = Y2040[path["y2040"]]
    roof = p40["roof"] if path.get("roof") is None else path["roof"]
    demand = interp_year({**DEMAND, 2040: p40["demand"]}, y)
    dc = interp_year({**DC, 2040: p40["dc"]}, y)
    wind = interp_year({**WIND, 2040: p40["wind"]}, y)
    s35 = SOLAR[2035]
    if y <= 2035:
        util, selfc = interp_year(SOLAR, y), 0.0
    else:
        inc = max(p40["solar"] - s35, 0.0) * (y - 2035) / 5.0       # 配賦の値が2035年の供給計画を下回る場合は増加0（既設は残る）
        util = s35 + (1 - roof) * inc
        # 屋根置きは自家消費（需要の減少、出力は事業用の0.85倍）。エネ基の倍率は発電量の倍率なので、屋根置きの容量を÷0.85 して発電量をそろえる
        selfc = roof * inc / (0.85 if p40["energy"] else 1.0)
    kw = dict(year=int(y), demand_gwh=demand, dc_gwh=dc, wind_mw=wind, solar_mw=util, selfcons_mw=selfc)
    # 北本の送電の上限: 2035年の公式の57万kW は東北向の運用容量100万kW（FY2028〜）から。FY2026〜27 は70万kW なので比で縮める
    kw["X_fixed"] = 570.0 * ((700.0 if y < 2028 else 1_000.0) - 300.0) / (1_000.0 - 300.0)
    kw["mimp_mw"] = (900.0 if y < 2028 else 1_200.0) - 300.0       # 受電: 北海道向の運用容量−マージン（FY2028〜120万kW）
    if path.get("hvdc_from") is not None and y >= path["hvdc_from"]:
        kw["X_fixed"] += 0.55 * 2_000.0
        kw["hvdc_mw"] = 2_000.0
        kw["mimp_mw"] += 0.55 * 2_000.0
    return m59["sc_of"](nuc_of(y, path.get("nuc", "主")), **kw)


# ---------------------------------------------------------------- 価格の組み立て（59 の build を写し、受電の上限と炭素を年ごとに入れる）
def build61(sc, carbon=0.0, markup_from=None):
    """59 の build と同じ。受電の上限 mimp_mw と炭素の費用 carbon（円/t-CO2）を加え、東北の価格を S['P_TH'] に持たせる"""
    current = sc is None
    year = 2025 if current else sc["year"]
    hv = 0.0 if current else sc.get("hvdc_mw", 0.0)
    Mimp = np.maximum(600.0, -X_ACT) if current else np.full(SH, sc.get("mimp_mw", 900.0 + 0.55 * hv))
    scc = None if current else {k: v for k, v in sc.items() if k != "mimp_mw"}
    I0 = dict(m59["inputs_cached"](scc, current))
    I0["_Mimp_day"] = Mimp.min(1)
    units, on, floor = m58["commit"](I0, year)
    I = dict(m59["inputs_cached"](scc, current, floor_arr=pd.Series(floor, index=DATES_B)))
    if current:
        dNS = np.zeros(SH)
        Mexp = np.maximum(I["X"], X_ACT)
    else:
        Ia = m59["inputs_cached"](None, True)
        dNS = (m59["supply"](I) - m59["supply"](Ia)) - (I["D"] - Ia["D"])
        Mexp = I["X"]
    caps, bids, vcs = [], [], []
    for k, u in enumerate(units):
        ft = m59["FUELTYPE"](u)
        avail = np.array(m59["AVAIL"][ft])[MONTH - 1] / 100.0
        vc = m59["vc_matrix"](u, DATES_B) + carbon * EI[ft] / 1_000.0
        vcs.append(vc)
        if u[5]:
            caps.append(u[1] * avail)
            bids.append(vc + u[4] / (m58["DSS_H"] * m58["DSS_QSHARE"] * u[1] * 1_000))
        else:
            caps.append(np.where(on[:, k][:, None], np.maximum(u[1] * avail - u[2], 0.0), 0.0))
            bids.append(np.where(on[:, k][:, None], vc, np.inf))
    B, C = np.stack(bids, 2), np.stack(caps, 2)
    if markup_from is not None:
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
    pth = P_TH0 + np.where(TFLOOR, 0.0, carbon * EI_TH / 1_000.0)
    return dict(I=I, units=units, on=on, floor=floor, Mexp=Mexp, Mimp=Mimp, Xp=X_ACT + dNS, BS=BS, CUM=np.cumsum(CS, 2),
                VCS=np.stack(vcs, 2), year=year, P_TH=pth)


# ---------------------------------------------------------------- 価格の設計
# v_bid: 再エネが限界の時間（構造の抑制、北本が詰まって火力が床を下回る時間）の価格。tohoku_floor: 東北が0.01円の時間の価格
# （None は p_TH のまま）。hydro: 水力の放流（0円）に使える割合。nuc_flex: 原子力の出力調整（定格に対する割合、0円）。
# p_last: それでも吸収しきれない時間の価格（−c_LR）。fix_split: 東北が0.01円の時間に分断の経験式を当てない（訂正）。
DESIGNS = {
    "現行": dict(v_bid=FLOOR, tohoku_floor=None, hydro=0.0, nuc_flex=0.0, p_last=FLOOR, fix_split=False, carbon=None),
    "効率": dict(v_bid=0.0, tohoku_floor=0.0, hydro=1.0, nuc_flex=0.5, p_last=0.0, fix_split=True, carbon=None),
    "効率＋炭素": dict(v_bid=0.0, tohoku_floor=0.0, hydro=1.0, nuc_flex=0.5, p_last=0.0, fix_split=True, carbon="中点"),
    "歪み（余剰の全時間 −10円）": dict(v_bid=-10.0, tohoku_floor=-10.0, hydro=0.0, nuc_flex=0.0, p_last=-10.0, fix_split=True, carbon=None),
}


def price61(S, chg, dis, dz, mode="経験式"):
    I = S["I"]
    pth = S["P_TH"]
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
        p_hi = np.maximum(SPLIT["lo"][0] + SPLIT["lo"][1] * pth, FLOOR)
        p_lo = SPLIT["hi"][0] + SPLIT["hi"][1] * pth
    else:
        p_hi = np.minimum(m59["bid_at"](S, np.maximum(T_new - floor, 0.0)), pth)
        p_lo = np.maximum(m59["bid_at"](S, np.maximum(T_up - floor, 0.0)), pth)
    p = np.where(hi, p_hi, pth)
    p = np.where(lo, p_lo, p)
    if dz["tohoku_floor"] is not None:
        p = np.where(TFLOOR & ~lo, dz["tohoku_floor"], p)
    if dz["fix_split"]:
        p = np.where(hi & TFLOOR, dz["v_bid"] if dz["tohoku_floor"] is None else dz["tohoku_floor"], p)
    p = np.where(hi & (T_new < floor), dz["v_bid"], p)
    p = np.where(rem_curt > 1e-9, dz["v_bid"], p)
    r = np.maximum(rem_def, 0.0)
    hsp = dz["hydro"] * I["Hy"]
    nf = dz["nuc_flex"] * I["N"]
    absorbed = r <= hsp + nf + 1e-9
    p_def = np.where(absorbed & ((dz["hydro"] > 0) | (dz["nuc_flex"] > 0)), dz["v_bid"], dz["p_last"])
    p = np.where(rem_def > 1e-9, p_def, p)
    last = (rem_def > 1e-9) & ~absorbed
    return p, hi, lo, last


def run61(S, dz, mode="経験式", Ks=m59["K_EVAL"]):
    """59 の run と同じ増分貪欲（刻み1万kW、各日の最安4時間に充電・最高4時間に放電）"""
    chg, dis = np.zeros(SH), np.zeros(SH)
    rows, done = [], 0.0
    yr = EVD.sum() / 365
    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            pp = price61(S, chg, dis, dz, mode)[0]
            oo = np.argsort(pp, 1)
            c4, d4 = oo[:, :4], oo[:, -4:]
            mg = np.take_along_axis(pp, d4, 1).sum(1) * ETA - np.take_along_axis(pp, c4, 1).sum(1)
            a = mg > 0
            chg[RB[a], c4[a]] += st * 10.0
            dis[RB[a], d4[a]] += st * 10.0 * ETA
            done += st
        pp, hi, lo, last = price61(S, chg, dis, dz, mode)
        d = m59["daily_eval"](pp, m59["W_B"])
        rows.append({"K(万kW)": K, "c": m59["annual"](d["c"], m59["FYB"], m59["EVB"]),
                     "負の時間(h/年)": float((pp[EVD] < -1e-9).sum() / yr),
                     "0円以下の時間(h/年)": float((pp[EVD] <= FLOOR + 1e-12).sum() / yr),
                     "吸収しきれない時間(h/年)": float(last[EVD].sum() / yr)})
    return pd.DataFrame(rows)


def pi_of(df):
    return (LAM * df["c"] - P4.W_LOSS).clip(lower=0).to_numpy(float)


# ---------------------------------------------------------------- コホートの自由参入（線形計画）
LIFE, WACC, LAG = 20, 0.06, 1


def capex_path(tau, case="主"):
    """資本費（円/kWh、4時間、工事費込み）。【暫定】発電コスト検証WG（2025/2/6）p.37〜38 の方法: 足下の単価を IEA「Batteries and
    Secure Energy Transitions」(2024) の見通し（足下から2040年に約40%低下）で下げる。足下は6.8万円（2025）。2040年以降は一定。
    資本費の調査（wf_ffeefcd0-d8b）の結果で置き換える"""
    start, cut = 68_000.0, {"主": 0.40, "低位": 0.55, "高位": 0.25}[case]
    return start * (1 - cut * min(max(tau - 2025, 0), 15) / 15.0)


def entry_lp(V, I_tau, K0=None):
    """V: {年: v_t(K)（K_EVAL 上、円/kW-年）}。I_tau: {建設年: 円/kW}。
    max Σ_t δ^t Σ_j v_{t,j} y_{t,j} − Σ_τ δ^τ I_τ k_τ  s.t. Σ_j y_{t,j} = K0_t + Σ_{τ=t−L−LAG+1}^{t−LAG} k_τ, 0≤y≤ΔK, k≥0。
    KKT 条件はコホートの自由参入の条件（NPV_τ≤0、k_τ≥0、相補性）と一致する（Lucas & Prescott 1971）"""
    years = sorted(V)
    taus = list(range(years[0] - LAG, years[-1] - LAG + 1))
    dK = np.diff(K_EVAL)
    nseg, nt, nk = len(dK), len(years), len(taus)
    nv = nk + nt * nseg
    c = np.zeros(nv)
    disc = lambda t: (1 + WACC) ** -(t - years[0])
    for i, tau in enumerate(taus):
        c[i] = disc(tau) * I_tau[tau]
    bounds = [(0, None)] * nk
    for a, t in enumerate(years):
        v = np.minimum.accumulate(V[t])                            # 区分の価値は K とともに下がる（凹）
        c[nk + a * nseg: nk + (a + 1) * nseg] = -disc(t) * (v[:-1] + v[1:]) / 2
        bounds += [(0, w) for w in dK]
    A = np.zeros((nt, nv))
    b = np.zeros(nt)
    for a, t in enumerate(years):
        A[a, nk + a * nseg: nk + (a + 1) * nseg] = 1.0
        for i, tau in enumerate(taus):
            if t - LIFE - LAG + 1 <= tau <= t - LAG:
                A[a, i] = -1.0
        b[a] = 0.0 if K0 is None else K0.get(t, 0.0)
    r = linprog(c, A_eq=A, b_eq=b, bounds=bounds, method="highs")
    assert r.status == 0, r.message
    k = dict(zip(taus, r.x[:nk]))
    Kt = {t: float(r.x[nk + a * nseg: nk + (a + 1) * nseg].sum()) for a, t in enumerate(years)}
    return k, Kt


PREM_HKD, PREM_K = 2_584.0, 106.0                                 # 北海道の上乗せ（2029年度向け: 北海道14,972−全国12,388円/kW）と、それが消える K（万kW）


def kp_of(mode):
    """容量収入 κP(K)（円/kW-年）。主＝全国連系、北海道の上乗せ込み（上乗せは K とともに線形に減り、約106万kW で0。不足91万kW÷κ0.861）、
    旧の主（北海道ブロック按分）、なし"""
    if mode == "全国連系（主）":
        return KP(K_EVAL)
    if mode == "全国連系＋北海道の上乗せ":
        return KP(K_EVAL) + P4.KP_SCALE * 0.836 * PREM_HKD * np.clip(1 - K_EVAL / PREM_K, 0, None)
    if mode == "北海道ブロック按分（旧の主）":
        return m59["KP_OLD"](K_EVAL)
    return np.zeros_like(K_EVAL)


def v_of(pi, kp="全国連系（主）"):
    """1kW あたりの年の純収益 v(K)＝π(K)＋κP(K)−運転維持費−託送等の固定費（円/kW-年）"""
    return pi + kp_of(kp) - P4.OM - P4.NET_FIX


# ---------------------------------------------------------------- 計算
YEARS = list(range(2026, 2041))
PATHS = {
    "主（2040 は OCCTO 11,000億kWh、泊の公式の時期）": dict(y2040="OCCTO 11,000億kWh", nuc="主"),
    "2040 は OCCTO 9,000億kWh": dict(y2040="OCCTO 9,000億kWh", nuc="主"),
    "2040 の太陽光はエネ基の倍率×3.0": dict(y2040="エネ基の倍率×3.0（需要は11,000億kWh）", nuc="主"),
    "エネ基×3.0・屋根置き45%（全国の配賦）": dict(y2040="エネ基の倍率×3.0（需要は11,000億kWh）", nuc="主", roof=0.45),
    "原子力なし": dict(y2040="OCCTO 11,000億kWh", nuc="原子力なし"),
    "泊全基（2035〜）": dict(y2040="OCCTO 11,000億kWh", nuc="泊全基（2035〜）"),
    "直流連系（2034〜）": dict(y2040="OCCTO 11,000億kWh", nuc="主", hvdc_from=2034),
}
EXTRA = {  # 主の経路だけで計算する設計（感応度）
    "効率＋炭素（下限）": dict(DESIGNS["効率＋炭素"], carbon="下限"),
    "効率＋炭素（上限）": dict(DESIGNS["効率＋炭素"], carbon="上限"),
    "効率（吸収しきれない時間 −10円）": dict(DESIGNS["効率"], p_last=-10.0),
    "効率（原子力は出力調整なし）": dict(DESIGNS["効率"], nuc_flex=0.0),
}
MAIN = next(iter(PATHS))
K_LTDA, LTDA_FROM = 51.0, 2028


def run_path(pname, pth, designs):
    out, PI = [], {}
    for y in YEARS:
        sc = sc_year(y, pth)
        cache = {}
        for dk, dz in designs.items():
            cb = carbon_price(y, dz["carbon"]) if dz.get("carbon") else 0.0
            if cb not in cache:
                cache[cb] = build61(sc, carbon=cb)
            df = run61(cache[cb], dz)
            pi = pi_of(df)
            PI[(dk, y)] = pi
            out.append({"経路": pname, "設計": dk, "年": y, "π(0)": pi[0], "π(20)": float(np.interp(20, K_EVAL, pi)),
                        "π(50)": float(np.interp(50, K_EVAL, pi)), "負の時間 K=0(h/年)": df["負の時間(h/年)"].iloc[0],
                        "0円以下の時間 K=0(h/年)": df["0円以下の時間(h/年)"].iloc[0],
                        "吸収しきれない時間 K=0(h/年)": df["吸収しきれない時間(h/年)"].iloc[0],
                        "炭素価格(円/t)": cb, "太陽光（事業用）MW": sc["solar_mw"], "自家消費 MW": sc.get("selfcons_mw", 0.0),
                        "風力 MW": sc["wind_mw"], "需要 GWh": sc["demand_gwh"], "原子力 MW": sc["nuclear_mw"]})
    return out, PI


def entry_paths(pname, PI, designs):
    rows = []
    for dk in designs:
        for capc in ("主", "低位", "高位"):
            for kp in ("全国連系（主）", "全国連系＋北海道の上乗せ", "北海道ブロック按分（旧の主）", "なし"):
                for ltda in (False, True):
                    for decline in (0.0, 0.01):
                        nmain = (capc != "主") + (kp != "全国連系（主）") + ltda + (decline > 0)
                        if (nmain and pname != MAIN) or nmain > 1:
                            continue
                        V = {}
                        for t in range(YEARS[0], 2076):
                            base = PI[(dk, min(t, YEARS[-1]))]
                            fac = (1 - decline) ** max(t - YEARS[-1], 0)
                            V[t] = v_of(base * fac, kp)
                        I_tau = {tau: 4 * capex_path(tau, capc) for tau in range(YEARS[0] - LAG, 2076)}
                        K0 = {t: (K_LTDA if LTDA_FROM <= t < LTDA_FROM + LIFE else 0.0) for t in V} if ltda else None
                        k, Kt = entry_lp(V, I_tau, K0)
                        first = next((t for t in sorted(Kt) if Kt[t] - (K0 or {}).get(t, 0.0) > 0.5), None)
                        rows.append({"経路": pname, "設計": dk, "資本費の経路": capc, "容量収入": kp,
                                     "LTDA 51万kW 先行": ltda, "2041年以降の収益の低下（年）": decline, "最初の参入年": first,
                                     **{f"K {t}(万kW)": Kt[t] for t in (2027, 2030, 2035, 2040, 2045)}})
    return rows


if __name__ == "__main__":
    import time
    t0 = time.time()
    PIR, ENT, SAVE = [], [], {}
    for pname, pth in PATHS.items():
        ds = {**DESIGNS, **(EXTRA if pname == MAIN else {})}
        out, PI = run_path(pname, pth, ds)
        PIR += out
        SAVE.update({f"{pname}|{dk}|{y}": v for (dk, y), v in PI.items()})
        ENT += entry_paths(pname, PI, ds)
        print(f"{pname}: {time.time() - t0:.0f}s", flush=True)
    np.savez_compressed(os.path.join(PROC, "signal_market_pik.npz"), K=K_EVAL, **SAVE)
    PIRD, ENTD = pd.DataFrame(PIR), pd.DataFrame(ENT)
    PIRD.round(3).to_csv(os.path.join(PROC, "signal_market_pi.csv"), index=False, encoding="utf-8-sig")
    ENTD.round(3).to_csv(os.path.join(PROC, "signal_market_entry.csv"), index=False, encoding="utf-8-sig")
    show = PIRD[PIRD["年"].isin([2026, 2030, 2035, 2040])].pivot_table(index=["経路", "設計"], columns="年", values="π(0)", sort=False)
    print("\nπ(0)（円/kW-年）"); print(show.round(0).to_string())
    print("\n均衡の容量（主の資本費・容量収入あり・LTDA なし・2041年以降一定）")
    e = ENTD[(ENTD["資本費の経路"] == "主") & (ENTD["容量収入"] == "全国連系（主）") & (~ENTD["LTDA 51万kW 先行"]) & (ENTD["2041年以降の収益の低下（年）"] == 0)]
    print(e.drop(columns=["資本費の経路", "容量収入", "LTDA 51万kW 先行", "2041年以降の収益の低下（年）"]).round(1).to_string(index=False))
