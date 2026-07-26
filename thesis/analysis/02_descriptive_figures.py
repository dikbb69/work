#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""九州パイロット: 記述統計図表の生成(ゼミ発表用)

入力: thesis/data/processed/*.csv (01_build_panel.py の出力)
出力: thesis/figures/kyushu/f1..f6 PNG + fy_summary.csv
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
os.makedirs(FIG, exist_ok=True)

SURFACE, INK, SUB = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, CORAL = "#2a78d6", "#ec835a"
RAMP = ["#cde2fb", "#b7d3f6", "#86b6ef", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#184f95"]

j = pd.read_csv(os.path.join(PROC, "jepx_kyushu_30min.csv"), parse_dates=["ts"])
daily = pd.read_csv(os.path.join(PROC, "kyushu_daily_metrics.csv"), parse_dates=["day"])
FY_FULL = list(range(2016, 2026))  # FY2026は部分年度のため年度間比較から除外


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=SUB, labelsize=8.5)
    ax.grid(axis="y", color="#e8e7e0", lw=0.6)
    ax.set_axisbelow(True)


def newfig(w=7.4, h=4.4):
    fig, ax = plt.subplots(figsize=(w, h), dpi=300)
    fig.patch.set_facecolor(SURFACE)
    style(ax)
    return fig, ax


def save(fig, name, note=None):
    if note:
        fig.text(0.12, 0.012, note, fontsize=6.8, color=SUB)
    fig.tight_layout(rect=(0, 0.045 if note else 0, 1, 1))
    p = os.path.join(FIG, name)
    fig.savefig(p, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print("saved", p)


# ---- F1: 年度別・時間帯別平均価格カーブ(ダックカーブの深化) ----
sel = [2016, 2019, 2023, 2025]
colors = {2016: RAMP[1], 2019: RAMP[3], 2023: RAMP[5], 2025: RAMP[7]}
j["hour"] = j["ts"].dt.hour + j["ts"].dt.minute / 60
j["fy"] = j["ts"].dt.year - (j["ts"].dt.month < 4).astype(int)
fig, ax = newfig()
label_dy = {2016: 0.25, 2019: -0.35, 2023: -0.55, 2025: 0.55}  # 右端ラベルの衝突回避
for fy in sel:
    g = j[j["fy"] == fy].groupby("hour")["p_kyushu"].mean()
    ax.plot(g.index, g.values, lw=2, color=colors[fy])
    ax.annotate(f"FY{fy}", (g.index[-1], g.values[-1]),
                xytext=(24.2, g.values[-1] + label_dy.get(fy, 0)),
                fontsize=9, color=colors[fy], fontweight="bold", va="center")
ax.set_xlim(0, 27)
ax.set_xticks(range(0, 25, 3))
ax.set_xlabel("時刻", fontsize=9.5, color=INK)
ax.set_ylabel("九州エリアプライス 平均（円/kWh）", fontsize=9.5, color=INK)
ax.set_title("時間帯別平均価格カーブの変化：昼間の陥没（ダックカーブ）が年々深化", fontsize=11.5, color=INK, pad=10)
save(fig, "f1-duck-curve.png",
     "JEPXスポット九州エリアプライス30分値の年度内平均。価格水準は燃料価格の影響を含む（FY2022の燃料危機年は表示から除外）。")

# ---- F2: 0.01円張り付きコマ数の年度推移 ----
fy = daily[daily["fy"].isin(FY_FULL)].groupby("fy").agg(
    floor=("floor_koma", "sum"), curt=("curtail_day", "sum"),
    tb4h_med=("spread_tb4h", "median"), tb4h_q1=("spread_tb4h", lambda x: x.quantile(.25)),
    tb4h_q3=("spread_tb4h", lambda x: x.quantile(.75)), p_mean=("p_mean", "mean"),
    solar_peak=("solar_peak_mw", "max"),
).reset_index()
fig, ax = newfig()
ax.bar(fy["fy"], fy["floor"], color=BLUE, width=0.62)
for _, r in fy.iterrows():
    ax.annotate(f"{int(r['floor']):,}", (r["fy"], r["floor"]), xytext=(0, 3),
                textcoords="offset points", ha="center", fontsize=8, color=SUB)
ax.annotate("FY2023をピークに減少\n（蓄電池増・関門増強等の吸収要因は要検証）",
            (2024.4, 1900), fontsize=8.5, color=CORAL, ha="center")
ax.set_xticks(fy["fy"])
ax.set_xticklabels([f"FY{y}" for y in fy["fy"]], fontsize=8)
ax.set_ylabel("0.01円/kWh 約定コマ数（年度計）", fontsize=9.5, color=INK)
ax.set_title("下限価格0.01円への張り付き：太陽光普及とともに急増し、FY2023がピーク", fontsize=11.5, color=INK, pad=10)
save(fig, "f2-floor-koma.png",
     "九州エリアプライス（30分コマ）が0.01円/kWhで約定したコマ数。九州の需給制約による出力制御はFY2018（2018年10月）開始。")

# ---- F3: Top-Bottom 4h スプレッドの年度推移(中央値+四分位帯) ----
fig, ax = newfig()
ax.fill_between(fy["fy"], fy["tb4h_q1"], fy["tb4h_q3"], color=RAMP[2], alpha=0.55, label="四分位範囲（日次分布の25–75%）")
ax.plot(fy["fy"], fy["tb4h_med"], color=BLUE, lw=2.2, marker="o", ms=5, label="中央値")
ax.axvspan(2021.6, 2022.4, color="#f1e4dc", alpha=0.6)
ax.annotate("燃料危機\n(FY2022)", (2022, float(fy["tb4h_q3"].max()) * 0.92), ha="center", fontsize=8.5, color=CORAL)
ax.annotate("構造水準 ≈5円 → ≈10円へ", (2018.3, 12.5), fontsize=9.5, color=INK)
ax.set_xticks(fy["fy"])
ax.set_xticklabels([f"FY{y}" for y in fy["fy"]], fontsize=8)
ax.set_ylabel("日次 Top4h−Bottom4h スプレッド（円/kWh）", fontsize=9.5, color=INK)
ax.set_title("4時間蓄電池の理論粗利（日次スプレッド）：燃料危機後も高止まり＝構造的拡大", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8, loc="upper left", frameon=False)
save(fig, "f3-tb4h-spread.png",
     "各日の九州エリアプライス48コマのうち上位8コマ平均−下位8コマ平均。効率・劣化調整前。FY2022は燃料価格高騰の影響が大きい。")

# ---- F4: 太陽光普及(実績ピーク) × 昼間価格・張り付き率 ----
noon = j[(j["hour"] >= 10) & (j["hour"] < 14)].copy()
noon_fy = noon[noon["fy"].isin(FY_FULL)].groupby("fy").agg(
    p_noon=("p_kyushu", "mean"),
    floor_share=("p_kyushu", lambda x: (x <= 0.011).mean() * 100),
).reset_index().merge(fy[["fy", "solar_peak"]], on="fy")
fig, ax = newfig(7.4, 4.6)
ax.scatter(noon_fy["solar_peak"] / 1000, noon_fy["floor_share"], s=90, color=BLUE,
           edgecolors=SURFACE, linewidths=1.5, zorder=3)
for _, r in noon_fy.iterrows():
    ax.annotate(f"FY{int(r['fy'])}", (r["solar_peak"] / 1000, r["floor_share"]),
                xytext=(5, 4), textcoords="offset points", fontsize=8.2, color=INK)
ax.set_xlabel("太陽光の年度最大実績出力（GW）※導入量の代理指標", fontsize=9.5, color=INK)
ax.set_ylabel("昼間（10–14時）の0.01円張り付き率（%）", fontsize=9.5, color=INK)
ax.set_title("太陽光普及と昼間価格の崩落：普及が進むほど昼間は「タダ」の時間になる", fontsize=11.5, color=INK, pad=10)
save(fig, "f4-solar-vs-floor.png",
     "横軸は需給実績の太陽光発電実績の年度最大値（接続量の公式系列は別途整備予定）。FY2023→25の張り付き率低下の要因分解は今後の分析対象。")

# ---- F5: 出力制御日 vs 非制御日の平均価格カーブ(FY2023-2025) ----
dsub = daily[daily["fy"].isin([2023, 2024, 2025])][["day", "curtail_day"]]
jj = j.merge(dsub, left_on=j["ts"].dt.normalize(), right_on="day", how="inner")
fig, ax = newfig()
for flag, color, lab in [(True, CORAL, "出力制御 実施日"), (False, BLUE, "非実施日")]:
    g = jj[jj["curtail_day"] == flag].groupby("hour")["p_kyushu"].mean()
    n = jj[jj["curtail_day"] == flag]["day"].nunique()
    ax.plot(g.index, g.values, lw=2.2, color=color, label=f"{lab}（{n}日）")
ax.set_xlim(0, 24)
ax.set_xticks(range(0, 25, 3))
ax.set_xlabel("時刻", fontsize=9.5, color=INK)
ax.set_ylabel("九州エリアプライス 平均（円/kWh）", fontsize=9.5, color=INK)
ax.set_title("出力制御日の価格形状：昼間はほぼゼロ、夕方ランプは残る（FY2023–25）", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8.5, frameon=False)
save(fig, "f5-curtail-days.png",
     "出力制御実施日＝需給実績の太陽光・風力抑制量が正の日。制御日ほど日中スプレッドが深く、蓄電池の裁定機会が大きい。")

# ---- F6: 価格分位点の年度推移(分布の二極化) ----
qf = j[j["fy"].isin(FY_FULL)].groupby("fy")["p_kyushu"].quantile([.05, .25, .5, .75, .95]).unstack()
fig, ax = newfig()
ax.fill_between(qf.index, qf[.05], qf[.95], color=RAMP[1], alpha=0.7, label="5–95%範囲")
ax.fill_between(qf.index, qf[.25], qf[.75], color=RAMP[3], alpha=0.7, label="25–75%範囲")
ax.plot(qf.index, qf[.5], color=RAMP[6], lw=2.2, label="中央値")
ax.set_xticks(qf.index)
ax.set_xticklabels([f"FY{y}" for y in qf.index], fontsize=8)
ax.set_ylabel("九州エリアプライス（円/kWh）", fontsize=9.5, color=INK)
ax.set_title("価格分布の二極化：下端は0.01円に固定され、上側だけが動く分布へ", fontsize=11.5, color=INK, pad=10)
ax.legend(fontsize=8, frameon=False, loc="upper left")
save(fig, "f6-quantiles.png",
     "30分コマ別価格の年度内分位点。FY2019以降、5%分位は0.01円に到達。FY2020の95%分位上昇は2021年1月の需給逼迫による。")

# ---- 年度サマリー表 ----
summary = fy.rename(columns={
    "fy": "年度", "floor": "0.01円コマ数", "curt": "出力制御日数",
    "tb4h_med": "TB4hスプレッド中央値", "p_mean": "平均価格", "solar_peak": "太陽光最大実績MW"})
summary.to_csv(os.path.join(FIG, "fy_summary.csv"), index=False)
print(summary.to_string(index=False))
