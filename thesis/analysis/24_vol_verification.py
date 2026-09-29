#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""①「再エネ→価格ボラ上昇」の北海道検証（Fuke & Ohashi 型の回帰・風力拡張）

仕様:
  日次パネル（FY2016-25）で、水準と変動性を再エネ日次発電量（制御前）に回帰
    y_d = Σ_s [β_s^solar·Solar_d + β_s^wind·Wind_d]·1{season=s} + γ·Demand_d + FY固定効果 + 季節固定効果 + ε
  y: 日平均価格（水準）／ 日内標準偏差・TB4hスプレッド（変動性2種）
  FY固定効果が燃料価格等の年次水準シフトを吸収し、年度内変動で識別。HC3頑健標準誤差
  九州でも同一仕様を推定（Fuke & Ohashi の対象市場でのクロスチェック）

出力: data/processed/vol_regression_results.csv ＋ 標準出力の係数表
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")

SEASON_MAP = {7: "夏", 8: "夏", 12: "冬", 1: "冬", 2: "冬",
              4: "春秋", 5: "春秋", 10: "春秋", 11: "春秋",
              3: "端境", 6: "端境", 9: "端境"}
MAIN_SEASONS = ["夏", "冬", "春秋"]


def build_daily(area, pcol):
    p = pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=[pcol]).copy()
    p["day"] = p["ts"].dt.normalize()
    p["hour"] = p["ts"].dt.hour
    cnt = p.groupby("day")["hour"].count()
    p = p[p["day"].isin(cnt[cnt == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    P = p.pivot(index="day", columns="hour", values=pcol)
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["mean_p"] = P.mean(axis=1)
    d["sd"] = P.std(axis=1)
    d["tb4"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
    d["solar"] = p.groupby("day")["solar_pre"].sum() / 1000   # GWh/日
    d["wind"] = p.groupby("day")["wind_pre"].sum() / 1000
    d["demand"] = p.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    return d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()


def run_reg(d, ycol):
    X = pd.DataFrame(index=d.index)
    for s in MAIN_SEASONS + ["端境"]:
        m = (d["season"] == s).astype(float)
        X[f"solar_{s}"] = d["solar"] * m
        X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X,
                   pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    X = sm.add_constant(X)
    res = sm.OLS(d[ycol], X).fit(cov_type="HC3")
    out = []
    for s in MAIN_SEASONS:
        for src in ("solar", "wind"):
            k = f"{src}_{s}"
            out.append({"係数": k, "推定値": res.params[k], "SE": res.bse[k],
                        "p値": res.pvalues[k]})
    return pd.DataFrame(out), res.rsquared


all_rows = []
for area, pcol in [("hokkaido", "p_hokkaido"), ("kyushu", "p_kyushu")]:
    d = build_daily(area, pcol)
    print(f"\n===== {area}（n={len(d)}日, FY2016-25） =====")
    for ycol, lab in [("mean_p", "水準: 日平均価格"), ("sd", "変動性: 日内SD"), ("tb4", "変動性: TB4hスプレッド")]:
        tab, r2 = run_reg(d, ycol)
        tab.insert(0, "被説明変数", lab)
        tab.insert(0, "エリア", area)
        all_rows.append(tab)
        print(f"\n--- {lab}（R²={r2:.3f}、円/kWh per GWh/日） ---")
        disp = tab.copy()
        disp["推定値"] = disp["推定値"].round(3)
        disp["SE"] = disp["SE"].round(3)
        disp["有意"] = np.where(disp["p値"] < 0.01, "***", np.where(disp["p値"] < 0.05, "**", np.where(disp["p値"] < 0.1, "*", "")))
        print(disp[["係数", "推定値", "SE", "有意"]].to_string(index=False))

res = pd.concat(all_rows, ignore_index=True)
res.to_csv(os.path.join(PROC, "vol_regression_results.csv"), index=False)
print("\nsaved vol_regression_results.csv")
