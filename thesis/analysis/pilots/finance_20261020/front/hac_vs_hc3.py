#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""棚卸し用の補助計算（リポジトリには書き込まない）
1. analysis/24_vol_verification.py の日次回帰を複製し、HC3 と Newey-West(HAC, lag 7/14) の SE を比較
2. 残差の1次自己相関
3. 下限張り付き時間の比率（打ち切り分位点回帰の必要性の判定）
4. 完全予見粗利の「行使しない日」（max(0,·) が0の日）の比率
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

PROC = "/Users/matsuba/work/thesis/data/processed"
OUT = os.path.dirname(os.path.abspath(__file__))

SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}
MAIN_SEASONS = ["夏", "冬", "春秋"]


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
    # 完全予見粗利（4h, η=0.85, 円/kW-日）= max(0, 0.85*Σtop4 − Σbottom4)
    d["pf"] = np.maximum(0.0, 0.85 * srt[:, -4:].sum(axis=1) - srt[:, :4].sum(axis=1))
    d["pf_raw"] = 0.85 * srt[:, -4:].sum(axis=1) - srt[:, :4].sum(axis=1)
    d["solar"] = p.groupby("day")["solar_pre"].sum() / 1000
    d["wind"] = p.groupby("day")["wind_pre"].sum() / 1000
    d["demand"] = p.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    d = d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()
    return d, p


def design(d):
    X = pd.DataFrame(index=d.index)
    for s in MAIN_SEASONS:
        m = (d["season"] == s).astype(float)
        X[f"solar_{s}"] = d["solar"] * m
        X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X,
                   pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    return sm.add_constant(X)


rows = []
for area, pcol in [("hokkaido", "p_hokkaido"), ("kyushu", "p_kyushu")]:
    d, p = build_daily(area, pcol)
    X = design(d)
    for ycol in ("mean_p", "tb4"):
        hc3 = sm.OLS(d[ycol], X).fit(cov_type="HC3")
        resid = hc3.resid
        rho1 = float(np.corrcoef(resid[1:], resid[:-1])[0, 1])
        fits = {"HC3": hc3}
        for L in (7, 14):
            fits[f"HAC{L}"] = sm.OLS(d[ycol], X).fit(cov_type="HAC", cov_kwds={"maxlags": L})
        for s in MAIN_SEASONS:
            for src in ("solar", "wind"):
                k = f"{src}_{s}"
                r = {"area": area, "y": ycol, "var": k, "coef": hc3.params[k], "rho1_resid": rho1}
                for nm, f in fits.items():
                    r[f"se_{nm}"] = f.bse[k]
                    r[f"p_{nm}"] = f.pvalues[k]
                rows.append(r)
    # 下限張り付き比率（時間値）
    p["fy"] = p["ts"].dt.year - (p["ts"].dt.month < 4).astype(int)
    for f0, f1 in ((2016, 2019), (2023, 2025)):
        sub = p[(p["fy"] >= f0) & (p["fy"] <= f1)]
        share = float((sub[pcol] <= 0.011).mean())
        print(f"{area} FY{f0}-{f1}: 下限張り付き時間の比率 = {share*100:.2f}% (n={len(sub)})")
    # 完全予見粗利が0の日（行使しない日）の比率、FY2023-25
    s = d[(d["fy"] >= 2023) & (d["fy"] <= 2025)]
    print(f"{area} FY2023-25: 完全予見粗利が0（休止）の日の比率 = {(s['pf_raw'] <= 0).mean()*100:.2f}%, 年平均 PF = {s.groupby('fy')['pf'].sum().round(0).to_dict()}")

out = pd.DataFrame(rows)
out.to_csv(os.path.join(OUT, "hac_vs_hc3.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 200)
show = out.copy()
for c in [c for c in show.columns if c.startswith("se_") or c.startswith("p_") or c in ("coef", "rho1_resid")]:
    show[c] = show[c].round(3)
print(show.to_string(index=False))
