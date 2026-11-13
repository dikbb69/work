#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""レビュー（review/20261113）で足した図2点

1. v2_entry_path_by_rule.png  3つの回収方法の普及均衡点の経路（2026〜40年度）と設置量
   data/processed/v2_table63.csv から描く（モデルは回さない）
2. v2_hourly_price_by_rule.png  2040年度・蓄電池100万kW の時刻別の平均価格（3つの回収方法）
   モデルを3回解く。結果は data/processed/v2_hourly_price_by_rule.csv に保存する
   FIG_ONLY=1 なら保存した結果から図だけ描き直す

フォントは Hiragino Sans があれば使い、なければ IPA Pゴシックで描く
（原稿のほかの図と書体をそろえるには、Mac で FIG_ONLY=1 を付けて描き直す）
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
C1, C2, C4 = "#2a78d6", "#eb6834", "#eda100"
_have = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = [f for f in ("Hiragino Sans", "IPAPGothic", "IPAGothic") if f in _have] + ["sans-serif"]
plt.rcParams["font.size"] = 10
BASE_P = 14_972.0
STOCK = 98.8          # 既設と LTDA の落札分（万kW）
APPLY = 238.0         # 契約申込（万kW、2026年9月末）
# v2_table63.csv の「場合」の名前 → 本文の呼び名、線の色と形（図6.2・6.3 と同じ）
RULES = {"スポットで回収（主）": ("スポット回収", C1, "-", "o"),
         "赤字だけ市場外": ("運転損失だけ補填", C4, "--", "s"),
         "すべて市場外": ("燃料費入札", C2, ":", "^")}
CASE_ARGS = {"スポット回収": (False, "spot"), "運転損失だけ補填": (False, "outside"), "燃料費入札": (True, "spot")}   # (standard, losses)
EXIT_CASE = {"spot": "上乗せ", "outside": "上乗せ_赤字は外"}


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def fig_path():
    T = pd.read_csv(os.path.join(PROC, "v2_table63.csv"))
    T = T[(T["シナリオ"] == "主") & (T["年"] <= 2040)]
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    names = [n for n in RULES if n in set(T["場合"])]
    if len(names) != 3:
        raise SystemExit(f"場合の名前が合わない: {sorted(set(T['場合']))}")
    last = {}
    for n in names:
        lab, col, ls, mk = RULES[n]
        g = T[T["場合"] == n].sort_values("年")
        last[lab] = float(g["採算が合う量 K*(万kW)"].iloc[-1])
        ax.plot(g["年"], g["採算が合う量 K*(万kW)"], color=col, ls=ls, marker=mk, ms=5, lw=2.2,
                label=f"普及均衡点：{lab}（2040年度 {last[lab]:.1f}万kW）")
    g = T[T["場合"] == names[0]].sort_values("年")
    ax.step(g["年"], np.minimum(g["経路の量(万kW)"], STOCK), where="mid", color="#9b9a94", lw=1.6, label="既設と LTDA の落札分")
    ax.axhline(STOCK, color=MUTED, lw=0.9, ls="-.")
    ax.text(2026.0, STOCK + 5, f"既設＋LTDA {STOCK:.1f}万kW", fontsize=9, color=MUTED)
    ax.axhline(APPLY, color=MUTED, lw=0.9, ls="-.")
    ax.text(2026.0, APPLY + 5, f"契約申込 {APPLY:.0f}万kW", fontsize=9, color=MUTED)
    a, b, c = last["スポット回収"], last["運転損失だけ補填"], last["燃料費入札"]
    x = 2040.45
    for lo, hi, txt in ((b, a, f"運転損失の回収\n+{a - b:.1f}"), (c, b, f"固定費の不足の回収\n+{b - c:.1f}")):
        ax.annotate("", xy=(x, hi), xytext=(x, lo), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=0.9))
        ax.text(x + 0.12, (lo + hi) / 2, txt, fontsize=8.5, color=INK, va="center", linespacing=1.3)
    ax.set_xlim(2025.5, 2042.6)
    ax.set_ylim(0, 260)
    ax.set_xticks(range(2026, 2041, 2))
    ax.set_xlabel("年度", color=MUTED)
    ax.set_ylabel("蓄電池の量（万kW）", color=INK)
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0.0, 0.88))
    spines(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "v2_entry_path_by_rule.png"), dpi=200)
    plt.close(fig)
    return T


def _job(rule):
    warnings.filterwarnings("ignore")
    from model import params as PR, simple as SM, merit as MO
    y, K = 2040, 100.0
    standard, losses = CASE_ARGS[rule]
    sc = PR.SCENARIOS["主"]
    X = pd.read_csv(os.path.join(PROC, "simple_exit_years.csv"))
    drop = tuple(X[(X["場合"] == EXIT_CASE[losses]) & (X["退出の年"] < y)]["号機"]) if "場合" in X else ()
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    T, _, st = SM.run_year(I, SM.calibration("commit"), Ks=[K], P_list=(BASE_P,), standard=standard, p_sched=BASE_P,
                           drop=drop, losses=losses, return_state=True)
    p, chg, dis = st["p"], st["chg"], st["dis"]
    r = T.iloc[0]
    low4 = float(np.sort(p, 1)[:, :4].mean())
    high4 = float(np.sort(p, 1)[:, -4:].mean())
    H = pd.DataFrame({"回収方法": rule, "年": y, "K(万kW)": K, "時刻": np.arange(24), "価格(円/kWh)": p.mean(0),
                      "充電(MW)": chg.mean(0), "放電(MW)": dis.mean(0)})
    S = {"回収方法": rule, "年": y, "K(万kW)": K, "μ(円/kWh)": float(r["上乗せ μ(円/kWh)"]), "π(円/kW-年)": float(r["π(円/kW-年)"]),
         "安い4時間(円/kWh)": low4, "高い4時間(円/kWh)": high4, "日の値幅(円/kWh)": high4 - low4,
         "0.01円の時間(h/年)": float(r["0.01円の時間(h/年)"])}
    return H, S


def run_hourly():
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=3) as ex:
        out = list(ex.map(_job, list(CASE_ARGS)))
    H = pd.concat([o[0] for o in out], ignore_index=True)
    S = pd.DataFrame([o[1] for o in out])
    H.to_csv(os.path.join(PROC, "v2_hourly_price_by_rule.csv"), index=False, encoding="utf-8-sig")
    S.to_csv(os.path.join(PROC, "v2_hourly_price_by_rule_summary.csv"), index=False, encoding="utf-8-sig")
    return H, S


def fig_hourly(H):
    fig, (a, b) = plt.subplots(2, 1, figsize=(9.2, 5.6), sharex=True, gridspec_kw={"height_ratios": [3.2, 1]})
    for n, (lab, col, ls, mk) in RULES.items():
        g = H[H["回収方法"] == lab]
        a.plot(g["時刻"], g["価格(円/kWh)"], color=col, ls=ls, marker=mk, ms=4, lw=2.2, label=lab)
    a.set_ylabel("平均価格（円/kWh）", color=INK)
    a.set_ylim(bottom=0)
    a.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, 0.98))
    spines(a)
    g = H[H["回収方法"] == "スポット回収"]
    b.bar(g["時刻"], -g["充電(MW)"] / 10, color="#9b9a94", width=0.8, label="充電")
    b.bar(g["時刻"], g["放電(MW)"] / 10, color=C1, width=0.8, label="放電")
    b.axhline(0, color=MUTED, lw=0.8)
    b.set_ylabel("充放電\n（万kW）", color=INK)
    b.set_xlabel("時刻", color=MUTED)
    b.set_xticks(range(0, 24, 3))
    b.legend(frameon=False, fontsize=8.5, ncol=2, loc="lower right")
    spines(b)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "v2_hourly_price_by_rule.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "path"):
        fig_path()
        print("v2_entry_path_by_rule.png")
    if which in ("all", "hourly"):
        f = os.path.join(PROC, "v2_hourly_price_by_rule.csv")
        if os.environ.get("FIG_ONLY") == "1" and os.path.exists(f):
            H = pd.read_csv(f)
        else:
            H, S = run_hourly()
            print(S.round(3).to_string(index=False))
        fig_hourly(H)
        print("v2_hourly_price_by_rule.png")
