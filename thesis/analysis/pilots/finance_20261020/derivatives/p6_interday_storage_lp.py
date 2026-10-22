#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット6: 日をまたぐ持ち越し（日間スプレッド・オプション）とサイクル予算（スイング・オプション）の上限値
価格テイカー・完全予見の線形計画（1kW、容量 E=h kWh、往復効率0.85を放電側に一括、60分粒度）で、
  (a) 毎日 SoC=0 に戻す＋1日の充電量 ≤ E（本研究の1日1サイクルに充放電順序を加えたもの）
  (b) 日をまたぐ持ち越し可＋1日の充電量 ≤ E
  (c) 持ち越し可＋年間の充電量 ≤ 365·E（サイクル予算をどの日に使うかを選べる＝スイング型）
  (d) 持ち越し可・サイクル無制限
を FY2023〜25、h=4・8・24 時間で解き、(b)−(a) を「日間の持ち越しの価値」、(c)−(b) を「サイクル配分の価値」とする。
上限値（完全予見）であり実行可能な価値ではない。出力: p6_interday_lp.csv
"""
import os

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, hstack, vstack, identity, csr_matrix

OUT = os.path.dirname(os.path.abspath(__file__))
PANEL = "/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv"
ETA = 0.85

hp = pd.read_csv(PANEL, parse_dates=["ts"])
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)
hp["day"] = hp["ts"].dt.normalize()
cnt = hp.dropna(subset=["p_hokkaido"]).groupby("day")["ts"].count()
full = cnt[cnt == 24].index


def solve(p, day_id, E, reset, per_day_cap, annual_cap):
    T = len(p)
    # 変数 x = [c(0..T-1), d(0..T-1), s(0..T-1)]
    cost = np.concatenate([p, -ETA * p, np.zeros(T)])
    # SoC: s_t − s_{t−1} − c_t + d_t = 0
    I = identity(T, format="csr")
    shift = coo_matrix((np.ones(T - 1), (np.arange(1, T), np.arange(0, T - 1))), shape=(T, T)).tocsr()
    A_eq = hstack([-I, I, I - shift]).tocsr()
    b_eq = np.zeros(T)
    A_ub, b_ub = [], []
    days_u, inv = np.unique(day_id, return_inverse=True)
    nd = len(days_u)
    if per_day_cap:
        M = coo_matrix((np.ones(T), (inv, np.arange(T))), shape=(nd, T)).tocsr()
        A_ub.append(hstack([M, csr_matrix((nd, 2 * T))]))
        b_ub.append(np.full(nd, E))
    if annual_cap:
        A_ub.append(hstack([csr_matrix(np.ones((1, T))), csr_matrix((1, 2 * T))]))
        b_ub.append(np.array([365.0 * E * nd / 365.0]))
    bounds_s = [(0, E)] * T
    if reset:
        last = np.r_[np.where(np.diff(inv) != 0)[0], T - 1]
        for t in last:
            bounds_s[t] = (0, 0)
    bounds = [(0, 1)] * (2 * T) + bounds_s
    res = linprog(cost, A_ub=vstack(A_ub).tocsr() if A_ub else None, b_ub=np.concatenate(b_ub) if b_ub else None,
                  A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    assert res.status == 0, res.message
    c = res.x[:T]
    return -res.fun, c.sum() / E / nd


rows = []
for fy in [2023, 2024, 2025]:
    d = hp[(hp["fy"] == fy) & hp["day"].isin(full)].sort_values("ts")
    p = d["p_hokkaido"].to_numpy()
    day_id = d["day"].to_numpy()
    for h in [4, 8, 24]:
        out = {"FY": fy, "h": h}
        for key, kw in {"(a)毎日リセット・1日1サイクル": dict(reset=True, per_day_cap=True, annual_cap=False),
                        "(b)持ち越し・1日1サイクル": dict(reset=False, per_day_cap=True, annual_cap=False),
                        "(c)持ち越し・年間サイクル予算": dict(reset=False, per_day_cap=False, annual_cap=True),
                        "(d)持ち越し・無制限": dict(reset=False, per_day_cap=False, annual_cap=False)}.items():
            v, cyc = solve(p, day_id, float(h), **kw)
            out[key] = v
            out[key + "_サイクル/日"] = cyc
        rows.append(out)
        print(out, flush=True)
res = pd.DataFrame(rows)
res["持ち越しの価値(b-a)"] = res["(b)持ち越し・1日1サイクル"] - res["(a)毎日リセット・1日1サイクル"]
res["サイクル配分の価値(c-b)"] = res["(c)持ち越し・年間サイクル予算"] - res["(b)持ち越し・1日1サイクル"]
res.to_csv(os.path.join(OUT, "p6_interday_lp.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250)
cols = ["FY", "h", "(a)毎日リセット・1日1サイクル", "(b)持ち越し・1日1サイクル", "(c)持ち越し・年間サイクル予算",
        "(d)持ち越し・無制限", "持ち越しの価値(b-a)", "サイクル配分の価値(c-b)", "(d)持ち越し・無制限_サイクル/日"]
print(res[cols].round(0).to_string(index=False))
print(res.groupby("h")[cols[2:]].mean().round(0).to_string())
