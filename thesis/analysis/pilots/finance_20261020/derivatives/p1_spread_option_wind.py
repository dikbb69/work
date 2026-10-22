#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット1: 蓄電池＝日次スプレッドオプション（交換オプション）としての分解（北海道）

問い: 風力の多い日に蓄電池の価値が増えないのは、オプション理論でいえば
      「風力が放電窓と充電窓の両方を同じだけ動かす共通因子（ρ が高い）なので
        交換オプションのスプレッド・ボラティリティ σ_X に寄与しない」からか。

日次ペイオフ（4h・η=0.85・1日1サイクル、円/kW-日）:
    X_d = 4 × (η·P_dis,d − P_chg,d)
    P_dis = 放電窓4時間の平均価格, P_chg = 充電窓4時間の平均価格
窓の定義:
    (E) 事前固定窓: 季節（報告用3区分）×期間の平均時刻プロファイルの上位4h/下位4h
        → 「フォワードカーブ」に対する intrinsic スケジュール
    (P) 事後窓: 当日の実現価格の上位4h/下位4h（=完全予見、PF）
分散の恒等式（Margrabe 型）:
    σ_X² = 16·[η²σ_dis² + σ_chg² − 2ηρσ_disσ_chg]
オプション価値（1日あたり、年間は ×日数）:
    Bachelier（正規）: E[max(X,0)] = μΦ(μ/σ) + σφ(μ/σ)
    Margrabe（対数正規・モーメント一致）
    実現値 mean(max(X_d,0))、PF mean、intrinsic max(μ_X,0)

出力: このフォルダの p1_*.csv（リポジトリには書き込まない）
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

OUT = os.path.dirname(os.path.abspath(__file__))
PANEL = "/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv"
ETA = 0.85
H = 4

SEASONS = {"夏(7-9)": [7, 8, 9], "冬(12-2)": [12, 1, 2], "不需要期": [3, 4, 5, 6, 10, 11]}
PERIODS = {"FY2023-25": [2023, 2024, 2025], "FY2016-19": [2016, 2017, 2018, 2019],
           "FY2016-25": list(range(2016, 2026))}

hp = pd.read_csv(PANEL, parse_dates=["ts"])
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
hp["solar_pre"] = hp["solar"].fillna(0) + hp["solar_curt"].fillna(0)

P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
daily = pd.DataFrame(index=P.index)
daily["fy"] = daily.index.year - (daily.index.month < 4).astype(int)
daily["month"] = daily.index.month
g = hp.groupby("day")
daily["wind_gwh"] = g["wind_pre"].sum().reindex(daily.index) / 1000
daily["solar_gwh"] = g["solar_pre"].sum().reindex(daily.index) / 1000
daily["demand_gwh"] = g["demand"].sum().reindex(daily.index) / 1000
daily["season"] = None
for s, ms in SEASONS.items():
    daily.loc[daily["month"].isin(ms), "season"] = s

arr = P.to_numpy()
srt = np.sort(arr, axis=1)
daily["P_top"] = srt[:, -H:].mean(axis=1)
daily["P_bot"] = srt[:, :H].mean(axis=1)
daily["PF"] = np.maximum(0.0, H * (ETA * daily["P_top"] - daily["P_bot"]))  # 円/kW-日
daily["TB4h"] = daily["P_top"] - daily["P_bot"]
daily["level"] = arr.mean(axis=1)


def bachelier(mu, sd):
    if sd <= 0:
        return max(mu, 0.0)
    z = mu / sd
    return mu * norm.cdf(z) + sd * norm.pdf(z)


def margrabe_mm(m1, s1, m2, s2, rho):
    """モーメント一致の対数正規で max(S1−S2,0) を評価（S1=η·P_dis, S2=P_chg）"""
    v1 = np.log(1 + (s1 / m1) ** 2)
    v2 = np.log(1 + (s2 / m2) ** 2)
    cov = np.log(1 + rho * s1 * s2 / (m1 * m2))
    sig2 = v1 + v2 - 2 * cov
    if sig2 <= 0:
        return max(m1 - m2, 0.0), 0.0
    sig = np.sqrt(sig2)
    d1 = (np.log(m1 / m2) + 0.5 * sig2) / sig
    return m1 * norm.cdf(d1) - m2 * norm.cdf(d1 - sig), sig


def windows(profile):
    o = profile.sort_values()
    return list(o.index[-H:]), list(o.index[:H])


rows, wrows = [], []
for pname, fys in PERIODS.items():
    for s in SEASONS:
        d = daily[(daily["season"] == s) & daily["fy"].isin(fys)].copy()
        # 事前固定窓（季節×期間の平均プロファイル）
        prof = P.loc[d.index].mean()
        dis, chg = windows(prof)
        wrows.append({"期間": pname, "季節": s, "放電窓": dis, "充電窓": chg})
        d["P_dis"] = P.loc[d.index, dis].mean(axis=1)
        d["P_chg"] = P.loc[d.index, chg].mean(axis=1)
        d["X"] = H * (ETA * d["P_dis"] - d["P_chg"])
        q = d["wind_gwh"].quantile([1 / 3, 2 / 3])
        d["ter"] = np.select([d["wind_gwh"] <= q.iloc[0], d["wind_gwh"] >= q.iloc[1]],
                             ["1小", "3大"], "2中")
        for ter, c in list(d.groupby("ter")) + [("全体", d)]:
            # 三分位ごとの条件付き窓（風力予報を知っている場合のフォワード）
            dis_c, chg_c = windows(P.loc[c.index].mean())
            Xc = H * (ETA * P.loc[c.index, dis_c].mean(axis=1) - P.loc[c.index, chg_c].mean(axis=1))
            m_d, m_c = c["P_dis"].mean(), c["P_chg"].mean()
            s_d, s_c = c["P_dis"].std(), c["P_chg"].std()
            rho = c[["P_dis", "P_chg"]].corr().iloc[0, 1]
            muX, sdX = c["X"].mean(), c["X"].std()
            sd_identity = H * np.sqrt(ETA**2 * s_d**2 + s_c**2 - 2 * ETA * rho * s_d * s_c)
            marg, sig_ln = margrabe_mm(ETA * m_d, ETA * s_d, m_c, s_c, rho)
            rho_pf = c[["P_top", "P_bot"]].corr().iloc[0, 1]
            rows.append({
                "期間": pname, "季節": s, "風力三分位": ter, "日数": len(c),
                "風力GWh/日": c["wind_gwh"].mean(),
                "日平均価格": c["level"].mean(), "sd日平均": c["level"].std(),
                "μ_dis": m_d, "μ_chg": m_c, "σ_dis": s_d, "σ_chg": s_c, "ρ(dis,chg)": rho,
                "σ_X(円/kW日)": sdX, "σ_X恒等式": sd_identity,
                "intrinsic=max(μX,0)": max(muX, 0.0),
                "Bachelier": bachelier(muX, sdX),
                "Margrabe(mm)": H * marg,
                "実現max(X,0)": np.maximum(c["X"], 0).mean(),
                "条件付き窓のmax(μX,0)": max(Xc.mean(), 0.0),
                "PF(事後窓)": c["PF"].mean(),
                "μ_top": c["P_top"].mean(), "μ_bot": c["P_bot"].mean(),
                "σ_top": c["P_top"].std(), "σ_bot": c["P_bot"].std(), "ρ(top,bot)": rho_pf,
                "TB4h": c["TB4h"].mean(),
            })

res = pd.DataFrame(rows)
res.to_csv(os.path.join(OUT, "p1_spread_option_by_wind_tercile.csv"), index=False, encoding="utf-8-sig")
pd.DataFrame(wrows).to_csv(os.path.join(OUT, "p1_windows.csv"), index=False, encoding="utf-8-sig")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
show = ["期間", "季節", "風力三分位", "日数", "風力GWh/日", "日平均価格", "μ_dis", "μ_chg", "σ_dis", "σ_chg",
        "ρ(dis,chg)", "σ_X(円/kW日)", "intrinsic=max(μX,0)", "Bachelier", "Margrabe(mm)", "実現max(X,0)",
        "条件付き窓のmax(μX,0)", "PF(事後窓)"]
print(pd.DataFrame(wrows).to_string(index=False))
print(res[show].round(2).to_string(index=False))
print()
print(res[["期間", "季節", "風力三分位", "μ_top", "μ_bot", "σ_top", "σ_bot", "ρ(top,bot)", "TB4h", "PF(事後窓)"]]
      .round(2).to_string(index=False))

# ------------------------------------------------------------------
# 因子分解: 各脚（放電窓・充電窓）と交換オプションの原資 X の日間分散のうち、
# 風力・太陽光で説明される部分（年度FE・需要を統制、季節内回帰）
# ------------------------------------------------------------------
frows = []
for pname in ["FY2023-25", "FY2016-25"]:
    fys = PERIODS[pname]
    for s in SEASONS:
        d = daily[(daily["season"] == s) & daily["fy"].isin(fys)].copy()
        dis, chg = windows(P.loc[d.index].mean())
        d["P_dis"] = P.loc[d.index, dis].mean(axis=1)
        d["P_chg"] = P.loc[d.index, chg].mean(axis=1)
        d["X"] = H * (ETA * d["P_dis"] - d["P_chg"])
        Xr = pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float)
        Xr["wind"] = d["wind_gwh"]
        Xr["solar"] = d["solar_gwh"]
        Xr["demand"] = d["demand_gwh"]
        Xr = sm.add_constant(Xr)
        out = {"期間": pname, "季節": s, "放電窓": str(dis), "充電窓": str(chg)}
        betas = {}
        for y in ["P_dis", "P_chg", "X", "P_top", "P_bot", "PF"]:
            yv = d[y] if y not in ("P_dis", "P_chg", "P_top", "P_bot") else d[y]
            m = sm.OLS(yv, Xr).fit(cov_type="HC3")
            betas[y] = m
            for f in ["wind", "solar"]:
                b = m.params[f]
                sd_f = d[f + "_gwh"].std()
                out[f"β_{f}[{y}]"] = b
                out[f"t_{f}[{y}]"] = m.tvalues[f]
                # 1σ の発電量変動が動かす量（脚は円/kWh、X・PF は円/kW-日）
                out[f"1σ効果_{f}[{y}]"] = b * sd_f
        # 風力成分の相殺率: 脚ごとの風力成分を X に持ち込んだときに残る割合
        for f in ["wind", "solar"]:
            bd, bc = out[f"β_{f}[P_dis]"], out[f"β_{f}[P_chg]"]
            gross = H * np.sqrt((ETA * bd) ** 2 + bc ** 2)  # ρ=0 なら X に入る大きさ
            net = H * abs(ETA * bd - bc)                    # 実際（共通因子なので相殺）
            out[f"{f}_相殺後/相殺前"] = net / gross if gross > 0 else np.nan
        # Pratt 型の分散シェア β·Cov(f,y)/Var(y)
        for y in ["P_dis", "P_chg", "X"]:
            for f in ["wind", "solar"]:
                out[f"分散シェア_{f}[{y}]"] = (out[f"β_{f}[{y}]"] * np.cov(d[f + "_gwh"], d[y])[0, 1]
                                             / d[y].var())
        frows.append(out)
fac = pd.DataFrame(frows)
fac.to_csv(os.path.join(OUT, "p1_factor_decomposition.csv"), index=False, encoding="utf-8-sig")
cols = ["期間", "季節", "1σ効果_wind[P_dis]", "1σ効果_wind[P_chg]", "1σ効果_wind[X]", "t_wind[X]",
        "wind_相殺後/相殺前", "1σ効果_solar[P_dis]", "1σ効果_solar[P_chg]", "1σ効果_solar[X]", "t_solar[X]",
        "solar_相殺後/相殺前", "分散シェア_wind[P_dis]", "分散シェア_wind[P_chg]", "分散シェア_wind[X]",
        "分散シェア_solar[P_dis]", "分散シェア_solar[P_chg]", "分散シェア_solar[X]"]
print()
print(fac[cols].round(3).T.to_string())
