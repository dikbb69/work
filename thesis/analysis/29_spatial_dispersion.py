#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""6.4 空間分散シミュレーション: 集中立地の反実仮想（日内帯域を λ 倍に増幅）を価格過程 v2 に通す

手順（5.2.5）:
  1. FY2023-25 の実フリート風力（制御前, MWh）を 08 と同じ移動平均カスケードで帯域分解
       <6h = x − MA6h, 6–24h = MA6h − MA24h, 1–7日 = MA24h − MA168h, >7日 = MA168h − 平均
  2. 合成系列 x_λ = x + (λ−1)(b_<6h + b_6–24h) を 0〜設備容量でクリップし、日次エネルギーが実績と一致するよう日ごとに再スケール
     （λ=1 が実フリート。λ は「日内帯域の振幅倍率」。分散シェアは λ² で効く）
  3. net_λ = 需要 − 太陽光 − x_λ − 原子力 を供給曲線 v2（仕様A, θ=1）に通し、床時間・TB4h・p95・PF価値を比較
  4. 日次回帰: 日内TB4h（モデル価格）を風力（合成, GWh/日）×季節（夏/冬/不需要期）＋太陽光×季節＋需要＋FY・季節ダミーに回帰し、
     風力→日内形状の係数が λ でどう動くか（分散立地が「中立性」を作るか）を見る
出力: data/processed/spatial_dispersion.csv・figures/hokkaido/spatial_dispersion.png
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib import font_manager
import matplotlib.pyplot as plt

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
PROC = os.path.join(ROOT, "data", "processed")
GRAY = "#595959"

ns = {"__file__": os.path.join(HERE, "26_price_process_v2.py"), "__name__": "pp_v2"}
exec(open(os.path.join(HERE, "26_price_process_v2.py"), encoding="utf-8").read(), ns)
est = ns["est"].sort_values("ts").reset_index(drop=True).copy()
predict_A = ns["predict_A"]
metrics = ns["metrics"]
ETA = 0.85
LAMBDAS = [1.0, 1.5, 2.0, 3.0, 4.0]
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬", 3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}  # 2026-10-04: 9月は夏

# 連続時系列（欠測時間はゼロ埋めではなく補間）で帯域分解
ts_full = pd.date_range(est["ts"].min(), est["ts"].max(), freq="h")
x = est.set_index("ts")["wind_pre"].reindex(ts_full).interpolate(limit_direction="both")
cap_mwh = est.set_index("ts")["wind_kw"].reindex(ts_full).ffill().bfill() / 1000


def bands(x):
    ma6 = x.rolling(6, center=True, min_periods=3).mean()
    ma24 = x.rolling(24, center=True, min_periods=12).mean()
    ma168 = x.rolling(168, center=True, min_periods=84).mean()
    return {"<6h": x - ma6, "6-24h": ma6 - ma24, "1-7d": ma24 - ma168, ">7d": ma168 - x.mean()}


def shares(x):
    b = bands(x); v = x.var()
    return {k: float(s.var() / v * 100) for k, s in b.items()}


b0 = bands(x)
intra0 = b0["<6h"] + b0["6-24h"]
print("実フリートの帯域分散シェア(%):", {k: round(v, 1) for k, v in shares(x).items()})


def synth(lam):
    y = x + (lam - 1.0) * intra0
    y = y.clip(lower=0.0, upper=cap_mwh)
    day = y.index.normalize()
    scale = x.groupby(day).sum() / y.groupby(day).sum().replace(0, np.nan)
    y = (y * scale.reindex(day).to_numpy()).clip(lower=0.0, upper=cap_mwh)
    return y


def daily_reg(df, pcol, wcol):
    P = df.pivot(index="day", columns="hour", values=pcol)
    P = P[P.count(axis=1) == 24]
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["tb4"] = srt[:, -4:].mean(1) - srt[:, :4].mean(1)
    d["wind"] = df.groupby("day")[wcol].sum() / 1000
    d["solar"] = df.groupby("day")["solar_pre"].sum() / 1000
    d["demand"] = df.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    d = d.dropna()
    X = pd.DataFrame(index=d.index)
    for s in ["夏", "冬", "春秋"]:
        m = (d["season"] == s).astype(float)
        X[f"wind_{s}"] = d["wind"] * m
        X[f"solar_{s}"] = d["solar"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    res = sm.OLS(d["tb4"], sm.add_constant(X)).fit(cov_type="HC3")
    return {s: (float(res.params[f"wind_{s}"]), float(res.pvalues[f"wind_{s}"])) for s in ["夏", "冬", "春秋"]}


rows = []
for lam in LAMBDAS:
    y = synth(lam)
    sh = shares(y)
    df = est.copy()
    df["wind_syn"] = y.reindex(df["ts"]).to_numpy()
    df["net_syn"] = df["demand"] - df["solar_pre"] - df["wind_syn"] - df["nuclear"].fillna(0)
    df["p_syn"] = predict_A(df, net_col="net_syn", theta=1.0)
    m = metrics(df, "p_syn")
    reg = daily_reg(df, "p_syn", "wind_syn")
    r = {"λ": lam, "日内シェア(<24h,%)": round(sh["<6h"] + sh["6-24h"], 1), "<6h(%)": round(sh["<6h"], 1), "6-24h(%)": round(sh["6-24h"], 1),
         "1-7d(%)": round(sh["1-7d"], 1), ">7d(%)": round(sh[">7d"], 1),
         "床時間(h/年)": round(m["床(≤0.01円)時間"].mean()), "TB4h中央値": round(m["TB4h中央値"].mean(), 2),
         "p05": round(m["p05"].mean(), 2), "p95": round(m["p95"].mean(), 2), "PF価値(円/kW-年)": round(m["PF価値(円/kW-年)"].mean()),
         "日次エネルギー相関": round(float(np.corrcoef(x.groupby(x.index.normalize()).sum(), y.groupby(y.index.normalize()).sum())[0, 1]), 4)}
    for s in ["夏", "冬", "春秋"]:
        r[f"β_wind→TB4h {s}"] = round(reg[s][0], 3); r[f"p {s}"] = round(reg[s][1], 3)
    rows.append(r); print(r)
out = pd.DataFrame(rows)
out.to_csv(os.path.join(PROC, "spatial_dispersion.csv"), index=False)

# 実績価格での同じ回帰（参照: 6.2 と同じ仕様、FY2023-25 のみ）
ref = daily_reg(est.assign(day=est["ts"].dt.normalize()), "p_hokkaido", "wind_pre")
print("参照（実績価格, FY2023-25）: β_wind→TB4h", {s: (round(v[0], 3), round(v[1], 3)) for s, v in ref.items()})

# ---------- 図 ----------
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
ax = axes[0]
ax.plot(out["λ"], out["PF価値(円/kW-年)"], color="#0079C2", lw=2.2, marker="o", label="PF価値（円/kW-年、左軸）")
ax.set_ylabel("PF価値（円/kW-年）", color=GRAY); ax.set_xlabel("日内帯域の振幅倍率 λ（1=実フリート）", color=GRAY)
ax2 = ax.twinx()
ax2.plot(out["λ"], out["TB4h中央値"], color="#D95B20", lw=2.2, marker="s", label="TB4h中央値（円/kWh、右軸）")
ax2.plot(out["λ"], out["床時間(h/年)"] / 100, color="#176871", lw=1.6, marker="^", ls="--", label="床時間（百時間/年、右軸）")
ax2.set_ylabel("TB4h（円/kWh）／床時間（百h/年）", color=GRAY)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, fontsize=8.5, frameon=False, loc="upper left")
ax.set_title("(a) 集中立地の反実仮想と蓄電池価値", fontsize=11)
for a in (ax, ax2):
    a.tick_params(colors=GRAY)
    for sp_ in ("top",):
        a.spines[sp_].set_visible(False)
ax = axes[1]
for s, c in (("夏", "#D95B20"), ("冬", "#0079C2"), ("春秋", "#176871")):
    ax.plot(out["λ"], out[f"β_wind→TB4h {s}"], color=c, lw=2.2, marker="o", label=("不需要期" if s == "春秋" else s))
ax.axhline(0, color="#999999", lw=1)
ax.set_xlabel("日内帯域の振幅倍率 λ（1=実フリート）", color=GRAY); ax.set_ylabel("風力→TB4h の係数（円/kWh per GWh/日）", color=GRAY)
ax.set_title("(b) 風力の日次発電量が日内スプレッドに与える効果", fontsize=11)
ax.legend(fontsize=9, frameon=False); ax.tick_params(colors=GRAY)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
fig.suptitle("空間分散シミュレーション — 日内帯域を増幅した集中立地の反実仮想（供給曲線v2・FY2023-25パス）", fontsize=12.5, fontweight="bold", y=1.02)
fig.text(0.99, -0.03, "λ: 実フリート風力の <6h・6–24h 帯域の振幅倍率（日次エネルギー保存・0〜設備容量でクリップ）。回帰はFY・季節ダミー、太陽光×季節、需要をコントロール（HC3）", ha="right", fontsize=7.5, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "spatial_dispersion.png"), dpi=160, bbox_inches="tight")
print("saved spatial_dispersion.png")
