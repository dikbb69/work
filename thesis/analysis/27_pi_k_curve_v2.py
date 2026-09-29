#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フェーズC v2: 供給曲線 v2（26、年度別水準係数 θ）の上で π(K) と均衡容量 K* を再計算

23（v1）と同じ増分貪欲ディスパッチ（10万kW刻み・仕様A・FY2023-25 パス）。違いは価格過程が
  p = 0.01 ∨ { 0.01 + θ·[g(net;季節)+μ(季節,時刻) − 0.01] }
で、θ を価格水準シナリオ（FY2023-25 平均=1 ／ FY2026 上期 ／ FY2022 燃料危機）として振る点。
併せて (i) 参入に必要な水準に達する損益分岐の θ*（K=0）、(ii) 裾圧縮の補正（実績/モデルの PF 比）
を掛けた上限ケースを出す。
出力: figures/hokkaido/pi_k_curve_v2.png・data/processed/pi_k_curve_v2.csv・標準出力の判定表
"""
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = "Noto Sans CJK JP"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
PROC = os.path.join(ROOT, "data", "processed")

ns = {"__file__": os.path.join(HERE, "26_price_process_v2.py"), "__name__": "pp_v2"}
exec(open(os.path.join(HERE, "26_price_process_v2.py"), encoding="utf-8").read(), ns)
est = ns["est"].copy()
samp = ns["samp"].copy()
predict_A = ns["predict_A"]
THETA = ns["THETA"]
metrics = ns["metrics"]

ETA = 0.85
CAPTURE = 0.81
WHEEL_YEN_KWH = 1.2
CHARGE_KWH = 4 * 365
TOMARI = 912_000 * 0.9 / 1000
K_WIND_NOW = est["wind_kw"].mean() / 1e4

# 裾圧縮の補正係数: FY2023-25 の実績 PF ÷ v2 モデル PF（同一パス）
samp["p_v2"] = predict_A(samp, theta=samp["fy"].map(THETA).to_numpy())
m_act = metrics(samp[samp["fy"].isin([2023, 2024, 2025])], "p_hokkaido")["PF価値(円/kW-年)"]
m_mod = metrics(samp[samp["fy"].isin([2023, 2024, 2025])], "p_v2")["PF価値(円/kW-年)"]
TAIL = float(m_act.sum() / m_mod.sum())
print(f"裾補正係数（実績PF/モデルPF, FY2023-25）= {TAIL:.3f}")

est = est.sort_values("ts").reset_index(drop=True)
est["date"] = est["ts"].dt.normalize()

SCEN = {
    "現状（FY2023-25水準 θ=1）": {"theta": 1.0, "dnuc": 0.0},
    f"FY2026上期水準（θ={THETA[2026]:.2f}）": {"theta": THETA[2026], "dnuc": 0.0},
    f"FY2022水準（θ={THETA[2022]:.2f}）": {"theta": THETA[2022], "dnuc": 0.0},
    f"FY2026上期水準＋泊3号再稼働": {"theta": THETA[2026], "dnuc": TOMARI},
}
K_GRID = [0, 10, 25, 50, 100, 150, 200, 300]
SLICE_MANKW = 10

NEED = {"標準（容量1.25万・c_req3.45万）": 34500 - 12500,
        "楽観（容量1.25万・c_req3.2万）": 32000 - 12500,
        "保守（容量0.83万・c_req3.7万）": 37000 - 8300}


def marginal_pf(P1):
    srt = np.sort(P1, axis=1)
    return np.maximum(0.0, (srt[:, -4:].sum(axis=1) * ETA - srt[:, :4].sum(axis=1)) * 1000)


rows = []
for scen_name, sp in SCEN.items():
    th = sp["theta"]
    base = est.copy()
    base["net0"] = base["net"] - sp["dnuc"]
    piv_net = base.pivot_table(index="date", columns="hour", values="net0").dropna()
    full = piv_net.index
    tmp = base.loc[base["date"].isin(full)].sort_values("ts").copy()
    n_days = len(full)
    fy = full.year - (full.month < 4).astype(int)
    rowsel = np.arange(n_days)[:, None]
    adj = piv_net.to_numpy().copy()
    done_k = 0
    for K in K_GRID:
        while done_k < K:
            slice_mw = SLICE_MANKW * 10.0
            p_now = predict_A(tmp.assign(net=adj.reshape(-1)), net_col="net", theta=th).reshape(n_days, 24)
            order = np.argsort(p_now, axis=1)
            chg, dis = order[:, :4], order[:, -4:]
            margin = (np.take_along_axis(p_now, dis, 1).sum(1) * ETA - np.take_along_axis(p_now, chg, 1).sum(1))
            act = margin > 0
            adj[rowsel[act], chg[act]] += slice_mw
            adj[rowsel[act], dis[act]] -= slice_mw * ETA
            done_k += SLICE_MANKW
        p_fin = predict_A(tmp.assign(net=adj.reshape(-1)), net_col="net", theta=th).reshape(n_days, 24)
        pi_pf = pd.Series(marginal_pf(p_fin), index=full).groupby(fy).sum().mean() / 1000
        pi_feas = pi_pf * CAPTURE - CHARGE_KWH * WHEEL_YEN_KWH
        pi_feas_tail = pi_pf * TAIL * CAPTURE - CHARGE_KWH * WHEEL_YEN_KWH
        rows.append({"シナリオ": scen_name, "θ": round(th, 3), "K(万kW)": K,
                     "π_PF(円/kW-年)": round(pi_pf, 0), "π_実現可能(円/kW-年)": round(pi_feas, 0),
                     "π_実現可能_裾補正(円/kW-年)": round(pi_feas_tail, 0)})
        print(rows[-1])

df = pd.DataFrame(rows)
df.to_csv(os.path.join(PROC, "pi_k_curve_v2.csv"), index=False)

# ---------- 判定 ----------
pf0 = df[(df["シナリオ"].str.startswith("現状")) & (df["K(万kW)"] == 0)]["π_PF(円/kW-年)"].iloc[0]
print(f"\n=== 参入条件と損益分岐の水準係数 θ*（K=0、π_PF(0;θ)≈θ×{pf0:,.0f}） ===")
be = []
for case, need in NEED.items():
    th_star = (need + CHARGE_KWH * WHEEL_YEN_KWH) / CAPTURE / pf0
    th_star_tail = th_star / TAIL
    be.append({"ケース": case, "必要水準(円/kW-年)": need, "θ*": round(th_star, 2), "θ*_裾補正": round(th_star_tail, 2),
               "対FY2026上期(倍)": round(th_star / THETA[2026], 2), "対FY2026上期_裾補正(倍)": round(th_star_tail / THETA[2026], 2)})
be = pd.DataFrame(be)
print(be.to_string(index=False))
be.to_csv(os.path.join(PROC, "pi_k_breakeven_theta.csv"), index=False)

print("\n=== 各シナリオの K*（π_実現可能(K) ≥ 必要水準 となる最大 K、グリッド補間） ===")
for scen_name in SCEN:
    d = df[df["シナリオ"] == scen_name].sort_values("K(万kW)")
    for col in ("π_実現可能(円/kW-年)", "π_実現可能_裾補正(円/kW-年)"):
        out = []
        for case, need in NEED.items():
            y = d[col].to_numpy(); x = d["K(万kW)"].to_numpy()
            if y[0] < need:
                out.append(f"{case.split('（')[0]}: K*=0（不足 {need - y[0]:,.0f}）")
            else:
                idx = np.where(y >= need)[0].max()
                kstar = x[idx] if idx == len(x) - 1 else np.interp(need, [y[idx + 1], y[idx]], [x[idx + 1], x[idx]])
                out.append(f"{case.split('（')[0]}: K*≈{kstar:.0f}万kW")
        print(f"  {scen_name} [{col.split('(')[0]}] → " + " / ".join(out))

# ---------- 図 ----------
C = ["#0079C2", "#D95B20", "#176871", "#7B3F9E"]
fig, ax = plt.subplots(figsize=(10.2, 5.8))
for (scen_name, _), c in zip(SCEN.items(), C):
    d = df[df["シナリオ"] == scen_name]
    ax.plot(d["K(万kW)"], d["π_実現可能(円/kW-年)"], color=c, lw=2.3, marker="o", ms=5, label=scen_name)
    ax.plot(d["K(万kW)"], d["π_実現可能_裾補正(円/kW-年)"], color=c, lw=1.2, ls=":", marker=None)
for lab, v, ls in [("参入に必要な水準（標準: 2.20万円）", NEED["標準（容量1.25万・c_req3.45万）"], "--"),
                   ("同（楽観: 1.95万円）", NEED["楽観（容量1.25万・c_req3.2万）"], ":")]:
    ax.axhline(v, color="#999999", lw=1.2, ls=ls)
    ax.text(2, v + 300, lab, ha="left", fontsize=9, color="#666666")
ax.set_xlabel("蓄電池フリート容量 K（万kW、4h）", fontsize=11, color="#595959")
ax.set_ylabel("限界参入者の実現可能スポット収益 π(K)（円/kW-年）", fontsize=11, color="#595959")
ax.set_title("π(K)曲線の価格水準感応度（供給曲線v2）— FY2026上期・FY2022の水準でも純市場の K*=0",
             fontsize=12.5, fontweight="bold", pad=12)
ax.grid(axis="y", color="#DDDDDD", lw=0.6)
for sp_ in ["top", "right"]:
    ax.spines[sp_].set_visible(False)
ax.tick_params(colors="#595959")
ax.legend(fontsize=9.5, frameon=False, loc="center right")
fig.text(0.99, 0.005,
         f"実線=モデル値、点線=裾補正（×{TAIL:.2f}、FY2023-25の実績/モデルPF比）。仕様A・FY2023-25パス・capture0.81・充電従量1.2円/kWh控除・増分貪欲ディスパッチ（10万kW刻み）",
         ha="right", fontsize=7.5, color="#595959")
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "pi_k_curve_v2.png"), dpi=160, bbox_inches="tight")
print("saved pi_k_curve_v2.png")
