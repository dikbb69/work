#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""フェーズC v1: 蓄電池フリートの内生化 → π(K)曲線 → 均衡容量K*の初回判定

手法:
  価格過程v1（13）の仕様A（決定論: p = g(net;季節)+μ(季節,時刻)）の上で、
  規模Kの蓄電池フリートを10万kW刻みの増分で逐次投入する（増分貪欲ディスパッチ）。
  各増分はその時点の価格で「最安4hに充電・最高4hに放電」（正マージンの日のみ）し、
  netと価格を更新 → 競争均衡（各参入者が残されたスプレッドを順に取る）の近似。
  π_spot(K) ＝ フリートK投入後の価格での限界参入者（価格テイカー・完全予見4h）の年間裁定粗利。

  実現可能収益 = π_spot(K) × capture率0.81（気候値戦略c） − 充電従量負担
  参入条件: π_feasible(K) + κ·P_cap − c_req ≥ 0
    κ·P_cap: 安定電源1.25万 ／ 発動指令0.83万円/kW-年の2ケース
    c_req: 3.2〜3.7万円/kW-年（AFC2.5-3.0万＋託送等固定0.69万）

シナリオ: 現状 ／ 泊3号再稼働 ／ 泊＋風力2倍
出力: figures/hokkaido/pi_k_curve.png・data/processed/pi_k_curve.csv・標準出力の判定表
限界(v1): 1パス近似（フリートの充放電窓は変形前価格で決定）・p_system外生・仕様A。
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

# 13を実行してモデル部品を取り込む（仕様A: predict_A / est）
ns = {"__file__": os.path.join(HERE, "13_price_process_v1.py"), "__name__": "pp_v1"}
exec(open(os.path.join(HERE, "13_price_process_v1.py"), encoding="utf-8").read(), ns)
est = ns["est"].copy()
predict_A = ns["predict_A"]
K_WIND_NOW = ns["K_WIND_NOW"]

ETA = 0.85
CAPTURE = 0.81          # 気候値戦略cの実測capture率
WHEEL_YEN_KWH = 1.2     # 充電kWhへの託送従量+賦課金ロス分の概算（円/kWh）
TOMARI = 912_000 * 0.9 / 1000

est = est.sort_values("ts").reset_index(drop=True)
est["date"] = est["ts"].dt.normalize()

SCEN = {
    "現状": {"dnuc": 0.0, "wind_mult": 1.0},
    "泊3号再稼働": {"dnuc": TOMARI, "wind_mult": 1.0},
    "泊＋風力2倍": {"dnuc": TOMARI, "wind_mult": 2.0},
}
K_GRID = [0, 10, 25, 50, 100, 150, 200, 300]  # 万kW
SLICE_MANKW = 10  # 増分刻み（万kW）


def marginal_pf(P1):
    """価格行列P1（日×24）上の限界参入者の年間PF価値（円/kW-年、FY平均）"""
    srt = np.sort(P1, axis=1)
    m = np.maximum(0.0, (srt[:, -4:].sum(axis=1) * ETA - srt[:, :4].sum(axis=1)) * 1000)
    return m


rows = []
for scen_name, sp in SCEN.items():
    base = est.copy()
    dwind_kw = (sp["wind_mult"] - 1.0) * K_WIND_NOW * 1e4
    base["net0"] = base["net"] - dwind_kw * base["cf_wind"] / 1000 - sp["dnuc"]
    piv_net = base.pivot_table(index="date", columns=base["ts"].dt.hour, values="net0").dropna()
    full = piv_net.index
    tmp = base.loc[base["date"].isin(full)].sort_values("ts").copy()
    n_days = len(full)
    fy = full.year - (full.month < 4).astype(int)
    rowsel = np.arange(n_days)[:, None]

    adj = piv_net.to_numpy().copy()
    done_k = 0
    for K in K_GRID:
        # 増分貪欲ディスパッチ: done_k → K まで10万kW刻みで投入
        while done_k < K:
            slice_mw = SLICE_MANKW * 10.0
            p_now = predict_A(tmp.assign(net=adj.reshape(-1)), net_col="net").reshape(n_days, 24)
            order = np.argsort(p_now, axis=1)
            chg = order[:, :4]
            dis = order[:, -4:]
            margin = (np.take_along_axis(p_now, dis, 1).sum(1) * ETA
                      - np.take_along_axis(p_now, chg, 1).sum(1))
            act = margin > 0  # 正マージンの日のみ稼働
            adj[rowsel[act], chg[act]] += slice_mw
            adj[rowsel[act], dis[act]] -= slice_mw * ETA
            done_k += SLICE_MANKW
        p_fin = predict_A(tmp.assign(net=adj.reshape(-1)), net_col="net").reshape(n_days, 24)
        m = marginal_pf(p_fin)
        pi_pf = pd.Series(m, index=full).groupby(fy).sum().mean() / 1000
        charge_kwh = 4 * 365
        pi_feas = pi_pf * CAPTURE - charge_kwh * WHEEL_YEN_KWH
        rows.append({"シナリオ": scen_name, "K(万kW)": K,
                     "π_PF(円/kW-年)": round(pi_pf, 0),
                     "π_実現可能(円/kW-年)": round(pi_feas, 0)})
        print(rows[-1])

df = pd.DataFrame(rows)
df.to_csv(os.path.join(PROC, "pi_k_curve.csv"), index=False)

# ---------- 参入条件の判定 ----------
CASES = {
    "標準（容量1.25万・c_req3.45万）": 34500 - 12500,
    "楽観（容量1.25万・c_req3.2万）": 32000 - 12500,
    "保守（容量0.83万・c_req3.7万）": 37000 - 8300,
}
print("\n=== 参入に必要なスポット実現収益（円/kW-年） ===")
for k, v in CASES.items():
    print(f"  {k}: {v:,.0f}")
print("\n=== 各シナリオのπ_実現可能（K=0） vs 必要水準 ===")
for scen_name in SCEN:
    pi0 = df[(df["シナリオ"] == scen_name) & (df["K(万kW)"] == 0)]["π_実現可能(円/kW-年)"].iloc[0]
    need = CASES["標準（容量1.25万・c_req3.45万）"]
    print(f"  {scen_name}: π(0)={pi0:,.0f} → 不足 {need - pi0:,.0f} 円/kW-年"
          f"（損益分岐AFC: {pi0 + 12500 - 6900:,.0f} 円/kW-年 vs 実勢2.5-3.0万）")

# ---------- 図 ----------
C = {"現状": "#0079C2", "泊3号再稼働": "#D95B20", "泊＋風力2倍": "#176871"}
fig, ax = plt.subplots(figsize=(10.2, 5.6))
for scen_name in SCEN:
    d = df[df["シナリオ"] == scen_name]
    ax.plot(d["K(万kW)"], d["π_実現可能(円/kW-年)"], color=C[scen_name], lw=2.3,
            marker="o", ms=5, label=scen_name)
for lab, v, ls in [("参入に必要な水準（標準: 2.20万円）", CASES["標準（容量1.25万・c_req3.45万）"], "--"),
                   ("同（楽観: 1.95万円）", CASES["楽観（容量1.25万・c_req3.2万）"], ":")]:
    ax.axhline(v, color="#999999", lw=1.2, ls=ls)
    ax.text(298, v + 300, lab, ha="right", fontsize=9, color="#666666")
ax.set_xlabel("蓄電池フリート容量 K（万kW、4h）", fontsize=11, color="#595959")
ax.set_ylabel("限界参入者の実現可能スポット収益 π(K)（円/kW-年）", fontsize=11, color="#595959")
ax.set_title("π(K)曲線と参入条件 — 現行構造ではマーチャントの均衡容量 K*=0（参入は市場外収入に依存する容量が駆動）",
             fontsize=13, fontweight="bold", pad=12)
ax.grid(axis="y", color="#DDDDDD", lw=0.6)
for sp_ in ["top", "right"]:
    ax.spines[sp_].set_visible(False)
ax.tick_params(colors="#595959")
ax.legend(fontsize=10, frameon=False, loc="center right")
fig.text(0.99, 0.005,
         "基本仕様の価格過程（決定論仕様）・FY2023-25パス・capture0.81・充電従量1.2円/kWh控除。参入必要水準=c_req−容量市場収入。増分貪欲ディスパッチ（10万kW刻み）・部分均衡",
         ha="right", fontsize=7.5, color="#595959")
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "pi_k_curve.png"), dpi=160, bbox_inches="tight")
print("saved pi_k_curve.png")
