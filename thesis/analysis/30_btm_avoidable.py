#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""9.3.2 併設（BTM）蓄電池の容量制約下での抑制回避可能率（北海道風力、2025/4〜2026/6 の時間値）

  ・抑制イベントの日内分布・持続時間・設備容量比の記述統計
  ・フリート集約 SoC シミュレーション: 併設 E kWh/kW（P kW/kW）で抑制電力量をどれだけ吸収できるか
      一様分布（全サイトが同じ抑制率）と、集中分布（容量シェア20%のサイトに抑制の77%: Maji et al. 2025 の ERCOT 分布を援用）
出力: data/processed/btm_avoidable_share.csv、標準出力
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROC = os.path.join(ROOT, "data", "processed")
T0, T1 = "2025-04-01", "2026-07-01"

p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
cap = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
cap = cap[cap["area"] == "hokkaido"].set_index("date")["wind_kw"]
full = pd.date_range(cap.index.min(), pd.Timestamp("2026-06-30"), freq="ME")
cap = cap.reindex(full.union(cap.index)).ffill()
p["wind_kw"] = p["ts"].dt.to_period("M").dt.to_timestamp("M").map(cap)
p = p[(p["ts"] >= T0) & (p["ts"] < T1)].copy()
p["curt"] = p["wind_curt"].fillna(0.0)

print(f"期間 {T0}〜{T1}: 抑制電力量 {p['curt'].sum():,.0f} MWh、抑制時間 {(p['curt'] > 0).sum()} h、風力容量(平均) {p['wind_kw'].mean() / 1e4:.1f} 万kW")
hod = p.groupby(p["ts"].dt.hour)["curt"].sum(); hod = (hod / hod.sum() * 100).round(1)
print("抑制電力量の時刻別シェア(%):", {h: v for h, v in hod.items() if v > 0})
ev = (p["curt"] > 0).astype(int); grp = (ev.diff() != 0).cumsum()
dur = p[ev == 1].groupby(grp[ev == 1]).agg(h=("curt", "size"), mwh=("curt", "sum"))
print(f"イベント数 {len(dur)}、持続時間 中央値 {dur['h'].median():.0f}h 平均 {dur['h'].mean():.1f}h 最大 {dur['h'].max()}h、電力量加重平均 {(dur['h'] * dur['mwh']).sum() / dur['mwh'].sum():.1f}h")
print(f"持続≤4h の電力量シェア {dur.loc[dur['h'] <= 4, 'mwh'].sum() / dur['mwh'].sum() * 100:.1f}%、≤8h {dur.loc[dur['h'] <= 8, 'mwh'].sum() / dur['mwh'].sum() * 100:.1f}%")
share = p.loc[p["curt"] > 0, "curt"] / (p.loc[p["curt"] > 0, "wind_kw"] / 1000)
print(f"抑制時の抑制量/設備容量: 中央値 {share.median() * 100:.1f}% 平均 {share.mean() * 100:.1f}% p90 {share.quantile(.9) * 100:.1f}%")


def avoid(E_kwh_per_kw, P_kw_per_kw, conc=1.0):
    """conc = 抑制シェア÷容量シェア（1=一様）。集中群は蓄電池を 1/conc に縮小して評価するのと等価"""
    E = E_kwh_per_kw / 1000 * p["wind_kw"].to_numpy() / conc
    P = P_kw_per_kw / 1000 * p["wind_kw"].to_numpy() / conc
    c = p["curt"].to_numpy(); soc = charged = 0.0
    for i in range(len(c)):
        if c[i] > 0:
            ch = min(c[i], P[i], E[i] - soc); soc += ch; charged += ch
        else:
            soc = max(0.0, soc - P[i])
    return charged / c.sum()


rows = []
for E, P, lab in ((0.64, 0.16, "0.64kWh/kW・4h"), (0.64, 0.32, "0.64kWh/kW・2h"), (1.28, 0.32, "1.28kWh/kW・4h"), (2.0, 0.5, "2.0kWh/kW・4h")):
    u = avoid(E, P)
    conc = 0.77 * avoid(E, P, conc=0.77 / 0.2) + 0.23 * avoid(E, P, conc=0.23 / 0.8)
    rows.append({"併設仕様": lab, "E(kWh/kW)": E, "P(kW/kW)": P, "回避可能率_一様(%)": round(u * 100, 1), "回避可能率_集中20%/77%(%)": round(conc * 100, 1)})
    print(rows[-1])
out = pd.DataFrame(rows)
out.to_csv(os.path.join(PROC, "btm_avoidable_share.csv"), index=False)
print("saved btm_avoidable_share.csv")
