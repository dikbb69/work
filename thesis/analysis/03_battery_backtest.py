#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""案1: 九州エリアにおける4時間蓄電池の日次裁定価値バックテスト

蓄電池仕様: 出力1MW・容量4MWh・往復効率85%(放電側に一括適用)・1日1サイクル・
            日をまたぐSoC持ち越しなし・劣化無視(注記の上)・価格テイカー

3戦略(いずれも60分粒度で統一。価格はJEPX九州エリアプライス30分値の時間平均):
  PF   完全予見: 当日Dの実現価格で最安4時間に充電・最高4時間に放電(粗利が負なら休止)
  A    前日価格ナイーブ: 受渡日D-1の実現価格の時間帯ランクでDの充放電時間帯を決定
  B    前日予測ベース: D-2までに利用可能な実績のみから需要・太陽光を予測し、
       予測残余需要(需要-太陽光)の最低4時間に充電・最高4時間に放電
       (TSO翌日計画値の情報集合の代理再現。予測値の過去アーカイブは非公開のため)
         需要予測: 平日/休日別に直近28日(D-2まで)の同時刻平均
         太陽光予測: 直近7日(D-2まで)の同時刻平均(季節持続性)

出力: thesis/data/processed/kyushu_battery_backtest_daily.csv (日次粗利3系列)
      thesis/figures/kyushu/f7-backtest-annual.png, f7_annual_table.csv
"""
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = "Noto Sans CJK JP"

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "kyushu")

ETA = 0.85          # 往復効率(放電側に一括適用)
HOURS = 4           # 充放電時間
POWER_MW = 1.0

panel = pd.read_csv(os.path.join(PROC, "kyushu_hourly_panel.csv"), parse_dates=["ts"])
panel = panel.dropna(subset=["p_kyushu"]).copy()
panel["day"] = panel["ts"].dt.normalize()
panel["hour"] = panel["ts"].dt.hour

# 24時間そろっている日のみ対象
cnt = panel.groupby("day")["hour"].count()
full_days = cnt[cnt == 24].index
panel = panel[panel["day"].isin(full_days)]

# 日×時間の行列に変形
P = panel.pivot(index="day", columns="hour", values="p_kyushu")     # 円/kWh
D = panel.pivot(index="day", columns="hour", values="demand")       # MWh(旧)/MW平均(新)→ランク用途なので単位差は無害
S = panel.pivot(index="day", columns="hour", values="solar")
days = P.index

def margin_from_windows(prices_today, dis_hours, chg_hours):
    """円/kWh × 1MW×1h×1000kWh = 円。粗利/MW/日を返す"""
    rev = prices_today[list(dis_hours)].sum() * 1000 * ETA
    cost = prices_today[list(chg_hours)].sum() * 1000
    return rev - cost

def windows_from_ranks(series):
    order = series.sort_values()
    return order.index[-HOURS:], order.index[:HOURS]  # (放電=高い4h, 充電=安い4h)

rows = []
weekend = pd.Series(days).dt.dayofweek >= 5
weekend.index = days

for i, d in enumerate(days):
    p_today = P.loc[d]
    # --- PF ---
    dis, chg = windows_from_ranks(p_today)
    m_pf = max(0.0, margin_from_windows(p_today, dis, chg))
    # --- A: 前日価格 ---
    m_a = np.nan
    if i >= 1:
        p_prev = P.loc[days[i - 1]]
        dis_a, chg_a = windows_from_ranks(p_prev)
        m_a = margin_from_windows(p_today, dis_a, chg_a)
    # --- B: 予測残余需要 ---
    m_b = np.nan
    if i >= 30:
        hist = days[max(0, i - 29):i - 1]           # D-2 まで
        same_type = [h for h in hist if weekend[h] == weekend[d]]
        if len(same_type) >= 5:
            dem_f = D.loc[same_type].mean()
            sol_hist = days[i - 8:i - 1]            # 直近7日(D-2まで)
            sol_f = S.loc[sol_hist].mean()
            net_f = dem_f - sol_f
            order = net_f.sort_values()
            chg_b, dis_b = order.index[:HOURS], order.index[-HOURS:]
            m_b = margin_from_windows(p_today, dis_b, chg_b)
    rows.append({"day": d, "pf": m_pf, "naive": m_a, "forecast": m_b})

bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
bt.to_csv(os.path.join(PROC, "kyushu_battery_backtest_daily.csv"), index=False)

# ---- 年度集計(円/kW-年 = 円/MW-年 / 1000) ----
FY_FULL = list(range(2016, 2026))
ann = bt[bt["fy"].isin(FY_FULL)].groupby("fy")[["pf", "naive", "forecast"]].sum() / 1000
ann["capture_naive"] = ann["naive"] / ann["pf"] * 100
ann["capture_forecast"] = ann["forecast"] / ann["pf"] * 100
ann.round(1).to_csv(os.path.join(FIG, "f7_annual_table.csv"))
print(ann.round(1).to_string())

# ---- 図 f7 ----
SURFACE, INK, SUB = "#fcfcfb", "#0b0b0b", "#52514e"
COL = {"pf": "#184f95", "naive": "#6da7ec", "forecast": "#ec835a"}
LAB = {"pf": "完全予見（上限値）", "naive": "a. 前日価格ナイーブ", "forecast": "b. 前日予測ベース（TSO計画値の代理）"}
fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=300)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
for k in ["pf", "naive", "forecast"]:
    v = ann[k] / 10000  # 万円/kW-年
    ax.plot(ann.index, v, lw=2.2, marker="o", ms=4.5, color=COL[k], label=LAB[k])
ax.axvspan(2021.6, 2022.4, color="#f1e4dc", alpha=0.6)
ax.annotate("燃料危機", (2022, ax.get_ylim()[1] * 0.95), ha="center", fontsize=8.5, color=SUB)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#c3c2b7")
ax.tick_params(colors=SUB, labelsize=8.5)
ax.grid(axis="y", color="#e8e7e0", lw=0.6)
ax.set_axisbelow(True)
ax.set_xticks(ann.index)
ax.set_xticklabels([f"FY{y}" for y in ann.index], fontsize=8)
ax.set_ylabel("年間裁定粗利（万円/kW-年）", fontsize=9.5, color=INK)
ax.set_title("4時間蓄電池のスポット裁定価値（九州・実績バックテスト）", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
fig.text(0.12, 0.012,
         "出力1MW・4MWh・往復効率85%・日次1サイクル・劣化無視・スポット裁定のみ（需給調整・容量市場収益を含まない下限推定）。\n"
         "a=前日受渡日の実現価格の時間帯ランクで翌日の充放電帯を決定。b=D-2までの実績による需要(平日/休日別28日平均)・太陽光(7日平均)予測の残余需要ランク。",
         fontsize=6.6, color=SUB)
fig.tight_layout(rect=(0, 0.055, 1, 1))
fig.savefig(os.path.join(FIG, "f7-backtest-annual.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f7")
