#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fuke & Ohashi (2025) 仕様の再現と、日内スプレッド（TB4h）との対比（第6章6.5）

F&O仕様（原典 §2–3）:
  被説明変数: 「PV time」日次データ＝太陽光が発電している時間帯の時間値価格の単純平均
  説明変数: 季節ダミー×{需要(load), 太陽光(solar), 原子力(nuclear)} ＋ 7日ラグ価格 ＋ 土日祝ダミー ＋ バイオマス増設ダミー(2018-10-01〜, 九州)
  季節: 冬12/16–3/15, 春3/16–6/30, 夏7/1–9/30, 秋10/1–12/15
  分位点回帰 τ=0.1..0.9。変動性 IQR = P(0.9)−P(0.1)、係数差 β(0.9)−β(0.1) をブートストラップで検定
  需要 = エリア需要 + 域外への送電量（九州は関門連系線の中国向け）
拡張:
  ・北海道に同仕様を適用（風力を追加）
  ・同一の日次サンプルで被説明変数を日内スプレッド TB4h（24時間中 上位4h平均−下位4h平均）に替えたOLS
  ・期間: FY2016–19（F&Oと同一）と FY2023–25（直近）
出力: data/processed/fo_replication_results.csv
"""
import os, sys, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.quantile_regression import QuantReg

warnings.filterwarnings("ignore")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROC = os.path.join(ROOT, "data", "processed")
B_BOOT = int(os.environ.get("B_BOOT", "300"))
RNG = np.random.default_rng(20260929)

try:
    import jpholiday
    def is_hol(d):
        return d.weekday() >= 5 or jpholiday.is_holiday(d.date())
except Exception:
    print("jpholiday なし → 土日＋年末年始・GWのみ", file=sys.stderr)
    def is_hol(d):
        md = (d.month, d.day)
        return d.weekday() >= 5 or md in {(1,1),(1,2),(1,3),(12,29),(12,30),(12,31),(5,3),(5,4),(5,5)}

def fo_season(idx):
    m, d = idx.month, idx.day
    md = m * 100 + d
    out = np.where((md >= 1216) | (md <= 315), "冬",
          np.where(md <= 630, "春", np.where(md <= 930, "夏", "秋")))
    return pd.Series(out, index=idx)

SEASONS = ["冬", "春", "夏", "秋"]

def build_daily(area, pcol):
    p = pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=[pcol, "demand", "nuclear"]).copy()
    p["day"] = p["ts"].dt.normalize()
    cnt = p.groupby("day")["ts"].count()
    p = p[p["day"].isin(cnt[cnt == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    # 域外送電（interconn<0 を送出とみなす）を需要に加算（F&O: 域内需要＋中国向け送電）
    p["export"] = (-p["interconn"].fillna(0)).clip(lower=0)
    p["load"] = p["demand"] + p["export"]
    pv = p[p["solar_pre"] > 0]
    d = pd.DataFrame(index=sorted(p["day"].unique()))
    g = pv.groupby("day")
    d["price"] = g[pcol].mean()                 # PV time 昼間平均価格
    d["load"] = g["load"].mean() / 1000         # GWh/h（GW）
    d["solar"] = g["solar_pre"].mean() / 1000
    d["wind"] = g["wind_pre"].mean() / 1000
    d["nuclear"] = g["nuclear"].mean() / 1000
    d["pv_hours"] = g[pcol].count()
    p["hour"] = p["ts"].dt.hour
    P = p.pivot(index="day", columns="hour", values=pcol)
    srt = np.sort(P.to_numpy(), axis=1)
    d["tb4"] = pd.Series(srt[:, -4:].mean(1) - srt[:, :4].mean(1), index=P.index)
    d["mean24"] = P.mean(axis=1)
    d = d.dropna()
    d["season"] = fo_season(d.index)
    d["hol"] = [1.0 if is_hol(t) else 0.0 for t in d.index]
    d["bio"] = (d.index >= pd.Timestamp("2018-10-01")).astype(float)
    for i in range(1, 8):
        d[f"lag{i}"] = d["price"].shift(i)
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    return d.dropna()

def design(d, with_wind, with_bio):
    X = pd.DataFrame(index=d.index)
    X["const"] = 1.0
    X["hol"] = d["hol"]
    if with_bio:
        X["bio"] = d["bio"]
    for s in SEASONS:
        m = (d["season"] == s).astype(float)
        X[f"load_{s}"] = d["load"] * m
        X[f"solar_{s}"] = d["solar"] * m
        X[f"nuclear_{s}"] = d["nuclear"] * m
        if with_wind:
            X[f"wind_{s}"] = d["wind"] * m
    for i in range(1, 8):
        X[f"lag{i}"] = d[f"lag{i}"]
    # 季節が1つも観測されない列（サブ期間）を落とす
    X = X.loc[:, (X != 0).any(axis=0)]
    return X

def qfit(y, X, tau):
    return QuantReg(y, X).fit(q=tau, max_iter=5000, p_tol=1e-6)

def run_sample(d, label, with_wind, with_bio, keys):
    X = design(d, with_wind, with_bio); y = d["price"]
    rows = []
    # 水準: τ=0.1,0.5,0.9
    fits = {t: qfit(y, X, t) for t in (0.1, 0.5, 0.9)}
    for k in keys:
        if k not in X: continue
        rows.append({"sample": label, "y": "PV時間平均価格（水準）", "var": k,
                     "q10": fits[0.1].params[k], "q50": fits[0.5].params[k], "q90": fits[0.9].params[k],
                     "IQR": fits[0.9].params[k] - fits[0.1].params[k]})
    # IQR ブートストラップ（xyペア）
    n = len(y); boots = {k: [] for k in keys if k in X}
    for b in range(B_BOOT):
        ix = RNG.integers(0, n, n)
        try:
            f1 = qfit(y.iloc[ix], X.iloc[ix], 0.1); f9 = qfit(y.iloc[ix], X.iloc[ix], 0.9)
        except Exception:
            continue
        for k in boots:
            boots[k].append(f9.params[k] - f1.params[k])
    for r in rows:
        bs = np.array(boots[r["var"]])
        r["IQR_se"] = bs.std(ddof=1)
        r["IQR_p"] = 2 * min((bs <= 0).mean(), (bs >= 0).mean())  # 符号のブートストラップp
        r["IQR_p_norm"] = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(r["IQR"] / r["IQR_se"])))
    # 同一サンプル・同一Xで TB4h（日内）と 24h平均（水準）をOLS
    for ycol, lab in (("tb4", "TB4hスプレッド（日内・OLS）"), ("mean24", "24h平均価格（OLS）")):
        res = sm.OLS(d[ycol], X).fit(cov_type="HC3")
        for k in keys:
            if k not in X: continue
            rows.append({"sample": label, "y": lab, "var": k, "OLS": res.params[k],
                         "OLS_se": res.bse[k], "OLS_p": res.pvalues[k]})
    return rows, n

def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""

all_rows = []
specs = [
    ("kyushu", "p_kyushu", "九州 FY2016–19（F&O再現）", (2016, 2019), False, True),
    ("kyushu", "p_kyushu", "九州 FY2023–25", (2023, 2025), True, False),
    ("hokkaido", "p_hokkaido", "北海道 FY2016–19", (2016, 2019), True, False),
    ("hokkaido", "p_hokkaido", "北海道 FY2023–25", (2023, 2025), True, False),
]
for area, pcol, label, (f0, f1), with_wind, with_bio in specs:
    d = build_daily(area, pcol)
    d = d[(d["fy"] >= f0) & (d["fy"] <= f1)]
    keys = [f"{v}_{s}" for v in (["load", "solar"] + (["wind"] if with_wind else [])) for s in SEASONS]
    rows, n = run_sample(d, label, with_wind, with_bio, keys)
    all_rows += rows
    print(f"\n===== {label}  n={n}日  PV時間平均価格: mean={d['price'].mean():.2f} sd={d['price'].std():.2f}  TB4h mean={d['tb4'].mean():.2f}")
    df = pd.DataFrame(rows)
    lv = df[df["y"].str.startswith("PV時間")].set_index("var")
    print("  [F&O型] 水準 q10/q50/q90 と IQR係数(β0.9−β0.1)")
    for k in keys:
        if k not in lv.index: continue
        r = lv.loc[k]
        print(f"   {k:12s} {r['q10']:8.3f} {r['q50']:8.3f} {r['q90']:8.3f} | IQR {r['IQR']:8.3f} (se {r['IQR_se']:.3f}) {stars(r['IQR_p_norm'])}")
    tb = df[df["y"].str.startswith("TB4h")].set_index("var")
    print("  [本研究型] 同一サンプル・同一X で TB4h をOLS")
    for k in keys:
        if k not in tb.index: continue
        r = tb.loc[k]
        print(f"   {k:12s} {r['OLS']:8.3f} (se {r['OLS_se']:.3f}) {stars(r['OLS_p'])}")

out = pd.DataFrame(all_rows)
out.to_csv(os.path.join(PROC, "fo_replication_results.csv"), index=False, encoding="utf-8-sig")
print("\nsaved:", os.path.join(PROC, "fo_replication_results.csv"), "B_BOOT=", B_BOOT)
