#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全体整理（2026-10-25）の図。65 の出力（revsuff_*.csv・revsuff_pik.npz）から作る

図1 overview_mix.png: 年ごとの需要と発電量の構成（主の経路、蓄電池なし。実績 FY2024〜25 を並べる）
図2 overview_prices.png: 年ごとの価格（需要加重の平均・昼・夕・夜）と α（主の経路、蓄電池なし）
図3 overview_pi_breakeven.png: 蓄電池の価値 π(K) と、参入の損益分岐（その年に建てる場合の必要収益−容量収入）
図4 overview_entry_path.png: 均衡の量の経路（LTDA の北海道分を含む合計）。変種ごと。OCCTO のエリア配賦（2040年 9,000億kWh ケース 80万kW）を参考に置く
出力: figures/hokkaido/overview_*.png、data/processed/overview_entry_path.csv
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
plt.rcParams["font.family"] = ["Hiragino Sans", "Yu Gothic", "IPAexGothic", "sans-serif"]
plt.rcParams["font.size"] = 11
KAP, P_CAP = 0.861, 14_972.0
INK, MUTED = "#1F2A3A", "#6B7480"
COL = {"原子力": "#7B5EA7", "水力": "#2F6DB5", "地熱・バイオマス": "#5B8C5A", "太陽光": "#E8B33A", "風力": "#7FB3D5",
       "石炭": "#5A5A5A", "LNG": "#D9822B", "石油": "#A0522D", "対象外の火力": "#B8B8B8", "火力（合計）": "#7A7A7A"}

BAL = pd.read_csv(os.path.join(PROC, "revsuff_balance.csv"))
YR = pd.read_csv(os.path.join(PROC, "revsuff_years.csv"))
Z = np.load(os.path.join(PROC, "revsuff_pik.npz"))
K = Z["K"]
MAIN = [k for k in Z.files if k.startswith("主") and k.split("|")[-1] == "2026" and k.count("|") == 1][0].split("|")[0]


# ---------------------------------------------------------------- 図1 電源構成
def fig_mix():
    act = BAL[BAL["系列"] == "実績"].iloc[0]
    rows = [("実績\nFY24〜25", {"原子力": act["原子力"], "水力": act["水力"], "地熱・バイオマス": act["地熱"] + act["バイオマス"],
                              "太陽光": act["太陽光（抑制前）"] - act["抑制"] * 0.5, "風力": act["風力（抑制前）"] - act["抑制"] * 0.5,
                              "火力（合計）": act["火力（合計）"]}, act["需要(TWh)"])]
    for y in (2026, 2028, 2030, 2032, 2035, 2038, 2040):
        r = BAL[(BAL["年"].astype(str) == str(y)) & (BAL["系列"] == "蓄電池なし")].iloc[0]
        sw = r["太陽光（抑制前）"] + r["風力（抑制前）"]
        rows.append((str(y), {"原子力": r["原子力"], "水力": r["水力"], "地熱・バイオマス": r["地熱"] + r["バイオマス"],
                              "太陽光": r["太陽光（抑制前）"] * (1 - r["抑制"] / sw), "風力": r["風力（抑制前）"] * (1 - r["抑制"] / sw),
                              "石炭": r["火力 石炭"], "LNG": r["火力 LNG"], "石油": r["火力 石油"], "対象外の火力": r["対象外の火力"]}, r["需要(TWh)"]))
    fig, ax = plt.subplots(figsize=(11, 5.6))
    order = ["原子力", "水力", "地熱・バイオマス", "風力", "太陽光", "石炭", "LNG", "石油", "対象外の火力", "火力（合計）"]
    x = np.arange(len(rows))
    seen = set()
    for i, (lab, d, dem) in enumerate(rows):
        b = 0.0
        for k in order:
            v = d.get(k, 0.0)
            if v <= 0:
                continue
            ax.bar(i, v, 0.62, bottom=b, color=COL[k], label=k if k not in seen else None, edgecolor="white", linewidth=0.5)
            seen.add(k)
            b += v
        ax.plot([i - 0.36, i + 0.36], [dem, dem], color=INK, lw=2.2, label="需要" if i == 0 else None)
    ax.set_xticks(x, [r[0] for r in rows])
    ax.set_ylabel("TWh/年（気象年 FY2023〜25 の平均）")
    ax.set_title("需要と発電量の構成（主の経路: 2040年 OCCTO 9,000億kWh、泊3 2027・泊1 2032、蓄電池なし）", fontsize=12, color=INK)
    ax.legend(ncol=6, fontsize=9, loc="upper left", frameon=False)
    ax.set_ylim(0, 52)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.text(0.99, 0.01, "発電量と需要の差は、北本の送電・揚水の動力・マストランの最低出力の超過分（北本の受電は明示しない）", ha="right", fontsize=9, color=MUTED)
    fig.savefig(os.path.join(FIG, "overview_mix.png"), dpi=200)


# ---------------------------------------------------------------- 図2 価格と α
def fig_prices():
    b = BAL[BAL["系列"] == "蓄電池なし"].copy()
    b["年"] = b["年"].astype(int)
    act = BAL[BAL["系列"] == "実績"].iloc[0]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    a2 = ax.twinx()
    a2.bar(b["年"], b["α"], color="#E6E2D8", width=0.6, zorder=0)
    a2.set_ylabel("α（過去の上乗せに対する倍率、棒）", color=MUTED)
    a2.set_ylim(0, 12)
    ax.set_zorder(a2.get_zorder() + 1)
    ax.patch.set_visible(False)
    for c, st, col, lab in (("夕17〜21時", "-o", "#D9822B", "夕17〜21時"), ("需要加重の平均価格", "-s", INK, "平均（需要加重）"),
                            ("夜0〜6時", "--", "#2F6DB5", "夜0〜6時"), ("昼10〜15時", "-^", "#E8B33A", "昼10〜15時")):
        ax.plot(b["年"], b[c], st, color=col, ms=4, lw=2, label=lab)
        ax.scatter([2025], [act[c]], color=col, marker="D", s=30, zorder=5)
    ax.text(2025, 2.2, "実績\nFY24〜25", ha="center", fontsize=9, color=MUTED)
    ax.set_xlim(2024.4, 2040.6)
    ax.set_ylim(0, 30)
    ax.set_ylabel("価格（円/kWh、蓄電池なし）")
    ax.set_title("価格の推移: 昼は下がり、夕方は上がる。平均はほぼ横ばい", fontsize=12, color=INK)
    ax.legend(fontsize=9, loc="upper left", frameon=False, ncol=4)
    for s in ("top",):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "overview_prices.png"), dpi=200)


# ---------------------------------------------------------------- 図3 π(K) と損益分岐
def breakeven(year, P=P_CAP):
    """year 年に建てて year+1 年から20年運転する場合に、毎年要る π（円/kW-年）。資本費・廃止費の年額＋運転維持費＋託送等の固定費−容量収入"""
    capex = P4.capex_path(year, "主", 48_000.0)
    return P4.c_req_v5(capex) * 1.06 - KAP * P          # 建設の1年後から運転するので、年額を1年分割り増す（近似）


def fig_pi():
    fig, ax = plt.subplots(figsize=(11, 5.4))
    for y, col in ((2030, "#2F6DB5"), (2035, "#D9822B"), (2040, INK)):
        pi = Z[f"{MAIN}|{y}"]
        ax.plot(K, pi / 1e4, color=col, lw=2.2, label=f"{y}年の π(K)")
        ax.axhline(breakeven(y - 1) / 1e4, color=col, lw=1, ls="--", label=f"{y - 1}年に建てる場合の損益分岐（容量価格14,972円）")
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 3.6)
    ax.set_xlabel("北海道の蓄電池の量 K（万kW、4時間）")
    ax.set_ylabel("蓄電池1kW の年の裁定収入 π（万円/kW-年）")
    ax.set_title("蓄電池の価値は量とともに下がる（カニバリゼーション）。損益分岐と交わる所が均衡の目安", fontsize=12, color=INK)
    ax.legend(fontsize=9, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "overview_pi_breakeven.png"), dpi=200)


# ---------------------------------------------------------------- 図4 均衡の量の経路
def fig_entry():
    ns62 = {"__file__": os.path.join(HERE, "62_entry_path.py"), "__name__": "m62"}
    exec(open(os.path.join(HERE, "62_entry_path.py"), encoding="utf-8").read().split('if __name__ == "__main__":')[0], ns62)
    ns62["K"] = K
    ltda = lambda t: (32.5 if 2029 <= t < 2049 else 0.0) + (20.9 if 2030 <= t < 2050 else 0.0) + (14.0 if 2031 <= t < 2051 else 0.0)

    def path(key_of, P):
        V = {t: Z[key_of(min(t, 2040))] + KAP * P - P4.OM_BASE - P4.NET_FIX for t in range(2026, ns62["HORIZON"] + 1)}
        I = {tau: 4 * P4.capex_path(tau, "主", 48_000.0) * (1 + 0.05 / 1.06 ** 20) for tau in range(2025, ns62["HORIZON"] + 1)}
        return ns62["entry_lp"](V, I, {t: ltda(t) for t in V})[1]

    others = sorted({k.split("|")[0] for k in Z.files if k != "K"})
    nonuc = [p for p in others if p.startswith("原子力なし")][0]
    nohk = [p for p in others if p.startswith("北本")][0]
    occ11 = [p for p in others if p.startswith("2040 は OCCTO 11,000")][0]
    V = [("主（容量価格14,972円）", lambda y: f"{MAIN}|{y}", P_CAP, INK, "-"),
         ("主・α を蓄電池なしの値に固定", lambda y: f"{MAIN}|α固定|{y}", P_CAP, INK, "--"),
         ("主・容量収入なし（蓄電池だけ0円）", lambda y: f"{MAIN}|{y}", 0.0, INK, ":"),
         ("北本の増強を反映しない", lambda y: f"{nohk}|{y}", P_CAP, "#D9822B", "-"),
         ("2040年 OCCTO 11,000億kWh", lambda y: f"{occ11}|{y}", P_CAP, "#7B5EA7", "-"),
         ("原子力なし", lambda y: f"{nonuc}|{y}", P_CAP, "#2F6DB5", "-")]
    out = []
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for lab, kf, P, col, st in V:
        Kt = path(kf, P)
        ys = list(range(2026, 2046))
        ax.plot(ys, [Kt[y] for y in ys], st, color=col, lw=2, label=lab)
        out += [{"変種": lab, "容量価格 P(円/kW)": P, "年": y, "合計(万kW)": Kt[y], "LTDA(万kW)": ltda(y)} for y in ys]
    ys = list(range(2026, 2046))
    ax.fill_between(ys, 0, [ltda(y) for y in ys], color="#E6E2D8", zorder=0, label="LTDA の北海道分（約67万kW、推定を含む）")
    ax.set_xticks(range(2026, 2046, 2))
    ax.plot([2040], [80], "D", color="#C0392B", ms=8)
    ax.text(2040.3, 80, "OCCTO のエリア配賦\n2040年 80万kW（9,000億kWh）", fontsize=9, color="#C0392B", va="center")
    ax.plot([2026.6], [21], "o", color=MUTED, ms=6)
    ax.text(2026.9, 21, "接続済み21万kW（2026年8月末）", fontsize=9, color=MUTED, va="center")
    ax.set_xlim(2026, 2045)
    ax.set_ylim(0, 300)
    ax.set_ylabel("北海道の系統用蓄電池（万kW、LTDA を含む合計）")
    ax.set_title("均衡の量の経路（65、完全予見のコホート自由参入。建設・接続のリードタイムは入れていない）", fontsize=12, color=INK)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "overview_entry_path.png"), dpi=200)
    pd.DataFrame(out).round(2).to_csv(os.path.join(PROC, "overview_entry_path.csv"), index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    fig_mix()
    fig_prices()
    fig_pi()
    fig_entry()
    print("図を保存: figures/hokkaido/overview_mix.png・overview_prices.png・overview_pi_breakeven.png・overview_entry_path.png")
