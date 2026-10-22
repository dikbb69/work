#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット3: 実行可能戦略 a/b/c の粗利の差の Diebold-Mariano 検定（北海道 FY2023-25）

戦略の定義は analysis/16_strategy_decomposition.py と同一（コードを読み取り、ここに複製。リポジトリは実行しない）。
  PF: 完全予見、a: 前日の実現価格ランク、a2: 同曜日区分の直近日、c: 過去28日・同曜日区分の平均価格ランク、
  b: 予測残余需要ランク（D-2 まで）
損失差 d_t = π_X,t − π_Y,t（円/kW-日）。DM 統計量 = mean(d)/sqrt(LRV/T)、LRV は NW(Bartlett)。
Harvey, Leybourne and Newbold (1997) の小標本補正（h=1）と t(T−1) 分布も併記。
年間換算の差（円/kW-年）と capture率の差の週次ブロック・ブートストラップ区間も出す。
出力: out/p3_*.csv
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUT, PROC  # noqa: E402

ETA = 0.85
rng = np.random.default_rng(20261020)

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
D = hp.pivot(index="day", columns="hour", values="demand")
S = hp.pivot(index="day", columns="hour", values="solar")
days = P.index
all_days = D.index
wk = pd.Series(all_days.dayofweek >= 5, index=all_days)
wkP = pd.Series(P.index.dayofweek >= 5, index=P.index)


def margin(p, dis, chg):
    return (p[list(dis)].sum() * ETA - p[list(chg)].sum()) * 1000


def win(series):
    o = series.sort_values()
    return o.index[-4:], o.index[:4]


rows = []
start = days.get_indexer([pd.Timestamp("2023-03-01")], method="bfill")[0]
for i in range(start, len(days)):
    d = days[i]
    p = P.loc[d]
    rec = {"day": d, "pf": max(0.0, margin(p, *win(p)))}
    if i >= 1:
        rec["a"] = margin(p, *win(P.loc[days[i - 1]]))
    prev_same = [dd for dd in days[max(0, i - 8):i] if wkP[dd] == wkP[d]]
    if prev_same:
        rec["a2"] = margin(p, *win(P.loc[prev_same[-1]]))
    hist_p = [dd for dd in days[max(0, i - 29):i] if wkP[dd] == wkP[d]]
    if len(hist_p) >= 5:
        rec["c"] = margin(p, *win(P.loc[hist_p].mean()))
    jj = all_days.get_loc(d)
    if jj >= 30:
        hist = all_days[max(0, jj - 29):jj - 1]
        same = [h for h in hist if wk[h] == wk[d]]
        if len(same) >= 5:
            dem_f = D.loc[same].mean()
            sol_f = S.loc[all_days[jj - 8:jj - 1]].mean()
            rec["b"] = margin(p, *win(dem_f - sol_f))
    rows.append(rec)

bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
est = bt[bt["fy"].isin([2023, 2024, 2025])].dropna().reset_index(drop=True)
ann = est.groupby("fy")[["pf", "a", "a2", "c", "b"]].sum() / 1000
cap = ann.div(ann["pf"], axis=0) * 100
print("=== 年間価値（円/kW-年）と capture率（%）: 原稿 表7.1・7.2 との照合 ===")
print(ann.round(0).to_string())
print(cap.round(1).to_string())


def nw_lrv(x, L):
    x = x - x.mean()
    T = len(x)
    g0 = x @ x / T
    s = g0
    for j in range(1, L + 1):
        s += 2 * (1 - j / (L + 1)) * (x[j:] @ x[:-j] / T)
    return s


def dm(dser, L):
    x = np.asarray(dser, float)
    T = len(x)
    lrv = nw_lrv(x, L)
    stat = x.mean() / np.sqrt(lrv / T)
    # HLN 補正（h=1）: sqrt((T+1-2h+h(h-1)/T)/T) = sqrt((T-1)/T)
    stat_hln = stat * np.sqrt((T - 1) / T)
    return stat, 2 * (1 - stats.norm.cdf(abs(stat))), stat_hln, 2 * (1 - stats.t.cdf(abs(stat_hln), T - 1))


pairs = [("c", "b"), ("c", "a"), ("b", "a"), ("a2", "a"), ("c", "a2")]
out = []
for scope, g in [("FY2023-25", est)] + [(f"FY{fy}", gg) for fy, gg in est.groupby("fy")]:
    g = g.reset_index(drop=True)
    for x, y in pairs:
        dd = (g[x] - g[y]).to_numpy()
        ac1 = float(np.corrcoef(dd[1:], dd[:-1])[0, 1])
        for L in (0, 7, 14):
            s, p, sh, ph = dm(dd, L)
            out.append({"期間": scope, "比較": f"{x} − {y}", "lag": L, "日数": len(dd),
                        "平均差(円/kW-日)": dd.mean(), "年間換算(円/kW-年)": dd.mean() * 365 / 1000,
                        "capture差(pt)": (g[x].sum() - g[y].sum()) / g["pf"].sum() * 100,
                        "差のρ1": ac1, "DM": s, "p": p, "DM_HLN": sh, "p_HLN": ph})
res = pd.DataFrame(out)
res.to_csv(os.path.join(OUT, "p3_dm_tests.csv"), index=False, encoding="utf-8-sig")

# capture率の差（c − b）の週次ブロック・ブートストラップ（FY2023-25 プール）
nb = int(np.ceil(len(est) / 7))
blk = [est.iloc[k * 7:(k + 1) * 7] for k in range(nb)]
sums = np.array([[b_["pf"].sum(), b_["c"].sum(), b_["b"].sum(), b_["a"].sum()] for b_ in blk])
stat = []
for _ in range(5000):
    ix = rng.integers(0, nb, nb)
    s_ = sums[ix].sum(axis=0)
    stat.append([(s_[1] - s_[2]) / s_[0], (s_[1] - s_[3]) / s_[0], (s_[2] - s_[3]) / s_[0]])
stat = np.array(stat) * 100
ci = pd.DataFrame({"比較": ["c − b", "c − a", "b − a"],
                   "点推定(pt)": [(sums[:, 1].sum() - sums[:, 2].sum()) / sums[:, 0].sum() * 100,
                                  (sums[:, 1].sum() - sums[:, 3].sum()) / sums[:, 0].sum() * 100,
                                  (sums[:, 2].sum() - sums[:, 3].sum()) / sums[:, 0].sum() * 100],
                   "2.5%": np.percentile(stat, 2.5, axis=0), "97.5%": np.percentile(stat, 97.5, axis=0)})
ci.to_csv(os.path.join(OUT, "p3_capture_diff_ci.csv"), index=False, encoding="utf-8-sig")

pd.set_option("display.width", 250)
print("\n=== Diebold-Mariano 検定（lag 7 を主、0/14 は感度） ===")
show = res[res["lag"] == 7][["期間", "比較", "日数", "平均差(円/kW-日)", "年間換算(円/kW-年)", "capture差(pt)", "差のρ1", "DM", "p", "DM_HLN", "p_HLN"]]
print(show.round(3).to_string(index=False))
print("\nlag 感度（FY2023-25）:")
print(res[res["期間"] == "FY2023-25"][["比較", "lag", "DM", "p"]].round(3).to_string(index=False))
print("\n=== capture率の差の週次ブロック・ブートストラップ（FY2023-25、B=5000、pt） ===")
print(ci.round(2).to_string(index=False))

# ---------- 補遺: θ* の標本誤差（気象・需要の日次サンプリング）の目安 ----------
# 原稿 8.4: θ* = (c_req − κP_cap + w_chg) / (c · π_PF,model(0))、標準 3.55・楽観 3.17・保守 4.55。
# π(0)=4,943 = 0.81·π_PF,model − 1,752 → π_PF,model ≈ 8,265（表6.4 の λ=1 の 8,266 と整合）。
# ここでは θ*_b = θ*_0 × (PF̄_0·c_0)/(PF̄_b·c_b) として、実績の日次 PF と戦略 c を
# 7日・30日ブロックでリサンプルしたときの θ* の変動幅を見る（モデル PF の変動は実績 PF の相対変動で代理）。
pf0, c0 = est["pf"].mean(), est["c"].sum() / est["pf"].sum()
theta0 = {"標準": 3.55, "楽観": 3.17, "保守": 4.55}
rows_t = []
for blen in (7, 30):
    nb = int(np.ceil(len(est) / blen))
    bl = [est.iloc[k * blen:(k + 1) * blen] for k in range(nb)]
    sp = np.array([b_["pf"].sum() for b_ in bl]); sc = np.array([b_["c"].sum() for b_ in bl])
    ln = np.array([len(b_) for b_ in bl])
    ratio = []
    for _ in range(5000):
        ix = rng.integers(0, nb, nb)
        pfb = sp[ix].sum() / ln[ix].sum(); cb = sc[ix].sum() / sp[ix].sum()
        ratio.append((pf0 * c0) / (pfb * cb))
    ratio = np.array(ratio)
    pf_ann = pf0 * 365 / 1000
    for k, t0 in theta0.items():
        q = np.percentile(t0 * ratio, [2.5, 97.5])
        rows_t.append({"ブロック長": blen, "ケース": k, "θ*点推定": t0, "2.5%": q[0], "97.5%": q[1]})
    rows_t.append({"ブロック長": blen, "ケース": "年平均PF(円/kW-年)", "θ*点推定": pf_ann,
                   "2.5%": np.percentile(pf_ann / ratio * 1, 2.5), "97.5%": np.percentile(pf_ann / ratio, 97.5)})
tt = pd.DataFrame(rows_t)
tt.to_csv(os.path.join(OUT, "p3_theta_star_bootstrap.csv"), index=False, encoding="utf-8-sig")
print("\n=== 補遺: θ* と PF×c の標本誤差（ブロック・ブートストラップ、B=5000） ===")
print("注: 年平均PF の行は PF×capture の積の変動を PF 単位で表示")
print(tt.round(3).to_string(index=False))
