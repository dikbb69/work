# -*- coding: utf-8 -*-
"""付録B.1 第1の確かめ（基準シナリオ、2026-11-03 に基準の前提で解き直し）: 起動と上乗せを固定し、無作為の25日で式4.7 を汎用の線形計画でも解いて目的関数の値を比べる"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import numpy as np
from scipy.optimize import linprog
from model import params as PR, merit as MO, simple as SM, balance as B, battery as BT

sc = PR.SCENARIOS["主"]
import pandas as pd, os
_M = pd.read_csv(os.path.join(ROOT, "data", "processed", "v2_path_metrics.csv"))
_M = _M[(_M["シナリオ"] == "主") & _M["場合"].str.startswith("スポット")]
MU = {int(r["年"]): round(float(r["上乗せ μ(円/kWh)"]), 2) for _, r in _M.iterrows()}
eta = PR.ETA
for y, mu in ((2035, MU[2035]), (2040, MU[2040])):   # 基準の経路の上の μ（v2_path_metrics.csv、スポットで回収）
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    units = SM.with_mustrun(B.fleet(y))
    nd = I["D"].shape[0]
    on, cap = SM.commit(I, units, np.zeros((nd, 24)), np.zeros((nd, 24)))
    fixed = lambda I_, u_, c_, d_: (on, cap)
    q0, E_, V = MO.supply_curve(I, units, commit_fn=fixed)
    V = np.where(V > PR.FLOOR + 0.001, np.minimum(V + mu, PR.PRICE_CAP), V)

    def cost(q, d):
        out = 0.0
        for h in range(24):
            lo, hi = E_[d, h, :-1], E_[d, h, 1:]
            a, b = min(q0[d, h], q[h]), max(q0[d, h], q[h])
            seg = np.clip(np.minimum(hi, b) - np.maximum(lo, a), 0, None)
            out += np.sign(q[h] - q0[d, h]) * (seg * V[d, h]).sum()
        return out

    rng = np.random.default_rng(1)
    days = rng.choice(nd, 25, replace=False)
    for Kman in (10, 100, 400, 800):
        P = Kman * 10.0
        chg, dis = BT.fleet_schedule(q0, E_, V, P)
        worst, worst_rel, scale = 0.0, 0.0, 0.0
        for d in days:
            lo, hi = E_[d, :, :-1], E_[d, :, 1:]
            a = np.clip(np.minimum(hi, q0[d][:, None] + P) - np.maximum(lo, q0[d][:, None]), 0, None).ravel()
            b = (np.clip(np.minimum(hi, q0[d][:, None]) - np.maximum(lo, q0[d][:, None] - eta * P), 0, None) / eta).ravel()
            v = V[d].ravel(); m = len(v)
            c = np.concatenate([v, -eta * v])
            A_eq = np.concatenate([np.ones(m), -np.ones(m)])[None, :]
            A_ub = np.concatenate([np.ones(m), np.zeros(m)])[None, :]
            res = linprog(c, A_ub=A_ub, b_ub=[PR.HOURS * P], A_eq=A_eq, b_eq=[0.0],
                          bounds=list(zip(np.zeros(2 * m), np.concatenate([a, b]))), method="highs")
            g = cost(q0[d] + chg[d] - dis[d], d)
            worst = max(worst, abs(g - res.fun))
            scale = max(scale, abs(res.fun))
            assert abs(chg[d].sum() * eta - dis[d].sum()) < 1e-6 and chg[d].sum() <= PR.HOURS * P + 1e-6
            assert (np.minimum(chg[d], dis[d]) < 1e-9).all() and chg[d].max() <= P + 1e-6 and dis[d].max() <= eta * P + 1e-6
        print(f"{y} μ={mu} K={Kman}万kW: 25日の目的関数の差 最大 {worst:.6f}（MWh×円/kWh、1日）、線形計画の目的関数の大きさ 最大 {scale:.1f}、"
              f"相対 {worst / max(scale, 1e-9):.2e}、同時の充放電 {np.minimum(chg, dis).sum():.3f}MW、放電/充電 {dis.sum() / max(chg.sum(), 1e-9):.6f}", flush=True)
