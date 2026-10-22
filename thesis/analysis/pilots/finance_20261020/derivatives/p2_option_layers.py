#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット2: 蓄電池＝日次スプレッドオプションの価値の層分解（北海道 p_hokkaido）

商品ストレージ評価の intrinsic / extrinsic 分解を日次に適用する。
 日次ペイオフ（円/kW-日、4h・η=0.85、充電→放電、日をまたがない）:
   X_w = 4·(η·P̄_dis(w) − P̄_chg(w))  （w = 充放電の時間窓）
 層:
   (I)  ローリング・イントリンジック = 事前に固定した窓 w_c（戦略c: 過去28日・同曜日区分の平均価格の
        上位4h/下位4h。北海道の時間別フォワードカーブが存在しないため、気候値をフォワードの代理とする）
        で得る実現粗利 E[X_{w_c}]
   (II) 休止オプション = E[max(X_{w_c},0)] − E[X_{w_c}]（固定窓が損失になる日に休む権利。
        事後の符号を使うので、指値入札で取れる価値の上限）
   (III) 窓の切替価値（エクストリンジック）= PF − E[max(X_{w_c},0)]（当日の実現価格で窓を選び直す価値）
   PF = (I)+(II)+(III)、capture率(c) = (I)/PF
 加えて:
   - 年度別（FY2016〜25）と季節×風力三分位（FY2023〜25）で層を出す
   - Bachelier（正規）で (I)+(II) を μ_X, σ_X から閉形式で再現できるか、ベガ φ(μ/σ) とマネーネス μ/σ
   - レベル・デルタ: 日次 PF・X_c を日平均価格に回帰（季節×年度FE）→「蓄電池は水準にほぼデルタ中立」
出力: このフォルダの p2_*.csv（リポジトリには書き込まない）
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

OUT = os.path.dirname(os.path.abspath(__file__))
PANEL = "/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv"
ETA, H = 0.85, 4
SEASON = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
          3: "不需要期", 4: "不需要期", 5: "不需要期", 6: "不需要期", 10: "不需要期", 11: "不需要期"}

hp = pd.read_csv(PANEL, parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
hp["solar_pre"] = hp["solar"].fillna(0) + hp["solar_curt"].fillna(0)
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
days = P.index
wkP = pd.Series(days.dayofweek >= 5, index=days)
arr = P.to_numpy()


def win(v):
    o = np.argsort(v, kind="stable")
    return o[-H:], o[:H]


rows = []
for i, d in enumerate(days):
    p = arr[i]
    dis, chg = win(p)
    xpf = H * (ETA * p[dis].mean() - p[chg].mean())
    rec = {"day": d, "pf": max(0.0, xpf), "pf_raw": xpf, "level": p.mean(),
           "top4": p[dis].mean(), "bot4": p[chg].mean()}
    hist = [j for j in range(max(0, i - 29), i) if wkP.iloc[j] == wkP.iloc[i]]
    if len(hist) >= 5:
        prof = arr[hist].mean(axis=0)
        dc, cc = win(prof)
        rec["xc"] = H * (ETA * p[dc].mean() - p[cc].mean())
        rec["pdis_c"], rec["pchg_c"] = p[dc].mean(), p[cc].mean()
    rows.append(rec)
bt = pd.DataFrame(rows).set_index("day")
g = hp.groupby("day")
bt["wind"] = g["wind_pre"].sum().reindex(bt.index) / 1000
bt["solar"] = g["solar_pre"].sum().reindex(bt.index) / 1000
bt["demand"] = g["demand"].sum().reindex(bt.index) / 1000
bt["fy"] = bt.index.year - (bt.index.month < 4).astype(int)
bt["season"] = bt.index.month.map(SEASON)
bt = bt.dropna(subset=["xc"])
bt["xc_pos"] = bt["xc"].clip(lower=0)


def layers(df):
    pf, xc, xcp = df["pf"].mean(), df["xc"].mean(), df["xc_pos"].mean()
    mu, sd = df["xc"].mean(), df["xc"].std()
    z = mu / sd if sd > 0 else np.inf
    bach = mu * norm.cdf(z) + sd * norm.pdf(z)
    return {"日数": len(df), "PF": pf, "(I)イントリンジック": xc, "(II)休止": xcp - xc, "(III)切替": pf - xcp,
            "capture(I/PF)": xc / pf, "(II)/PF": (xcp - xc) / pf, "(III)/PF": (pf - xcp) / pf,
            "μ_Xc": mu, "σ_Xc": sd, "マネーネスμ/σ": z, "ベガφ(μ/σ)": norm.pdf(z),
            "Bachelier": bach, "実現E[max(Xc,0)]": xcp,
            "固定窓で損失の日の比率": (df["xc"] < 0).mean(),
            "PF=0の日の比率": (df["pf_raw"] <= 0).mean()}


# ---- 年度別（円/kW-年 = 日次平均×日数、ここでは年合計で表示）----
fy_rows = []
for fy, df in bt[bt["fy"].between(2016, 2025)].groupby("fy"):
    r = layers(df)
    n = len(df)
    fy_rows.append({"FY": fy, **{k: v for k, v in r.items()},
                    "PF年合計": df["pf"].sum(), "(I)年合計": df["xc"].sum(),
                    "(II)年合計": (df["xc_pos"] - df["xc"]).sum(), "(III)年合計": (df["pf"] - df["xc_pos"]).sum()})
fyt = pd.DataFrame(fy_rows)
fyt.to_csv(os.path.join(OUT, "p2_layers_by_fy.csv"), index=False, encoding="utf-8-sig")

# ---- 季節×風力三分位（FY2023-25、三分位は季節内の3年プール）----
st_rows = []
sub = bt[bt["fy"].isin([2023, 2024, 2025])].copy()
for s, df in sub.groupby("season"):
    q = df["wind"].quantile([1 / 3, 2 / 3])
    df = df.assign(ter=np.select([df["wind"] <= q.iloc[0], df["wind"] >= q.iloc[1]], ["1小", "3大"], "2中"))
    for ter, c in list(df.groupby("ter")) + [("全体", df)]:
        st_rows.append({"季節": s, "風力三分位": ter, "風力GWh/日": c["wind"].mean(), **layers(c)})
stt = pd.DataFrame(st_rows)
stt.to_csv(os.path.join(OUT, "p2_layers_by_season_wind.csv"), index=False, encoding="utf-8-sig")

# ---- レベル・デルタ（水準に対する感応度）と風力のデルタ ----
# 日次 PF・X_c・各脚 を 日平均価格 に回帰（季節×年度FE）。HC3 と Newey-West(7)
drows = []
for pname, fys in {"FY2023-25": [2023, 2024, 2025], "FY2016-25": list(range(2016, 2026))}.items():
    d = bt[bt["fy"].isin(fys)].copy()
    fe = pd.get_dummies(d["season"] + "_" + d["fy"].astype(str), drop_first=True).astype(float)
    for y in ["pf", "xc", "top4", "bot4"]:
        X = sm.add_constant(pd.concat([d[["level"]], fe], axis=1))
        m = sm.OLS(d[y], X).fit(cov_type="HC3")
        mn = sm.OLS(d[y], X).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
        # 部分R²（level が FE の残差をどれだけ説明するか）
        r0 = sm.OLS(d[y], sm.add_constant(fe)).fit()
        drows.append({"期間": pname, "被説明": y, "β_level": m.params["level"], "t_HC3": m.tvalues["level"],
                      "t_NW7": mn.tvalues["level"],
                      "部分R2(level)": 1 - m.ssr / r0.ssr})
    # 風力・太陽光（季節別係数）→ 各脚・X_c・PF（24_vol_verification と同じ右辺: 季節×電源、需要、FY・季節FE）
    Xr = pd.DataFrame(index=d.index)
    for s in ["夏", "冬", "不需要期"]:
        msk = (d["season"] == s).astype(float)
        Xr[f"wind_{s}"] = d["wind"] * msk
        Xr[f"solar_{s}"] = d["solar"] * msk
    Xr["demand"] = d["demand"]
    Xr = pd.concat([Xr, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                    pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    Xr = sm.add_constant(Xr)
    for y in ["level", "top4", "bot4", "pdis_c", "pchg_c", "xc", "pf"]:
        m = sm.OLS(d[y], Xr).fit(cov_type="HC3")
        mn = sm.OLS(d[y], Xr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
        for s in ["夏", "冬", "不需要期"]:
            for f in ["wind", "solar"]:
                k = f"{f}_{s}"
                sdf = d.loc[d["season"] == s, f].std()
                drows.append({"期間": pname, "被説明": y, "説明": k, "β": m.params[k], "t_HC3": m.tvalues[k],
                              "p_NW7": mn.pvalues[k], "1σ効果": m.params[k] * sdf})
dl = pd.DataFrame(drows)
dl.to_csv(os.path.join(OUT, "p2_level_delta_and_factor.csv"), index=False, encoding="utf-8-sig")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print("=== 年度別の層（年合計、円/kW-年）===")
print(fyt[["FY", "PF年合計", "(I)年合計", "(II)年合計", "(III)年合計", "capture(I/PF)", "(II)/PF", "(III)/PF",
           "マネーネスμ/σ", "ベガφ(μ/σ)", "固定窓で損失の日の比率"]].round(3).to_string(index=False))
print("\n=== 季節×風力三分位の層（日次平均、円/kW-日、FY2023-25）===")
print(stt[["季節", "風力三分位", "日数", "風力GWh/日", "PF", "(I)イントリンジック", "(II)休止", "(III)切替",
           "capture(I/PF)", "(III)/PF", "μ_Xc", "σ_Xc", "マネーネスμ/σ", "ベガφ(μ/σ)", "Bachelier",
           "実現E[max(Xc,0)]"]].round(3).to_string(index=False))
print("\n=== レベル・デルタ（日平均価格1円/kWh上昇あたりの変化、季節×年度FE）===")
print(dl[dl["説明"].isna()][["期間", "被説明", "β_level", "t_HC3", "t_NW7", "部分R2(level)"]].round(3).to_string(index=False))
print("\n=== 風力・太陽光の季節別係数（1σ効果、脚は円/kWh、X_c・PFは円/kW-日）===")
w = dl[dl["説明"].notna()].copy()
print(w.pivot_table(index=["期間", "説明"], columns="被説明", values="1σ効果").round(3)
      [["level", "top4", "bot4", "pdis_c", "pchg_c", "xc", "pf"]].to_string())
print("\nNW7 p値")
print(w.pivot_table(index=["期間", "説明"], columns="被説明", values="p_NW7").round(3)
      [["level", "top4", "bot4", "pdis_c", "pchg_c", "xc", "pf"]].to_string())
