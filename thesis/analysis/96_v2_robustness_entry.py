#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの頑健性（付録C、2026-11-03）: 需給と価格を変えず、参入の計算だけが変わる項目
割引率4%・8%（基準6%）、寿命15年（基準20年）、実行できる比0.70・0.90（基準は較正の値、約0.825）。
建設費の想定は別のスクリプト（simple_capex_robustness.csv）。
π の曲線は基準の計算（simple_pik.npz、容量価格14,972円）を使う。実行できる比は π＝max(比×完全予見の粗利−充電の従量費, 0) を
基準の年ごとの出力（simple_years.csv の完全予見の粗利）から作り直す（価格と充放電は比によらない）。
出力: data/processed/v2_robustness_entry.csv
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, entry as EN, simple as SM

PROC = os.path.join(ROOT, "data", "processed")
P = 14_972.0
CASES = {"上乗せ": "スポットで回収（基準）", "上乗せ_赤字は外": "運転赤字だけ市場外", "燃料費": "すべて市場外"}
TARGET = 98.8


def curves_pik():
    Z = dict(np.load(os.path.join(PROC, "simple_pik.npz")))
    Ks = Z.pop("K")
    return Ks, {c: {y: Z[f"{c}|{P:.0f}|{y}"] for y in PR.YEARS} for c in CASES}


def curves_capture(share):
    Y = pd.read_csv(os.path.join(PROC, "simple_years.csv"), encoding="utf-8-sig",
                    usecols=["場合", "年", "K(万kW)", "容量価格(円/kW)", "π(円/kW-年)", "完全予見の粗利(円/kW-年)"])
    Y = Y[Y["容量価格(円/kW)"] == P]
    Ks = np.array(sorted(Y["K(万kW)"].unique()), float)
    out, err = {}, 0.0
    cap0 = SM.calibration("commit", None)["capture"]
    for c in CASES:
        g = Y[Y["場合"] == c]
        out[c] = {}
        for y in PR.YEARS:
            gy = g[g["年"] == y].sort_values("K(万kW)")
            pf = gy["完全予見の粗利(円/kW-年)"].to_numpy()
            err = max(err, float(np.abs(np.maximum(cap0 * pf - PR.W_LOSS, 0.0) - gy["π(円/kW-年)"].to_numpy()).max()))
            out[c][y] = np.maximum(share * pf - PR.W_LOSS, 0.0)
    return Ks, out, cap0, err


def row(label, Ks, cur, case):
    Kt = EN.path(cur[case], Ks, P)
    over = [t for t in range(2026, 2046) if Kt[t] > TARGET + 1e-6]
    return {"頑健性": label, "場合": CASES[case], **{f"量 {t}": Kt[t] for t in (2030, 2035, 2040, 2045)},
            "98.8万kW を超える最初の年": over[0] if over else np.nan}


def main():
    rows = []
    Ks, cur = curves_pik()
    for c in CASES:
        rows.append(row("基準", Ks, cur, c))
    base_wacc, base_life = PR.WACC, PR.LIFE
    for label, wacc, life in (("割引率4%", 0.04, base_life), ("割引率8%", 0.08, base_life), ("寿命15年", base_wacc, 15)):
        PR.WACC, PR.LIFE = wacc, life
        for c in CASES:
            rows.append(row(label, Ks, cur, c))
    PR.WACC, PR.LIFE = base_wacc, base_life
    for share in (0.70, 0.90):
        Ks2, cur2, cap0, err = curves_capture(share)
        print(f"実行できる比: 基準 {cap0:.4f}、π の作り直しの誤差 最大 {err:.2e} 円/kW-年", flush=True)
        for c in CASES:
            rows.append(row(f"実行できる比{share:.2f}", Ks2, cur2, c))
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(PROC, "v2_robustness_entry.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(T.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
