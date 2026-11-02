#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの再計算（notes/38 §1.3・§1.4、2026-11-03）: シナリオごとの表6.3 に当たる表、経路の指標、電源構成

入力: 80 の出力（simple_entry{接尾辞}.csv・simple_pik{接尾辞}.npz・simple_years{接尾辞}.csv）。主の接尾辞は空、ほかは "_シナリオ名"
1. 表6.3 に当たる表（3つの払い方、容量価格14,972円）: 年ごとの LTDA などの契約なしで採算が合う量 K*_y（その年の π と κ×容量価格で
   年あたりの費用を賄える量、EN.path_myopic と同じ）、100万kW での π、参入のしきい値、98.8万kW での余り、経路の量、98.8万kW を超える年
2. 経路の指標（3つの払い方、2030・2035・2040年）: 経路の量そのもので解き直した μ・平均価格（需要加重）・0.01円の時間・出力抑制率
   （抑制÷制御前の太陽光・風力）
3. 電源構成（スポットで回収の経路、2030・2035・2040年、notes/38 §1.4 の規則）: 発電電力量ベース。揚水は除く、自家消費の太陽光は発電量に戻す
   （設備×太陽光の CF×0.85、需要の側と同じ）、蓄電池の充電はすべて再エネからとし往復の損失（充電−放電）を再エネと合計の両方から引く、
   その他の火力（石油・自家発など）とアンモニア混焼は火力。注: 北本で送る分をすべて再エネと置いた消費ベースの下限側の比率
4. 年ごとの全出力から本文で使う格子の点（0〜300万kW）を抜き出した表
5. ONLY_GRID_CHECK=1: 付録 B.3 の確かめ（経路の量で解き直した π・μ と最も近い格子の点の差、v2_grid_check.csv）
出力: data/processed/v2_table63.csv・v2_path_metrics.csv・v2_mix.csv・v2_years_extract.csv
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
from model import params as PR, data as DT, merit as MO, simple as SM, entry as EN

PROC = os.path.join(ROOT, "data", "processed")
BASE_P = 14_972.0
CASES = {"上乗せ": "スポットで回収（主）", "上乗せ_赤字は外": "赤字だけ市場外", "燃料費": "すべて市場外"}
SCENS = os.environ.get("SCENS", "主,エネ基の下限,エネ基の上限,旧の主").split(",")
WORKERS = int(os.environ.get("WORKERS", "3"))
STOCK = 98.8                                                   # 既設＋LTDA（万kW、2031年以降）


def suffix(scen):
    return "" if scen == "主" else f"_{scen}"


def threshold(y, P=BASE_P):
    """参入のしきい値: その年に運転を始める蓄電池の年あたりの建設費＋運転維持費＋託送等−κ×容量価格"""
    return EN.annual_cost(y) + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * PR.cap_price(y, P)


def k_star(Ks, pi, th):
    v = np.minimum.accumulate(pi)
    if v[0] < th:
        return 0.0
    if v[-1] >= th:
        return float(Ks[-1])
    j = int(np.argmax(v < th))
    return float(Ks[j - 1] + (Ks[j] - Ks[j - 1]) * (v[j - 1] - th) / (v[j - 1] - v[j]))


def table63(scen):
    sx = suffix(scen)
    Z = dict(np.load(os.path.join(PROC, f"simple_pik{sx}.npz")))
    Ks = Z.pop("K")
    E = pd.read_csv(os.path.join(PROC, f"simple_entry{sx}.csv"))
    rows = []
    for case, name in CASES.items():
        e = E[(E["場合"] == case) & (E["容量価格(円/kW)"] == BASE_P)]
        if e.empty:
            continue
        e = e.iloc[0]
        over = [y for y in range(2026, 2046) if e[f"量 {y}"] > STOCK + 0.05]
        for y in PR.YEARS:
            pi = Z[f"{case}|{BASE_P:.0f}|{y}"]
            th = threshold(y)
            rows.append({"シナリオ": scen, "場合": name, "年": y, "採算が合う量 K*(万kW)": k_star(Ks, pi, th),
                         "経路の量(万kW)": float(e[f"量 {y}"]), "100万kW での π": float(np.interp(100.0, Ks, pi)),
                         "参入のしきい値": th, "98.8万kW での π": float(np.interp(STOCK, Ks, pi)),
                         "98.8万kW での余り": float(np.interp(STOCK, Ks, pi)) - th, "π 0万kW": float(pi[0]),
                         "98.8万kW を超える最初の年": over[0] if over else np.nan, "量 2045": float(e["量 2045"])})
    return pd.DataFrame(rows)


CASE_ARGS = {"上乗せ": (False, "spot"), "上乗せ_赤字は外": (False, "outside"), "燃料費": (True, "spot")}   # (standard, losses)、80 と同じ


def _path_job(a):
    """経路の量 k そのもので、その年の需給・上乗せ・蓄電池の運用を解く（格子の点ではなく）"""
    warnings.filterwarnings("ignore")
    scen, case, y, k, drop = a
    standard, losses = CASE_ARGS[case]
    sc = PR.SCENARIOS[scen]
    sy = PR.scenario_year(y, sc)
    I = MO.inputs_future(sy, sc)
    T, _ = SM.run_year(I, SM.calibration("commit", None), Ks=[k], P_list=(BASE_P,), standard=standard, p_sched=BASE_P, drop=drop,
                       losses=losses)
    r = T.iloc[0]
    vre = float((I["S"] + I["W"]).sum() / (I["D"].shape[0] / 365.25) / 1e6)
    return {"シナリオ": scen, "場合": CASES[case], "年": y, "経路の量(万kW)": k, "上乗せ μ(円/kWh)": r["上乗せ μ(円/kWh)"],
            "上乗せが上限": bool(r["上乗せが上限"]),
            "平均価格（需要加重、円/kWh）": r["平均価格（需要加重）"], "0.01円の時間(h/年)": r["0.01円の時間(h/年)"],
            "抑制(TWh)": r["抑制(TWh)"], "制御前の太陽光・風力(TWh)": vre, "出力抑制率(%)": r["抑制(TWh)"] / vre * 100,
            "日の値幅(円/kWh)": r["日の値幅 高い4時間−安い4時間(円/kWh)"], "π(円/kW-年)": r["π(円/kW-年)"],
            "要件(億円/年)": r["要件(億円/年)"], "粗利(億円/年)": r["粗利(億円/年)"],
            "マストランの赤字（上乗せなしの価格、億円/年）": r["マストランの運転の赤字 α＝1(億円/年)"],
            "市場の外の補填(億円/年)": r["市場の外の補填(億円/年)"], "北本 送電(TWh)": r["北本 送電(TWh)"], "北本 受電(TWh)": r["北本 受電(TWh)"],
            "退出する号機": r["退出する号機"],
            "太陽光 系統(万kW)": sy["solar_mw"] / 10, "太陽光 自家消費(万kW)": sy["selfcons_mw"] / 10, "風力(万kW)": sy["wind_mw"] / 10}


def path_metrics(scen, T63):
    sc = PR.SCENARIOS[scen]
    cal = SM.calibration("commit")
    drops = {}
    for case, (standard, losses) in CASE_ARGS.items():
        if losses not in drops:
            drops[losses] = SM.exit_years(cal, sc, PR.YEARS, "commit", losses=losses)[0]
    jobs = []
    for case, name in CASES.items():
        for y in (2030, 2035, 2040):
            t = T63[(T63["場合"] == name) & (T63["年"] == y)]
            if t.empty:
                continue
            jobs.append((scen, case, y, float(t["経路の量(万kW)"].iloc[0]), drops[CASE_ARGS[case][1]][y]))
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        return pd.DataFrame(list(ex.map(_path_job, jobs, chunksize=1)))


def mix(scen, T63):
    """スポットで回収の経路の量で需給を解き、発電電力量ベースの電源構成を出す"""
    sc = PR.SCENARIOS[scen]
    cal = SM.calibration("commit")
    before, _ = SM.exit_years(cal, sc, PR.YEARS, "commit")
    cfS = DT.weather()["cf_S"]
    rows = []
    for y in (2030, 2035, 2040):
        K = float(T63[(T63["場合"] == CASES["上乗せ"]) & (T63["年"] == y)]["経路の量(万kW)"].iloc[0])
        sy = PR.scenario_year(y, sc)
        I = MO.inputs_future(sy, sc)
        T, _, st = SM.run_year(I, cal, Ks=[K], P_list=(BASE_P,), drop=before[y], return_state=True)
        R, chg, dis = st["R"], st["chg"], st["dis"]
        yrs = I["D"].shape[0] / 365.25
        tw = lambda x: float(np.asarray(x).sum() / yrs / 1e6)
        fS = np.maximum(I["S"] - I["U"], 0.0)
        share = np.where(fS + I["W"] > 0, fS / np.maximum(fS + I["W"], 1e-9), 0.0)
        cS = R["curt"] * share
        solar = tw(I["S"] - cS)
        selfc = tw(sy["selfcons_mw"] * cfS * 0.85)
        wind = tw(I["W"] - (R["curt"] - cS))
        hydro = tw(I["Hy"])                                    # 揚水は除く
        geo, bio = tw(I["G"]), tw(I["Bm"])
        nuc = tw(I["N"])
        thermal = tw(R["g"].sum(2)) + tw(R["other_out"])       # 号機の火力＋その他の火力（石油・自家発など）。アンモニア混焼も火力
        loss = tw(chg) - tw(dis)                               # 蓄電池の往復の損失（充電はすべて再エネから）
        exp, imp = tw(np.maximum(R["X"], 0)), tw(np.maximum(-R["X"], 0))
        re = solar + selfc + wind + hydro + geo + bio - loss
        tot = re + nuc + thermal
        rows.append({"シナリオ": scen, "年": y, "蓄電池(万kW)": K, "合計の発電量(TWh)": tot,
                     "再エネ比率(%)": re / tot * 100, "太陽光(%)": (solar + selfc) / tot * 100, "うち自家消費(%)": selfc / tot * 100,
                     "風力(%)": wind / tot * 100, "水力・地熱・バイオマス(%)": (hydro + geo + bio) / tot * 100,
                     "原子力(%)": nuc / tot * 100, "火力(%)": thermal / tot * 100, "蓄電池の損失(TWh)": loss,
                     "北本 送電(TWh)": exp, "北本 受電(TWh)": imp,
                     "消費ベースの再エネ比率 下限側(%)": (re - exp) / (tot - exp + imp) * 100,
                     "太陽光(TWh)": solar, "自家消費の太陽光(TWh)": selfc, "風力(TWh)": wind, "水力(TWh)": hydro, "地熱(TWh)": geo, "バイオマス(TWh)": bio,
                     "原子力(TWh)": nuc, "火力(TWh)": thermal, "抑制(TWh)": tw(R["curt"])})
    return pd.DataFrame(rows)


EXTRACT_K = (0.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0, 250.0, 300.0)
EXTRACT_COLS = ["場合", "年", "K(万kW)", "π(円/kW-年)", "上乗せ μ(円/kWh)", "上乗せが上限", "平均価格（需要加重）", "0.01円の時間(h/年)",
                "日の値幅 高い4時間−安い4時間(円/kWh)", "高い4時間の平均(円/kWh)", "安い4時間の平均(円/kWh)", "抑制(TWh)", "火力の発電量(TWh)",
                "北本 送電(TWh)", "北本 受電(TWh)", "マストランの運転の赤字 α＝1(億円/年)", "市場の外の補填(億円/年)", "要件(億円/年)", "粗利(億円/年)",
                "退出する号機"]


def years_extract(scen):
    """80 の年ごとの全出力（大きいのでコミットしない）から、本文で使う格子の点だけを抜き出す（容量価格14,972円）"""
    Y = pd.read_csv(os.path.join(PROC, f"simple_years{suffix(scen)}.csv"), usecols=EXTRACT_COLS + ["容量価格(円/kW)"])
    Y = Y[(Y["容量価格(円/kW)"] == BASE_P) & (Y["K(万kW)"].isin(EXTRACT_K))].drop(columns="容量価格(円/kW)")
    Y["場合"] = Y["場合"].map(CASES).fillna(Y["場合"])
    Y.insert(0, "シナリオ", scen)
    return Y


def grid_check(scen):
    """付録 B.3: 経路の量そのもので解いた π・μ と、最も近い格子の点の値の差（スポットで回収、2030〜40年）"""
    T63 = table63(scen)
    Y = pd.read_csv(os.path.join(PROC, f"simple_years{suffix(scen)}.csv"), usecols=["場合", "年", "K(万kW)", "容量価格(円/kW)", "上乗せ μ(円/kWh)", "π(円/kW-年)"])
    Y = Y[(Y["場合"] == "上乗せ") & (Y["容量価格(円/kW)"] == BASE_P)]
    sc = PR.SCENARIOS[scen]
    drops = SM.exit_years(SM.calibration("commit"), sc, PR.YEARS, "commit")[0]
    years = list(range(2030, 2041))
    ks = {y: float(T63[(T63["場合"] == CASES["上乗せ"]) & (T63["年"] == y)]["経路の量(万kW)"].iloc[0]) for y in years}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        ex_rows = list(ex.map(_path_job, [(scen, "上乗せ", y, ks[y], drops[y]) for y in years], chunksize=1))
    rows = []
    for y, r in zip(years, ex_rows):
        g = Y[Y["年"] == y].set_index("K(万kW)")
        kk = g.index[np.argmin(np.abs(g.index.to_numpy() - ks[y]))]
        rows.append({"シナリオ": scen, "年": y, "経路の量(万kW)": ks[y], "最も近い格子の点(万kW)": kk,
                     "π 解き直し": r["π(円/kW-年)"], "π 格子の点": float(g.loc[kk, "π(円/kW-年)"]),
                     "μ 解き直し": r["上乗せ μ(円/kWh)"], "μ 格子の点": float(g.loc[kk, "上乗せ μ(円/kWh)"])})
    D = pd.DataFrame(rows)
    D["π の差"] = D["π 格子の点"] - D["π 解き直し"]
    D["μ の差"] = D["μ 格子の点"] - D["μ 解き直し"]
    return D


def main():
    warnings.filterwarnings("ignore")
    if os.environ.get("ONLY_GRID_CHECK") == "1":                 # 付録 B.3 の確かめ（重いので別に回す）
        D = pd.concat([grid_check(s) for s in SCENS], ignore_index=True)
        D.to_csv(os.path.join(PROC, "v2_grid_check.csv"), index=False, encoding="utf-8-sig")
        print(D.round(3).to_string(index=False))
        return
    if os.environ.get("ONLY_EXTRACT") == "1":
        E = pd.concat([years_extract(s) for s in SCENS], ignore_index=True)
        E.to_csv(os.path.join(PROC, f"v2_years_extract{os.environ.get('OUT_SUFFIX', '')}.csv"), index=False, encoding="utf-8-sig")
        return
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    T, M, X = [], [], []
    for scen in SCENS:
        t = table63(scen)
        T.append(t)
        M.append(path_metrics(scen, t))
        if os.environ.get("NO_MIX") != "1":
            X.append(mix(scen, t))
        print(scen, "済", flush=True)
    T, M = pd.concat(T, ignore_index=True), pd.concat(M, ignore_index=True)
    out = os.environ.get("OUT_SUFFIX", "")
    pd.concat([years_extract(s) for s in SCENS], ignore_index=True).to_csv(os.path.join(PROC, f"v2_years_extract{out}.csv"), index=False,
                                                                          encoding="utf-8-sig")
    T.to_csv(os.path.join(PROC, f"v2_table63{out}.csv"), index=False, encoding="utf-8-sig")
    M.to_csv(os.path.join(PROC, f"v2_path_metrics{out}.csv"), index=False, encoding="utf-8-sig")
    show = T[T["年"].isin([2030, 2031, 2033, 2035, 2037, 2039, 2040])]
    print(show.round(1).to_string(index=False))
    print(M.round(2).to_string(index=False))
    if X:
        X = pd.concat(X, ignore_index=True)
        X.to_csv(os.path.join(PROC, f"v2_mix{out}.csv"), index=False, encoding="utf-8-sig")
        print(X.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
