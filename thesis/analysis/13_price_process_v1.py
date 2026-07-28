#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フェーズB: 北海道の価格過程モデル v1

構成:
  1. cf過程: 制御前VRE出力 ÷ 導入量（area_capacity_series）で設備利用率系列を抽出
  2. 供給曲線 g: p = g(net_pre; 季節) + μ(季節,時刻) で推定
     - g: 分位ビン中央値＋単調化（0.01円は左側センサリング）
     - μ: 時刻別の中央値残差（ランプ・希少性など net で説明できない日内プレミアム）
     - 仕様A: 全時間帯で単一の局所供給曲線（07の九州反実仮想と同方式）
     - 仕様B: 市場分断3レジーム（安値分断/連系/高値分断）の混合
       レジーム確率は net の多項ロジット、連系時は p_system を適用（共通乱数で比較）
  3. 検証: FY2023-25の in-sample 再現（床コマ・TB4h・PF価値・分位点）＋FY2026 OOS
  4. レバー実験: K_wind +50万kW / 泊3号再稼働 / 両方（FY2023-25の気象・需要パス上）

限界(v1): 部分均衡（揚水・連系線潮流・入札行動は g に埋め込まれた歴史的応答のまま固定）。
         連系レジームの p_system は外生（観測値）。ランプ費用・時間帯効果なし。
出力: data/processed/hokkaido_cf_series.csv と標準出力の検証表
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
ETA = 0.85
RNG = np.random.default_rng(20260728)

# ---------- 1. パネルとcf過程 ----------
p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
cap = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
cap = cap[cap["area"] == "hokkaido"].set_index("date")[["solar_kw", "wind_kw"]]
# B表の最終月(2025/12)以降は直近値ホールドで延長（FY2026のcf算出用・保守的）
full = pd.date_range(cap.index.min(), p_end := pd.Timestamp("2026-06-30"), freq="ME")
cap = cap.reindex(full.union(cap.index)).ffill()

p["month_end"] = p["ts"].dt.to_period("M").dt.to_timestamp("M")
p = p.merge(cap, left_on="month_end", right_index=True, how="left")
p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
p["cf_solar"] = p["solar_pre"] / (p["solar_kw"] / 1000)
p["cf_wind"] = p["wind_pre"] / (p["wind_kw"] / 1000)
p[["ts", "cf_solar", "cf_wind"]].to_csv(os.path.join(PROC, "hokkaido_cf_series.csv"), index=False)

p["season"] = (p["ts"].dt.month % 12) // 3  # 0:冬 1:春 2:夏 3:秋
p["day"] = p["ts"].dt.normalize()
p["net"] = p["demand"] - p["solar_pre"] - p["wind_pre"] - p["nuclear"].fillna(0)

est = p[p["fy"].isin([2023, 2024, 2025])].dropna(subset=["p_hokkaido", "p_system", "net"]).copy()
oos = p[p["fy"] == 2026].dropna(subset=["p_hokkaido", "p_system", "net"]).copy()
est["regime"] = np.select(
    [est["p_hokkaido"] < est["p_system"] - 0.01, est["p_hokkaido"] > est["p_system"] + 0.01],
    [0, 2], default=1)  # 0=安値分断 1=連系 2=高値分断
print("推定サンプル: FY2023-25", len(est), "時間 | レジーム構成:",
      dict(zip(*np.unique(est["regime"], return_counts=True))))


# ---------- 2. 供給曲線の推定 ----------
def fit_g(df, nbins=80):
    q = np.unique(np.quantile(df["net"], np.linspace(0, 1, nbins + 1)))
    idx = np.clip(np.searchsorted(q, df["net"], side="right") - 1, 0, len(q) - 2)
    med = df.groupby(idx)["p_hokkaido"].median()
    x = ((q[:-1] + q[1:]) / 2)[med.index]
    y = np.maximum.accumulate(med.to_numpy())
    return x, y


def apply_g(G, net, season):
    out = np.empty(len(net))
    for s in range(4):
        m = season == s
        x, y = G[s]
        out[m] = np.interp(net[m], x, y, left=0.01, right=y[-1])
    return np.maximum(out, 0.01)


def fit_adj(df, G):
    """時刻別プレミアム μ(季節,時刻): g の残差の中央値"""
    base = apply_g(G, df["net"].to_numpy(), df["season"].to_numpy())
    tmp = pd.DataFrame({"season": df["season"].to_numpy(),
                        "hour": df["ts"].dt.hour.to_numpy(),
                        "r": df["p_hokkaido"].to_numpy() - base})
    return tmp.groupby(["season", "hour"])["r"].median()


def apply_adj(base, season, hour, adj):
    key = pd.MultiIndex.from_arrays([season, hour])
    return np.maximum(base + adj.reindex(key).fillna(0).to_numpy(), 0.01)


# 仕様A: 単一曲線
GA = {s: fit_g(est[est["season"] == s]) for s in range(4)}
ADJ_A = fit_adj(est, GA)
# 仕様B: レジーム別曲線（安値分断・高値分断）＋レジーム確率（netの3値ロジット）
GB_low = {s: fit_g(est[(est["season"] == s) & (est["regime"] == 0)]) for s in range(4)}
GB_high = {s: fit_g(est[(est["season"] == s) & (est["regime"] == 2)]) for s in range(4)}
ADJ_low = fit_adj(est[est["regime"] == 0], GB_low)
ADJ_high = fit_adj(est[est["regime"] == 2], GB_high)


def predict_A(df, net_col="net"):
    base = apply_g(GA, df[net_col].to_numpy(), df["season"].to_numpy())
    return apply_adj(base, df["season"].to_numpy(), df["ts"].dt.hour.to_numpy(), ADJ_A)

import statsmodels.api as sm

X = sm.add_constant(np.column_stack([est["net"] / 1000, (est["net"] / 1000) ** 2,
                                     pd.get_dummies(est["season"]).iloc[:, 1:].to_numpy(dtype=float)]))
mn = sm.MNLogit(est["regime"], X).fit(disp=0, maxiter=200)


def regime_probs(net, season):
    Xn = sm.add_constant(np.column_stack([net / 1000, (net / 1000) ** 2,
                                          np.column_stack([(season == s).astype(float) for s in (1, 2, 3)])]))
    return mn.predict(Xn)  # (n,3)


def simulate_B(df, net_col="net", psys_col="p_system"):
    net = df[net_col].to_numpy()
    season = df["season"].to_numpy()
    hour = df["ts"].dt.hour.to_numpy()
    pr = regime_probs(net, season)
    u = np.random.default_rng(20260728).random(len(df))  # 共通乱数（シナリオ比較のMCノイズ除去）
    reg = np.select([u < pr[:, 0], u < pr[:, 0] + pr[:, 1]], [0, 1], default=2)
    out = np.empty(len(df))
    for s in range(4):
        for regv, G in ((0, GB_low), (2, GB_high)):
            m = (season == s) & (reg == regv)
            x, y = G[s]
            out[m] = np.interp(net[m], x, y, left=0.01, right=y[-1])
    for regv, adj in ((0, ADJ_low), (2, ADJ_high)):
        m = reg == regv
        out[m] = apply_adj(out[m], season[m], hour[m], adj)
    out[reg == 1] = df[psys_col].to_numpy()[reg == 1]
    return np.maximum(out, 0.01)


# ---------- 3. 検証 ----------
def pf_value(df, col):
    piv = df.pivot_table(index="day", columns=df["ts"].dt.hour, values=col)
    piv = piv[piv.count(axis=1) == 24]
    vals = piv.to_numpy()
    srt = np.sort(vals, axis=1)
    m = np.maximum(0.0, (srt[:, -4:].sum(axis=1) * ETA - srt[:, :4].sum(axis=1)) * 1000)
    fy = piv.index.year - (piv.index.month < 4).astype(int)
    return pd.Series(m, index=piv.index).groupby(fy).sum() / 1000


def metrics(df, col):
    g = df.groupby("fy")
    daily = df.groupby(["fy", "day"])[col].apply(
        lambda x: x.sort_values().iloc[-4:].mean() - x.sort_values().iloc[:4].mean())
    return pd.DataFrame({
        "床(≤0.01円)時間": g[col].apply(lambda x: int((x <= 0.011).sum())),
        "TB4h中央値": daily.groupby(level="fy").median().round(2),
        "p05": g[col].quantile(.05).round(2), "p95": g[col].quantile(.95).round(2),
        "PF価値(円/kW-年)": pf_value(df, col).round(0),
    })


est["p_A"] = predict_A(est)
est["p_B"] = simulate_B(est)
oos["p_A"] = predict_A(oos)
oos["p_B"] = simulate_B(oos)

print("\n=== in-sample 再現（FY2023-25） ===")
print("実績:");      print(metrics(est, "p_hokkaido").to_string())
print("仕様A(単一曲線):"); print(metrics(est, "p_A").to_string())
print("仕様B(分断混合):"); print(metrics(est, "p_B").to_string())
print("相関: A", round(np.corrcoef(est["p_hokkaido"], est["p_A"])[0, 1], 3),
      "/ B", round(np.corrcoef(est["p_hokkaido"], est["p_B"])[0, 1], 3))
print("\n=== out-of-sample（FY2026 4-6月） ===")
print("実績:");  print(metrics(oos, "p_hokkaido").to_string())
print("仕様A:"); print(metrics(oos, "p_A").to_string())
print("仕様B:"); print(metrics(oos, "p_B").to_string())

# ---------- 4. レバー実験（FY2023-25パス上・仕様Bと仕様A併記） ----------
K_WIND_NOW = est["wind_kw"].mean() / 1e4  # 万kW表示用
levers = {
    "①風力+50万kW": {"dwind_kw": 500_000, "dnuc": 0},
    "②泊3号再稼働(稼働率90%)": {"dwind_kw": 0, "dnuc": 912_000 * 0.9 / 1000},
    "③両方": {"dwind_kw": 500_000, "dnuc": 912_000 * 0.9 / 1000},
}
base_B = metrics(est, "p_B")
print(f"\n=== レバー実験（FY2023-25の気象・需要パス、現行風力平均{K_WIND_NOW:.0f}万kW） ===")
print("ベース(仕様B再現):"); print(base_B.to_string())
for name, lv in levers.items():
    sc = est.copy()
    sc["net"] = sc["net"] - lv["dwind_kw"] * sc["cf_wind"] / 1000 - lv["dnuc"]
    sc["p_B"] = simulate_B(sc)
    sc["p_A2"] = predict_A(sc)
    mB = metrics(sc, "p_B")
    mA = metrics(sc, "p_A2")
    print(f"\n--- {name} ---")
    print("仕様B:"); print(mB.to_string())
    print("仕様A ΔPF(円/kW-年):", (mA["PF価値(円/kW-年)"] - metrics(est, "p_A")["PF価値(円/kW-年)"]).round(0).to_dict())
