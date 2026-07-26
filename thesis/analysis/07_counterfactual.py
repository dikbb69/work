#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反実仮想分析: 「半導体需要増・原子力稼働変動がなかりせば」のFY2024-25価格と裁定価値

設計(パイロット仕様):
  1) 異例イベントの規模の推定(いずれもフラットな水準シフトとして扱う)
     - 需要増 δD: 夜間(2-5時)需要のFY2023からの増分を「24時間フラットな新規産業負荷
       (半導体工場・DC等)」の代理とする(気温感応の小さい夜間帯で識別)
     - 原子力 δN: 年度平均出力のFY2023からの差(定検・稼働スケジュール変動)
  2) 経験的供給曲線 g: FY2024-25の実績から、市場が処理する正味需要
       net = 需要 − 太陽光 − 風力 − 原子力
     と九州エリアプライスの単調関係を季節(四半期)別に推定
     (分位ビン中央値 + 単調化 + 線形補間。観測レンジ外の下側は床0.01円)
  3) 反実仮想: net_cf = net − δD − δN (需要増なし・原子力FY2023水準) を g に通して
     p_cf を生成。床コマ・TB4h・完全予見裁定価値を実績と比較
  4) 検証: g を実績netに適用した in-sample 再現度(床コマ・TB4h)を併記

限界(明示): 部分均衡(揚水・輸出・入札行動の反応を固定) → 反実仮想は「上限」方向。
出力: f14-counterfactual.png と統計表(標準出力)
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
BLUE, CORAL, LBLUE = "#2a78d6", "#ec835a", "#6da7ec"
ETA, HOURS = 0.85, 4

p = pd.read_csv(os.path.join(PROC, "kyushu_hourly_panel.csv"), parse_dates=["ts"])
p["hour"] = p["ts"].dt.hour
p["day"] = p["ts"].dt.normalize()
p["month"] = p["ts"].dt.month
p["season"] = ((p["month"] % 12) // 3)  # 0:冬(12-2) 1:春(3-5) 2:夏(6-8) 3:秋(9-11)

# ---------- 1) 異例イベントの規模 ----------
night = p[(p["hour"] >= 2) & (p["hour"] < 5)]
dn = night.groupby("fy")["demand"].mean()
nuc = p.groupby("fy")["nuclear"].mean()
deltas = {}
for fy in [2024, 2025]:
    deltas[fy] = {"dD": dn[fy] - dn[2023], "dN": nuc[2023] - nuc[fy]}
print("=== 異例イベントの規模(MW, FY2023比) ===")
print("夜間需要の増分 δD:", {k: round(v["dD"]) for k, v in deltas.items()})
print("原子力の減少分 δN:", {k: round(v["dN"]) for k, v in deltas.items()})
print("(参考) 年度平均需要:", p.groupby("fy")["demand"].mean().round(0).loc[2019:].to_dict())
print("(参考) 年度平均原子力:", nuc.round(0).loc[2019:].to_dict())

# ---------- 2) 経験的供給曲線 g(net) 季節別 ----------
est = p[p["fy"].isin([2024, 2025])].dropna(subset=["p_kyushu"]).copy()
est["net"] = est["demand"] - est["solar"] - est["wind"] - est["nuclear"]

def fit_g(df, nbins=80):
    q = np.quantile(df["net"], np.linspace(0, 1, nbins + 1))
    q = np.unique(q)
    idx = np.clip(np.searchsorted(q, df["net"], side="right") - 1, 0, len(q) - 2)
    med = df.groupby(idx)["p_kyushu"].median()
    x = (q[:-1] + q[1:]) / 2
    x = x[med.index]
    y = np.maximum.accumulate(med.to_numpy())  # 単調非減少化
    return x, y

G = {s: fit_g(est[est["season"] == s]) for s in range(4)}

def apply_g(net, season):
    x, y = G[season]
    out = np.interp(net, x, y, left=0.01, right=y[-1])
    return np.maximum(out, 0.01)

# ---------- 3) 実績再現(検証)と反実仮想 ----------
tgt = est.copy()
tgt["p_fit"] = [apply_g(n, s) for n, s in zip(tgt["net"], tgt["season"])]
tgt["dD"] = tgt["fy"].map(lambda f: deltas[f]["dD"])
tgt["dN"] = tgt["fy"].map(lambda f: deltas[f]["dN"])
tgt["net_cf"] = tgt["net"] - tgt["dD"] - tgt["dN"]
tgt["p_cf"] = [apply_g(n, s) for n, s in zip(tgt["net_cf"], tgt["season"])]

def metrics(df, col):
    g = df.groupby("fy")
    daily = df.groupby(["fy", "day"])[col].apply(
        lambda x: x.sort_values().iloc[-4:].mean() - x.sort_values().iloc[:4].mean())
    pf = df.groupby(["fy", "day"])[col].apply(
        lambda x: max(0.0, ETA * x.sort_values().iloc[-4:].sum() * 1000 - x.sort_values().iloc[:4].sum() * 1000))
    return pd.DataFrame({
        "床コマ相当(h)": g[col].apply(lambda x: (x <= 0.011).sum()),
        "TB4h中央値": daily.groupby(level="fy").median().round(2),
        "昼間平均価格": df[(df["hour"] >= 10) & (df["hour"] < 14)].groupby("fy")[col].mean().round(2),
        "PF価値(円/kW-年)": (pf.groupby(level="fy").sum() / 1000).round(0),
    })

print()
print("=== 実績 ===");        print(metrics(tgt, "p_kyushu").to_string())
print("=== モデル再現(検証) ===");  print(metrics(tgt, "p_fit").to_string())
print("=== 反実仮想(需要増なし・原子力FY2023水準) ==="); print(metrics(tgt, "p_cf").to_string())

# 適合度
from numpy import corrcoef
r = corrcoef(tgt["p_kyushu"], tgt["p_fit"])[0, 1]
print(f"\nin-sample相関(実績 vs 再現): {r:.3f}")

# ---------- 4) 図 f14 ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.6, 4.4), dpi=300)
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

d25 = tgt[tgt["fy"] == 2025]
for col, c, lab in [("p_kyushu", BLUE, "実績"), ("p_cf", CORAL, "反実仮想（需要増なし・原子力FY2023水準）")]:
    g = d25.groupby("hour")[col].mean()
    ax1.plot(g.index, g.values, lw=2.2, color=c, label=lab)
ax1.set_xlabel("時刻", fontsize=9, color=INK)
ax1.set_ylabel("九州エリアプライス平均（円/kWh）", fontsize=9, color=INK)
ax1.set_title("FY2025の時間帯別平均価格", fontsize=10.5, color=INK)
ax1.legend(fontsize=8, frameon=False)

m_act = metrics(tgt, "p_kyushu")["床コマ相当(h)"]
m_fit = metrics(tgt, "p_fit")["床コマ相当(h)"]
m_cf = metrics(tgt, "p_cf")["床コマ相当(h)"]
xx = np.arange(2)
for off, series, c, lab in [(-0.26, m_act, "#184f95", "実績"),
                            (0.0, m_fit, LBLUE, "モデル再現"),
                            (0.26, m_cf, CORAL, "反実仮想")]:
    vals = [series[2024], series[2025]]
    ax2.bar(xx + off, vals, width=0.24, color=c, label=lab)
    for i, v in enumerate(vals):
        ax2.annotate(f"{int(v):,}", (i + off, v), xytext=(0, 3), textcoords="offset points",
                     ha="center", fontsize=8, color=SUB)
ax2.set_xticks(xx)
ax2.set_xticklabels(["FY2024", "FY2025"], fontsize=9)
ax2.set_ylabel("床（≤0.01円）時間数", fontsize=9, color=INK)
ax2.set_title("床時間数：実績 vs 反実仮想", fontsize=10.5, color=INK)
ax2.legend(fontsize=8, frameon=False)
fig.suptitle("反実仮想：需要増・原子力変動がなければFY2024-25の余剰と床はもっと深かった", fontsize=11.5, color=INK)
fig.text(0.1, 0.012,
         "経験的供給曲線（FY2024-25実績の net=需要−太陽光−風力−原子力 と価格の季節別単調写像）上で、需要とベースロードのみ反実仮想水準に移動。\n"
         "揚水・輸出・入札行動の反応は固定した部分均衡のため、反実仮想の床・価値は上限方向の評価。60分粒度。",
         fontsize=6.6, color=SUB)
fig.tight_layout(rect=(0, 0.055, 1, 0.94))
fig.savefig(os.path.join(FIG, "f14-counterfactual.png"), facecolor=SURFACE, bbox_inches="tight")
print("saved f14")

# 太陽光シェアの推移(発表用)
ann = p.groupby("fy").agg(solar_gwh=("solar", lambda x: x.sum() / 1000),
                          dem_gwh=("demand", lambda x: x.sum() / 1000))
ann["share_%"] = ann["solar_gwh"] / ann["dem_gwh"] * 100
print()
print("=== 太陽光発電量とエリア需要比シェア ===")
print(ann.round(1).loc[2016:2025].to_string())
