#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット4: Margrabe 型の分散恒等式で「風力の多い日に価値が増えない」理由を分解する（北海道）

(A) 分散恒等式 σ_X² = 16·[η²σ_dis² + σ_chg² − 2ηρσ_disσ_chg] の要因分解
    風力三分位「小」→「大」の σ_X の変化を、σ_dis・σ_chg・ρ の変化に Shapley 法で配分する。
    脚は (i) 事前固定窓（年度×季節の平均プロファイルの上位4h/下位4h）と (ii) 事後窓（上位4h/下位4h、PF）。
(B) 24次元ガウス・モンテカルロ（モーメント型オプション評価）
    季節×風力三分位ごとに、24時間価格の平均ベクトル m と共分散 Σ を推定し、N(m, Σ) から日を
    生成して下限0.01円で打ち切り、PF と固定窓粗利を計算する。実績 PF を2次モーメントだけで再現できるかを確認し、
    風力「小」→「大」の PF 変化を、平均（イントリンジック／デルタの経路）と共分散（ベガの経路）に分ける:
      ΔPF = [PF(m_大, Σ_小) − PF(m_小, Σ_小)] + [PF(m_大, Σ_大) − PF(m_大, Σ_小)]  （順序を入れ替えた平均も）
出力: このフォルダの p4_*.csv
"""
import itertools
import os

import numpy as np
import pandas as pd

OUT = os.path.dirname(os.path.abspath(__file__))
PANEL = "/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv"
ETA, H, FLOOR = 0.85, 4, 0.01
SEASON = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
          3: "不需要期", 4: "不需要期", 5: "不需要期", 6: "不需要期", 10: "不需要期", 11: "不需要期"}
rng = np.random.default_rng(20261020)
NSIM = 40000

hp = pd.read_csv(PANEL, parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
info = pd.DataFrame(index=P.index)
info["fy"] = info.index.year - (info.index.month < 4).astype(int)
info["season"] = info.index.month.map(SEASON)
info["wind"] = hp.groupby("day")["wind_pre"].sum().reindex(info.index) / 1000


def pf_arr(A):
    s = np.sort(A, axis=1)
    return np.maximum(0, H * (ETA * s[:, -H:].mean(1) - s[:, :H].mean(1)))


def fixed_arr(A, prof):
    o = np.argsort(prof)
    return H * (ETA * A[:, o[-H:]].mean(1) - A[:, o[:H]].mean(1))


def sx(sd, sc, rho):
    return H * np.sqrt(max(ETA**2 * sd**2 + sc**2 - 2 * ETA * rho * sd * sc, 0))


def shapley(f, a, b):
    """f(x1,x2,x3) の a→b 変化を3要因に Shapley 配分"""
    n = len(a)
    out = np.zeros(n)
    for perm in itertools.permutations(range(n)):
        x = list(a)
        prev = f(*x)
        for k in perm:
            x[k] = b[k]
            cur = f(*x)
            out[k] += cur - prev
            prev = cur
    return out / len(list(itertools.permutations(range(n))))


ident_rows, mc_rows = [], []
for pname, fys in {"FY2023-25": [2023, 2024, 2025], "FY2016-19": [2016, 2017, 2018, 2019]}.items():
    for s_name in ["夏", "冬", "不需要期"]:
        idx = (info["season"] == s_name) & info["fy"].isin(fys)
        inf = info[idx]
        A = P[idx].to_numpy()
        prof_all = A.mean(0)
        q = inf["wind"].quantile([1 / 3, 2 / 3])
        ter = np.select([inf["wind"] <= q.iloc[0], inf["wind"] >= q.iloc[1]], ["小", "大"], "中")
        o = np.argsort(prof_all)
        dis_w, chg_w = o[-H:], o[:H]
        mom = {}
        for t in ["小", "大"]:
            At = A[ter == t]
            srt = np.sort(At, axis=1)
            legs = {"固定窓": (At[:, dis_w].mean(1), At[:, chg_w].mean(1)),
                    "事後窓(PF)": (srt[:, -H:].mean(1), srt[:, :H].mean(1))}
            mom[t] = {}
            for lname, (ld, lc) in legs.items():
                mom[t][lname] = (ld.std(ddof=1), lc.std(ddof=1), np.corrcoef(ld, lc)[0, 1],
                                 (H * (ETA * ld - lc)).std(ddof=1))
        for lname in ["固定窓", "事後窓(PF)"]:
            a, b = mom["小"][lname], mom["大"][lname]
            contrib = shapley(sx, a[:3], b[:3])
            ident_rows.append({"期間": pname, "季節": s_name, "脚": lname,
                               "σ_dis小": a[0], "σ_dis大": b[0], "σ_chg小": a[1], "σ_chg大": b[1],
                               "ρ小": a[2], "ρ大": b[2], "σ_X小(恒等式)": sx(*a[:3]), "σ_X大(恒等式)": sx(*b[:3]),
                               "σ_X小(直接)": a[3], "σ_X大(直接)": b[3],
                               "Δσ_X": sx(*b[:3]) - sx(*a[:3]),
                               "寄与σ_dis": contrib[0], "寄与σ_chg": contrib[1], "寄与ρ": contrib[2],
                               "ρを小に固定したσ_X大": sx(b[0], b[1], a[2])})
        # (B) ガウス MC
        par = {}
        for t in ["小", "中", "大"]:
            At = A[ter == t]
            par[t] = (At.mean(0), np.cov(At, rowvar=False), At)
        for t in ["小", "中", "大"]:
            m, S, At = par[t]
            Z = rng.multivariate_normal(m, S, size=NSIM, method="eigh")
            mc_rows.append({"期間": pname, "季節": s_name, "風力三分位": t, "組合せ": f"m_{t},Σ_{t}",
                            "実績PF": pf_arr(At).mean(), "MC_PF": pf_arr(np.maximum(Z, FLOOR)).mean(),
                            "実績固定窓": fixed_arr(At, prof_all).mean(),
                            "MC固定窓": fixed_arr(np.maximum(Z, FLOOR), prof_all).mean()})
        for (mt, St) in [("大", "小"), ("小", "大")]:
            Z = rng.multivariate_normal(par[mt][0], par[St][1], size=NSIM, method="eigh")
            mc_rows.append({"期間": pname, "季節": s_name, "風力三分位": "反実仮想", "組合せ": f"m_{mt},Σ_{St}",
                            "実績PF": np.nan, "MC_PF": pf_arr(np.maximum(Z, FLOOR)).mean(),
                            "実績固定窓": np.nan,
                            "MC固定窓": fixed_arr(np.maximum(Z, FLOOR), prof_all).mean()})

ident = pd.DataFrame(ident_rows)
mc = pd.DataFrame(mc_rows)
ident.to_csv(os.path.join(OUT, "p4_margrabe_identity_shapley.csv"), index=False, encoding="utf-8-sig")
mc.to_csv(os.path.join(OUT, "p4_gauss_mc_channels.csv"), index=False, encoding="utf-8-sig")

# チャネル分解（平均＝デルタ経路、共分散＝ベガ経路）
ch_rows = []
for (pname, s_name), g in mc.groupby(["期間", "季節"]):
    v = dict(zip(g["組合せ"], g["MC_PF"]))
    lo, hi = v["m_小,Σ_小"], v["m_大,Σ_大"]
    mean1 = v["m_大,Σ_小"] - lo
    cov1 = hi - v["m_大,Σ_小"]
    cov2 = v["m_小,Σ_大"] - lo
    mean2 = hi - v["m_小,Σ_大"]
    ch_rows.append({"期間": pname, "季節": s_name, "MC_PF小": lo, "MC_PF大": hi, "ΔPF": hi - lo,
                    "平均の経路(デルタ)": (mean1 + mean2) / 2, "共分散の経路(ベガ)": (cov1 + cov2) / 2})
ch = pd.DataFrame(ch_rows)
ch.to_csv(os.path.join(OUT, "p4_channel_split.csv"), index=False, encoding="utf-8-sig")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print("=== (A) 分散恒等式と Shapley 配分（風力 小→大、σは円/kWh、σ_Xは円/kW-日）===")
print(ident.round(3).to_string(index=False))
print("\n=== (B) ガウス MC による PF 再現（円/kW-日）===")
print(mc.round(2).to_string(index=False))
print("\n=== (B) 風力 小→大 の PF 変化のチャネル分解（円/kW-日）===")
print(ch.round(2).to_string(index=False))
