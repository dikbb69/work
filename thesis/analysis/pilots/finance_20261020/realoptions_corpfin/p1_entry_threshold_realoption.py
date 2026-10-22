#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット1: 参入の閾値を実物オプションで評価する（静学ゼロレント θ* と動学的な参入閾値 θ̄ の比較）

リポジトリは読むだけ。出力はこのディレクトリの out/ へ。

構成
  A. 価格水準 θ の確率過程の推定
     - 月次 θ（price_level_theta.csv、FY2022-04〜2026-06、51か月）
     - 長期の代理変数: 月平均システムプライス／FY2023-25 の同月平均（FY2016-04〜2026-06）
     - Schwartz-Smith 型の2因子分解（恒久成分＝ランダムウォーク、一時成分＝AR(1)）を
       statsmodels UnobservedComponents（状態空間・カルマンフィルタ）で推定
  B. 参入閾値（年次の動的計画法、対数θの格子上）
     年間キャッシュフロー = a·θ − F（a = capture率0.81 × π_PF(0)=8,265、F = 運維・廃止0.53万＋託送等固定0.69万
     ＋充電従量1,752 − 実効容量収入1.25万）、投資額 I_t = 4h×資本費（6.8万円/kWh、低下率 g、下限2.3万円/kWh）、寿命20年
     静学 θ*_t = (I_t·CRF + F)/a（原稿 9.4 の定義。θ が現在値のまま続くと置く）
     動学 θ̄_t = 待機を考慮した最適投資の閾値（Dixit-Pindyck）。Leahy (1993) により競争均衡の参入閾値と一致（GBM の場合）
  C. 競争均衡のフリート経路（Dixit-Pindyck 第8章の産業均衡: 収入 X = θ·c·π_PF(K) が θ̄ で反射）と
     参入が開く確率（初到達確率）を 2030/2035/2040 年度について計算
  D. 排他的な参入権（接続枠）を持つ主体の待機オプション価値 W_0（円/kW）
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

REPO = "/Users/matsuba/work/thesis"
PROC = os.path.join(REPO, "data", "processed")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261020)
pd.set_option("display.width", 200)

# ---------------- 原稿の諸元（09_wedge.md 9.4、28_equilibrium_surface.py） ----------------
CAPTURE = 0.81
PI_PF0 = 8_265.0                       # π_PF(0), θ=1（equilibrium_surface.csv 泊なし・風力×1）
A_COEF = CAPTURE * PI_PF0              # 6,694.65 円/kW-年 per θ
OM, WHEEL, CHG, KPCAP = 5_300.0, 6_900.0, 4 * 365 * 1.2, 12_500.0
F_NET = OM + WHEEL + CHG - KPCAP       # 1,452 円/kW-年（θ に比例しない正味固定費）
CAPEX0, CAPEX_FLOOR = 6.8e4, 2.3e4     # 円/kWh
I0 = 4 * CAPEX0                        # 272,000 円/kW
T_LIFE = 20
PI_K = pd.Series({0: 8265, 10: 7144, 25: 5113, 50: 3416, 100: 961, 150: 198, 200: 12}, dtype=float)  # θ=1 の π_PF(K)


def crf(r, n=T_LIFE):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def theta_static(I, r):
    return (I * crf(r) + F_NET) / A_COEF


print(f"検算: θ*(6.8万, 6%) = {theta_static(I0, 0.06):.3f}（原稿 表9.2: 3.76）")

# =====================================================================================
# A. θ の確率過程
# =====================================================================================
th = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
thm = th[th["ym"].str.contains("-")].copy()
thm["date"] = pd.to_datetime(thm["ym"] + "-01")
thm = thm.set_index("date")["theta_m"]

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"],
                 usecols=["ts", "p_system", "p_hokkaido", "fy"])
hp["m"] = hp["ts"].dt.to_period("M").dt.to_timestamp()
mon = hp.groupby("m")[["p_system", "p_hokkaido", "fy"]].mean()
mon["fy"] = mon["fy"].round().astype(int)
mon["cal"] = mon.index.month
base = mon[mon["fy"].between(2023, 2025)].groupby("cal")[["p_system", "p_hokkaido"]].mean()
mon["proxy_sys"] = mon["p_system"] / mon["cal"].map(base["p_system"])
mon["proxy_hkd"] = mon["p_hokkaido"] / mon["cal"].map(base["p_hokkaido"])
mon = mon[mon.index >= "2016-04-01"]
ov = mon.join(thm.rename("theta_m"), how="inner")
print(f"\n[A] 月次 θ と代理変数の対数相関（重複 {len(ov)} か月）: システム {np.corrcoef(np.log(ov['theta_m']), np.log(ov['proxy_sys']))[0,1]:.3f}, "
      f"北海道 {np.corrcoef(np.log(ov['theta_m']), np.log(ov['proxy_hkd']))[0,1]:.3f}")

est_rows = []


def ar1(x, label, per_year):
    y, xl = x[1:], x[:-1]
    X = sm.add_constant(xl)
    res = sm.OLS(y, X).fit()
    phi = res.params[1]
    sig = np.sqrt(res.scale)
    d = np.diff(x)
    est_rows.append({"系列": label, "n": len(x), "φ(期あたり)": phi, "φ(年換算)": phi ** per_year,
                     "半減期(年)": np.log(0.5) / np.log(phi) / per_year if 0 < phi < 1 else np.nan,
                     "対数差分SD×√期数(年率)": d.std(ddof=1) * np.sqrt(per_year),
                     "AR残差SD(期)": sig})


ar1(np.log(thm.to_numpy()), "θ_m 月次 FY2022-26", 12)
ar1(np.log(mon["proxy_sys"].to_numpy()), "代理(システム) 月次 FY2016-26", 12)
ar1(np.log(mon["proxy_hkd"].to_numpy()), "代理(北海道) 月次 FY2016-26", 12)
fy_sys = hp[hp["fy"] <= 2025].groupby("fy")["p_system"].mean()
fy_sys = fy_sys / fy_sys.loc[2023:2025].mean()
ar1(np.log(fy_sys.to_numpy()), "代理(システム) 年度 FY2016-25", 1)
thfy = th[~th["ym"].str.contains("-")].set_index("fy")["theta_m"]
est_rows.append({"系列": "θ_FY 年度 FY2022-26", "n": len(thfy),
                 "対数差分SD×√期数(年率)": np.diff(np.log(thfy.to_numpy())).std(ddof=1)})
estA = pd.DataFrame(est_rows)
print(estA.round(3).to_string(index=False))

# Schwartz-Smith 型 2因子: log proxy = ξ（ランダムウォーク）+ χ（AR(1)）+ 観測誤差なし
uc_rows = {}
for col in ("proxy_sys", "proxy_hkd"):
    y = np.log(mon[col].to_numpy())
    mod = sm.tsa.UnobservedComponents(y, level="random walk", autoregressive=1)
    res = mod.fit(disp=False, maxiter=2000)
    p = dict(zip(mod.param_names, res.params))
    s_lvl = np.sqrt(p["sigma2.level"]) * np.sqrt(12)
    phi = p["ar.L1"]
    s_ar = np.sqrt(p["sigma2.ar"])
    lvl = res.smoothed_state[0]
    ar_ = res.smoothed_state[1]
    filt_lvl = res.filtered_state[0]
    uc_rows[col] = {"σ_ξ(年率)": s_lvl, "φ_χ(月)": phi, "χ 半減期(月)": np.log(0.5) / np.log(phi) if 0 < phi < 1 else np.nan,
                    "σ_χ(月)": s_ar, "χ定常SD": s_ar / np.sqrt(1 - phi ** 2) if abs(phi) < 1 else np.nan,
                    "ξ 2026-06(filtered)": np.exp(filt_lvl[-1]), "ξ 2026-06(smoothed)": np.exp(lvl[-1]),
                    "χ 2026-06(smoothed)": np.exp(ar_[-1]), "loglik": res.llf}
    comp = pd.DataFrame({"log_proxy": y, "xi_smoothed": lvl, "chi_smoothed": ar_, "xi_filtered": filt_lvl}, index=mon.index)
    comp.to_csv(os.path.join(OUT, f"p1_twofactor_{col}.csv"))
    # 年度平均での分解（FY2022 と FY2026）
    fyx = comp.join(mon["fy"]).groupby("fy")[["log_proxy", "xi_smoothed", "chi_smoothed"]].mean().apply(np.exp)
    uc_rows[col]["FY2022: 実績/恒久/一時"] = "/".join(f"{v:.2f}" for v in fyx.loc[2022])
    uc_rows[col]["FY2026上期: 実績/恒久/一時"] = "/".join(f"{v:.2f}" for v in fyx.loc[2026])
uc = pd.DataFrame(uc_rows).T
print("\n[A] 2因子分解（Schwartz-Smith 型、状態空間・カルマンフィルタ）")
print(uc.to_string())
estA.to_csv(os.path.join(OUT, "p1_A_theta_process.csv"), index=False)
uc.to_csv(os.path.join(OUT, "p1_A_twofactor.csv"))
SIG_XI = float(uc.loc["proxy_sys", "σ_ξ(年率)"])
XI_NOW = float(uc.loc["proxy_sys", "ξ 2026-06(filtered)"])

# =====================================================================================
# B. 参入閾値（年次 DP）
# =====================================================================================
NX = 1201
XG = np.linspace(np.log(0.02), np.log(80.0), NX)
HX = XG[1] - XG[0]
TH_G = np.exp(XG)


def trans_matrix(mu_next, sd):
    """各格子点 i から次期 x' ~ N(mu_next[i], sd) への遷移確率（端は吸収して和=1）"""
    edges = np.concatenate([[-np.inf], (XG[:-1] + XG[1:]) / 2, [np.inf]])
    cdf = norm.cdf((edges[None, :] - mu_next[:, None]) / sd)
    return np.diff(cdf, axis=1)


def capex_path(g, H):
    t = np.arange(H + 1)
    return np.maximum(4 * CAPEX_FLOOR, I0 * (1 - g) ** t)


def solve(sigma, r, g, process="gbm", phi=None, xbar=0.0, H=80):
    """θ̄_t（t=0）と W_0(θ) を返す。process: gbm（θ はマルチンゲール）/ ou（対数θが AR(1)、年次）"""
    disc = 1 / (1 + r)
    It = capex_path(g, H)
    k = np.arange(1, T_LIFE + 1)
    dfk = disc ** k
    if process == "gbm":
        P = trans_matrix(XG - 0.5 * sigma ** 2, sigma)
        Eth = TH_G[:, None] * np.ones_like(k)[None, :]
    else:
        s2 = sigma ** 2 / (1 - phi ** 2)
        P = trans_matrix(xbar + phi * (XG - xbar), sigma)
        Eth = np.exp(xbar + (phi ** k)[None, :] * (XG[:, None] - xbar) + 0.5 * s2 * (1 - phi ** (2 * k))[None, :])
    pv_rev = (A_COEF * Eth - F_NET) @ dfk                 # 格子点ごとの 20 年 PV（投資額控除前）
    W = np.maximum(pv_rev - It[H], 0.0)
    thr = np.full(H + 1, np.nan)
    for t in range(H - 1, -1, -1):
        npv = pv_rev - It[t]
        cont = disc * (P @ W)
        ex = (npv >= cont) & (npv > 0)
        W = np.where(ex, npv, cont)
        if ex.any():
            thr[t] = TH_G[np.argmax(ex)]
    return thr, W, pv_rev


def beta_disc(sigma, r):
    return 0.5 + np.sqrt(0.25 + 2 * np.log(1 + r) / sigma ** 2)


# 検証: g=0・GBM で DP の倍率と閉形式 β/(β−1)（年次離散のマルチンゲール）
print("\n[B] 検証: GBM・g=0・r=6% の DP 倍率 vs 閉形式 β/(β−1)")
for s in (0.10, 0.20, 0.30):
    thr, _, _ = solve(s, 0.06, 0.0)
    b = beta_disc(s, 0.06)
    # 有限寿命・正味固定費込みの静学 θ*（θ が恒常的に続く場合の NPV=0）
    print(f"  σ={s:.2f}: DP θ̄/θ* = {thr[0] / theta_static(I0, 0.06):.3f}  閉形式 β/(β−1) = {b / (b - 1):.3f}")

rowsB = []
SIGMAS = [0.01, 0.10, 0.15, 0.20, round(SIG_XI, 3), 0.30]
for r in (0.05, 0.06, 0.08):
    for g in (0.0, 0.03, 0.05, 0.08):
        ts = theta_static(I0, r)
        for s in SIGMAS:
            thr, W, _ = solve(s, r, g)
            rowsB.append({"r(WACC)": r, "資本費低下率g": g, "σ": s, "θ*静学": ts, "θ̄動学": thr[0],
                          "倍率θ̄/θ*": thr[0] / ts,
                          "Jorgenson倍率(σ→0近似)": (r + g) / r if g > 0 else 1.0})
dfB = pd.DataFrame(rowsB)
dfB.to_csv(os.path.join(OUT, "p1_B_thresholds.csv"), index=False)
print("\n[B] 参入閾値（t=0、資本費6.8万円/kWh、実効容量収入1.25万、capture 0.81）")
print(dfB[dfB["r(WACC)"] == 0.06].round(3).to_string(index=False))
print(dfB[(dfB["r(WACC)"] != 0.06) & (dfB["σ"].isin([0.01, round(SIG_XI, 3)]))].round(3).to_string(index=False))

# 一時成分しかない（平均回帰のみ）場合: θ_now の高さが続かないときの NPV=0 となる θ
print("\n[B'] 一時的な価格水準の上昇（年次 AR(1)、長期平均 θ=1）だけで NPV≥0 になる θ（r=6%, g=0）")
rowsBp = []
for phi_a in (0.3, 0.5, 0.7, 0.9):
    s_a = 0.25
    s2 = s_a ** 2 / (1 - phi_a ** 2)
    xbar = -0.5 * s2
    thr, W, pv = solve(s_a, 0.06, 0.0, "ou", phi_a, xbar)
    npv = pv - I0
    th0 = TH_G[np.argmax(npv > 0)] if (npv > 0).any() else np.nan
    rowsBp.append({"φ(年)": phi_a, "σ(年)": s_a, "NPV=0 の θ_now": th0, "θ̄（待機込み）": thr[0]})
dfBp = pd.DataFrame(rowsBp)
print(dfBp.round(2).to_string(index=False))
dfBp.to_csv(os.path.join(OUT, "p1_Bprime_transitory.csv"), index=False)

# =====================================================================================
# C. 競争均衡のフリート経路と参入が開く確率
# =====================================================================================
Kfine = np.arange(0, 201)
pifine = np.interp(Kfine, PI_K.index.to_numpy(), PI_K.to_numpy())


def k_of(theta_level, thr_mult_level):
    """θ 水準で、限界参入者の (θ·c·π_PF(K) − F)/(c·π_PF(0)) 相当が閾値を満たす最大 K
    閾値条件: θ·c·π_PF(K) − F ≥ θ_thr·a − F  ⇔  θ·π_PF(K) ≥ θ_thr·π_PF(0)"""
    ok = theta_level * pifine >= thr_mult_level * PI_PF0
    return Kfine[ok].max() if ok.any() else 0


def fleet_paths(theta0, sigma, r, g, years, n=20000):
    """θ（恒久成分）を GBM マルチンゲールで生成。動学: 参入閾値 θ̄_t に対し K_t = max_s≤t K(θ_s; θ̄_s)（不可逆）
    静学: K_t = K(θ_t; θ*_t)（その年の θ が続くと置いた原稿型の判定、退出なし）"""
    H = max(years) - 2026
    thr, _, _ = solve(sigma, r, g, H=H + 60)
    It = capex_path(g, H + 60)
    ths = np.array([theta_static(It[t], r) for t in range(H + 1)])
    z = rng.standard_normal((n, H))
    lt = np.log(theta0) + np.cumsum(-0.5 * sigma ** 2 + sigma * z, axis=1)
    thp = np.exp(lt)                                     # t=1..H（FY2027..）
    out = {}
    run_dyn = np.zeros(n)
    run_sta = np.zeros(n)
    open_dyn = np.zeros(n, bool)
    open_sta = np.zeros(n, bool)
    for t in range(1, H + 1):
        th_t = thp[:, t - 1]
        kd = np.array([k_of(v, thr[t]) for v in th_t])
        ks = np.array([k_of(v, ths[t]) for v in th_t])
        run_dyn = np.maximum(run_dyn, kd)
        run_sta = np.maximum(run_sta, ks)
        open_dyn |= th_t >= thr[t]
        open_sta |= th_t >= ths[t]
        fy = 2026 + t
        if fy in years:
            out[fy] = {"P(参入が開く)_動学": open_dyn.mean(), "P(参入が開く)_静学": open_sta.mean(),
                       "E[K]_動学(万kW)": run_dyn.mean(), "E[K]_静学(万kW)": run_sta.mean(),
                       "K 95%点_動学": np.percentile(run_dyn, 95), "K 95%点_静学": np.percentile(run_sta, 95),
                       "θ̄_t": thr[t], "θ*_t": ths[t]}
    return out


rowsC = []
YEARS = [2030, 2035, 2040]
for lab, th0 in (("θ0=恒久成分の推定値(2026-06)", XI_NOW), ("θ0=1.57（FY2026上期が恒久と仮定）", 1.57), ("θ0=1.00", 1.0)):
    for g in (0.0, 0.05):
        for s in (round(SIG_XI, 3), 0.30):
            res = fleet_paths(th0, s, 0.06, g, YEARS, n=4000)
            for fy, d in res.items():
                rowsC.append({"出発点": lab, "θ0": th0, "g": g, "σ": s, "年度": fy, **d})
dfC = pd.DataFrame(rowsC)
dfC.to_csv(os.path.join(OUT, "p1_C_entry_probability.csv"), index=False)
print("\n[C] 参入が開く確率と競争均衡のフリート経路（r=6%、資本費6.8万→下限2.3万、容量収入1.25万一定）")
print(dfC.round(3).to_string(index=False))

# =====================================================================================
# D. 排他的な参入権（接続枠）の待機オプション価値
# =====================================================================================
rowsD = []
for s in (round(SIG_XI, 3), 0.20, 0.30):
    for g in (0.0, 0.03, 0.05, 0.08):
        thr, W, pv = solve(s, 0.06, g)
        for th0 in (1.0, XI_NOW, 1.57):
            i = np.argmin(np.abs(TH_G - th0))
            rowsD.append({"σ": s, "g": g, "θ0": round(th0, 3), "静学NPV(円/kW)": pv[i] - I0, "待機オプション価値W0(円/kW)": W[i],
                          "W0/I0": W[i] / I0})
dfD = pd.DataFrame(rowsD)
dfD.to_csv(os.path.join(OUT, "p1_D_option_value.csv"), index=False)
print("\n[D] 排他的な参入権の価値（r=6%、マーチャント収入のみ、円/kW）")
print(dfD.round(3).to_string(index=False))
