#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""コホートの自由参入均衡の経路（2026〜2040年の π_t(K) は 61 の signal_market_pik.npz）。資本費の経路と容量収入の置き方を動かす

資本費: params_v4.capex_path（発電コスト検証WG と同じ方法: 足下の単価×IEA BSET の4時間の低下率。低位・高位は NREL 2025 Update）。
  足下は FY2025 の系統用の加重平均4.8万円/kWh（主）と単純平均6.7万円。建設の1年後から20年運転。廃止費（建設費の5%）は20年目に払う。
運転維持費5,000円/kW-年、託送等の固定費は params_v4（NET_FIX）。π_t(K) は充電の従量費を差し引いた値（61 の pi_of）。
容量収入 κP(K)（κ＝0.861、起点は2029年度向けの北海道14,972円/kW）:
  (a) 現状の水準で一定、(b) 北海道だけが参入（全国連系の需要曲線を北海道の K の分だけ動かす）、
  (c) 全国の参入がエリア別の系統用蓄電池の契約申込の分布に比例（全国2,868.8÷北海道176.0万kW、エネ庁 次世代電力系統WG 第7回 資料1-1、2025/12/25）、
  (d) 全国の参入が H3 需要の比（16,208÷529）に比例（旧の主）。
  需要曲線は2030年度向け（上限30,700・指標価格20,911円/kW、OCCTO 2026/7/30）を、2029年度向けの数量軸に置いた近似（42 と同じ）。
均衡: 61 の entry_lp（Lucas & Prescott 1971 の等価な凹計画）。2041年以降の収益は2040年の値（感応度は年1% 低下）。
出力: data/processed/entry_path_results.csv、entry_path_required_kp.csv（2040年に80万kW に届くのに要る容量収入）
"""
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

Z = np.load(os.path.join(PROC, "signal_market_pik.npz"))
K = Z["K"]
KEYS = [k for k in Z.files if k != "K"]
PATHS = list(dict.fromkeys(k.split("|")[0] for k in KEYS))
YEARS = sorted({int(k.split("|")[2]) for k in KEYS})
LIFE, LAG, WACC, HORIZON = 20, 1, 0.06, 2100                      # 期間の打ち切りの影響を避けるため2100年まで（報告は2045年まで）

# ---------------------------------------------------------------- 容量収入
CURVE30 = {"ceil": 30_700.0, "cone": 20_911.0}
Q_CAP, Q_TGT, Q_ZERO = 188_813_656.0, 189_966_340.0, 195_652_080.0
KAP, P0 = 0.861, 14_952.0


def curve_p(q):
    q = np.asarray(q, float)
    up = CURVE30["ceil"] - (CURVE30["ceil"] - CURVE30["cone"]) * (q - Q_CAP) / (Q_TGT - Q_CAP)
    lo = CURVE30["cone"] * (Q_ZERO - q) / (Q_ZERO - Q_TGT)
    return np.where(q <= Q_CAP, CURVE30["ceil"], np.where(q <= Q_TGT, up, np.maximum(lo, 0.0)))


Q0 = Q_TGT + (CURVE30["cone"] - P0) / CURVE30["cone"] * (Q_ZERO - Q_TGT)
KPM = {"(a) 現状の水準で一定": np.full_like(K, KAP * P0),
       "(b) 北海道だけ参入": KAP * curve_p(Q0 + KAP * K * 1e4),
       "(c) 全国は接続申込の分布に比例": KAP * curve_p(Q0 + KAP * K * 1e4 * 2_868.8 / 176.0),
       "(d) 全国は H3 需要に比例（旧の主）": KAP * curve_p(Q0 + KAP * K * 1e4 * 16_208 / 529)}


# ---------------------------------------------------------------- 線形計画（61 と同じ）
def entry_lp(V, I_tau, K0=None):
    years = sorted(V)
    taus = list(range(years[0] - LAG, years[-1] - LAG + 1))
    dK = np.diff(K)
    nseg, nt, nk = len(dK), len(years), len(taus)
    nv = nk + nt * nseg
    c = np.zeros(nv)
    disc = lambda t: (1 + WACC) ** -(t - years[0])
    for i, tau in enumerate(taus):
        c[i] = disc(tau) * I_tau[tau]
    bounds = [(0, None)] * nk
    for a, t in enumerate(years):
        v = np.minimum.accumulate(V[t])
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
    Kt = {t: float(r.x[nk + a * nseg: nk + (a + 1) * nseg].sum()) for a, t in enumerate(years)}
    return dict(zip(taus, r.x[:nk])), Kt


def solve(path, design, cap="主", start=48_000.0, kp="(b) 北海道だけ参入", ltda=False, decline=0.0, kp_add=0.0):
    V = {}
    for t in range(YEARS[0], HORIZON + 1):
        pi = Z[f"{path}|{design}|{min(t, YEARS[-1])}"] * (1 - decline) ** max(t - YEARS[-1], 0)
        V[t] = pi + KPM[kp] + kp_add - P4.OM_BASE - P4.NET_FIX
    I_tau = {tau: 4 * P4.capex_path(tau, cap, start) * (1 + 0.05 / 1.06 ** 20) for tau in range(YEARS[0] - LAG, HORIZON + 1)}
    K0 = {t: (51.0 if 2028 <= t < 2048 else 0.0) for t in V} if ltda else None
    k, Kt = entry_lp(V, I_tau, K0)
    base = K0 or {}
    first = next((t for t in sorted(Kt) if Kt[t] - base.get(t, 0.0) > 0.5), None)
    return first, {t: Kt[t] - base.get(t, 0.0) for t in Kt}


def required_kp(path, design, target=80.0, year=2040, **kw):
    """year 年に市場参入の容量が target 万kW に届くのに要る、K によらない一定の容量収入の上乗せ（円/kW-年。(a) に足す）"""
    lo, hi = -15_000.0, 30_000.0
    if solve(path, design, kp="(a) 現状の水準で一定", kp_add=hi, **kw)[1][year] < target:
        return np.nan
    for _ in range(25):
        mid = (lo + hi) / 2
        if solve(path, design, kp="(a) 現状の水準で一定", kp_add=mid, **kw)[1][year] >= target:
            hi = mid
        else:
            lo = mid
    return KAP * P0 + hi


if __name__ == "__main__":
    MAIN = PATHS[0]
    DES = ["現行", "効率", "効率＋炭素", "歪み（余剰の全時間 −10円）"]
    rows = []
    for path in PATHS:
        for design in DES:
            combos = [dict()]
            if path == MAIN:
                combos += [dict(cap="低位"), dict(cap="高位"), dict(start=67_000.0), dict(ltda=True), dict(decline=0.01)]
                combos += [dict(kp=m) for m in KPM if m != "(b) 北海道だけ参入"]
            for kw in combos:
                first, Kt = solve(path, design, **kw)
                rows.append({"経路": path, "設計": design, "資本費の経路": kw.get("cap", "主"),
                             "足下の単価(万円/kWh)": kw.get("start", 48_000.0) / 1e4, "容量収入": kw.get("kp", "(b) 北海道だけ参入"),
                             "LTDA 51万kW 先行": kw.get("ltda", False), "2041年以降の低下（年）": kw.get("decline", 0.0),
                             "最初の参入年": first, **{f"K {t}": Kt[t] for t in (2030, 2035, 2040, 2045)}})
    R = pd.DataFrame(rows)
    R.round(2).to_csv(os.path.join(PROC, "entry_path_results.csv"), index=False, encoding="utf-8-sig")
    print("均衡の経路（市場参入の容量、万kW）")
    print(R.round(1).to_string(index=False))
    REQ = []
    for path in PATHS:
        for design in DES:
            for cap in (("主", "低位", "高位") if path == MAIN else ("主",)):
                REQ.append({"経路": path, "設計": design, "資本費の経路": cap,
                            "2040年に80万kW に要る容量収入 κP(円/kW-年)": required_kp(path, design, cap=cap),
                            "2035年に50万kW に要る容量収入 κP(円/kW-年)": required_kp(path, design, target=50.0, year=2035, cap=cap)})
    Q = pd.DataFrame(REQ)
    Q["参考: κ×指標価格（2030年度向け Net CONE 20,911円）"] = KAP * 20_911
    Q.round(0).to_csv(os.path.join(PROC, "entry_path_required_kp.csv"), index=False, encoding="utf-8-sig")
    print("\n計画上の想定量に届くのに要る容量収入（K によらない一定の κP）")
    print(Q.round(0).to_string(index=False))
