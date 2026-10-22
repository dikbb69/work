#!/usr/bin/env python3
"""表6.2 の日次回帰（analysis/24_vol_verification.py と同一仕様）を
HC3 と Newey-West HAC（lag 7, 14）で比較し、残差の自己相関を報告する。
リポジトリには書き込まない（読み取りのみ）。出力は本ディレクトリ。"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

PROC = "/Users/matsuba/work/thesis/data/processed"
OUT = os.path.dirname(os.path.abspath(__file__))
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}
MAIN = ["夏", "冬", "春秋"]


def build_daily(area, pcol):
    p = pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=[pcol]).copy()
    p["day"] = p["ts"].dt.normalize()
    p["hour"] = p["ts"].dt.hour
    cnt = p.groupby("day")["hour"].count()
    p = p[p["day"].isin(cnt[cnt == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    P = p.pivot(index="day", columns="hour", values=pcol)
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["mean_p"] = P.mean(axis=1)
    d["sd"] = P.std(axis=1)
    d["tb4"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
    d["solar"] = p.groupby("day")["solar_pre"].sum() / 1000
    d["wind"] = p.groupby("day")["wind_pre"].sum() / 1000
    d["demand"] = p.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    return d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()


def design(d):
    X = pd.DataFrame(index=d.index)
    for s in MAIN:
        m = (d["season"] == s).astype(float)
        X[f"solar_{s}"] = d["solar"] * m
        X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    return sm.add_constant(X)


def st(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


rows = []
for area, pcol in [("hokkaido", "p_hokkaido"), ("kyushu", "p_kyushu")]:
    d = build_daily(area, pcol)
    # 日付の欠落（ブラックアウト等）がある場合でも HAC は観測順で計算（近似）
    X = design(d)
    for y in ["mean_p", "tb4", "sd"]:
        m = sm.OLS(d[y], X)
        r3 = m.fit(cov_type="HC3")
        r7 = m.fit(cov_type="HAC", cov_kwds={"maxlags": 7})
        r14 = m.fit(cov_type="HAC", cov_kwds={"maxlags": 14})
        e = r3.resid.to_numpy()
        ac1 = np.corrcoef(e[:-1], e[1:])[0, 1]
        ac7 = np.corrcoef(e[:-7], e[7:])[0, 1]
        for s in MAIN:
            for src in ("solar", "wind"):
                k = f"{src}_{s}"
                rows.append(dict(area=area, y=y, coef=k, b=r3.params[k],
                                 se_hc3=r3.bse[k], p_hc3=r3.pvalues[k],
                                 se_nw7=r7.bse[k], p_nw7=r7.pvalues[k],
                                 se_nw14=r14.bse[k], p_nw14=r14.pvalues[k],
                                 resid_ac1=ac1, resid_ac7=ac7, n=len(d)))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(OUT, "p1_hac_check.csv"), index=False)
pd.set_option("display.width", 200)
for (a, y), g in out.groupby(["area", "y"], sort=False):
    print(f"\n== {a} {y} n={g.n.iloc[0]} 残差AC(1)={g.resid_ac1.iloc[0]:.2f} AC(7)={g.resid_ac7.iloc[0]:.2f}")
    for _, r in g.iterrows():
        print(f"  {r.coef:10s} b={r.b:+.3f}  HC3 se={r.se_hc3:.3f}{st(r.p_hc3):3s}  "
              f"NW7 se={r.se_nw7:.3f}{st(r.p_nw7):3s}  NW14 se={r.se_nw14:.3f}{st(r.p_nw14):3s}  "
              f"比(NW14/HC3)={r.se_nw14 / r.se_hc3:.2f}")
