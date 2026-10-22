#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット2の補足: 年月FE仕様（S4: 需要＋曜日・祝日＋年月FE）の残差自己相関と長い帯域の NW"""
import os, sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, KEYS, build_daily, design, stars  # noqa: E402
from p2_hac_identification import add_controls, andrews_bw  # noqa: E402

rows = []
for area, pcol in [("hokkaido", "p_hokkaido"), ("kyushu", "p_kyushu")]:
    d = build_daily(area, pcol)
    X = add_controls(d, design(d), "S4", area)
    for y in ("mean_p", "tb4", "sd"):
        m = sm.OLS(d[y], X)
        f0 = m.fit()
        rho, bw = andrews_bw(f0.resid)
        fits = {"NW7": m.fit(cov_type="HAC", cov_kwds={"maxlags": 7}),
                "NW28": m.fit(cov_type="HAC", cov_kwds={"maxlags": 28}),
                "NW-Andrews": m.fit(cov_type="HAC", cov_kwds={"maxlags": bw})}
        for k in KEYS:
            r = {"area": area, "y": y, "係数": k, "推定値": f0.params[k], "残差ρ1": rho, "Andrews帯域": bw}
            for nm, f in fits.items():
                r[nm] = f"{f.bse[k]:.3f}{stars(f.pvalues[k])}"
            rows.append(r)
t = pd.DataFrame(rows)
t.to_csv(os.path.join(OUT, "p2b_ymfe_hac.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 200)
print(t.round(3).to_string(index=False))
