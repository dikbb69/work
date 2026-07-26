#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""案2: 日次スプレッド(完全予見粗利)の確率モデル + モンテカルロによる年間価値分布

モデル(パイロット仕様):
  m_d = s(month) + x_d,  x_d = rho * x_{d-1} + eps_d
  - m_d: 完全予見の日次粗利(円/MW-日, 03の出力)
  - s(month): 月別平均(季節成分)
  - eps: 残差の経験分布からのブートストラップ(分布仮定を置かない)
  - シミュレーション時は m<0 を0に切り上げ(サイクル休止オプション)
推定窓: 主 = FY2023-2025(燃料正常化後の現行構造) / 感応度 = FY2021-2025(危機込み)
出力: f8-montecarlo.png, f8_mc_table.csv
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

rng = np.random.default_rng(20260726)
N_PATHS = 5000

bt = pd.read_csv(os.path.join(PROC, "kyushu_battery_backtest_daily.csv"), parse_dates=["day"])
bt["month"] = bt["day"].dt.month


def fit_and_simulate(df):
    m = df.set_index("day")["pf"]
    month = df.set_index("day")["month"]
    s = m.groupby(month).mean()                     # 月別季節成分
    x = m - month.map(s)                            # 残差
    x0, x1 = x.iloc[:-1].to_numpy(), x.iloc[1:].to_numpy()
    rho = float(np.dot(x0, x1) / np.dot(x0, x0))    # AR(1) OLS
    eps = x1 - rho * x0
    # 365日カレンダー(月構成は通年)
    cal = pd.date_range("2027-04-01", periods=365, freq="D").month
    s_cal = np.array([s[mo] for mo in cal])
    sims = np.empty(N_PATHS)
    for i in range(N_PATHS):
        e = rng.choice(eps, size=365, replace=True)
        xs = np.empty(365)
        prev = 0.0
        for t in range(365):
            prev = rho * prev + e[t]
            xs[t] = prev
        daily = np.maximum(0.0, s_cal + xs)
        sims[i] = daily.sum() / 1000                # 円/kW-年
    return rho, eps.std(), sims


results = {}
for label, fys in [("FY2023-25", [2023, 2024, 2025]), ("FY2021-25", [2021, 2022, 2023, 2024, 2025])]:
    df = bt[bt["fy"].isin(fys)].dropna(subset=["pf"])
    rho, sd, sims = fit_and_simulate(df)
    results[label] = dict(rho=rho, sd=sd, sims=sims)
    q = np.percentile(sims, [5, 25, 50, 75, 95])
    print(f"{label}: rho={rho:.3f}, eps_sd={sd:,.0f}円 | 年間価値(円/kW-年) "
          f"mean={sims.mean():,.0f} p5={q[0]:,.0f} p50={q[2]:,.0f} p95={q[4]:,.0f}")

# 実現値(検証用)
real = bt[bt["fy"].isin([2023, 2024, 2025])].groupby("fy")["pf"].sum() / 1000

tab = pd.DataFrame({
    lab: {
        "AR(1) rho": r["rho"],
        "平均 (円/kW-年)": r["sims"].mean(),
        "5%点": np.percentile(r["sims"], 5),
        "中央値": np.percentile(r["sims"], 50),
        "95%点": np.percentile(r["sims"], 95),
    } for lab, r in results.items()
}).T
tab.round(1).to_csv(os.path.join(FIG, "f8_mc_table.csv"))
print(tab.round(0).to_string())

# ---- 図 f8 ----
SURFACE, INK, SUB = "#fcfcfb", "#0b0b0b", "#52514e"
BLUE, CORAL, LBLUE = "#2a78d6", "#ec835a", "#b7d3f6"
fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=300)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
sims_main = results["FY2023-25"]["sims"] / 10000
ax.hist(sims_main, bins=60, color=LBLUE, edgecolor=SURFACE, linewidth=0.4, density=True)
for fy, v in real.items():
    ax.axvline(v / 10000, color=BLUE, lw=1.6, ls=(0, (4, 2)))
    ax.annotate(f"実績FY{fy}", (v / 10000, ax.get_ylim()[1] * (0.92 - 0.1 * (fy - 2023))),
                fontsize=8, color=BLUE, ha="left", xytext=(3, 0), textcoords="offset points")
mean = sims_main.mean()
ax.axvline(mean, color=CORAL, lw=2)
ax.annotate(f"シミュレーション平均 {mean:.2f}万円/kW-年", (mean, ax.get_ylim()[1] * 0.99),
            fontsize=8.8, color=CORAL, ha="left", xytext=(5, -2), textcoords="offset points")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
for s in ["left", "bottom"]:
    ax.spines[s].set_color("#c3c2b7")
ax.tick_params(colors=SUB, labelsize=8.5)
ax.grid(axis="y", color="#e8e7e0", lw=0.6)
ax.set_axisbelow(True)
ax.set_xlabel("年間裁定粗利（万円/kW-年、完全予見ベース）", fontsize=9.5, color=INK)
ax.set_ylabel("確率密度", fontsize=9.5, color=INK)
ax.set_title("モンテカルロによる年間価値分布（現行構造 FY2023–25でモデル推定、5,000パス）", fontsize=11.2, color=INK, pad=10)
fig.text(0.12, 0.012,
         "日次スプレッドモデル: 月別季節成分 + AR(1) + 残差ブートストラップ。負の日はサイクル休止(0)に切上げ。\n"
         "破線は実現値(FY2023-25)。分布仮定を置かない経験分布ベース。燃料危機を含むFY2021-25推定の感応度は表参照。",
         fontsize=6.8, color=SUB)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(os.path.join(FIG, "f8-montecarlo.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f8")
