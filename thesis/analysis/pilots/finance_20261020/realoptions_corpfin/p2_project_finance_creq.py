#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット2: c_req をプロジェクトファイナンスの資本構成から導く（契約型 LTDA とマーチャントの資本コストの違い）

リポジトリは読むだけ。出力は out/。
原稿の c_req = 4h資本費×CRF(WACC,20年) + 運維・廃止0.53万 + 託送等固定0.69万（WACC 一律 6%）に対し、
  (1) 借入余力を DSCR で決める（デット・サイジング）→ 負債比率 → 税引前 WACC → c_req → θ*
      契約型（LTDA: 固定収入、DSCR 1.20〜1.30、18年）とマーチャント（下振れケースの CFADS、DSCR 1.4〜1.75、10〜12年）
  (2) LTDA の最低応札価格（6時間仕様）と上限価格（7.2〜7.7万円/kW-年）での事業 IRR・エクイティ IRR
  (3) 6時間仕様で LTDA（上限価格）とマーチャントが無差別になる θ
  (4) 劣化（1%/年）と DoD 80%（kWh 当たり資本費の実効1.25倍）が θ* に与える影響
資本コスト・借入条件の数値は出典付きの範囲（LTDA 事業報酬率4〜6%、算定委 IRR 4〜6%）と
実務の仮定（借入金利・DSCR・エクイティ・コスト）を分けて示す。後者は仮定であり出典ではない。
"""
import os

import numpy as np
import pandas as pd
from scipy.optimize import brentq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 220)

T = 20
OM, WHEEL, DECOM_SHARE = 5_000.0, 6_900.0, 0.05
P_CAP = 14_972.0
KAPPA = {4: 0.836, 6: 0.932}                         # 2029年度向け北海道（07_results2.md 7.4）
DUR_MULT = {4: 1.00, 6: 1.27}                        # PF 価値の duration 比（07_results2.md 7.4、FY2023-25 実績）
PI_PF0_4H = 8_265.0                                  # 価格過程モデルの π_PF(0)（θ=1）
CAPTURE = 0.81
CHG_RATE = 1.2


def spot_net(h, theta=1.0, degr=0.0, year=1):
    """スポットの実現可能粗利（充電従量控除後）。劣化は放電可能量に比例して粗利を減らす近似"""
    return CAPTURE * PI_PF0_4H * DUR_MULT[h] * theta * (1 - degr) ** (year - 1) - h * 365 * CHG_RATE


def capex(h, unit=6.8e4, dod=1.0):
    return h * unit / dod


def annuity(r, n):
    return (1 - (1 + r) ** -n) / r if r > 0 else n


def crf(r, n=T):
    return 1 / annuity(r, n)


def npv_project(I, cf, r):
    """cf: 長さ T の年次 CF（期末）。廃止費は I×5% を T 年目に"""
    t = np.arange(1, T + 1)
    return -I + np.sum(cf / (1 + r) ** t) - DECOM_SHARE * I / (1 + r) ** T


def irr(I, cf):
    f = lambda r: npv_project(I, cf, r)
    try:
        return brentq(f, -0.2, 1.0)
    except ValueError:
        return np.nan


def c_req(I, r):
    """原稿と同じ形: 資本費年額＋運維・廃止＋託送等固定（廃止費は PV を年額化）"""
    return I * crf(r) + OM + DECOM_SHARE * I / (1 + r) ** T * crf(r) + WHEEL


def theta_star(h, I, r, kp, degr=0.0):
    """K=0 で参入が開く θ*（劣化ありの場合は年価値の PV で評価）"""
    if degr == 0:
        return (c_req(I, r) - kp + h * 365 * CHG_RATE) / (CAPTURE * PI_PF0_4H * DUR_MULT[h])
    t = np.arange(1, T + 1)
    df = (1 + r) ** -t
    pv_gross = np.sum(CAPTURE * PI_PF0_4H * DUR_MULT[h] * (1 - degr) ** (t - 1) * df)
    pv_fixed = (OM + WHEEL - kp + h * 365 * CHG_RATE) * df.sum() + DECOM_SHARE * I / (1 + r) ** T
    return (I + pv_fixed) / pv_gross


print(f"検算: c_req(4h, 6.8万, 6%) = {c_req(capex(4), 0.06):,.0f} 円/kW-年（原稿: 約3.59万）, "
      f"θ* = {theta_star(4, capex(4), 0.06, 12_500):.2f}（表9.2: 3.76）")


# ------------------------------------------------------------------ デット・サイジング
def size_debt(cfads_lender, dscr, kd, tenor, I, cap_gear):
    D = min(cfads_lender / dscr * annuity(kd, tenor), cap_gear * I)
    return D, D / I


def equity_irr(I, cf, D, kd, tenor):
    ds = D / annuity(kd, tenor)
    eq = cf.copy()
    eq[:tenor] -= ds
    t = np.arange(1, T + 1)
    f = lambda r: -(I - D) + np.sum(eq / (1 + r) ** t) - DECOM_SHARE * I / (1 + r) ** T
    try:
        return brentq(f, -0.5, 3.0)
    except ValueError:
        return np.nan


rows = []
# ---- (1) マーチャント 4h ----
I4 = capex(4)
kp4 = KAPPA[4] * P_CAP
for theta_lender, lab_l in ((0.68, "θ P10（σ=0.30）"), (1.00, "θ=1（中央）")):
    for dscr, tenor in ((1.40, 12), (1.75, 10)):
        for kd, ke in ((0.025, 0.10), (0.035, 0.12)):
            cf_l = spot_net(4, theta_lender) + kp4 - OM - WHEEL
            D, gear = size_debt(max(cf_l, 0), dscr, kd, tenor, I4, 0.60)
            wacc = gear * kd + (1 - gear) * ke
            rows.append({"区分": "マーチャント4h", "貸し手ケース": lab_l, "DSCR": dscr, "年限": tenor, "kd": kd, "ke": ke,
                         "CFADS_貸し手(円/kW-年)": cf_l, "負債比率": gear, "WACC(税引前)": wacc,
                         "c_req(円/kW-年)": c_req(I4, wacc), "θ*": theta_star(4, I4, wacc, kp4)})
# 参照: 原稿の一律 6%、算定委・LTDA 事業報酬率の帯
for w, lab in ((0.05, "参照: LTDA 事業報酬率（第1・2回）5%"), (0.06, "原稿の基準 6%"), (0.04, "参照: LTDA 第3回の下限4%")):
    rows.append({"区分": lab, "WACC(税引前)": w, "c_req(円/kW-年)": c_req(I4, w), "θ*": theta_star(4, I4, w, kp4)})
dfM = pd.DataFrame(rows)
print("\n(1) マーチャント 4h のデット・サイジングと WACC・c_req・θ*（資本費6.8万円/kWh、実効容量収入 κP=1.25万）")
print(dfM.round(3).to_string(index=False))
dfM.to_csv(os.path.join(OUT, "p2_1_merchant_wacc.csv"), index=False)

# ---- (2) LTDA 6h: 最低応札価格（エクイティが ke_L を得る価格）と上限価格での IRR ----
I6 = capex(6)
rows2 = []
for unit in (6.8e4, 6.0e4):
    I6u = capex(6, unit)
    for dscr, kd, ke in ((1.20, 0.015, 0.06), (1.30, 0.020, 0.08), (1.30, 0.030, 0.10)):
        tenor = 18
        retained = 0.10 * max(spot_net(6, 1.0), 0)

        def solve_price(P):
            # エクイティ NPV（割引率 ke）= 0 となる価格。IRR ではなく NPV で解いて単調性を確保
            cf = np.full(T, P + retained - OM - WHEEL)
            D, gear = size_debt(max(P - OM - WHEEL, 0), dscr, kd, tenor, I6u, 0.90)
            eq = cf.copy()
            eq[:tenor] -= D / annuity(kd, tenor)
            t = np.arange(1, T + 1)
            return -(I6u - D) + np.sum(eq / (1 + ke) ** t) - DECOM_SHARE * I6u / (1 + ke) ** T

        Pmin = brentq(solve_price, 20_000, 200_000)
        D, gear = size_debt(Pmin - OM - WHEEL, dscr, kd, tenor, I6u, 0.90)
        r_ = {"資本費(円/kWh)": unit, "DSCR": dscr, "kd": kd, "ke": ke, "最低応札価格P_min(円/kW-年)": Pmin,
              "P_min時の負債比率": gear, "P_min時の事業IRR": irr(I6u, np.full(T, Pmin + retained - OM - WHEEL))}
        for cap in (72_000, 77_000):
            cf = np.full(T, cap + retained - OM - WHEEL)
            Dc, gc = size_debt(cap - OM - WHEEL, dscr, kd, tenor, I6u, 0.90)
            r_[f"上限{cap//1000}千円での事業IRR"] = irr(I6u, cf)
            r_[f"上限{cap//1000}千円でのエクイティIRR"] = equity_irr(I6u, cf, Dc, kd, tenor)
        rows2.append(r_)
dfL = pd.DataFrame(rows2)
print("\n(2) LTDA 6h（固定収入＋スポットの1割を保持）: 最低応札価格と上限価格での IRR（税引前・名目と実質の区別なし）")
print(dfL.round(3).to_string(index=False))
dfL.to_csv(os.path.join(OUT, "p2_2_ltda_price_irr.csv"), index=False)

# ---- (3) 6h で LTDA（上限価格・契約型の WACC）とマーチャント（マーチャントの WACC）が無差別になる θ ----
rows3 = []
kp6 = KAPPA[6] * P_CAP
for cap in (72_000, 77_000):
    for w_L, w_M in ((0.04, 0.08), (0.05, 0.10), (0.04, 0.06)):
        npv_L = npv_project(I6, np.full(T, cap + 0.10 * max(spot_net(6), 0) - OM - WHEEL), w_L)

        def gap(th):
            return npv_project(I6, np.full(T, spot_net(6, th) + kp6 - OM - WHEEL), w_M) - npv_L
        th_ind = brentq(gap, 0.0, 100.0)
        rows3.append({"LTDA価格(円/kW-年)": cap, "WACC_LTDA": w_L, "WACC_マーチャント": w_M, "LTDA の NPV(円/kW)": npv_L,
                      "無差別 θ": th_ind, "参考: 6h マーチャントの θ*(WACC_M)": theta_star(6, I6, w_M, kp6)})
df3 = pd.DataFrame(rows3)
print("\n(3) 6h: LTDA（上限価格で落札）とマーチャント残留が無差別になる価格水準 θ")
print(df3.round(2).to_string(index=False))
df3.to_csv(os.path.join(OUT, "p2_3_ltda_vs_merchant.csv"), index=False)

# ---- (4) 劣化・DoD の影響（4h、WACC 6%） ----
rows4 = []
for degr in (0.0, 0.01, 0.02):
    for dod in (1.0, 0.8):
        I = capex(4, dod=dod)
        rows4.append({"劣化(年)": degr, "DoD": dod, "実効資本費(円/kW)": I, "θ*(WACC6%)": theta_star(4, I, 0.06, kp4, degr),
                      "θ*(WACC8%)": theta_star(4, I, 0.08, kp4, degr)})
df4 = pd.DataFrame(rows4)
print("\n(4) 劣化と DoD の θ* への影響（4h、容量収入1.25万）")
print(df4.round(2).to_string(index=False))
df4.to_csv(os.path.join(OUT, "p2_4_degradation_dod.csv"), index=False)

# ---- (2b) 事業報酬率で積み上げた応札価格（固定費のみ算入・事業IRR=4〜6%）でのエクイティ IRR（レバレッジ効果） ----
rows2b = []
retained6 = 0.10 * max(spot_net(6, 1.0), 0)
for unit in (6.8e4, 6.0e4):
    I6u = capex(6, unit)
    for w_reg in (0.04, 0.05, 0.06):
        P_reg = brentq(lambda P: npv_project(I6u, np.full(T, P - OM - WHEEL), w_reg), 10_000, 300_000)
        cf = np.full(T, P_reg + retained6 - OM - WHEEL)
        for dscr, kd, gcap in ((1.20, 0.015, 0.90), (1.30, 0.020, 0.85), (1.30, 0.020, 0.75), (1.30, 0.030, 0.75)):
            D, gear = size_debt(P_reg - OM - WHEEL, dscr, kd, 18, I6u, gcap)
            rows2b.append({"資本費(円/kWh)": unit, "事業報酬率": w_reg, "積み上げ応札価格(円/kW-年)": P_reg,
                           "DSCR": dscr, "kd": kd, "負債比率上限": gcap, "負債比率": gear,
                           "事業IRR(1割保持込み)": irr(I6u, cf), "エクイティIRR": equity_irr(I6u, cf, D, kd, 18)})
df2b = pd.DataFrame(rows2b)
print("\n(2b) 事業報酬率で積み上げた応札価格でのエクイティ IRR（6h、18年借入、スポットの1割保持）")
print(df2b.round(3).to_string(index=False))
df2b.to_csv(os.path.join(OUT, "p2_2b_ltda_regulated_return_leverage.csv"), index=False)

# ---- (3b) 積み上げ応札価格（事業報酬率5%）で落札した場合のマーチャントとの無差別 θ ----
rows3b = []
P5 = brentq(lambda P: npv_project(I6, np.full(T, P - OM - WHEEL), 0.05), 10_000, 300_000)
for w_L, w_M in ((0.04, 0.08), (0.05, 0.10), (0.05, 0.06)):
    npv_L = npv_project(I6, np.full(T, P5 + retained6 - OM - WHEEL), w_L)
    th_ind = brentq(lambda th: npv_project(I6, np.full(T, spot_net(6, th) + kp6 - OM - WHEEL), w_M) - npv_L, 0.0, 100.0)
    rows3b.append({"LTDA価格(事業報酬率5%で積み上げ)": P5, "WACC_LTDA": w_L, "WACC_マーチャント": w_M,
                   "LTDA の NPV(円/kW)": npv_L, "無差別 θ": th_ind})
df3b = pd.DataFrame(rows3b)
print("\n(3b) 積み上げ価格で落札した LTDA とマーチャント残留の無差別 θ（6h）")
print(df3b.round(2).to_string(index=False))
df3b.to_csv(os.path.join(OUT, "p2_3b_ltda_cost_based_vs_merchant.csv"), index=False)

# ---- (5) トルネード: θ*（4h、K=0）の一変数感応度。基準=資本費6.8万・WACC6%・capture0.81・κP1.25万・劣化0・DoD1 ----
def theta_star_gen(unit=6.8e4, r=0.06, cap=CAPTURE, kp=12_500.0, degr=0.0, dod=1.0, tail=1.0, chg=CHG_RATE):
    I = capex(4, unit, dod)
    t = np.arange(1, T + 1)
    df = (1 + r) ** -t
    pv_gross = np.sum(cap * PI_PF0_4H * tail * (1 - degr) ** (t - 1) * df)
    pv_fixed = (OM + WHEEL - kp + 4 * 365 * chg) * df.sum() + DECOM_SHARE * I / (1 + r) ** T
    return (I + pv_fixed) / pv_gross


base_t = theta_star_gen()
tor = [("資本費（万円/kWh）", "unit", 6.0e4, 7.6e4, "6.0（50MWh以上）", "7.6（FY2023）"),
       ("WACC", "r", 0.05, 0.10, "5%", "10%（マーチャントのプロジェクトファイナンス試算）"),
       ("capture率", "cap", 0.86, 0.70, "0.86（区間上端）", "0.70（Butters 水準）"),
       ("実効容量収入（円/kW-年）", "kp", 25_000.0, 8_300.0, "2.5万（上限近傍）", "0.83万（発動指令）"),
       ("劣化（年）", "degr", 0.0, 0.02, "0%", "2%"),
       ("DoD（kWh 当たり資本費の実効倍率）", "dod", 1.0, 0.8, "1.0", "0.8"),
       ("裾の補正（π_PF×）", "tail", 1.25, 1.0, "1.25", "1.00"),
       ("充電従量（円/kWh）", "chg", 0.88, 1.5, "0.88", "1.5")]
rows5 = []
for name, key, lo, hi, llab, hlab in tor:
    a_ = theta_star_gen(**{key: lo}); b_ = theta_star_gen(**{key: hi})
    rows5.append({"要因": name, "有利側": llab, "θ*(有利)": a_, "不利側": hlab, "θ*(不利)": b_, "幅": abs(b_ - a_)})
df5 = pd.DataFrame(rows5).sort_values("幅", ascending=False)
print(f"\n(5) トルネード（基準 θ* = {base_t:.2f}）")
print(df5.round(2).to_string(index=False))
df5.to_csv(os.path.join(OUT, "p2_5_tornado_theta_star.csv"), index=False)
