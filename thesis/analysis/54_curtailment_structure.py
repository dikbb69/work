#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""【使わない（2026-10-22 の検証で重大な問題。notes/36 §8.8）。55 の演繹モデルに置き換える】
出力抑制時の電源構成に着目した構造モデル（簡易版・帰納的）: 自家消費の増加と原子力の再稼働が、火力の停止を要する余剰（深い負の価格）を生むか

考え方（著者の整理、2026-10-22）:
  - 事業用の太陽光・風力は遠隔で制御でき、止める物理的な費用はほぼ0 である。余剰を事業用の再エネの抑制だけで吸収できる
    時間は、負の価格を許しても価格はほぼ0 にとどまる（再エネが限界の電源）。
  - 自家消費の太陽光は逆潮流せず、昼の需要のへこみとして現れる。自家消費の増加と原子力の再稼働によるベース電源の底上げが
    重なると、事業用の再エネをすべて止めても供給が吸収できる量を上回る時間が生じる。その時間は火力を停止（解列）するしかなく、
    価格は火力の停止コスト（起動費を停止時間の最低出力の発電量で割った値）まで下がる。
  本スクリプトは、この「火力の停止を要する余剰」を時間別に数え、その時間の負の価格を停止コストで決めて蓄電池の π(K)・K* を求める。

構造（時間 h、MW）:
  硬直的な供給   B(h) = 原子力 N ＋ 火力の床 T ＋ 水力(h) ＋ バイオマス(h) ＋ 地熱(h)
  吸収できる量   A(h) = 需要(h) − ΔS·CF(h) ＋ 北本の送電 X ＋ 揚水動力 P
  余剰（再エネを全部止めた後） E(h) = B(h) − A(h)。E>0 の時間は火力の停止が要る。
  - 需要・水力・バイオマス・地熱は北海道エリアの需給実績（hokkaido_hourly_panel.csv、時間平均 MW）。需要は既存の自家消費を
    差し引いた系統の需要である。バイオマスは実績（出力制御後）をそのまま硬直的とみなす。
  - 火力の床 T: 2024/4〜2026/6 の出力制御のコマ（30分値、eria_jukyu）の火力合計の5%点 561MW を主とする（資源エネルギー庁
    第12回次世代電力系統WG 参考資料1 の2035年の前提は調整火力39万kW＋非調整火力22万kW＝61万kW）。感応度は 400MW
    （既設火力の最低出力30%化・石炭の廃止）。
  - 北本の送電 X: 570MW（同前提の連系線活用 ▲57万kW）。感応度 900MW。揚水動力 P: 680MW（同前提 p.13、上池394万kWh）。
  - 自家消費の追加 ΔS（万kW）: 0・50・100・150・200。CF(h) は北海道の制御前太陽光 ÷ 設備容量（area_capacity_series.csv、
    月末値を日次に補間）。追加の自家消費はすべて自家で消費され、逆潮流しないと置く。
  - 原子力 N: 0、泊3号 820.8MW（41 と同じ 912MW×0.9）、泊全基 1,680MW（同前提 p.11 の 198万kW×85%）。
停止コスト（負の価格の深さ）:
  OCCTO 第103回広域系統整備委員会 資料3（2026/9/1）p.53〜54 の起動費の式（電中研 2016）と最低出力を北海道のユニットに当てる。
  余剰 E のうち最初の 114MW は LNG（石狩湾新港1号 569.4MW、最低出力20%、起動費 569.4×1,000＋1,000,000 円）、
  それを超える分は石炭（苫東厚真の各機、最低出力30%、起動費 容量×13,000 円/MW）を止めるとし、価格は限界のユニットの
  停止コスト＝起動費÷（最低出力×その日の E>0 の連続時間 H）で決める（LNG ≈ 13.8/H 円/kWh、石炭 ≈ 43.3/H 円/kWh）。
  石炭は起動停止に8時間・1日1回の制約があるので、H<8 の停止は実務上むずかしい（その場合の価格は上の値より深くなりうる）。
価格と蓄電池:
  41 の仕様A（水準係数付き、θ=1）の価格に、E>0 の時間だけ −停止コスト を入れる。それ以外の下限の時間は 0.01円のまま
  （事業用の再エネが限界）。純需要は 需要 − ΔS·CF − 事業用太陽光（倍率 m）− 風力 − N。蓄電池の充電は A を増やす（E を減らす）。
  π(K) は 41 と同じ増分貪欲（刻み1万kW）、収益は実績整合（λ）、費用は 53 の主ケース（託送の蓄電池特措、税抜）。
出力: data/processed/curtailment_structure_now.csv（現状の出力制御のコマの電源構成）、curtailment_structure_surplus.csv
      （シナリオ別の E>0 の時間・深さ・連続時間・停止コスト）、curtailment_structure_kstar.csv（π(0)・K*）、
      figures/hokkaido/curtailment_structure.png
限界: 部分均衡（需要・水力・バイオマス・連系線の時間別のパターンは FY2023〜25 の実績のまま）。水力の調整池・貯水池の時間移動、
      揚水の上池の容量、連系線の相手側（東北）の余剰、火力の慣性・電圧維持のための最低台数は、床 T と X・P の一定値に
      まとめている。風力は事業用の太陽光と同じく遠隔で止められると置く（北海道の風力のオンライン化率は約89%）。
      停止コストは OCCTO の想定式による推計で、実際の入札は燃料契約・設備劣化・起動の失敗の危険などで異なる。
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
RAW = os.path.join(ROOT, "data", "raw", "hokkaido")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY = "#595959"
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------- (A) 現状: 出力制御のコマの電源構成（30分値）
fs = sorted(f for f in os.listdir(RAW) if f.startswith("eria_jukyu_2") and f.endswith("_01.csv"))
J = pd.concat([pd.read_csv(os.path.join(RAW, f), encoding="shift_jis", skiprows=1) for f in fs], ignore_index=True)
J.columns = [c.strip() for c in J.columns]
J["ts"] = pd.to_datetime(J["DATE"] + " " + J["TIME"])
NUMC = [c for c in J.columns if c not in ("DATE", "TIME", "ts")]
J[NUMC] = J[NUMC].apply(pd.to_numeric, errors="coerce")
J["火力計"] = J[["火力(LNG)", "火力(石炭)", "火力(石油)", "火力(その他)"]].sum(axis=1)
J["再エネ出力制御"] = J["太陽光出力制御量"].fillna(0) + J["風力出力制御量"].fillna(0)
CUR = J[J["再エネ出力制御"] > 0]
COLS_A = ["エリア需要", "原子力", "火力(LNG)", "火力(石炭)", "火力(石油)", "火力(その他)", "火力計", "水力", "地熱", "バイオマス",
          "バイオマス出力制御量", "太陽光発電実績", "太陽光出力制御量", "風力発電実績", "風力出力制御量", "揚水", "蓄電池", "連系線"]
NOW = CUR[COLS_A].describe(percentiles=[0.05, 0.5, 0.95]).T[["mean", "5%", "50%", "95%", "min", "max"]]
NOW.insert(0, "コマ数", len(CUR))
NOW.round(1).to_csv(os.path.join(PROC, "curtailment_structure_now.csv"), encoding="utf-8-sig")
T_FLOOR = float(CUR["火力計"].quantile(0.05))
print(f"[A] 出力制御のコマ（{J.ts.min():%Y-%m}〜{J.ts.max():%Y-%m}、30分値）: {len(CUR):,} コマ、火力計の5%点 {T_FLOOR:.0f}MW")
print(NOW[["mean", "5%", "50%"]].round(0).to_string())

# ---------------------------------------------------------------- 41 の部品（価格モデル・増分貪欲の道具）
SRC41 = open(os.path.join(HERE, "41_equilibrium_v3.py"), encoding="utf-8").read()
HEAD41 = SRC41.split("\ncurves = []\n")[0]
m41 = {"__file__": os.path.join(HERE, "41_equilibrium_v3.py"), "__name__": "mod41_head"}
_to_csv = pd.DataFrame.to_csv
pd.DataFrame.to_csv = lambda *a, **k: None
try:
    with contextlib.redirect_stdout(io.StringIO()):
        exec(HEAD41, m41)
finally:
    pd.DataFrame.to_csv = _to_csv
daily_eval, annual, g_curve = m41["daily_eval"], m41["annual"], m41["g_curve"]
G26, MU26B, SEASB, BLK, RB = m41["G26"], m41["MU26B"], m41["SEASB"], m41["BLK"], m41["RB"]
W_B, FYB, EVB, DAYS = m41["W_B"], m41["FYB"], m41["EVB"], m41["DAYS"]
NETM, SOLM, WINDM, DEMM = m41["NETM"], m41["SOLM"], m41["WINDM"], m41["DEMM"]
FLOOR, ETA, C_ACT = m41["FLOOR"], m41["ETA"], m41["C_ACT"]

# 需給実績の時間別（41 と同じ日の行列）
P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
P = P[(P["ts"] >= DAYS[0]) & (P["ts"] < DAYS[-1] + pd.Timedelta(days=1))].copy()
P["date"], P["hour"] = P["ts"].dt.normalize(), P["ts"].dt.hour


def matp(col):
    m = P.pivot_table(index="date", columns="hour", values=col).reindex(DAYS)
    return m.to_numpy(float)


HYM, BIOM, GEOM, DEMP = matp("hydro"), matp("biomass"), matp("geothermal"), matp("demand")
assert np.nanmax(np.abs(DEMP - DEMM)) < 1e-6                    # 41 の需要と同じ系列
for nm, m in (("水力", HYM), ("バイオマス", BIOM), ("地熱", GEOM)):
    assert not np.isnan(m).any(), nm
CAP = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
CAP = CAP[CAP["area"] == "hokkaido"].set_index("date")["solar_kw"].sort_index()
SOLCAP = CAP.reindex(CAP.index.union(DAYS)).interpolate("time").reindex(DAYS).to_numpy()[:, None] / 1000.0   # MW
CFM = np.clip(SOLM / SOLCAP, 0, 1)
print(f"\n太陽光の CF（制御前÷設備）: 平均 {CFM.mean():.3f}、最大 {CFM.max():.3f}（設備 {SOLCAP.min():.0f}〜{SOLCAP.max():.0f}MW）")

# ---------------------------------------------------------------- (B) 構造: 再エネを全部止めた後の余剰 E(h)
X_MAIN, P_PUMP = 570.0, 680.0
N_SC = {"なし": 0.0, "泊3号（820.8MW）": 912.0 * 0.9, "泊全基（1,680MW）": 1680.0}
DS_SC = [0, 50, 100, 150, 200]                                   # 自家消費の追加（万kW）
LNG_MIN, LNG_START = 569.4 * 0.2, 569.4 * 1_000 + 1_000_000      # MW、円
COAL_PER_MW_START, COAL_MIN_SHARE = 13_000.0, 0.3


def surplus(rows, ds, n, t_floor=T_FLOOR, x=X_MAIN):
    b = n + t_floor + HYM[rows] + BIOM[rows] + GEOM[rows]
    a = DEMM[rows] - ds * 1e4 / 1e3 * CFM[rows] + x + P_PUMP
    return b - a


def runlen(pos):
    """各日の E>0 の時間の、その時間が属する連続区間の長さ（時間）"""
    n, m = pos.shape
    pad = np.zeros((n, m + 1), np.int8)                          # 日の境界で区間を切る
    pad[:, :m] = pos
    d = np.diff(np.concatenate([[0], pad.ravel()]))
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    H = np.zeros(pad.size)
    for s, e in zip(starts, ends):
        H[s:e] = e - s
    return H.reshape(n, m + 1)[:, :m]


def stop_cost(E, H):
    """停止コスト（円/kWh、正の値）。最初の LNG_MIN は LNG、超える分は石炭（苫東厚真の 1 機あたり起動費/最低出力は容量によらず 43.3/H）"""
    h = np.maximum(H, 1.0)
    lng = LNG_START / (LNG_MIN * 1e3 * h)
    coal = COAL_PER_MW_START / (COAL_MIN_SHARE * 1e3 * h)
    return np.where(E <= LNG_MIN, lng, coal)


EV_ALL = np.where(m41["EV"])[0]                                  # FY2023〜25 の日
SUR = []
for tl, tf in (("主（出力制御のコマの火力5%点）", T_FLOOR), ("感応度（400MW）", 400.0)):
    for xl, xv in (("主（570MW）", X_MAIN), ("感応度（900MW）", 900.0)):
        if tl.startswith("感応度") and xl.startswith("感応度"):
            continue
        for nl, nv in N_SC.items():
            for ds in DS_SC:
                E = surplus(EV_ALL, ds, nv, tf, xv)
                pos = E > 0
                H = runlen(pos)
                c = stop_cost(E, H)
                yrs = len(EV_ALL) / 365
                SUR.append({"火力の床": tl, "北本の送電": xl, "原子力": nl, "自家消費の追加(万kW)": ds,
                            "火力の停止が要る時間(h/年)": pos.sum() / yrs, "同 日数(日/年)": pos.any(1).sum() / yrs,
                            "余剰の平均(MW)": E[pos].mean() if pos.any() else 0.0,
                            "余剰の最大(MW)": E.max() if pos.any() else 0.0,
                            "余剰の95%点(MW)": np.quantile(E[pos], 0.95) if pos.any() else 0.0,
                            "連続時間の平均(h)": H[pos].mean() if pos.any() else 0.0,
                            "停止コストの平均(円/kWh)": c[pos].mean() if pos.any() else 0.0,
                            "うち石炭が限界の割合": (E[pos] > LNG_MIN).mean() if pos.any() else 0.0,
                            "4〜6月の割合": (np.isin(DAYS[EV_ALL].month, [4, 5, 6])[:, None].repeat(24, 1)[pos]).mean() if pos.any() else 0.0})
SURD = pd.DataFrame(SUR)
SURD.round(3).to_csv(os.path.join(PROC, "curtailment_structure_surplus.csv"), index=False, encoding="utf-8-sig")
print("\n[B] 火力の停止が要る時間（h/年、FY2023〜25 の需給パターン、主: 火力の床・北本570MW）")
mm = SURD[(SURD["火力の床"].str.startswith("主")) & (SURD["北本の送電"].str.startswith("主"))]
print(mm.pivot_table(index="自家消費の追加(万kW)", columns="原子力", values="火力の停止が要る時間(h/年)", sort=False).round(0).to_string())
print("\n    余剰の最大（MW）")
print(mm.pivot_table(index="自家消費の追加(万kW)", columns="原子力", values="余剰の最大(MW)", sort=False).round(0).to_string())
print("\n    停止コストの平均（円/kWh、E>0 の時間）")
print(mm.pivot_table(index="自家消費の追加(万kW)", columns="原子力", values="停止コストの平均(円/kWh)", sort=False).round(1).to_string())
for lab in ("感応度（400MW）",):
    s2 = SURD[SURD["火力の床"] == lab]
    print(f"\n    火力の床 {lab}: 火力の停止が要る時間（h/年）")
    print(s2.pivot_table(index="自家消費の追加(万kW)", columns="原子力", values="火力の停止が要る時間(h/年)", sort=False).round(0).to_string())
s3 = SURD[SURD["北本の送電"] == "感応度（900MW）"]
print("\n    北本の送電 900MW: 火力の停止が要る時間（h/年）")
print(s3.pivot_table(index="自家消費の追加(万kW)", columns="原子力", values="火力の停止が要る時間(h/年)", sort=False).round(0).to_string())

# ---------------------------------------------------------------- (C) 蓄電池: E>0 の時間に −停止コスト を入れた価格での π(K)・K*
CRF20 = 0.06 * 1.06 ** 20 / (1.06 ** 20 - 1)
OM, NET_FIX = 5_300.0, 12 * (0.15 * 628.10 + 0.85 * 137.50) / 1.1
W_LOSS = 4 * 365 * 0.15 * (1.02 + 4.18) / 1.1
CAPEX = {"6.8万": 68_000.0, "4.0万": 40_000.0, "2.3万": 23_000.0}
CAPP = pd.read_csv(os.path.join(PROC, "capacity_price_of_k_v3.csv"))
KP = lambda K: np.interp(K, CAPP["K(万kW)"].to_numpy(float),
                         CAPP["κP 北海道ブロック按分・起点1.25万・2030年度向け近似（主）(円/kW-年)"].to_numpy(float))
K_EVAL = list(range(0, 101)) + list(range(105, 201, 5))


def run(sm, ds, n, negative=True, Ks=K_EVAL):
    net0 = NETM[BLK] - (sm - 1.0) * SOLM[BLK] - ds * 1e4 / 1e3 * CFM[BLK] - n
    E0 = surplus(BLK, ds, n)

    def price(adj):
        base = np.maximum(g_curve(adj, G26, SEASB) + MU26B, FLOOR)
        p = base                                               # θ=1
        if not negative:
            return p
        E = E0 - np.maximum(adj - net0, 0.0)                   # 蓄電池の充電は吸収できる量を増やす
        pos = E > 0
        if not pos.any():
            return p
        return np.where(pos, -stop_cost(E, runlen(pos)), p)

    adj, done, out = net0.copy(), 0.0, []
    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            pr = price(adj)
            o = np.argsort(pr, 1)
            chg, dis = o[:, :4], o[:, -4:]
            mg = np.take_along_axis(pr, dis, 1).sum(1) * ETA - np.take_along_axis(pr, chg, 1).sum(1)
            a = mg > 0
            adj[RB[a], chg[a]] += st * 10.0
            adj[RB[a], dis[a]] -= st * 10.0 * ETA
            done += st
        pr = price(adj)
        d = daily_eval(pr, W_B)
        out.append({"K(万kW)": K, "c": annual(d["c"], FYB, EVB), "負の時間(h/年)": float((pr[EVB] < 0).sum() / EVB.sum() * 365)})
    return pd.DataFrame(out)


LAM = C_ACT / run(1.0, 0, 0.0, False, [0])["c"].iloc[0]
assert abs(LAM - 1.1085) < 1e-3, LAM
print(f"\n[C] λ={LAM:.4f}（41 と同じ）")


def kstar(df, capex):
    K = df["K(万kW)"].to_numpy(float)
    slack = (LAM * df["c"] - W_LOSS).clip(lower=0).to_numpy() + KP(K) - (capex * 4 * CRF20 + OM + NET_FIX)
    if slack[0] < 0:
        return np.nan
    neg = np.where(slack < 0)[0]
    if len(neg) == 0:
        return float(K[-1])
    i = neg[0]
    return float(K[i - 1] + (K[i] - K[i - 1]) * slack[i - 1] / (slack[i - 1] - slack[i]))


KS = []
for sm in (1.0, 3.0):
    for nl, nv in N_SC.items():
        for ds in (0, 100, 200):
            res = {}
            for neg in (False, True):
                res[neg] = run(sm, ds, nv, neg)
            for neg, df in res.items():
                row = {"事業用太陽光の倍率": sm, "原子力": nl, "自家消費の追加(万kW)": ds,
                       "下限": "停止コストの負の価格" if neg else "現行（0.01円）",
                       "π(0)": LAM * df["c"].iloc[0] - W_LOSS, "π(50)": LAM * df.set_index("K(万kW)").loc[50, "c"] - W_LOSS,
                       "負の時間(h/年) K=0": df["負の時間(h/年)"].iloc[0],
                       "負の時間(h/年) K=50": df.set_index("K(万kW)").loc[50, "負の時間(h/年)"]}
                for ck, cv in CAPEX.items():
                    row[f"K*（{ck}）"] = kstar(df, cv)
                KS.append(row)
KSD = pd.DataFrame(KS)
KSD.round(3).to_csv(os.path.join(PROC, "curtailment_structure_kstar.csv"), index=False, encoding="utf-8-sig")
print(KSD.round(1).to_string(index=False))

# ---------------------------------------------------------------- 図
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8,
                     "xtick.labelsize": 8, "ytick.labelsize": 8})
fig, axes = plt.subplots(1, 2, figsize=(6.1, 2.8))
ax = axes[0]
for (nl, col) in zip(N_SC, ("#1f4e79", "#c55a11", "#c00000")):
    d = mm[mm["原子力"] == nl]
    ax.plot(d["自家消費の追加(万kW)"], d["火力の停止が要る時間(h/年)"], marker="o", ms=3.5, color=col, lw=1.4, label=f"原子力 {nl}")
ax.set_xlabel("自家消費の太陽光の追加（万kW）")
ax.set_ylabel("火力の停止が要る時間（h/年）")
ax.set_title("再エネを全部止めても余る時間")
ax.grid(alpha=0.3, lw=0.5)
ax.legend(frameon=False, loc="upper left")
ax = axes[1]
d = KSD[(KSD["事業用太陽光の倍率"] == 1.0)]
xs = np.arange(3)
w = 0.13
for j, nl in enumerate(N_SC):
    for k, (neg, hatch) in enumerate((("現行（0.01円）", ""), ("停止コストの負の価格", "//"))):
        y = [d[(d["原子力"] == nl) & (d["自家消費の追加(万kW)"] == ds) & (d["下限"] == neg)]["π(0)"].iloc[0] / 1e4 for ds in (0, 100, 200)]
        ax.bar(xs + (2 * j + k - 2.5) * w, y, w, color=("#1f4e79", "#c55a11", "#c00000")[j], alpha=1.0 if k else 0.45, hatch=hatch,
               edgecolor="white", lw=0.3)
ax.set_xticks(xs)
ax.set_xticklabels(["＋0", "＋100万kW", "＋200万kW"])
ax.set_xlabel("自家消費の追加（事業用太陽光は現状）")
ax.set_ylabel("限界参入者の収益 π(0)（万円/kW-年）")
ax.set_title("薄色: 0.01円の下限、濃色: 停止コストの負の価格")
ax.grid(axis="y", alpha=0.3, lw=0.5)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "curtailment_structure.png"), dpi=200)
plt.close(fig)
print("\n図: curtailment_structure.png")
