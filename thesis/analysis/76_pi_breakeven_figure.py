#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""蓄電池の価値 π(K) と損益分岐（主の前提: 要らない火力はマストランも退出、容量収入の κ は量に応じた実効値）

2035年・2040年の π(K)（補填・契約と、すべてスポット（全国の上乗せ））と、その年から動く蓄電池の損益分岐の π を重ねる。
損益分岐 ＝ 年あたりの投資額（建設は前年）＋運転維持費＋託送等の固定費 − κ×容量価格。κ は実効値（実線）と0.861 一定（点線）
出力: figures/hokkaido/eqm_pi_breakeven.png、data/processed/eqm_pi_breakeven.csv
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, calibrate as CB, merit as MO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = os.path.join(ROOT, "data", "processed")
P = 14_972.0
SERIES = [("補填・契約（基準）", "capacity_退出あり", "#2a78d6"), ("すべてスポット（全国の上乗せ）", "all_spot_退出あり", "#eb6834")]   # 検証済みの色の1・2番


def breakeven(y, kap):
    """y 年から動く蓄電池（前年に建てる）の損益分岐の π（円/kW-年）。π が一定と置いた近似"""
    tau = y - PR.LAG
    ann = sum(1 / (1 + PR.WACC) ** s for s in range(PR.LAG, PR.LAG + PR.LIFE))
    inv = PR.HOURS * PR.capex(tau) * (1 + PR.DECOM / (1 + PR.WACC) ** PR.LIFE)
    return inv / ann + PR.OM + PR.NET_FIX - kap * P


def main():
    import warnings
    warnings.filterwarnings("ignore")
    Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
    K = Z["K"]
    plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
    plt.rcParams["font.size"] = 11
    ink, muted = "#1F2A3A", "#6B7480"
    rows = []
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    sc = PR.SCENARIOS["主"]
    for ax, y in zip(axes, (2035, 2040)):
        kap = CB.kappa_eff(MO.inputs_future(PR.scenario_year(y, sc), sc), K)
        be_eff, be_const = breakeven(y, kap), breakeven(y, PR.KAPPA_BATT)
        for name, key, col in SERIES:
            pi = Z[f"主|{key}|{P:.0f}|{y}"]
            ax.plot(K, pi, color=col, lw=2, label=name)
            for k, v in zip(K, pi):
                rows.append({"年": y, "払い方": name, "K(万kW)": k, "π(円/kW-年)": v})
        ax.plot(K, be_eff, color=muted, lw=1.6, label="損益分岐（κ は量に応じた実効値）")
        ax.axhline(be_const, color=muted, lw=1.2, ls="--", label="損益分岐（κ 0.861 で一定）")
        for k, b, kp in zip(K, be_eff, kap):
            rows.append({"年": y, "払い方": "損益分岐（κ 実効値）", "K(万kW)": k, "π(円/kW-年)": b, "κ 実効値": kp})
        ax.axvline(98.8, color=muted, lw=1, ls=":")
        ax.text(101, 21_500, "既設＋LTDA\n98.8万kW", color=muted, fontsize=9, va="top")
        ax.set_title(f"{y}年（容量価格14,972円）", color=ink, fontsize=12, loc="left")
        ax.set_xlabel("蓄電池の量 K（万kW）", color=ink)
        ax.set_xlim(0, 400)
        ax.set_ylim(0, 22_000)
        ax.grid(axis="y", color="#E3E1DA", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("1kW の価値 π（円/kW-年）", color=ink)
    axes[-1].legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.01, -0.03, "主の前提（要らない火力はマストランも燃料費の高い号機から退出）。損益分岐は、その年から動く蓄電池（前年に建てる）の、π が一定と置いた近似。"
             "κ の実効値は、各年度の上位3日に4時間分のエネルギーで余裕を持ち上げられる幅÷容量（0.861 が上限）", fontsize=8.5, color=muted)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "hokkaido", "eqm_pi_breakeven.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    pd.DataFrame(rows).to_csv(os.path.join(PROC, "eqm_pi_breakeven.csv"), index=False, encoding="utf-8-sig")
    print("wrote", out)


if __name__ == "__main__":
    main()
