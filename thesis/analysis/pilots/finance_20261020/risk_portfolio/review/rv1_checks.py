#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""risk_portfolio 敵対的レビュー: r1〜r3 の再検証と修正計算（リポジトリは読むだけ。出力は review/）

(1) log PF 分散分解の FY2022 依存（水準 vs 形状の寄与）
(2) A3 の確実性等価: 20年年金換算の SD に λρ を掛けるのは「時間分散の誤謬」。
    期ごとの CAPM リスク調整（各期の価値イノベーションに λρ を掛ける、線形近似）で再計算。
    天候・形状ノイズは市場と無相関（ρ=0）とし、θ ショックのみに系統的リスクを置く。
(3) マーチャントの事業 IRR（＝損益分岐 WACC）: K*=0 は WACC に依存しないことの確認
(4) A2: 年次・FY2026Q1 の弾力性、20年基準での θ ≥ θ*_β の確率（単年基準との比較）
(5) B1: ヘッジ有効性を「水準」ではなく「k か月前からの変化」（先物の事前価格の粗い代理）で再計算
(6) 競合参入 K のリスク（π(K)）を水準・天候リスクと同じ物差しで比較
(7) LTDA 上限価格の IRR: 契約容量が期待容量（κ_6h=0.932）ベースの場合
"""
import glob
import os

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

REPO = "/Users/matsuba/work/thesis"
PROC = os.path.join(REPO, "data", "processed")
OUT = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(OUT, "rerun")
ETA, H, CAP = 0.85, 4, 0.81
W_CHG = 1.2 * H * 365
rng = np.random.default_rng(7)


def crf(r, n=20):
    return r / (1 - (1 + r) ** -n)


# ---------------------------------------------------------------- (1)
ann = pd.read_csv(os.path.join(RUN, "r1_annual.csv"), index_col=0)
full = ann.loc[2016:2025]
print("=== (1) log PF 分散分解（365日換算、θ代理=システム比）===")
for lab, sub in {"FY2016-25": full, "FY2016-25 除FY2022": full.drop(index=[2022]),
                 "FY2016-25 除FY2020-22": full.drop(index=[2020, 2021, 2022])}.items():
    lp, lt = np.log(sub.PF_365), np.log(sub.proxy_sys)
    ls = lp - lt
    print(f"{lab}: Var(logPF)={lp.var():.4f}  Var(logθ)={lt.var():.4f}  Var(logS)={ls.var():.4f}  "
          f"2Cov={2 * np.cov(lt, ls)[0, 1]:.4f}  R²(θ)={np.corrcoef(lp, lt)[0, 1] ** 2:.3f}  "
          f"σ_logθ={lt.std():.3f}  σ_logS={ls.std():.3f}")

# ---------------------------------------------------------------- (2) CE（期ごとの CAPM 調整）
S_mean = 10336.0               # r1 (3) の θ=1 形状の年間 PF 平均（L=7）
G = CAP * S_mean               # θ=1 のときの年間スポット粗収入（充電従量控除前）
sig_lt = 0.267
T, R = 20, 0.06
d = 1 / (1 + R)
print("\n=== (2) CAPM 型確実性等価: r1 の方法（20年年金の SD×λρ）vs 期ごとの調整（線形近似）===")
rows = []
pv_sd_r1 = {0.0: 563.4, 0.5: 911.5, 0.9: 1759.9}   # r1_pv20_risk.csv
for phi in [0.0, 0.5, 0.9]:
    se = sig_lt * np.sqrt(1 - phi ** 2)
    # 時点 t の θ ショック ε_t が t..T の CF に与える PV（時点 t 価値）への影響の SD
    # E[θ] ≈ exp(σ²/2) ≈ 1.036 は定常からの開始なので無視（水準1として線形化）
    sd_innov = np.array([se * G * sum((phi * d) ** k for k in range(T - t + 1)) for t in range(1, T + 1)])
    for lam in [0.2, 0.4]:
        for rho in [0.3, 1.0]:
            rp_pv = (lam * rho * sd_innov * d ** np.arange(1, T + 1)).sum()
            rp_ann = rp_pv * crf(R)
            rp_r1 = lam * rho * pv_sd_r1[phi]
            rows.append(dict(phi=phi, lam=lam, rho=rho, RP_r1=rp_r1, RP_per_period=rp_ann,
                             ratio=rp_ann / rp_r1, share_of_gap=rp_ann / (22000 - 6920),
                             LTDA_ins_upper=0.9 * rp_ann))
ce = pd.DataFrame(rows)
print(ce.round(3).to_string(index=False))
ce.to_csv(os.path.join(OUT, "rv1_ce_corrected.csv"), index=False)

# ---------------------------------------------------------------- (3) マーチャント IRR
print("\n=== (3) マーチャント4hの事業 IRR（無レバレッジ・税前、資本費6.8万円/kWh×4=27.2万円/kW、"
      "運維・廃止0.53万＋託送等固定0.69万、20年）===")
CAPEX4 = 272000
FIXED = 5300 + 6900
rows = []
for pi_nm, pi in [("π モデル 4,944（表8.4）", 4944), ("π ×1.25 上限 6,598（表8.5）", 6598),
                  ("π 実績価格 6,620（r1）", 6620), ("π θ=1.57 ×1.25 11,331（表8.5）", 11331),
                  ("π θ=1.72 ×1.25 12,572（表8.5）", 12572)]:
    for kp_nm, kp in [("容量1.25万", 12517), ("容量0.73万（2026向け）", 7314), ("容量0.83万（発動指令）", 8300)]:
        cf = pi + kp - FIXED
        f = lambda r: -CAPEX4 + cf * (1 - (1 + r) ** -20) / r if abs(r) > 1e-9 else -CAPEX4 + 20 * cf
        try:
            irr = brentq(f, -0.3, 0.5)
        except ValueError:
            irr = np.nan
        rows.append(dict(spot=pi_nm, capacity=kp_nm, CFADS=cf, undiscounted_20y=20 * cf, IRR=irr))
irr_t = pd.DataFrame(rows)
print(irr_t.round(4).to_string(index=False))
irr_t.to_csv(os.path.join(OUT, "rv1_merchant_irr.csv"), index=False)

# ---------------------------------------------------------------- (4) A2 の弾力性と 20年基準
print("\n=== (4) A2: 弾力性の時間スケール ===")
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
s = np.sort(P.to_numpy(), axis=1)
dpf = pd.Series(np.maximum(ETA * s[:, -H:].sum(1) - s[:, :H].sum(1), 0), index=P.index)
dfd = pd.DataFrame({"pf": dpf, "fy": P.index.year - (P.index.month < 4), "m": P.index.month})
aj = dfd[dfd.m.isin([4, 5, 6])].groupby("fy")["pf"].sum()
th = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
thm = th[~th.ym.str.startswith("FY")].copy()
thm["m"] = thm.ym.str[-2:].astype(int)
thq = thm[thm.m.isin([4, 5, 6])].groupby("fy")["theta_m"].mean()
base_pf = aj.loc[[2023, 2024, 2025]].mean()
base_th = thq.loc[[2023, 2024, 2025]].mean()
b26 = np.log(aj.loc[2026] / base_pf) / np.log(thq.loc[2026] / base_th)
print(f"4〜6月 PF: FY2023-25平均 {base_pf:.0f} → FY2026 {aj.loc[2026]:.0f}（比 {aj.loc[2026] / base_pf:.3f}）、"
      f"θ(4〜6月平均) {base_th:.3f} → {thq.loc[2026]:.3f}（比 {thq.loc[2026] / base_th:.3f}）→ 弧弾力性 {b26:.2f}")
print("4〜6月 PF 年度別:", aj.round(0).to_dict())

# 20年基準の確率（×1.25 は掛けない＝二重計上を避ける）。参入条件: 年金換算の θ^β 加重平均 ≥ θ*^β（=θ*_β^β）
print("\n20年年金換算での参入確率 P( Σ d^t θ_t^β / Σ d^t ≥ θ*_標準^... ) — θ*（標準3.55, β=1 基準）を PF(θ)=PF(1)θ^β で読み替え")
M = 40000
rows = []
for beta in [1.0, 1.18, 1.42]:
    for phi in [0.5, 0.9]:
        for start, lr_med in [(1.57, 1.0), (1.57, 1.57), (1.0, 1.0)]:
            se = sig_lt * np.sqrt(1 - phi ** 2)
            mu = np.log(lr_med)
            x = np.full(M, np.log(start))
            acc = np.zeros(M)
            for t in range(1, T + 1):
                x = mu + phi * (x - mu) + rng.normal(0, se, M)
                acc += d ** t * np.exp(beta * x)
            avg = acc / sum(d ** t for t in range(1, T + 1))
            for nm, ts in [("標準3.55", 3.55), ("楽観3.17", 3.17)]:
                rows.append(dict(beta=beta, phi=phi, theta0=start, lr_median=lr_med, theta_star=nm,
                                 P_20y=(avg >= ts).mean(),
                                 P_1y_lr=1 - norm.cdf((np.log(ts) / beta - mu) / sig_lt)))
pr = pd.DataFrame(rows)
print(pr.round(4).to_string(index=False))
pr.to_csv(os.path.join(OUT, "rv1_theta_star_20y.csv"), index=False)

# ---------------------------------------------------------------- (5) B1: 変化でのヘッジ有効性
print("\n=== (5) B1: 水準 vs k か月変化のヘッジ有効性（季節除去後、東京ベース・ピーク）===")
frames = []
for f in sorted(glob.glob(os.path.join(REPO, "data", "raw", "jepx", "spot_summary_*.csv"))):
    x = pd.read_csv(f, encoding="cp932").iloc[:, [0, 1, 5, 6, 8]]
    x.columns = ["date", "slot", "sys", "hkd", "tky"]
    frames.append(x)
j = pd.concat(frames, ignore_index=True)
j["date"] = pd.to_datetime(j["date"])
j["hour"] = (j["slot"] - 1) // 2
for c in ["sys", "hkd", "tky"]:
    j[c] = pd.to_numeric(j[c], errors="coerce")
hr = j.groupby(["date", "hour"])[["hkd", "tky"]].mean().reset_index()
hr = hr[hr["date"] <= "2026-06-30"]
Mh = hr.pivot(index="date", columns="hour", values="hkd")
Mt = hr.pivot(index="date", columns="hour", values="tky")
Mh, Mt = Mh[Mh.count(axis=1) == 24], Mt[Mt.count(axis=1) == 24]
days = Mh.index.intersection(Mt.index)
Mh, Mt = Mh.loc[days], Mt.loc[days]
sh = np.sort(Mh.to_numpy(), axis=1)
D = pd.DataFrame({"X": np.maximum(ETA * sh[:, -H:].sum(1) - sh[:, :H].sum(1), 0), "base_t": Mt.mean(axis=1).to_numpy()},
                 index=days)
D["peak_t"] = np.where(days.dayofweek < 5, Mt.loc[:, 8:19].mean(axis=1), np.nan)
D["ym"] = days.to_period("M")
Mo = D.groupby("ym").agg(X=("X", "sum"), base_t=("base_t", "mean"), peak_t=("peak_t", "mean"), n=("X", "size"))
Mo = Mo[Mo.n >= 25]
Mo["cal"] = Mo.index.month
Mo["fy"] = Mo.index.year - (Mo.index.month < 4)
for c in ["X", "base_t", "peak_t"]:
    Mo[c + "_ds"] = Mo[c] - Mo.groupby("cal")[c].transform("mean")
# 連続月のインデックス（欠月があれば差分を作らない）
Mo = Mo.asfreq("M") if False else Mo
idx = Mo.index
rows = []
for samp_nm, keep in {"全期間": np.ones(len(Mo), bool), "FY2023-26": (Mo.fy >= 2023).to_numpy(),
                      "除FY2020-22": (~Mo.fy.isin([2020, 2021, 2022])).to_numpy()}.items():
    for k in [0, 1, 3, 6, 12]:
        for inst in ["base_t", "peak_t"]:
            if k == 0:
                x, fsr = Mo["X_ds"], Mo[inst + "_ds"]
            else:
                lagged = Mo[["X_ds", inst + "_ds"]].copy()
                lagged.index = lagged.index + k     # 期間 index を k か月後へずらす
                x = Mo["X_ds"] - lagged["X_ds"].reindex(Mo.index)
                fsr = Mo[inst + "_ds"] - lagged[inst + "_ds"].reindex(Mo.index)
            z = pd.DataFrame({"x": x, "f": fsr})[keep].dropna()
            h = np.cov(z.x, z.f)[0, 1] / z.f.var()
            he = 1 - (z.x - h * z.f).var() / z.x.var()
            rows.append(dict(sample=samp_nm, k_months=k, instrument=inst, n=len(z), h=h, HE=he))
hk = pd.DataFrame(rows)
print(hk.pivot_table(index=["sample", "k_months"], columns="instrument", values="HE").round(3).to_string())
hk.to_csv(os.path.join(OUT, "rv1_hedge_changes.csv"), index=False)

# ---------------------------------------------------------------- (6) 競合参入 K のリスク
print("\n=== (6) π(K)（表8.4 現状, 円/kW-年）と各リスク源の大きさの比較 ===")
pk = pd.read_csv(os.path.join(PROC, "pi_k_curve.csv"))
pk = pk[pk["シナリオ"] == "現状"].set_index("K(万kW)")["π_実現可能(円/kW-年)"]
interp = lambda k: np.interp(k, pk.index.to_numpy(float), pk.to_numpy(float))
for k in [0, 20, 43.7, 57.7, 77.7, 100]:
    print(f"K={k:>5}万kW: π={interp(k):,.0f}  （K=0 からの低下 {4944 - interp(k):,.0f}）")
# K を一様分布 [20, 57.7+20] 万kW（接続済み＋LTDA北海道分の範囲）とした場合の年次 π の分布（θ=1 の天候・形状ノイズは r1 の SD 342 を加算）
Kd = rng.uniform(20, 77.7, 200000)
pik = interp(Kd) + rng.normal(0, 342, Kd.size)
q = np.quantile(pik, 0.05)
print(f"K~U[20,77.7]万kW: 平均 {pik.mean():,.0f}, 5%点 {q:,.0f}, K=0・θ=1 平均（4,944）からの不足 {4944 - q:,.0f}")

# ---------------------------------------------------------------- (7) LTDA IRR（κ 調整）
print("\n=== (7) LTDA 上限価格の IRR: 契約容量＝設備容量（r3）vs 期待容量（κ_6h=0.932）===")
CAPEX6 = 6.8e4 * 6
spot6 = 13062 * 0.81 - 1.2 * 6 * 365
for F in [50000, 60000, 72000, 77000]:
    out = []
    for kap in [1.0, 0.932]:
        cfs = np.full(20, F * kap - 5000 - 6900 + 0.1 * spot6)
        cfs[-1] -= 0.05 * CAPEX6
        irr = brentq(lambda r: -CAPEX6 + (cfs / (1 + r) ** np.arange(1, 21)).sum(), -0.5, 1.0)
        out.append(irr)
    print(f"F={F:,}: κ=1 → {out[0]:.1%} ／ κ=0.932 → {out[1]:.1%}")
