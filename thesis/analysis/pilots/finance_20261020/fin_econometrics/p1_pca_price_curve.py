#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット1: 日次24時間価格ベクトルの主成分分析（Litterman-Scheinkman 型の level / slope / curvature）
と、因子スコアの再エネ回帰（原稿 5.2.3 と同じ右辺、HC3 と Newey-West）

問い: 原稿 6.2 の「風力は水準（日平均）だけを動かし、日内形状（TB4h）を動かさない／太陽光は形状を動かす」
      という分離を、ファイナンスの標準手法（イールドカーブの主成分分解）で裏付けられるか。

設計:
  P_d = (p_d,0, ..., p_d,23)  北海道エリアプライス（時間値、FY2016-25、24時間そろった日）
  (A) 主仕様: 各時刻の価格から FY×季節（報告用3区分）×時刻 の平均を除いた偏差ベクトルを PCA
      → 回帰の FY 固定効果・季節固定効果に対応する「年度・季節内の日々の変動」の因子構造
  (B) 参考: 全期間平均だけを除いた生の偏差の PCA（燃料危機の水準シフトが入る）
  (C) 季節別 PCA（主仕様の偏差を季節ごとに分解）
  (D) FY2023-25 のみ
  因子スコア f_k,d = v_k'(P_d - 平均) を被説明変数に、common.design() の右辺で OLS
  （HC3、NW lag 7・14）。線形性より、因子回帰の係数 = v_k' × 時刻別回帰の係数ベクトル。

  追加: 時刻別回帰（24本、同一右辺）の風力・太陽光係数ベクトル b_s（24次元）について
      「平行シフト」帰無仮説 H0: b_s,0 = ... = b_s,23（23制約）の Wald 検定を、
      24本の残差の時刻間相関と日次の系列相関を両方考慮した多式 NW 共分散で行う。
      平行シフト比率 = 24·mean(b)^2 / ||b||^2（係数ベクトルのノルムのうち一様成分の割合）

出力: out/p1_*.csv（リポジトリには書き込まない）
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, MAIN_SEASONS, KEYS, build_daily, design, stars  # noqa: E402

SEASON_LABEL = {"夏": "夏(7-9月)", "冬": "冬(12-2月)", "春秋": "不需要期"}
HOURS = list(range(24))


def pca(dev):
    """dev: (n×24) 偏差行列 → 固有値（降順）・固有ベクトル（列）"""
    C = np.cov(dev, rowvar=False)
    w, V = np.linalg.eigh(C)
    idx = np.argsort(w)[::-1]
    w, V = w[idx], V[:, idx]
    # 符号の規準化: PC1 は平均負荷が正、PC2 は「夕方(17-19時)−昼(11-13時)」が正（=ダックの深さが正）、
    # PC3 は「夜(0-5時)」平均が正
    if V[:, 0].mean() < 0:
        V[:, 0] *= -1
    if V[17:20, 1].mean() - V[11:14, 1].mean() < 0:
        V[:, 1] *= -1
    if V[0:6, 2].mean() < 0:
        V[:, 2] *= -1
    return w, V


def fit_all(y, X):
    out = {"HC3": sm.OLS(y, X).fit(cov_type="HC3")}
    for L in (7, 14):
        out[f"NW{L}"] = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": L})
    return out


def nw_long_run(G, L):
    """G: (n×m) スコア行列（平均ゼロ想定）→ Bartlett 重みの長期共分散 Σ_j w_j Γ_j"""
    n = G.shape[0]
    S = G.T @ G
    for j in range(1, L + 1):
        w = 1.0 - j / (L + 1.0)
        Gj = G[j:].T @ G[:-j]
        S += w * (Gj + Gj.T)
    return S


def multi_eq_cov(X, E, rows, L):
    """24本の同一右辺 OLS の係数 B (k×24) のうち、行 rows（説明変数）について
    vec 共分散（|rows|·24 次元）を NW(L) で推定。L=0 なら White(HC0)。
    並び: 変数 r ごとに 24時刻ブロック"""
    Xn = X.to_numpy()
    n, k = Xn.shape
    XtXi = np.linalg.inv(Xn.T @ Xn)
    A = Xn @ XtXi[:, rows]                     # n×|rows|: 各日の x_t'(X'X)^{-1} の該当列
    # スコア ψ_t = A_t ⊗ e_t  →  (n × |rows|·24)
    G = (A[:, :, None] * E[:, None, :]).reshape(n, -1)
    S = nw_long_run(G, L) if L > 0 else G.T @ G
    return S                                   # statsmodels の HAC と同じく小標本補正なし


def wald_parallel(b, V):
    """b: 24 次元係数、V: 24×24 共分散。H0: 全時刻で等しい（23制約）"""
    C = np.eye(24)[1:] - np.eye(24)[:1]        # b_h - b_0, h=1..23
    Cb = C @ b
    W = float(Cb @ np.linalg.solve(C @ V @ C.T, Cb))
    return W, 1 - stats.chi2.cdf(W, 23)


def main():
    d, P = build_daily("hokkaido", "p_hokkaido", return_matrix=True)
    P = P.astype(float)
    n = len(d)
    print(f"北海道 FY2016-25: {n} 日（原稿 6.2 の 3,632 日と一致するか: {n == 3632}）")

    # ---------- 偏差の作成 ----------
    cell = d["fy"].astype(str) + "_" + d["season"]
    dev_A = P - P.groupby(cell.values).transform("mean").to_numpy()   # FY×季節×時刻の平均を除去
    dev_B = P - P.mean()

    results_var, results_load, results_reg, results_wald, results_corr = [], [], [], [], []

    def run_pca(tag, dev, sub_idx=None):
        Dv = dev if sub_idx is None else dev.loc[sub_idx]
        w, V = pca(Dv.to_numpy())
        share = w / w.sum()
        for k in range(5):
            results_var.append({"仕様": tag, "PC": k + 1, "固有値": w[k], "寄与率": share[k],
                                "累積寄与率": share[:k + 1].sum()})
        for k in range(3):
            v = V[:, k]
            results_load.append({"仕様": tag, "PC": k + 1,
                                 "一様ベクトルとの cos": float(v.sum() / np.sqrt(24) / np.linalg.norm(v)),
                                 **{f"h{h:02d}": v[h] for h in HOURS}})
        return w, V, Dv

    # (A) 主仕様
    wA, VA, DA = run_pca("A: FY×季節内の偏差（主仕様）", dev_A)
    # (B) 生の偏差
    run_pca("B: 全期間平均からの偏差（参考）", dev_B)
    # (C) 季節別
    for s in MAIN_SEASONS:
        run_pca(f"C: 季節別 {SEASON_LABEL[s]}", dev_A, d.index[d["season"] == s])
    # (D) FY2023-25
    run_pca("D: FY2023-25（FY×季節内の偏差）", dev_A, d.index[d["fy"] >= 2023])

    # ---------- 主仕様の因子スコアと既存指標の関係 ----------
    F = pd.DataFrame(DA.to_numpy() @ VA[:, :5], index=d.index, columns=[f"PC{k}" for k in range(1, 6)])
    # 既存指標も同じく FY×季節内で中心化
    for ycol in ("mean_p", "tb4", "sd"):
        yc = d[ycol] - d.groupby(cell)[ycol].transform("mean")
        r1 = sm.OLS(yc, sm.add_constant(F[["PC1"]])).fit().rsquared
        r2_5 = sm.OLS(yc, sm.add_constant(F[["PC2", "PC3", "PC4", "PC5"]])).fit().rsquared
        r1_5 = sm.OLS(yc, sm.add_constant(F)).fit().rsquared
        results_corr.append({"指標（FY×季節内で中心化）": ycol,
                             "corr(PC1)": np.corrcoef(yc, F["PC1"])[0, 1],
                             "corr(PC2)": np.corrcoef(yc, F["PC2"])[0, 1],
                             "corr(PC3)": np.corrcoef(yc, F["PC3"])[0, 1],
                             "R2: PC1のみ": r1, "R2: PC2-5のみ": r2_5, "R2: PC1-5": r1_5})

    # ---------- 因子スコアの回帰（原稿と同じ右辺） ----------
    # 負荷 V は FY×季節内の偏差の共分散から推定し、スコアは全期間平均からの偏差の射影とする。
    # これにより因子回帰の係数 = v_k' × 時刻別回帰（同一右辺）の係数ベクトル が厳密に成り立つ
    X = design(d)
    Fr = pd.DataFrame(dev_B.to_numpy() @ VA[:, :5], index=d.index, columns=[f"PC{k}" for k in range(1, 6)])
    for k in range(1, 4):
        fits = fit_all(Fr[f"PC{k}"], X)
        for key in KEYS:
            row = {"被説明変数": f"PC{k}", "係数": key, "推定値": fits["HC3"].params[key]}
            for nm, f in fits.items():
                row[f"SE_{nm}"] = f.bse[key]
                row[f"p_{nm}"] = f.pvalues[key]
            row["R2"] = fits["HC3"].rsquared
            results_reg.append(row)
    # ---------- TB4h 係数の経路分解（水準因子 PC1 経由 vs 形状因子 PC2-5 経由） ----------
    # TB4h = a + Σ_k c_k·PC_k + X·γ + u を推定（c_k は FE・再エネを統制した偏回帰の傾き）し、
    # 再エネの TB4h 係数 ≈ Σ_k c_k·β_k（β_k は因子回帰の係数）と分解。残りは非線形（ソート）由来の残差
    Z = pd.concat([X, Fr], axis=1)
    cfit = sm.OLS(d["tb4"], Z).fit()
    beta_k = {k: sm.OLS(Fr[f"PC{k}"], X).fit().params for k in range(1, 6)}
    tb4_direct = sm.OLS(d["tb4"], X).fit().params
    sd_src = {key: float(X[key][X[key] != 0].std()) for key in KEYS}   # 当該季節内の発電量SD（GWh/日）
    chan_rows = []
    for key in KEYS:
        lvl = cfit.params["PC1"] * beta_k[1][key]
        shp = sum(cfit.params[f"PC{k}"] * beta_k[k][key] for k in range(2, 6))
        chan_rows.append({"係数": key, "TB4h係数(原稿の仕様)": tb4_direct[key],
                          "PC1(水準)経由": lvl, "PC2-5(形状)経由": shp,
                          "残差(非線形・直接)": tb4_direct[key] - lvl - shp,
                          "季節内の発電量SD(GWh/日)": sd_src[key],
                          "1SDあたり PC1(年度・季節内SD単位)": beta_k[1][key] * sd_src[key] / F["PC1"].std(),
                          "1SDあたり PC2(年度・季節内SD単位)": beta_k[2][key] * sd_src[key] / F["PC2"].std()})
    chan = pd.DataFrame(chan_rows)
    chan.to_csv(os.path.join(OUT, "p1_tb4_channel_decomposition.csv"), index=False, encoding="utf-8-sig")
    print("TB4h = Σ c_k PC_k の偏回帰の傾き c_1..c_5:", cfit.params[[f"PC{k}" for k in range(1, 6)]].round(3).to_dict(),
          f"R2={cfit.rsquared:.3f}")

    # 残差の自己相関（PC1, PC2）
    ac = {}
    for k in (1, 2, 3):
        e = sm.OLS(Fr[f"PC{k}"], X).fit().resid.to_numpy()
        ac[f"PC{k}"] = float(np.corrcoef(e[1:], e[:-1])[0, 1])

    # ---------- 時刻別回帰と平行シフト検定 ----------
    def hourly_tests(dsub, Psub, tag):
        Xs = design(dsub)
        Y = Psub.to_numpy()
        Xn = Xs.to_numpy()
        B = np.linalg.lstsq(Xn, Y, rcond=None)[0]           # k×24
        E = Y - Xn @ B
        cols = list(Xs.columns)
        rows = [cols.index(k) for k in KEYS]
        hourly = pd.DataFrame(B[rows, :], index=KEYS, columns=[f"h{h:02d}" for h in HOURS])
        hourly.insert(0, "標本", tag)
        # 季節別の平均価格プロファイル（比例シフト仮説 b_h = λ·p̄_h の比較用）
        prof = {s_: Psub.loc[dsub["season"] == s_].mean().to_numpy() for s_ in MAIN_SEASONS}
        for L, nm in ((0, "HC0"), (7, "NW7"), (14, "NW14")):
            V = multi_eq_cov(Xs, E, rows, L)
            for i, key in enumerate(KEYS):
                b = B[rows[i], :]
                Vi = V[i * 24:(i + 1) * 24, i * 24:(i + 1) * 24]
                W, pw = wald_parallel(b, Vi)
                mean_b = b.mean()
                se_mean = float(np.sqrt(np.ones(24) @ Vi @ np.ones(24)) / 24)
                # 形状成分の振幅（夕方17-19時平均 − 昼11-13時平均）とその SE
                c = np.zeros(24); c[17:20] = 1 / 3; c[11:14] = -1 / 3
                amp = float(c @ b); se_amp = float(np.sqrt(c @ Vi @ c))
                pbar = prof[key.split("_")[1]]
                lam = float(b @ pbar / (pbar @ pbar))
                prop_share = lam ** 2 * float(pbar @ pbar) / float(b @ b)
                # 比例シフトの Wald 検定: H0: b = λ p̄（λ を GLS で推定、自由度 23）
                Vinv = np.linalg.pinv(Vi)
                lam_g = float(pbar @ Vinv @ b / (pbar @ Vinv @ pbar))
                r = b - lam_g * pbar
                Wp = float(r @ Vinv @ r)
                results_wald.append({"標本": tag, "共分散": nm, "係数": key, "時刻平均(=日平均への効果)": mean_b,
                                     "SE(時刻平均)": se_mean,
                                     "最小(時刻)": b.min(), "最大(時刻)": b.max(),
                                     "平行シフト比率 24·mean²/‖b‖²": 24 * mean_b ** 2 / float(b @ b),
                                     "PC1への射影比率 (v1'b)²/‖b‖²": float(VA[:, 0] @ b) ** 2 / float(b @ b),
                                     "夕方−昼 振幅": amp, "SE(振幅)": se_amp,
                                     "p(振幅)": 2 * (1 - stats.norm.cdf(abs(amp / se_amp))),
                                     "Wald(平行シフト, χ²23)": W, "p(Wald)": pw,
                                     "比例係数 λ（b≈λ·p̄）": lam, "比例シフト比率": prop_share,
                                     "Wald(比例シフト, χ²23)": Wp, "p(比例)": 1 - stats.chi2.cdf(Wp, 23)})
        return Xs, B, E, rows, hourly

    X, B, E, rows, hourly = hourly_tests(d, P, "FY2016-25")
    sub = d.index[d["fy"] >= 2023]
    _, _, _, _, hourly_d = hourly_tests(d.loc[sub], P.loc[sub], "FY2023-25")
    hourly = pd.concat([hourly, hourly_d])
    # 単一式の NW SE が statsmodels と一致するかの検算（h=18, wind_冬）
    chk = sm.OLS(P[18], X).fit(cov_type="HAC", cov_kwds={"maxlags": 7}).bse["wind_冬"]
    V7 = multi_eq_cov(X, E, rows, 7)
    i = KEYS.index("wind_冬")
    mine = float(np.sqrt(V7[i * 24 + 18, i * 24 + 18]))
    print(f"検算: wind_冬 h18 NW7 SE statsmodels={chk:.5f} 自作={mine:.5f}")
    # 因子回帰係数 = v_k' b の検算
    fac = sm.OLS(Fr["PC1"], X).fit().params["wind_冬"]
    print(f"検算: PC1 の wind_冬 係数 {fac:.5f} = v1'b {float(VA[:, 0] @ B[rows[i], :]):.5f}")

    # ---------- 出力 ----------
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    var = pd.DataFrame(results_var)
    load = pd.DataFrame(results_load)
    reg = pd.DataFrame(results_reg)
    wald = pd.DataFrame(results_wald)
    corr = pd.DataFrame(results_corr)
    var.to_csv(os.path.join(OUT, "p1_pca_variance.csv"), index=False, encoding="utf-8-sig")
    load.to_csv(os.path.join(OUT, "p1_pca_loadings.csv"), index=False, encoding="utf-8-sig")
    reg.to_csv(os.path.join(OUT, "p1_factor_regression.csv"), index=False, encoding="utf-8-sig")
    wald.to_csv(os.path.join(OUT, "p1_parallel_shift_test.csv"), index=False, encoding="utf-8-sig")
    corr.to_csv(os.path.join(OUT, "p1_factor_vs_metrics.csv"), index=False, encoding="utf-8-sig")
    hourly.to_csv(os.path.join(OUT, "p1_hourly_coefficients.csv"), encoding="utf-8-sig")

    print("\n=== 寄与率（PC1-3） ===")
    v3 = var[var["PC"] <= 3].pivot(index="仕様", columns="PC", values="寄与率")
    v3["累積3"] = v3.sum(axis=1)
    print(v3.round(3).to_string())
    print("\n=== 負荷（主仕様 A, 3時間おき）と一様ベクトルとの cos ===")
    la = load[load["仕様"].str.startswith("A")]
    print(la[["PC", "一様ベクトルとの cos"] + [f"h{h:02d}" for h in range(0, 24, 3)]].round(3).to_string(index=False))
    print("\n=== 季節別・FY2023-25 の負荷 cos（PC1-3） ===")
    print(load.pivot(index="仕様", columns="PC", values="一様ベクトルとの cos").round(3).to_string())
    print("\n=== 因子と既存指標（FY×季節内で中心化） ===")
    print(corr.round(3).to_string(index=False))
    print("\n=== 因子スコアの回帰（円/kWh·√24 単位の因子 per GWh/日） ===")
    show = reg.copy()
    show["HC3"] = show.apply(lambda r: f"{r['推定値']:+.3f}{stars(r['p_HC3'])}", axis=1)
    show["NW7"] = show.apply(lambda r: f"{r['推定値']:+.3f}{stars(r['p_NW7'])}", axis=1)
    show["NW14"] = show.apply(lambda r: f"{r['推定値']:+.3f}{stars(r['p_NW14'])}", axis=1)
    print(show.pivot(index="係数", columns="被説明変数", values=["HC3", "NW7", "NW14"]).loc[KEYS].to_string())
    print("残差の1次自己相関:", {k: round(v, 3) for k, v in ac.items()})
    print("\n=== 時刻別係数ベクトルの平行シフト検定 ===")
    cols_show = ["共分散", "係数", "時刻平均(=日平均への効果)", "SE(時刻平均)", "最小(時刻)", "最大(時刻)",
                 "平行シフト比率 24·mean²/‖b‖²", "PC1への射影比率 (v1'b)²/‖b‖²", "夕方−昼 振幅", "SE(振幅)",
                 "p(振幅)", "Wald(平行シフト, χ²23)", "p(Wald)", "比例係数 λ（b≈λ·p̄）", "比例シフト比率",
                 "Wald(比例シフト, χ²23)", "p(比例)"]
    for tag, g in wald.groupby("標本", sort=False):
        print(f"--- 標本 {tag} ---")
        print(g[cols_show].round(3).to_string(index=False))
    print("\n=== TB4h 係数の経路分解（FY2016-25、円/kWh per GWh/日）と標準化効果（発電量1SD→因子SD単位） ===")
    print(chan.round(3).to_string(index=False))
    print("\n=== 時刻別係数（3時間おき） ===")
    print(hourly[["標本"] + [f"h{h:02d}" for h in range(0, 24, 3)] + ["h17", "h19"]].round(3).to_string())


if __name__ == "__main__":
    main()
