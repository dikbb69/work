#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""価格水準で規格化した指標

問題意識: TB4hスプレッドや裁定価値は市場価格の「水準」(燃料価格)に比例的に
膨らむため、FY2020-22の山には水準効果が混入している。水準の影響を除いた
「形状」由来の裁定機会を見るため、以下の2指標を計算する。

  1) 日次相対スプレッド RS_d = TB4hスプレッド_d ÷ 当日48コマ平均価格
     (無次元。ベース価格=当日フラット調達価格とみなした規格化)
  2) 等価時間 EH_fy = 年間裁定粗利(円/kW-年) ÷ 年度平均価格(円/kWh) → kWh/kW-年
     (「年間粗利が平均価格何kWh分に相当するか」。理論上限 = 365日×4MWh×補正)

出力: f9-relative-spread.png, f10-normalized-value.png, f9_f10_tables.csv
"""
import os

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
SURFACE, INK, SUB = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, CORAL, LBLUE, RAMP2 = "#2a78d6", "#ec835a", "#6da7ec", "#86b6ef"
FY_FULL = list(range(2016, 2026))

daily = pd.read_csv(os.path.join(PROC, "kyushu_daily_metrics.csv"), parse_dates=["day"])
bt = pd.read_csv(os.path.join(PROC, "kyushu_battery_backtest_daily.csv"), parse_dates=["day"])

# ---- 1) 日次相対スプレッド ----
daily["rel_spread"] = daily["spread_tb4h"] / daily["p_mean"]
fy = daily[daily["fy"].isin(FY_FULL)].groupby("fy").agg(
    rs_med=("rel_spread", "median"),
    rs_q1=("rel_spread", lambda x: x.quantile(.25)),
    rs_q3=("rel_spread", lambda x: x.quantile(.75)),
    abs_med=("spread_tb4h", "median"),
    p_mean=("p_mean", "mean"),
).reset_index()

fig, ax = plt.subplots(figsize=(7.6, 4.5), dpi=300)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
ax.fill_between(fy["fy"], fy["rs_q1"], fy["rs_q3"], color=RAMP2, alpha=0.5, label="四分位範囲")
ax.plot(fy["fy"], fy["rs_med"], color=BLUE, lw=2.2, marker="o", ms=5, label="中央値")
ax.axvspan(2021.6, 2022.4, color="#f1e4dc", alpha=0.6)
ax.annotate("燃料危機\n(FY2022)", (2022, float(fy["rs_q3"].max()) * 0.97), ha="center", fontsize=8.5, color=CORAL)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#c3c2b7")
ax.tick_params(colors=SUB, labelsize=8.5)
ax.grid(axis="y", color="#e8e7e0", lw=0.6)
ax.set_axisbelow(True)
ax.set_xticks(fy["fy"])
ax.set_xticklabels([f"FY{y}" for y in fy["fy"]], fontsize=8)
ax.set_ylabel("相対スプレッド（TB4h ÷ 当日平均価格、無次元）", fontsize=9.5, color=INK)
ax.set_title("価格水準で規格化したスプレッド：水準効果を除いても構造的拡大は残る", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
fig.text(0.12, 0.012,
         "相対スプレッド＝各日のTop4h−Bottom4hスプレッド÷当日48コマ平均価格。当日平均をベース(フラット)価格とみなした規格化。",
         fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(os.path.join(FIG, "f9-relative-spread.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f9")
print(fy.round(3).to_string(index=False))

# ---- 2) 等価時間(年間粗利 ÷ 年度平均価格) ----
btf = bt[bt["fy"].isin(FY_FULL)]
ann = btf.groupby("fy")[["pf", "naive", "forecast"]].sum() / 1000  # 円/kW-年
pmean = daily[daily["fy"].isin(FY_FULL)].groupby("fy")["p_mean"].mean()
eh = ann.div(pmean, axis=0)  # kWh/kW-年 相当
eh.columns = ["pf_eh", "naive_eh", "forecast_eh"]

COL = {"pf_eh": "#184f95", "naive_eh": "#6da7ec", "forecast_eh": "#ec835a"}
LAB = {"pf_eh": "完全予見", "naive_eh": "a. 前日価格ナイーブ", "forecast_eh": "b. 前日予測ベース"}
fig, ax = plt.subplots(figsize=(7.6, 4.5), dpi=300)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
for k in eh.columns:
    ax.plot(eh.index, eh[k], lw=2.2, marker="o", ms=4.5, color=COL[k], label=LAB[k])
ax.axvspan(2021.6, 2022.4, color="#f1e4dc", alpha=0.6)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#c3c2b7")
ax.tick_params(colors=SUB, labelsize=8.5)
ax.grid(axis="y", color="#e8e7e0", lw=0.6)
ax.set_axisbelow(True)
ax.set_xticks(eh.index)
ax.set_xticklabels([f"FY{y}" for y in eh.index], fontsize=8)
ax.set_ylabel("規格化年間価値（年間粗利 ÷ 年度平均価格、kWh/kW-年）", fontsize=9.5, color=INK)
ax.set_title("価格水準で規格化した蓄電池価値：構造要因（形状）による価値の推移", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
fig.text(0.12, 0.012,
         "年間裁定粗利(円/kW-年)を年度平均価格(円/kWh)で除した値＝「平均価格の電気の何kWh分を稼いだか」。水準(燃料)効果を除いた尺度。\n"
         "参考: 年間放電量は最大で約1,241kWh/kW-年(365日×4h×効率0.85)。充放電の価格差が平均価格を上回る年はこの値を超えうる。",
         fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(os.path.join(FIG, "f10-normalized-value.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f10")

out = fy.merge(eh.reset_index(), on="fy")
out.round(3).to_csv(os.path.join(FIG, "f9_f10_tables.csv"), index=False)
print(eh.round(0).to_string())
