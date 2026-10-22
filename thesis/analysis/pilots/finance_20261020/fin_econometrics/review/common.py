#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""共通: analysis/24_vol_verification.py の build_daily / 右辺の作り方を読み取り専用で複製。
リポジトリのデータは読むだけ。出力はすべてこのディレクトリ配下 (out/)。
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO = "/Users/matsuba/work/thesis"
PROC = os.path.join(REPO, "data", "processed")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# 24_vol_verification.py と同一の季節区分
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}
MAIN_SEASONS = ["夏", "冬", "春秋"]


def load_hourly(area):
    return pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])


def build_daily(area, pcol, fy_min=2016, fy_max=2025, return_matrix=False):
    """24_vol_verification.build_daily と同一ロジック（＋24時間価格行列を返すオプション）"""
    p = load_hourly(area)
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
    d["top4"] = srt[:, -4:].mean(axis=1)
    d["bot4"] = srt[:, :4].mean(axis=1)
    d["solar"] = p.groupby("day")["solar_pre"].sum() / 1000   # GWh/日
    d["wind"] = p.groupby("day")["wind_pre"].sum() / 1000
    d["demand"] = p.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    d = d[(d["fy"] >= fy_min) & (d["fy"] <= fy_max)].dropna()
    if return_matrix:
        return d, P.loc[d.index]
    return d


def design(d):
    """24_vol_verification.run_reg と同一の右辺"""
    X = pd.DataFrame(index=d.index)
    for s in MAIN_SEASONS:
        m = (d["season"] == s).astype(float)
        X[f"solar_{s}"] = d["solar"] * m
        X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X,
                   pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    return sm.add_constant(X)


KEYS = [f"{src}_{s}" for s in MAIN_SEASONS for src in ("solar", "wind")]


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
