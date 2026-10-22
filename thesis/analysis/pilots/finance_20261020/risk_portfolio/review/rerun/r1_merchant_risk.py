#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""risk_portfolio パイロット1: マーチャント・スポット収益のリスク指標と確実性等価（北海道）

リポジトリは読むだけ。出力はこのフォルダ（r1_*.csv）。

(1) 日次の完全予見粗利を再計算（4h・η=0.85・1日1サイクル・上位4h放電/下位4h充電・負の日は休止。
    analysis/03, 16 と同一仕様）→ 年度別の完全予見粗利 PF_y と実現可能収益 π_y = 0.81·PF_y − 1,752
    （充電従量 1.2円/kWh×4h×365日）。表7.1（FY2023 9,873 / FY2024 9,586 / FY2025 11,493 /
    FY2022 25,160）と照合。
(2) 年次の価格水準ファクター: θ_FY（price_level_theta.csv, FY2022〜26）と、FY2016〜25 の代理変数
    （年平均システムプライス・北海道エリアプライスの FY2023〜25 平均比）。PF_y = θ_y × S_y と分けた
    ときの log PF の分散分解（水準 vs 形状）。
(3) 天候・形状リスク（θ=1 に正規化した価格で）: FY2023〜25 の日次粗利の季節（暦月）層別ブロック・
    ブートストラップ（ブロック長 1/7/14/月全体）→ 年間 PF と π の分布、5% CFaR、5% ES。
(4) 水準リスクを重ねた年次分布: θ を (A)=1 固定、(B) FY2016〜25 の経験分布、(C) 対数正規
    → 年間 π の分布、CFaR/ES、参入必要水準（19,500/22,000/28,700）に届く確率。
(5) 20年 PV（年金換算）の分布: log θ を AR(1)（φ=0/0.5/0.9）で、形状は(3)から iid 抽出。
(6) 確実性等価とリスクプレミアム（CAPM 型 CE = E − λ·ρ·σ、λ=市場シャープレシオ、ρ=市場との相関）
    → LTDA の 9割還付が提供する「保険価値」= 0.9 × (E − CE) の上限。
"""
import os

import numpy as np
import pandas as pd

PROC = "/Users/matsuba/work/thesis/data/processed"
OUT = os.path.dirname(os.path.abspath(__file__))
ETA, H = 0.85, 4
CAPTURE = 0.81
W_CHG = 1.2 * H * 365          # 1,752 円/kW-年
C_REQ_NET = {"楽観": 19500, "標準": 22000, "保守": 28700}   # c_req − κP_cap（8.4）
rng = np.random.default_rng(20261020)

# ---------------------------------------------------------------- (1) 日次 PF
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
fy_of = lambda idx: idx.year - (idx.month < 4).astype(int)
FY = pd.Series(fy_of(P.index), index=P.index)


def pf_daily(Pm):
    s = np.sort(Pm, axis=1)
    raw = ETA * s[:, -H:].sum(axis=1) - s[:, :H].sum(axis=1)   # 円/kW-日
    return np.maximum(raw, 0.0), raw


pf, pf_raw = pf_daily(P.to_numpy())
daily = pd.DataFrame({"pf": pf, "pf_raw": pf_raw, "fy": FY.values,
                      "month": P.index.month}, index=P.index)
ann = daily.groupby("fy").agg(PF=("pf", "sum"), n_days=("pf", "size"),
                              idle_share=("pf_raw", lambda x: (x <= 0).mean()))
ann["PF_365"] = ann["PF"] / ann["n_days"] * 365
ann["pi"] = CAPTURE * ann["PF"] - W_CHG

# ---------------------------------------------------------------- (2) 水準ファクター
th = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
th_fy = th[th["ym"].str.startswith("FY")].set_index("fy")["theta_m"]
lvl = hp.assign(fy=fy_of(hp["ts"].dt)).groupby("fy")[["p_system", "p_hokkaido"]].mean()
base = lvl.loc[[2023, 2024, 2025]].mean()
ann["theta_FY"] = th_fy.reindex(ann.index)
ann["proxy_sys"] = (lvl["p_system"] / base["p_system"]).reindex(ann.index)
ann["proxy_hkd"] = (lvl["p_hokkaido"] / base["p_hokkaido"]).reindex(ann.index)
ann["S_sys"] = ann["PF_365"] / ann["proxy_sys"]       # 水準を割り戻した「形状」成分
ann["S_hkd"] = ann["PF_365"] / ann["proxy_hkd"]
print("=== (1)(2) 年度別 完全予見粗利・実現可能収益・水準ファクター（円/kW-年）===")
print(ann.round(3).to_string())
ann.to_csv(os.path.join(OUT, "r1_annual.csv"))

full = ann.loc[2016:2025]
print("\n=== log PF の分散分解（FY2016〜25、365日換算）===")
for px in ["proxy_sys", "proxy_hkd"]:
    lp, lt = np.log(full["PF_365"]), np.log(full[px])
    ls = lp - lt
    v = lp.var(ddof=1)
    beta = np.cov(lp, lt, ddof=1)[0, 1] / lt.var(ddof=1)
    print(f"{px}: Var(logPF)={v:.4f} = Var(logθ) {lt.var(ddof=1):.4f} + Var(logS) {ls.var(ddof=1):.4f}"
          f" + 2Cov {2 * np.cov(lt, ls, ddof=1)[0, 1]:.4f} | 水準の寄与 R²={np.corrcoef(lp, lt)[0, 1] ** 2:.3f}"
          f" | 年次弾力性 β(logPF on logθ)={beta:.2f}")
    sub = full.drop(index=[2022])
    lp2, lt2 = np.log(sub["PF_365"]), np.log(sub[px])
    print(f"   FY2022除外: R²={np.corrcoef(lp2, lt2)[0, 1] ** 2:.3f}, β={np.cov(lp2, lt2, ddof=1)[0, 1] / lt2.var(ddof=1):.2f}")
print("年次PFの記述統計 FY2016〜25（365日換算）: mean={:.0f} sd={:.0f} CV={:.2f} min={:.0f}(FY{}) max={:.0f}(FY{}) median={:.0f}".format(
    full.PF_365.mean(), full.PF_365.std(ddof=1), full.PF_365.std(ddof=1) / full.PF_365.mean(),
    full.PF_365.min(), full.PF_365.idxmin(), full.PF_365.max(), full.PF_365.idxmax(), full.PF_365.median()))
print("年次πの記述統計 FY2016〜25: mean={:.0f} sd={:.0f} 最悪年={:.0f} 最良年={:.0f}".format(
    full.pi.mean(), full.pi.std(ddof=1), full.pi.min(), full.pi.max()))

# ---------------------------------------------------------------- (3) 天候・形状リスク（θ=1）
EST = [2023, 2024, 2025]
mask = FY.isin(EST).values
Pn = P.to_numpy()[mask].copy()
th_d = FY[mask].map(th_fy).to_numpy()
Pn = 0.01 + (Pn - 0.01) / th_d[:, None]      # θ=1 に割り戻した価格（5.4.1 と同じスケーリング）
pfn, _ = pf_daily(Pn)
dn = pd.DataFrame({"pf": pfn, "fy": FY[mask].values, "month": P.index[mask].month},
                  index=P.index[mask])
ann_n = dn.groupby("fy")["pf"].sum()
print("\nθ=1 正規化後の年間PF:", ann_n.round(0).to_dict(), " 実績:", ann.loc[EST, "PF"].round(0).to_dict())

FY_MONTHS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
MDAYS = {4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, 1: 31, 2: 28, 3: 31}
seqs = {(y, m): g["pf"].to_numpy() for (y, m), g in dn.groupby(["fy", "month"])}


def boot_year(L, B):
    out = np.empty(B)
    for b in range(B):
        tot = 0.0
        for m in FY_MONTHS:
            need, got = MDAYS[m], []
            while sum(len(x) for x in got) < need:
                y = EST[rng.integers(0, 3)]
                s = seqs[(y, m)]
                if L >= 28:
                    blk = s
                else:
                    st = rng.integers(0, len(s))
                    blk = np.take(s, np.arange(st, st + L), mode="wrap")
                got.append(blk)
            tot += np.concatenate(got)[:need].sum()
        out[b] = tot
    return out


def risk_stats(x, alpha=0.05):
    q = np.quantile(x, alpha)
    es = x[x <= q].mean()
    return dict(mean=x.mean(), sd=x.std(), q05=q, CFaR05=x.mean() - q, ES05=x.mean() - es,
                CV=x.std() / x.mean())


rows = []
boot_store = {}
for L in [1, 7, 14, 31]:
    s = boot_year(L, 4000)
    boot_store[L] = s
    r_pf = risk_stats(s)
    r_pi = risk_stats(CAPTURE * s - W_CHG)
    rows.append(dict(block=L, **{f"PF_{k}": v for k, v in r_pf.items()},
                     **{f"pi_{k}": v for k, v in r_pi.items()}))
wr = pd.DataFrame(rows)
print("\n=== (3) 天候・形状リスク（θ=1、FY2023〜25 の暦月層別ブロック・ブートストラップ、B=4000）===")
print(wr[["block", "PF_mean", "PF_sd", "PF_CV", "PF_CFaR05", "PF_ES05", "pi_mean", "pi_q05", "pi_CFaR05", "pi_ES05"]]
      .round(3).to_string(index=False))
print("参考: 実績3年の θ=1 正規化 PF の SD =", round(ann_n.std(ddof=1)), "／ 未正規化 PF の SD =",
      round(ann.loc[EST, "PF"].std(ddof=1)))
wr.to_csv(os.path.join(OUT, "r1_weather_risk.csv"), index=False)

# ---------------------------------------------------------------- (4) 水準リスクを重ねた年次分布
S = boot_store[7]                                    # 形状（θ=1）の年間PF
theta_emp = full["proxy_sys"].to_numpy()             # FY2016〜25 の水準代理（10年）
sig_lt = np.log(theta_emp).std(ddof=1)
N = 200000
Sdraw = rng.choice(S, N)
cases = {
    "A: θ=1固定（天候・形状のみ）": np.ones(N),
    "B: θ=FY2016〜25経験分布(代理)": rng.choice(theta_emp, N),
    "C: 対数正規(中央値1, σ=経験値)": np.exp(rng.normal(0, sig_lt, N)),
    "D: 対数正規(中央値1, σ=2×経験値)": np.exp(rng.normal(0, 2 * sig_lt, N)),
}
rows = []
for k, t in cases.items():
    pi = CAPTURE * t * Sdraw - W_CHG
    r = risk_stats(pi)
    r.update({f"P(π≥{n})": (pi >= v).mean() for n, v in C_REQ_NET.items()})
    r["P(π<0)"] = (pi < 0).mean()
    rows.append(dict(case=k, **r))
lr = pd.DataFrame(rows)
print(f"\n=== (4) 年次 π の分布（形状×水準、σ_logθ 経験値={sig_lt:.3f}）===")
print(lr.round(4).to_string(index=False))
lr.to_csv(os.path.join(OUT, "r1_level_risk.csv"), index=False)

# ---------------------------------------------------------------- (5) 20年 PV（年金換算）
T, R = 20, 0.06
disc = (1 + R) ** -np.arange(1, T + 1)
crf = R / (1 - (1 + R) ** -T)
M = 20000
rows = []
for phi in [0.0, 0.5, 0.9]:
    se = sig_lt * np.sqrt(1 - phi ** 2)
    lt = np.empty((M, T))
    prev = rng.normal(0, sig_lt, M)       # 定常分布から開始
    for t in range(T):
        prev = phi * prev + rng.normal(0, se, M)
        lt[:, t] = prev
    th_path = np.exp(lt)
    cf = CAPTURE * th_path * rng.choice(S, (M, T)) - W_CHG
    ann_eq = (cf * disc).sum(axis=1) * crf
    r = risk_stats(ann_eq)
    r.update({f"P(年金≥{n})": (ann_eq >= v).mean() for n, v in C_REQ_NET.items()})
    rows.append(dict(phi=phi, **r))
pv = pd.DataFrame(rows)
print("\n=== (5) 20年 PV の年金換算（割引率6%）===")
print(pv.round(4).to_string(index=False))
pv.to_csv(os.path.join(OUT, "r1_pv20_risk.csv"), index=False)

# ---------------------------------------------------------------- (6) 確実性等価・保険価値
print("\n=== (6) CAPM 型確実性等価 CE = E − λρσ（σ は20年年金換算のSD、φ別）と LTDA 9割還付の保険価値上限 ===")
rows = []
for _, r in pv.iterrows():
    for lam in [0.2, 0.4]:
        for rho in [0.3, 1.0]:
            rp = lam * rho * r["sd"]
            rows.append(dict(phi=r["phi"], lam=lam, rho=rho, E=r["mean"], sd=r["sd"], RP=rp,
                             CE=r["mean"] - rp, LTDA保険価値=0.9 * rp,
                             RP_vs_gap_標準=rp / (C_REQ_NET["標準"] - r["mean"])))
ce = pd.DataFrame(rows)
print(ce.round(3).to_string(index=False))
ce.to_csv(os.path.join(OUT, "r1_ce.csv"), index=False)

# ---------------------------------------------------------------- (7) 感応度: 年効果つき形状リスク＋capture率の不確実性
# 実績3年の θ=1 正規化 PF の SD（1,272, CV≈0.12）はブートストラップの SD（420〜560）より大きい
# → 年単位で共通の形状ショック（年効果）がある。形状の CV を 0.12 に引き上げ、capture を N(0.81, 0.033) とする
#   （0.033 は前回パイロット p2_capture_ci.csv の FY別区間 [0.74, 0.87] 幅/3.92 の目安）
cv_target = ann_n.std(ddof=1) / ann_n.mean()
sig_u = np.sqrt(max(cv_target ** 2 - (S.std() / S.mean()) ** 2, 0))
print(f"\n=== (7) 感応度: 形状の年効果 σ_u={sig_u:.3f}（目標CV={cv_target:.3f}）＋ capture~N(0.81,0.033) ===")
rows = []
for k, t in {"θ=1固定": np.ones(N), "θ対数正規(σ=経験値)": np.exp(rng.normal(0, sig_lt, N))}.items():
    sh = Sdraw * np.exp(rng.normal(-sig_u ** 2 / 2, sig_u, N))
    cc = np.clip(rng.normal(CAPTURE, 0.033, N), 0.6, 0.95)
    pi = cc * t * sh - W_CHG
    r = risk_stats(pi)
    r.update({f"P(π≥{n})": (pi >= v).mean() for n, v in C_REQ_NET.items()})
    rows.append(dict(case=k, **r))
s7 = pd.DataFrame(rows)
print(s7.round(4).to_string(index=False))
s7.to_csv(os.path.join(OUT, "r1_sensitivity_yeareffect.csv"), index=False)
