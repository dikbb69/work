# -*- coding: utf-8 -*-
"""付録B.1 第2の確かめ（基準シナリオ、2026-11-03 に基準の前提で解き直し）: 起動と上乗せを固定し、蓄電池を少し（5MW）足したときの式4.7 の目的関数の減り方から測る1kW の価値と、
価格から測る値差の粗利（0.825 と690円を当てる前）を比べる"""
import sys, warnings
warnings.filterwarnings("ignore")
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
import numpy as np
from model import params as PR, merit as MO, simple as SM, balance as B, battery as BT, price as PZ
sc = PR.SCENARIOS["主"]
cal = SM.calibration("commit", None)


def area(q0, E_, V, x):
    lo, hi = E_[..., :-1], E_[..., 1:]
    a, b = np.minimum(q0, q0 + x)[..., None], np.maximum(q0, q0 + x)[..., None]
    seg = np.clip(np.minimum(hi, b) - np.maximum(lo, a), 0, None)
    return (np.sign(x) * (seg * V).sum(2)).sum(1)


for y in (2035, 2040):
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    um = SM.with_mustrun(B.fleet(y))
    for K in (0.0, 50.0, 100.0, 200.0, 300.0):
        T, _, st = SM.run_year(I, cal, Ks=[K], drop=(), return_state=True)
        R = st["R"]; cap = B.avail_cap(um, I["month"], I)
        fx = lambda *a: (R["on"], cap)
        q0, E_, V = MO.supply_curve(I, um, st["dis"], commit_fn=fx)
        Vm = SM.markup_curve(V, st["info"], I)
        d = 5.0
        c1, s1 = BT.fleet_schedule(q0, E_, Vm, K * 10)
        c2, s2 = BT.fleet_schedule(q0, E_, Vm, K * 10 + d)
        mv = PZ.annual((area(q0, E_, Vm, c1 - s1) - area(q0, E_, Vm, c2 - s2)) / d, I["fy"])
        pv = PZ.annual(PZ.daily_value(st["p"]), I["fy"])
        print(y, K, f"価格から {pv:8.1f}  目的関数の差から {mv:8.1f}  差 {mv - pv:+7.1f}（{(mv - pv) / pv:+.4f}）  π {T.iloc[0]['π(円/kW-年)']:7.0f}  "
              f"同じ解か {np.abs(c1 - st['chg']).max():.2f}MW  繰り返し {int(T.iloc[0]['運用の繰り返し(回)'])}", flush=True)
