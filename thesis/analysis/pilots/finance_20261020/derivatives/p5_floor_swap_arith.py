#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット5（算術のみ）: 収入フロア（プット）と LTDA（固定・変動のレベニュースワップ）の読み替え
実績の年度別完全予見粗利（p2_layers_by_fy.csv、FY2016-25）から実現可能スポット収入 R = 0.81·PF − 1,752（K=0、
充電従量負担 1.2円/kWh 控除は 08章の π(K) と同じ定義）を作り、
  - 行使価格 = 参入に必要なスポット実現収益（c_req − κP_cap: 楽観19,500・標準22,000・保守28,700、08章8.4）
  - フロア（プット）の経験的価値 E[max(行使価格 − R, 0)]（年度を等確率の状態とみなす）
  - LTDA の還付後に事業者に残る変動収入 0.1·R と、固定収入との比較
"""
import os
import numpy as np
import pandas as pd
OUT = os.path.dirname(os.path.abspath(__file__))
fy = pd.read_csv(os.path.join(OUT, "p2_layers_by_fy.csv"))
pf = fy.set_index("FY")["PF年合計"]
R = 0.81 * pf - 1752
print("年度別 PF と R（円/kW-年）"); print(pd.DataFrame({"PF": pf.round(0), "R": R.round(0)}).to_string())
print(f"PF 平均 {pf.mean():.0f}, sd {pf.std():.0f}, CV {pf.std()/pf.mean():.2f}; FY2022除く CV {pf.drop(2022).std()/pf.drop(2022).mean():.2f}")
for k, strike in {"楽観": 19500, "標準": 22000, "保守": 28700}.items():
    put = np.maximum(strike - R, 0).mean()
    print(f"{k}: 行使価格 {strike}, フロアの経験的価値 {put:.0f}, 本源的価値 strike−E[R] {strike - R.mean():.0f}, R>行使価格の年度数 {(R > strike).sum()}")
print(f"LTDA 還付後に残る変動収入 0.1·E[R] = {0.1 * R.mean():.0f} 円/kW-年（K=0・実績PFベース）")
