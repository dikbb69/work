#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの基準の変更（2026-11-03: 太陽光の自家消費を分けない、火力の起動の判断を時間ごとに、伊達1・2号を FY2023 に）に合わせた再計算
簡素版のモデルの実行（_job と同じ SM.run_year、量の格子・容量価格の格子も同じ）を、速さのため部分に分けて解き、最後につなぐ。
- 部分（PART＝名前）: SCENS のシナリオについて、P_ONLY の容量価格（スポットで回収・運転赤字だけ市場外）の YEAR_MIN〜2040年と、
  INCLUDE_FUEL＝1 ならすべて市場外の FUEL_YEAR_MIN〜2040年を解き、data/processed/rebuild/ に書く。
- つなぐ（MERGE＝1）: 部分の行と、次の2つの使い回しをつなぎ、simple_years*.csv に書いて参入の経路などを ENTRY_ONLY＝1 で作る。
  (1) すべて市場外は上乗せがなく較正の比 k によらないので、FUEL_YEAR_MIN より前の年は保存した行を使う（入力は2035年まで変わらない）。
  (2) 2029年度までの容量価格は実績の値で、格子の容量価格によらない（PR.cap_price）。2026〜2029年は容量価格14,972円の行を、ほかの容量価格に写す。
退出の年はどの部分でも全期間を解き直す。SCENS（カンマ区切り）、WORKERS（既定10）。
"""
import glob
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, simple as SM

PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(PROC, "rebuild")
SCENS = os.environ.get("SCENS", "主,エネ基の下限,エネ基の上限").split(",")
P_GRID = [0.0, 5_000.0, 10_000.0, 12_500.0, 14_972.0, 16_000.0, 17_000.0, 18_000.0, 19_000.0, 20_000.0, 20_911.0, 25_000.0, 30_000.0]
BASE_P = 14_972.0
FIXED_UNTIL = 2029                                              # この年度までは容量価格が実績の値（格子の容量価格によらない）
FUEL_YEAR_MIN = int(os.environ.get("FUEL_YEAR_MIN", "2036"))
CASES = {"上乗せ": (False, "spot"), "上乗せ_赤字は外": (False, "outside"), "燃料費": (True, "spot")}


def suffix(scen):
    return "" if scen == "主" else f"_{scen}"


def _exits(a):
    import warnings
    warnings.filterwarnings("ignore")
    scen, losses = a
    before, when = SM.exit_years(SM.calibration("commit", None), PR.SCENARIOS[scen], PR.YEARS, "commit", losses=losses)
    return scen, losses, before, when


def _job(a):
    import warnings
    warnings.filterwarnings("ignore")
    from model import merit as MO
    scen, case, P, y, drop = a
    standard, losses = CASES[case]
    sc = PR.SCENARIOS[scen]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    T, _ = SM.run_year(I, SM.calibration("commit", None), Ks=SM.K_GRID, P_list=(P,), standard=standard, mode="commit", p_sched=P,
                       drop=drop, losses=losses)
    T.insert(0, "前の年までに退出", "・".join(drop))
    T.insert(0, "年", y)
    T.insert(0, "場合", case)
    T.insert(0, "シナリオ", scen)
    return scen, T


def part(name):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    p_only = [float(x) for x in os.environ["P_ONLY"].split(",")] if os.environ.get("P_ONLY") else P_GRID
    y_min = int(os.environ.get("YEAR_MIN", "2026"))
    fuel = os.environ.get("INCLUDE_FUEL") == "1"
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "10"))) as ex:
        drops, ex_rows = {}, []
        for scen, losses, before, when in ex.map(_exits, [(s, l) for s in SCENS for l in ("spot", "outside")], chunksize=1):
            drops[(scen, losses)] = before
            ex_rows += [{"シナリオ": scen, "運転の赤字の払い方": losses, "号機": n, "退出の年": y} for n, y in when.items()]
        print(f"[{name}] 退出の年 {time.time() - t0:.0f}秒", pd.DataFrame(ex_rows).to_string() if ex_rows else "（退出なし）", flush=True)
        jobs = [(s, c, P, y, drops[(s, CASES[c][1])][y]) for s in SCENS for c in ("上乗せ", "上乗せ_赤字は外") for P in p_only
                for y in PR.YEARS if y >= y_min and not (y <= FIXED_UNTIL and P != BASE_P)]
        if fuel:
            jobs += [(s, "燃料費", BASE_P, y, drops[(s, "spot")][y]) for s in SCENS for y in PR.YEARS if y >= FUEL_YEAR_MIN]
        jobs.sort(key=lambda j: (-j[3], j[1] != "上乗せ"))
        print(f"[{name}] 計算の数 {len(jobs)}", flush=True)
        res = {}
        for i, (scen, T) in enumerate(ex.map(_job, jobs, chunksize=1)):
            res.setdefault(scen, []).append(T)
            if (i + 1) % 25 == 0:
                print(f"  [{name}] {i + 1}/{len(jobs)} {time.time() - t0:.0f}秒", flush=True)
    for scen in SCENS:
        if scen in res:
            pd.concat(res[scen], ignore_index=True).to_csv(os.path.join(OUT, f"part_{name}{suffix(scen)}.csv"), index=False, encoding="utf-8-sig")
        pd.DataFrame([r for r in ex_rows if r["シナリオ"] == scen], columns=["シナリオ", "運転の赤字の払い方", "号機", "退出の年"]).to_csv(
            os.path.join(OUT, f"exits_{name}{suffix(scen)}.csv"), index=False, encoding="utf-8-sig")
    print(f"[{name}] 完了 {time.time() - t0:.0f}秒", flush=True)


def merge():
    for scen in SCENS:
        sfx = suffix(scen)
        parts = [pd.read_csv(f, encoding="utf-8-sig", low_memory=False) for f in sorted(glob.glob(os.path.join(OUT, f"part_*{sfx}.csv")))
                 if (sfx == "" and not os.path.basename(f).split("part_")[1].split(".")[0].count("_エネ基")) or (sfx and f.endswith(f"{sfx}.csv"))]
        new = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["場合", "容量価格(円/kW)", "年", "K(万kW)"], keep="last")
        old = pd.read_csv(os.path.join(PROC, f"simple_years{sfx}.csv"), encoding="utf-8-sig", low_memory=False)
        fuel_old = old[(old["場合"] == "燃料費") & (old["年"] < FUEL_YEAR_MIN)]                       # (1) k によらない
        fuel_new = new[(new["場合"] == "燃料費")]
        assert set(fuel_new["年"]) | set(fuel_old["年"]) == set(PR.YEARS), f"{scen}: すべて市場外の年が足りない"
        early = new[(new["場合"] != "燃料費") & (new["年"] <= FIXED_UNTIL) & (new["容量価格(円/kW)"] == BASE_P)]   # (2) 写す
        grid = sorted(set(new[new["場合"] != "燃料費"]["容量価格(円/kW)"]))
        copies = [early.assign(**{"容量価格(円/kW)": P}) for P in grid if P != BASE_P]
        Y = pd.concat([fuel_old, new] + copies, ignore_index=True)
        Y = Y.drop_duplicates(subset=["場合", "容量価格(円/kW)", "年", "K(万kW)"], keep="first").sort_values(["場合", "容量価格(円/kW)", "年", "K(万kW)"])
        for c in ("上乗せ", "上乗せ_赤字は外"):                   # どの容量価格もすべての年がそろっているか
            g = Y[Y["場合"] == c]
            for P in grid:
                miss = set(PR.YEARS) - set(g[g["容量価格(円/kW)"] == P]["年"])
                assert not miss, f"{scen} {c} {P}: 年 {sorted(miss)} がない"
        Y.to_csv(os.path.join(PROC, f"simple_years{sfx}.csv"), index=False, encoding="utf-8-sig")
        ex = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in sorted(glob.glob(os.path.join(OUT, f"exits_*{sfx}.csv")))
                        if (sfx == "" and "_エネ基" not in os.path.basename(f)) or (sfx and f.endswith(f"{sfx}.csv"))], ignore_index=True)
        # 簡素版のモデルと同じ形（シナリオ・場合・号機・退出の年。燃料費は上乗せと同じ退出の経路なので行を持たない）
        ex["場合"] = ex["運転の赤字の払い方"].map({"spot": "上乗せ", "outside": "上乗せ_赤字は外"})
        ex = ex[["シナリオ", "場合", "号機", "退出の年"]].drop_duplicates()
        ex.to_csv(os.path.join(PROC, f"simple_exit_years{sfx}.csv"), index=False, encoding="utf-8-sig")
        env = dict(os.environ, SCEN=scen, CASES=",".join(CASES), ENTRY_ONLY="1")
        env.pop("SCENS", None)
        if len(grid) < len(P_GRID):
            env["P_GRID"] = ",".join(f"{p:.0f}" for p in grid)
        r = subprocess.run([sys.executable, os.path.join(HERE, "80_simple_model.py")], env=env, capture_output=True, text=True)
        print(f"{scen}: 容量価格 {len(grid)}点、参入の経路 {'済' if r.returncode == 0 else '失敗'}", flush=True)
        print(r.stdout[-2500:] if r.returncode == 0 else r.stderr[-3000:], flush=True)


if __name__ == "__main__":
    if os.environ.get("MERGE") == "1":
        merge()
    else:
        part(os.environ.get("PART", "all"))
