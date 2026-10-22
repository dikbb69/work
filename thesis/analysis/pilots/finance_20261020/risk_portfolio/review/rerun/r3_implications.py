#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""risk_portfolio 補助計算: r1/r2 の結果を論文の数値（θ*、c_req、LTDA）に接続する。

(a) 収益の水準弾力性 β≠1 のとき θ* はどう動くか: PF(θ)=PF(1)·θ^β なら θ*_β = θ*^{1/β}
    （8.4 の θ*: 楽観3.17・標準3.55・保守4.55、×1.25上限ケース 2.55・2.84・3.65）
(b) 2商品ヘッジ（東京ベース先物＋間接送電権 北海道→東北 相当の値差 p_tohoku − p_hokkaido）
(c) 債務調達余力（デット・サイジング）の例示: マーチャント（スポット＋容量）と LTDA 型固定収入
    → 達成可能なレバレッジと WACC（仮定は明示、例示のみ）
(d) LTDA 上限価格が許容する事業 IRR の上限（6時間、資本費6.8万円/kWh 一定の仮定）
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

OUT = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/matsuba/work/thesis"

# ---------------------------------------------------------------- (a)
th_star = {"楽観": 3.17, "標準": 3.55, "保守": 4.55}
th_star_tail = {"楽観": 2.55, "標準": 2.84, "保守": 3.65}
rows = []
for b in [1.0, 1.18, 1.20, 1.36, 1.42]:
    r = {"β": b}
    r.update({f"θ*{k}": v ** (1 / b) for k, v in th_star.items()})
    r.update({f"θ*{k}(×1.25上限)": v ** (1 / b) for k, v in th_star_tail.items()})
    rows.append(r)
ta = pd.DataFrame(rows)
print("=== (a) 水準弾力性 β と損益分岐の水準係数 θ*（8.4 の値を θ^β で読み替え）===")
print(ta.round(2).to_string(index=False))
print("参考: 観測された θ の最大 = FY2022 1.72、FY2026上期 1.57（表8.2）")
ta.to_csv(os.path.join(OUT, "r3_theta_star_beta.csv"), index=False)

# 対数正規の水準分布の下で単年に θ ≥ θ*_β となる確率（σ_logθ=0.267 は r1 の FY2016〜25 代理）
from scipy.stats import norm
sig = 0.267
print("\n単年で θ ≥ θ*（×1.25上限・標準）となる確率: 中央値1 / 中央値1.57（FY2026上期水準が定着）")
for b in [1.0, 1.2, 1.42]:
    ts = th_star_tail["標準"] ** (1 / b)
    print(f"  β={b}: θ*={ts:.2f}  P(中央値1)={1 - norm.cdf(np.log(ts) / sig):.4f}  "
          f"P(中央値1.57)={1 - norm.cdf(np.log(ts / 1.57) / sig):.4f}")

# ---------------------------------------------------------------- (b) 2商品ヘッジ
hp = pd.read_csv(os.path.join(REPO, "data/processed/hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
s = np.sort(P.to_numpy(), axis=1)
d = pd.DataFrame({"pf": np.maximum(0.85 * s[:, -4:].sum(1) - s[:, :4].sum(1), 0)}, index=P.index)
hp["sprd"] = hp["p_tohoku"] - hp["p_hokkaido"]          # 北海道→東北 方向の値差（間接送電権の精算額の代理）
hp["sprd_pos"] = hp["sprd"].clip(lower=0)
dd = hp.groupby("day")[["sprd", "sprd_pos", "p_tohoku"]].mean()
d = d.join(dd)
d["ym"] = d.index.to_period("M")
mo = d.groupby("ym").agg(X=("pf", "sum"), sprd=("sprd", "mean"), sprd_pos=("sprd_pos", "mean"),
                         base_tohoku=("p_tohoku", "mean"), n=("pf", "size"))
mo = mo[mo.n >= 25]
r2 = pd.read_csv(os.path.join(OUT, "r2_hedge.csv"))  # 参照のみ
# 東京ベースは r2 と同じ定義で再計算
import glob
fr = []
for f in sorted(glob.glob(os.path.join(REPO, "data/raw/jepx/spot_summary_*.csv"))):
    x = pd.read_csv(f, encoding="cp932").iloc[:, [0, 8]]
    x.columns = ["date", "tky"]
    fr.append(x)
j = pd.concat(fr)
j["date"] = pd.to_datetime(j["date"])
j["tky"] = pd.to_numeric(j["tky"], errors="coerce")
mo = mo.join(j.groupby(j["date"].dt.to_period("M"))["tky"].mean().rename("base_t"))
mo["cal"] = mo.index.month
mo["fy"] = mo.index.year - (mo.index.month < 4)


def he_multi(df, cols):
    z = df[["X"] + cols].dropna()
    z = z - z.groupby(df.loc[z.index, "cal"]).transform("mean")
    r = sm.OLS(z["X"], sm.add_constant(z[cols])).fit()
    return r.rsquared, r.params[cols].to_dict()


print("\n=== (b) 月間蓄電池粗利のヘッジ有効性（季節除去後 R²）: 東京ベース単独 vs ＋北海道→東北値差 ===")
rows = []
for samp, df in {"FY2016/4-2026/6": mo, "FY2023/4-2026/6": mo[mo.fy >= 2023]}.items():
    for cols in [["base_t"], ["sprd"], ["sprd_pos"], ["base_t", "sprd"], ["base_t", "sprd_pos"]]:
        he, prm = he_multi(df, cols)
        rows.append(dict(sample=samp, instruments="+".join(cols), HE=he, **{f"h_{k}": v for k, v in prm.items()}))
hb = pd.DataFrame(rows)
print(hb.round(3).to_string(index=False))
hb.to_csv(os.path.join(OUT, "r3_two_instrument_hedge.csv"), index=False)

# ---------------------------------------------------------------- (c) デット・サイジング（例示）
CAPEX4 = 6.8e4 * 4          # 円/kW
FIXED = 5300 + 6900         # 運維・廃止 0.53万 ＋ 託送等固定 0.69万（c_req の内訳）
lev = pd.read_csv(os.path.join(OUT, "r1_level_risk.csv"))
rng = np.random.default_rng(1)
# r1 の B ケース（θ 経験分布）を再現する代わりに、r1 の年次π分布の分位点を読む
print("\n=== (c) デット・サイジング（例示、仮定: 金利2%・15年元利均等、DSCR 1.30）===")
ann_f = 0.02 / (1 - 1.02 ** -15)
kap = np.array([8749, 13287, 14812, 14972]) * 0.836        # 北海道の容量約定価格（2026〜29年度向け）×κ
rows = []
for case in lev["case"]:
    q = lev.set_index("case").loc[case]
    for nm, pi_q in [("P50(平均)", q["mean"]), ("5%点(P95)", q["q05"])]:
        for kp_nm, kp in [("容量=1.25万（2029向け）", 12517), ("容量=最小0.73万（2026向け）", kap.min())]:
            cfads = pi_q + kp - FIXED
            debt = max(cfads, 0) / 1.30 / ann_f
            rows.append(dict(case=case, spot=nm, capacity=kp_nm, CFADS=cfads, debt=debt,
                             gearing=min(debt / CAPEX4, 1.0)))
dsz = pd.DataFrame(rows)
print(dsz.round(3).to_string(index=False))
dsz.to_csv(os.path.join(OUT, "r3_debt_sizing.csv"), index=False)
# LTDA 型（6h、固定収入 F）
CAPEX6 = 6.8e4 * 6
for F in [50000, 60000, 72000, 77000]:
    cf = F - (5000 + 0.05 * CAPEX6 / 20) - 6900
    debt = cf / 1.30 / ann_f
    print(f"LTDA型 6h 固定収入 {F:,} 円/kW-年: CFADS={cf:,.0f}, 債務上限={debt:,.0f} 円/kW, gearing 上限={min(debt / CAPEX6, 1):.2f}")


# WACC の例示
def wacc(g, kd=0.02, ke=0.08, tax=0.3):
    return g * kd * (1 - tax) + (1 - g) * ke


print("WACC 例示（kd=2%、税率30%）: gearing 0.8 & ke 7% → {:.2%} ／ gearing 0.2 & ke 10% → {:.2%} ／ gearing 0 & ke 10% → {:.2%}".format(
    wacc(0.8, ke=0.07), wacc(0.2, ke=0.10), wacc(0.0, ke=0.10)))


def crf(r, n=20):
    return r / (1 - (1 + r) ** -n)


print("c_req（4h、資本費6.8万/kWh）: WACC 6% {:,.0f} / 9% {:,.0f} / 3% {:,.0f} 円/kW-年".format(
    CAPEX4 * crf(0.06) + FIXED, CAPEX4 * crf(0.09) + FIXED, CAPEX4 * crf(0.03) + FIXED))

# ---------------------------------------------------------------- (d) LTDA 上限価格の IRR 上限
from scipy.optimize import brentq
print("\n=== (d) LTDA 上限価格が許容する税前・無レバレッジ IRR（6h、資本費6.8万円/kWh×6、運維5,000円/kW-年、"
      "廃止 資本費の5%（20年目）、託送等固定6,900円、他市場収益の残り1割は加算）===")
spot6 = 13062 * 0.81 - 1.2 * 6 * 365     # 6h の完全予見粗利（7.4）×capture − 充電従量
for F in [50000, 60000, 72000, 77000]:
    cfs = np.full(20, F - 5000 - 6900 + 0.1 * spot6)
    cfs[-1] -= 0.05 * CAPEX6

    def npv(r):
        return -CAPEX6 + (cfs / (1 + r) ** np.arange(1, 21)).sum()
    irr = brentq(npv, -0.5, 1.0)
    print(f"F={F:,} 円/kW-年 → IRR={irr:.1%}")
