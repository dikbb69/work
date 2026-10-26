#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""燃料の輸入価格（月別）から火力の発電単価（送電端、円/kWh）を計算し、価格の水準が燃料費で説明できるかを確かめる

データ:
  - 財務省「普通貿易統計」統計品別表（輸入、e-Stat 政府統計コード00350300）の月別の数量・金額から作った CIF 単価
    （LNG 2711.11-000、一般炭 2701.12-099＋2701.19-010・090、原油 2709.00-100・900）。2016/4〜2026/9（data/raw/fuel/fuel_cif_monthly.csv）。
    2025年は確々報、2026年1〜7月は確報、8月は9桁速報、9月は概況品の速報（改定されうる）。
  - 発熱量・燃料諸経費・発電効率・所内率: 発電コスト検証WG「各電源の諸元一覧」（2025/2/6、資料2）の石炭火力（p.13）・
    LNG 火力（p.14）・石油火力（p.15）のモデルプラントの値（著者が原典を確認、2026-10-23）。
    - 発熱量（総発熱量）: 輸入一般炭26.08MJ/kg、LNG 54.70MJ/kg、発電用C重油41.63MJ/l（総合エネルギー統計の標準発熱量）。
    - 燃料諸経費（石油石炭税を含む、各社の直近実績の平均）: 石炭2,300円/t（税・輸入手数料・内航運賃等）、LNG 3,100円/t
      （税・輸入手数料・気化費用等）、石油21,800円/kl（税・内航運賃・精製・脱硫費用等）。石油は WG と同じく原油の CIF 単価を起点にする。
    - 発電効率（HHV・発電端、サンプルプラントの平均）: 石炭43.4%（超々臨界。横須賀1・2号、西条新1号、三隅2号）、
      LNG 54.9%（姉崎新1号、上越1号、石狩湾新港1号、富山新港 LNG1号）、石油39.0%（尾鷲三田3号、宮津1・2号、知内2号）。
    - 所内率: 石炭5.6%、LNG 2.2%、石油4.8%。
    CO2 の価格は入れない（GX-ETS の本格運用前。WG は CO2 対策費用を別に置く）。
    北海道の既設の石炭ユニットの効率の差は、OCCTO の想定の燃種別の比率で反映する
    （超臨界は×10.4/11.2、亜臨界は×10.4/11.5。59 の vc_matrix がユニットの燃料費の想定の比で伸縮する）。
式: 送電端の燃料費（円/kWh）＝（CIF 単価＋燃料諸経費）÷ 発熱量 × 3.6/1,000 ÷ 発電効率 ÷（1−所内率）
出力: data/processed/fuel_vc_monthly.csv（month、vc_coal＝超々臨界、vc_lng＝LNG コンバインド、vc_oil＝石油火力）、
  fuel_price_fit.csv（価格の水準の回帰と、年度ごとの疑似標本外の誤差）、fuel_price_cointegration.csv（単位根・共和分・VECM）
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw", "fuel")

HV = {"coal": 26.08, "lng": 54.70, "oil": 41.63}                 # GJ/t、GJ/t、GJ/kl（C重油）
FEE = {"coal": 2_300.0, "lng": 3_100.0, "oil": 21_800.0}         # 燃料諸経費（税込み）: 円/t、円/t、円/kl
EFF = {"coal": 0.434, "lng": 0.549, "oil": 0.390}                 # 発電端（総発熱量）
OWN = {"coal": 0.056, "lng": 0.022, "oil": 0.048}                 # 所内率
COL = {"coal": "coal_yen_per_t", "lng": "lng_yen_per_t", "oil": "crude_yen_per_kl"}

F = pd.read_csv(os.path.join(RAW, "fuel_cif_monthly.csv"))
F["month"] = pd.to_datetime(F["month"] + "-01")
out = pd.DataFrame({"month": F["month"]})
for k in ("coal", "lng", "oil"):
    out[f"vc_{k}"] = (F[COL[k]] + FEE[k]) / HV[k] * 3.6 / 1_000 / EFF[k] / (1 - OWN[k])
out["データの段階"] = F["data_status"]
out.round(4).to_csv(os.path.join(PROC, "fuel_vc_monthly.csv"), index=False, encoding="utf-8-sig")
fy = out["month"].dt.year - (out["month"].dt.month < 4)
print("送電端の燃料費（円/kWh、年度平均）")
print(out.groupby(fy)[["vc_coal", "vc_lng", "vc_oil"]].mean().round(2).to_string())

# ---------------------------------------------------------------- 価格の水準は燃料費で説明できるか（東北・北海道・システム）
# 被説明変数は月の中央値（スパイクに頑健）。主の仕様は、石炭と LNG の燃料費の平均を1つの指標にした単回帰
# （2変数では共線性が強く、個別の係数は不安定）。2020/12〜2021/2（LNG の在庫不足による高騰）は特殊要因として除く。
# 平均値・除外なし・2変数の結果も併記する。
# 疑似標本外: 年度ごとに、前年度までで推定して当年度を予測（拡大窓）。素朴な基準は前年度の中央値の平均。
P = pd.read_csv(os.path.join(PROC, "tohoku_hourly_panel.csv"), parse_dates=["ts"])
P["month"] = P["ts"].dt.to_period("M").dt.to_timestamp()
VC = out.set_index("month")[["vc_coal", "vc_lng"]]
VC["vc_avg"] = VC[["vc_coal", "vc_lng"]].mean(axis=1)
SPECIAL = ("2020-12-01", "2021-02-01")
rows, oos_rows = [], []
for stat in ("median", "mean"):
    M = P.groupby("month")[["p_tohoku", "p_hokkaido", "p_system"]].agg(stat).join(VC, how="inner")
    M = M[(M.index >= "2016-04-01") & (M.index < "2026-07-01")]
    for excl in (True, False):
        d = M[~((M.index >= SPECIAL[0]) & (M.index <= SPECIAL[1]))] if excl else M
        fy_d = d.index.year - (d.index.month < 4)
        for spec, cols in (("指標1つ（石炭と LNG の平均）", ["vc_avg"]), ("2変数（石炭・LNG）", ["vc_coal", "vc_lng"])):
            for ycol in ("p_tohoku", "p_hokkaido", "p_system"):
                X = sm.add_constant(d[cols])
                r = sm.OLS(d[ycol], X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
                slope = r.params[cols].sum()
                wald = r.wald_test(" + ".join(cols) + (" = 1" if len(cols) == 1 else " = 1"), scalar=True) if len(cols) == 2 else \
                    r.wald_test(f"{cols[0]} = 1", scalar=True)
                row = {"月の集計": "中央値" if stat == "median" else "平均", "特殊要因（2020/12〜2021/2）": "除く" if excl else "含む",
                       "仕様": spec, "被説明変数": ycol, "切片": r.params["const"], "傾き（合計）": slope,
                       "傾き＝1 の検定 p 値（HAC）": float(wald.pvalue), "R2": r.rsquared, "月数": len(d)}
                if len(cols) == 1:
                    row["傾きの t（HAC）"] = r.tvalues[cols[0]]
                for test_fy in (2022, 2023, 2024, 2025):
                    tr, te = fy_d < test_fy, fy_d == test_fy
                    rt = sm.OLS(d[ycol][tr], sm.add_constant(d[cols][tr])).fit()
                    pred = rt.predict(sm.add_constant(d[cols][te], has_constant="add"))
                    mae = float(np.abs(d[ycol][te] - pred).mean())
                    naive = float(np.abs(d[ycol][te] - d[ycol][fy_d == test_fy - 1].mean()).mean())
                    row[f"標本外 MAE FY{test_fy}"] = mae
                    row[f"素朴な基準の MAE FY{test_fy}"] = naive
                    if stat == "median" and excl and len(cols) == 1:
                        oos_rows.append({"被説明変数": ycol, "予測する年度": test_fy, "実績の平均": d[ycol][te].mean(), "予測の平均": pred.mean(),
                                         "MAE": mae, "素朴な基準（前年度の平均）の MAE": naive})
                rows.append(row)
FIT = pd.DataFrame(rows)
FIT.round(4).to_csv(os.path.join(PROC, "fuel_price_fit.csv"), index=False, encoding="utf-8-sig")
OOS = pd.DataFrame(oos_rows)
print("\n月の中央値 ＝ 切片 ＋ 傾き × 燃料費の指標（HAC 標準誤差、FY2016〜2026/6）")
show = ["月の集計", "特殊要因（2020/12〜2021/2）", "仕様", "被説明変数", "切片", "傾き（合計）", "傾きの t（HAC）", "傾き＝1 の検定 p 値（HAC）", "R2", "月数"]
print(FIT[show].round(3).to_string(index=False))
print("\n疑似標本外（主の仕様: 中央値・特殊要因を除く・指標1つ。前年度までで推定し、当年度を予測）")
print(OOS.round(2).to_string(index=False))

# ---------------------------------------------------------------- 共和分（エナジー・ファイナンス第4節の手順: 単位根 → 共和分 → 誤差修正）
# 月の中央値の価格 p と燃料費の指標 v（石炭と LNG の平均）が非定常なら、水準の回帰は見せかけの回帰になりうる。
# (i) ADF・KPSS（水準と1階差分）、(ii) Engle–Granger（残差の ADF）と Johansen（トレース）、(iii) DOLS（Stock & Watson 1993）で傾き＝1、
# (iv) マージン m＝p−v（共和分ベクトル (1,−1) を課す）の ADF、(v) VECM の調整係数と半減期。
# 2020/12〜2021/2 は、除いた系列（主）と、含めた系列の両方で示す。
from statsmodels.tsa.stattools import adfuller, kpss, coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM

CO = []
Mm = P.groupby("month")[["p_tohoku", "p_system", "p_hokkaido"]].median().join(VC, how="inner")
Mm = Mm[(Mm.index >= "2016-04-01") & (Mm.index < "2026-07-01")]
for excl in (True, False):
    d0 = Mm[~((Mm.index >= SPECIAL[0]) & (Mm.index <= SPECIAL[1]))] if excl else Mm
    for ycol in ("p_tohoku", "p_system", "p_hokkaido"):
        y, v = d0[ycol].to_numpy(), d0["vc_avg"].to_numpy()
        row = {"特殊要因（2020/12〜2021/2）": "除く" if excl else "含む", "被説明変数": ycol, "月数": len(d0)}
        for nm, s in (("価格", y), ("燃料費", v)):
            row[f"ADF p 値 {nm}（水準）"] = adfuller(s, regression="c", autolag="AIC")[1]
            row[f"ADF p 値 {nm}（差分）"] = adfuller(np.diff(s), regression="c", autolag="AIC")[1]
            with np.errstate(all="ignore"):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    row[f"KPSS p 値 {nm}（水準）"] = kpss(s, regression="c", nlags="auto")[1]
        row["Engle–Granger p 値"] = coint(y, v, trend="c", autolag="AIC")[1]
        jo = coint_johansen(np.column_stack([y, v]), det_order=0, k_ar_diff=2)
        row["Johansen トレース r=0（統計量）"], row["同 5%臨界値"] = jo.lr1[0], jo.cvt[0, 1]
        row["Johansen トレース r≤1（統計量）"], row["同 5%臨界値 r≤1"] = jo.lr1[1], jo.cvt[1, 1]
        # DOLS: y = a + b v + Σ_{j=-2..2} c_j Δv_{t-j}
        dv = pd.Series(v).diff()
        Z = pd.DataFrame({"v": v, **{f"dv{j}": dv.shift(-j) for j in range(-2, 3)}})
        Z = sm.add_constant(Z)
        ok = Z.notna().all(axis=1).to_numpy()
        rd = sm.OLS(y[ok], Z[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
        row["DOLS 傾き"], row["DOLS 傾き＝1 の p 値"] = rd.params["v"], float(rd.t_test("v = 1").pvalue)
        row["マージン p−v の ADF p 値"] = adfuller(y - v, regression="c", autolag="AIC")[1]
        vm = VECM(np.column_stack([y, v]), k_ar_diff=2, coint_rank=1, deterministic="ci").fit()
        a_p = vm.alpha[0, 0]
        row["VECM 調整係数 α（価格）"], row["VECM 調整係数 α（燃料費）"] = a_p, vm.alpha[1, 0]
        row["VECM β（燃料費の係数、価格=1 に基準化）"] = -vm.beta[1, 0] / vm.beta[0, 0]
        row["半減期（月）"] = np.log(0.5) / np.log(1 + a_p) if -1 < a_p < 0 else np.nan
        CO.append(row)
COD = pd.DataFrame(CO)
COD.round(4).to_csv(os.path.join(PROC, "fuel_price_cointegration.csv"), index=False, encoding="utf-8-sig")
print("\n共和分の検定（月の中央値。燃料費は石炭と LNG の平均）")
print(COD.round(3).T.to_string())
