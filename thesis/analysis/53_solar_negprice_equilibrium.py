#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""太陽光の増加・負の価格・価格水準・資本費の下での自由参入均衡容量 K* と固定費の不足額（論文の再設計 notes/36）

目的:
  「蓄電池はどこまで増えるか」を、市場収入（スポット裁定＋北海道ブロックの容量市場）だけで成立する容量 K*（4時間の
  系統用蓄電池、万kW）で答える。太陽光がエネルギー基本計画の2040年度の水準まで増えたとき、0.01円の下限価格が裁定価値に
  かけるキャップと、負の価格を許したときの K* と必要な市場外の補填を測る。

前提（notes/36 の合意事項・仮定 A1〜A7）:
  - 需給調整市場とスポット市場の間に裁定機会はない（A1）。蓄電池の市場収益はスポットのスプレッドで測る。
  - 容量市場は北海道を独立のブロックとし、κP(K) は capacity_price_of_k_v3.csv の「北海道ブロック按分・起点1.25万・
    2030年度向け近似（主）」（感応度は同「比例縮小」）。LTDA・補助金は扱わない（A3、参入に有利な側）。
  - 費用（A4、2026-10-22 の調査で改訂。税抜、JEPX 価格に合わせる）:
      資本費 6.8万円/kWh×4時間×CRF(6%,20年) ＋ 運維・廃止 5,300円 ＋ 託送等の固定費 2,303円/kW-年。
      託送等の固定費は、北海道電力ネットワーク託送供給等約款 附則3（揚水発電設備等の特別措置: 需要側は充電の損失分だけに
      課金）と発電側課金（揚水・蓄電池は kWh 課金を免除、kW 課金は損失分を除く逆潮 kW）による。
      12×(0.15×628.10＋0.85×137.50)÷1.1（特高標準、2026/11〜の単価、税込→税抜、揚水等損失率0.15）。
      充電の従量費は1,460kWh/kW-年×0.15×(託送従量1.02＋再エネ賦課金4.18)÷1.1＝1,035円/kW-年（賦課金はロス分のみ、
      著者確認 2026-10-22）。旧原稿の値（託送等6,947円・充電従量1,752円）は再現の確認にだけ使う。
  - 太陽光（A5）: 純需要から（倍率−1）×制御前太陽光を引く。倍率は 1.0（現状）、1.5（OCCTO 2026年度供給計画の北海道
    2035年度末 356万kW ≈ 現行の1.5倍）、2.6・3.0・3.5（第7次エネ基の2040年度見通し: 太陽光 23〜29%×1.1〜1.2兆kWh ＝
    2,530〜3,480億kWh、FY2024 確報981億kWh の2.58〜3.55倍）。
  - 負の価格（A6）: 段差モデル（43 と同じ）。仕様A（26）の base=max{0.01, g(net)+μ} が 0.01 に達する時間だけ価格を −c 円
    とし、それ以外は 0.01＋θ(base−0.01)。c は 現行（0.01円のまま）・1・3・5・10円。−c は θ で伸縮させない。
  - 価格水準 θ: 1.0（主、FY2023〜25）、θ_FY2026上期（1.567）、θ_FY2022（1.715）を感応度。
手法:
  41 の前半（"curves = []" より前の定義部分）を exec で読み込み（to_csv は無効、標準出力は捨てる）、41 と同じ増分貪欲
  （刻み1万kW、目標の K に正確に到達）で π(K) を求める。K は 0〜100万kW を1万kW ごと、105〜200万kW を5万kW ごと。
  収益は実績整合（λ＝実績の戦略c 8,427円 ÷ モデルの c(K=0, θ=1, 太陽光×1, 現行の下限)、41 と同じ λ=1.1085）。
  π(K) = λ·c(K) − 充電従量費。K* はゼロレント条件 π(K)＋κP(K) ≥ c_req を満たす最大の K（格子の間は線形補間）。
  F(K) = c_req − max{π(K),0} − κP(K) を固定費の不足額とし、K_target までの限界の不足額の合計（Σ_k max{F(k),0}×1万kW、
  億円/年）を「その容量を支えるのに要る市場外の補填」とする。下限が奪う価値は π(負の価格) − π(0.01円)。
  頑健性: 下限の時間を季節別に実績へ較正した段差モデル（43 の (1c) と同じ考え方）、容量価格の比例縮小版、賦課金全量。
出力: data/processed/solar_negprice_curves.csv（π(K) の全曲線）、solar_negprice_kstar.csv、solar_negprice_support.csv、
      solar_negprice_floor_value.csv、solar_negprice_robust.csv、solar_negprice_cost_params.csv、
      figures/hokkaido/solar_negprice_stack.png、figures/hokkaido/solar_negprice_kstar.png
限界: 部分均衡（揚水・連系線・入札行動は g に埋め込まれた歴史的応答のまま）。太陽光の倍率は全国の発電量の倍率を北海道の
      制御前出力の伸縮に使ったもので、需要の伸び・風力・原子力は現状のまま。倍率2.6〜3.5 では純需要が g の推定範囲を大きく
      下回り、下限の時間は段差の仮定で決まる。負の価格の深さ c は外生（0.01円で打ち切られたデータから負の領域は識別できない）。
      λ は現状の K=0 で校正した in-sample の係数。完全予見の増分貪欲のフリートは、裁定の取り分を大きく見せる側にある。
"""
import contextlib
import io
import logging
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
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
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------- (0) 41 の部品
SRC41 = open(os.path.join(HERE, "41_equilibrium_v3.py"), encoding="utf-8").read()
HEAD41 = SRC41.split("\ncurves = []\n")[0]
assert len(HEAD41) < len(SRC41) and "def run_curve" in HEAD41
m41 = {"__file__": os.path.join(HERE, "41_equilibrium_v3.py"), "__name__": "mod41_head"}
_to_csv = pd.DataFrame.to_csv
pd.DataFrame.to_csv = lambda *a, **k: None            # 既存の出力ファイルを上書きしない
try:
    with contextlib.redirect_stdout(io.StringIO()):
        exec(HEAD41, m41)
finally:
    pd.DataFrame.to_csv = _to_csv

daily_eval, annual, g_curve = m41["daily_eval"], m41["annual"], m41["g_curve"]
G26, MU26, MU26B, SEASB, SEASM, BLK, RB = m41["G26"], m41["MU26"], m41["MU26B"], m41["SEASB"], m41["SEASM"], m41["BLK"], m41["RB"]
W_B, FYB, EVB, EV = m41["W_B"], m41["FYB"], m41["EVB"], m41["EV"]
NETM, SOLM, PACTM = m41["NETM"], m41["SOLM"], m41["PACTM"]
FLOOR, ETA, C_ACT = m41["FLOOR"], m41["ETA"], m41["C_ACT"]
TH26, TH22 = m41["TH26"], m41["THETA"][2022]
assert np.allclose(m41["DEMM"] - SOLM - m41["WINDM"], NETM)   # 純需要＝需要−太陽光−風力（MW）
print(f"41 の部品を読み込み: 実績の戦略c {C_ACT:,.1f}円/kW-年（FY2023〜25）、θ_FY2026上期 {TH26:.3f}、θ_FY2022 {TH22:.3f}")

# ---------------------------------------------------------------- 費用の前提（税抜）
CRF20 = 0.06 * 1.06 ** 20 / (1.06 ** 20 - 1)
OM = 5_300.0
LOSS = 0.15
CHG_KWH = 4 * 365                                     # 年間充電量（kWh/kW-年、41 と同じ定義）
NET_FIX = 12 * (LOSS * 628.10 + (1 - LOSS) * 137.50) / 1.1
W_LOSS = CHG_KWH * LOSS * (1.02 + 4.18) / 1.1
W_FULL = CHG_KWH * (LOSS * 1.02 + 4.18) / 1.1
NET_FIX_OLD, W_OLD = 6_900.0, 1_752.0                 # 旧原稿（41 の C_FIX の託送等6,900、WHEEL 1,752）
assert abs(m41["C_FIX"] - (OM + NET_FIX_OLD)) < 1e-9 and abs(m41["WHEEL"] - W_OLD) < 1e-9
CAPEX = {"6.8万": 68_000.0, "4.0万": 40_000.0, "2.3万": 23_000.0}


def c_req(capex, net_fix=NET_FIX):
    return capex * 4 * CRF20 + OM + net_fix


COSTS = pd.DataFrame([
    {"項目": "CRF(6%,20年)", "値": CRF20, "単位": "—", "根拠": "r(1+r)^n/((1+r)^n−1)"},
    {"項目": "運維・廃止", "値": OM, "単位": "円/kW-年", "根拠": "現原稿と同じ（算定委員会の想定）"},
    {"項目": "託送等の固定費（主）", "値": NET_FIX, "単位": "円/kW-年", "根拠": "12×(0.15×628.10＋0.85×137.50)÷1.1。約款 附則3（特措）・発電側課金 kW、特高、2026/11〜、税抜"},
    {"項目": "充電の従量費（主、賦課金ロス分のみ）", "値": W_LOSS, "単位": "円/kW-年", "根拠": "1,460kWh×0.15×(1.02＋4.18)÷1.1"},
    {"項目": "充電の従量費（感応度、賦課金全量）", "値": W_FULL, "単位": "円/kW-年", "根拠": "1,460kWh×(0.15×1.02＋4.18)÷1.1"},
    {"項目": "託送等の固定費（旧原稿）", "値": NET_FIX_OLD, "単位": "円/kW-年", "根拠": "託送503.8＋発電側75.1 円/kW・月×12（二重計上）"},
    {"項目": "充電の従量費（旧原稿）", "値": W_OLD, "単位": "円/kW-年", "根拠": "1.2円/kWh×1,460kWh"},
] + [{"項目": f"c_req（資本費{k}円/kWh）", "値": c_req(v), "単位": "円/kW-年", "根拠": "資本費×4×CRF＋運維＋託送等（主）"} for k, v in CAPEX.items()])
COSTS.to_csv(os.path.join(PROC, "solar_negprice_cost_params.csv"), index=False, encoding="utf-8-sig")
print(COSTS[["項目", "値"]].round(1).to_string(index=False))

# ---------------------------------------------------------------- 容量価格 κP(K)（北海道ブロック）
CAP = pd.read_csv(os.path.join(PROC, "capacity_price_of_k_v3.csv"))
CAP_K = CAP["K(万kW)"].to_numpy(float)
KP_SPEC = {"北海道ブロック・2030年度向け近似（主）": "κP 北海道ブロック按分・起点1.25万・2030年度向け近似（主）(円/kW-年)",
           "北海道ブロック・比例縮小（感応度）": "κP 北海道ブロック按分・起点1.25万・比例縮小(円/kW-年)",
           "全国連系・2030年度向け近似（参考）": "κP 全国連系・起点1.25万・2030年度向け近似（主）(円/kW-年)"}
KP_MAIN = "北海道ブロック・2030年度向け近似（主）"


def kp(K, spec=KP_MAIN):
    return np.interp(K, CAP_K, CAP[KP_SPEC[spec]].to_numpy(float))


# ---------------------------------------------------------------- 価格関数と増分貪欲
K_EVAL = list(range(0, 101)) + list(range(105, 201, 5))
TAU = None                                            # 較正版の閾値（後で設定）


def pfun_of(theta, depth, calibrated=False):
    def f(net):
        base = np.maximum(g_curve(net, G26, SEASB) + MU26B, FLOOR)
        p = np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)
        low = base <= (TAU if calibrated else FLOOR + 1e-9)
        if calibrated:
            p = np.where(low, FLOOR, p)
        return p if depth is None else np.where(low, -depth, p)
    return f


def run(net0, pfun, Ks=K_EVAL):
    """41 の run_curve（mode=PF）と同じ増分貪欲。各 K で π_PF・戦略c・下限（以下）の時間（評価期間の年平均）を返す"""
    adj, done, out = net0.copy(), 0.0, []
    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            p = pfun(adj)
            o = np.argsort(p, 1)
            chg, dis = o[:, :4], o[:, -4:]
            mg = np.take_along_axis(p, dis, 1).sum(1) * ETA - np.take_along_axis(p, chg, 1).sum(1)
            a = mg > 0
            adj[RB[a], chg[a]] += st * 10.0
            adj[RB[a], dis[a]] -= st * 10.0 * ETA
            done += st
        P = pfun(adj)
        d = daily_eval(P, W_B)
        out.append({"K(万kW)": K, "π_PF": annual(d["pf"], FYB, EVB), "c": annual(d["c"], FYB, EVB),
                    "下限以下の時間(h/年)": float((P[EVB] <= FLOOR + 1e-9).sum() / EVB.sum() * 365)})
    return pd.DataFrame(out)


def net_solar(sm):
    return NETM[BLK] - (sm - 1.0) * SOLM[BLK]


# λ と旧原稿の再現
base0 = run(net_solar(1.0), pfun_of(1.0, None), [0, 50])
LAM = C_ACT / base0["c"].iloc[0]
v3 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
v3 = v3[(v3["価格モデル"].str.startswith("仕様A（26")) & (v3["シナリオ"] == "現状") & (v3["θ"] == 1.0)
        & (v3["フリート配分"] == "完全予見の増分貪欲（主）") & (v3["刻み(万kW)"].astype(str) == "1.0")].set_index("K(万kW)")
for K in (0, 50):
    old = LAM * base0.set_index("K(万kW)").loc[K, "c"] - W_OLD
    assert abs(old - v3.loc[K, "π_実績整合"]) < 1.0, (K, old, v3.loc[K, "π_実績整合"])
print(f"λ={LAM:.4f}。旧費用で π(0)・π(50) が pi_k_curve_v3.csv（6,675・1,510）と一致")

# ---------------------------------------------------------------- (1) 格子
SM = {1.0: "現状", 1.5: "OCCTO 2035年度（約1.5倍）", 2.6: "エネ基2040 下限（2.6倍）", 3.0: "エネ基2040 中央（3.0倍）",
      3.5: "エネ基2040 上限（3.5倍）"}
DEPTH = {None: "現行（0.01円）", 1.0: "−1円", 3.0: "−3円", 5.0: "−5円", 10.0: "−10円"}
THETAS = {1.0: "θ=1（主、FY2023〜25）", round(TH26, 3): "θ=FY2026上期", round(TH22, 3): "θ=FY2022"}
print("\n[1] π(K) の格子を計算中 ...")
rows = []
for th, thl in THETAS.items():
    for sm in SM:
        for dp, dpl in DEPTH.items():
            df = run(net_solar(sm), pfun_of(th, dp))
            df.insert(0, "下限", dpl)
            df.insert(0, "太陽光倍率", sm)
            df.insert(0, "θ", th)
            rows.append(df)
CUR = pd.concat(rows, ignore_index=True)
CUR["π_実績整合"] = LAM * CUR["c"] - W_LOSS
CUR["π_実績整合（賦課金全量）"] = LAM * CUR["c"] - W_FULL
for spec in KP_SPEC:
    CUR[f"κP（{spec}）"] = kp(CUR["K(万kW)"].to_numpy(float), spec)
for ck, cv in CAPEX.items():
    CUR[f"F（資本費{ck}）"] = c_req(cv) - CUR["π_実績整合"].clip(lower=0) - CUR[f"κP（{KP_MAIN}）"]
CUR["損益分岐の資本費(円/kWh)"] = (CUR["π_実績整合"].clip(lower=0) + CUR[f"κP（{KP_MAIN}）"] - OM - NET_FIX) / (4 * CRF20)
CUR.insert(3, "太陽光の想定", CUR["太陽光倍率"].map(SM))
CUR.round(4).to_csv(os.path.join(PROC, "solar_negprice_curves.csv"), index=False, encoding="utf-8-sig")
print(f"  {len(CUR):,} 行")


def kstar(d, capex, pi_col="π_実績整合", spec=KP_MAIN, net_fix=NET_FIX):
    """ゼロレント π(K)+κP(K) ≥ c_req を満たす最大の K（格子の間は線形補間）。K=0 で不成立なら NaN"""
    K = d["K(万kW)"].to_numpy(float)
    slack = d[pi_col].clip(lower=0).to_numpy() + kp(K, spec) - c_req(capex, net_fix)
    if slack[0] < 0:
        return np.nan
    neg = np.where(slack < 0)[0]
    if len(neg) == 0:
        return float(K[-1])                            # 格子の上限（200万kW）でも成立
    i = neg[0]
    return float(K[i - 1] + (K[i] - K[i - 1]) * slack[i - 1] / (slack[i - 1] - slack[i]))


KS = []
for (th, sm, dpl), d in CUR.groupby(["θ", "太陽光倍率", "下限"], sort=False):
    for ck, cv in CAPEX.items():
        KS.append({"θ": th, "太陽光倍率": sm, "太陽光の想定": SM[sm], "下限": dpl, "資本費(円/kWh)": ck,
                   "K*(万kW)": kstar(d, cv), "K*（容量価格の比例縮小）": kstar(d, cv, spec="北海道ブロック・比例縮小（感応度）"),
                   "K*（賦課金全量）": kstar(d, cv, pi_col="π_実績整合（賦課金全量）"),
                   "π(0)": d["π_実績整合"].iloc[0], "π(50)": d.set_index("K(万kW)").loc[50, "π_実績整合"],
                   "下限以下の時間(K=0)": d["下限以下の時間(h/年)"].iloc[0],
                   "F(0)": c_req(cv) - max(d["π_実績整合"].iloc[0], 0) - kp(0.0),
                   "損益分岐の資本費 K=0(円/kWh)": d["損益分岐の資本費(円/kWh)"].iloc[0]})
KST = pd.DataFrame(KS)
KST.round(3).to_csv(os.path.join(PROC, "solar_negprice_kstar.csv"), index=False, encoding="utf-8-sig")
print("\n[2] K*（万kW、θ=1、資本費別。NaN は K=0 でも不成立、200 は格子の上限）")
piv = KST[KST["θ"] == 1.0].pivot_table(index=["太陽光倍率", "下限"], columns="資本費(円/kWh)", values="K*(万kW)", sort=False)
print(piv[list(CAPEX)].round(1).to_string())

# θ*（K=0、太陽光×1、現行の下限）: 収益が θ に比例するとした値と、3点の a=α+βθ の直接解
a_th = {th: LAM * CUR[(CUR["θ"] == th) & (CUR["太陽光倍率"] == 1.0) & (CUR["下限"] == DEPTH[None]) & (CUR["K(万kW)"] == 0)]["c"].iloc[0]
        for th in THETAS}
need = c_req(CAPEX["6.8万"]) - kp(0.0) + W_LOSS
al, be = np.polyfit(list(a_th), list(a_th.values()), 1)[::-1]
THETA_STAR = {"比例": need / a_th[1.0], "直接解（a=α+βθ）": (need - al) / be}
print(f"\nθ*（K=0、資本費6.8万、主の費用）: 比例 {THETA_STAR['比例']:.3f}、直接解 {THETA_STAR['直接解（a=α+βθ）']:.3f}"
      f"（旧費用の比例の値 {(c_req(CAPEX['6.8万'], NET_FIX_OLD) - kp(0.0) + W_OLD) / a_th[1.0]:.3f}）")

# ---------------------------------------------------------------- (3) 下限が奪う価値と市場外の補填
FV, SUP = [], []
for (th, sm), d in CUR.groupby(["θ", "太陽光倍率"], sort=False):
    ref = d[d["下限"] == DEPTH[None]].set_index("K(万kW)")["π_実績整合"]
    for dpl in list(DEPTH.values())[1:]:
        x = d[d["下限"] == dpl].set_index("K(万kW)")["π_実績整合"]
        FV.append({"θ": th, "太陽光倍率": sm, "太陽光の想定": SM[sm], "下限": dpl,
                   "下限が奪う価値 K=0(円/kW-年)": x.loc[0] - ref.loc[0], "同 K=50": x.loc[50] - ref.loc[50],
                   "c_req（6.8万）に対する比 K=0": (x.loc[0] - ref.loc[0]) / c_req(CAPEX["6.8万"])})
    for dpl in DEPTH.values():
        x = d[d["下限"] == dpl].set_index("K(万kW)")
        for ck, cv in CAPEX.items():
            for KT in (20, 50, 100):
                ks = np.arange(0, KT)                  # 1万kW の増分 k=0..KT−1 の限界の不足額
                f = c_req(cv) - x.loc[ks, "π_実績整合"].clip(lower=0).to_numpy() - kp(ks.astype(float))
                SUP.append({"θ": th, "太陽光倍率": sm, "太陽光の想定": SM[sm], "下限": dpl, "資本費(円/kWh)": ck, "K_target(万kW)": KT,
                            "市場外の補填の合計(億円/年)": float(np.clip(f, 0, None).sum() * 1e4 / 1e8),
                            "K_target での F(円/kW-年)": float(c_req(cv) - max(x.loc[KT, "π_実績整合"], 0) - kp(float(KT))),
                            "K_target の下限以下の時間(h/年)": float(x.loc[KT, "下限以下の時間(h/年)"])})
FVD, SUPD = pd.DataFrame(FV), pd.DataFrame(SUP)
FVD.round(4).to_csv(os.path.join(PROC, "solar_negprice_floor_value.csv"), index=False, encoding="utf-8-sig")
SUPD.round(3).to_csv(os.path.join(PROC, "solar_negprice_support.csv"), index=False, encoding="utf-8-sig")
print("\n[3] 下限が奪う価値（θ=1、K=0、円/kW-年）")
print(FVD[FVD["θ"] == 1.0].pivot_table(index="太陽光倍率", columns="下限", values="下限が奪う価値 K=0(円/kW-年)", sort=False).round(0).to_string())
print("\n    0〜50万kW を支える市場外の補填の合計（θ=1、資本費6.8万、億円/年）")
print(SUPD[(SUPD["θ"] == 1.0) & (SUPD["資本費(円/kWh)"] == "6.8万") & (SUPD["K_target(万kW)"] == 50)]
      .pivot_table(index="太陽光倍率", columns="下限", values="市場外の補填の合計(億円/年)", sort=False).round(1).to_string())

# ---------------------------------------------------------------- (4) 頑健性: 下限の時間を季節別に実績へ較正
seas_ev = SEASM[EV]
b_ev = np.maximum(g_curve(NETM[EV], G26, seas_ev) + MU26[EV], FLOOR)
tau = {}
for s in range(4):
    m = seas_ev == s
    n_act = int((PACTM[EV][m] <= 0.011).sum())
    b = np.sort(b_ev[m])
    tau[s] = max(FLOOR + 1e-9, b[n_act - 1]) if n_act > 0 else FLOOR + 1e-9
TAU = np.vectorize(tau.get)(SEASB)
LAM_CAL = C_ACT / run(net_solar(1.0), pfun_of(1.0, None, True), [0])["c"].iloc[0]
RB_ = []
for sm in (1.0, 2.6, 3.0, 3.5):
    for dp in (None, 5.0, 10.0):
        dc = run(net_solar(sm), pfun_of(1.0, dp, True), [0, 50])
        dm = CUR[(CUR["θ"] == 1.0) & (CUR["太陽光倍率"] == sm) & (CUR["下限"] == DEPTH[dp])].set_index("K(万kW)")
        RB_.append({"太陽光倍率": sm, "下限": DEPTH[dp], "較正版 λ": LAM_CAL,
                    "較正版 π(0)": LAM_CAL * dc["c"].iloc[0] - W_LOSS, "主 π(0)": dm.loc[0, "π_実績整合"],
                    "較正版 π(50)": LAM_CAL * dc["c"].iloc[1] - W_LOSS, "主 π(50)": dm.loc[50, "π_実績整合"],
                    "較正版 下限以下の時間(K=0)": dc["下限以下の時間(h/年)"].iloc[0], "主 下限以下の時間(K=0)": dm.loc[0, "下限以下の時間(h/年)"]})
RBD = pd.DataFrame(RB_)
RBD["π(0) の差(%)"] = (RBD["較正版 π(0)"] / RBD["主 π(0)"] - 1) * 100
RBD.round(3).to_csv(os.path.join(PROC, "solar_negprice_robust.csv"), index=False, encoding="utf-8-sig")
print(f"\n[4] 下限の時間の較正（τ_s={ {k: round(float(v), 3) for k, v in tau.items()} }、実績の下限時間 "
      f"{(PACTM[EV] <= 0.011).sum() / EV.sum() * 365:.0f}h/年）")
print(RBD.round(1).to_string(index=False))

# ---------------------------------------------------------------- 図
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8})
fig, axes = plt.subplots(1, 2, figsize=(6.1, 2.9), sharey=True)
for ax, sm in zip(axes, (1.0, 3.0)):
    for dpl, col, ls in ((DEPTH[None], "#1f4e79", "-"), (DEPTH[5.0], "#c55a11", "--"), (DEPTH[10.0], "#c00000", ":")):
        d = CUR[(CUR["θ"] == 1.0) & (CUR["太陽光倍率"] == sm) & (CUR["下限"] == dpl)]
        ax.plot(d["K(万kW)"], (d["π_実績整合"].clip(lower=0) + d[f"κP（{KP_MAIN}）"]) / 1e4, color=col, ls=ls, lw=1.4,
                label=f"下限 {dpl.replace('現行（0.01円）', '0.01円')}")
    for ck, ls in (("6.8万", "-"), ("4.0万", "--"), ("2.3万", ":")):
        ax.axhline(c_req(CAPEX[ck]) / 1e4, color=GRAY, lw=0.8, ls=ls)
        ax.text(200, c_req(CAPEX[ck]) / 1e4, f"必要収益（{ck}円/kWh）", fontsize=7.5, color=GRAY, ha="right", va="bottom")
    ax.set_title(f"太陽光 {SM[sm]}")
    ax.set_xlabel("蓄電池の容量 K（万kW）")
    ax.set_xlim(0, 200)
    ax.grid(alpha=0.3, lw=0.5)
axes[0].set_ylabel("限界参入者の市場収入（万円/kW-年）")
axes[0].legend(loc="lower right", frameon=False, bbox_to_anchor=(1.0, 0.06))
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "solar_negprice_stack.png"), dpi=200)
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(6.1, 2.7), sharey=True)
xs = np.arange(len(SM))
w = 0.16
for ax, ck in zip(axes, ("6.8万", "4.0万")):
    for j, (dp, dpl) in enumerate(DEPTH.items()):
        y = [KST[(KST["θ"] == 1.0) & (KST["太陽光倍率"] == sm) & (KST["下限"] == dpl) & (KST["資本費(円/kWh)"] == ck)]["K*(万kW)"].fillna(0).iloc[0]
             for sm in SM]
        ax.bar(xs + (j - 2) * w, y, w, label=dpl.replace("現行（0.01円）", "0.01円"),
               color=["#1f4e79", "#5b9bd5", "#f4b183", "#c55a11", "#c00000"][j])
    ax.set_xticks(xs)
    ax.set_xticklabels([f"×{s:g}" for s in SM])
    ax.set_xlabel("太陽光の倍率（現状比）")
    ax.set_title(f"資本費 {ck}円/kWh")
    ax.grid(axis="y", alpha=0.3, lw=0.5)
axes[0].set_ylabel("市場だけで成立する容量 K*（万kW）")
axes[1].legend(frameon=False, loc="upper left", ncol=1)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "solar_negprice_kstar.png"), dpi=200)
plt.close(fig)
print("\n図: solar_negprice_stack.png、solar_negprice_kstar.png")
