#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下限価格（床）シナリオ: 負価格の導入が蓄電池の裁定価値・均衡容量・再エネ収入に与える影響

  価格過程（年度別水準係数付き、26）の床 0.01円/kWh を、床に達する時間だけ −c 円/kWh に置く段差モデル
  （負の領域の供給曲線は 0.01円で打ち切られたデータから識別できないため、深さ c は外生）。
  1. π(K; c) を増分貪欲ディスパッチで再計算（θ=1 と θ=FY2026上期）
  2. 損益分岐の水準係数 θ*(資本費, 容量収入, c)
  3. 再エネ側の収入変化（床時間の VRE 出力 × (0.01+c)）＝蓄電池・需要側への移転額
  4. 出力制御の影の価格: 抑制時間（風力・太陽光）に負価格が成立した場合に市場に現れる価値と、
     蓄電池（フリート K）が回収できる分
出力: data/processed/negative_price_scenarios.csv, negative_price_transfer.csv, negative_price_breakeven.csv
      figures/hokkaido/negative_price_pi_k.png
"""
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY = "#595959"

ns = {"__file__": os.path.join(HERE, "26_price_process_v2.py"), "__name__": "pp_v2"}
exec(open(os.path.join(HERE, "26_price_process_v2.py"), encoding="utf-8").read(), ns)
est = ns["est"].sort_values("ts").reset_index(drop=True).copy()
base_price = ns["base_price"]; G = ns["G"]; ADJ = ns["ADJ"]; THETA = ns["THETA"]
FLOOR = 0.01
ETA, CAPTURE, CHARGE_COST = 0.85, 0.81, 4 * 365 * 1.2
K_GRID = [0, 10, 25, 50, 100, 150, 200]
SLICE = 10
C_LIST = [0.0, 5.0, 10.0]           # 負価格の深さ（0 = 下限を 0 円に、5・10 = −5・−10円）


def predict(df, net_col="net", theta=1.0, c=None):
    base = base_price(df, G, ADJ, net_col)
    p = np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)
    if c is not None:
        p = np.where(base <= FLOOR + 1e-9, -c, p)     # 床に達する時間だけ −c
    return p


TOMARI = 912_000 * 0.9 / 1000
K_WIND_NOW = est["wind_kw"].mean() / 1e4


def pi_curve(theta, c, dnuc=0.0, wind_mult=1.0):
    base = est.copy()
    base["net"] = base["net"] - (wind_mult - 1.0) * K_WIND_NOW * 1e4 * base["cf_wind"] / 1000 - dnuc
    piv = base.pivot_table(index=base["ts"].dt.normalize(), columns="hour", values="net").dropna()
    full = piv.index
    tmp = base.loc[base["ts"].dt.normalize().isin(full)].sort_values("ts").copy()
    n = len(full); fy = full.year - (full.month < 4).astype(int)
    rowsel = np.arange(n)[:, None]; adj = piv.to_numpy().copy(); done = 0; out = []
    for K in K_GRID:
        while done < K:
            p_now = predict(tmp.assign(net=adj.reshape(-1)), theta=theta, c=c).reshape(n, 24)
            order = np.argsort(p_now, axis=1); chg, dis = order[:, :4], order[:, -4:]
            margin = np.take_along_axis(p_now, dis, 1).sum(1) * ETA - np.take_along_axis(p_now, chg, 1).sum(1)
            act = margin > 0
            adj[rowsel[act], chg[act]] += SLICE * 10.0; adj[rowsel[act], dis[act]] -= SLICE * 10.0 * ETA
            done += SLICE
        p_fin = predict(tmp.assign(net=adj.reshape(-1)), theta=theta, c=c).reshape(n, 24)
        srt = np.sort(p_fin, axis=1)
        m = np.maximum(0.0, (srt[:, -4:].sum(1) * ETA - srt[:, :4].sum(1)) * 1000)
        pi_pf = pd.Series(m, index=full).groupby(fy).sum().mean() / 1000
        neg_h = int((p_fin < 0).sum()) / 3
        out.append((K, pi_pf, pi_pf * CAPTURE - CHARGE_COST, neg_h))
    return out


rows = []
SCEN = [("θ=1（FY2023-25水準）", 1.0, 0.0, 1.0), (f"θ={THETA[2026]:.2f}（FY2026上期水準）", THETA[2026], 0.0, 1.0),
        ("θ=1・泊3号再稼働", 1.0, TOMARI, 1.0), ("θ=1・泊＋風力2倍", 1.0, TOMARI, 2.0)]
for th_lab, th, dnuc, wm in SCEN:
    for c in [None] + C_LIST:
        lab = "現行（下限0.01円）" if c is None else f"下限 −{c:.0f}円" if c > 0 else "下限 0円"
        for K, pf, feas, negh in pi_curve(th, c, dnuc, wm):
            rows.append({"水準": th_lab, "下限": lab, "c": 0.01 if c is None else -c, "K(万kW)": K,
                         "π_PF(円/kW-年)": round(pf), "π_実現可能(円/kW-年)": round(feas), "負価格時間(h/年)": round(negh)})
        print(th_lab, lab, [(r["K(万kW)"], r["π_実現可能(円/kW-年)"]) for r in rows[-len(K_GRID):]], "負価格h/年:", rows[-len(K_GRID)]["負価格時間(h/年)"])
df = pd.DataFrame(rows); df.to_csv(os.path.join(PROC, "negative_price_scenarios.csv"), index=False)

# ---- 損益分岐 θ*(資本費, 容量収入, c) ----
def crf(w, n=20): return w * (1 + w) ** n / ((1 + w) ** n - 1)
def c_req(cx, w=0.06): return (4 * cx * crf(w) + 0.53 + 0.69) * 1e4
pf0 = {r["下限"]: r["π_PF(円/kW-年)"] for _, r in df[(df["水準"].str.startswith("θ=1（")) & (df["K(万kW)"] == 0)].iterrows()}
be = []
for lab, pf in pf0.items():
    for cx in (2.3, 4.0, 6.8):
        for cl, ci in (("1.25万", 12500.0), ("1.75万", 20911 * 0.836), ("2.5万", 30000 * 0.836)):
            be.append({"下限": lab, "π_PF(0)": pf, "資本費(万円/kWh)": cx, "κP_cap": cl, "θ*": round((c_req(cx) - ci + CHARGE_COST) / (CAPTURE * pf), 2)})
be = pd.DataFrame(be); be.to_csv(os.path.join(PROC, "negative_price_breakeven.csv"), index=False)
print("\n=== θ*（資本費6.8万, κP1.25万） ===")
print(be[(be["資本費(万円/kWh)"] == 6.8) & (be["κP_cap"] == "1.25万")].to_string(index=False))
print(be[(be["資本費(万円/kWh)"] == 2.3) & (be["κP_cap"] == "1.75万")].to_string(index=False))

# ---- 再エネ側の収入変化と出力制御の影の価格（実績パス、FY2023-26） ----
p = ns["p"].copy()
p = p.dropna(subset=["p_hokkaido"])
p["vre"] = p["solar_pre"] + p["wind_pre"]
p["curt"] = p["solar_curt"].fillna(0) + p["wind_curt"].fillna(0)
p["floor"] = p["p_hokkaido"] <= 0.011
tr = []
for fy, g in p[p["fy"].between(2023, 2026)].groupby("fy"):
    fl = g[g["floor"]]
    r = {"FY": fy, "床時間(h)": len(fl), "床時間のVRE出力(GWh)": round(fl["vre"].sum() / 1000, 1),
         "抑制電力量(GWh)": round(g["curt"].sum() / 1000, 1), "抑制時間(h)": int((g["curt"] > 0).sum()),
         "抑制が床と一致(h)": int(((g["curt"] > 0) & g["floor"]).sum())}
    for c in C_LIST[1:]:
        r[f"再エネ収入減 c={c:.0f}(億円)"] = round(fl["vre"].sum() * (0.01 + c) / 1e5, 1)      # MWh×円/kWh=千円 → 億円は /1e5
        r[f"抑制の影の価格価値 c={c:.0f}(億円)"] = round(g["curt"].sum() * c / 1e5, 2)
    tr.append(r); print(r)
tr = pd.DataFrame(tr); tr.to_csv(os.path.join(PROC, "negative_price_transfer.csv"), index=False)

# ---- 図 ----
fig, ax = plt.subplots(figsize=(10, 5.6))
cols = {"現行（下限0.01円）": "#0079C2", "下限 0円": "#9DC3E6", "下限 −5円": "#D95B20", "下限 −10円": "#7B3F9E"}
for lab, c in cols.items():
    for th_lab, ls in ((SCEN[0][0], "-"), (SCEN[2][0], "--")):
        d = df[(df["下限"] == lab) & (df["水準"] == th_lab)]
        ax.plot(d["K(万kW)"], d["π_実現可能(円/kW-年)"], color=c, ls=ls, lw=2.0 if ls == "-" else 1.3, marker="o" if ls == "-" else None, ms=4, label=lab if ls == "-" else None)
ax.axhline(22000, color="#999999", lw=1.2, ls="--"); ax.text(2, 22300, "参入に必要な水準（標準: 2.20万円）", fontsize=9, color="#666666")
ax.axhline(19500, color="#999999", lw=1.2, ls=":"); ax.text(2, 19800, "同（楽観: 1.95万円）", fontsize=9, color="#666666")
ax.set_xlabel("蓄電池フリート容量 K（万kW、4h）", color=GRAY); ax.set_ylabel("限界参入者の実現可能スポット収益 π(K)（円/kW-年）", color=GRAY)
ax.set_title("下限価格シナリオ別の π(K)（実線: 現状、破線: 泊3号再稼働）", fontsize=12.5, fontweight="bold", pad=12)
ax.grid(axis="y", color="#DDDDDD", lw=0.6); ax.tick_params(colors=GRAY)
for sp_ in ("top", "right"): ax.spines[sp_].set_visible(False)
ax.legend(fontsize=9.5, frameon=False, loc="center right")
fig.text(0.99, 0.005, "床に達する時間だけ −c 円/kWh に置く段差モデル。負領域の供給曲線は識別できないため c は外生。FY2023-25パス・capture0.81・充電従量1.2円/kWh控除", ha="right", fontsize=7.5, color=GRAY)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "negative_price_pi_k.png"), dpi=160, bbox_inches="tight")
print("saved")
