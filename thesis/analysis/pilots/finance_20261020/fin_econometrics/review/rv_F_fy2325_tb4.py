# FY2023-25 の主仕様で TB4h・日平均・夕方−昼コントラスト・夕方−夜コントラストを推定（NW14）
import os, sys
import numpy as np, pandas as pd, statsmodels.api as sm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, KEYS, build_daily, design
d, P = build_daily("hokkaido", "p_hokkaido", return_matrix=True)
P = P.astype(float)
d["eve_mid"] = P[[17, 18, 19]].mean(axis=1) - P[[11, 12, 13]].mean(axis=1)
d["eve_night"] = P[[17, 18, 19]].mean(axis=1) - P[[2, 3, 4]].mean(axis=1)
d["floor_hrs"] = (P <= 0.011).sum(axis=1)
rows = []
for tag, sub in [("FY2016-25", d), ("FY2023-25", d[d["fy"] >= 2023])]:
    X = design(sub)
    for y in ("tb4", "eve_mid", "eve_night"):
        f = sm.OLS(sub[y], X).fit(cov_type="HAC", cov_kwds={"maxlags": 14})
        for k in KEYS:
            rows.append({"標本": tag, "y": y, "係数": k, "推定値": f.params[k], "p_NW14": f.pvalues[k]})
    print(tag, "下限張り付き時間（日平均, 季節別）:", sub.groupby("season")["floor_hrs"].mean().round(2).to_dict())
t = pd.DataFrame(rows)
t["表示"] = [f"{v:+.3f}" + ("***" if p < .01 else "**" if p < .05 else "*" if p < .1 else "") for v, p in zip(t["推定値"], t["p_NW14"])]
pd.set_option("display.width", 200)
print(t.pivot_table(index="係数", columns=["標本", "y"], values="表示", aggfunc="first").loc[KEYS].to_string())
t.to_csv(os.path.join(OUT, "rv_F_contrasts.csv"), index=False, encoding="utf-8-sig")
