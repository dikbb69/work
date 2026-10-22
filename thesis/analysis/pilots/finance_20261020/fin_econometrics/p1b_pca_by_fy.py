#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット1の補足: 年度別 PCA（FY×季節×時刻の平均を除いた偏差）で、形状因子（PC2以降）の寄与率の推移を見る"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, build_daily  # noqa: E402
from p1_pca_price_curve import pca  # noqa: E402

d, P = build_daily("hokkaido", "p_hokkaido", return_matrix=True)
cell = d["fy"].astype(str) + "_" + d["season"]
dev = P - P.groupby(cell.values).transform("mean").to_numpy()
rows = []
for fy, idx in d.groupby("fy").groups.items():
    w, V = pca(dev.loc[idx].to_numpy())
    sh = w / w.sum()
    tot_sd = float(np.sqrt(w.sum()))
    rows.append({"FY": fy, "日数": len(idx), "PC1寄与率": sh[0], "PC2寄与率": sh[1], "PC3寄与率": sh[2],
                 "PC1負荷と一様ベクトルのcos": float(V[:, 0].sum() / np.sqrt(24)),
                 "PC2の夕方−昼負荷": float(V[17:20, 1].mean() - V[11:14, 1].mean()),
                 "総変動の平方根(円/kWh)": tot_sd,
                 "PC1のSD": float(np.sqrt(w[0])), "PC2+のSD": float(np.sqrt(w[1:].sum()))})
t = pd.DataFrame(rows)
t.to_csv(os.path.join(OUT, "p1b_pca_by_fy.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 200)
print(t.round(3).to_string(index=False))
