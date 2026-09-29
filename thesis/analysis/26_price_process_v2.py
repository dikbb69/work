#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""供給曲線 v2: 上側水準を年度別スケール係数 θ_FY で非定常化した価格過程（北海道）

v1（13）との違い:
  p = 0.01 ∨ { 0.01 + θ_FY · [ g(net; 季節) + μ(季節, 時刻) − 0.01 ] }
  - 形状 g・μ は FY2023-25 で推定（v1 と同じ分位ビン中央値＋単調化、季節×時刻プレミアム）。
    推定は「θ で deflate した価格」に対して行い、θ と形状を交互に更新（3回）
  - θ_FY は年度ごとの1パラメータ。床（0.01円）より上の部分だけをスケールする
    （再エネ・水力のゼロ限界費用セグメントは動かず、火力セグメントが燃料価格に比例して動く、という
    メリットオーダーの読み）。FY2023-25 の時間加重平均が 1 になるよう正規化
  - 形状固定のまま FY2022（燃料危機）と FY2026 上期（4-6月）の θ を推定 → out-of-sample 検証
    （FY2026 は形状に使っていないので、水準1パラメータだけの OOS）
  - 月次 θ_m も同じ方法で算出（燃料価格指数の代理としての「価格水準指数」）
出力: data/processed/price_level_theta.csv、標準出力の検証表
   モジュールとして exec すると predict_A(df, net_col, theta)・est（FY2023-25）・THETA を提供（27 が使う）
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROC = os.path.join(ROOT, "data", "processed")
ETA = 0.85
FLOOR = 0.01
SHAPE_FY = [2023, 2024, 2025]

# ---------- パネル・cf（13 と同一） ----------
p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
cap = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
cap = cap[cap["area"] == "hokkaido"].set_index("date")[["solar_kw", "wind_kw"]]
full = pd.date_range(cap.index.min(), pd.Timestamp("2026-06-30"), freq="ME")
cap = cap.reindex(full.union(cap.index)).ffill()
p["month_end"] = p["ts"].dt.to_period("M").dt.to_timestamp("M")
p = p.merge(cap, left_on="month_end", right_index=True, how="left")
p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
p["cf_solar"] = p["solar_pre"] / (p["solar_kw"] / 1000)
p["cf_wind"] = p["wind_pre"] / (p["wind_kw"] / 1000)
p["season"] = (p["ts"].dt.month % 12) // 3  # 気象学的4季 0:冬 1:春 2:夏 3:秋（報告用区分とは別）
p["day"] = p["ts"].dt.normalize()
p["hour"] = p["ts"].dt.hour
p["net"] = p["demand"] - p["solar_pre"] - p["wind_pre"] - p["nuclear"].fillna(0)
p["ym"] = p["ts"].dt.to_period("M")

samp = p[p["fy"].isin([2022] + SHAPE_FY + [2026])].dropna(subset=["p_hokkaido", "p_system", "net"]).copy()
est = samp[samp["fy"].isin(SHAPE_FY)].copy()


# ---------- 形状の推定（v1 と同じ関数） ----------
def fit_g(df, ycol, nbins=80):
    q = np.unique(np.quantile(df["net"], np.linspace(0, 1, nbins + 1)))
    idx = np.clip(np.searchsorted(q, df["net"], side="right") - 1, 0, len(q) - 2)
    med = df.groupby(idx)[ycol].median()
    x = ((q[:-1] + q[1:]) / 2)[med.index]
    y = np.maximum.accumulate(med.to_numpy())
    return x, y


def apply_g(G, net, season):
    out = np.empty(len(net))
    for s in range(4):
        m = season == s
        x, y = G[s]
        out[m] = np.interp(net[m], x, y, left=FLOOR, right=y[-1])
    return np.maximum(out, FLOOR)


def fit_adj(df, ycol, G):
    base = apply_g(G, df["net"].to_numpy(), df["season"].to_numpy())
    tmp = pd.DataFrame({"season": df["season"].to_numpy(), "hour": df["hour"].to_numpy(),
                        "r": df[ycol].to_numpy() - base})
    return tmp.groupby(["season", "hour"])["r"].median()


def base_price(df, G, ADJ, net_col="net"):
    """deflate 尺度での基準価格 g+μ（床で打ち切り）"""
    base = apply_g(G, df[net_col].to_numpy(), df["season"].to_numpy())
    key = pd.MultiIndex.from_arrays([df["season"].to_numpy(), df["hour"].to_numpy()])
    return np.maximum(base + ADJ.reindex(key).fillna(0).to_numpy(), FLOOR)


def fit_theta(pobs, pbase, min_base=3.0):
    """床より上（基準価格 ≥ min_base 円、観測が床でない）の時間で原点回帰: (p−0.01) = θ·(base−0.01)"""
    m = (pbase >= min_base) & (pobs > FLOOR + 0.001)
    x, y = pbase[m] - FLOOR, pobs[m] - FLOOR
    return float((x * y).sum() / (x * x).sum()), int(m.sum())


# 交互推定: θ_FY(2023-25) と形状
theta_fy = {fy: 1.0 for fy in SHAPE_FY}
for it in range(3):
    est["p_def"] = FLOOR + (est["p_hokkaido"] - FLOOR) / est["fy"].map(theta_fy)
    G = {s: fit_g(est[est["season"] == s], "p_def") for s in range(4)}
    ADJ = fit_adj(est, "p_def", G)
    est["p_base"] = base_price(est, G, ADJ)
    raw = {fy: fit_theta(est.loc[est["fy"] == fy, "p_hokkaido"].to_numpy(),
                         est.loc[est["fy"] == fy, "p_base"].to_numpy())[0] for fy in SHAPE_FY}
    w = est["fy"].value_counts()
    norm = sum(raw[fy] * w[fy] for fy in SHAPE_FY) / w.sum()   # FY2023-25 の時間加重平均を 1 に
    theta_fy = {fy: raw[fy] / norm for fy in SHAPE_FY}
    print(f"iter{it}: θ =", {k: round(v, 3) for k, v in theta_fy.items()})

# 形状固定で FY2022・FY2026 の θ を推定（OOS）
samp["p_base"] = base_price(samp, G, ADJ)
THETA = dict(theta_fy)
for fy in (2022, 2026):
    m = samp["fy"] == fy
    THETA[fy], n = fit_theta(samp.loc[m, "p_hokkaido"].to_numpy(), samp.loc[m, "p_base"].to_numpy())
THETA = {int(k): float(v) for k, v in sorted(THETA.items())}
print("θ_FY（FY2023-25平均=1）:", {k: round(v, 3) for k, v in THETA.items()})

# 月次 θ_m（価格水準指数）
rows = []
for ym, g_ in samp.groupby("ym"):
    th, n = fit_theta(g_["p_hokkaido"].to_numpy(), g_["p_base"].to_numpy())
    rows.append({"ym": str(ym), "fy": int(g_["fy"].iloc[0]), "theta_m": round(th, 3), "n_hours": n,
                 "mean_p_hokkaido": round(g_["p_hokkaido"].mean(), 2), "mean_p_system": round(g_["p_system"].mean(), 2)})
theta_m = pd.DataFrame(rows)
out = pd.concat([pd.DataFrame([{"ym": f"FY{fy}", "fy": fy, "theta_m": round(th, 3), "n_hours": int((samp["fy"] == fy).sum()),
                                "mean_p_hokkaido": round(samp.loc[samp["fy"] == fy, "p_hokkaido"].mean(), 2),
                                "mean_p_system": round(samp.loc[samp["fy"] == fy, "p_system"].mean(), 2)} for fy, th in THETA.items()]),
                 theta_m], ignore_index=True)
out.to_csv(os.path.join(PROC, "price_level_theta.csv"), index=False)


# ---------- 予測（仕様A・θ付き） ----------
def predict_A(df, net_col="net", theta=1.0):
    base = base_price(df, G, ADJ, net_col)
    return np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)


# ---------- 検証 ----------
def pf_value(df, col):
    piv = df.pivot_table(index="day", columns="hour", values=col)
    piv = piv[piv.count(axis=1) == 24]
    srt = np.sort(piv.to_numpy(), axis=1)
    m = np.maximum(0.0, (srt[:, -4:].sum(axis=1) * ETA - srt[:, :4].sum(axis=1)) * 1000)
    fy = piv.index.year - (piv.index.month < 4).astype(int)
    return pd.Series(m, index=piv.index).groupby(fy).sum() / 1000


def metrics(df, col):
    g = df.groupby("fy")
    daily = df.groupby(["fy", "day"])[col].apply(lambda x: x.sort_values().iloc[-4:].mean() - x.sort_values().iloc[:4].mean())
    return pd.DataFrame({"床(≤0.01円)時間": g[col].apply(lambda x: int((x <= 0.011).sum())),
                         "TB4h中央値": daily.groupby(level="fy").median().round(2),
                         "p05": g[col].quantile(.05).round(2), "p95": g[col].quantile(.95).round(2),
                         "PF価値(円/kW-年)": pf_value(df, col).round(0)})


if __name__ == "__main__":
    samp["p_v1"] = predict_A(samp, theta=1.0)                       # 水準固定（v1 相当）
    samp["p_v2"] = predict_A(samp, theta=samp["fy"].map(THETA).to_numpy())
    print("\n=== 実績 ===");            print(metrics(samp, "p_hokkaido").to_string())
    print("\n=== v1相当（θ=1 固定） ===");  print(metrics(samp, "p_v1").to_string())
    print("\n=== v2（θ_FY） ===");       print(metrics(samp, "p_v2").to_string())
    for fy in THETA:
        m = samp["fy"] == fy
        print(f"FY{fy}: 相関 v1 {np.corrcoef(samp.loc[m,'p_hokkaido'], samp.loc[m,'p_v1'])[0,1]:.3f} / v2 {np.corrcoef(samp.loc[m,'p_hokkaido'], samp.loc[m,'p_v2'])[0,1]:.3f}")
    print("\n=== 月次 θ_m（2025/4〜2026/6） ===")
    print(theta_m[theta_m["ym"] >= "2025-04"].to_string(index=False))
    # 4-6月だけの比較（OOS の対象期間）
    aj = samp[samp["ts"].dt.month.isin([4, 5, 6])]
    print("\n=== 4-6月のみ: 実績 / v1相当 / v2 ===")
    for col in ("p_hokkaido", "p_v1", "p_v2"):
        print(col); print(metrics(aj, col).to_string())
    print("\nsaved price_level_theta.csv")
