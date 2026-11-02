#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの再計算（notes/38 §1、2026-11-03）: 2035年の出力制御率の照合（5.4節）に、需要もそろえた場合を足す
新しい主では2035年の太陽光・風力（356・275万kW）が北電NW の公式シミュレーション（ケース①）と同じになるので、
残るそろえていない入力は需要（モデル372.0億kWh、公式330.5億kWh）だけになる。81 の照合（原子力168万kW で一定・北本の送電770MW・
水力5,428GWh、蓄電池なし）に、需要を公式の年間量に比例で縮めた場合を足す（時間の形はモデルのまま）。
出力: data/processed/v2_curtailment_check_2035.csv
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, balance as B, merit as MO, simple as SM

PROC = os.path.join(ROOT, "data", "processed")
OFFICIAL_DEMAND_GWH = 33_050.0                                   # 公式の年間需要（5.4節の脚注の集計）
SCENS = os.environ.get("SCENS", "主,旧の主").split(",")


def main():
    warnings.filterwarnings("ignore")
    rows = []
    for scen in SCENS:
        sc = PR.SCENARIOS[scen]
        cal = SM.calibration("commit")
        before, _ = SM.exit_years(cal, sc, PR.YEARS, "commit")
        sy = PR.scenario_year(2035, sc)
        I0 = MO.inputs_future(sy, sc)
        units = B.fleet(2035, drop=before[2035])
        yrs = I0["D"].shape[0] / 365.25
        I1 = dict(I0, N=np.full_like(I0["N"], 1680.0), largest=np.full_like(I0["N"], PR.NUC["泊3号"]))
        I2 = dict(I1, link=(770.0, I1["link"][1]))
        I3 = dict(I2, Hy=I2["Hy"] * 5_428.0 / (I2["Hy"].sum() / yrs / 1e3))
        dem = I3["D"].sum() / yrs / 1e3
        I4 = dict(I3, D=I3["D"] * OFFICIAL_DEMAND_GWH / dem)
        for lab, I, mr in (("公式の原子力・送電・水力、マストラン3台（主）", I3, None), ("同、マストランなし", I3, ()),
                           ("公式の原子力・送電・水力・需要、マストラン3台（主）", I4, None), ("同、マストランなし", I4, ())):
            R = SM.dispatch(I, units, mustrun=mr)
            ch = R["curt"] > 1e-6
            rows.append({"シナリオ": scen, "照合": lab, "需要(GWh)": float(I["D"].sum() / yrs / 1e3),
                         "太陽光 系統(万kW)": sy["solar_mw"] / 10, "風力(万kW)": sy["wind_mw"] / 10,
                         "出力制御率": float(R["curt"].sum() / (I["S"] + I["W"]).sum()), "出力制御の時間(h/年)": float(ch.sum() / yrs)})
            print(rows[-1], flush=True)
    rows.append({"シナリオ": "公式", "照合": "北電NW 公式シミュレーション（ケース①）", "需要(GWh)": OFFICIAL_DEMAND_GWH, "太陽光 系統(万kW)": 356.0,
                 "風力(万kW)": 275.0, "出力制御率": 0.300, "出力制御の時間(h/年)": 3972.0})
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(PROC, "v2_curtailment_check_2035.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(T.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
