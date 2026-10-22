#!/usr/bin/env python3
"""北海道 FY2023-25: 16_strategy_decomposition.py と同一仕様の PF・戦略c（気候値）を再計算し、
ファイナンス的読み替えの補助数値を出す（リポジトリには書き込まない）。
  (1) 完全予見粗利 = 日次スプレッド（交換）オプションの事後ペイオフ max(0, η·Top4 − Bot4) の年間合計
      → 行使されない日（ペイオフ0）の比率
  (2) 戦略c（予想価格形状に対して事前に固定した充放電）＝ intrinsic 型、PF との差＝完全情報の価値（VPI）
  (3) capture率の週次ブロック・ブートストラップ信頼区間
  (4) 04_spread_montecarlo.py と同一仕様（月別季節成分＋AR(1)＋残差iidブートストラップ）の北海道版
      → 年間完全予見粗利の分布（5%点＝Earnings-at-Risk 的指標）と実績の位置
"""
import os
import numpy as np
import pandas as pd

PROC = "/Users/matsuba/work/thesis/data/processed"
OUT = os.path.dirname(os.path.abspath(__file__))
ETA = 0.85
rng = np.random.default_rng(20261019)

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
days = P.index
wkP = pd.Series(P.index.dayofweek >= 5, index=P.index)


def margin(p, dis, chg):
    return (p[list(dis)].sum() * ETA - p[list(chg)].sum()) * 1000  # 円/MW-日


def win(series):
    o = series.sort_values()
    return o.index[-4:], o.index[:4]


rows = []
for i, d in enumerate(days):
    p = P.loc[d]
    raw = margin(p, *win(p))
    rec = {"day": d, "pf_raw": raw, "pf": max(0.0, raw)}
    hist_p = [dd for dd in days[max(0, i - 29):i] if wkP[dd] == wkP[d]]
    if len(hist_p) >= 5:
        rec["c"] = margin(p, *win(P.loc[hist_p].mean()))
    rows.append(rec)
bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
bt["month"] = bt["day"].dt.month
bt.to_csv(os.path.join(OUT, "p2_hokkaido_pf_c_daily.csv"), index=False)

est = bt[bt["fy"].isin([2023, 2024, 2025])].dropna(subset=["c"])
ann = est.groupby("fy")[["pf", "c"]].sum() / 1000
ann["capture_c"] = ann["c"] / ann["pf"]
ann["VPI(pf-c)"] = ann["pf"] - ann["c"]
ann["行使されない日の比率"] = est.groupby("fy")["pf_raw"].apply(lambda x: (x <= 0).mean())
print("=== (1)(2) 年間（円/kW-年）===")
print(ann.round(3).to_string())

# (3) 週次ブロック・ブートストラップ（FY別、ブロック=7日）
print("\n=== (3) capture率（c/PF）の週次ブロック・ブートストラップ 95%区間（B=2000）===")
ci_rows = []
for fy, g in est.groupby("fy"):
    g = g.reset_index(drop=True)
    nb = int(np.ceil(len(g) / 7))
    blocks = [g.iloc[k * 7:(k + 1) * 7] for k in range(nb)]
    pf_b = np.array([b["pf"].sum() for b in blocks])
    c_b = np.array([b["c"].sum() for b in blocks])
    stats = []
    for _ in range(2000):
        ix = rng.integers(0, nb, nb)
        stats.append(c_b[ix].sum() / pf_b[ix].sum())
    lo, hi = np.percentile(stats, [2.5, 97.5])
    pt = c_b.sum() / pf_b.sum()
    ci_rows.append(dict(fy=fy, capture=pt, lo=lo, hi=hi))
    print(f"FY{fy}: {pt:.3f} [{lo:.3f}, {hi:.3f}]")
pool = est.reset_index(drop=True)
nb = int(np.ceil(len(pool) / 7))
pf_b = np.array([pool.iloc[k * 7:(k + 1) * 7]["pf"].sum() for k in range(nb)])
c_b = np.array([pool.iloc[k * 7:(k + 1) * 7]["c"].sum() for k in range(nb)])
stats = [c_b[ix].sum() / pf_b[ix].sum() for ix in (rng.integers(0, nb, nb) for _ in range(2000))]
print(f"FY2023-25 プール: {c_b.sum() / pf_b.sum():.3f} [{np.percentile(stats, 2.5):.3f}, {np.percentile(stats, 97.5):.3f}]")
pd.DataFrame(ci_rows).to_csv(os.path.join(OUT, "p2_capture_ci.csv"), index=False)

# (4) 04 と同一仕様の MC（北海道、FY2023-25 推定）
m = est.set_index("day")["pf"]
mon = est.set_index("day")["month"]
s = m.groupby(mon).mean()
x = m - mon.map(s)
x0, x1 = x.iloc[:-1].to_numpy(), x.iloc[1:].to_numpy()
rho = float(np.dot(x0, x1) / np.dot(x0, x0))
eps = x1 - rho * x0
cal = pd.date_range("2027-04-01", periods=365, freq="D").month
s_cal = np.array([s[mo] for mo in cal])
N = 5000
sims = np.empty(N)
for i in range(N):
    e = rng.choice(eps, size=365, replace=True)
    xs = np.empty(365); prev = 0.0
    for t in range(365):
        prev = rho * prev + e[t]; xs[t] = prev
    sims[i] = np.maximum(0.0, s_cal + xs).sum() / 1000
q = np.percentile(sims, [5, 50, 95])
real = ann["pf"]
print(f"\n=== (4) 北海道 MC（FY2023-25 推定、5,000パス）: rho={rho:.3f} 平均={sims.mean():,.0f} "
      f"5%={q[0]:,.0f} 中央={q[1]:,.0f} 95%={q[2]:,.0f} 円/kW-年")
print("実績（同一サンプル）:", {int(k): round(v) for k, v in real.items()},
      "| 実績の分布内パーセンタイル:", {int(k): round((sims < v).mean() * 100, 1) for k, v in real.items()})
# 年度間の実績変動と MC の分布幅の比較
print(f"MC の年間値SD={sims.std():,.0f} vs 実績3年のSD={real.std(ddof=1):,.0f}")
pd.DataFrame({"sim": sims}).describe().to_csv(os.path.join(OUT, "p2_mc_summary.csv"))
