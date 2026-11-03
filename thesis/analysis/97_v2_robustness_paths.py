#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの頑健性（付録C、2026-11-03）: 基準の上で1つだけ動かした需給・価格の項目を、3つの払い方で経路まで解く（容量価格14,972円）。
計算の中身は簡素版のモデルの実行（_job と同じ SM.run_year）と同じ。速さのため、すべての項目の年・場合を1つのプロセスの池でまとめて解く
（項目ごとに順に解くと、較正・退出の計算と最後の数件の間にコアが空く）。量の格子は KMAX（既定500万kW）まで。
結果の年ごとの表を項目ごとに data/processed/robust/<名前>/ に書き、参入の経路は簡素版のモデルの ENTRY_ONLY=1 で作る。
ONLY＝名前（カンマ区切り）で絞れる。WORKERS（既定10）。
"""
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

OUT = os.path.join(ROOT, "data", "processed", "robust")
P = 14_972.0
KMAX = float(os.environ.get("KMAX", "500"))
KS = SM.K_GRID[SM.K_GRID <= KMAX + 1e-9]
MR2 = ("石狩湾新港1", "苫東厚真4")
# (出力の名前, シナリオ, マストラン（None は基準の3台）, 上乗せの形（None は一律）[, 北本の上限の決め方（PR.LINK_RULE）])
ROBUST = [
    ("selfcons_split", "自家消費を分ける", None, None),
    ("link_margin", "主", None, None, "margin_both"),
    ("nuc3", "原子力 3基", None, None),
    ("demand9000", "需要 9,000億kWh ケースの値", None, None),
    ("demandplan", "需要の計画の経路", None, None),
    ("th_plus3", "東北の価格 +3円", None, None),
    ("th_minus3", "東北の価格 −3円", None, None),
    ("fuel12", "燃料費 +20%", None, None),
    ("fuel08", "燃料費 −20%", None, None),
    ("req08", "要件×0.8", None, None),
    ("req12", "要件×1.2", None, None),
    ("mr2", "主", MR2, None),
    ("mr0", "主", (), None),
    ("prop", "主", None, "prop"),
    ("link60", "北本 両方向60万kW", None, None),
    ("noupgrade", "北本の増強なし", None, None),
    ("link333", "連系量 実績の流れ（333MW）", None, None),
    ("link055", "連系量 活用率55%", None, None),
    ("link100", "連系量 運用容量いっぱい", None, None),
    ("retire45", "火力 運開45年で廃止", None, None),
    ("th_comove", "東北の価格が北海道の再エネに連動", None, None),
]
if os.environ.get("ONLY"):
    ROBUST = [r for r in ROBUST if r[0] in os.environ["ONLY"].split(",")]
# 場合のキー: (standard, 運転の赤字の払い方)。キーは簡素版のモデルと同じ
CASES = {"上乗せ": (False, "spot"), "上乗せ_赤字は外": (False, "outside"), "燃料費": (True, "spot")}
_BY = {r[0]: r for r in ROBUST}


def _rule(name):
    """北本の上限の決め方を項目ごとに切り替える（較正の k もその決め方で取り直す）"""
    rule = _BY[name][4] if len(_BY[name]) > 4 else "opcap"
    if PR.LINK_RULE != rule:
        PR.LINK_RULE = rule
        SM.calibration.cache_clear()


def _shape(name, standard):
    return "flat" if standard or _BY[name][3] is None else _BY[name][3]


def _exits(a):
    import warnings
    warnings.filterwarnings("ignore")
    name, losses = a
    _rule(name)
    _, scen, mr, shape = _BY[name][:4]
    sh = shape or "flat"
    before, when = SM.exit_years(SM.calibration("commit", mr), PR.SCENARIOS[scen], PR.YEARS, "commit", mustrun=mr, losses=losses, shape=sh)
    return name, losses, before, when


def _job(a):
    import warnings
    warnings.filterwarnings("ignore")
    name, case, y, drop = a
    _rule(name)
    _, scen, mr, _ = _BY[name][:4]
    standard, losses = CASES[case]
    sc = PR.SCENARIOS[scen]
    from model import merit as MO
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    T, _ = SM.run_year(I, SM.calibration("commit", mr), Ks=KS, P_list=(P,), standard=standard, mode="commit", p_sched=P, drop=drop,
                       mustrun=mr, losses=losses, shape=_shape(name, standard))
    T.insert(0, "前の年までに退出", "・".join(drop))
    T.insert(0, "年", y)
    T.insert(0, "場合", case)
    T.insert(0, "シナリオ", scen)
    return name, T


def main():
    t0 = time.time()
    workers = int(os.environ.get("WORKERS", "10"))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        # 1. 退出の年（燃料費も上乗せありの退出の経路を使う。基準と同じ）
        ex_jobs = [(r[0], losses) for r in ROBUST for losses in ("spot", "outside")]
        drops, ex_rows = {}, []
        for name, losses, before, when in ex.map(_exits, ex_jobs, chunksize=1):
            drops[(name, losses)] = before
            ex_rows += [{"頑健性": name, "運転の赤字の払い方": losses, "号機": n, "退出の年": y} for n, y in when.items()]
        print(f"退出の年 {time.time() - t0:.0f}秒", pd.DataFrame(ex_rows).to_string() if ex_rows else "（退出なし）", flush=True)
        # 2. 年・場合ごとの π(K)（重い後ろの年から）
        jobs = [(r[0], c, y, drops[(r[0], CASES[c][1] if not CASES[c][0] else "spot")][y]) for r in ROBUST for c in CASES for y in PR.YEARS]
        jobs.sort(key=lambda j: (-j[2], j[1] != "上乗せ"))
        print(f"計算の数 {len(jobs)}（量の格子 {len(KS)}点、{KS[-1]:.0f}万kW まで）", flush=True)
        res = {}
        for i, (name, T) in enumerate(ex.map(_job, jobs, chunksize=1)):
            res.setdefault(name, []).append(T)
            if (i + 1) % 25 == 0:
                print(f"  {i + 1}/{len(jobs)} {time.time() - t0:.0f}秒", flush=True)
    # 3. 項目ごとに書き出し、参入の経路を作る
    for item in ROBUST:
        name, scen, mr, shape = item[:4]
        d = os.path.join(OUT, name)
        os.makedirs(d, exist_ok=True)
        suffix = "" if scen == "主" else f"_{scen}"
        Y = pd.concat(res[name], ignore_index=True).sort_values(["場合", "年", "K(万kW)"])
        Y.to_csv(os.path.join(d, f"simple_years{suffix}.csv"), index=False, encoding="utf-8-sig")
        E = pd.DataFrame([r for r in ex_rows if r["頑健性"] == name], columns=["頑健性", "運転の赤字の払い方", "号機", "退出の年"])
        E.to_csv(os.path.join(d, f"simple_exit_years{suffix}.csv"), index=False, encoding="utf-8-sig")
        env = dict(os.environ, SCEN=scen, CASES=",".join(CASES), P_GRID=f"{P:.0f}", EQM_PROC=d, ENTRY_ONLY="1")
        env.pop("ONLY", None)
        if mr is not None:
            env["MR"] = "2" if mr else "0"
        if shape:
            env["SHAPE"] = shape
        if len(item) > 4:
            env["LINK_RULE"] = item[4]
        r = subprocess.run([sys.executable, os.path.join(HERE, "80_simple_model.py")], env=env, capture_output=True, text=True)
        open(os.path.join(d, "entry.log"), "w", encoding="utf-8").write(r.stdout + r.stderr)
        print(f"{name}（{scen}）: 参入の経路 {'済' if r.returncode == 0 else '失敗'}", flush=True)
    print(f"完了 {time.time() - t0:.0f}秒", flush=True)


if __name__ == "__main__":
    main()
