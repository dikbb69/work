#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""4.2節 図「価格の決まり方」の模式図（上乗せ前の価格 p0_h と、x_h・連系線の流れの関係）

式(4.2)の5つの場合を、横軸 x_h（火力が最低出力を超えて出す必要がある量）、縦軸 価格 の階段として描く。
下段に東北との連系線の流れ（東北向きを正）を並べ、どの区間で連系線が上限に張り付くかを示す。
数値は形を見せるための仮の値（E=1, Δ=1, G<=1.9, M=1.2、燃料費の並び）で、実データではない。
出力: figures/hokkaido/price_regime_schematic.png（と .svg）
"""
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo", "IPAGothic"]
plt.rcParams["mathtext.fontset"] = "cm"
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures", "hokkaido")
INK, GRAY, LIGHT = "#1f1f1f", "#595959", "#8c8c8c"
LINE = "#1f4e79"
BANDS = ["#f2f2f2", "#ffffff"]
FS_ANN, FS_LAB, FS_REG = 8, 9, 8

# ---------------------------------------------------------------- 仮の値（形を見せるため）
E, DELTA, G_LT, M = 1.0, 1.0, 1.9, 1.2
P_FLOOR, F_MIN, P_T, P_CAP = 0.3, 4.0, 9.0, 19.0      # 0.01 円は見やすさのため少し持ち上げて描く
X_LO, X_HI = -3.1, 4.6
# 最低出力を超える出力を燃料費の安い順に積んだ階段（累積量 q の区切り, 燃料費）。q=G< で東北の価格を超える
MERIT = [(0.0, F_MIN), (0.7, 6.0), (1.3, 7.5), (G_LT, 11.0), (2.6, 13.5), (3.2, 17.0)]
T1, T2, T3, T4 = -E - DELTA, -E, G_LT - E, G_LT + M


def lam(q):
    v = MERIT[0][1]
    for q0, c in MERIT:
        if q >= q0 - 1e-12:
            v = c
    return v


def price(x):
    if x < T1:
        return P_FLOOR
    if x < T2:
        return min(F_MIN, P_T)
    if x < T3:
        return lam(x + E)
    if x < T4:
        return P_T
    return lam(x - M)


def flow(x):            # 東北向きを正
    if x < T3:
        return E
    if x < T4:
        return G_LT - x
    return -M


def step_xy(f, lo, hi, n=4000):
    """不連続点で縦線を描かないよう、値が跳ぶところで NaN を挟む"""
    xs, ys = [], []
    prev = None
    for i in range(n + 1):
        x = lo + (hi - lo) * i / n
        y = f(x)
        if prev is not None and abs(y - prev) > 0.05 * (P_CAP if f is price else 1) and f is price:
            xs.append(x)
            ys.append(float("nan"))
        xs.append(x)
        ys.append(y)
        prev = y
    return xs, ys


fig, (ax, axf) = plt.subplots(2, 1, figsize=(6.3, 4.6), sharex=True, gridspec_kw={"height_ratios": [3.2, 1.25], "hspace": 0.08})
edges = [X_LO, T1, T2, T3, T4, X_HI]
labels = ["①再エネを\n出力制御", "②火力などを\n下げて吸収", "③東北向きが\n混雑", "④東北と\n同じ価格", "⑤北海道向き\nが混雑"]
for k in range(5):
    for a in (ax, axf):
        a.axvspan(edges[k], edges[k + 1], color=BANDS[k % 2], zorder=0, lw=0)
    ax.text((edges[k] + edges[k + 1]) / 2, P_CAP + 0.6, labels[k], ha="center", va="bottom", fontsize=FS_REG, color=INK, linespacing=1.25)
for t in (T1, T2, T3, T4):
    for a in (ax, axf):
        a.axvline(t, color=LIGHT, lw=0.7, ls=(0, (3, 2)), zorder=1)

# 価格の階段
xs, ys = step_xy(price, X_LO, X_HI)
ax.plot(xs, ys, color=LINE, lw=2.0, zorder=3, solid_capstyle="butt")
# 東北の価格の参照線
ax.axhline(P_T, color=GRAY, lw=0.6, ls=":", zorder=2)

# 区間ごとの価格の式（直接ラベル）
ax.text((T1 + T2) / 2 + 0.06, F_MIN - 0.5, r"$\min\{f_h,\ p^T_h\}$", ha="center", va="top", fontsize=FS_ANN + 0.5, color=INK)
ax.text(T2 + 0.06, F_MIN + 0.55, r"$\lambda_h(x_h+E)$", ha="left", va="bottom", fontsize=FS_ANN + 0.5, color=INK)
ax.text((T3 + T4) / 2, P_T + 0.5, r"$p^T_h$（東北の価格）", ha="center", va="bottom", fontsize=FS_ANN, color=INK)
ax.text(T4 + 0.08, 15.2, r"$\lambda_h(x_h-M)$", ha="left", va="bottom", fontsize=FS_ANN + 0.5, color=INK)
ax.text(T4 + 0.08, 14.9, "（上限200円/kWh）", ha="left", va="top", fontsize=FS_ANN - 0.5, color=GRAY)

ax.set_ylim(0, P_CAP)
ax.set_yticks([P_FLOOR, F_MIN, P_T])
ax.set_yticklabels(["0.01", r"$f_h$", r"$p^T_h$"], fontsize=FS_LAB)
ax.set_ylabel(r"上乗せ前の価格 $p^0_h$", fontsize=FS_LAB, color=GRAY)

# 連系線の流れ
xs, ys = step_xy(flow, X_LO, X_HI)
axf.plot(xs, ys, color=LINE, lw=2.0, zorder=3)
axf.axhline(0, color=GRAY, lw=0.6, zorder=2)
axf.text((X_LO + T3) / 2, E - 0.12, "東北へ上限 $E$ まで送電", ha="center", va="top", fontsize=FS_ANN, color=INK)
axf.text((T4 + X_HI) / 2, -M + 0.12, "東北から上限 $M$\nまで受電", ha="center", va="bottom", fontsize=FS_ANN, color=INK, linespacing=1.2)
axf.set_ylim(-M - 0.35, E + 0.35)
axf.set_yticks([E, 0, -M])
axf.set_yticklabels([r"$E$", "0", r"$-M$"], fontsize=FS_LAB)
axf.set_ylabel("連系線の流れ\n（東北向き＋）", fontsize=FS_LAB, color=GRAY, linespacing=1.2)

axf.set_xlim(X_LO, X_HI)
axf.set_xticks([T1, T2, 0, T3, T4])
axf.set_xticklabels([r"$-E-\Delta_h$", r"$-E$", "0", r"$G^<_h-E$", r"$G^<_h+M$"], fontsize=FS_LAB)
axf.set_xlabel(r"$x_h$（火力が最低出力を超えて出す必要がある量）", fontsize=FS_LAB, color=GRAY, labelpad=4)
fig.text(0.13, 0.005, "← 電気が余る", fontsize=FS_ANN, color=GRAY, ha="left", va="bottom")
fig.text(0.97, 0.005, "電気が足りない →", fontsize=FS_ANN, color=GRAY, ha="right", va="bottom")

for a in (ax, axf):
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        a.spines[s].set_color(LIGHT)
    a.tick_params(colors=GRAY, length=3, width=0.6)
ax.tick_params(axis="x", length=0)

fig.subplots_adjust(left=0.13, right=0.97, top=0.86, bottom=0.15)
os.makedirs(FIGDIR, exist_ok=True)
for ext in ("png", "svg"):
    fig.savefig(os.path.join(FIGDIR, f"price_regime_schematic.{ext}"), dpi=300)
print("saved:", os.path.join(FIGDIR, "price_regime_schematic.png"))
