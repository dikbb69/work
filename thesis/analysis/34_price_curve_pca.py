#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24時間価格カーブの主成分分解と、蓄電池の完全予見粗利の因子エクスポージャー（北海道、FY2016〜25）

位置づけ:
  前日スポットの24時間価格は、同じオークションで同時に決まる受渡時刻別の24本の商品である。
  そこで日次の価格ベクトルを短い期間構造とみなし、金利の期間構造の主成分分解（Litterman & Scheinkman 1991 の
  水準・傾き・曲率）の類比として分解する。同論文は利回りの「変化」を分解したが、ここでは年度×季節×時刻の
  平均を除いた「水準の偏差」を分解する（回帰の年度・季節固定効果に近いが、年度×季節の交差まで除く点でやや強い）。
  日次変化の PCA は頑健性として併記する。

手法:
  (1) PCA: 偏差 D_{d,h} = p_{d,h} − M_{FY×季節,h} の共分散を固有分解する（主仕様 A=全期間、B=全期間平均からの偏差、
      C=季節別、D=FY2023〜25、E=年度別、F=日次変化 Δp_d=p_d−p_{d−1}）。符号は PC1 の平均負荷が正、
      PC2 の「夕方(17〜19時)−昼(11〜13時)」が正、PC3 の夜(0〜5時)平均が正になるように揃える。
  (2) 因子スコア回帰: f_{k,d}=v_k'(p_d−p̄)（v_k は主仕様 A の負荷）を、24_vol_verification.py と同じ右辺
      （季節×太陽光／風力の制御前 GWh/日、需要、FY・季節固定効果）に OLS で回帰し、HC3・NW7・NW14 を並べる。
      線形性より、因子回帰の係数 = v_k'×（時刻別回帰の係数ベクトル b）が厳密に成り立つ（検算を出力）。
      FY2023〜25 は、全期間の負荷 A による版と、FY2023〜25 自身の負荷 D による版（現行の構造で測る版）を併記する。
  (3) 時刻別係数ベクトル b（同一右辺の24本の OLS）の形状検定。時刻間の残差相関と日次の系列相関を両方考慮した
      多式 Newey-West 共分散（スコア ψ_d=(X'X)^{-1}x_d⊗e_d、Bartlett 重み、小標本補正なし＝statsmodels の HAC と同じ）で、
      (a) 平行シフト H0: b_0=…=b_23 の Wald（23制約）、(b) 4時間ブロック平均6本への縮約版（5制約）、
      (c) 14日の移動ブロック・ブートストラップ（B=299、乱数種固定）による縮約版の p 値、
      (d) 比例シフト H0: b=λ·p̄（p̄ は標本・季節の平均価格プロファイル。b∈span(p̄) の線形制約として 23制約と縮約5制約）、
      (e) 時刻別係数の変動係数 sd(b)/|mean(b)|、(f) 一様成分の比率 24·mean(b)²/‖b‖²（判別力が弱いので参考）、
      (g) 夕方(17〜19時)−昼(11〜13時)、夕方−夜(0〜5時) のコントラスト（FY2016〜25 と FY2023〜25）。
  (4) TB4h 係数の経路分解: TB4h を右辺＋PC1〜5 に回帰した傾き c_k と因子回帰の係数 β_k から、
      TB4h 係数 = c_1β_1（水準経由）＋Σ_{k≥2}c_kβ_k（形状経由）＋残差。OLS の欠落変数の恒等式なので分解は厳密で、
      残差は長い回帰（右辺＋PC1〜5）での風力・太陽光の係数そのもの（PC6〜24 を通る線形の経路と、ソート・休止による
      非線形の部分の合計）である。
  (5) 完全予見粗利（4h、往復効率0.85 を放電側に一括、粗利が負の日は休止。円/kW-日）を右辺＋PC1〜5 に回帰した
      因子エクスポージャー（NW14。債券のファクター・デュレーションの線形近似の類比）と、風力・太陽光の完全予見粗利への
      効果の同じ経路分解（全期間×負荷A、FY2023〜25×負荷A、FY2023〜25×負荷D）。季節別の係数の年間換算は、
      その季節の暦日数（夏92・冬90.25・不需要期183日）を掛ける（365日を掛けると季節外の日まで数えてしまう）。
      頑健性: 期間別（FY2016〜19・FY2020〜22・FY2023〜25・年度別）に主成分を求め直したエクスポージャーと、
      年度×季節内で中心化した完全予見粗利と日平均価格の相関（期間・年度・FY2023〜25 の季節別）。
  (6) 因子別の感応度の反実仮想（FY2023〜25、季節別 PCA。derivatives/p3 と同じ設計）: 第k主成分のスコア、
      水準成分（日平均の偏差×全時刻同額）、形状成分（日内偏差）を s 倍し、下限価格0.01円で打ち切る版と打ち切らない版で
      完全予見粗利と固定窓の粗利を再計算する。風力・太陽光が作る日間変動（時刻別負荷 B(h)×発電量の年度内偏差）は 0〜3倍。
      固定窓は年度×季節の事後平均プロファイルの上位／下位4時間で、実行可能戦略 c とは別物（実行不能な参照値）。

出力:
  data/processed/price_curve_pca_{variance,loadings,metrics_corr,factor_regression,hourly_coef,shape_tests,
                                  contrasts,tb4_channels,pf_exposure,pf_exposure_by_period,pf_channels,sensitivity}.csv
  figures/hokkaido/price_curve_pca.png（上段: 負荷 PC1〜3、中段・下段: 季節別の時刻別係数と NW14 の95%帯）

限界:
  PCA は外れ値に敏感で、プールした負荷は FY2020〜22 の高分散年に重みが寄る（FY2023〜25 版を併記）。
  主成分は統計的な因子で、PC2 には昼対夜の対比も混じる（蓄電池に効く形状は夕方−昼・夕方−夜のコントラストで判断する）。
  TB4h・完全予見粗利はソート・休止を含む非線形な指標で、線形の因子経路では残差が残る。(6) の B(h) による反実仮想は
  線形の局所感応度で、導入量の増加に伴う供給曲線の下端の急勾配の効果（第8章）は含まない。HAC の帯域（7・14日）は
  残差の強い自己相関（ρ1≈0.4〜0.85）の下では過大棄却の恐れがあり、縮約版とブロック・ブートストラップで補う。
  FY2023〜25 の水準因子へのエクスポージャー≈0 は3年・3季節の平均で、年度別（FY2023 −0.55〜FY2025 +0.75）・
  季節別（冬は粗利と日平均価格の相関が残る）には揺れる（(5b)）。FY2016〜25 の大きな水準エクスポージャーは
  燃料危機期だけのものではなく、FY2016〜19 にも同程度にある。
"""
import logging
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from matplotlib import font_manager
import matplotlib.pyplot as plt

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)   # 代替フォントの探索ログを抑止

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY = "#595959"
C_WIND, C_SOLAR = "#0079C2", "#D95B20"
# 主成分の負荷は風力・太陽光の色と意味が重ならないよう、3パネルとも同じ中立色（期間は線種で区別）
C_PC = ["#8A5AAB", "#8A5AAB", "#8A5AAB"]

# 24_vol_verification.py と同一の季節区分（不需要期の内部名は「春秋」）
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}
MAIN_SEASONS = ["夏", "冬", "春秋"]
SEASON_LABEL = {"夏": "夏（7〜9月）", "冬": "冬（12〜2月）", "春秋": "不需要期"}
KEYS = [f"{src}_{s}" for s in MAIN_SEASONS for src in ("solar", "wind")]
KEY_LABEL = {f"{src}_{s}": f"{'太陽光' if src == 'solar' else '風力'}・{SEASON_LABEL[s].split('（')[0]}"
             for s in MAIN_SEASONS for src in ("solar", "wind")}
HOURS = np.arange(24)
EVE, MID, NIGHT, NIGHT_RV = [17, 18, 19], [11, 12, 13], [0, 1, 2, 3, 4, 5], [2, 3, 4]
ETA, H4, FLOOR = 0.85, 4, 0.01
SEASON_DAYS = {"夏": 92.0, "冬": 90.25, "春秋": 183.0}   # 暦日数（年度平均。冬はうるう年を平均）
RESID = "残差（PC6以下の経路と非線形）"
B_BOOT, L_BOOT, SEED = 299, 14, 20261020
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def save(df, name):
    df.to_csv(os.path.join(PROC, f"price_curve_pca_{name}.csv"), index=False, encoding="utf-8-sig")


# ============================================================ データ（24_vol_verification.build_daily と同一）
def build_daily():
    p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=["p_hokkaido"]).copy()
    p["day"] = p["ts"].dt.normalize()
    p["hour"] = p["ts"].dt.hour
    cnt = p.groupby("day")["hour"].count()
    p = p[p["day"].isin(cnt[cnt == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    P = p.pivot(index="day", columns="hour", values="p_hokkaido")
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["mean_p"] = P.mean(axis=1)
    d["sd"] = P.std(axis=1)
    d["tb4"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
    d["solar"] = p.groupby("day")["solar_pre"].sum() / 1000   # GWh/日
    d["wind"] = p.groupby("day")["wind_pre"].sum() / 1000
    d["demand"] = p.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    d = d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()
    P = P.loc[d.index].astype(float)
    # 完全予見粗利（4h、η=0.85 を放電側、粗利が負の日は休止）: 円/kW-日
    s2 = np.sort(P.to_numpy(), axis=1)
    d["pf"] = np.maximum(0.0, ETA * s2[:, -H4:].sum(axis=1) - s2[:, :H4].sum(axis=1))
    d["eve_mid"] = P[EVE].mean(axis=1) - P[MID].mean(axis=1)
    d["eve_night"] = P[EVE].mean(axis=1) - P[NIGHT].mean(axis=1)
    d["eve_night_2_4"] = P[EVE].mean(axis=1) - P[NIGHT_RV].mean(axis=1)
    return d, P


def design(d):
    """24_vol_verification.run_reg と同一の右辺"""
    X = pd.DataFrame(index=d.index)
    for s in MAIN_SEASONS:
        m = (d["season"] == s).astype(float)
        X[f"solar_{s}"] = d["solar"] * m
        X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X,
                   pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    return sm.add_constant(X)


def fit3(y, X):
    out = {"HC3": sm.OLS(y, X).fit(cov_type="HC3")}
    for L in (7, 14):
        out[f"NW{L}"] = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": L})
    return out


# ============================================================ PCA
def pca(dev):
    C = np.cov(np.asarray(dev, float), rowvar=False)
    w, V = np.linalg.eigh(C)
    idx = np.argsort(w)[::-1]
    w, V = w[idx], V[:, idx].copy()
    if V[:, 0].mean() < 0:
        V[:, 0] *= -1
    if V[EVE, 1].mean() - V[MID, 1].mean() < 0:
        V[:, 1] *= -1
    if V[NIGHT, 2].mean() < 0:
        V[:, 2] *= -1
    return w, V


def cos(a, b):
    return float(a @ b / np.linalg.norm(a) / np.linalg.norm(b))


# ============================================================ 多式 Newey-West
def nw_long_run(G, L):
    S = G.T @ G
    for j in range(1, L + 1):
        Gj = G[j:].T @ G[:-j]
        S += (1.0 - j / (L + 1.0)) * (Gj + Gj.T)
    return S


def multi_eq_cov(Xn, E, rows, L):
    """24本の同一右辺 OLS の係数のうち、行 rows について vec 共分散（変数ごとに24時刻のブロック）。L=0 は HC0"""
    XtXi = np.linalg.inv(Xn.T @ Xn)
    A = Xn @ XtXi[:, rows]
    G = (A[:, :, None] * E[:, None, :]).reshape(Xn.shape[0], -1)
    return nw_long_run(G, L) if L > 0 else G.T @ G


def null_basis(v):
    """v に直交する補空間の正規直交基底（行ベクトル、次元 len(v)−1）。R b = 0 ⇔ b ∈ span(v)"""
    v = np.asarray(v, float).reshape(1, -1)
    _, _, Vt = np.linalg.svd(v)
    return Vt[1:]


def wald(R, b, V):
    Rb = R @ b
    W = float(Rb @ np.linalg.solve(R @ V @ R.T, Rb))
    return W, 1 - stats.chi2.cdf(W, R.shape[0])


BLK = np.zeros((6, 24))
for _j in range(6):
    BLK[_j, 4 * _j:4 * _j + 4] = 0.25
R_PAR23 = null_basis(np.ones(24))           # 平行シフト（23制約）
R_PAR5 = null_basis(np.ones(6)) @ BLK       # 4時間ブロック平均で縮約（5制約）


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    d, P = build_daily()
    n = len(d)
    print(f"北海道 FY2016-25: {n} 日（原稿 6.2 の 3,632 日と一致: {n == 3632}）")
    cell = (d["fy"].astype(str) + "_" + d["season"]).to_numpy()
    devA = P - P.groupby(cell).transform("mean").to_numpy()
    devB = P - P.mean()
    is2325 = (d["fy"] >= 2023).to_numpy()

    # ------------------------------------------------ (1) PCA
    var_rows, load_rows = [], []

    def run_pca(tag, dev, pbar):
        w, V = pca(dev)
        sh = w / w.sum()
        for k in range(5):
            var_rows.append({"仕様": tag, "PC": k + 1, "固有値": w[k], "寄与率": sh[k], "累積寄与率": sh[:k + 1].sum(),
                             "日数": len(dev)})
        for k in range(3):
            v = V[:, k]
            load_rows.append({"仕様": tag, "PC": k + 1, "寄与率": sh[k],
                              "cos(負荷, 一様)": cos(v, np.ones(24)),
                              "cos(負荷, p̄−0.01)": cos(v, pbar - 0.01),
                              "夜0-5平均": v[NIGHT].mean(), "昼11-13平均": v[MID].mean(), "夕方17-19平均": v[EVE].mean(),
                              **{f"h{h:02d}": v[h] for h in HOURS}})
        return w, V

    wA, VA = run_pca("A: FY×季節内の偏差（主仕様、FY2016-25）", devA.to_numpy(), P.mean().to_numpy())
    run_pca("B: 全期間平均からの偏差（参考）", devB.to_numpy(), P.mean().to_numpy())
    for s in MAIN_SEASONS:
        m = (d["season"] == s).to_numpy()
        run_pca(f"C: 季節別 {SEASON_LABEL[s]}", devA.to_numpy()[m], P.to_numpy()[m].mean(0))
    wD, VD = run_pca("D: FY2023-25（FY×季節内の偏差）", devA.to_numpy()[is2325], P.to_numpy()[is2325].mean(0))
    for s in MAIN_SEASONS:
        m = ((d["season"] == s).to_numpy()) & is2325
        run_pca(f"D: FY2023-25 季節別 {SEASON_LABEL[s]}", devA.to_numpy()[m], P.to_numpy()[m].mean(0))
    for fy in range(2016, 2026):
        m = (d["fy"] == fy).to_numpy()
        run_pca(f"E: 年度別 FY{fy}", devA.to_numpy()[m], P.to_numpy()[m].mean(0))
    # F: 日次変化（Litterman-Scheinkman と同じく変化を分解する頑健性）。前日がそろう日だけ
    gap = pd.Series(d.index).diff().dt.days.to_numpy()
    dP = np.diff(P.to_numpy(), axis=0)[gap[1:] == 1]
    run_pca("F: 日次変化 Δp（頑健性、FY2016-25）", dP, P.mean().to_numpy())
    m23 = is2325[1:][gap[1:] == 1]
    run_pca("F: 日次変化 Δp（頑健性、FY2023-25）", dP[m23], P.to_numpy()[is2325].mean(0))
    var = pd.DataFrame(var_rows)
    load = pd.DataFrame(load_rows)
    save(var, "variance")
    save(load, "loadings")

    # 因子スコア: 負荷 A（全期間）または D（FY2023-25 自身）で、全期間平均からの偏差を射影（回帰用）、
    # FY×季節内の偏差を射影（相関・SD 用）。スコア回帰の係数 = v_k'b は負荷によらず成り立つ
    cols5 = [f"PC{k}" for k in range(1, 6)]

    def scores(V):
        return (pd.DataFrame(devB.to_numpy() @ V[:, :5], index=d.index, columns=cols5),
                pd.DataFrame(devA.to_numpy() @ V[:, :5], index=d.index, columns=cols5))

    F, Fw = scores(VA)
    FD, FwD = scores(VD)
    # 標本×負荷の組合せ（D 負荷は FY2023-25 の構造そのもので測るための版）
    combos = [("FY2016-25", np.ones(n, bool), "A（FY2016-25）", F, Fw),
              ("FY2023-25", is2325, "A（FY2016-25）", F, Fw),
              ("FY2023-25", is2325, "D（FY2023-25）", FD, FwD)]
    corr_rows = []
    for tag, msk, vlab, _, Fw_ in combos:
        for ycol, lab in (("mean_p", "日平均価格"), ("tb4", "TB4h"), ("sd", "日内SD"), ("pf", "完全予見粗利"),
                          ("eve_mid", "夕方−昼"), ("eve_night", "夕方−夜")):
            yc = (d[ycol] - d.groupby(cell)[ycol].transform("mean"))[msk]
            Fm = Fw_[msk]
            corr_rows.append({"標本": tag, "負荷": vlab, "指標（FY×季節内で中心化）": lab,
                              **{f"corr(PC{k})": np.corrcoef(yc, Fm[f"PC{k}"])[0, 1] for k in (1, 2, 3)},
                              "R2: PC1のみ": sm.OLS(yc, sm.add_constant(Fm[["PC1"]])).fit().rsquared,
                              "R2: PC2-5のみ": sm.OLS(yc, sm.add_constant(Fm[["PC2", "PC3", "PC4", "PC5"]])).fit().rsquared,
                              "R2: PC1-5": sm.OLS(yc, sm.add_constant(Fm)).fit().rsquared})
    corr = pd.DataFrame(corr_rows)
    save(corr, "metrics_corr")

    # ------------------------------------------------ (2) 因子スコア回帰
    samples = {"FY2016-25": np.ones(n, bool), "FY2023-25": is2325}
    reg_rows = []
    for tag, msk, vlab, F_, Fw_ in combos:
        ds, Fs = d[msk], F_[msk]
        Xs = design(ds)
        Fws = Fw_[msk]
        for k in range(1, 6):
            fits = fit3(Fs[f"PC{k}"], Xs)
            e = fits["HC3"].resid.to_numpy()
            for key in KEYS:
                # 発電量の SD は因子の SD と同じく年度内（その季節の日の、年度平均からの偏差）で測る
                src_, s_ = key.split("_")
                ms_ = (ds["season"] == s_)
                xs_ = ds.loc[ms_, src_]
                sd_x = float((xs_ - xs_.groupby(ds.loc[ms_, "fy"]).transform("mean")).std())
                row = {"標本": tag, "負荷": vlab, "被説明変数": f"PC{k}", "係数": key, "推定値": fits["HC3"].params[key]}
                for nm, f_ in fits.items():
                    row[f"SE_{nm}"] = f_.bse[key]
                    row[f"p_{nm}"] = f_.pvalues[key]
                row["R2"] = fits["HC3"].rsquared
                row["残差の1次自己相関"] = float(np.corrcoef(e[1:], e[:-1])[0, 1])
                row["発電量の年度内SD（GWh/日）"] = sd_x
                row["発電量1SDあたり（因子の年度・季節内SD単位）"] = fits["HC3"].params[key] * sd_x / Fws[f"PC{k}"].std()
                reg_rows.append(row)
    reg = pd.DataFrame(reg_rows)
    save(reg, "factor_regression")

    # ------------------------------------------------ (3) 時刻別係数と形状検定
    hourly_rows, test_rows = [], []
    store = {}
    for tag, msk in samples.items():
        ds, Ps = d[msk], P[msk]
        Xs = design(ds)
        Xn, Y = Xs.to_numpy(), Ps.to_numpy()
        B = np.linalg.lstsq(Xn, Y, rcond=None)[0]
        E = Y - Xn @ B
        cols = list(Xs.columns)
        rows = [cols.index(k) for k in KEYS]
        V = {nm: multi_eq_cov(Xn, E, rows, L) for nm, L in (("HC0", 0), ("NW7", 7), ("NW14", 14))}
        prof = {s: Ps[(ds["season"] == s).to_numpy()].mean().to_numpy() for s in MAIN_SEASONS}
        # ブロック・ブートストラップ（14日移動ブロック）
        nn = len(ds)
        starts = np.arange(0, nn - L_BOOT + 1)
        nb = int(np.ceil(nn / L_BOOT))
        Bst = np.empty((B_BOOT, len(rows), 24))
        for r_ in range(B_BOOT):
            st = rng.choice(starts, nb)
            ix = np.concatenate([np.arange(s0, s0 + L_BOOT) for s0 in st])[:nn]
            Bst[r_] = np.linalg.lstsq(Xn[ix], Y[ix], rcond=None)[0][rows, :]
        store[tag] = {"B": B, "rows": rows, "V": V, "prof": prof, "X": Xs, "E": E}
        for i, key in enumerate(KEYS):
            b = B[rows[i]]
            pbar = prof[key.split("_")[1]]
            R_PRO23 = null_basis(pbar)
            R_PRO5 = null_basis(BLK @ pbar) @ BLK
            # ブートストラップ: 共分散 Vb と、中心化した統計量の分布
            Db = Bst[:, i, :] - b
            Vb = np.cov(Bst[:, i, :], rowvar=False)
            bs = {}
            for nm_, R in (("平行5", R_PAR5), ("比例5", R_PRO5)):
                Wb, _ = wald(R, b, Vb)
                M = np.linalg.inv(R @ Vb @ R.T)
                Wst = np.einsum("bi,ij,bj->b", Db @ R.T, M, Db @ R.T)
                bs[nm_] = (Wb, (1 + (Wst >= Wb).sum()) / (B_BOOT + 1))
            for nm, Vfull in V.items():
                Vi = Vfull[i * 24:(i + 1) * 24, i * 24:(i + 1) * 24]
                W23, p23 = wald(R_PAR23, b, Vi)
                W5, p5 = wald(R_PAR5, b, Vi)
                Wp23, pp23 = wald(R_PRO23, b, Vi)
                Wp5, pp5 = wald(R_PRO5, b, Vi)
                Vinv = np.linalg.inv(Vi)
                lam = float(pbar @ Vinv @ b / (pbar @ Vinv @ pbar))
                c_em = np.zeros(24); c_em[EVE] = 1 / 3; c_em[MID] = -1 / 3
                c_en = np.zeros(24); c_en[EVE] = 1 / 3; c_en[NIGHT] = -1 / 6
                row = {"標本": tag, "共分散": nm, "係数": key,
                       "時刻平均（日平均への効果）": b.mean(), "SE(時刻平均)": float(np.sqrt(np.ones(24) @ Vi @ np.ones(24)) / 24),
                       "最小（時刻）": b.min(), "最大（時刻）": b.max(),
                       "変動係数 sd(b)/|mean(b)|": float(b.std() / abs(b.mean())),
                       "一様成分の比率 24·mean²/‖b‖²（参考）": 24 * b.mean() ** 2 / float(b @ b),
                       "PC1方向の比率 (v1'b)²/‖b‖²": float(VA[:, 0] @ b) ** 2 / float(b @ b),
                       "cos(b, p̄)": cos(b, pbar),
                       "夕方−昼": float(c_em @ b), "SE(夕方−昼)": float(np.sqrt(c_em @ Vi @ c_em)),
                       "夕方−夜(0-5時)": float(c_en @ b), "SE(夕方−夜)": float(np.sqrt(c_en @ Vi @ c_en)),
                       "Wald 平行(23)": W23, "p 平行(23)": p23, "Wald 平行(縮約5)": W5, "p 平行(縮約5)": p5,
                       "λ（b≈λ·p̄、GLS）": lam, "Wald 比例(23)": Wp23, "p 比例(23)": pp23,
                       "Wald 比例(縮約5)": Wp5, "p 比例(縮約5)": pp5,
                       "p 平行(縮約5, ブロックBS)": bs["平行5"][1], "p 比例(縮約5, ブロックBS)": bs["比例5"][1]}
                row["p(夕方−昼)"] = 2 * (1 - stats.norm.cdf(abs(row["夕方−昼"] / row["SE(夕方−昼)"])))
                row["p(夕方−夜)"] = 2 * (1 - stats.norm.cdf(abs(row["夕方−夜(0-5時)"] / row["SE(夕方−夜)"])))
                test_rows.append(row)
            se14 = np.sqrt(np.diag(V["NW14"][i * 24:(i + 1) * 24, i * 24:(i + 1) * 24]))
            se7 = np.sqrt(np.diag(V["NW7"][i * 24:(i + 1) * 24, i * 24:(i + 1) * 24]))
            Vi14 = V["NW14"][i * 24:(i + 1) * 24, i * 24:(i + 1) * 24]
            Vinv = np.linalg.inv(Vi14)
            lam14 = float(pbar @ Vinv @ b / (pbar @ Vinv @ pbar))
            for h in HOURS:
                hourly_rows.append({"標本": tag, "係数": key, "時刻": int(h), "推定値": b[h], "SE_NW7": se7[h], "SE_NW14": se14[h],
                                    "下限95%(NW14)": b[h] - 1.96 * se14[h], "上限95%(NW14)": b[h] + 1.96 * se14[h],
                                    "平均価格 p̄_h": pbar[h], "比例シフトの当てはめ λ·p̄_h(GLS, NW14)": lam14 * pbar[h],
                                    "比例シフトの当てはめ λ·p̄_h(最小二乗)": float(b @ pbar / (pbar @ pbar)) * pbar[h]})
    hourly = pd.DataFrame(hourly_rows)
    tests = pd.DataFrame(test_rows)
    save(hourly, "hourly_coef")
    save(tests, "shape_tests")

    # 検算: 多式 NW と statsmodels の HAC、因子回帰の係数 = v1'b
    Xf = store["FY2016-25"]["X"]
    Bf, rows_f = store["FY2016-25"]["B"], store["FY2016-25"]["rows"]
    i_w = KEYS.index("wind_冬")
    chk = sm.OLS(P[18], Xf).fit(cov_type="HAC", cov_kwds={"maxlags": 7}).bse["wind_冬"]
    mine = float(np.sqrt(store["FY2016-25"]["V"]["NW7"][i_w * 24 + 18, i_w * 24 + 18]))
    fac = reg[(reg["標本"] == "FY2016-25") & (reg["被説明変数"] == "PC1") & (reg["係数"] == "wind_冬")]["推定値"].iloc[0]
    print(f"検算: wind_冬 18時 NW7 SE  statsmodels={chk:.5f}  多式NW={mine:.5f}")
    print(f"検算: PC1 の wind_冬 係数 {fac:.5f} = v1'b {float(VA[:, 0] @ Bf[rows_f[i_w]]):.5f}")

    # ------------------------------------------------ (3g) コントラストと既存指標（直接の OLS。c'b・c'Vc と同値）
    con_rows = []
    YLAB = {"eve_mid": "夕方(17-19)−昼(11-13)", "eve_night": "夕方(17-19)−夜(0-5)",
            "eve_night_2_4": "夕方(17-19)−夜(2-4)（レビュー版の定義）", "tb4": "TB4h", "mean_p": "日平均価格",
            "pf": "完全予見粗利（円/kW-日）"}
    for tag, msk in samples.items():
        ds = d[msk]
        Xs = design(ds)
        for ycol, lab in YLAB.items():
            fits = fit3(ds[ycol], Xs)
            for key in KEYS:
                row = {"標本": tag, "被説明変数": lab, "係数": key, "推定値": fits["HC3"].params[key]}
                for nm, f_ in fits.items():
                    row[f"SE_{nm}"] = f_.bse[key]
                    row[f"p_{nm}"] = f_.pvalues[key]
                con_rows.append(row)
    con = pd.DataFrame(con_rows)
    save(con, "contrasts")
    # 同値性の検算（夕方−昼、wind_冬、NW14）
    a1 = con[(con["標本"] == "FY2016-25") & (con["被説明変数"] == YLAB["eve_mid"]) & (con["係数"] == "wind_冬")].iloc[0]
    a2 = tests[(tests["標本"] == "FY2016-25") & (tests["共分散"] == "NW14") & (tests["係数"] == "wind_冬")].iloc[0]
    print(f"検算: 夕方−昼 wind_冬 直接OLS {a1['推定値']:.4f} (SE {a1['SE_NW14']:.4f}) = c'b {a2['夕方−昼']:.4f} (SE {a2['SE(夕方−昼)']:.4f})")

    # ------------------------------------------------ (4)(5) 経路分解と完全予見粗利の因子エクスポージャー
    tb_rows, pfx_rows, pfc_rows = [], [], []
    for tag, msk, vlab, F_, Fw_ in combos:
        ds, Fs, Fws = d[msk], F_[msk], Fw_[msk]
        Xs = design(ds)
        beta = {k: sm.OLS(Fs[f"PC{k}"], Xs).fit().params for k in range(1, 6)}
        Z = pd.concat([Xs, Fs], axis=1)
        for ycol, out_rows in (("tb4", tb_rows), ("pf", pfc_rows)):
            cz = sm.OLS(ds[ycol], Z).fit(cov_type="HAC", cov_kwds={"maxlags": 14})
            direct = sm.OLS(ds[ycol], Xs).fit(cov_type="HAC", cov_kwds={"maxlags": 14})
            for key in KEYS:
                lvl = cz.params["PC1"] * beta[1][key]
                shp = {k: cz.params[f"PC{k}"] * beta[k][key] for k in range(2, 6)}
                row = {"標本": tag, "負荷": vlab, "係数": key, "効果（右辺のみの回帰）": direct.params[key], "p_NW14": direct.pvalues[key],
                       "PC1（水準）経由": lvl, "PC2-5（形状）経由": sum(shp.values()),
                       "うちPC2経由": shp[2], "うちPC3経由": shp[3],
                       RESID: direct.params[key] - lvl - sum(shp.values()),
                       "検算: 長い回帰の係数（=残差）": cz.params[key]}
                if ycol == "pf":
                    days = SEASON_DAYS[key.split("_")[1]]
                    row["季節の暦日数"] = days
                    row["効果の年間換算（季節の日数×、円/kW-年 per GWh/日）"] = direct.params[key] * days
                out_rows.append(row)
            if ycol == "pf":
                yc = ds["pf"] - ds.groupby(cell[msk])["pf"].transform("mean")
                r2w = sm.OLS(yc, sm.add_constant(Fws)).fit().rsquared
                pf_mean = float(ds["pf"].mean())
                for k in range(1, 6):
                    sdk = float(Fws[f"PC{k}"].std())
                    pfx_rows.append({"標本": tag, "負荷": vlab, "因子": f"PC{k}",
                                     "エクスポージャー c_k（円/kW-日 per 因子1単位）": cz.params[f"PC{k}"],
                                     "SE_NW14": cz.bse[f"PC{k}"], "t_NW14": cz.tvalues[f"PC{k}"],
                                     "因子の年度・季節内SD": sdk, "因子1SDあたり（円/kW-日）": cz.params[f"PC{k}"] * sdk,
                                     "因子1SDあたり（平均粗利比）": cz.params[f"PC{k}"] * sdk / pf_mean,
                                     "平均完全予見粗利（円/kW-日）": pf_mean, "R2（右辺＋PC1-5）": cz.rsquared,
                                     "R2（FY×季節内、PC1-5のみ）": r2w, "TB4h の c_k（参考）": np.nan})
            else:
                c_tb = cz
        for r_ in pfx_rows:
            if r_["標本"] == tag and r_["負荷"] == vlab:
                r_["TB4h の c_k（参考）"] = c_tb.params[r_["因子"]]
    tb = pd.DataFrame(tb_rows)
    pfx = pd.DataFrame(pfx_rows)
    pfc = pd.DataFrame(pfc_rows)
    save(tb, "tb4_channels")
    save(pfx, "pf_exposure")
    save(pfc, "pf_channels")

    # ------------------------------------------------ (5b) 頑健性: 期間別に主成分を求め直したエクスポージャーと、粗利と日平均価格の相関
    fyv = d["fy"].to_numpy()
    pc_ = d[["pf", "mean_p"]] - d.groupby(cell)[["pf", "mean_p"]].transform("mean")
    periods = [("FY2016-25", np.ones(n, bool)), ("FY2016-19", fyv <= 2019),
               ("FY2020-22", (fyv >= 2020) & (fyv <= 2022)), ("FY2023-25", fyv >= 2023)]
    periods += [(f"FY{y}", fyv == y) for y in range(2016, 2026)]
    periods += [(f"FY2023-25 {SEASON_LABEL[s]}", (fyv >= 2023) & (d["season"] == s).to_numpy()) for s in MAIN_SEASONS]
    per_rows = []
    for lab, msk in periods:
        row = {"期間": lab, "日数": int(msk.sum()),
               "corr(粗利, 日平均価格)（FY×季節内）": float(np.corrcoef(pc_["pf"][msk], pc_["mean_p"][msk])[0, 1]),
               "粗利の日平均価格への傾き（円/kW-日 per 円/kWh、FY×季節内）":
                   float(sm.OLS(pc_["pf"][msk], sm.add_constant(pc_["mean_p"][msk])).fit().params["mean_p"])}
        if " " not in lab:      # 季節別は日数が少ないので主成分は求めない
            w_, V_ = pca(devA.to_numpy()[msk])
            Fp = pd.DataFrame(devB.to_numpy() @ V_[:, :5], index=d.index, columns=cols5)[msk]
            Fpw = pd.DataFrame(devA.to_numpy() @ V_[:, :5], index=d.index, columns=cols5)[msk]
            ds_ = d[msk]
            cz_ = sm.OLS(ds_["pf"], pd.concat([design(ds_), Fp], axis=1)).fit(cov_type="HAC", cov_kwds={"maxlags": 14})
            yc_ = ds_["pf"] - ds_.groupby(cell[msk])["pf"].transform("mean")
            row.update({"PC1寄与率（自期間の主成分）": w_[0] / w_.sum(), "PC2寄与率": w_[1] / w_.sum(),
                        "PC1負荷 12時": V_[12, 0], "PC1負荷 18時": V_[18, 0], "PC1負荷 3時": V_[3, 0]})
            for k in (1, 2, 3):
                row[f"c_PC{k}"] = cz_.params[f"PC{k}"]
                row[f"t_PC{k}(NW14)"] = cz_.tvalues[f"PC{k}"]
                row[f"PC{k} 1SD/平均粗利"] = cz_.params[f"PC{k}"] * Fpw[f"PC{k}"].std() / ds_["pf"].mean()
            row["R2: PC1のみ（FY×季節内）"] = sm.OLS(yc_, sm.add_constant(Fpw[["PC1"]])).fit().rsquared
            row["R2（右辺＋PC1-5）"] = cz_.rsquared
        per_rows.append(row)
    per = pd.DataFrame(per_rows)
    save(per, "pf_exposure_by_period")

    # ------------------------------------------------ (6) 因子別の感応度の反実仮想（FY2023-25、季節別 PCA）
    def pf_sum(A):
        s_ = np.sort(A, axis=1)
        return np.maximum(0.0, ETA * s_[:, -H4:].sum(1) - s_[:, :H4].sum(1)).sum()

    def fixed_sum(A, M):
        o = np.argsort(M, axis=1)
        return (ETA * np.take_along_axis(A, o[:, -H4:], 1).sum(1) - np.take_along_axis(A, o[:, :H4], 1).sum(1)).sum()

    sens_rows = []
    d3, P3 = d[is2325], P[is2325]
    n_fy = 3
    for s in MAIN_SEASONS:
        m = (d3["season"] == s).to_numpy()
        A = P3.to_numpy()[m]
        inf = d3[m]
        grp = inf["fy"].to_numpy()
        M = np.zeros_like(A)
        for fy in np.unique(grp):
            M[grp == fy] = A[grp == fy].mean(0)
        D = A - M
        _, _, Vt = np.linalg.svd(D, full_matrices=False)
        Zs = D @ Vt.T
        nd = len(A)
        base_pf, base_fx = pf_sum(A), fixed_sum(A, M)

        def add(comp, sc, Araw, clip):
            As = np.maximum(Araw, FLOOR) if clip else Araw
            sens_rows.append({"季節": SEASON_LABEL[s], "成分": comp, "倍率s": sc, "下限で打ち切り": clip, "日数": nd,
                              "PF（円/kW-日）": pf_sum(As) / nd, "固定窓（円/kW-日）": fixed_sum(As, M) / nd,
                              "PF合計（円/kW、3年）": pf_sum(As), "固定窓合計（円/kW、3年）": fixed_sum(As, M),
                              "PF/基準": pf_sum(As) / base_pf})

        for k in range(3):
            for sc in (0.0, 0.5, 1.0, 1.5, 2.0):
                Zk = Zs.copy()
                Zk[:, k] *= sc
                for clip in (True, False):
                    add(f"PC{k + 1}", sc, M + Zk @ Vt, clip)
        Lv = np.repeat(D.mean(1, keepdims=True), 24, axis=1)
        Sh = D - Lv
        for comp, X_ in (("水準成分（日平均の偏差）", Lv), ("形状成分（日内偏差）", Sh)):
            for sc in (0.0, 0.5, 1.0, 1.5, 2.0):
                for clip in (True, False):
                    add(comp, sc, A + (sc - 1) * X_, clip)
        # 風力・太陽光が作る日間変動（年度内偏差 × 時刻別負荷 B(h)）
        Wd = (inf["wind"] - inf.groupby("fy")["wind"].transform("mean")).to_numpy()
        Sd = (inf["solar"] - inf.groupby("fy")["solar"].transform("mean")).to_numpy()
        Dd = (inf["demand"] - inf.groupby("fy")["demand"].transform("mean")).to_numpy()
        Xh = np.column_stack([Wd, Sd, Dd])
        Bh = np.linalg.lstsq(Xh, D, rcond=None)[0]
        for j, comp in ((0, "風力が作る日間変動"), (1, "太陽光が作る日間変動")):
            cmp_ = np.outer(Xh[:, j], Bh[j])
            for sc in (0.0, 1.0, 2.0, 3.0):
                for clip in (True, False):
                    add(comp, sc, A + (sc - 1) * cmp_, clip)
        # 水準成分の性質の確認: 打ち切りなしの加法シフト c_d は上位・下位の時刻を変えず、粗利を −4(1−η)c_d だけ動かす
        active = (ETA * np.sort(A, 1)[:, -H4:].sum(1) - np.sort(A, 1)[:, :H4].sum(1)) > 0
        print(f"[{SEASON_LABEL[s]}] 水準成分の偏差の平均（休止なしの日）={Lv[active, 0].mean():+.2e} 円/kWh、"
              f"休止日 {int((~active).sum())} 日 → s 倍の加法シフトによる平均粗利の変化は −4(1−η)(s−1)×この値（≈0）")
    sens = pd.DataFrame(sens_rows)
    # 年間（3季節の合計、FY2023-25 平均の円/kW-年）
    ann = (sens.groupby(["成分", "倍率s", "下限で打ち切り"], as_index=False)[["PF合計（円/kW、3年）", "固定窓合計（円/kW、3年）", "日数"]].sum())
    ann["季節"] = "年間（FY2023-25平均、円/kW-年）"
    ann["PF（円/kW-日）"] = np.nan
    ann["固定窓（円/kW-日）"] = np.nan
    ann["PF年間（円/kW-年）"] = ann["PF合計（円/kW、3年）"] / n_fy
    ann["固定窓年間（円/kW-年）"] = ann["固定窓合計（円/kW、3年）"] / n_fy
    base_ann = ann[(ann["成分"] == "PC1") & (ann["倍率s"] == 1.0) & (ann["下限で打ち切り"])]["PF年間（円/kW-年）"].iloc[0]
    ann["PF/基準"] = ann["PF年間（円/kW-年）"] / base_ann
    sens = pd.concat([sens, ann[sens.columns.intersection(ann.columns).tolist() + ["PF年間（円/kW-年）", "固定窓年間（円/kW-年）"]]],
                     ignore_index=True)
    save(sens, "sensitivity")

    # ------------------------------------------------ 標準出力
    print("\n=== 寄与率（PC1-3） ===")
    v3 = var[var["PC"] <= 3].pivot_table(index="仕様", columns="PC", values="寄与率", sort=False)
    v3["累積3"] = v3.sum(axis=1)
    print(v3.round(3).to_string())
    print("\n=== 負荷の形 ===")
    print(load[["仕様", "PC", "寄与率", "cos(負荷, 一様)", "cos(負荷, p̄−0.01)", "夜0-5平均", "昼11-13平均", "夕方17-19平均",
                "h03", "h12", "h18"]][~load["仕様"].str.startswith("E")].round(3).to_string(index=False))
    print("\n=== 因子と既存指標（FY×季節内） ===")
    print(corr.round(3).to_string(index=False))
    print("\n=== 因子スコア回帰（NW14 の有意性） ===")
    sh_ = reg[reg["被説明変数"].isin(["PC1", "PC2", "PC3"])].copy()
    sh_["表示"] = [f"{v:+.3f}{stars(p)}" for v, p in zip(sh_["推定値"], sh_["p_NW14"])]
    print(sh_.pivot_table(index="係数", columns=["標本", "負荷", "被説明変数"], values="表示", aggfunc="first").loc[KEYS].to_string())
    print("発電量1SD（年度内）あたりの因子の動き（因子の年度・季節内SD単位）:")
    print(reg[reg["被説明変数"].isin(["PC1", "PC2"])].pivot_table(
        index="係数", columns=["標本", "負荷", "被説明変数"], values="発電量1SDあたり（因子の年度・季節内SD単位）",
        aggfunc="first").loc[KEYS].round(3).to_string())
    print("残差の1次自己相関（FY2016-25）:",
          reg[(reg["標本"] == "FY2016-25") & (reg["係数"] == "wind_冬")].set_index("被説明変数")["残差の1次自己相関"].round(3).to_dict())
    print("\n=== 形状検定（NW14） ===")
    cols_show = ["標本", "係数", "時刻平均（日平均への効果）", "最小（時刻）", "最大（時刻）", "変動係数 sd(b)/|mean(b)|",
                 "一様成分の比率 24·mean²/‖b‖²（参考）", "夕方−昼", "p(夕方−昼)", "夕方−夜(0-5時)", "p(夕方−夜)",
                 "p 平行(23)", "p 平行(縮約5)", "p 平行(縮約5, ブロックBS)", "λ（b≈λ·p̄、GLS）", "p 比例(23)",
                 "p 比例(縮約5)", "p 比例(縮約5, ブロックBS)"]
    print(tests[tests["共分散"] == "NW14"][cols_show].round(3).to_string(index=False))
    print("\n=== 比例シフトの p（NW7）===")
    print(tests[tests["共分散"] == "NW7"][["標本", "係数", "p 比例(23)", "p 比例(縮約5)", "p 平行(23)"]].round(3).to_string(index=False))
    print("\n=== コントラストと既存指標（NW14 の有意性） ===")
    c2 = con.copy()
    c2["表示"] = [f"{v:+.3f}{stars(p)}" for v, p in zip(c2["推定値"], c2["p_NW14"])]
    print(c2.pivot_table(index="係数", columns=["標本", "被説明変数"], values="表示", aggfunc="first").loc[KEYS].T.to_string())
    print("\n=== TB4h 係数の経路分解 ===")
    print(tb.round(3).to_string(index=False))
    print("\n=== 完全予見粗利の因子エクスポージャー ===")
    print(pfx.round(3).to_string(index=False))
    print("\n=== 完全予見粗利への効果の経路分解（円/kW-日 per GWh/日） ===")
    print(pfc.round(3).to_string(index=False))
    print("\n=== 頑健性: 期間別の主成分によるエクスポージャーと、粗利と日平均価格の相関（FY×季節内） ===")
    print(per.round(3).to_string(index=False))
    print("\n=== 因子別の感応度（FY2023-25、下限で打ち切り、PF 円/kW-日） ===")
    sv = sens[sens["季節"] != "年間（FY2023-25平均、円/kW-年）"]
    print(sv.pivot_table(index=["季節", "成分", "下限で打ち切り"], columns="倍率s", values="PF（円/kW-日）", sort=False).round(2).to_string())
    print("\n固定窓（円/kW-日）")
    print(sv.pivot_table(index=["季節", "成分", "下限で打ち切り"], columns="倍率s", values="固定窓（円/kW-日）", sort=False).round(2).to_string())
    print("\n年間（円/kW-年）")
    sa = sens[sens["季節"] == "年間（FY2023-25平均、円/kW-年）"]
    print(sa.pivot_table(index=["成分", "下限で打ち切り"], columns="倍率s", values="PF年間（円/kW-年）", sort=False).round(0).to_string())
    print(f"基準の年間完全予見粗利（FY2023-25平均）= {base_ann:,.0f} 円/kW-年（原稿 7.4 の 10,317 と一致: {round(base_ann) == 10317}）")
    print("\n原稿表6.2との照合（HC3、FY2016-25）:")
    print(con[(con["標本"] == "FY2016-25") & con["被説明変数"].isin(["TB4h", "日平均価格"])]
          .pivot_table(index="係数", columns="被説明変数", values="推定値").loc[KEYS].round(3).to_string())

    # ------------------------------------------------ 図
    make_figure(load, var, hourly, tests)


def fmt_p(p):
    return "<0.01" if p < 0.01 else f"={p:.2f}"


def make_figure(load, var, hourly, tests):
    fig, axes = plt.subplots(3, 3, figsize=(13.5, 11.2))
    specA = "A: FY×季節内の偏差（主仕様、FY2016-25）"
    specD = "D: FY2023-25（FY×季節内の偏差）"
    hcols = [f"h{h:02d}" for h in HOURS]
    names = {1: "第1主成分（水準）", 2: "第2主成分（昼と夕方の差）", 3: "第3主成分（夜と夕方の差）"}
    for k in (1, 2, 3):
        ax = axes[0, k - 1]
        la = load[(load["仕様"] == specA) & (load["PC"] == k)].iloc[0]
        ld = load[(load["仕様"] == specD) & (load["PC"] == k)].iloc[0]
        ax.axhline(0, color="#BBBBBB", lw=0.8)
        ax.plot(HOURS, la[hcols].to_numpy(float), color=C_PC[k - 1], lw=2, label="FY2016〜25")
        ax.plot(HOURS, ld[hcols].to_numpy(float), color=C_PC[k - 1], lw=1.6, ls="--", label="FY2023〜25")
        ax.set_title(f"{names[k]}\n寄与率 {la['寄与率']*100:.0f}%（FY2023〜25 {ld['寄与率']*100:.0f}%）", fontsize=11, pad=6)
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlim(-0.5, 23.5)
        ax.tick_params(labelsize=9, colors=GRAY)
        ax.set_xlabel("時刻", fontsize=9.5, color=GRAY)
        if k == 1:
            ax.set_ylabel("負荷（単位ベクトル）", fontsize=10, color=GRAY)
        ax.legend(fontsize=8.5, frameon=False, loc="best")
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    for r, tag in ((1, "FY2016-25"), (2, "FY2023-25")):
        for c, s in enumerate(MAIN_SEASONS):
            # 縦軸はパネルごと（冬の太陽光の広い帯で他の季節の風力の形が潰れないように）
            hs = hourly[(hourly["標本"] == tag) & hourly["係数"].isin([f"wind_{s}", f"solar_{s}"])]
            ymin = hs["下限95%(NW14)"].min()
            ymax = max(0.25, hs["上限95%(NW14)"].max()) + 0.1
            ax = axes[r, c]
            for lo, hi in ((0, 5), (11, 13), (17, 19)):
                ax.axvspan(lo - 0.5, hi + 0.5, color="#F0F0F0", lw=0, zorder=0)
            ax.axhline(0, color="#BBBBBB", lw=0.8)
            for src, col, lab in (("wind", C_WIND, "風力"), ("solar", C_SOLAR, "太陽光")):
                g = hourly[(hourly["標本"] == tag) & (hourly["係数"] == f"{src}_{s}")].sort_values("時刻")
                ax.fill_between(g["時刻"], g["下限95%(NW14)"], g["上限95%(NW14)"], color=col, alpha=0.15, lw=0)
                ax.plot(g["時刻"], g["推定値"], color=col, lw=2, label=lab)
                if src == "wind":
                    ax.plot(g["時刻"], g["比例シフトの当てはめ λ·p̄_h(最小二乗)"], color=col, lw=1.1, ls=":",
                            label="風力の比例シフトの当てはめ（λ×季節の平均価格）")
            tw = tests[(tests["標本"] == tag) & (tests["共分散"] == "NW14") & (tests["係数"] == f"wind_{s}")].iloc[0]
            ts = tests[(tests["標本"] == tag) & (tests["共分散"] == "NW14") & (tests["係数"] == f"solar_{s}")].iloc[0]
            txt = (f"夕方−昼  風力 {tw['夕方−昼']:+.2f}{stars(tw['p(夕方−昼)'])}  太陽光 {ts['夕方−昼']:+.2f}{stars(ts['p(夕方−昼)'])}\n"
                   f"夕方−夜  風力 {tw['夕方−夜(0-5時)']:+.2f}{stars(tw['p(夕方−夜)'])}  太陽光 {ts['夕方−夜(0-5時)']:+.2f}{stars(ts['p(夕方−夜)'])}\n"
                   f"風力 平行シフト p{fmt_p(tw['p 平行(縮約5)'])}・比例シフト p{fmt_p(tw['p 比例(縮約5)'])}（縮約5制約）")
            ax.text(0.02, 0.03, txt, transform=ax.transAxes, fontsize=7.8, color=GRAY, va="bottom")
            ax.set_ylim(ymin - 0.05 - 0.45 * (ymax - ymin), ymax + 0.05)
            ax.set_xticks(range(0, 24, 3))
            ax.set_xlim(-0.5, 23.5)
            ax.tick_params(labelsize=9, colors=GRAY)
            ax.set_title(f"{SEASON_LABEL[s]}・{tag.replace('-', '〜').replace('FY2016〜25', 'FY2016〜25').replace('FY2023〜25', 'FY2023〜25')}",
                         fontsize=11, pad=6)
            if r == 1:
                for lo, hi, nm in ((0, 5, "夜"), (11, 13, "昼"), (17, 19, "夕方")):
                    ax.text((lo + hi) / 2, 0.985, nm, ha="center", va="top", fontsize=8, color=GRAY,
                            transform=ax.get_xaxis_transform())
            if c == 0:
                ax.set_ylabel("時刻別係数（円/kWh per GWh/日）", fontsize=10, color=GRAY)
            if r == 2:
                ax.set_xlabel("時刻", fontsize=9.5, color=GRAY)
            if r == 1 and c == 0:
                handles, labels = ax.get_legend_handles_labels()
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
    fig.suptitle("24時間価格カーブの主成分と、風力・太陽光の時刻別係数（北海道エリアプライス）",
                 fontsize=13.5, fontweight="bold", y=0.995)
    fig.text(0.99, 0.003,
             "上段: FY×季節×時刻の平均を除いた偏差の主成分負荷。中段・下段: 原稿5.2.3と同じ右辺の時刻別回帰の係数と Newey-West(14日) の95%帯。"
             "灰色の帯は夜(0〜5時)・昼(11〜13時)・夕方(17〜19時)。縦軸の範囲はパネルごとに異なる。\n***p<0.01、**p<0.05、*p<0.1（NW14）。平行・比例シフトの p は4時間ブロック平均に縮約した Wald（5制約、NW14）。点線は風力の比例シフトの最小二乗の当てはめ。"
             "北海道エリアプライス（60分値）、発電量は制御前。",
             ha="right", fontsize=7.5, color=GRAY)
    fig.legend(handles, ["風力（95%帯つき）", "風力の比例シフトの当てはめ（λ×季節の平均価格）", "太陽光（95%帯つき）"],
               loc="lower center", bbox_to_anchor=(0.5, 0.035), ncol=3, fontsize=9.5, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 0.975))
    fig.savefig(os.path.join(FIGDIR, "price_curve_pca.png"), dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("saved figures/hokkaido/price_curve_pca.png")


if __name__ == "__main__":
    main()
