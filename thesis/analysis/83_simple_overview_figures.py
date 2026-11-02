#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデルの骨子を説明する図（2026-10-27）

simple_frame.png       モデルの骨組み（①〜④と参入の均衡）
simple_fit.png         足元（FY2024〜25）の当てはまり: 時刻別の平均価格（季節別）と燃料別の発電量
simple_requirement.png 火力の要件と一律の上乗せ（均衡の経路、容量価格14,972円）
simple_pi_balance.png  蓄電池1kW の価値 π(K) と損益分岐（2035・2040年、上乗せの形・赤字の払い方で比較）
simple_entry_paths.png 普及の経路（容量価格ごと）と、2040年の量に要る容量価格
simple_robustness.png  2040年に100万kW に要る容量価格の頑健性
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, simple as SM, merit as MO, balance as B, data as DT, entry as EN

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"      # 検証済みの並び（隣り合う組が見分けられる）
plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
plt.rcParams["font.size"] = 10
BASE_P = 14_972.0
SUFFIX = os.environ.get("SUFFIX", "")                         # シナリオの出力の接尾辞（主は空、例: "_エネ基の下限"）。図の名前にも付ける
TITLE = os.environ.get("TITLE", "")                           # 図の題に添えるシナリオの名前
NAMES = {"上乗せ": "スポットで回収（主）", "燃料費": "すべて市場外", "上乗せ_赤字は外": "赤字だけ市場外", "上乗せ_比例": "比例の上乗せ（頑健性）"}


def spines(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def save(fig, name):
    if SUFFIX and name != "simple_frame.png":
        name = name.replace(".png", f"{SUFFIX}.png")
    fig.savefig(os.path.join(FIG, name), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def breakeven(y, P=BASE_P, kap=PR.KAPPA_BATT, case="主", start=None):
    """参入の規則のしきい値: その年に運転を始める蓄電池の年あたりの建設費＋運転維持費＋託送等−κ×容量価格"""
    return EN.annual_cost(y, case, start) + PR.OM + PR.NET_FIX - kap * P


def fig_frame():
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (0.2, 3.4, 3.6, 2.2, "前提（外から与える）", "需要（OCCTO）・太陽光・風力（供給計画・エネ基）\n原子力（泊の再稼働）・水力（気象年）\n火力の号機・廃止・LTDA\n燃料費・東北の価格・北本の容量"),
        (4.2, 3.4, 3.6, 2.2, "① 価格: メリットオーダー", "コマごとに燃料費の安い順に並べる\nマストラン3台＋日ごとの起動・最低出力\n東北とは北本の範囲で売買\n蓄電池は全体の充放電を量ごとに解く"),
        (8.2, 3.4, 3.6, 2.2, "② 入札＝燃料費＋一律の上乗せ", "上乗せ＝回収できない固定費と\nマストランの運転の赤字÷約定量\n（0.01円の時間を除くコマに一律）"),
        (8.2, 0.4, 3.6, 2.2, "③ 必要な収入（足元）", "FY2024〜25 のスポットの粗利\n＋容量収入（1kW 年19,196円）\n−将来の容量収入（14,972円で固定）"),
        (4.2, 0.4, 3.6, 2.2, "④ 退出", "1年間一度も動かない号機は退出\n（マストラン・LTDA は残る）\n→③の対象から外れる"),
        (0.2, 0.4, 3.6, 2.2, "蓄電池の参入", "その年の1kW の価値 π（日々の値差）\n＋0.861×容量価格−運転維持費−託送等が\n年あたりの建設費を上回る量まで入る\n（建設費の低下を待たない）"),
    ]
    for x, y, w, h, t, b in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12", fc="#f4f6f9", ec="#c3c2b7", lw=1))
        ax.text(x + 0.15, y + h - 0.3, t, fontsize=11.5, color=INK, va="top", weight="bold")
        ax.text(x + 0.15, y + h - 0.85, b, fontsize=9.5, color=MUTED, va="top", linespacing=1.5)
    arr = dict(arrowstyle="-|>", color=C1, lw=1.6)
    ax.annotate("", xy=(4.2, 4.5), xytext=(3.8, 4.5), arrowprops=arr)
    ax.annotate("", xy=(8.2, 4.5), xytext=(7.8, 4.5), arrowprops=arr)
    ax.annotate("", xy=(10.0, 3.4), xytext=(10.0, 2.6), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.6))
    ax.text(10.1, 3.0, "要件を満たす上乗せ", fontsize=9, color=C2)
    ax.annotate("", xy=(8.2, 1.5), xytext=(7.8, 1.5), arrowprops=arr)
    ax.annotate("", xy=(3.8, 2.45), xytext=(8.3, 3.35), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.6))
    ax.text(5.0, 2.8, "上乗せ込みの価格", fontsize=9, color=C2, rotation=10.5, rotation_mode="anchor")
    ax.annotate("", xy=(4.6, 3.4), xytext=(3.4, 2.6), arrowprops=dict(arrowstyle="-|>", color=C3, lw=1.6))
    ax.text(0.25, 2.95, "充放電が需給と価格を変える（共食い）", fontsize=9, color=C3)
    ax.set_title("簡素版のモデルの骨組み（収益源をスポットに集約し、蓄電池の自由参入の均衡を測る）", loc="left", fontsize=12.5, color=INK)
    save(fig, "simple_frame.png")


def fig_fit():
    C = DT.calib()
    seasons = {"冬（12〜2月）": (12, 1, 2), "春（3〜5月）": (3, 4, 5), "夏（6〜9月）": (6, 7, 8, 9), "秋（10〜11月）": (10, 11)}
    pa, pm, mo = [], [], []
    gen = {}
    for fy in PR.CALIB_FY:
        I = MO.inputs_actual(fy)
        R = SM.dispatch(I, B.fleet(fy))
        pa.append(I["p_act"])
        pm.append(R["p0"])
        mo.append(I["month"][:, 0])
        r = C["fy"] == fy
        for fuel in ("石炭", "LNG", "石油"):
            ia = [j for j, u in enumerate(C["units"]) if u[1] == fuel]
            im = [j for j, u in enumerate(R["units"]) if u[1] == fuel]
            gen[(fy, fuel, "実績")] = C["G"][r][:, :, ia].sum() / 1e6
            gen[(fy, fuel, "モデル")] = R["g"][:, :, im].sum() / 1e6
    pa, pm, mo = np.vstack(pa), np.vstack(pm), np.concatenate(mo)
    fig, axes = plt.subplots(1, 5, figsize=(17, 3.9), gridspec_kw=dict(width_ratios=[1, 1, 1, 1, 1.3]))
    for ax, (s, ms) in zip(axes[:4], seasons.items()):
        sel = np.isin(mo, ms)
        ax.plot(range(24), np.nanmean(pa[sel], 0), color=INK, lw=2, label="実績（JEPX 北海道）")
        ax.plot(range(24), pm[sel].mean(0), color=C1, lw=2, ls="--", label="モデル（上乗せ前）")
        ax.set_title(s, loc="left", color=INK, fontsize=10.5)
        ax.set_xticks([0, 6, 12, 18, 23])
        ax.set_ylim(0, 22)
        spines(ax)
    axes[0].set_ylabel("時刻別の平均価格（円/kWh）", color=INK)
    axes[0].legend(frameon=False, fontsize=8.5, loc="lower left")
    ax = axes[4]
    x = np.arange(3)
    for k, fy in enumerate(PR.CALIB_FY):
        for j, lab in enumerate(("実績", "モデル")):
            v = [gen[(fy, f, lab)] for f in ("石炭", "LNG", "石油")]
            ax.bar(x + (k * 2 + j) * 0.2 - 0.3, v, width=0.18, color=[C1, C2][j], alpha=1.0 if k == 0 else 0.55,
                   label=f"FY{fy} {lab}", edgecolor="white", lw=0.6)
    ax.set_xticks(x, ["石炭", "LNG", "石油"])
    ax.set_ylabel("発電量（TWh/年）", color=INK)
    ax.set_title("燃料別の発電量", loc="left", color=INK, fontsize=10.5)
    ax.set_ylim(0, 14)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper right")
    spines(ax)
    fit = SM.calibration("commit")["fit"]
    fig.suptitle(f"足元の当てはまり（FY2024〜25）: 価格の R² {fit[2024]['R²']:.2f}・{fit[2025]['R²']:.2f}、日の値幅 実績 {fit[2024]['日の値幅 実績']:.1f}・{fit[2025]['日の値幅 実績']:.1f}円、"
                 f"モデル {fit[2024]['日の値幅 モデル']:.1f}・{fit[2025]['日の値幅 モデル']:.1f}円", x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save(fig, "simple_fit.png")


def fig_requirement(Y, path):
    rows = []
    for y in PR.YEARS:
        k = float(path[f"量 {y}"])
        g = Y[(Y["場合"] == "上乗せ") & (Y["容量価格(円/kW)"] == BASE_P) & (Y["年"] == y)]
        r = g.iloc[np.argmin(np.abs(g["K(万kW)"].to_numpy() - k))]
        rows.append({"年": y, "要件": r["要件(億円/年)"], "上乗せなしの粗利": r["α＝1 の粗利(億円/年)"],
                     "マストランの赤字": r["マストランの運転の赤字 α＝1(億円/年)"], "μ": r["上乗せ μ(円/kWh)"], "π": r["π(円/kW-年)"]})
    D = pd.DataFrame(rows)
    D["上乗せで回収する額"] = (D["要件"] - D["上乗せなしの粗利"]).clip(lower=0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.6))
    x = D["年"]
    a1.bar(x, D["要件"], color=C1, width=0.7, label="③ 要件（固定費のうちスポットで回収する分）", edgecolor="white")
    a1.bar(x, D["マストランの赤字"], bottom=D["要件"], color=C2, width=0.7, label="マストランの運転の赤字（上乗せなしの価格で）", edgecolor="white")
    a1.plot(x, D["上乗せで回収する額"], color=INK, marker="o", ms=4, lw=1.8, label="上乗せで回収する額")
    a1.set_ylabel("億円/年", color=INK)
    a1.set_title(f"火力が上乗せで回収する額（{TITLE + '、' if TITLE else ''}均衡の経路、容量価格14,972円）", loc="left", color=INK, fontsize=11)
    a1.legend(frameon=False, fontsize=8.5, loc="upper right")
    spines(a1)
    a2.plot(x, D["μ"], color=C1, marker="o", ms=4, lw=2)
    a2.set_ylim(0, None)
    a2.set_ylabel("一律の上乗せ μ（円/kWh）", color=INK)
    a2.set_title("一律の上乗せ（0.01円の時間を除く約定コマ）", loc="left", color=INK, fontsize=11)
    spines(a2)
    fig.text(0.01, -0.03, "要件は2029年度まで容量価格の実績が低いので大きい。スポットで回収（主）の経路。"
             "上乗せで回収する額＝要件−上乗せなしの粗利（マストランの赤字を差し引いた正味）", fontsize=8.5, color=MUTED)
    fig.tight_layout()
    save(fig, "simple_requirement.png")
    return D


def fig_pi(Z, Ks):
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), sharey=True)
    series = [("上乗せ", NAMES["上乗せ"], C1, "-"), ("燃料費", NAMES["燃料費"], C2, "-"),
              ("上乗せ_比例", NAMES["上乗せ_比例"], C3, "--"), ("上乗せ_赤字は外", NAMES["上乗せ_赤字は外"], C4, "--")]
    series = [x for x in series if f"{x[0]}|{BASE_P:.0f}|2040" in Z]
    last = max(float(Ks[Z[f"{k}|{BASE_P:.0f}|{y}"] > 0].max(initial=0.0)) for k, *_ in series for y in (2035, 2040))   # π＞0 の最後の格子の点
    xmax = min(float(Ks.max()), max(400.0, float(np.ceil((last + 1.0) / 50.0) * 50.0)))
    for ax, y in zip(axes, (2035, 2040)):
        for key, lab, col, ls in series:
            ax.plot(Ks, Z[f"{key}|{BASE_P:.0f}|{y}"], color=col, lw=2, ls=ls, label=lab)
        b = breakeven(y)
        ax.axhline(b, color=INK, lw=1.2, ls=":")
        ax.text(xmax - 5, b + 150, f"損益分岐 {b:,.0f}円", ha="right", fontsize=9, color=INK)
        ks = EN.preset_stock(y)
        ax.axvline(ks, color=MUTED, lw=0.8, ls=":")
        ax.text(ks + 4, 12_500, f"既設＋LTDA {ks:.1f}万kW", fontsize=8.5, color=MUTED)
        ax.set_xlim(0, xmax)
        ax.set_ylim(0, max(14_000, float(np.ceil(max(Z[f"{k}|{BASE_P:.0f}|{y}"][0] for k, *_ in series) / 2_000) * 2_000)))
        ax.set_title(f"{y}年（{TITLE + '、' if TITLE else ''}容量価格14,972円、κ 0.861）", loc="left", color=INK, fontsize=11)
        ax.set_xlabel("蓄電池の量（万kW）", color=MUTED)
        spines(ax)
    axes[0].set_ylabel("1kW の価値 π（円/kW-年）", color=INK)
    axes[1].legend(frameon=False, fontsize=8.5, loc="upper right")
    fig.text(0.01, -0.03, "損益分岐＝その年に運転を始める蓄電池の年あたりの建設費＋運転維持費＋託送等の固定費−0.861×容量価格。"
             "参入の規則: その年の π が損益分岐を上回る量まで入る（建設費の将来の低下は見込まない）。"
             + (f"{xmax:.0f}万kW より先は、どの線も π＝0" if last < xmax else f"{xmax:.0f}万kW（計算の格子の上限）でも π＞0 の線がある"), fontsize=8.5, color=MUTED)
    fig.tight_layout()
    save(fig, "simple_pi_balance.png")


def fig_entry(E, RQ):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8))
    yrs = list(range(2026, 2046))
    cols = {14_972.0: C1, 17_000.0: C2, 18_000.0: C3, 20_000.0: C4}
    for P, col in reversed(list(cols.items())):                 # 主（14,972円）を最後に描いて、重なっても見えるようにする
        r = E[(E["場合"] == "上乗せ") & (E["容量価格(円/kW)"] == P)]
        if r.empty:
            continue
        a1.plot(yrs, [r.iloc[0][f"量 {t}"] for t in yrs], color=col, lw=2.6 if P == BASE_P else 2, marker="o", ms=3, label=f"容量価格 {P:,.0f}円",
                zorder=3 if P == BASE_P else 2)
    a1.set_ylabel("蓄電池の量（万kW）", color=INK)
    a1.set_xticks(list(range(2026, 2046, 2)))
    a1.set_title(f"普及の経路（{TITLE + '、' if TITLE else ''}スポットで回収、κ 0.861）", loc="left", color=INK, fontsize=11)
    top = max(float(E[(E["場合"] == "上乗せ") & (E["容量価格(円/kW)"] == P)].iloc[0][f"量 {t}"]) for P in cols for t in yrs
              if not E[(E["場合"] == "上乗せ") & (E["容量価格(円/kW)"] == P)].empty)
    a1.set_ylim(0, min(max(250, np.ceil(top / 50) * 50), 800))
    a1.axhline(98.8, color=MUTED, lw=0.8, ls="--")
    h, l = a1.get_legend_handles_labels()
    a1.legend(h[::-1], l[::-1], frameon=False, fontsize=8.5, loc="upper left")
    spines(a1)
    tg = [100.0, 150.0, 200.0]
    show = [(k, NAMES[k], c) for k, c in (("上乗せ", C1), ("燃料費", C2), ("上乗せ_赤字は外", C4), ("上乗せ_比例", C3)) if (RQ["場合"] == k).any()]
    for key, lab, col in show:
        g = RQ[(RQ["場合"] == key) & (RQ["κ"] == "0.861 一定")].sort_values("2040年の合計（万kW）")
        zero = g["要る容量価格（2030年度以降、円/kW）"] <= 0                # 0円は「容量価格がなくても届く」という下限で、計算した価格ではない
        a2.plot(g.loc[~zero, "要る容量価格（2030年度以降、円/kW）"], g.loc[~zero, "2040年の合計（万kW）"], color=col, lw=2, marker="o", ms=5, label=lab)
        if zero.any():
            a2.plot(g.loc[zero, "要る容量価格（2030年度以降、円/kW）"], g.loc[zero, "2040年の合計（万kW）"], "o", ms=6, mfc="white", mec=col, mew=1.5)
            a2.text(400, float(g.loc[zero, "2040年の合計（万kW）"].iloc[0]) + 3 + 4 * [s[0] for s in show].index(key), f"{lab}: 0円でも届く", fontsize=8.5, color=col)
    a2.axvline(BASE_P, color=MUTED, lw=1, ls=":")
    a2.text(BASE_P - 100, 196, "現行 14,972円", fontsize=8.5, color=MUTED, ha="right")
    a2.set_ylim(90, 210)
    a2.set_xlabel("2030年度以降の容量価格（円/kW）", color=MUTED)
    a2.set_ylabel("2040年の蓄電池の合計（万kW）", color=INK)
    a2.set_title("2040年の量に要る容量価格（参入の供給曲線）", loc="left", color=INK, fontsize=11)
    a2.legend(frameon=False, fontsize=8.5, loc="center left")
    spines(a2, grid="both")
    fig.tight_layout()
    save(fig, "simple_entry_paths.png")


def fig_robust(RQ, CX):
    base = float(RQ[(RQ["場合"] == "上乗せ") & (RQ["κ"] == "0.861 一定") & (RQ["2040年の合計（万kW）"] == 100.0)].iloc[0]["要る容量価格（2030年度以降、円/kW）"])
    get = lambda case, kap="0.861 一定": float(RQ[(RQ["場合"] == case) & (RQ["κ"] == kap) & (RQ["2040年の合計（万kW）"] == 100.0)].iloc[0]["要る容量価格（2030年度以降、円/kW）"])
    cx = lambda lab: float(CX[(CX["場合"] == "上乗せ") & (CX["建設費"] == lab)].iloc[0]["2040年に100万kW に要る容量価格"])
    items = [
        ("建設費: 速く下がる（NREL の最小）", cx("速く下がる（NREL の最小）"), "建設費"),
        ("建設費: ゆっくり下がる（NREL の最大）", cx("ゆっくり下がる（NREL の最大）"), "建設費"),
        ("建設費: 下がらない（4.8万円）", cx("下がらない（4.8万円で一定）"), "建設費"),
        ("建設費: 足元6.7万円", cx("足元6.7万円（IEA の低下率）"), "建設費"),
        ("上乗せの形: 比例", get("上乗せ_比例"), "価格の作り方"),
        ("一般的な方法（上乗せなし）", get("燃料費"), "価格の作り方"),
        ("マストランの赤字はスポットの外（上乗せ0 で一般的な方法と同じ）", get("上乗せ_赤字は外"), "マストラン"),
        ("マストラン2台（知内2 を外す）", get("上乗せ_マストラン2台"), "マストラン"),
        ("マストランなし", get("上乗せ_マストランなし"), "マストラン"),
        ("κ を量に応じて下げる", get("上乗せ", "量に応じた実効値（上限0.861）"), "容量市場"),
    ]
    items = sorted(items, key=lambda t: abs(t[1] - base))
    col = {"建設費": C1, "価格の作り方": C2, "マストラン": C3, "容量市場": C4}
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i, (lab, v, grp) in enumerate(items):
        ax.plot([base, v], [i, i], color=col[grp], lw=2.5)
        ax.plot(v, i, "o", color=col[grp], ms=8, mec="white", mew=1.5)
        if v > 0:
            ax.text(v + (250 if v >= base else -250), i, f"{v:,.0f}円", va="center", ha="left" if v >= base else "right", fontsize=9, color=INK)
        else:                                                   # 0円は「容量価格なしでも届く」という下限
            ax.text(v + 250, i + 0.12, "0円（容量価格なしでも届く）", va="bottom", ha="left", fontsize=9, color=INK)
    ax.axvline(base, color=INK, lw=1.2)
    ax.text(base, len(items) - 0.4, f" 主 {base:,.0f}円", fontsize=9.5, color=INK, va="bottom")
    ax.axvline(BASE_P, color=MUTED, lw=1, ls=":")
    ax.text(BASE_P, len(items) - 0.4, "現行14,972円 ", fontsize=8.5, color=MUTED, va="bottom", ha="right")
    ax.set_xlim(min(v for _, v, _ in items) - 2_200, max(v for _, v, _ in items) + 1_800)
    ax.set_ylim(-0.6, len(items) + 0.3)
    ax.set_yticks(range(len(items)), [t[0] for t in items])
    ax.set_xlabel("2040年に蓄電池100万kW に要る容量価格（2030年度以降、円/kW）", color=MUTED)
    ax.set_title("頑健性: 要る容量価格はどの前提で動くか", loc="left", color=INK, fontsize=12)
    handles = [plt.Line2D([], [], color=c, lw=2.5, marker="o", label=g) for g, c in col.items()]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="lower right")
    spines(ax, grid="x")
    fig.tight_layout()
    save(fig, "simple_robustness.png")


def main():
    import warnings
    warnings.filterwarnings("ignore")
    Y = pd.read_csv(os.path.join(PROC, f"simple_years{SUFFIX}.csv"), usecols=["場合", "年", "K(万kW)", "容量価格(円/kW)", "要件(億円/年)", "α＝1 の粗利(億円/年)",
                    "マストランの運転の赤字 α＝1(億円/年)", "上乗せ μ(円/kWh)", "π(円/kW-年)"])
    E = pd.read_csv(os.path.join(PROC, f"simple_entry{SUFFIX}.csv"))
    RQ = pd.read_csv(os.path.join(PROC, f"simple_required_capacity_price{SUFFIX}.csv"))
    robust = os.environ.get("NO_ROBUST") != "1"                    # 頑健性の図は頑健性の計算を回し直したときだけ描く
    CX = pd.read_csv(os.path.join(PROC, "simple_capex_robustness.csv")) if robust else None
    Z = dict(np.load(os.path.join(PROC, f"simple_pik{SUFFIX}.npz")))
    Ks = Z.pop("K")
    path = E[(E["場合"] == "上乗せ") & (E["容量価格(円/kW)"] == BASE_P)].iloc[0]
    if not SUFFIX and os.environ.get("ONLY_RESULTS") != "1":
        fig_frame()
        fig_fit()
    D = fig_requirement(Y, path)
    D.to_csv(os.path.join(PROC, f"simple_requirement_path{SUFFIX}.csv"), index=False, encoding="utf-8-sig")
    print(D.round(2).to_string())
    fig_pi(Z, Ks)
    fig_entry(E, RQ)
    if robust:
        fig_robust(RQ, CX)


if __name__ == "__main__":
    main()
