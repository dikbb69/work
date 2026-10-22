#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""敵対的レビュー用の追加検証（リポジトリには書き込まない。出力は review/out/）

A. 平行シフト Wald（χ²23, NW14）の過大棄却の確認:
   (i) 4時間ブロック平均6本に縮約した5制約の Wald、(ii) 日のブロック・ブートストラップ（14日、B=299）で
   W* = (b*−b̂)' C'(C V* C')^{-1} C (b*−b̂) の分布から臨界値を取る（H0 の下の分布の近似）
B. FGLS(AR1) の SE を、準差分後の回帰に HAC（Andrews 帯域）を当てて再計算
C. θ* の下限: 裾の補正（÷1.25）と capture=1 の場合（原稿 8.4 の式で再計算）
D. 蓄電池の日次 PF 粗利の因子エクスポージャー（PC1〜3）と、風力・太陽光の PF 粗利への効果の経路分解
E. Diebold-Li 型の因子予測戦略（気候値 c ＋ 前日偏差の主成分を AR(1) で持ち越す）と c の DM 比較
"""
import os
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, PROC, MAIN_SEASONS, KEYS, build_daily, design  # noqa: E402
from p1_pca_price_curve import pca, multi_eq_cov, nw_long_run  # noqa: E402
from p2_hac_identification import andrews_bw  # noqa: E402

rng = np.random.default_rng(7)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

d, P = build_daily("hokkaido", "p_hokkaido", return_matrix=True)
P = P.astype(float)
X = design(d)
Xn = X.to_numpy()
cols = list(X.columns)
rows = [cols.index(k) for k in KEYS]
Y = P.to_numpy()
B = np.linalg.lstsq(Xn, Y, rcond=None)[0]
E = Y - Xn @ B

# ---------------- A ----------------
print("=== A. 平行シフト検定の過大棄却チェック（FY2016-25, NW14） ===")
V14 = multi_eq_cov(X, E, rows, 14)
blk = np.zeros((6, 24))
for j in range(6):
    blk[j, 4 * j:4 * j + 4] = 0.25
C5 = blk[1:] - blk[:1]
C23 = np.eye(24)[1:] - np.eye(24)[:1]
resA = []
# ブートストラップ: 14日ブロックで日を再標本化し、係数ベクトルを再推定
n = len(d)
L = 14
nb = int(np.ceil(n / L))
starts = np.arange(0, n - L + 1)
Bstar = []
for b_ in range(299):
    st = rng.choice(starts, nb)
    ix = np.concatenate([np.arange(s, s + L) for s in st])[:n]
    Bb = np.linalg.lstsq(Xn[ix], Y[ix], rcond=None)[0]
    Bstar.append(Bb[rows, :])
Bstar = np.array(Bstar)      # B×6×24
for i, key in enumerate(KEYS):
    b = B[rows[i]]
    Vi = V14[i * 24:(i + 1) * 24, i * 24:(i + 1) * 24]
    W23 = float((C23 @ b) @ np.linalg.solve(C23 @ Vi @ C23.T, C23 @ b))
    W5 = float((C5 @ b) @ np.linalg.solve(C5 @ Vi @ C5.T, C5 @ b))
    # ブートストラップ共分散で Wald（中心化）
    Db = Bstar[:, i, :] - b
    Vb = np.cov(Bstar[:, i, :], rowvar=False)
    W5b = float((C5 @ b) @ np.linalg.solve(C5 @ Vb @ C5.T, C5 @ b))
    # NW14 の Wald を再標本ごとに計算するのは重いので、ブートストラップ共分散版の χ² p 値と
    # 「ブートストラップ分布の分位」による p 値を報告
    Wst = np.array([float((C5 @ db) @ np.linalg.solve(C5 @ Vb @ C5.T, C5 @ db)) for db in Db])
    cv = float(1 + (Wst >= W5b).sum()) / (len(Wst) + 1)
    blk_b = blk @ b
    resA.append({"係数": key, "W23(NW14)": W23, "p23": 1 - stats.chi2.cdf(W23, 23),
                 "W5(NW14)": W5, "p5": 1 - stats.chi2.cdf(W5, 5),
                 "W5(ブロックBS共分散)": W5b, "p5_χ²": 1 - stats.chi2.cdf(W5b, 5), "p5_BS分布": cv,
                 **{f"{4*j:02d}-{4*j+3:02d}時": blk_b[j] for j in range(6)},
                 "CV(時刻別係数)": float(b.std() / abs(b.mean())),
                 "最大/最小": float(b.max() / b.min()) if b.max() < 0 else np.nan})
A = pd.DataFrame(resA)
print(A.round(3).to_string(index=False))
A.to_csv(os.path.join(OUT, "rv_A_parallel_shift_reduced.csv"), index=False, encoding="utf-8-sig")

# ---------------- B ----------------
print("\n=== B. FGLS(AR1) の SE: 古典 SE vs 準差分後の HAC（Andrews 帯域） ===")
resB = []
for ycol in ("mean_p", "tb4"):
    y = d[ycol]
    g = sm.GLSAR(y, X, rho=1).iterative_fit(maxiter=20)
    rho = float(np.atleast_1d(g.model.rho)[0])
    yt = (y.to_numpy()[1:] - rho * y.to_numpy()[:-1])
    Xt = Xn[1:] - rho * Xn[:-1]
    f0 = sm.OLS(yt, Xt).fit()
    r1, bw = andrews_bw(f0.resid)
    fh = sm.OLS(yt, Xt).fit(cov_type="HAC", cov_kwds={"maxlags": max(bw, 7)})
    for k in KEYS:
        j = cols.index(k)
        resB.append({"y": ycol, "係数": k, "ρ": rho, "FGLS推定値": f0.params[j], "古典SE": g.bse[k],
                     "p古典": g.pvalues[k], "準差分残差ρ1": r1, "帯域": max(bw, 7),
                     "HAC SE": fh.bse[j], "p_HAC": fh.pvalues[j]})
Bt = pd.DataFrame(resB)
print(Bt.round(3).to_string(index=False))
Bt.to_csv(os.path.join(OUT, "rv_B_fgls_hac.csv"), index=False, encoding="utf-8-sig")

# ---------------- C ----------------
print("\n=== C. θ* の下限（原稿 8.4: θ* = (c_req − κP_cap + w_chg)/(c·π_PF,model(0))） ===")
w_chg = 1752.0
need = {"標準": 22000.0, "楽観": 19500.0, "保守": 28700.0}
pi_pf0 = (need["標準"] + w_chg) / (0.81 * 3.55)
print(f"逆算 π_PF,model(0) = {pi_pf0:,.0f} 円/kW-年（原稿の 8,265 と整合するか）")
resC = []
for k, v in need.items():
    for cap in (0.81, 0.83, 1.0):
        th = (v + w_chg) / (cap * pi_pf0)
        resC.append({"ケース": k, "capture": cap, "θ*": th, "θ*(裾の補正÷1.25)": th / 1.25})
Ct = pd.DataFrame(resC)
print(Ct.round(2).to_string(index=False))
# p3 の 30日ブロックの比率の下側 2.5% を裾補正後にも当てる
bs = pd.read_csv(os.path.join(os.path.dirname(OUT), "out", "p3_theta_star_bootstrap.csv")) if os.path.exists(
    os.path.join(os.path.dirname(OUT), "out", "p3_theta_star_bootstrap.csv")) else None
if bs is not None:
    r = bs[(bs["ブロック長"] == 30) & (bs["ケース"] == "楽観")].iloc[0]
    print(f"楽観・30日ブロックの下限比 {r['2.5%']/r['θ*点推定']:.3f} → 裾補正後の楽観 2.55 の下限 ≈ {2.55*r['2.5%']/r['θ*点推定']:.2f}")
Ct.to_csv(os.path.join(OUT, "rv_C_theta_bounds.csv"), index=False, encoding="utf-8-sig")

# ---------------- D ----------------
print("\n=== D. 蓄電池の日次 PF 粗利（円/kW-日）の因子エクスポージャー（FY2016-25） ===")
ETA = 0.85
srt_idx = np.argsort(Y, axis=1)
top = np.take_along_axis(Y, srt_idx[:, -4:], axis=1).sum(axis=1)
bot = np.take_along_axis(Y, srt_idx[:, :4], axis=1).sum(axis=1)
pf = np.maximum(0, top * ETA - bot)          # 円/kW-日（1kW×4h）
d["pf"] = pf
cell = d["fy"].astype(str) + "_" + d["season"]
devA = P - P.groupby(cell.values).transform("mean").to_numpy()
w, V = pca(devA.to_numpy())
devB = (P - P.mean()).to_numpy()
F = pd.DataFrame(devB @ V[:, :5], index=d.index, columns=[f"PC{k}" for k in range(1, 6)])
Z = pd.concat([X, F], axis=1)
fz = sm.OLS(d["pf"], Z).fit(cov_type="HAC", cov_kwds={"maxlags": 14})
print("PF粗利 = X·γ + Σ c_k PC_k:", {k: f"{fz.params[k]:+.3f} (t={fz.tvalues[k]:.1f})" for k in F.columns},
      f"R2={fz.rsquared:.3f}")
direct = sm.OLS(d["pf"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 14})
beta_k = {k: sm.OLS(F[k], X).fit().params for k in F.columns}
resD = []
for key in KEYS:
    lvl = fz.params["PC1"] * beta_k["PC1"][key]
    shp = sum(fz.params[f"PC{k}"] * beta_k[f"PC{k}"][key] for k in range(2, 6))
    resD.append({"係数": key, "PF粗利への効果(円/kW-日 per GWh/日)": direct.params[key],
                 "p(NW14)": direct.pvalues[key], "年換算(円/kW-年 per GWh/日)": direct.params[key] * 365,
                 "PC1経由": lvl, "PC2-5経由": shp, "残差": direct.params[key] - lvl - shp})
Dt = pd.DataFrame(resD)
print(Dt.round(3).to_string(index=False))
Dt.to_csv(os.path.join(OUT, "rv_D_pf_factor_exposure.csv"), index=False, encoding="utf-8-sig")

# ---------------- E ----------------
print("\n=== E. Diebold-Li 型の因子予測戦略 vs 気候値 c（北海道 FY2023-25） ===")
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
PP = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
PP = PP[PP.count(axis=1) == 24]
days = PP.index
wkP = pd.Series(days.dayofweek >= 5, index=days)
PA = PP.to_numpy()


def margin(p, order):
    return (p[order[-4:]].sum() * ETA - p[order[:4]].sum())


# 気候値（c と同じ: 過去28日・同曜日区分の平均）を全日について
clim = np.full_like(PA, np.nan)
for i in range(len(days)):
    hist = [j for j in range(max(0, i - 29), i) if wkP.iloc[j] == wkP.iloc[i]]
    if len(hist) >= 5:
        clim[i] = PA[hist].mean(axis=0)
dev = PA - clim          # 当日の気候値からの偏差（当日の実現後に既知）
start = days.get_indexer([pd.Timestamp("2023-04-01")], method="bfill")[0]
recs = []
cache = {}
for i in range(start, len(days)):
    p = PA[i]
    if np.isnan(clim[i]).any() or np.isnan(dev[i - 1]).any():
        continue
    rec = {"day": days[i], "pf": max(0.0, margin(p, np.argsort(p))), "c": margin(p, np.argsort(clim[i]))}
    # 30日ごとに過去365日の偏差で負荷と AR(1) 係数を再推定（先読みなし）
    key = (i - start) // 30
    if key not in cache:
        H = dev[max(0, i - 366):i - 1]
        H = H[~np.isnan(H).any(axis=1)]
        Hc = H - H.mean(axis=0)
        w_, V_ = np.linalg.eigh(np.cov(Hc, rowvar=False))
        V_ = V_[:, np.argsort(w_)[::-1]]
        S = Hc @ V_
        phi = np.array([np.dot(S[1:, k], S[:-1, k]) / np.dot(S[:-1, k], S[:-1, k]) for k in range(24)])
        mu = H.mean(axis=0)
        # 時刻別 AR(1)（24本のスカラー持続）
        phih = np.array([np.dot(H[1:, h] - mu[h], H[:-1, h] - mu[h]) / np.dot(H[:-1, h] - mu[h], H[:-1, h] - mu[h])
                         for h in range(24)])
        cache[key] = (V_, phi, mu, phih)
    V_, phi, mu, phih = cache[key]
    s_prev = (dev[i - 1] - mu) @ V_
    for K in (1, 3, 5):
        fc = clim[i] + mu + V_[:, :K] @ (phi[:K] * s_prev[:K])
        rec[f"DL{K}"] = margin(p, np.argsort(fc))
    fc_shape = clim[i] + mu + V_[:, 1:3] @ (phi[1:3] * s_prev[1:3])   # 形状因子（PC2-3）のみ持ち越し
    rec["DL_shape23"] = margin(p, np.argsort(fc_shape))
    rec["AR_hour"] = margin(p, np.argsort(clim[i] + mu + phih * (dev[i - 1] - mu)))
    recs.append(rec)
bt = pd.DataFrame(recs)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
bt = bt[bt["fy"].between(2023, 2025)]
strat = ["c", "DL1", "DL3", "DL5", "DL_shape23", "AR_hour"]
ann = bt.groupby("fy")[["pf"] + strat].sum()
print("年間価値（円/kW-年）:")
print(ann.round(0).to_string())
print("capture率（%）:")
print((ann[strat].div(ann["pf"], axis=0) * 100).round(1).to_string())


def dm(x, L=7):
    x = np.asarray(x, float)
    T = len(x)
    xc = x - x.mean()
    s = xc @ xc / T
    for j in range(1, L + 1):
        s += 2 * (1 - j / (L + 1)) * (xc[j:] @ xc[:-j] / T)
    t = x.mean() / np.sqrt(s / T)
    return t, 2 * (1 - stats.norm.cdf(abs(t)))


resE = []
for s_ in strat[1:]:
    dd = (bt[s_] - bt["c"]).to_numpy()
    t, p = dm(dd)
    resE.append({"比較": f"{s_} − c", "年換算差(円/kW-年)": dd.mean() * 365, "capture差(pt)": dd.sum() / bt["pf"].sum() * 100,
                 "DM(NW7)": t, "p": p})
Et = pd.DataFrame(resE)
print(Et.round(3).to_string(index=False))
Et.to_csv(os.path.join(OUT, "rv_E_dieboldli_strategy.csv"), index=False, encoding="utf-8-sig")
