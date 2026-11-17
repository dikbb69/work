# -*- coding: utf-8 -*-
"""プレ報告会（2026-12-07）のスライド用の図。

  python presentation/pre_20261207/make_figures.py        （thesis/ で実行）

出力: presentation/pre_20261207/fig/pre_*.png
  pre_hourly.png   2040年度の時刻別の平均価格（2つの回収方法、蓄電池100万kW）
  pre_path.png     普及均衡点の経路（2026〜40年度）
  pre_mix.png      電源を1つだけ動かしたときの2040年度の普及均衡点
  pre_robust.png   前提を1つずつ変えたときの2040年度の量（表C.1）
入力: data/processed/v2_hourly_price_by_rule.csv, v2_table63.csv, simple_source_scenarios.csv
図の中の文字は、スライド上で24px 以上になる大きさにしてある（図の幅1インチ＝スライドの100px）。
書体は Noto Sans CJK JP（なければ IPA Pゴシック）。
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(HERE, "fig")
os.makedirs(OUT, exist_ok=True)

have = {f.name for f in font_manager.fontManager.ttflist}
FONT = next((f for f in ("Noto Sans CJK JP", "Hiragino Sans", "IPAPGothic") if f in have), "sans-serif")
plt.rcParams["font.family"] = FONT
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE = "#2a78d6", "#eb6834"          # スポット回収、燃料費入札
INK, MUTED, GRID, GREY, PAPER, BAND = "#2B3440", "#5B6472", "#E1E5EA", "#8A919C", "#FAFAF7", "#EDF0F4"
STOCK = 98.8
DPI = 200


def px(v):
    """スライド上の px → 図の中の pt（図の幅1インチ＝スライドの100px）"""
    return v * 0.72


def style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.spines["bottom"].set_linewidth(px(1.5))
    ax.tick_params(axis="both", colors=MUTED, labelsize=px(24), length=0, pad=px(8))
    ax.grid(axis="y", color=GRID, lw=px(1.5))
    ax.set_axisbelow(True)
    ax.set_facecolor(PAPER)


def line(ax, x, y, col, label=None, marker=True):
    ax.plot(x, y, color=col, lw=px(4), solid_capstyle="round", solid_joinstyle="round", label=label,
            marker="o" if marker else None, ms=px(13), mec=PAPER, mew=px(2.5), zorder=3)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=DPI, facecolor=PAPER)
    plt.close(fig)
    print(name)


# ------------------------------------------------------------------ 1. 時刻別の平均価格
def fig_hourly():
    H = pd.read_csv(os.path.join(PROC, "v2_hourly_price_by_rule.csv"))
    H = H[(H["年"] == 2040) & (H["K(万kW)"] == 100)]
    a = H[H["回収方法"] == "スポット回収"].sort_values("時刻")
    b = H[H["回収方法"] == "燃料費入札"].sort_values("時刻")
    fig, ax = plt.subplots(figsize=(10.0, 5.9))
    fig.subplots_adjust(left=0.085, right=0.80, top=0.90, bottom=0.14)
    chg = sorted(a.nlargest(5, "充電(MW)")["時刻"])
    dis = sorted(a.nlargest(5, "放電(MW)")["時刻"])
    for hrs, lab in ((chg, "蓄電池が充電"), (dis, "蓄電池が放電")):
        ax.axvspan(min(hrs) - 0.5, max(hrs) + 0.5, color=BAND, zorder=0)
        ax.text((min(hrs) + max(hrs)) / 2, 13.25, lab, ha="center", va="center", fontsize=px(24), color=MUTED)
    line(ax, a["時刻"], a["価格(円/kWh)"], BLUE, "スポット回収")
    line(ax, b["時刻"], b["価格(円/kWh)"], ORANGE, "燃料費入札")
    pa, pb = a.set_index("時刻")["価格(円/kWh)"], b.set_index("時刻")["価格(円/kWh)"]
    for h in (12, 19):
        ax.annotate("", xy=(h, pa[h] - 0.25), xytext=(h, pb[h] + 0.25),
                    arrowprops=dict(arrowstyle="<->", color=INK, lw=px(2), shrinkA=0, shrinkB=0))
    ax.text(12, pb[12] - 0.55, f"差は約{pa[12] - pb[12]:.0f}円", fontsize=px(25), color=INK, va="top", ha="center")
    ax.text(19.45, (pa[19] + pb[19]) / 2, f"差は約{pa[19] - pb[19]:.0f}円", fontsize=px(25), color=INK, va="center", ha="left")
    ax.text(23.6, pa[23], "スポット回収", fontsize=px(26), color=INK, va="center", ha="left", fontweight="bold")
    ax.text(23.6, pb[23], "燃料費入札", fontsize=px(26), color=INK, va="center", ha="left", fontweight="bold")
    ax.set_xlim(-0.6, 23.4)
    ax.set_ylim(0, 14)
    ax.set_yticks([0, 4, 8, 12])
    ax.set_xticks([0, 6, 12, 18, 23])
    ax.set_xticklabels(["0時", "6時", "12時", "18時", "23時"])
    ax.text(-0.6, 14.9, "平均価格（円/kWh）", fontsize=px(24), color=MUTED, ha="left", va="bottom")
    style(ax)
    save(fig, "pre_hourly.png")
    return float(pa[12] - pb[12]), float(pa[19] - pb[19]), chg, dis


# ------------------------------------------------------------------ 2. 普及均衡点の経路
def fig_path():
    T = pd.read_csv(os.path.join(PROC, "v2_table63.csv"))
    T = T[(T["シナリオ"] == "主") & (T["年"] <= 2040)]
    col = "採算が合う量 K*(万kW)"
    a = T[T["場合"] == "スポットで回収（主）"].sort_values("年")
    b = T[T["場合"] == "すべて市場外"].sort_values("年")
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    fig.subplots_adjust(left=0.085, right=0.745, top=0.90, bottom=0.14)
    ax.step(a["年"], np.minimum(a["経路の量(万kW)"], STOCK), where="mid", color=GREY, lw=px(3), zorder=2)
    line(ax, a["年"], a[col], BLUE, "スポット回収")
    line(ax, b["年"], b[col], ORANGE, "燃料費入札")
    ya, yb = float(a[col].iloc[-1]), float(b[col].iloc[-1])
    ax.text(2040.5, ya, f"スポット回収\n{ya:.0f}万kW", fontsize=px(27), color=INK, va="center", ha="left", fontweight="bold", linespacing=1.35)
    ax.text(2040.5, yb, f"燃料費入札\n{yb:.0f}万kW", fontsize=px(27), color=INK, va="center", ha="left", fontweight="bold", linespacing=1.35)
    ax.text(2026.0, STOCK + 7, "既設と LTDA の落札分（98.8万kW）", fontsize=px(24), color=MUTED, ha="left", va="bottom")
    ax.set_xlim(2025.5, 2040.3)
    ax.set_ylim(0, 230)
    ax.set_yticks([0, 50, 100, 150, 200])
    ax.set_xticks([2026, 2030, 2035, 2040])
    ax.set_xticklabels(["2026", "2030", "2035", "2040年度"])
    ax.text(2025.5, 245, "蓄電池の量（万kW）", fontsize=px(24), color=MUTED, ha="left", va="bottom")
    style(ax)
    save(fig, "pre_path.png")
    return ya, yb


# ------------------------------------------------------------------ 3. 電源構成
def fig_mix():
    S = pd.read_csv(os.path.join(PROC, "simple_source_scenarios.csv"))
    D = S[S["年"] == 2040]
    name = {"スポット回収": "スポットで回収（主）", "燃料費入札": "すべて市場外"}
    units = {"なし": 0, "3号だけ": 1, "3号＋1号": 2, "3基": 3}
    ycol = "市場だけで入る量(万kW)"
    fig, axes = plt.subplots(1, 3, figsize=(16.64, 5.0), sharey=True)
    fig.subplots_adjust(left=0.055, right=0.905, top=0.83, bottom=0.17, wspace=0.09)
    out = {}
    for ax, g in zip(axes, ("太陽光", "風力", "原子力")):
        for lab, c in (("スポット回収", BLUE), ("燃料費入札", ORANGE)):
            d = D[(D["場合"] == name[lab]) & D["動かす電源"].isin([g, "主"])].copy()
            d["x"] = d["泊"].map(units) if g == "原子力" else d[f"{g}(万kW)"]
            d = d.sort_values("x")
            line(ax, d["x"], d[ycol], c, lab)
            out[(g, lab)] = list(zip(d["x"].round(0), d[ycol].round(1)))
            if lab == "スポット回収":
                m = d[d["動かす電源"] == "主"].iloc[0]
                ax.annotate("基準", (m["x"], m[ycol]), xytext=(0, px(20)), textcoords="offset points", ha="center", va="bottom",
                            fontsize=px(24), color=MUTED)
        ax.axhline(STOCK, color=GREY, lw=px(2), zorder=1)
        ax.set_ylim(0, 290)
        ax.set_yticks([0, 100, 200])
        if g == "原子力":
            ax.set_xticks([0, 1, 2, 3])
            ax.set_xticklabels(["0基", "1基", "2基", "3基"])
            ax.set_xlim(-0.3, 3.3)
            title = "原子力（泊発電所の基数）"
        elif g == "太陽光":
            ax.set_xticks([250, 500, 750])
            ax.set_xticklabels(["250", "500", "750"])
            ax.set_xlim(200, 860)
            title = "太陽光の設備（万kW）"
        else:
            ax.set_xticks([300, 600, 900, 1200])
            ax.set_xticklabels(["300", "600", "900", "1,200"])
            ax.set_xlim(80, 1300)
            title = "風力の設備（万kW）"
        ax.set_title(title, loc="left", fontsize=px(27), color=INK, fontweight="bold", pad=px(16))
        style(ax)
    axes[1].text(100, STOCK - 7, "既設と LTDA の落札分", fontsize=px(24), color=MUTED, ha="left", va="top")
    axes[0].set_ylabel("2040年度の普及均衡点（万kW）", fontsize=px(24), color=MUTED, labelpad=px(10))
    x1 = axes[2].get_xlim()[1]
    d2 = D[(D["動かす電源"].isin(["原子力", "主"]))]
    ya = float(d2[(d2["場合"] == name["スポット回収"]) & (d2["泊"] == "3基")][ycol].iloc[0])
    yb = float(d2[(d2["場合"] == name["燃料費入札"]) & (d2["泊"] == "3基")][ycol].iloc[0])
    axes[2].text(3.22, ya, "スポット回収", fontsize=px(26), color=INK, va="center", ha="left", fontweight="bold", clip_on=False)
    axes[2].text(3.22, yb, "燃料費入札", fontsize=px(26), color=INK, va="center", ha="left", fontweight="bold", clip_on=False)
    save(fig, "pre_mix.png")
    return out


# ------------------------------------------------------------------ 4. 頑健性（表C.1）
ROBUST = [  # (前提, スポット回収, 燃料費入札)。提出版の表C.1 の値（2040年度の設置量、万kW）
    ("基準シナリオ", 202.1, 132.7),
    ("東北の価格が北海道の再エネに連動", 368.4, 207.7),
    ("上乗せを燃料費に比例", 246.2, 132.7),
    ("燃料費 +20%", 231.1, 165.7),
    ("燃料費 −20%", 160.0, 98.8),
    ("需要が少ないケース", 234.3, 98.8),
    ("マストランなし", 174.0, 146.9),
    ("建設費の低下が速い", 349.3, 303.3),
    ("建設費の低下が遅い", 98.8, 98.8),
    ("調整係数を量に応じて下げる", 124.5, 98.8),
    ("寿命15年", 133.9, 98.8),
    ("割引率4%", 262.1, 203.1),
    ("割引率8%", 142.6, 98.8),
    ("実現率0.70", 161.4, 98.8),
    ("実現率0.90", 222.0, 152.8),
]


def fig_robust():
    n = len(ROBUST)
    fig, ax = plt.subplots(figsize=(10.2, 6.6))
    fig.subplots_adjust(left=0.40, right=0.975, top=0.90, bottom=0.11)
    for i, (lab, a, b) in enumerate(ROBUST):
        y = n - 1 - i
        ax.plot([b, a], [y, y], color=GREY, lw=px(3), solid_capstyle="round", zorder=2)
        ax.plot(b, y, "o", color=ORANGE, ms=px(15), mec=PAPER, mew=px(2.5), zorder=3)
        ax.plot(a, y, "o", color=BLUE, ms=px(15), mec=PAPER, mew=px(2.5), zorder=4)
        ax.text(-12, y, lab, ha="right", va="center", fontsize=px(24), color=INK, fontweight="bold" if i == 0 else "normal")
    ax.axvline(STOCK, color=GREY, lw=px(1.5), zorder=1)
    ax.text(STOCK, n - 0.2, "既設と LTDA", ha="center", va="bottom", fontsize=px(22), color=MUTED)
    ax.plot([], [], "o", color=ORANGE, ms=px(15), label="燃料費入札")
    ax.plot([], [], "o", color=BLUE, ms=px(15), label="スポット回収")
    ax.legend(loc="lower right", frameon=False, fontsize=px(24), labelcolor=INK, handletextpad=0.3, borderaxespad=0.2)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlim(0, 390)
    ax.set_xticks([0, 100, 200, 300])
    ax.set_xticklabels(["0", "100", "200", "300万kW"])
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.spines["bottom"].set_linewidth(px(1.5))
    ax.tick_params(axis="x", colors=MUTED, labelsize=px(24), length=0, pad=px(8))
    ax.grid(axis="x", color=GRID, lw=px(1.5))
    ax.set_axisbelow(True)
    ax.set_facecolor(PAPER)
    save(fig, "pre_robust.png")


if __name__ == "__main__":
    print("font:", FONT)
    print(fig_hourly())
    print(fig_path())
    r = fig_mix()
    for k, v in r.items():
        print(k, v)
    fig_robust()
