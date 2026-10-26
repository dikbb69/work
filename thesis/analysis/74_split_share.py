#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""蓄電池の稼ぎが、北海道が東北から分断している時間にどれだけ集まるか（主の経路、2つの場合、先に入っている量と0・50・100万kW）

  - 東北と同じ価格の時間（分断していない時間）
  - 放電4時間のうち東北と同じ価格の割合、放電の収入のうち分断している時間の割合
  - 充電4時間のうち0.01円の割合
出力: data/processed/eqm_split_share.csv
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, balance as B, calibrate as CB, battery as BT, merit as MO

PROC = os.path.join(ROOT, "data", "processed")


def main():
    import warnings
    warnings.filterwarnings("ignore")
    cal = CB.calibration(0.0)
    sc = PR.SCENARIOS["主"]
    rows = []
    for y in PR.YEARS:
        I = MO.inputs_future(PR.scenario_year(y, sc), sc)
        for mode in ("capacity", "spot"):
            df, _ = BT.run_year(I, cal, mode, 14_972.0, Ks=np.array([0.0, 50.0, 100.0]))
            for _, r in df.iterrows():
                rows.append({"年": y, "価格の作り方": {"capacity": "容量回収", "spot": "スポット回収"}[mode], "K(万kW)": r["K(万kW)"],
                             "東北と同じ価格の時間(h/年)": r["東北と同じ価格の時間(h/年)"], "0.01円の時間(h/年)": r["0.01円の時間(h/年)"],
                             "北海道が価格を決める時間(h/年)": r["北海道が価格を決める時間(h/年)"],
                             "放電4時間のうち東北と同じ価格の割合": r["放電4時間のうち東北と同じ価格の割合"],
                             "放電の収入のうち分断している時間の割合": r["放電の収入のうち分断している時間の割合"],
                             "充電4時間のうち0.01円の割合": r["充電4時間のうち0.01円の割合"], "π(円/kW-年)": r["π(円/kW-年)"]})
        print(y, flush=True)
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(PROC, "eqm_split_share.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(T.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
