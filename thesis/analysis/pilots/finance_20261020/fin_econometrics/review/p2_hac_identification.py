#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット2: 主回帰（原稿 5.2.3／表6.2）の推論の頑健性と、因果解釈のための識別チェック

(a) 推論: HC3（原稿）、Newey-West lag 7/14/28、Andrews (1991) AR(1) プラグインの自動帯域、
    年月クラスタ（120クラスタ）、FGLS（AR(1) 誤差、GLSAR 反復）。
    再エネ（気象）は厳密外生とみなせるため、系列相関を FGLS でモデル化して効率を上げることも正当化される。
(b) 識別: 係数の安定性（統制の追加）
    S0 需要なし → S1 主仕様 → S2 +曜日・祝日 → S3 月固定効果 → S4 年月固定効果（S2に追加）
    → S5 +日平均価格の7日ラグ（F&O 型） → S6 +翌日・前日の発電量（リード＝プラセボ、ラグ＝動学）
    Oster (2019) の近似式による δ（係数をゼロにするのに必要な「観察されない交絡の相対的な強さ」）
(c) 需要の内生性: 曜日・祝日ダミーを操作変数とする 2SLS（気温データがリポジトリに無いための暫定）
(d) 出力制御: 制御前（主仕様）と制御後の発電量で係数を比較

出力: out/p2_*.csv（リポジトリには書き込まない）
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, MAIN_SEASONS, KEYS, build_daily, design, load_hourly, stars  # noqa: E402

AREAS = [("hokkaido", "p_hokkaido"), ("kyushu", "p_kyushu")]


def holiday_flag(idx):
    """jpholiday が無いので近似: 土日＋年末年始(12/29-1/3)＋GW(5/3-5/5)＋お盆(8/13-8/16)"""
    m, dd = idx.month, idx.day
    h = (idx.dayofweek >= 5)
    h |= ((m == 12) & (dd >= 29)) | ((m == 1) & (dd <= 3))
    h |= (m == 5) & (dd >= 3) & (dd <= 5)
    h |= (m == 8) & (dd >= 13) & (dd <= 16)
    return pd.Series(h.astype(float), index=idx)


def andrews_bw(resid):
    """Andrews (1991) Bartlett カーネルの AR(1) プラグイン帯域"""
    e = np.asarray(resid)
    rho = float(np.dot(e[1:], e[:-1]) / np.dot(e[:-1], e[:-1]))
    a1 = 4 * rho ** 2 / ((1 - rho) ** 2 * (1 + rho) ** 2)
    return rho, int(np.floor(1.1447 * (a1 * len(e)) ** (1 / 3)))


def inference_table(area, d, ycol):
    X = design(d)
    y = d[ycol]
    ols = sm.OLS(y, X)
    fits = {"HC3": ols.fit(cov_type="HC3")}
    for L in (7, 14, 28):
        fits[f"NW{L}"] = ols.fit(cov_type="HAC", cov_kwds={"maxlags": L})
    rho, bw = andrews_bw(fits["HC3"].resid)
    fits[f"NW-Andrews({bw})"] = ols.fit(cov_type="HAC", cov_kwds={"maxlags": bw})
    ym = (d.index.year * 100 + d.index.month).to_numpy()
    fits["年月クラスタ"] = ols.fit(cov_type="cluster", cov_kwds={"groups": ym})
    # FGLS AR(1)
    gls = sm.GLSAR(y, X, rho=1).iterative_fit(maxiter=20)
    rows = []
    for key in KEYS:
        r = {"area": area, "y": ycol, "係数": key, "OLS推定値": fits["HC3"].params[key],
             "残差ρ1": rho, "Andrews帯域": bw}
        for nm, f in fits.items():
            nm2 = "NW-Andrews" if nm.startswith("NW-Andrews") else nm
            r[f"SE_{nm2}"] = f.bse[key]
            r[f"p_{nm2}"] = f.pvalues[key]
        r["FGLS推定値"] = gls.params[key]
        r["SE_FGLS"] = gls.bse[key]
        r["p_FGLS"] = gls.pvalues[key]
        r["FGLS_ρ"] = float(gls.model.rho[0]) if np.ndim(gls.model.rho) else float(gls.model.rho)
        rows.append(r)
    return rows


def add_controls(d, X, spec, area):
    X = X.copy()
    if spec in ("S2", "S3", "S4", "S5", "S6", "IV"):
        dow = pd.get_dummies(d.index.dayofweek, prefix="dow", drop_first=True).astype(float)
        dow.index = d.index
        X = pd.concat([X, dow], axis=1)
        X["holiday"] = holiday_flag(d.index)
    if spec == "S3":
        # 季節FEを月FEに置き換え（季節×再エネ交互作用は維持）
        X = X.drop(columns=[c for c in X.columns if c.startswith("ssn_")])
        mon = pd.get_dummies(d.index.month, prefix="m", drop_first=True).astype(float)
        mon.index = d.index
        X = pd.concat([X, mon], axis=1)
    if spec in ("S4", "S5", "S6"):
        # 年月固定効果（120セル）で FY・季節・月の FE を置き換え: 識別は同じ月の中の日次変動のみ
        X = X.drop(columns=[c for c in X.columns if c.startswith("ssn_") or c.startswith("fy_")])
        ym = pd.get_dummies(d.index.year * 100 + d.index.month, prefix="ym", drop_first=True).astype(float)
        ym.index = d.index
        X = pd.concat([X, ym], axis=1)
    if spec in ("S5",):
        for L in range(1, 8):
            X[f"lag_mean_p{L}"] = d["mean_p"].shift(L)
    if spec in ("S6",):
        for src in ("solar", "wind"):
            for s in MAIN_SEASONS:
                m = (d["season"] == s).astype(float)
                X[f"{src}_{s}_lead1"] = d[src].shift(-1) * m
                X[f"{src}_{s}_lag1"] = d[src].shift(1) * m
    return X


def two_sls(y, X, endog, Z_extra, L=7):
    """2SLS（内生: endog 列、追加の操作変数: Z_extra）＋ NW(L) 共分散"""
    exog = X.drop(columns=[endog])
    Z = pd.concat([exog, Z_extra], axis=1)
    fs = sm.OLS(X[endog], Z).fit()
    # 第1段の F（追加の操作変数の結合有意性、HAC）
    fs_h = sm.OLS(X[endog], Z).fit(cov_type="HAC", cov_kwds={"maxlags": L})
    R = np.zeros((Z_extra.shape[1], Z.shape[1]))
    for i, c in enumerate(Z_extra.columns):
        R[i, list(Z.columns).index(c)] = 1
    F1 = float(fs_h.f_test(R).fvalue)
    Xhat = X.copy()
    Xhat[endog] = fs.fittedvalues
    Xn, Xh, yn = X.to_numpy(), Xhat.to_numpy(), y.to_numpy()
    A = np.linalg.inv(Xh.T @ Xh)
    b = A @ Xh.T @ yn
    e = yn - Xn @ b
    G = Xh * e[:, None]
    S = G.T @ G
    for j in range(1, L + 1):
        w = 1 - j / (L + 1)
        Gj = G[j:].T @ G[:-j]
        S += w * (Gj + Gj.T)
    V = A @ S @ A
    se = np.sqrt(np.diag(V))
    return pd.Series(b, index=X.columns), pd.Series(se, index=X.columns), F1


def oster_delta(b_short, r_short, b_long, r_long, rmax_mult=1.3):
    """Oster (2019) の近似: β*=0 とする δ = β̃(R̃−R̊) / ((β̊−β̃)(Rmax−R̃))、Rmax=min(1, 1.3R̃)"""
    rmax = min(1.0, rmax_mult * r_long)
    den = (b_short - b_long) * (rmax - r_long)
    return np.inf if den == 0 else b_long * (r_long - r_short) / den


def main():
    inf_rows, stab_rows, iv_rows, curt_rows, lead_rows = [], [], [], [], []
    for area, pcol in AREAS:
        d = build_daily(area, pcol)
        for ycol in ("mean_p", "tb4", "sd"):
            inf_rows += inference_table(area, d, ycol)

        # (b) 係数の安定性
        for ycol in ("mean_p", "tb4"):
            base = design(d)
            specs = {}
            # S0: 需要なし
            specs["S0 需要なし"] = base.drop(columns=["demand"])
            specs["S1 主仕様"] = base
            specs["S2 +曜日・祝日"] = add_controls(d, base, "S2", area)
            specs["S3 +月FE"] = add_controls(d, base, "S3", area)
            specs["S4 +年月FE"] = add_controls(d, base, "S4", area)
            specs["S5 +価格7日ラグ"] = add_controls(d, base, "S5", area)
            specs["S6 +発電量リード・ラグ"] = add_controls(d, base, "S6", area)
            res = {}
            for nm, X in specs.items():
                ok = X.notna().all(axis=1)
                f = sm.OLS(d.loc[ok, ycol], X.loc[ok]).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
                res[nm] = f
                for key in KEYS:
                    stab_rows.append({"area": area, "y": ycol, "仕様": nm, "係数": key,
                                      "推定値": f.params[key], "SE_NW7": f.bse[key], "p_NW7": f.pvalues[key],
                                      "R2": f.rsquared, "n": int(f.nobs)})
                if nm.startswith("S6"):
                    for key in KEYS:
                        for suf in ("lead1", "lag1"):
                            k2 = f"{key}_{suf}"
                            lead_rows.append({"area": area, "y": ycol, "係数": k2,
                                              "推定値": f.params[k2], "SE_NW7": f.bse[k2], "p_NW7": f.pvalues[k2]})
            # Oster δ: 短い回帰 = S0（需要なし）、長い回帰 = S4（需要＋曜日祝日＋年月FE）
            for key in KEYS:
                bs, rs = res["S0 需要なし"].params[key], res["S0 需要なし"].rsquared
                bl, rl = res["S4 +年月FE"].params[key], res["S4 +年月FE"].rsquared
                stab_rows.append({"area": area, "y": ycol, "仕様": "Oster δ (S0→S4, Rmax=1.3R̃)", "係数": key,
                                  "推定値": oster_delta(bs, rs, bl, rl), "SE_NW7": np.nan, "p_NW7": np.nan,
                                  "R2": np.nan, "n": np.nan})

            # (c) 2SLS: 需要を曜日・祝日ダミーで操作
            X = design(d)
            dow = pd.get_dummies(d.index.dayofweek, prefix="dow", drop_first=True).astype(float)
            dow.index = d.index
            Zx = pd.concat([dow, holiday_flag(d.index).rename("holiday")], axis=1)
            b, se, F1 = two_sls(d[ycol], X, "demand", Zx, L=7)
            ols = sm.OLS(d[ycol], X).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
            for key in KEYS + ["demand"]:
                iv_rows.append({"area": area, "y": ycol, "係数": key, "OLS": ols.params[key], "SE_OLS_NW7": ols.bse[key],
                                "2SLS": b[key], "SE_2SLS_NW7": se[key],
                                "p_2SLS": 2 * (1 - stats.norm.cdf(abs(b[key] / se[key]))), "第1段F(HAC)": F1})

        # (d) 出力制御: 制御後の発電量で同じ回帰
        p = load_hourly(area)
        p["day"] = p["ts"].dt.normalize()
        post = p.groupby("day")[["solar", "wind"]].sum() / 1000
        d2 = d.copy()
        d2["solar"] = post.loc[d2.index, "solar"]
        d2["wind"] = post.loc[d2.index, "wind"]
        for ycol in ("mean_p", "tb4"):
            f1 = sm.OLS(d[ycol], design(d)).fit(cov_type="HC3")
            f2 = sm.OLS(d2[ycol], design(d2)).fit(cov_type="HC3")
            for key in KEYS:
                curt_rows.append({"area": area, "y": ycol, "係数": key, "制御前(主仕様)": f1.params[key],
                                  "制御後": f2.params[key], "差": f2.params[key] - f1.params[key]})

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    inf = pd.DataFrame(inf_rows)
    stab = pd.DataFrame(stab_rows)
    iv = pd.DataFrame(iv_rows)
    curt = pd.DataFrame(curt_rows)
    lead = pd.DataFrame(lead_rows)
    for nm, df in (("inference", inf), ("stability", stab), ("iv_demand", iv), ("curtailment", curt), ("lead_lag", lead)):
        df.to_csv(os.path.join(OUT, f"p2_{nm}.csv"), index=False, encoding="utf-8-sig")

    print("=== (a) 推論の頑健性（星: ***1% **5% *10%） ===")
    cols = ["HC3", "NW7", "NW14", "NW28", "NW-Andrews", "年月クラスタ"]
    for (area, y), g in inf.groupby(["area", "y"], sort=False):
        print(f"--- {area} {y}  残差ρ1={g['残差ρ1'].iloc[0]:.3f} Andrews帯域={g['Andrews帯域'].iloc[0]} ---")
        t = pd.DataFrame({"係数": g["係数"], "推定値": g["OLS推定値"].round(3)})
        for c in cols:
            t[c] = [f"{se:.3f}{stars(pv)}" for se, pv in zip(g[f"SE_{c}"], g[f"p_{c}"])]
        t["FGLS(AR1)"] = [f"{b:+.3f}({se:.3f}){stars(pv)}" for b, se, pv in zip(g["FGLS推定値"], g["SE_FGLS"], g["p_FGLS"])]
        t["FGLS_ρ"] = g["FGLS_ρ"].round(3).to_numpy()
        print(t.to_string(index=False))

    print("\n=== (b) 係数の安定性（NW7、星付き） ===")
    for (area, y), g in stab.groupby(["area", "y"], sort=False):
        g = g.copy()
        g["表示"] = [f"{v:+.3f}{stars(pv)}" if not np.isnan(pv) else f"{v:.2f}" for v, pv in zip(g["推定値"], g["p_NW7"])]
        t = g.pivot(index="係数", columns="仕様", values="表示").loc[KEYS]
        t = t[[c for c in g["仕様"].unique()]]
        r2 = g.dropna(subset=["R2"]).groupby("仕様", sort=False)["R2"].first().round(3)
        print(f"--- {area} {y} ---")
        print(t.to_string())
        print("R2:", r2.to_dict())

    print("\n=== (b') リード（プラセボ）とラグの係数（S6、NW7） ===")
    lead["表示"] = [f"{v:+.3f}{stars(pv)}" for v, pv in zip(lead["推定値"], lead["p_NW7"])]
    print(lead.pivot_table(index="係数", columns=["area", "y"], values="表示", aggfunc="first").to_string())

    print("\n=== (c) 需要を曜日・祝日で操作した 2SLS（NW7） ===")
    iv["OLS表示"] = [f"{v:+.3f}" for v in iv["OLS"]]
    iv["2SLS表示"] = [f"{v:+.3f}{stars(pv)}" for v, pv in zip(iv["2SLS"], iv["p_2SLS"])]
    print(iv[["area", "y", "係数", "OLS表示", "2SLS表示", "SE_2SLS_NW7", "第1段F(HAC)"]].round(3).to_string(index=False))

    print("\n=== (d) 制御前 vs 制御後の発電量 ===")
    print(curt.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
