#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""risk_portfolio パイロット2: 蓄電池収益のファクター・エクスポージャーと最小分散ヘッジ（北海道）

リポジトリは読むだけ。出力はこのフォルダ（r2_*.csv）。

(1) 価格水準ファクターへの弾力性（ベータ）:
    log X_m = a_{暦月} + β·log θ_m + e    （X_m: 月間の完全予見粗利、θ_m: price_level_theta.csv の月次、
                                           FY2022/4〜FY2026/6、51か月、Newey-West 3ラグ）
    同じ式を上位4h平均（放電側）・下位4h平均（充電側）にも当てる → 蓄電池＝放電側ロング・充電側ショート
    θ の代わりに月平均システムプライス（FY2016/4〜、123か月）でも推定。
    5.4.1 の価格過程では π ∝ θ（β=1）を仮定し、9.4 の θ* は閉じた形で出している → その検証。
(2) 最小分散ヘッジ比率とヘッジ有効性（Ederington 1979）:
    月間の蓄電池粗利（北海道）を、上場先物の満期ペイオフの代理（JEPX 実績の月平均:
    東京ベース、東京ピーク[平日8-20時]、東京ピーク−ベース、システムベース）で
    ヘッジしたときの h* = Cov/Var と HE = 1 − Var(X − h*F)/Var(X)。
    季節成分（暦月平均）を除いた系列で計算（先物価格が予見可能な季節性を織り込むとみなす近似）。
    参考: 上場していない北海道ベース・東京の4h蓄電池粗利（理想的なスプレッド商品）も併記。
(3) 日次 TB4h の北海道–東京の相関（ベーシス・リスクの大きさ）。
"""
import glob
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO = "/Users/matsuba/work/thesis"
PROC = os.path.join(REPO, "data", "processed")
OUT = os.path.dirname(os.path.abspath(__file__))
ETA, H = 0.85, 4

# ---------------------------------------------------------------- JEPX 生データ（読むだけ）
frames = []
for f in sorted(glob.glob(os.path.join(REPO, "data", "raw", "jepx", "spot_summary_*.csv"))):
    d = pd.read_csv(f, encoding="cp932")
    d = d.iloc[:, [0, 1, 5, 6, 8]]
    d.columns = ["date", "slot", "sys", "hkd", "tky"]
    frames.append(d)
j = pd.concat(frames, ignore_index=True)
j["date"] = pd.to_datetime(j["date"])
j["hour"] = (j["slot"] - 1) // 2
for c in ["sys", "hkd", "tky"]:
    j[c] = pd.to_numeric(j[c], errors="coerce")
hr = j.groupby(["date", "hour"])[["sys", "hkd", "tky"]].mean().reset_index()
hr = hr[hr["date"] <= "2026-06-30"]


def mat(col):
    M = hr.pivot(index="date", columns="hour", values=col)
    return M[M.count(axis=1) == 24]


Mh, Mt, Ms = mat("hkd"), mat("tky"), mat("sys")
days = Mh.index.intersection(Mt.index).intersection(Ms.index)
Mh, Mt, Ms = Mh.loc[days], Mt.loc[days], Ms.loc[days]


def pf(M):
    s = np.sort(M.to_numpy(), axis=1)
    return pd.Series(np.maximum(ETA * s[:, -H:].sum(1) - s[:, :H].sum(1), 0), index=M.index)


def tb4(M):
    s = np.sort(M.to_numpy(), axis=1)
    return pd.Series(s[:, -H:].mean(1) - s[:, :H].mean(1), index=M.index)


def topbot(M):
    s = np.sort(M.to_numpy(), axis=1)
    return pd.Series(s[:, -H:].mean(1), index=M.index), pd.Series(s[:, :H].mean(1), index=M.index)


D = pd.DataFrame(index=days)
D["pf_h"] = pf(Mh)
D["pf_t"] = pf(Mt)
D["tb4_h"], D["tb4_t"] = tb4(Mh), tb4(Mt)
D["top_h"], D["bot_h"] = topbot(Mh)
D["base_h"], D["base_t"], D["base_s"] = Mh.mean(1), Mt.mean(1), Ms.mean(1)
wkday = days.dayofweek < 5
pk = Mt.loc[:, 8:19].mean(1)   # 平日 8:00-20:00（祝日は未除外）
D["peak_t"] = np.where(wkday, pk, np.nan)
D["ym"] = days.to_period("M")
D["fy"] = days.year - (days.month < 4)

# 照合: 年度別 PF（表7.1）
print("年度別PF照合（北海道, 円/kW-年）:", D[D.fy.between(2022, 2025)].groupby("fy")["pf_h"].sum().round(0).to_dict())

Mo = D.groupby("ym").agg(X=("pf_h", "sum"), Xt=("pf_t", "sum"), top=("top_h", "mean"), bot=("bot_h", "mean"),
                         base_h=("base_h", "mean"), base_t=("base_t", "mean"), base_s=("base_s", "mean"),
                         peak_t=("peak_t", "mean"), n=("pf_h", "size"))
Mo = Mo[Mo["n"] >= 25]
Mo["pkbs_t"] = Mo["peak_t"] - Mo["base_t"]
Mo["cal_m"] = Mo.index.month
Mo["fy"] = Mo.index.year - (Mo.index.month < 4)

th = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
thm = th[~th["ym"].str.startswith("FY")].copy()
thm["ym"] = pd.PeriodIndex(thm["ym"], freq="M")
Mo = Mo.join(thm.set_index("ym")["theta_m"])


# ---------------------------------------------------------------- (1) 弾力性
def elast(y, x, df, lags=3, fe=True, extra=None):
    d = df.dropna(subset=[y, x]).copy()
    d = d[(d[y] > 0) & (d[x] > 0)]
    X = pd.DataFrame({"lx": np.log(d[x])}, index=d.index)
    if fe:
        X = pd.concat([X, pd.get_dummies(d["cal_m"], prefix="m", drop_first=True).astype(float)], axis=1)
    if extra is not None:
        X = pd.concat([X, pd.get_dummies(d[extra], prefix=extra, drop_first=True).astype(float)], axis=1)
    X = sm.add_constant(X)
    r = sm.OLS(np.log(d[y]), X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return dict(y=y, x=x, n=len(d), beta=r.params["lx"], se=r.bse["lx"],
                t_vs1=(r.params["lx"] - 1) / r.bse["lx"], r2=r.rsquared)


rows = []
sub_t = Mo.loc[Mo["theta_m"].notna()]
for y in ["X", "top", "bot"]:
    rows.append(dict(sample="FY2022/4-2026/6 (θ_m)", **elast(y, "theta_m", sub_t)))
ex22 = sub_t[sub_t["fy"] >= 2023]
rows.append(dict(sample="FY2023/4-2026/6 (θ_m)", **elast("X", "theta_m", ex22)))
for y in ["X", "top", "bot"]:
    rows.append(dict(sample="FY2016/4-2026/6 (システム月平均)", **elast(y, "base_s", Mo)))
rows.append(dict(sample="FY2016/4-2026/6 (システム月平均)+FY固定効果", **elast("X", "base_s", Mo, extra="fy")))
rows.append(dict(sample="FY2016/4-2026/6 (北海道月平均)", **elast("X", "base_h", Mo)))
el = pd.DataFrame(rows)
print("\n=== (1) 月間粗利・上位4h・下位4h の価格水準弾力性（暦月固定効果、NW3）===")
print(el.round(3).to_string(index=False))
el.to_csv(os.path.join(OUT, "r2_elasticity.csv"), index=False)


# ---------------------------------------------------------------- (2) 最小分散ヘッジ
def deseason(s, cal):
    return s - s.groupby(cal).transform("mean")


def hedge(df, xcol, fcol):
    d = df.dropna(subset=[xcol, fcol])
    x = deseason(d[xcol], d["cal_m"])
    f = deseason(d[fcol], d["cal_m"])
    h = np.cov(x, f, ddof=1)[0, 1] / f.var(ddof=1)
    he = 1 - (x - h * f).var(ddof=1) / x.var(ddof=1)
    return dict(n=len(d), h_star=h, HE=he, corr=np.corrcoef(x, f)[0, 1], sd_X=x.std(ddof=1),
                sd_hedged=(x - h * f).std(ddof=1))


INSTR = {"東京ベース（EEX/TOCOM 上場）": "base_t", "東京ピーク平日8-20時（EEX ピーク/TOCOM 日中ロード）": "peak_t",
         "東京ピーク−ベース（カレンダー・スプレッド）": "pkbs_t", "システムプライス・ベース（非上場）": "base_s",
         "北海道ベース（非上場・理想的な水準ヘッジ）": "base_h", "東京4h蓄電池粗利（非上場・理想的なスプレッド）": "Xt"}
rows = []
for samp, df in {"FY2016/4-2026/6": Mo, "FY2016/4-2026/6（FY2020-22除外）": Mo[~Mo.fy.isin([2020, 2021, 2022])],
                 "FY2023/4-2026/6": Mo[Mo.fy >= 2023]}.items():
    for name, c in INSTR.items():
        rows.append(dict(sample=samp, instrument=name, **hedge(df, "X", c)))
hg = pd.DataFrame(rows)
print("\n=== (2) 月間蓄電池粗利（北海道、円/kW-月）の最小分散ヘッジ（季節除去後）===")
print("h* の単位: 円/kW-月 の粗利 1 単位あたり、ヘッジ商品の月平均価格（円/kWh）× h* … 例: h*=60 は 60 kWh/kW-月 相当のショート")
print(hg.round(3).to_string(index=False))
hg.to_csv(os.path.join(OUT, "r2_hedge.csv"), index=False)

# ---------------------------------------------------------------- (3) 日次 TB4h の地域ベーシス
print("\n=== (3) 日次 TB4h の北海道–東京相関（年度別）===")
cc = D.groupby("fy").apply(lambda g: pd.Series({"corr_tb4": g["tb4_h"].corr(g["tb4_t"]),
                                                  "corr_pf": g["pf_h"].corr(g["pf_t"]),
                                                  "PF_h": g["pf_h"].sum(), "PF_t": g["pf_t"].sum()}))
print(cc.round(3).to_string())
cc.to_csv(os.path.join(OUT, "r2_basis_corr.csv"))
