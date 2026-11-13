#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""レビュー（review/20261113）で足した図・描き直した図

1. v2_entry_path_by_rule.png  普及均衡点の経路（2026〜40年度）と、回収方法による差の内訳（図6.1）
   data/processed/v2_table63.csv から描く（モデルは回さない）。差の分解に使う「運転損失だけ補填」も載せる
2. v2_hourly_price_by_rule.png  2040年度・蓄電池100万kW の時刻別の平均価格（図6.3。スポット回収と燃料費入札）
   モデルを3回解く。結果は data/processed/v2_hourly_price_by_rule.csv に保存する
   FIG_ONLY=1 なら保存した結果から図だけ描き直す
3. v2_pi_two_rules.png  値差収益 π と参入のしきい値（図6.4。2つの回収方法）。data/processed/simple_pik.npz から描く
4. v2_source_two_rules.png  電源を1つだけ動かしたときの普及均衡点（図6.5。2つの回収方法）。
   data/processed/simple_source_scenarios.csv から描く。上の軸に設備の量を書く

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
import matplotlib.ticker
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
MAIN = ("スポット回収", "燃料費入札")          # 本文で比べる2つの回収方法（運転損失だけ補填は差の分解にだけ使う）
PIK_KEY = {"スポット回収": "上乗せ", "燃料費入札": "燃料費"}
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
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
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
    fig, (a, b) = plt.subplots(2, 1, figsize=(9.2, 4.4), sharex=True, gridspec_kw={"height_ratios": [3.0, 1]})
    for n, (lab, col, ls, mk) in RULES.items():
        if lab not in MAIN:
            continue
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


def fig_pi_two():
    """値差収益 π(K) と参入のしきい値（2035・2040年度）。2つの回収方法"""
    Z = np.load(os.path.join(PROC, "simple_pik.npz"), allow_pickle=True)
    K = Z["K"]
    T = pd.read_csv(os.path.join(PROC, "v2_table63.csv"))
    T = T[(T["シナリオ"] == "主") & (T["場合"] == "スポットで回収（主）")].set_index("年")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.7), sharey=True)
    mk_idx = [i for i, k in enumerate(K) if k % 50 == 0 and k <= 500]
    for ax, y in zip(axes, (2035, 2040)):
        for n, (lab, col, ls, mk) in RULES.items():
            if lab not in MAIN:
                continue
            ax.plot(K, Z[f"{PIK_KEY[lab]}|{BASE_P:.0f}|{y}"], color=col, ls=ls, marker=mk, ms=4.5, lw=2.2, markevery=mk_idx, label=lab)
        th = float(T.loc[y, "参入のしきい値"])
        ax.axhline(th, color=MUTED, lw=0.9, ls="-.")
        ax.text(495, th + 250, f"参入のしきい値 {th:,.0f}円", ha="right", fontsize=8.5, color=MUTED)
        ax.axvline(STOCK, color=MUTED, lw=0.9, ls="-.")
        ax.text(STOCK + 6, 13_000, f"既設＋LTDA {STOCK:.1f}万kW", fontsize=8.5, color=MUTED)
        ax.set_xlim(0, 500)
        ax.set_ylim(0, 14_000)
        ax.set_title(f"{y}年", loc="left", color=INK, fontsize=11)
        ax.set_xlabel("蓄電池の量（万kW）", color=MUTED)
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        spines(ax)
    axes[0].set_ylabel("値差収益 π（円/kW-年）", color=INK)
    axes[1].legend(frameon=False, fontsize=9, loc="upper right", bbox_to_anchor=(1.0, 0.9))
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "v2_pi_two_rules.png"), dpi=200)
    plt.close(fig)


def fig_source_two():
    """電源を1つだけ動かしたときの2040年度の普及均衡点。2つの回収方法。上の軸に設備の量（原子力は基数）を書く"""
    S = pd.read_csv(os.path.join(PROC, "simple_source_scenarios.csv"))
    D = S[S["年"] == 2040]
    name = {"スポット回収": "スポットで回収（主）", "燃料費入札": "すべて市場外"}
    xcol = {"太陽光": "太陽光の発電量(TWh、自家消費を含む)", "風力": "風力の発電量(TWh)", "原子力": "原子力の発電量(TWh)"}
    cap = {"太陽光": "太陽光(万kW)", "風力": "風力(万kW)"}
    units = {"なし": "0基", "3号だけ": "1基", "3号＋1号": "2基", "3基": "3基"}
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.9), sharey=True)
    for ax, (g, xc) in zip(axes, xcol.items()):
        for n, (lab, col, ls, mk) in RULES.items():
            if lab not in MAIN:
                continue
            d = D[(D["場合"] == name[lab]) & D["動かす電源"].isin([g, "主"])].sort_values(xc)
            ax.plot(d[xc], d["市場だけで入る量(万kW)"], color=col, ls=ls, marker=mk, ms=4.5, lw=2.2, label=lab)
        d = D[(D["場合"] == name["スポット回収"]) & D["動かす電源"].isin([g, "主"])].sort_values(xc)
        m = d[d["動かす電源"] == "主"].iloc[0]
        ax.annotate("基準", (m[xc], m["市場だけで入る量(万kW)"]), xytext=(-4, 8), textcoords="offset points", color=C1, fontsize=8.5, ha="right")
        ax.axhline(STOCK, color=MUTED, lw=0.9, ls="-.")
        ax.set_xlabel(f"{g}の発電量（TWh/年）", color=MUTED)
        ax.set_ylim(0, 270)
        spines(ax)
        top = ax.secondary_xaxis("top")
        top.set_xticks(list(d[xc]))
        labs = [units[v] for v in d["泊"]] if g == "原子力" else [f"{v:,.0f}" for v in d[cap[g]]]
        top.set_xticklabels(labs, fontsize=7.5, color=MUTED)
        top.tick_params(length=2.5, colors=MUTED)
        top.spines["top"].set_visible(False)
        ax.set_title(f"{g}（上の軸：{'基数' if g == '原子力' else '万kW'}）", loc="left", color=INK, fontsize=10, pad=20)
    axes[0].set_ylabel("普及均衡点（万kW、2040年）", color=INK)
    axes[0].text(axes[0].get_xlim()[1], STOCK - 16, "既設＋LTDA 98.8万kW", color=MUTED, fontsize=8, ha="right")
    axes[2].legend(frameon=False, fontsize=9, loc="center right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "v2_source_two_rules.png"), dpi=200)
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
    if which in ("all", "pi"):
        fig_pi_two()
        print("v2_pi_two_rules.png")
    if which in ("all", "source"):
        fig_source_two()
        print("v2_source_two_rules.png")
