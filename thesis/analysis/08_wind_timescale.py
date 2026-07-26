#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""風力変動の時間スケール構造の実測（九州フリート集約出力、FY2022-25）

目的: 「単一サイトの波形は時間レベルでギザギザ」という実務感覚と
「フリート集約後はスポット価格に効く変動の中心が数日帯域」という主張の
両立を、手元データ（需給実績の風力=九州全域の集約出力）で示す。

手法: 移動平均カスケードによる帯域分解
  <6h: x − MA6h／6-24h: MA6h − MA24h／1-7日: MA24h − MA168h／>7日: MA168h − 平均
出力: f15-wind-timescale.png
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
BLUE, CORAL = "#2a78d6", "#ec835a"

p = pd.read_csv(os.path.join(PROC, "kyushu_hourly_panel.csv"), parse_dates=["ts"])
p = p[(p["ts"] >= "2022-04-01") & (p["ts"] < "2026-04-01")].set_index("ts")


def band_shares(x):
    x = x.interpolate()
    ma6 = x.rolling(6, center=True, min_periods=3).mean()
    ma24 = x.rolling(24, center=True, min_periods=12).mean()
    ma168 = x.rolling(168, center=True, min_periods=84).mean()
    comps = {"<6時間": x - ma6, "6–24時間": ma6 - ma24,
             "1–7日": ma24 - ma168, ">7日": ma168 - x.mean()}
    tot = x.var()
    return {k: float(v.var() / tot * 100) for k, v in comps.items()}


w_sh, s_sh = band_shares(p["wind"]), band_shares(p["solar"])
print("wind:", {k: round(v, 1) for k, v in w_sh.items()})
print("solar:", {k: round(v, 1) for k, v in s_sh.items()})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.8, 4.2), dpi=300,
                               gridspec_kw={"width_ratios": [1.5, 1]})
fig.patch.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    ax.set_facecolor(SURFACE)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=SUB, labelsize=8.5)
    ax.grid(axis="y", color="#e8e7e0", lw=0.6)
    ax.set_axisbelow(True)

# (a) 30日間のサンプル波形（冬季、総観規模エピソードが見える月）
smp = p.loc["2025-01-01":"2025-01-31", "wind"]
ax1.plot(smp.index, smp.values, lw=1.1, color=BLUE)
ma24 = smp.rolling(24, center=True, min_periods=12).mean()
ax1.plot(ma24.index, ma24.values, lw=2.4, color=CORAL, label="24時間移動平均（総観規模の起伏）")
ax1.set_ylabel("九州エリア 風力出力（MW）", fontsize=9, color=INK)
ax1.set_title("(a) 集約出力の実波形（2025年1月）: 時間スケールの振動の下に数日の起伏", fontsize=9.8, color=INK)
ax1.legend(fontsize=8, frameon=False)
ax1.tick_params(axis="x", labelsize=7.5)

# (b) 分散シェア
bands = list(w_sh.keys())
xx = range(len(bands))
ax2.bar([i - 0.19 for i in xx], [w_sh[b] for b in bands], width=0.36, color=BLUE, label="風力")
ax2.bar([i + 0.19 for i in xx], [s_sh[b] for b in bands], width=0.36, color=CORAL, label="太陽光")
for i, b in enumerate(bands):
    ax2.annotate(f"{w_sh[b]:.0f}", (i - 0.19, w_sh[b]), xytext=(0, 3), textcoords="offset points",
                 ha="center", fontsize=8.5, color=SUB)
    ax2.annotate(f"{s_sh[b]:.0f}", (i + 0.19, s_sh[b]), xytext=(0, 3), textcoords="offset points",
                 ha="center", fontsize=8.5, color=SUB)
ax2.set_xticks(list(xx))
ax2.set_xticklabels(bands, fontsize=8.5)
ax2.set_ylabel("分散シェア（%）", fontsize=9, color=INK)
ax2.set_title("(b) 変動エネルギーの時間スケール配分", fontsize=9.8, color=INK)
ax2.legend(fontsize=8.5, frameon=False)

fig.suptitle("フリート集約後の風力変動は「数日帯域」が支配的（九州・需給実績 FY2022–25）", fontsize=11.5, color=INK)
fig.text(0.1, 0.012,
         "移動平均カスケードによる帯域分解（<6h＝x−MA6h 等）。単一サイトでは<6h成分が大きいが、集約出力では2%まで縮む（空間平滑化）。\n"
         "太陽光は6–24時間帯（日内サイクル）が66%と対照的。北海道の風力実績データ取得後に同じ分解を適用予定。",
         fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.055, 1, 0.93))
fig.savefig(os.path.join(FIG, "f15-wind-timescale.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f15")
