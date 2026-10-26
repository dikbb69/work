#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""容量価格と蓄電池の量の関係（蓄電池の「供給曲線」）。容量価格はモデルで導かず、水準を外から与えて読む（著者の提案 2026-10-23）

容量価格 P（円/kW、北海道エリアの約定価格）を K と年によらず一定と置き、蓄電池の容量収入を κ×P（κ＝0.861、2030年度向けの北海道
4時間の調整係数の月別の平均）とする。2030年度向けの規則では、指標価格以下で応札した電源の約定価格は指標価格（Net CONE 20,911円）で
頭打ちになるので、低く応札する蓄電池の収入は κ×min(P, 20,911) と注記する（ここでは P をそのまま使い、20,911円を縦線で示す）。
各 P で、62 のコホートの自由参入均衡を解き、最初の参入年と2035・2040年の量を読む。あわせて、目標の量に要る P を逆算する。
外挿の基準（OCCTO メインオークションの約定結果の北海道エリアの価格）:
  2024年度向け14,137、2025年度向け5,242、2026年度向け8,749、2027年度向け13,287、2028年度向け14,812、2029年度向け14,972円/kW。
  2030年度向けの指標価格（Net CONE）20,911円、上限価格31,366.5円（OCCTO 2026/7/30）。
補助との比較: 資本費の補助（SII の補助率1/3・1/2、上限額は無視）で同じ量を得る場合の財政の負担と比べる。
出力: data/processed/capacity_price_supply.csv、capacity_price_required.csv、capacity_vs_subsidy.csv、figures/hokkaido/capacity_price_supply.png
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

ns = {"__file__": os.path.join(HERE, "62_entry_path.py"), "__name__": "m62"}
exec(open(os.path.join(HERE, "62_entry_path.py"), encoding="utf-8").read().split('if __name__ == "__main__":')[0], ns)
Z, K, entry_lp, YEARS, HORIZON, LAG = ns["Z"], ns["K"], ns["entry_lp"], ns["YEARS"], ns["HORIZON"], ns["LAG"]
PATHS = ns["PATHS"]
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
KAP = 0.861
ANCHORS = {"2025年度向け（最低）": 5_242.0, "6回の平均（2024〜2029年度向け）": 11_867.0, "2029年度向け（最新）": 14_972.0,
           "2030年度向けの指標価格（Net CONE）": 20_911.0, "2030年度向けの上限価格": 31_366.5}


def solve_p(path, design, P, cap="主", start=48_000.0, subsidy=0.0, wacc=None):
    V = {}
    for t in range(YEARS[0], HORIZON + 1):
        pi = Z[f"{path}|{design}|{min(t, YEARS[-1])}"]
        V[t] = pi + KAP * P - P4.OM_BASE - P4.NET_FIX
    I_tau = {tau: 4 * P4.capex_path(tau, cap, start) * (1 + 0.05 / 1.06 ** 20) * (1 - subsidy) for tau in range(YEARS[0] - LAG, HORIZON + 1)}
    if wacc is not None:
        ns["WACC"] = wacc
    k, Kt = entry_lp(V, I_tau)
    ns["WACC"] = 0.06
    first = next((t for t in sorted(Kt) if Kt[t] > 0.5), None)
    return first, Kt, k


def required_p(path, design, target, year=2040, **kw):
    lo, hi = 0.0, 60_000.0
    if solve_p(path, design, hi, **kw)[1][year] < target:
        return np.nan
    for _ in range(24):
        mid = (lo + hi) / 2
        if solve_p(path, design, mid, **kw)[1][year] >= target:
            hi = mid
        else:
            lo = mid
    return hi


if __name__ == "__main__":
    MAIN = PATHS[0]
    DES = ["現行", "効率＋炭素", "歪み（余剰の全時間 −10円）"]
    PGRID = np.arange(0, 32_001, 1_000.0)
    rows = []
    for path in [MAIN, "2040 の太陽光はエネ基の倍率×3.0", "原子力なし", "直流連系（2034〜）", "泊全基（2035〜）"]:
        for design in DES:
            for cap in (("主", "低位", "高位") if path == MAIN else ("主",)):
                for P in PGRID:
                    first, Kt, _ = solve_p(path, design, P, cap=cap)
                    rows.append({"経路": path, "設計": design, "資本費の経路": cap, "容量価格 P(円/kW)": P, "最初の参入年": first,
                                 "K 2030": Kt[2030], "K 2035": Kt[2035], "K 2040": Kt[2040], "K 2045": Kt[2045]})
    S = pd.DataFrame(rows)
    S.round(2).to_csv(os.path.join(PROC, "capacity_price_supply.csv"), index=False, encoding="utf-8-sig")

    # 外挿の基準の価格での量
    A = []
    for nm, P in ANCHORS.items():
        for design in DES:
            for cap in ("主", "低位", "高位"):
                first, Kt, _ = solve_p(MAIN, design, P, cap=cap)
                A.append({"容量価格の置き方": nm, "P(円/kW)": P, "設計": design, "資本費の経路": cap, "最初の参入年": first,
                          "K 2035": Kt[2035], "K 2040": Kt[2040], "K 2045": Kt[2045]})
    AD = pd.DataFrame(A)
    print("外挿の基準の容量価格での量（主の経路、万kW）")
    print(AD.round(1).to_string(index=False))

    # 目標の量に要る容量価格
    R = []
    for path in [MAIN, "2040 の太陽光はエネ基の倍率×3.0", "原子力なし", "直流連系（2034〜）", "泊全基（2035〜）", "2040 は OCCTO 9,000億kWh"]:
        for design in DES:
            for cap in (("主", "低位", "高位") if path == MAIN else ("主",)):
                for start in ((48_000.0, 67_000.0) if path == MAIN and cap == "主" else (48_000.0,)):
                    r = {"経路": path, "設計": design, "資本費の経路": cap, "足下の資本費(万円/kWh)": start / 1e4}
                    for tgt, yr in ((20, 2040), (50, 2040), (80, 2040), (100, 2040), (50, 2035)):
                        r[f"{yr}年に{tgt}万kW に要る P(円/kW)"] = required_p(path, design, tgt, yr, cap=cap, start=start)
                    R.append(r)
    RD = pd.DataFrame(R)
    RD.round(0).to_csv(os.path.join(PROC, "capacity_price_required.csv"), index=False, encoding="utf-8-sig")
    print("\n目標の量に要る容量価格（円/kW。κ＝0.861 を掛ける前の約定価格）")
    print(RD.round(0).to_string(index=False))

    # 補助との比較（主の経路・現行）: 容量価格が2029年度向けの水準で続くとき、資本費の補助で2040年に80万kW を得るのに要る補助率と、その財政の負担
    C = []
    for design in ("現行", "効率＋炭素"):
        P0 = ANCHORS["2029年度向け（最新）"]
        lo, hi = 0.0, 0.95
        for _ in range(22):
            mid = (lo + hi) / 2
            if solve_p(MAIN, design, P0, subsidy=mid)[1][2040] >= 80:
                hi = mid
            else:
                lo = mid
        first, Kt, k = solve_p(MAIN, design, P0, subsidy=hi)
        cost = sum(v * 1e4 * 4 * P4.capex_path(t, "主") * hi for t, v in k.items() if v > 1e-6 and t <= 2039) / 1e8
        preq = required_p(MAIN, design, 80, 2040)
        cap_cost = (KAP * (preq - P0)) * 80e4 / 1e8
        C.append({"設計": design, "容量価格が14,972円で続くときに、2040年に80万kW に要る資本費の補助率": hi,
                  "補助の総額（2039年までの建設分、億円）": cost, "同じ80万kW を容量価格で得るのに要る P(円/kW)": preq,
                  "容量収入の上乗せの年額（80万kW、億円/年）": cap_cost})
    CD = pd.DataFrame(C)
    CD.round(3).to_csv(os.path.join(PROC, "capacity_vs_subsidy.csv"), index=False, encoding="utf-8-sig")
    print("\n補助と容量価格の比較"); print(CD.round(2).to_string(index=False))

    # 図: 容量価格と2040年の量
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Hiragino Sans", "Yu Gothic", "IPAexGothic", "sans-serif"]
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    sub = S[(S["経路"] == MAIN) & (S["資本費の経路"] == "主")]
    for design, st in zip(DES, ("-", "--", ":")):
        d = sub[sub["設計"] == design]
        ax.plot(d["容量価格 P(円/kW)"], d["K 2040"], st, color="k", label=f"{design}（主の資本費）")
    band = S[(S["経路"] == MAIN) & (S["設計"] == "現行")].pivot_table(index="容量価格 P(円/kW)", columns="資本費の経路", values="K 2040")
    ax.fill_between(band.index, band["高位"], band["低位"], color="0.85", label="現行・資本費の低位〜高位（NREL）")
    ax.set_ylim(-5, 215)
    for nm, P in ANCHORS.items():
        ax.axvline(P, color="0.6", lw=0.8)
        ax.text(P + 150, 120, nm, rotation=90, va="center", ha="left", fontsize=7, color="0.35")
    ax.axhline(80, color="0.4", lw=0.8, ls="-.")
    ax.text(22_500, 72, "計画上の想定量 80万kW（OCCTO、2040年）", fontsize=8, color="0.3")
    ax.text(31_800, 203, "200万kW は計算の上限", fontsize=7, color="0.4", ha="right")
    ax.set_xlabel("北海道エリアの容量価格 P（円/kW、K と年によらず一定）")
    ax.set_ylabel("2040年の市場参入の容量（万kW）")
    ax.set_title("容量価格と蓄電池の量（自由参入均衡、主の経路）", fontsize=11)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "capacity_price_supply.png"), dpi=200)
    print("図を保存:", os.path.join(FIGDIR, "capacity_price_supply.png"))
