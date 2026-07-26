#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FY2023→25 の「張り付き減・スプレッド縮小」の要因分解

検証する仮説:
  H1 床の持ち上がり: 0.01円コマが減った分は「0.01超〜数円」の低価格コマに
     置き換わった(=昼の買い側(蓄電池・揚水充電等)が下値を支えた)のか
  H2 山側の圧縮: 夕方Top4hが下がったのか
  H3 吸収リソースの増加: 昼間の揚水充電・蓄電池充電・域外送電・需要が増えたか
  H4 出力制御は本当に増えているか(日数でなく時間数・量で)
  H5 市場分断(九州安値側)の頻度変化

出力: f11-absorption.png, f12-top-bottom.png, f13-price-bands.png と統計表(標準出力)
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
SURFACE, INK, SUB = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, CORAL, LBLUE, DBLUE = "#2a78d6", "#ec835a", "#6da7ec", "#184f95"
RAMP = ["#cde2fb", "#b7d3f6", "#86b6ef", "#3987e5", "#184f95"]
FY_FULL = list(range(2016, 2026))

j = pd.read_csv(os.path.join(PROC, "jepx_kyushu_30min.csv"), parse_dates=["ts"])
panel = pd.read_csv(os.path.join(PROC, "kyushu_hourly_panel.csv"), parse_dates=["ts"])
j = j[j["fy"].isin(FY_FULL)]
panel = panel[panel["fy"].isin(FY_FULL)]
j["hour"] = j["ts"].dt.hour
panel["hour"] = panel["ts"].dt.hour

def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=SUB, labelsize=8.5)
    ax.grid(axis="y", color="#e8e7e0", lw=0.6)
    ax.set_axisbelow(True)

# ============ H4: 出力制御の実態(日数・時間数・量) ============
panel["curt_total"] = panel["solar_curt"].fillna(0) + panel["wind_curt"].fillna(0)
curt = panel.groupby("fy").agg(
    curt_hours=("curt_total", lambda x: (x > 0).sum()),
    curt_gwh=("curt_total", lambda x: x.sum() / 1000),
    solar_gwh=("solar", lambda x: x.sum() / 1000),
)
curt["curt_rate_%"] = curt["curt_gwh"] / (curt["curt_gwh"] + curt["solar_gwh"]) * 100
# H4b: 制御時間のうち市場価格が床(0.01円)で約定した割合
panel["floor_h"] = panel["p_kyushu"] <= 0.011
h4b = panel[panel["curt_total"] > 0].groupby("fy")["floor_h"].agg(["sum", "count"])
h4b["floor_share_%"] = h4b["sum"] / h4b["count"] * 100
curt = curt.join(h4b["floor_share_%"])
print("=== H4: 出力制御の時間数・量・制御時間中の床約定率 ===")
print(curt.round(1).to_string())

# ============ H1: 昼間(10-14時)の価格帯分布 ============
noon = j[(j["hour"] >= 10) & (j["hour"] < 14)]
bands = pd.DataFrame({
    "≤0.01円": noon.groupby("fy")["p_kyushu"].apply(lambda x: (x <= 0.011).mean()),
    "0.01–1円": noon.groupby("fy")["p_kyushu"].apply(lambda x: ((x > 0.011) & (x <= 1)).mean()),
    "1–3円": noon.groupby("fy")["p_kyushu"].apply(lambda x: ((x > 1) & (x <= 3)).mean()),
    "3–5円": noon.groupby("fy")["p_kyushu"].apply(lambda x: ((x > 3) & (x <= 5)).mean()),
    ">5円": noon.groupby("fy")["p_kyushu"].apply(lambda x: (x > 5).mean()),
}) * 100
print()
print("=== H1: 昼間(10-14時)コマの価格帯構成(%) ===")
print(bands.round(1).to_string())
print("昼間の平均価格:", noon.groupby("fy")["p_kyushu"].mean().round(2).to_dict())

# ============ H2: Top4h / Bottom4h の分解 ============
j["day"] = j["ts"].dt.normalize()
def tb(g):
    p = g.sort_values().to_numpy()
    return pd.Series({"bot4h": p[:8].mean(), "top4h": p[-8:].mean()})
tbd = j.groupby(["fy", "day"])["p_kyushu"].apply(lambda g: tb(g)).unstack()
tby = tbd.groupby("fy").median()
print()
print("=== H2: 日次Top4h/Bottom4hの年度中央値(円/kWh) ===")
print(tby.round(2).to_string())

# ============ H3: 昼間(10-14時)の吸収リソース ============
noonp = panel[(panel["hour"] >= 10) & (panel["hour"] < 14)].copy()
# 符号規約の確認: 揚水・蓄電池は負=充電(吸収), 連系線は負=域外送電(流出)
sign_check = noonp.groupby("fy")[["pumped", "battery", "interconn"]].mean()
print()
print("=== 符号確認(昼間平均, 負=充電/流出) ===")
print(sign_check.round(0).to_string())
noonp["storage_charge"] = -(noonp["pumped"].fillna(0).clip(upper=0) + noonp["battery"].fillna(0).clip(upper=0))
noonp["export"] = -noonp["interconn"].clip(upper=0)
abs_tab = noonp.groupby("fy").agg(
    demand=("demand", "mean"),
    solar=("solar", "mean"),
    solar_precurt=("solar", "mean"),
    storage_charge=("storage_charge", "mean"),
    export=("export", "mean"),
    curt=("curt_total", "mean"),
    nuclear=("nuclear", "mean"),
    thermal=("thermal", "mean"),
    wind=("wind", "mean"),
    battery_abs=("battery", lambda x: x.dropna().abs().mean() if x.notna().any() else np.nan),
)
abs_tab["solar_precurt"] = abs_tab["solar"] + abs_tab["curt"]
print()
print("=== H3: 昼間(10-14時)の需給・吸収(MW平均) ===")
print(abs_tab.round(0).to_string())

# ============ H5: 市場分断(九州が安値側)の頻度 ============
j["split_low"] = j["p_kyushu"] < (j["p_system"] - 0.01)
split = j.groupby("fy")["split_low"].mean() * 100
noon_split = noon.assign(sl=noon["p_kyushu"] < (noon["p_system"] - 0.01)).groupby("fy")["sl"].mean() * 100
print()
print("=== H5: 九州が安値側に分断されたコマ比率(%) 全時間帯/昼間 ===")
print(pd.DataFrame({"全時間帯": split, "昼間10-14時": noon_split}).round(1).to_string())

# ============ 図 f11: 昼間の吸収リソースと需要・太陽光 ============
fys = abs_tab.index
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.3), dpi=300)
fig.patch.set_facecolor(SURFACE)
for ax in (ax1, ax2):
    style(ax)
ax1.plot(fys, abs_tab["storage_charge"] / 1000, lw=2.2, marker="o", ms=4, color=DBLUE, label="揚水+蓄電池 充電")
ax1.plot(fys, abs_tab["export"] / 1000, lw=2.2, marker="o", ms=4, color=LBLUE, label="域外送電（関門）")
ax1.plot(fys, abs_tab["curt"] / 1000, lw=2.2, marker="o", ms=4, color=CORAL, label="出力制御")
ax1.set_ylabel("昼間(10-14時)平均 (GW)", fontsize=9.5, color=INK)
ax1.set_title("余剰の吸収先", fontsize=10.5, color=INK)
ax1.legend(fontsize=8, frameon=False)
ax2.plot(fys, abs_tab["demand"] / 1000, lw=2.2, marker="o", ms=4, color=DBLUE, label="エリア需要")
ax2.plot(fys, abs_tab["solar"] / 1000, lw=2.2, marker="o", ms=4, color=CORAL, label="太陽光実績（制御後）")
ax2.set_ylabel("昼間(10-14時)平均 (GW)", fontsize=9.5, color=INK)
ax2.set_title("需要と太陽光", fontsize=10.5, color=INK)
ax2.legend(fontsize=8, frameon=False)
for ax in (ax1, ax2):
    ax.set_xticks(list(fys))
    ax.set_xticklabels([f"'{str(y)[2:]}" for y in fys], fontsize=8)
fig.suptitle("昼間の需給バランスの変化（九州）", fontsize=12, color=INK)
fig.text(0.1, 0.012,
         "需給実績より。揚水+蓄電池充電=負値の絶対値（蓄電池列は2024年3月以降のみ分離、以前は「揚水等」に包含）。域外送電=連系線流出。",
         fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.05, 1, 0.94))
fig.savefig(os.path.join(FIG, "f11-absorption.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f11")

# ============ 図 f12: Top4h / Bottom4h ============
fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=300)
fig.patch.set_facecolor(SURFACE)
style(ax)
ax.plot(tby.index, tby["top4h"], lw=2.2, marker="o", ms=4.5, color=CORAL, label="Top4h（夕方ピーク側）")
ax.plot(tby.index, tby["bot4h"], lw=2.2, marker="o", ms=4.5, color=BLUE, label="Bottom4h（昼間の底側）")
ax.axvspan(2021.6, 2022.4, color="#f1e4dc", alpha=0.6)
ax.set_xticks(tby.index)
ax.set_xticklabels([f"FY{y}" for y in tby.index], fontsize=8)
ax.set_ylabel("日次Top4h／Bottom4h平均価格の年度中央値（円/kWh）", fontsize=9, color=INK)
ax.set_title("スプレッドの分解：縮小は「山が下がった」のか「底が上がった」のか", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8.5, frameon=False)
fig.text(0.12, 0.012, "各日の上位8コマ平均(Top4h)と下位8コマ平均(Bottom4h)の年度中央値。網掛けは燃料危機(FY2022)。", fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(os.path.join(FIG, "f12-top-bottom.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f12")

# ============ 図 f13: 昼間価格帯の構成(積み上げ) ============
fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=300)
fig.patch.set_facecolor(SURFACE)
style(ax)
cols = ["≤0.01円", "0.01–1円", "1–3円", "3–5円", ">5円"]
bottom = np.zeros(len(bands))
for c, col in zip(cols, RAMP):
    ax.bar(bands.index, bands[c], bottom=bottom, color=col, width=0.62, label=c, edgecolor=SURFACE, linewidth=0.8)
    bottom += bands[c].to_numpy()
ax.set_xticks(bands.index)
ax.set_xticklabels([f"FY{y}" for y in bands.index], fontsize=8)
ax.set_ylabel("昼間(10-14時)コマの価格帯構成（%）", fontsize=9.5, color=INK)
ax.set_title("床コマの減少分は低価格帯に残らず5円超帯へ移った（＝余剰時間そのものが減少）",
             fontsize=11, color=INK, pad=34)
ax.legend(fontsize=7.8, frameon=False, ncols=5, loc="upper center", bbox_to_anchor=(0.5, 1.12))
fig.text(0.12, 0.012, "九州エリアプライス。昼間=10:00-14:00の8コマ。", fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(os.path.join(FIG, "f13-price-bands.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f13")
