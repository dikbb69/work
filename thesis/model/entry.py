# -*- coding: utf-8 -*-
"""参入の均衡

主（PR.ENTRY_RULE＝"myopic"、著者の決定 2026-10-28）: 年 t ごとに、その年の1kW の純収益 v_t(K)（π＋κ×容量価格−運転維持費−託送等）が、
その年に運転を始める蓄電池の年あたりの建設費 A_t＝I_{t−LAG}×WACC/(1−(1+WACC)^−LIFE) を上回る量 K*_t まで入る。
入った蓄電池は寿命まで残る（量は K_t＝max(先に入っている量＋残っているコホート, K*_t)）。建設費の将来の低下を待つ判断（延期のオプション）は置かない。

前の主（"lp"）: コホートの自由参入（建設年ごとに NPV≤0、参入≥0、相補性）。等価な凹計画（Lucas & Prescott 1971）を線形計画で解く:
  max Σ_t δ^t Σ_j v_{t,j} y_{t,j} − Σ_τ δ^τ I_τ k_τ
  s.t. Σ_j y_{t,j} ＝ K0_t ＋ Σ_{τ＝t−L−LAG+1}^{t−LAG} k_τ、0≤y_{t,j}≤ΔK_j、k_τ≥0
v_{t,j} は年 t の量の区分 j での1kW の純収益（π＋容量収入−運転維持費−託送等の固定費）。区分の価値は K とともに下がるよう単調にする
"""
import numpy as np
from scipy.optimize import linprog

from . import params as PR


def solve(V, I_tau, K, K0=None):
    """V: {年: 格子 K 上の純収益（円/kW-年）}、I_tau: {建設年: 円/kW}。戻り値: ({建設年: 万kW}, {年: 合計 万kW})"""
    years = sorted(V)
    taus = list(range(years[0] - PR.LAG, years[-1] - PR.LAG + 1))
    dK = np.diff(K)
    nseg, nt, nk = len(dK), len(years), len(taus)
    nv = nk + nt * nseg
    c = np.zeros(nv)
    disc = lambda t: (1 + PR.WACC) ** -(t - years[0])
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
            if t - PR.LIFE - PR.LAG + 1 <= tau <= t - PR.LAG:
                A[a, i] = -1.0
        b[a] = 0.0 if K0 is None else K0.get(t, 0.0)
    r = linprog(c, A_eq=A, b_eq=b, bounds=bounds, method="highs")
    assert r.status == 0, r.message
    return dict(zip(taus, r.x[:nk])), {t: float(r.x[nk + a * nseg: nk + (a + 1) * nseg].sum()) for a, t in enumerate(years)}


def ltda_stock(t):
    return sum(v for y0, v in PR.LTDA_BATT.items() if y0 <= t < y0 + PR.LIFE)


def preset_stock(t, ltda=True):
    """先に入っている蓄電池（万kW、設備）: 既設（2026年から20年）＋LTDA"""
    return (PR.BATT_EXISTING if 2026 <= t < 2046 else 0.0) + (ltda_stock(t) if ltda else 0.0)


def annual_cost(t, capex_case="主", capex_start=None):
    """年 t に運転を始める蓄電池の年あたりの建設費（円/kW-年）。建設は t−LAG 年、廃止費を含む"""
    I = PR.HOURS * PR.capex(t - PR.LAG, capex_case, capex_start) * (1 + PR.DECOM / (1 + PR.WACC) ** PR.LIFE)
    return I * PR.WACC / (1 - (1 + PR.WACC) ** -PR.LIFE)


def _net_value(pi_by_year, cap_price_after2030, cap_price_fn, kappa_by_year):
    """年ごとの1kW の純収益の曲線 v_t(K)（2041年以降は最後の5年の平均の π）"""
    ys = sorted(pi_by_year)
    cp = cap_price_fn or (lambda t: PR.cap_price(t, cap_price_after2030))
    tail = np.mean([pi_by_year[y] for y in ys if y > ys[-1] - PR.TAIL_YEARS], axis=0)   # 最後の年より後は、最後の5年の平均
    pick = lambda t: tail if t > ys[-1] else pi_by_year[max([y for y in ys if y <= t] or [ys[0]])]
    if kappa_by_year is None:
        kap = lambda t: PR.KAPPA_BATT
    else:
        kys = sorted(kappa_by_year)
        ktail = np.mean([kappa_by_year[y] for y in kys if y > kys[-1] - PR.TAIL_YEARS], axis=0)
        kap = lambda t: ktail if t > kys[-1] else kappa_by_year[max([y for y in kys if y <= t] or [kys[0]])]
    return {t: pick(t) + kap(t) * cp(t) - PR.OM - PR.NET_FIX for t in range(ys[0], PR.HORIZON + 1)}


def path(pi_by_year, K, cap_price_after2030=14_972.0, capex_case="主", capex_start=None, ltda=True, cap_price_fn=None, kappa_by_year=None,
         rule=None):
    """π の年別の曲線から、量の経路を解く（戻り値: {年: 合計 万kW}）。容量収入は κ×その年の容量価格（2029年度まで実績、以後は据え置き）。
    kappa_by_year: 年ごとの κ の曲線（K の格子の上、量に応じた実効値）。None なら PR.KAPPA_BATT で一定。rule: None なら PR.ENTRY_RULE"""
    f = path_lp if (rule or PR.ENTRY_RULE) == "lp" else path_myopic
    return f(pi_by_year, K, cap_price_after2030, capex_case, capex_start, ltda, cap_price_fn, kappa_by_year)


def path_myopic(pi_by_year, K, cap_price_after2030=14_972.0, capex_case="主", capex_start=None, ltda=True, cap_price_fn=None, kappa_by_year=None):
    """その年の純収益が年あたりの建設費を上回る量まで入る（建設費の将来の低下は見込まない）。格子の上限（800万kW）以上は上限と書く"""
    V = _net_value(pi_by_year, cap_price_after2030, cap_price_fn, kappa_by_year)
    K = np.asarray(K, float)
    cohorts, Kt = {}, {}
    for t in sorted(V):
        v = np.minimum.accumulate(V[t])                        # 量とともに下がる形にする
        A = annual_cost(t, capex_case, capex_start)
        if v[0] < A:
            k_star = 0.0
        elif v[-1] >= A:
            k_star = float(K[-1])
        else:
            j = int(np.argmax(v < A))                          # v[j-1] ≥ A > v[j]
            k_star = float(K[j - 1] + (K[j] - K[j - 1]) * (v[j - 1] - A) / (v[j - 1] - v[j]))
        stock = preset_stock(t, ltda) + sum(c for s, c in cohorts.items() if s <= t < s + PR.LIFE)
        cohorts[t] = max(k_star - stock, 0.0)
        Kt[t] = min(stock + cohorts[t], float(K[-1]))
    return Kt


def path_lp(pi_by_year, K, cap_price_after2030=14_972.0, capex_case="主", capex_start=None, ltda=True, cap_price_fn=None, kappa_by_year=None):
    """前の主: 建設費の低下まで見込んだ完全予見の自由参入（線形計画）"""
    V = _net_value(pi_by_year, cap_price_after2030, cap_price_fn, kappa_by_year)
    I_tau = {tau: PR.HOURS * PR.capex(tau, capex_case, capex_start) * (1 + PR.DECOM / (1 + PR.WACC) ** PR.LIFE)
             for tau in range(min(pi_by_year) - PR.LAG, PR.HORIZON + 1)}
    K0 = {t: preset_stock(t, ltda) for t in V}
    k, Kt = solve(V, I_tau, K, K0)
    return Kt
