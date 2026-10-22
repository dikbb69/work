#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット1の補足2: 水準因子 PC1 の負荷が「平均価格プロファイル（−0.01）に比例」するか
（= 第8章の水準係数 θ が (p−0.01) を比例的にスケールする仕様の経験的裏付けになるか）
比較: cos(v1, p̄−0.01)、cos(v1, 1)（平行シフト）。季節別 PCA と FY2023-25 も。"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, build_daily, MAIN_SEASONS  # noqa: E402
from p1_pca_price_curve import pca  # noqa: E402

d, P = build_daily("hokkaido", "p_hokkaido", return_matrix=True)
cell = d["fy"].astype(str) + "_" + d["season"]
dev = P - P.groupby(cell.values).transform("mean").to_numpy()
cos = lambda a, b: float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))
rows = []
subsets = {"全期間・全季節": d.index, "FY2023-25・全季節": d.index[d["fy"] >= 2023]}
for s in MAIN_SEASONS:
    subsets[f"全期間・{s}"] = d.index[d["season"] == s]
    subsets[f"FY2023-25・{s}"] = d.index[(d["season"] == s) & (d["fy"] >= 2023)]
for nm, idx in subsets.items():
    w, V = pca(dev.loc[idx].to_numpy())
    v1 = V[:, 0]
    pbar = P.loc[idx].mean().to_numpy() - 0.01
    # 比例仕様の下での v1 の理論形: (p̄−0.01) を正規化したもの
    rows.append({"標本": nm, "PC1寄与率": w[0] / w.sum(), "cos(v1, p̄−0.01)": cos(v1, pbar),
                 "cos(v1, 一様)": cos(v1, np.ones(24)), "cos(p̄−0.01, 一様)": cos(pbar, np.ones(24)),
                 "負荷の最大/最小": v1.max() / v1.min(), "p̄の最大/最小": pbar.max() / pbar.min()})
t = pd.DataFrame(rows)
t.to_csv(os.path.join(OUT, "p1c_level_factor_vs_theta.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 200)
print(t.round(3).to_string(index=False))
