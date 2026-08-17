#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""戦略bの改善の分解: 「予測」か「平均化によるノイズ除去」か（北海道）

対照戦略を追加して b の優位の源泉を切り分ける:
  PF : 完全予見（上界）
  a  : 前日(D-1)の実現価格ランク（従来の戦略a）
  a2 : 直近の「同じ曜日区分（平日/休日）」の日の実現価格ランク（日タイプ補正のみ）
  c  : 過去28日・同曜日区分の「実現価格」の同時刻平均ランク（価格の気候値＝平均化のみ）
  b  : 需要(28日同区分平均) − 太陽光(7日平均) の予測残余需要ランク（従来の戦略b）

c ≈ b なら「改善の正体は平均化（気候値）」、b ≫ c なら「量ベースの構造情報」に固有の価値。
期間: FY2023-25（現行構造）。仕様は従来と同一（4h・η0.85・60分・1日1サイクル）。
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
ETA = 0.85

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)

P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
D = hp.pivot(index="day", columns="hour", values="demand")
S = hp.pivot(index="day", columns="hour", values="solar")
days = P.index
all_days = D.index
wk = pd.Series(all_days.dayofweek >= 5, index=all_days)
wkP = pd.Series(P.index.dayofweek >= 5, index=P.index)


def margin(p, dis, chg):
    return (p[list(dis)].sum() * ETA - p[list(chg)].sum()) * 1000


def win(series):
    o = series.sort_values()
    return o.index[-4:], o.index[:4]


rows = []
for i, d in enumerate(days):
    p = P.loc[d]
    rec = {"day": d, "pf": max(0.0, margin(p, *win(p)))}
    # a: 前日
    if i >= 1:
        rec["a"] = margin(p, *win(P.loc[days[i - 1]]))
    # a2: 直近の同じ曜日区分の日
    prev_same = [dd for dd in days[max(0, i - 8):i] if wkP[dd] == wkP[d]]
    if prev_same:
        rec["a2"] = margin(p, *win(P.loc[prev_same[-1]]))
    # c: 過去28日・同区分の平均価格ランク
    hist_p = [dd for dd in days[max(0, i - 29):i] if wkP[dd] == wkP[d]]
    if len(hist_p) >= 5:
        rec["c"] = margin(p, *win(P.loc[hist_p].mean()))
    # b: 予測残余需要ランク（従来実装と同じ情報集合 D-2まで）
    jj = all_days.get_loc(d)
    if jj >= 30:
        hist = all_days[max(0, jj - 29):jj - 1]
        same = [h for h in hist if wk[h] == wk[d]]
        if len(same) >= 5:
            dem_f = D.loc[same].mean()
            sol_f = S.loc[all_days[jj - 8:jj - 1]].mean()
            rec["b"] = margin(p, *win(dem_f - sol_f))
    rows.append(rec)

bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
est = bt[bt["fy"].isin([2023, 2024, 2025])].dropna()
ann = est.groupby("fy")[["pf", "a", "a2", "c", "b"]].sum() / 1000
cap = ann.div(ann["pf"], axis=0) * 100

print("=== 年間価値（円/kW-年、FY2023-25・共通サンプル） ===")
print(ann.round(0).to_string())
print("\n=== capture率（PF=100%） ===")
print(cap.round(1).to_string())
print("\n凡例: a=前日価格 / a2=同曜日区分の直近日価格 / c=28日同区分の平均価格ランク / b=予測残余需要ランク")
