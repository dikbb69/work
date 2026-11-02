#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデル: 判断の材料（2026-10-31）。泊の号機の置き方と、OCCTO 将来の電力需給シナリオ 第12回（2026-10-27）の2040年の値で、
既設＋LTDA の98.8万kW での π と、市場だけで入る量（その年の π が参入のしきい値まで下がる量）がどう変わるか（容量価格14,972円、主の上乗せ）。
前提はこのスクリプトの中だけで差し替える（params は変えない）。
- 泊2号は2033年度から（北海道電力 経営ビジョン2035 p.18「2030年代前半に全基」の読み、仮定）、定検の周期は3号・1号と重ならないようにずらす（仮定）
- 第12回の2040年: 需要 310／410億kWh（資料2-2 p.61）、DC・半導体の増分 20／40億kWh（p.64〜65）、太陽光 300／420万kW のうち併設型 60／130（p.75〜76）、
  風力 400／720万kW（同）、北本 両方向60万kW（資料2-1 p.106〜109、運用容量−マージン）。火力小＝2040年までに運開45年の号機（苫東厚真1・2、知内1）を外す
出力: data/processed/simple_decision_sensitivity.csv
記録: CSV は判断の前の主（第11回の2040年の値、2035年までは需要想定・供給計画、泊3号＋1号）で計算した。2026-10-31 の決定で主が変わったので、今これを回すと土台が新しい主になる
"""
import os
import sys
import warnings
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
from model import params as PR, merit as MO, simple as SM, entry as EN

KS = [0.0, 10.0, 25.0, 50.0, 75.0, 95.0, 100.0, 125.0, 150.0, 200.0, 300.0]
P = 14_972.0
EXIT = pd.read_csv(os.path.join(ROOT, "data", "processed", "simple_exit_years.csv"))
EXIT = EXIT[EXIT["場合"] == "上乗せ"]
OLD45 = ("苫東厚真1", "知内1", "苫東厚真2")                  # 2040年までに運開から45年（1980・1983・1985年運開、params.UNITS）


def setup():
    PR.NUC_START["泊2号"] = (2033, 4)                        # 3基の案: 2号は2033年度から（「2030年代前半に全基」の読み、仮定）
    PR.NUC_OUTAGE["phase"]["泊2号"] = 120                    # 定検が3号・1号と重ならないようにずらす（仮定）


def nuc_list(y, units):
    return [(u, None if (y > PR.NUC_START[u][0] or PR.NUC_START[u][1] == 4) else PR.NUC_START[u][1]) for u in units if y >= PR.NUC_START[u][0]]


def job(args):
    import warnings; warnings.filterwarnings("ignore")
    setup()
    name, y, mod = args
    sc = PR.SCENARIOS["主"]
    sy = PR.scenario_year(y, sc)
    if "nuclear" in mod:
        sy["nuclear"] = nuc_list(y, mod["nuclear"])
    if "y2040" in mod:                                        # 第12回の2040年の値
        d = mod["y2040"]
        sy["demand_gwh"], sy["dc_gwh"] = d["demand"], d["dc"]
        s35 = PR.SOLAR_MW[2035]
        inc = max(d["solar"] - s35, 0.0)
        sy["solar_mw"], sy["selfcons_mw"] = s35 + (1 - d["share"]) * inc, d["share"] * inc
        sy["wind_mw"] = d["wind"]
    I = MO.inputs_future(sy, sc)
    if "link" in mod:
        I["link"] = mod["link"]
    drop = tuple(EXIT[EXIT["退出の年"] < y]["号機"]) + tuple(u for u in mod.get("drop", ()) if u not in tuple(EXIT[EXIT["退出の年"] < y]["号機"]))
    cal = SM.calibration("commit", None)
    T, _ = SM.run_year(I, cal, Ks=KS, P_list=(P,), p_sched=P, drop=drop)
    pi = T["π(円/kW-年)"].to_numpy()
    th = EN.annual_cost(y) + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * P
    v = np.minimum.accumulate(pi)
    if v[0] < th:
        k = 0.0
    elif v[-1] >= th:
        k = float(KS[-1])
    else:
        j = int(np.argmax(v < th)); k = KS[j - 1] + (KS[j] - KS[j - 1]) * (v[j - 1] - th) / (v[j - 1] - v[j])
    r100 = T[T["K(万kW)"] == 100.0].iloc[0]
    pi988 = float(np.interp(98.8, KS, pi))
    return {"案": name, "年": y, "π 0万kW": pi[0], "π 98.8万kW": pi988, "しきい値": th, "市場だけで入る量(万kW)": k,
            "98.8万kW で参入": "あり" if pi988 > th else "なし", "μ 100万kW": r100["上乗せ μ(円/kWh)"], "平均価格 100万kW": r100["平均価格（需要加重）"],
            "抑制 100万kW(TWh)": r100["抑制(TWh)"], "0.01円の時間 100万kW(h)": r100["0.01円の時間(h/年)"], "残る火力(MW)": r100["残る火力(MW)"],
            "退出する号機": r100["退出する号機"], "原子力(TWh)": float(I["N"].sum() / (I["N"].shape[0] / 365.25) / 1e6)}


A9 = dict(demand=31_000.0, dc=2_000.0, solar=3_000.0, share=600.0 / 3_000.0, wind=4_000.0)      # 第12回 資料2-2 p.61・64〜65・75〜76
A11 = dict(demand=41_000.0, dc=4_000.0, solar=4_200.0, share=1_300.0 / 4_200.0, wind=7_200.0)
THREE = ("泊3号", "泊1号", "泊2号")
TWO = ("泊3号", "泊1号")
LINK_A = (600.0, 600.0)                                     # 第12回 資料2-1 p.106〜109（運用容量−マージン、両方向60万kW）
JOBS = []
for y in (2035, 2040):
    JOBS += [("原子力 3号＋1号（今の主）", y, {"nuclear": TWO}), ("原子力 3基（2号は2033年度から）", y, {"nuclear": THREE}),
             ("原子力 3号だけ", y, {"nuclear": ("泊3号",)}), ("原子力 なし", y, {"nuclear": ()})]
JOBS += [("第12回 9,000 火力大（北本は今の主）", 2040, {"y2040": A9, "nuclear": THREE}),
         ("第12回 9,000 火力大（北本60/60）", 2040, {"y2040": A9, "nuclear": THREE, "link": LINK_A}),
         ("第12回 9,000 火力小（北本60/60）", 2040, {"y2040": A9, "nuclear": THREE, "link": LINK_A, "drop": OLD45}),
         ("第12回 11,000 火力大（北本60/60）", 2040, {"y2040": A11, "nuclear": THREE, "link": LINK_A}),
         ("第12回 11,000 火力小（北本60/60）", 2040, {"y2040": A11, "nuclear": THREE, "link": LINK_A, "drop": OLD45}),
         ("第12回 9,000 火力大・原子力は今の主（北本60/60）", 2040, {"y2040": A9, "nuclear": TWO, "link": LINK_A}),
         ("第12回 11,000 火力大・原子力は今の主（北本60/60）", 2040, {"y2040": A11, "nuclear": TWO, "link": LINK_A})]

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=7) as ex:
        R = pd.DataFrame(list(ex.map(job, JOBS)))
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    R.to_csv(os.path.join(ROOT, "data", "processed", "simple_decision_sensitivity.csv"), index=False, encoding="utf-8-sig")
    print(R.round(2).to_string(index=False))
