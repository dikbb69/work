#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""8.5 均衡面と 9.4 break-even フロンティア（供給曲線 v2 の上で）

構成:
  1. π(K; K_wind, 泊) 面: 風力導入量 0.5〜3× × フリート K 0〜200万kW × 泊なし/あり（θ=1、増分貪欲ディスパッチ）
  2. 容量市場価格の K 依存 P_cap(K): 2029年度向け需要曲線（上限15,112.5円／目標調達量・指標価格10,075円／ゼロ価格量）を
     ブロック需要シェア s で按分した折れ線。s=北海道H3シェア(529/16,208) と s=1（全国連系）の2境界。蓄電池の供給寄与は κ·K
  3. 参入必要収益 c_req(資本費, WACC) = 4h資本費×CRF(WACC,20年) + 運維・廃止0.53万 + 託送等固定0.69万（notes/20）
  4. break-even フロンティア: K=0 で参入が開く価格水準係数 θ*(資本費, 実効容量収入)、および θ・資本費・容量収入の格子上の K*
     （容量価格定数 vs ブロック内生の両方）
  5. 需給調整市場レントの上限バンド: 調達量 Q × ΔkW価格 p × 8,760h ÷ K の格子（主仕様はゼロレント）
出力: data/processed/{equilibrium_surface.csv, capacity_price_of_k.csv, breakeven_frontier.csv, kstar_grid.csv, eprx_rent_cap.csv}
      figures/hokkaido/{equilibrium_surface.png, breakeven_frontier.png}
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
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
PROC = os.path.join(ROOT, "data", "processed")
GRAY = "#595959"

ns = {"__file__": os.path.join(HERE, "26_price_process_v2.py"), "__name__": "pp_v2"}
exec(open(os.path.join(HERE, "26_price_process_v2.py"), encoding="utf-8").read(), ns)
est = ns["est"].copy()
predict_A = ns["predict_A"]
THETA = ns["THETA"]

ETA, CAPTURE, WHEEL_YEN_KWH, CHARGE_KWH = 0.85, 0.81, 1.2, 4 * 365
CHARGE_COST = CHARGE_KWH * WHEEL_YEN_KWH          # 1,752 円/kW-年
TOMARI = 912_000 * 0.9 / 1000
K_WIND_NOW = est["wind_kw"].mean() / 1e4
est = est.sort_values("ts").reset_index(drop=True)
est["date"] = est["ts"].dt.normalize()
K_GRID = [0, 10, 25, 50, 100, 150, 200]
SLICE = 10


def pi_curve(theta=1.0, dnuc=0.0, wind_mult=1.0):
    base = est.copy()
    dwind_kw = (wind_mult - 1.0) * K_WIND_NOW * 1e4
    base["net0"] = base["net"] - dwind_kw * base["cf_wind"] / 1000 - dnuc
    piv = base.pivot_table(index="date", columns="hour", values="net0").dropna()
    full = piv.index
    tmp = base.loc[base["date"].isin(full)].sort_values("ts").copy()
    n = len(full)
    fy = full.year - (full.month < 4).astype(int)
    rowsel = np.arange(n)[:, None]
    adj = piv.to_numpy().copy()
    done, out = 0, []
    for K in K_GRID:
        while done < K:
            p_now = predict_A(tmp.assign(net=adj.reshape(-1)), net_col="net", theta=theta).reshape(n, 24)
            order = np.argsort(p_now, axis=1)
            chg, dis = order[:, :4], order[:, -4:]
            margin = np.take_along_axis(p_now, dis, 1).sum(1) * ETA - np.take_along_axis(p_now, chg, 1).sum(1)
            act = margin > 0
            adj[rowsel[act], chg[act]] += SLICE * 10.0
            adj[rowsel[act], dis[act]] -= SLICE * 10.0 * ETA
            done += SLICE
        p_fin = predict_A(tmp.assign(net=adj.reshape(-1)), net_col="net", theta=theta).reshape(n, 24)
        srt = np.sort(p_fin, axis=1)
        m = np.maximum(0.0, (srt[:, -4:].sum(1) * ETA - srt[:, :4].sum(1)) * 1000)
        pi_pf = pd.Series(m, index=full).groupby(fy).sum().mean() / 1000
        out.append((K, pi_pf, pi_pf * CAPTURE - CHARGE_COST))
    return out


# ---------- 1. π(K; K_wind, 泊) 面 ----------
rows = []
for tomari, tlab in ((0.0, "なし"), (TOMARI, "あり")):
    for wm in (0.5, 1.0, 1.5, 2.0, 3.0):
        for K, pf, feas in pi_curve(1.0, tomari, wm):
            rows.append({"泊": tlab, "K_wind倍率": wm, "K_wind(万kW)": round(K_WIND_NOW * wm), "K(万kW)": K,
                         "π_PF(円/kW-年)": round(pf), "π_実現可能(円/kW-年)": round(feas)})
        print(f"泊{tlab} K_wind×{wm}: " + ", ".join(f"K{r['K(万kW)']}={r['π_実現可能(円/kW-年)']}" for r in rows[-len(K_GRID):]))
surf = pd.DataFrame(rows)
surf.to_csv(os.path.join(PROC, "equilibrium_surface.csv"), index=False)
base_curve = surf[(surf["泊"] == "なし") & (surf["K_wind倍率"] == 1.0)].set_index("K(万kW)")["π_PF(円/kW-年)"]
PI0 = float(base_curve.loc[0])

# ---------- 2. 容量市場価格の K 依存 ----------
P0, P_CEIL, NET_CONE = 14_972.0, 15_112.5, 10_075.0
Q_CAP, Q_TGT, Q_ZERO = 188_813_656, 189_966_340, 195_652_080     # kW、2029年度向け全国
KAPPA = 0.836
SHARE = {"北海道ブロック按分": 529 / 16_208, "全国連系": 1.0}


def p_cap_of_k(K_mankw, share):
    dq = KAPPA * K_mankw * 1e4
    up = (P_CEIL - NET_CONE) / ((Q_TGT - Q_CAP) * share)
    lo = NET_CONE / ((Q_ZERO - Q_TGT) * share)
    room = (P0 - NET_CONE) / up
    if dq <= room:
        return P0 - up * dq
    return max(0.0, NET_CONE - lo * (dq - room))


cap_rows = []
for K in [0, 5, 10, 25, 50, 100, 150, 200, 300]:
    r = {"K(万kW)": K}
    for lab, s in SHARE.items():
        r[f"P_cap {lab}(円/kW)"] = round(p_cap_of_k(K, s))
        r[f"κP_cap {lab}(円/kW-年)"] = round(KAPPA * p_cap_of_k(K, s))
    cap_rows.append(r)
capdf = pd.DataFrame(cap_rows)
capdf.to_csv(os.path.join(PROC, "capacity_price_of_k.csv"), index=False)
print("\n=== P_cap(K) ===")
print(capdf.to_string(index=False))
for lab, s in SHARE.items():
    up = (P_CEIL - NET_CONE) / ((Q_TGT - Q_CAP) * s); lo = NET_CONE / ((Q_ZERO - Q_TGT) * s)
    k_cone = (P0 - NET_CONE) / up / KAPPA / 1e4
    k_zero = k_cone + NET_CONE / lo / KAPPA / 1e4
    print(f"  {lab}: 指標価格到達 K≈{k_cone:.1f}万kW、価格ゼロ K≈{k_zero:.0f}万kW（上側勾配 {up*1e4*KAPPA:,.0f} 円/kW per 万kW）")


# ---------- 3. c_req ----------
def crf(w, n=20):
    return w * (1 + w) ** n / ((1 + w) ** n - 1)


def c_req(capex_man_kwh, wacc, om_man=0.53, wheel_fixed_man=0.69):
    return (4 * capex_man_kwh * crf(wacc) + om_man + wheel_fixed_man) * 1e4   # 円/kW-年


print("\nc_req 検算: 6.8万/kWh・6% →", round(c_req(6.8, 0.06)), "円/kW-年（notes/20: AFC2.9万+0.69万）")

# ---------- 4. break-even フロンティア ----------
CAPEX = [2.3, 3.0, 4.0, 5.0, 6.0, 6.8]
CAPINC = {"0（容量収入なし）": 0.0, "0.83万（発動指令）": 8_300.0, "1.25万（現行・安定電源）": 12_500.0,
          "1.75万（2030年度向けNet CONE 20,911円）": 20_911 * KAPPA, "2.5万（上限近傍3万円）": 30_000 * KAPPA}
fr_rows = []
for wacc in (0.05, 0.06, 0.08):
    for cx in CAPEX:
        for clab, ci in CAPINC.items():
            th = (c_req(cx, wacc) - ci + CHARGE_COST) / (CAPTURE * PI0)
            fr_rows.append({"WACC": wacc, "資本費(万円/kWh)": cx, "実効容量収入": clab, "κP_cap(円/kW-年)": round(ci),
                            "c_req(円/kW-年)": round(c_req(cx, wacc)), "θ*": round(th, 2)})
fr = pd.DataFrame(fr_rows)
fr.to_csv(os.path.join(PROC, "breakeven_frontier.csv"), index=False)
print("\n=== θ*（WACC6%）: 行=資本費, 列=実効容量収入 ===")
print(fr[fr["WACC"] == 0.06].pivot(index="資本費(万円/kWh)", columns="実効容量収入", values="θ*").to_string())

# K* の格子（容量価格 定数 vs ブロック内生）
Kfine = np.arange(0, 201, 1)
pf_fine = np.interp(Kfine, base_curve.index.to_numpy(), base_curve.to_numpy())


def k_star(theta, cx, ci0, wacc=0.06, endog=None):
    """endog=None: κP_cap 定数 ci0。endog=share: P_cap(K) をブロック曲線で内生化（P0 を ci0/κ に置く）"""
    need = c_req(cx, wacc)
    best = 0.0
    for K, pf in zip(Kfine, pf_fine):
        ci = ci0 if endog is None else KAPPA * max(0.0, p_cap_of_k(K, endog) - P0 + ci0 / KAPPA)
        if theta * pf * CAPTURE - CHARGE_COST + ci - need >= 0:
            best = K
        else:
            break
    return best


ks_rows = []
for th_lab, th in (("θ=1（FY2023-25）", 1.0), ("θ=1.57（FY2026上期）", THETA[2026]), ("θ=1.72（FY2022）", THETA[2022]), ("θ=2.5", 2.5), ("θ=3.0", 3.0)):
    for cx in (2.3, 4.0, 6.8):
        for clab, ci in (("1.25万", 12_500.0), ("1.75万", 20_911 * KAPPA), ("2.5万", 30_000 * KAPPA)):
            ks_rows.append({"θ": th_lab, "資本費(万円/kWh)": cx, "κP_cap": clab,
                            "K*_容量定数(万kW)": k_star(th, cx, ci),
                            "K*_北海道按分(万kW)": k_star(th, cx, ci, endog=SHARE["北海道ブロック按分"]),
                            "K*_全国連系(万kW)": k_star(th, cx, ci, endog=SHARE["全国連系"])})
ks = pd.DataFrame(ks_rows)
ks.to_csv(os.path.join(PROC, "kstar_grid.csv"), index=False)
print("\n=== K* 格子（WACC6%） ===")
print(ks.to_string(index=False))

# ---------- 5. EPRX レント上限 ----------
ep_rows = []
for Q in (10, 30, 50):
    for pr in (5.0, 15.0):
        r = {"調達量Q(万kW)": Q, "ΔkW価格(円/ΔkW·h)": pr}
        for K in (25, 50, 100, 200):
            r[f"K={K}万kW"] = round(Q * 1e4 * pr * 8760 / (K * 1e4))
        ep_rows.append(r)
ep = pd.DataFrame(ep_rows)
ep.to_csv(os.path.join(PROC, "eprx_rent_cap.csv"), index=False)
print("\n=== EPRX レント上限（円/kW-年）= Q×p×8,760h ÷ K ===")
print(ep.to_string(index=False))

# ---------- 図 ----------
C = {0.5: "#9DC3E6", 1.0: "#0079C2", 1.5: "#176871", 2.0: "#D95B20", 3.0: "#7B3F9E"}
fig, ax = plt.subplots(figsize=(10.2, 5.8))
for wm, c in C.items():
    for tlab, ls in (("なし", "-"), ("あり", "--")):
        d = surf[(surf["泊"] == tlab) & (surf["K_wind倍率"] == wm)]
        ax.plot(d["K(万kW)"], d["π_実現可能(円/kW-年)"], color=c, lw=2.0 if tlab == "なし" else 1.3, ls=ls,
                marker="o" if tlab == "なし" else None, ms=4,
                label=f"風力×{wm}（{round(K_WIND_NOW*wm)}万kW）" if tlab == "なし" else None)
ax.axhline(22_000, color="#999999", lw=1.2, ls="--"); ax.text(2, 22_300, "参入に必要な水準（標準: 2.20万円）", fontsize=9, color="#666666")
ax.axhline(19_500, color="#999999", lw=1.2, ls=":"); ax.text(2, 19_800, "同（楽観: 1.95万円）", fontsize=9, color="#666666")
ax.set_xlabel("蓄電池フリート容量 K（万kW、4h）", fontsize=11, color=GRAY)
ax.set_ylabel("限界参入者の実現可能スポット収益 π(K)（円/kW-年）", fontsize=11, color=GRAY)
ax.set_title("均衡面 π(K; K_wind) — 風力3倍でも純市場の K*=0（実線: 泊なし、破線: 泊3号再稼働）", fontsize=12.5, fontweight="bold", pad=12)
ax.grid(axis="y", color="#DDDDDD", lw=0.6)
for sp_ in ("top", "right"):
    ax.spines[sp_].set_visible(False)
ax.tick_params(colors=GRAY)
ax.legend(fontsize=9.5, frameon=False, loc="center right")
fig.text(0.99, 0.005, "供給曲線v2（θ=1）・FY2023-25パス・capture0.81・充電従量1.2円/kWh控除・増分貪欲ディスパッチ（10万kW刻み）", ha="right", fontsize=7.5, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "equilibrium_surface.png"), dpi=160, bbox_inches="tight")

# フロンティア: θ* の等高線（横軸 資本費、縦軸 実効容量収入、WACC6%）
cx_axis = np.linspace(2.0, 7.0, 51)
ci_axis = np.linspace(0, 26_000, 53)
CX, CI = np.meshgrid(cx_axis, ci_axis)
TH = (np.vectorize(lambda cx: c_req(cx, 0.06))(CX) - CI + CHARGE_COST) / (CAPTURE * PI0)
fig, ax = plt.subplots(figsize=(9.6, 6.0))
cf = ax.contourf(CX, CI / 1e4, TH, levels=[0, 1, 1.57, 1.72, 2, 2.5, 3, 4, 6], colors=["#C7E4F5", "#9DC3E6", "#6FA8DC", "#4A90C8", "#2F6FA8", "#1F4E79", "#143452", "#0B1F33"], alpha=0.9)
cs = ax.contour(CX, CI / 1e4, TH, levels=[1.0, 1.57, 1.72, 2.5], colors=["#D95B20", "#D95B20", "#D95B20", "#FFFFFF"], linewidths=[2.2, 1.6, 1.6, 1.2], linestyles=["-", "--", ":", "-"])
ax.clabel(cs, fmt={1.0: "θ*=1.0（FY2023-25水準で参入）", 1.57: "θ*=1.57（FY2026上期）", 1.72: "θ*=1.72（FY2022）", 2.5: "θ*=2.5"}, fontsize=8.5, inline=True)
cb = fig.colorbar(cf, ax=ax, pad=0.02); cb.set_label("参入に必要な価格水準係数 θ*（FY2023-25=1）", fontsize=10, color=GRAY)
ax.scatter([6.8], [1.25], color="#D95B20", s=70, zorder=5); ax.text(6.75, 1.4, "現状（6.8万円/kWh・1.25万円）", ha="right", fontsize=9, color="#D95B20")
ax.scatter([2.3], [1.25], color="#176871", s=60, zorder=5); ax.text(2.35, 1.4, "揚水並み2.3万円/kWh", fontsize=9, color="#176871")
ax.set_xlabel("蓄電池の資本費（万円/kWh、4h）", fontsize=11, color=GRAY)
ax.set_ylabel("実効容量収入 κ·P_cap（万円/kW-年）", fontsize=11, color=GRAY)
ax.set_title("break-even フロンティア — 純市場参入（K*>0）に必要な価格水準係数 θ*（WACC 6%）", fontsize=12.5, fontweight="bold", pad=12)
ax.tick_params(colors=GRAY)
fig.text(0.99, 0.005, "θ* = (c_req − κP_cap + 充電従量負担) ÷ (capture 0.81 × π_PF(0) 8,265円)。c_req = 4h資本費×CRF(6%,20年)+運維0.53万+託送固定0.69万", ha="right", fontsize=7.5, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "breakeven_frontier.png"), dpi=160, bbox_inches="tight")
print("saved figures")
