#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道の蓄電池の均衡モデル（作り直し）の図。analysis/70 の出力（data/processed/eqm_*）から作る

eqm_mix.png 需要と電源構成／eqm_prices.png 価格の推移（2つの価格の作り方）／eqm_shape.png 時刻別の価格の形／
eqm_pi.png 蓄電池の価値と損益分岐／eqm_entry.png 量の経路／eqm_external.png 誘導形の推定との整合／eqm_burden.png 需要家の負担の分解
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, entry as EN, data as DT, balance as B, merit as MO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
plt.rcParams["font.size"] = 11
INK, MUTED, ORANGE, BLUE = "#1F2A3A", "#6B7480", "#C8641B", "#2F6DB5"
COL = {"原子力": "#7B5EA7", "水力": "#2F6DB5", "地熱・バイオマス": "#5B8C5A", "太陽光": "#E8B33A", "風力": "#7FB3D5",
       "石炭": "#5A5A5A", "LNG": "#D9822B", "石油": "#A0522D", "対象外の火力": "#B8B8B8", "火力（合計）": "#7A7A7A"}
Y = pd.read_csv(os.path.join(PROC, "eqm_years.csv"))
Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
K = Z["K"]
MAINP = 14_972.0


def sel(mode, sc="主", Kv=0.0):
    d = Y[(Y["シナリオ"] == sc) & (Y["価格の作り方"] == mode) & (Y["K(万kW)"] == Kv) & (Y["2030年度以降の容量価格"] == MAINP)]
    return d.sort_values("年")


def spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig_mix():
    P = DT.panel()
    q = P[(P.index >= "2024-04-01") & (P.index < "2026-04-01")]
    tw = lambda c: float(q[c].fillna(0).sum() / 2 / 1e6)
    rows = [("実績\nFY24〜25", {"原子力": 0.0, "水力": tw("hydro"), "地熱・バイオマス": tw("geothermal") + tw("biomass"),
                              "太陽光": tw("solar"), "風力": tw("wind"), "火力（合計）": tw("thermal")}, tw("demand"))]
    d = sel("容量回収")
    for y in (2026, 2028, 2030, 2032, 2035, 2038, 2040):
        r = d[d["年"] == y].iloc[0]
        sw = r["太陽光（抑制前）"] + r["風力（抑制前）"]
        k = 1 - r["抑制(TWh)"] / sw
        rows.append((str(y), {"原子力": r["原子力"], "水力": r["水力"], "地熱・バイオマス": r["地熱"] + r["バイオマス"],
                              "太陽光": r["太陽光（抑制前）"] * k, "風力": r["風力（抑制前）"] * k, "石炭": r["火力 石炭"], "LNG": r["火力 LNG"],
                              "石油": r["火力 石油"], "対象外の火力": r["対象外の火力"]}, r["需要(TWh)"]))
    fig, ax = plt.subplots(figsize=(11, 5.6))
    order = ["原子力", "水力", "地熱・バイオマス", "風力", "太陽光", "石炭", "LNG", "石油", "対象外の火力", "火力（合計）"]
    seen = set()
    for i, (lab, dd, dem) in enumerate(rows):
        b = 0.0
        for k_ in order:
            v = dd.get(k_, 0.0)
            if v <= 0:
                continue
            ax.bar(i, v, 0.62, bottom=b, color=COL[k_], label=k_ if k_ not in seen else None, edgecolor="white", linewidth=0.5)
            seen.add(k_)
            b += v
        ax.plot([i - 0.36, i + 0.36], [dem, dem], color=INK, lw=2.2, label="需要" if i == 0 else None)
    ax.set_xticks(range(len(rows)), [r[0] for r in rows])
    ax.set_ylabel("TWh/年（気象年 FY2023〜25 の平均）")
    ax.set_title("需要と発電量の構成（2040年 OCCTO 9,000億kWh、泊3号 2027年10月・1号 2032年、蓄電池なし）", fontsize=12, color=INK)
    ax.legend(ncol=6, fontsize=9, loc="upper left", frameon=False)
    ax.set_ylim(0, 46)
    spines(ax)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.text(0.99, 0.01, "太陽光・風力は抑制後。発電量と需要の差は、北本の送電・揚水の動力。需給の収支は全時間で閉じている", ha="right", fontsize=9, color=MUTED)
    fig.savefig(os.path.join(FIG, "eqm_mix.png"), dpi=200)


def fig_prices():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0), sharey=True)
    for ax, mode in zip(axes, ("スポット回収", "容量回収")):
        d = sel(mode)
        for c, st, col, lab in (("夕17〜21時", "-o", ORANGE, "夕17〜21時"), ("平均価格（需要加重）", "-s", INK, "平均（需要加重）"),
                                ("夜0〜6時", "--", BLUE, "夜0〜6時"), ("昼10〜15時", "-^", "#E8B33A", "昼10〜15時")):
            ax.plot(d["年"], d[c], st, color=col, ms=4, lw=2, label=lab)
        if mode == "スポット回収":
            a2 = ax.twinx()
            a2.bar(d["年"], d["α"], color="#E6E2D8", width=0.6, zorder=0)
            a2.set_ylim(0, 8)
            a2.set_ylabel("上乗せの倍率 α（棒）", color=MUTED)
            ax.set_zorder(a2.get_zorder() + 1)
            ax.patch.set_visible(False)
        ax.set_title(f"{mode}の場合", fontsize=12, color=INK)
        ax.set_ylim(0, 26)
        ax.set_xticks(range(2026, 2041, 2))
        spines(ax)
    axes[0].set_ylabel("価格（円/kWh、蓄電池なし）")
    axes[0].legend(fontsize=9, frameon=False, loc="upper left", ncol=2)
    fig.suptitle("価格の推移（蓄電池なし）: 昼も夕方も下がる。スポット回収の場合は上乗せで夕方の下がり方が小さい", fontsize=13, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_prices.png"), dpi=200)


def fig_shape():
    PRF = pd.read_csv(os.path.join(PROC, "eqm_price_profile.csv"))
    hc = [f"{h}時" for h in range(24)]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0), sharey=True)
    for ax, mode in zip(axes, ("スポット回収", "容量回収")):
        for y, st in zip((2026, 2030, 2035, 2040), ("-", "--", "-.", ":")):
            q = PRF[(PRF["シナリオ"] == "主") & (PRF["価格の作り方"] == mode) & (PRF["年"] == y) & (PRF["K(万kW)"] == 0.0)][hc].mean()
            ax.plot(range(24), q.to_numpy(), st, color=INK, label=f"{y}年")
        q = PRF[(PRF["シナリオ"] == "主") & (PRF["価格の作り方"] == mode) & (PRF["年"] == 2035) & (PRF["K(万kW)"] == 100.0)][hc].mean()
        ax.plot(range(24), q.to_numpy(), "-", color="#A0A8B3", lw=2, label="2035年・蓄電池100万kW")
        ax.set_title(f"{mode}の場合", fontsize=12, color=INK)
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlabel("時刻")
        spines(ax)
    axes[0].set_ylabel("価格（円/kWh、季節の平均）")
    axes[0].legend(fontsize=9, frameon=False)
    fig.suptitle("時刻別の価格の形（蓄電池なし。灰色は蓄電池100万kW を入れた場合）", fontsize=13, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_shape.png"), dpi=200)


def breakeven(year, P=MAINP):
    capex = PR.capex(year)
    crf = PR.WACC * (1 + PR.WACC) ** PR.LIFE / ((1 + PR.WACC) ** PR.LIFE - 1)
    ann = PR.HOURS * capex * (1 + PR.DECOM / (1 + PR.WACC) ** PR.LIFE) * crf * (1 + PR.WACC)
    return ann + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * P


def fig_pi():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0), sharey=True)
    for ax, (mode, key) in zip(axes, (("スポット回収", "spot"), ("容量回収", "capacity"))):
        for y, col in ((2030, BLUE), (2035, ORANGE), (2040, INK)):
            k = f"主|{key}|{MAINP:.0f}|{y}"
            ax.plot(K, Z[k] / 1e4, color=col, lw=2.2, label=f"{y}年の価値")
            ax.axhline(breakeven(y - 1, PR.cap_price(y, MAINP)) / 1e4, color=col, lw=1, ls="--")
        ax.set_title(f"{mode}の場合", fontsize=12, color=INK)
        ax.set_xlim(0, 300)
        ax.set_xlabel("北海道の蓄電池の量（万kW、4時間）")
        spines(ax)
    axes[0].set_ylabel("1kW の年の裁定収入（万円/kW-年）")
    axes[0].legend(fontsize=9, frameon=False)
    fig.suptitle("蓄電池の価値は量とともに下がる。点線は前年に建てる場合の損益分岐（容量価格14,972円）", fontsize=13, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_pi.png"), dpi=200)


def fig_entry():
    years = sorted({int(k.split("|")[3]) for k in Z.files if k != "K"})

    def cur(sc, key):
        return {y: Z[f"{sc}|{key}|{MAINP:.0f}|{y}"] for y in years if f"{sc}|{key}|{MAINP:.0f}|{y}" in Z.files}
    V = [("スポット回収", "主", "spot", INK, "-"), ("容量回収", "主", "capacity", BLUE, "-"),
         ("スポット回収・原子力なし", "原子力なし", "spot", INK, ":"), ("容量回収・原子力なし", "原子力なし", "capacity", BLUE, ":"),
         ("スポット回収・2040年 11,000億kWh", "2040年 11,000億kWh", "spot", "#7B5EA7", "-")]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ys = list(range(2026, 2046))
    ax.fill_between(ys, 0, [EN.ltda_stock(y) for y in ys], color="#E6E2D8", zorder=0, label="長期脱炭素電源オークションの北海道分（約67万kW）")
    for lab, sc, key, col, st in V:
        c = cur(sc, key)
        if len(c) < len(years):
            continue
        Kt = EN.path(c, K, MAINP)
        ax.plot(ys, [Kt[y] for y in ys], st, color=col, lw=2.2, label=lab)
    ax.plot([2040], [80], "D", color="#C0392B", ms=8)
    ax.text(2039.9, 72, "OCCTO のエリア配賦\n2040年 80万kW", fontsize=9, color="#C0392B", va="top", ha="right")
    ax.set_xlim(2026, 2040.5)
    ax.set_xticks(range(2026, 2041, 2))
    ax.set_ylabel("北海道の系統用蓄電池（万kW、合計）")
    ax.set_title("量の経路（容量価格は約定済みの年度は実績、2030年度以降14,972円。2041年以降は量が容量価格にきわめて敏感なので示さない）", fontsize=11, color=INK)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    spines(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_entry.png"), dpi=200)


def fig_external():
    E = pd.read_csv(os.path.join(PROC, "eqm_external_validation.csv"))
    E = E[E["回帰 FY2024〜25（円/kWh per GWh/日）"].notna()]
    lab = (E["要因"].str.replace(" +10%", "", regex=False) + "→" + E["価格"]).tolist()
    x = np.arange(len(E))
    fig, ax = plt.subplots(figsize=(12, 5.0))
    ax.bar(x - 0.27, E["回帰 FY2024〜25（円/kWh per GWh/日）"], 0.27, color="#B8B8B8", yerr=1.96 * E["回帰 FY2024〜25 の標準誤差"], capsize=3,
           label="過去データの回帰（FY2024〜25、日次、年月・曜日の固定効果、95%区間）")
    ax.bar(x, E["構造モデル（円/kWh per GWh/日）"], 0.27, color=ORANGE, label="構造モデル（主: 東北の価格は過去の実績のまま）")
    if "構造モデル・東北の価格が連動する版" in E:
        ax.bar(x + 0.27, E["構造モデル・東北の価格が連動する版"], 0.27, color=BLUE, label="構造モデル（頑健性の確認: 東北の価格が北海道の再エネに連動）")
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(x, lab, fontsize=10)
    ax.set_ylabel("価格の変化（円/kWh、1日1GWh の増加あたり）")
    ax.set_title("誘導形の推定との整合: 向きは合う。主のモデルの大きさは回帰の約3〜5割（東北の価格を固定しているため）", fontsize=12, color=INK)
    ax.legend(fontsize=9, frameon=False)
    spines(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_external.png"), dpi=200)


def fig_link():
    L = pd.read_csv(os.path.join(PROC, "eqm_link_calibration.csv"))
    L = L[L["北海道へ受けられる量(MW)"] == 900.0]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    x = np.arange(len(L))
    for c, col, lab in (("R² 推定期間", INK, "推定期間"), ("R² FY2023", BLUE, "FY2023"), ("R² FY2026 4〜6月", ORANGE, "FY2026 4〜6月")):
        axes[0].plot(x, L[c], "-o", color=col, label=lab)
    axes[0].set_xticks(x, L["東北へ送れる量"], fontsize=9)
    axes[0].set_ylabel("価格の R²")
    axes[0].set_title("価格の当てはまり", fontsize=11, color=INK)
    axes[0].legend(fontsize=9, frameon=False)
    for c, col, lab in (("流れの平均", INK, "平均"), ("昼の流れ", "#E8B33A", "昼10〜15時"), ("夕の流れ", ORANGE, "夕17〜21時")):
        axes[1].plot(x, L[f"{c} モデル"], "-o", color=col, label=f"モデル {lab}")
        axes[1].axhline(L[f"{c} 実績"].iloc[0], color=col, ls="--", lw=1)
    axes[1].set_xticks(x, L["東北へ送れる量"], fontsize=9)
    axes[1].set_ylabel("北本の流れ（MW、＋は東北へ）。点線は実績")
    axes[1].set_title("北本の流れ（推定期間 FY2024〜25）", fontsize=11, color=INK)
    axes[1].legend(fontsize=8, frameon=False)
    for a in axes:
        spines(a)
    fig.suptitle("連系線で東北へ送れる量の較正（北海道へ受けられる量は900MW）。主は運用容量×0.65", fontsize=12, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_link.png"), dpi=200)


def fig_burden():
    T = pd.read_csv(os.path.join(PROC, "eqm_burden_split.csv"))
    T = T[T["シナリオ"] == "主"]
    parts = [("うち火力（要件の対象）", "火力（要件の対象）＝不足額 M にほぼ等しい", "#7A7A7A"),
             ("うち火力（対象外・LTDA など）", "火力（LTDA・対象外）", "#B8B8B8"), ("うち原子力", "原子力", "#7B5EA7"),
             ("うち水力", "水力", "#2F6DB5"), ("うち FIT/FIP の電源（戻る分の上限）", "FIT/FIP の電源（賦課金の減少で戻る）", "#E8B33A"),
             ("うち揚水・蓄電池・北本ほか", "揚水・蓄電池・北本ほか", "#D9D4C7")]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    x = np.arange(len(T))
    b = np.zeros(len(T))
    for c, lab, col in parts:
        v = T[c].to_numpy()
        ax.bar(x, v, 0.55, bottom=b, color=col, label=lab, edgecolor="white", linewidth=0.5)
        b += v
    ax.plot(x, T["需要家の正味の負担の差(億円/年)"], "D", color=ORANGE, ms=9, label="需要家の正味の負担の差（FIT/FIP で戻る分と M を引いた値）")
    ax.set_xticks(x, [f"{int(y)}年" for y in T["年"]])
    ax.set_ylabel("スポットの約定総額の差（億円/年）")
    ax.set_title("スポット回収の場合の約定総額の増分は誰に渡るか（容量回収の場合との差、蓄電池は先に入っている量）", fontsize=12, color=INK)
    ax.legend(fontsize=9, frameon=False, loc="upper left")
    spines(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_burden.png"), dpi=200)


def fig_merit():
    """2035年（主、蓄電池なし）の5月の平日の昼12時と夕方19時のメリットオーダー。燃料費0の電源・必ず動く火力・燃料費の順の火力と、需要・東北の価格・連系線"""
    y = 2035
    sc = PR.SCENARIOS["主"]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    units = B.fleet(y)
    R = MO.dispatch(I, units)
    days = I["days"]
    cand = [i for i, d in enumerate(days) if d.month == 5 and d.weekday() < 5 and d.year == 2025]
    i = cand[len(cand) // 2]
    on, cap = MO.commit(I, units, np.zeros_like(I["D"]), np.zeros_like(I["D"]))
    nr = MO.normal_min_ratio()
    vc = I["vc_fn"](units)
    E, M = I["link"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), sharey=True)
    O = B.other_profile()[I["month"], np.arange(24)[None, :]]
    for ax, h, lab in zip(axes, (12, 19), ("昼12時", "夕方19時")):
        zero = {"原子力": I["N"][i, h], "水力・揚水": I["Hy"][i, h] + I["pump"][i, h], "地熱・バイオマス": I["G"][i, h] + I["Bm"][i, h],
                "対象外の火力": O[i, h], "風力": I["W"][i, h], "太陽光": I["S"][i, h]}
        x = 0.0
        for k_, v in zero.items():
            ax.add_patch(plt.Rectangle((x, 0), v, 0.4, color=COL.get(k_, "#9AA6B4") if k_ != "水力・揚水" else COL["水力"], alpha=0.9))
            if v > 150:
                ax.text(x + v / 2, 0.9, k_, ha="center", fontsize=8, rotation=90, color=INK)
            x += v
        mins = []
        flex = []
        for j, u in enumerate(units):
            if not on[i, j]:
                continue
            c = cap[i, h, j]
            nm = 0.0 if u[5] else min(max(nr.get(u[0], u[3] / u[2]), u[3] / u[2]) * c, c)
            mins.append((u[0], nm))
            flex.append((u[0], c - nm, vc[i, h, j]))
        for nme, nm in mins:
            ax.add_patch(plt.Rectangle((x, 0), nm, 0.4, color="#5A5A5A", alpha=0.6))
            x += nm
        ax.text(x - 10, 1.6, "必ず動く火力\n（通常時の最低出力）", ha="right", fontsize=8, color=MUTED)
        for nme, w, v in sorted(flex, key=lambda t: t[2]):
            ax.add_patch(plt.Rectangle((x, 0), w, v, facecolor=COL["石炭"] if v < 9.5 else (COL["LNG"] if v < 15 else COL["石油"]), alpha=0.8, edgecolor="white"))
            ax.text(x + w / 2, v + 0.4, nme, ha="center", fontsize=7, rotation=90, color=INK)
            x += w
        D = I["D"][i, h]
        pT = I["pT"][i, h]
        ax.axvline(D, color=INK, lw=2)
        ax.text(D, 27, f" 需要 {D:,.0f}MW", fontsize=9, color=INK)
        ax.axhline(pT, color=BLUE, lw=1.5, ls="--")
        ax.text(80, pT + 0.5, f"東北の価格 {pT:.1f}円（東北へ {E:,.0f}MW・北海道へ {M:,.0f}MW まで売買）", fontsize=8, color=BLUE)
        pp = R["p0"][i, h]
        ax.set_title(f"{lab}: 価格 {pp:.2f}円、北本 {R['X'][i, h]:+,.0f}MW（＋は東北へ）" if pp < 1 else f"{lab}: 価格 {pp:.1f}円、北本 {R['X'][i, h]:+,.0f}MW（＋は東北へ）", fontsize=11, color=INK)
        ax.set_xlim(0, x * 1.02)
        ax.set_ylim(0, 30)
        ax.set_xlabel("供給の量（MW）")
        spines(ax)
    axes[0].set_ylabel("燃料費（円/kWh）")
    d0 = days[i]
    fig.suptitle(f"将来のメリットオーダーの例（2035年、気象年 FY{d0.year - (d0.month < 4)} の{d0.month}月{d0.day}日、蓄電池なし）\n"
                 "燃料費0の電源と必ず動く火力だけで需要を超えると、東北へ送れるだけ送り、北海道の価格は東北から切り離される", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_merit.png"), dpi=200)



def fig_battery_energy():
    """蓄電池が避けた抑制の量と、減った火力の発電量（主の前提＝要らない火力は退出、容量回収、容量価格14,972円）。蓄電池なしとの差"""
    mode = "容量回収（要らない火力は退出）"
    if "蓄電池が避けた抑制(TWh)" not in Y.columns or not (Y["価格の作り方"] == mode).any():
        print("蓄電池の電力量の図: 列か行がないので省く")
        return
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for ax, (col, ttl) in zip(axes, [("蓄電池が避けた抑制(TWh)", "蓄電池が避けた再エネの抑制"), ("減った火力の発電量(TWh)", "減った火力の発電量")]):
        for Kv, c in ((50.0, BLUE), (100.0, ORANGE)):
            d = sel(mode, Kv=Kv)
            ax.bar(d["年"] + (-0.2 if Kv == 50.0 else 0.2), d[col], width=0.4, color=c, label=f"蓄電池 {Kv:.0f}万kW")
        ax.set_title(ttl, fontsize=12, color=INK)
        ax.set_xlabel("年")
        spines(ax)
    axes[0].set_ylabel("TWh/年（蓄電池なしとの差）")
    axes[0].legend(fontsize=9, frameon=False, loc="upper left")
    fig.suptitle("蓄電池の電力量の効果: 抑制されていた再エネを夕方に回し、その分の火力の発電を減らす（容量回収、要らない火力は退出）", fontsize=12, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "eqm_battery_energy.png"), dpi=150)
    plt.close(fig)
    Y[(Y["シナリオ"] == "主") & (Y["2030年度以降の容量価格"] == MAINP) & Y["K(万kW)"].isin([50.0, 100.0])
      & Y["価格の作り方"].isin([mode, "すべてスポット（要らない火力は退出）", "スポット回収（要らない火力は退出）"])][
        ["価格の作り方", "年", "K(万kW)", "抑制(TWh)", "蓄電池が避けた抑制(TWh)", "火力の発電量 合計(TWh)", "減った火力の発電量(TWh)"]
    ].sort_values(["価格の作り方", "年", "K(万kW)"]).to_csv(os.path.join(PROC, "eqm_battery_energy.csv"), index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    for f in (fig_mix, fig_prices, fig_shape, fig_pi, fig_entry, fig_external, fig_burden, fig_merit, fig_link, fig_battery_energy):
        f()
    print("図を保存: figures/hokkaido/eqm_*.png")
