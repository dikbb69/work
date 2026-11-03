#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの再計算（notes/38 §3・§2.3・§5、2026-11-03）: 新しい主の2040年の感応度

3つの払い方（スポットで回収（主）・赤字だけ市場外・すべて市場外）で、2040年の π（100万kW）、採算が合う量（その年の π がしきい値まで下がる量）、
μ・平均価格（需要加重、100万kW）を、次の場合で比べる（容量価格14,972円、ほかは新しい主のまま）。
- 基準（新しい主）
- §3 (a) 東北の価格の昼（9〜16時、時刻 9〜15 の7時間）を20%・40%下げる（0.01円の時間はそのまま）。本州で太陽光が増えた場合の近似
- §3 (b) 東北の価格に μ を足さない（全国の火力は上乗せしないと置く。北海道の価格が東北の価格に等しい時間は上乗せなし、北海道が安い側は
  上乗せしても東北の価格で頭打ち）。μ の置き方を2つ: (b1) 要件を満たすように解き直す、(b2) 主の μ（同じ払い方・100万kW の値）に固定し、届かない分は回収しない
- §2.3 受電の上限（北海道向の運用容量）×0.6（k は同じ倍率で較正し直した値 0.813、data/processed/v2_fit_import_cap.csv）
- 自家消費の規則の確かめ: 自家消費を FY2025 からの増分の31% とする（2040年の太陽光の合計は同じ）
- §5 割引率8%（マーチャントの資本コストの目安）: π は変わらず、しきい値だけが変わる
- §1.2・§5 エネ基の上限、エネ基の上限＋本州との新しい海底直流送電（+200万kW を両方向に。2036年度から、相手の価格は東北の価格で近似）
退出はそれぞれのシナリオの経路（SM.exit_years）。量の格子は表6.4 と同じ考え方で 0〜500万kW（上限のケースは800万kW まで）。
出力: data/processed/v2_sensitivity_2040.csv
"""
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, merit as MO, simple as SM, entry as EN

PROC = os.path.join(ROOT, "data", "processed")
WORKERS = int(os.environ.get("WORKERS", "9"))
P = 14_972.0
Y = 2040
KS = [0.0, 25.0, 50.0, 75.0, 95.0, 100.0, 125.0, 150.0, 175.0, 200.0, 250.0, 300.0, 400.0, 500.0]
CASES = [("スポットで回収（主）", False, "spot"), ("赤字だけ市場外", False, "outside"), ("すべて市場外", True, "spot")]
DAY = slice(9, 16)                                              # 9〜16時（時刻 9〜15）
VARIANTS = ["基準", "東北の昼 −20%", "東北の昼 −40%", "東北の価格に μ を足さない（μ を解き直す）",
            "東北の価格に μ を足さない（μ は主の値に固定）", "受電の上限×0.6（k を較正し直す）",
            "シナリオ: 自家消費を分ける", "シナリオ: エネ基の上限", "シナリオ: エネ基の上限＋海底直流"]
KS_WIDE = KS + [600.0, 700.0, 800.0]
_cp = pd.read_csv(os.path.join(PROC, "v2_fit_import_cap.csv"))                 # 受電の上限×0.6 で較正し直した k（当てはまりの補強の出力）
K_IMPORT06 = float(_cp[_cp["受電の上限の倍率"] == 0.6]["k"].iloc[0])


def threshold(wacc=None):
    if wacc is None:
        return EN.annual_cost(Y) + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * P
    w0 = PR.WACC
    try:
        EN.PR.WACC = wacc
        return EN.annual_cost(Y) + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * P
    finally:
        EN.PR.WACC = w0


def k_star(pi, th, ks=None):
    ks = KS if ks is None else ks
    v = np.minimum.accumulate(pi)
    if v[0] < th:
        return 0.0
    if v[-1] >= th:
        return float(ks[-1])
    j = int(np.argmax(v < th))
    return float(ks[j - 1] + (ks[j] - ks[j - 1]) * (v[j - 1] - th) / (v[j - 1] - v[j]))


def scen_of(var):
    if var.startswith("シナリオ: "):
        return var.split(": ", 1)[1]
    return "主"


def job(a):
    warnings.filterwarnings("ignore")
    var, c, drop = a
    case, standard, losses = CASES[c]
    sc = PR.SCENARIOS[scen_of(var)]
    ks = KS_WIDE if var.startswith("シナリオ: ") else KS
    I = MO.inputs_future(PR.scenario_year(Y, sc), sc)
    cal = SM.calibration("commit", None)
    if var.startswith("東北の昼"):
        x = 0.2 if "20" in var else 0.4
        pT = I["pT"].copy()
        d = pT[:, DAY]
        pT[:, DAY] = np.where(d <= PR.FLOOR + 0.001, d, d * (1 - x))
        I["pT"] = pT
    if var.startswith("東北の価格に μ を足さない"):
        I["mu_tohoku"] = False
        if "固定" in var and not standard:                      # 主（同じ払い方）の100万kW の μ
            T0, _ = SM.run_year(dict(I, mu_tohoku=True), cal, Ks=[100.0], P_list=(P,), standard=standard, p_sched=P, drop=drop, losses=losses)
            I["mu_fixed"] = float(T0.iloc[0]["上乗せ μ(円/kWh)"])
    if var.startswith("受電の上限"):
        E, M = I["link"]
        I["link"] = (E, M * 0.6)
        cal = {**cal, "k": K_IMPORT06}
    T, _ = SM.run_year(I, cal, Ks=ks, P_list=(P,), standard=standard, p_sched=P, drop=drop, losses=losses)
    pi = T["π(円/kW-年)"].to_numpy()
    r100 = T[T["K(万kW)"] == 100.0].iloc[0]
    r0 = T[T["K(万kW)"] == 0.0].iloc[0]
    return {"感応度": var, "場合": case, "π 0万kW": pi[0], "π 100万kW": r100["π(円/kW-年)"], "μ 100万kW": r100["上乗せ μ(円/kWh)"],
            "平均価格 100万kW": r100["平均価格（需要加重）"], "μ 0万kW": r0["上乗せ μ(円/kWh)"], "平均価格 0万kW": r0["平均価格（需要加重）"],
            "日の値幅 100万kW": r100["日の値幅 高い4時間−安い4時間(円/kWh)"], "0.01円の時間 100万kW": r100["0.01円の時間(h/年)"],
            "しきい値": threshold(), "採算が合う量(万kW)": k_star(pi, threshold(), ks),
            "割引率8% のしきい値": threshold(0.08), "割引率8% の採算が合う量(万kW)": k_star(pi, threshold(0.08), ks),
            "上乗せが上限 0万kW": bool(r0["上乗せが上限"]), "上乗せが上限 100万kW": bool(r100["上乗せが上限"]),
            "要件 100万kW(億円/年)": r100["要件(億円/年)"], "粗利 100万kW(億円/年)": r100["粗利(億円/年)"],
            "市場の外の補填 100万kW(億円/年)": r100["市場の外の補填(億円/年)"],
            "抑制 100万kW(TWh)": r100["抑制(TWh)"], "北本 送電 100万kW(TWh)": r100["北本 送電(TWh)"], "退出する号機 100万kW": r100["退出する号機"],
            **{f"π {k:g}万kW": v for k, v in zip(ks, pi)}}


def main():
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    drops = {}
    for s in sorted({scen_of(v) for v in VARIANTS}):
        before, when = SM.exit_years(SM.calibration("commit", None), PR.SCENARIOS[s], PR.YEARS, "commit")
        drops[s] = before[Y]
        print(s, "2040年より前に退出", before[Y], when, flush=True)
    jobs = [(v, c, drops[scen_of(v)]) for v in VARIANTS for c in range(len(CASES))]
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    R.to_csv(os.path.join(PROC, "v2_sensitivity_2040.csv"), index=False, encoding="utf-8-sig")
    cols = ["感応度", "場合", "π 100万kW", "採算が合う量(万kW)", "μ 100万kW", "平均価格 100万kW", "日の値幅 100万kW", "0.01円の時間 100万kW",
            "しきい値", "割引率8% のしきい値", "割引率8% の採算が合う量(万kW)"]
    print(R[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
