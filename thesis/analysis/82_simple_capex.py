#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデルの頑健性: 蓄電池の建設費の低下の想定（参入の計算だけが変わるので、π の曲線は simple_pik.npz を使い回す）

建設費の想定: 主（足元4.8万円/kWh、IEA BSET 2024 の低下率）、速く下がる（NREL 2025 の最小）、ゆっくり下がる（NREL 2025 の最大）、
足元6.7万円/kWh（三菱総研の単純平均、低下率は IEA）、下がらない（4.8万円で一定）
出力: data/processed/simple_capex_robustness.csv
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, entry as EN

PROC = os.path.join(ROOT, "data", "processed")
SCEN = os.environ.get("SCEN", "主")
SUFFIX = "" if SCEN == "主" else f"_{SCEN}"
CAPEX = {  # 表示名: (低下率の case, 足元の資本費)
    "主（4.8万円、IEA の低下率）": ("主", None),
    "速く下がる（NREL の最小）": ("低位", None),
    "ゆっくり下がる（NREL の最大）": ("高位", None),
    "足元6.7万円（IEA の低下率）": ("主", 67_000.0),
    "下がらない（4.8万円で一定）": ("一定", None),
}
CASES = ["上乗せ", "上乗せ_比例", "上乗せ_赤字は外", "燃料費", "上乗せ_マストラン2台", "上乗せ_マストランなし"]
P_SHOW = (14_972.0, 17_000.0, 20_000.0)
TARGETS = (100.0, 150.0, 200.0)
_Z = None


def _load():
    global _Z
    if _Z is None:
        Z = dict(np.load(os.path.join(PROC, f"simple_pik{SUFFIX}.npz")))
        _Z = (Z.pop("K"), Z)
    return _Z


def curves(case, P):
    """容量価格 P の π の曲線（格子の間は直線で補間）"""
    Ks, Z = _load()
    grid = sorted({float(k.split("|")[1]) for k in Z if k.startswith(case + "|")})
    lo = max([q for q in grid if q <= P] or [grid[0]])
    hi = min([q for q in grid if q >= P] or [grid[-1]])
    a = lambda q, y: Z[f"{case}|{q:.0f}|{y}"]
    return {y: a(lo, y) if hi == lo else a(lo, y) + (a(hi, y) - a(lo, y)) * (P - lo) / (hi - lo) for y in PR.YEARS}


def _job(args):
    case, lab = args
    Ks, _ = _load()
    cc, start = CAPEX[lab]
    path = lambda P: EN.path(curves(case, P), Ks, P, capex_case=cc, capex_start=start)
    row = {"シナリオ": SCEN, "場合": case, "建設費": lab}
    for P in P_SHOW:
        Kt = path(P)
        row.update({f"量 {t}（{P:,.0f}円）": Kt[t] for t in (2030, 2035, 2040, 2045)})
        jump = [t for t in range(2027, 2046) if Kt[t] >= Ks[-1] - 1e-6]
        row[f"上限に届く年（{P:,.0f}円）"] = jump[0] if jump else np.nan
    for tgt in TARGETS:
        f = lambda P: path(P)[2040] - tgt
        lo, hi = 0.0, 30_000.0
        if f(lo) >= 0:
            val = 0.0
        elif f(hi) < 0:
            val = np.nan
        else:
            for _ in range(16):
                mid = (lo + hi) / 2
                lo, hi = (lo, mid) if f(mid) >= 0 else (mid, hi)
            val = hi
        row[f"2040年に{tgt:.0f}万kW に要る容量価格"] = val
    return row


def main():
    _, Z = _load()
    cases = [c for c in CASES if any(k.startswith(c + "|") for k in Z)]   # 80 で解いた場合だけ（新しい主は3つの払い方）
    jobs = [(c, lab) for c in cases for lab in CAPEX]
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "9"))) as ex:
        rows = list(ex.map(_job, jobs, chunksize=1))
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(PROC, f"simple_capex_robustness{SUFFIX}.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    cols = ["場合", "建設費", "量 2035（14,972円）", "量 2040（14,972円）", "量 2045（14,972円）", "上限に届く年（14,972円）",
            "2040年に100万kW に要る容量価格", "2040年に150万kW に要る容量価格", "2040年に200万kW に要る容量価格"]
    print(T[cols].round(1).to_string())


if __name__ == "__main__":
    main()
