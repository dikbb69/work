#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""実行可能戦略の予測評価と取引ルールの検定（北海道 FY2023〜25）: Diebold-Mariano・SPA・capture率の区間

手法:
  1. 戦略の日次粗利（円/kW-日。4時間・往復効率0.85 を放電側に一括・1日1サイクル・60分粒度・持ち越しなし）。
     定義は analysis/16_strategy_decomposition.py と同一（コードを複製。16 は実行しない）:
       PF 完全予見（粗利が負の日は休止）／a 前日の実現価格ランク／a2 同じ曜日区分の直近日の価格ランク／
       b 予測残余需要ランク（需要は D−2 までの28日・平日休日別平均、太陽光は D−2 までの7日平均）／
       b' b からさらに風力の7日平均を控除（analysis/10 の fcst_w。7.2 の「風力の持続性シグナル」）／
       c 過去28日・同曜日区分の平均価格ランク（気候値）。
     追加: Diebold & Li (2006) 型の動的因子予測 DL1・DL3・DL5 と時刻別 AR(1)（AR）。c の気候値からの偏差
       e_t = p_t − 気候値_t を、過去365日（D−1 まで。前日価格は D の入札締切時に既知）の偏差の主成分で
       K 因子に縮約し、因子ごとの AR(1) で当日に持ち越す: 予測_D = 気候値_D + ē + Σ_{k≤K} v_k·φ_k·f_k(D−1)。
       Diebold-Li の Nelson-Siegel 負荷の代わりに主成分の負荷を使う2段階法。負荷・平均・φ は日ごとに再推定し、
       先読みはない。AR は時刻ごとの AR(1)（予測_D,h = 気候値_D,h + ē_h + φ_h·(e_{D−1,h} − ē_h)）。
     同値の扱い: ランクに使う信号の4位と5位（20位と21位）が同値の日は、同値の時間帯に充放電量を均等に配分する
       （同値から無作為に選ぶ場合の期待値に等しく、出力1kW・4kWh の制約を満たす）。この規則で表7.2 の
       a（68.0〜69.3%）を再現する。16 の実装（pandas の既定ソート）は同値の選び方が numpy の版と CPU に依存し、
       この環境（numpy 2.5・arm64）では a が 67.9〜69.2% になる（同値を最も不利／有利に選ぶと 66.5〜70.7%）。
       境界の同値は a・a2 で FY2023〜25 の219日、b' で1日、b・c・DL・AR で0日。
  2. Diebold & Mariano (1995) 検定: 損失差 d_t＝粗利の差（円/kW-日）、長期分散は Newey-West（Bartlett、
     ラグ7を主・0/14を感度）、Harvey, Leybourne & Newbold (1997) の小標本補正（h=1）と t(T−1)。プールと年度別。
     DL・AR は365日の固定長ローリング推定なので、推定誤差を含めた無条件の予測力の比較になる（Giacomini & White 2006）。
     対比として、信号が価格カーブの予測になっている戦略（a・c・DL・AR）について、時間別価格・日平均（水準）・
     日内形状（日平均を除いたカーブ）の二乗誤差でも DM 検定を行う（統計的な精度と経済的な価値の乖離、
     Leitch & Tanner 1991）。価格の二乗誤差＝日平均の二乗誤差＋形状の二乗誤差 が日ごとに恒等的に成り立つ。
  3. データ・スヌーピングを考慮した Hansen (2005) の SPA 検定（p_l・p_c・p_u）と White (2000) の Reality Check。
     候補は戦略9本（a・a2・b・b'・c・DL1・DL3・DL5・AR）から基準を除く8本。基準は a・b・c。
     ブートストラップは Politis & Romano (1994) の定常ブートストラップ（循環。日の添字を全戦略で共通に再標本化。
     平均ブロック長は Politis & White (2004)・Patton, Politis & White (2009) の自動選択を、損失差の全ペアと
     capture率・その差を線形化した系列（x_t − R·PF_t）に当てた最大値を切り上げる（現データで20日）。B=10,000）。
     年度別の検定にも同じ平均ブロック長を使う。
     SPA の分散 ω_k² は定常ブートストラップに対応するカーネル推定量（Hansen 2005 の式）。
     補足として Hansen, Lunde & Nason (2011) のモデル信頼集合（範囲統計量 T_R と T_max の両方を報告する。
     T_max を先に計算し、T_R を後から加えたので、どちらかを主とはしない。同じブートストラップ標本）。
     p 値は T*≥T の割合（T_SPA=0、すなわち基準を上回る候補がないときは p=1）。
     選択の偏り（勝者の呪い）の確認: 同じブートストラップ標本で、9本のうち c の capture率が最大になる割合と、
     最大の capture率のブートストラップ平均 − 点推定の最大値（選択による上方の偏りの推定）を出す。
  4. capture率（Σ戦略/ΣPF）とその差の95%区間: 定常ブートストラップのパーセンタイル区間（主）と、
     Carlstein (1986) 型の非重複固定ブロック（7日）の区間（パイロット p3 の再現）。
  5. θ* の下限: 8.4・9.4 の式 θ* = (c_req − κP_cap + 充電従量負担) / (c·裾の補正·π_PF(0)) で、capture=1 と
     裾の補正（実績の完全予見粗利 ÷ モデルの π_PF(0)）を同時に置いても θ* が FY2022 の水準を上回るかを確認する。
     π_PF(0) は data/processed/equilibrium_surface.csv（28 の出力）、θ_FY は price_level_theta.csv（26 の出力）を読む。
     あわせて、FY2022 の実績の完全予見粗利（本スクリプトで計算、25,160円/kW-年）をそのまま使った場合の実現可能収益
     （capture × 25,160 − 充電従量負担）と、参入必要収益に届くのに必要な capture を出す。モデルの θ と裾の補正×1.248
     は FY2023〜25 の分断構造を前提とするので、FY2022 の実績（連系線増強前の厚い裾）は別に確認する必要がある。
出力: data/processed/strategy_tests.csv（DM・二乗誤差の DM・SPA・RC・MCS・選択の偏り・区間）、
      strategy_daily_margins.csv（日次粗利）、
      strategy_capture_annual.csv（年度別の価値と capture率、FY2016〜25、同値の扱いの感度を含む）、
      strategy_theta_bounds.csv（θ* の下限と FY2022 実績での確認）、figures/hokkaido/strategy_capture_ci.png
限界: 検定が示すのは試した単純戦略の間の順位であり、capture率0.81 という水準の妥当性ではない。前日スポットでは
     24時間が同時に約定するので、価格条件付きの入札（指値・ブロック入札）はランク法より高い capture を取りうる。
     DL・AR の価格予測としての精度（二乗誤差）は対比のために示すだけで、取引戦略の評価は粗利で行う。
     θ* の下限はモデルの水準係数で比べており、FY2022 の実績の分断構造（裾）はモデルに入っていない。FY2022 の実績を
     そのまま使うと、capture を高く置くほど参入に届くケースが増える（楽観ケースは capture≥0.845 で届く）。
     1日1サイクル・充放電順序の制約なしは 16 と同じ（DP との差は原稿 7.2 で −0.3〜−1.7%）。
"""
import logging
import os

import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import font_manager
import matplotlib.pyplot as plt

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY = "#595959"

ETA = 0.85
HOURS = 4
SEED = 20261020
B = 10_000
FYS = [2023, 2024, 2025]
DL_WINDOW = 365
NW_LAGS = (0, 7, 14)
NW_MAIN = 7
STRATS = ["a", "a2", "b", "b2", "c", "DL1", "DL3", "DL5", "AR"]     # b2 = b'
PRICE_FC = ["a", "a2", "c", "DL1", "DL3", "DL5", "AR"]             # 信号が当日の価格カーブの予測になっている戦略
LABEL = {"pf": "PF", "a": "a", "a2": "a2", "b": "b", "b2": "b'", "c": "c",
         "DL1": "DL1", "DL3": "DL3", "DL5": "DL5", "AR": "AR"}
LONG = {"a": "a. 前日の実現価格ランク", "a2": "a2. 同じ曜日区分の直近日", "b": "b. 残余需要の予測ランク",
        "b2": "b'. b＋風力の7日平均", "c": "c. 28日・同曜日区分の平均価格（気候値）",
        "DL1": "DL1. 動的因子予測（1因子）", "DL3": "DL3. 動的因子予測（3因子）",
        "DL5": "DL5. 動的因子予測（5因子）", "AR": "AR. 時刻別 AR(1)"}
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------- データ（16 と同一）
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
D = hp.pivot(index="day", columns="hour", values="demand")
S = hp.pivot(index="day", columns="hour", values="solar")
W = hp.pivot(index="day", columns="hour", values="wind")
days = P.index
all_days = D.index
PA, DA, SA, WA = (x.to_numpy(float) for x in (P, D, S, W))
wkP = np.asarray(days.dayofweek >= 5)
wkA = np.asarray(all_days.dayofweek >= 5)
pos_all = all_days.get_indexer(days)
fy_of = np.asarray(days.year - (days.month < 4).astype(int))


# ---------------------------------------------------------------- 粗利の計算
def tie_weights(sig, k=HOURS):
    """信号の下位 k 時間の重み。境界の同値は均等に配分する（無作為に選ぶ場合の期待値）"""
    thr = np.sort(sig)[k - 1]
    w = (sig < thr).astype(float)
    tied = sig == thr
    w[tied] = (k - w.sum()) / tied.sum()
    return w


def margin(p, sig):
    """信号のランクで充放電する日の粗利（円/kW-日）"""
    return ETA * (tie_weights(-sig) @ p) - tie_weights(sig) @ p


def margin_order(p, order):
    return ETA * p[order[-HOURS:]].sum() - p[order[:HOURS]].sum()


def boundary_tie(sig):
    q = np.sort(sig)
    return bool(q[HOURS - 1] == q[HOURS] or q[-HOURS] == q[-HOURS - 1])


def envelope(p, sig, best):
    """境界の同値を当日の価格で最も有利（best=True）／不利に選んだ場合の粗利"""
    def pick(s, low):
        s_ = s if low else -s
        thr = np.sort(s_)[HOURS - 1]
        strict = np.where(s_ < thr)[0]
        tied = np.where(s_ == thr)[0]
        key = p[tied] if low else -p[tied]
        o = np.argsort(key, kind="stable") if best else np.argsort(-key, kind="stable")
        return np.concatenate([strict, tied[o[:HOURS - len(strict)]]])
    return ETA * p[pick(sig, False)].sum() - p[pick(sig, True)].sum()


# 気候値（戦略 c の信号）と偏差
clim = np.full_like(PA, np.nan)
for i in range(len(days)):
    hist = [j for j in range(max(0, i - 29), i) if wkP[j] == wkP[i]]
    if len(hist) >= 5:
        clim[i] = PA[hist].mean(axis=0)
dev = PA - clim

rows, ties = [], []
dl_info = []
for i in range(len(days)):
    p = PA[i]
    srt = np.sort(p)
    rec = {"day": days[i], "fy": fy_of[i], "pf": max(0.0, ETA * srt[-HOURS:].sum() - srt[:HOURS].sum())}
    sigs = {}
    if i >= 1:
        sigs["a"] = PA[i - 1]
    prev_same = [j for j in range(max(0, i - 8), i) if wkP[j] == wkP[i]]
    if prev_same:
        sigs["a2"] = PA[prev_same[-1]]
    if not np.isnan(clim[i]).any():
        sigs["c"] = clim[i]
    jj = pos_all[i]
    if jj >= 30:
        hist = range(max(0, jj - 29), jj - 1)                    # D−2 まで
        same = [h for h in hist if wkA[h] == wkA[jj]]
        if len(same) >= 5:
            dem_f = DA[same].mean(axis=0)
            win7 = range(jj - 8, jj - 1)                           # 直近7日（D−2 まで）
            sol_f = SA[list(win7)].mean(axis=0)
            sigs["b"] = dem_f - sol_f
            sigs["b2"] = dem_f - sol_f - np.nanmean(WA[list(win7)], axis=0)
    # Diebold-Li 型（FY2023〜25 のみ。推定窓は D−365〜D−1、FY2022 を含む）
    if fy_of[i] >= 2023 and "c" in sigs:
        H = dev[i - DL_WINDOW:i]
        H = H[~np.isnan(H).any(axis=1)]
        mu = H.mean(axis=0)
        Hc = H - mu
        ev, V = np.linalg.eigh(Hc.T @ Hc / (len(Hc) - 1))
        o = np.argsort(ev)[::-1]
        ev, V = ev[o], V[:, o]
        F = Hc @ V
        phi = (F[1:] * F[:-1]).sum(axis=0) / (F[:-1] ** 2).sum(axis=0)
        phih = (Hc[1:] * Hc[:-1]).sum(axis=0) / (Hc[:-1] ** 2).sum(axis=0)
        s_prev = (dev[i - 1] - mu) @ V
        for K in (1, 3, 5):
            sigs[f"DL{K}"] = clim[i] + mu + V[:, :K] @ (phi[:K] * s_prev[:K])
        sigs["AR"] = clim[i] + mu + phih * (dev[i - 1] - mu)
        dl_info.append({"day": days[i], **{f"φ{k+1}": phi[k] for k in range(5)},
                        **{f"寄与率{k+1}": ev[k] / ev.sum() for k in range(5)}, "φ_時刻別_平均": phih.mean()})
    for k, s in sigs.items():
        rec[k] = margin(p, s)
        ties.append({"day": days[i], "fy": fy_of[i], "戦略": k, "境界の同値": boundary_tie(s)})
        if k in PRICE_FC:                                           # 信号が価格の予測であるもの
            rec[f"mse_{k}"] = float(((p - s) ** 2).mean())
            rec[f"mse形状_{k}"] = float((((p - p.mean()) - (s - s.mean())) ** 2).mean())
            rec[f"mse水準_{k}"] = float((p.mean() - s.mean()) ** 2)          # 価格＝水準＋形状 の恒等式
    for k in ("a", "a2"):
        if k in sigs:
            rec[f"{k}_既定ソート"] = margin_order(p, np.argsort(sigs[k]))          # 16 の実装（pandas 既定）と同じ
            rec[f"{k}_時刻順"] = margin_order(p, np.argsort(sigs[k], kind="stable"))
            rec[f"{k}_同値最不利"] = envelope(p, sigs[k], False)
            rec[f"{k}_同値最有利"] = envelope(p, sigs[k], True)
    rows.append(rec)

bt = pd.DataFrame(rows)
ties = pd.DataFrame(ties)
dl_info = pd.DataFrame(dl_info)
CORE = ["pf", "a", "a2", "c", "b"]                 # 16 の共通標本の定義

# ---------------------------------------------------------------- 年度別の価値と capture率（FY2016〜25）
ann_rows = []
for fy, g0 in bt[bt["fy"].between(2016, 2025)].groupby("fy"):
    g = g0.dropna(subset=CORE)
    r = {"FY": fy, "日数": len(g), "PF(円/kW-年)": g["pf"].sum()}
    gc = g0.dropna(subset=["pf", "c"])           # c が定義される全日（共通標本でない）
    r["c_自標本の日数"] = len(gc)
    r["capture_c_自標本(%)"] = gc["c"].sum() / gc["pf"].sum() * 100
    for k in ["a", "a2", "b", "b2", "c", "DL1", "DL3", "DL5", "AR",
              "a_既定ソート", "a_時刻順", "a_同値最不利", "a_同値最有利", "a2_既定ソート", "a2_時刻順"]:
        if k in g and g[k].notna().all():
            r[f"{LABEL.get(k, k)}(円/kW-年)"] = g[k].sum()
            r[f"capture_{LABEL.get(k, k)}(%)"] = g[k].sum() / g["pf"].sum() * 100
    ann_rows.append(r)
ann = pd.DataFrame(ann_rows)
ann.round(2).to_csv(os.path.join(PROC, "strategy_capture_annual.csv"), index=False, encoding="utf-8-sig")

est = bt[bt["fy"].isin(FYS)].dropna(subset=["pf"] + STRATS).reset_index(drop=True)
assert len(est) == len(bt[bt["fy"].isin(FYS)]), "FY2023-25 に戦略の欠ける日がある"
est[["day", "fy", "pf"] + STRATS].round({k: 4 for k in ["pf"] + STRATS}).rename(columns={"b2": "b'"}).to_csv(
    os.path.join(PROC, "strategy_daily_margins.csv"), index=False, encoding="utf-8-sig")

print("=== 再現: 表7.1（完全予見粗利、円/kW-年）と表7.2（capture率、%）、FY2023〜25 ===")
show = ann[ann["FY"].isin(FYS)].set_index("FY")
print(show[["PF(円/kW-年)"]].round(0).T.to_string())
cols = [f"capture_{LABEL[k]}(%)" for k in STRATS]
print(show[cols].round(2).to_string())
print("a の同値の扱い（%）:")
print(show[["capture_a(%)", "capture_a_既定ソート(%)", "capture_a_時刻順(%)", "capture_a_同値最不利(%)",
            "capture_a_同値最有利(%)", "capture_a2(%)", "capture_a2_既定ソート(%)"]].round(2).to_string())
tie_tab = ties[ties["fy"].isin(FYS)].groupby("戦略")["境界の同値"].agg(["sum", "count"])
print("境界の同値がある日数（FY2023〜25）:", tie_tab["sum"].to_dict())
print("\n=== FY2016〜25 の capture率（%、16 の共通標本） ===")
print(ann.set_index("FY")[["日数", "capture_a(%)", "capture_a2(%)", "capture_b(%)", "capture_b'(%)", "capture_c(%)",
                           "c_自標本の日数", "capture_c_自標本(%)"]]
      .round(1).to_string())
print("\nDL の推定値（FY2023〜25 の平均）:", dl_info.drop(columns="day").mean().round(3).to_dict())


# ---------------------------------------------------------------- Diebold-Mariano
def nw_lrv(x, L):
    x = x - x.mean()
    T = len(x)
    s = x @ x / T
    for j in range(1, L + 1):
        s += 2 * (1 - j / (L + 1)) * (x[j:] @ x[:-j] / T)
    return s


def dm_test(d, L):
    T = len(d)
    stat = d.mean() / np.sqrt(nw_lrv(d, L) / T)
    stat_hln = stat * np.sqrt((T + 1 - 2 * 1 + 1 * 0 / T) / T)      # HLN 補正（h=1）
    return stat, 2 * stats.norm.sf(abs(stat)), stat_hln, 2 * stats.t.sf(abs(stat_hln), T - 1)


PAIRS = [("c", "b"), ("c", "a"), ("b", "a"), ("a2", "a"), ("c", "a2"), ("b2", "b"), ("c", "b2"),
         ("DL1", "c"), ("DL3", "c"), ("DL5", "c"), ("AR", "c"), ("DL3", "b"), ("DL3", "a")]
scopes = [("FY2023-25", est)] + [(f"FY{fy}", g.reset_index(drop=True)) for fy, g in est.groupby("fy")]
dm_rows = []
for scope, g in scopes:
    nfy = g["fy"].nunique()
    for x, y in PAIRS:
        d = (g[x] - g[y]).to_numpy()
        for L in NW_LAGS:
            s, p, sh, ph = dm_test(d, L)
            dm_rows.append({"区分": "DM", "期間": scope, "比較": f"{LABEL[x]} − {LABEL[y]}", "日数": len(d),
                            "NWラグ": L, "年平均差(円/kW-年)": d.sum() / nfy,
                            "capture差(pt)": d.sum() / g["pf"].sum() * 100,
                            "差のρ1": float(np.corrcoef(d[1:], d[:-1])[0, 1]),
                            "DM": s, "p": p, "DM_HLN": sh, "p_HLN": ph})
dm = pd.DataFrame(dm_rows)

# 統計的な予測精度（二乗誤差）との対比: 価格カーブの予測としての DM（負なら c より誤差が小さい）
mse_rows = []
for scope, g in scopes:
    for loss, lab in (("mse", "DM（価格の二乗誤差）"), ("mse水準", "DM（日平均の二乗誤差）"),
                      ("mse形状", "DM（日内形状の二乗誤差）")):
        for x in ["a", "DL1", "DL3", "DL5", "AR"]:
            d = (g[f"{loss}_{x}"] - g[f"{loss}_c"]).to_numpy()
            s_, p_, sh, ph = dm_test(d, NW_MAIN)
            mse_rows.append({"区分": lab, "期間": scope, "比較": f"{LABEL[x]} − c", "日数": len(d), "NWラグ": NW_MAIN,
                             "差のρ1": float(np.corrcoef(d[1:], d[:-1])[0, 1]), "DM": s_, "p": p_, "DM_HLN": sh,
                             "p_HLN": ph, "点推定": d.mean(), "損失の相対差(%)": d.mean() / g[f"{loss}_c"].mean() * 100})
msedf = pd.DataFrame(mse_rows)


# ---------------------------------------------------------------- 定常ブートストラップ
def pw_block_sb(x):
    """Politis & White (2004)、Patton, Politis & White (2009) の定常ブートストラップの最適平均ブロック長"""
    x = np.asarray(x, float)
    n = len(x)
    e = x - x.mean()
    kn = max(5, int(np.ceil(np.sqrt(np.log10(n)))))
    m_max = int(np.ceil(np.sqrt(n))) + kn
    b_max = np.ceil(min(3 * np.sqrt(n), n / 3))
    acv = np.array([e[k:] @ e[:n - k] / n for k in range(m_max + kn + 1)])
    rho = acv / acv[0]
    thr = 2 * np.sqrt(np.log10(n) / n)
    m_hat = m_max
    for m in range(0, m_max + 1):
        if np.all(np.abs(rho[m + 1:m + kn + 1]) < thr):
            m_hat = m
            break
    M = min(2 * max(m_hat, 1), m_max)
    k = np.arange(1, M + 1)
    lam = np.where(k / M <= 0.5, 1.0, 2 * (1 - k / M))
    g0 = acv[0] + 2 * (lam * acv[1:M + 1]).sum()
    G = 2 * (lam * k * acv[1:M + 1]).sum()
    b = (2 * G ** 2 / (2 * g0 ** 2)) ** (1 / 3) * n ** (1 / 3)
    return float(min(b, b_max))


def sb_means(X, mean_block, B, rng, chunk=500):
    """定常ブートストラップ（循環）で各列の標本平均を B 回再標本化する"""
    n = X.shape[0]
    q = 1.0 / mean_block
    out = np.empty((B, X.shape[1]))
    for s in range(0, B, chunk):
        bb = min(chunk, B - s)
        idx = np.empty((bb, n), dtype=np.int64)
        idx[:, 0] = rng.integers(0, n, bb)
        new = rng.random((bb, n)) < q
        jump = rng.integers(0, n, (bb, n))
        for t in range(1, n):
            idx[:, t] = np.where(new[:, t], jump[:, t], (idx[:, t - 1] + 1) % n)
        cnt = np.bincount((np.arange(bb)[:, None] * n + idx).ravel(), minlength=bb * n).reshape(bb, n)
        out[s:s + bb] = cnt @ X / n
    return out


def nbb_means(X, block, B, rng):
    """Carlstein (1986) 型の非重複固定ブロック（末尾の短いブロックも1本として扱う、パイロット p3 と同じ）"""
    n = X.shape[0]
    nb = int(np.ceil(n / block))
    sums = np.array([X[k * block:(k + 1) * block].sum(axis=0) for k in range(nb)])
    lens = np.array([min(block, n - k * block) for k in range(nb)])
    ix = rng.integers(0, nb, (B, nb))
    return sums[ix].sum(axis=1) / lens[ix].sum(axis=1)[:, None]


def sb_omega2(x, q):
    """定常ブートストラップに対応する長期分散のカーネル推定量（Hansen 2005、Politis & Romano 1994）"""
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(np.r_[x, np.zeros(n)])
    ac = np.fft.irfft(f * np.conj(f))[:n] / n
    i = np.arange(1, n)
    kap = ((n - i) / n) * (1 - q) ** i + (i / n) * (1 - q) ** (n - i)
    return ac[0] + 2 * (kap * ac[1:]).sum()


def spa_rc(X, Mbar, Mstar, names, bench, mean_block):
    """Hansen (2005) SPA（p_l, p_c, p_u）と White (2000) RC。d_k = π_k − π_基準（正なら候補が上回る）"""
    n = X.shape[0]
    q = 1.0 / mean_block
    k0 = names.index(bench)
    ks = [j for j, nm in enumerate(names) if nm in STRATS and j != k0]
    dbar = Mbar[ks] - Mbar[k0]
    dstar = Mstar[:, ks] - Mstar[:, [k0]]
    om = np.sqrt([sb_omega2(X[:, j] - X[:, k0], q) for j in ks])
    tst = np.sqrt(n) * dbar / om
    T = max(0.0, tst.max())
    thr = -np.sqrt(om ** 2 / n * 2 * np.log(np.log(n)))
    p = {}
    for key, gk in (("l", np.maximum(dbar, 0)), ("c", dbar * (dbar >= thr)), ("u", dbar)):
        Tst = np.maximum(0.0, (np.sqrt(n) * (dstar - gk) / om).max(axis=1))
        p[key] = float((Tst >= T).mean())      # T=0（基準を上回る候補なし）なら p=1
    Vrc = np.sqrt(n) * dbar.max()
    Vst = (np.sqrt(n) * (dstar - dbar)).max(axis=1)
    return {"T_SPA": T, "p_SPA_l": p["l"], "p_SPA_c": p["c"], "p_SPA_u": p["u"], "p_RC": float((Vst >= Vrc).mean()),
            "最良候補(t)": LABEL[names[ks[int(np.argmax(tst))]]], "最良候補の年平均差(円/kW-年)": None,
            "_best_j": ks[int(np.argmax(tst))]}


def mcs(Mbar, Mstar, names, stat="T_R"):
    """Hansen, Lunde & Nason (2011) のモデル信頼集合（損失＝−粗利）。各戦略の MCS p 値と除外順を返す。
    stat="T_R": 範囲統計量 max_{i,j}|t_ij|、除外は max_j t_ij が最大の戦略。stat="T_max": 集合平均との差の t の最大値"""
    alive = [j for j, nm in enumerate(names) if nm in STRATS]
    pval, pmax, order = {}, 0.0, []
    while len(alive) > 1:
        Lb = -Mbar[alive]
        Ls = -Mstar[:, alive]
        if stat == "T_max":
            db = Lb - Lb.mean()
            ds = Ls - Ls.mean(axis=1, keepdims=True) - db
            sd = np.sqrt((ds ** 2).mean(axis=0))
            t = db / sd
            p = float(((ds / sd).max(axis=1) >= t.max()).mean())
            worst = alive[int(np.argmax(t))]
        else:
            dij = Lb[:, None] - Lb[None, :]
            dsij = Ls[:, :, None] - Ls[:, None, :] - dij
            sd = np.sqrt((dsij ** 2).mean(axis=0))
            np.fill_diagonal(sd, np.inf)
            tij = dij / sd
            p = float((np.abs(dsij / sd).max(axis=(1, 2)) >= np.abs(tij).max()).mean())
            worst = alive[int(np.argmax(tij.max(axis=1)))]
        pmax = max(pmax, p)
        pval[names[worst]] = pmax
        order.append(names[worst])
        alive.remove(worst)
    pval[names[alive[0]]] = 1.0
    order.append(names[alive[0]])
    return pval, order


NAMES = ["pf"] + STRATS
# 平均ブロック長: 検定・区間が依存する系列に PW 法を当てた最大値を切り上げる。
#   SPA・MCS は損失差（全ペア）、capture率 R=Σx/Σpf は線形化した系列 x_t − R·pf_t、
#   capture差 Δ=(Σx−Σy)/Σpf は (x_t − y_t) − Δ·pf_t（完全予見粗利の水準そのものの持続性は比には入らない）
bl = {f"{LABEL[x]}−{LABEL[y]}": pw_block_sb(est[x] - est[y]) for i_, x in enumerate(STRATS) for y in STRATS[i_ + 1:]}
for k in STRATS:
    R = est[k].sum() / est["pf"].sum()
    bl[f"cap_{LABEL[k]}"] = pw_block_sb(est[k] - R * est["pf"])
for x, y in [("c", "b"), ("c", "a"), ("b", "a"), ("a2", "a"), ("b2", "b"), ("DL1", "c"), ("DL3", "c"), ("DL5", "c"), ("AR", "c")]:
    dlt = (est[x].sum() - est[y].sum()) / est["pf"].sum()
    bl[f"capdiff_{LABEL[x]}−{LABEL[y]}"] = pw_block_sb(est[x] - est[y] - dlt * est["pf"])
BL_PF = pw_block_sb(est["pf"])
MEAN_BLOCK = int(np.ceil(max(bl.values())))
print(f"\n=== 定常ブートストラップの平均ブロック長（PW 法）: 最大 {max(bl.values()):.1f} 日 → {MEAN_BLOCK} 日 ===")
print({k: round(v, 1) for k, v in sorted(bl.items(), key=lambda kv: -kv[1])[:10]}, "…")
print(f"（参考: 完全予見粗利の水準の系列そのものは {BL_PF:.1f} 日。比の区間には入らないので使わない）")

boot = {}
for scope, g in scopes:
    X = g[NAMES].to_numpy()
    boot[scope] = (X, X.mean(axis=0), sb_means(X, MEAN_BLOCK, B, rng))

test_rows = []
for scope, g in scopes:
    X, Mbar, Mstar = boot[scope]
    nfy = g["fy"].nunique()
    for bench in ("a", "b", "c"):
        r = spa_rc(X, Mbar, Mstar, NAMES, bench, MEAN_BLOCK)
        j = r.pop("_best_j")
        r["最良候補の年平均差(円/kW-年)"] = (Mbar[j] - Mbar[NAMES.index(bench)]) * len(X) / nfy
        test_rows.append({"区分": "SPA・RC", "期間": scope, "基準": LABEL[bench], "候補数": len(STRATS) - 1,
                          "日数": len(X), "平均ブロック長": MEAN_BLOCK, "B": B, **r})
# ブロック長の感度（プール）
X, Mbar, _ = boot["FY2023-25"]
for mb in (7, 14, 28):
    Mst = sb_means(X, mb, B, rng)
    for bench in ("b", "c"):
        r = spa_rc(X, Mbar, Mst, NAMES, bench, mb)
        r.pop("_best_j")
        test_rows.append({"区分": "SPA・RC（ブロック長の感度）", "期間": "FY2023-25", "基準": LABEL[bench],
                          "候補数": len(STRATS) - 1, "日数": len(X), "平均ブロック長": mb, "B": B, **r})
spa = pd.DataFrame(test_rows)

mcs_rows = []
for scope, g in scopes:
    X, Mbar, Mstar = boot[scope]
    for st in ("T_R", "T_max"):
        pv, order = mcs(Mbar, Mstar, NAMES, st)
        for k in STRATS:
            mcs_rows.append({"区分": f"MCS（{st}）", "期間": scope, "比較": LABEL[k], "日数": len(X),
                             "平均ブロック長": MEAN_BLOCK, "B": B, "MCS_p": pv[k], "除外順": order.index(k) + 1,
                             "MCS90に残る": pv[k] >= 0.10, "MCS75に残る": pv[k] >= 0.25})
mcsdf = pd.DataFrame(mcs_rows)

# 選択の偏り（勝者の呪い）: 同じブートストラップ標本で、9本の capture率の最大がどれか、最大値の偏り
sel_rows = []
for scope, g in scopes:
    X, Mbar, Mstar = boot[scope]
    js = [NAMES.index(k) for k in STRATS]
    capb = Mstar[:, js] / Mstar[:, [0]] * 100
    capp = Mbar[js] / Mbar[0] * 100
    sel_rows.append({"区分": "選択の偏り", "期間": scope, "比較": "c が9本の中で最大になる割合", "日数": len(X),
                     "平均ブロック長": MEAN_BLOCK, "B": B, "点推定": float((capb.argmax(axis=1) == STRATS.index("c")).mean())})
    sel_rows.append({"区分": "選択の偏り", "期間": scope, "比較": "最大の capture率（%）: 点推定とブートストラップ分布",
                     "日数": len(X), "平均ブロック長": MEAN_BLOCK, "B": B, "点推定": float(capp.max()),
                     "下限95": np.percentile(capb.max(axis=1), 2.5), "上限95": np.percentile(capb.max(axis=1), 97.5)})
    sel_rows.append({"区分": "選択の偏り", "期間": scope, "比較": "最大の capture率の偏り（ブートストラップ平均 − 点推定、pt）",
                     "日数": len(X), "平均ブロック長": MEAN_BLOCK, "B": B, "点推定": float(capb.max(axis=1).mean() - capp.max())})
seldf = pd.DataFrame(sel_rows)

# ---------------------------------------------------------------- capture率とその差の区間
DIFFS = [("c", "b"), ("c", "a"), ("c", "a2"), ("c", "b2"), ("b", "a"), ("a2", "a"), ("b2", "b"),
         ("DL1", "c"), ("DL3", "c"), ("DL5", "c"), ("AR", "c"), ("DL3", "b")]
ci_rows = []
for scope, g in scopes:
    X, Mbar, Mstar = boot[scope]
    Mnbb = nbb_means(X, 7, B, rng)
    nfy = g["fy"].nunique()
    ix = {k: NAMES.index(k) for k in NAMES}
    for how, Ms in (("定常ブートストラップ", Mstar), ("非重複固定ブロック7日（Carlstein 型）", Mnbb)):
        mb = MEAN_BLOCK if how.startswith("定常") else 7
        for k in STRATS:
            pt = Mbar[ix[k]] / Mbar[0] * 100
            dist = Ms[:, ix[k]] / Ms[:, 0] * 100
            ci_rows.append({"区分": "区間: capture率(%)", "期間": scope, "比較": LABEL[k], "日数": len(X), "方式": how,
                            "平均ブロック長": mb, "B": B, "点推定": pt,
                            "下限95": np.percentile(dist, 2.5), "上限95": np.percentile(dist, 97.5)})
        for x, y in DIFFS:
            pt = (Mbar[ix[x]] - Mbar[ix[y]]) / Mbar[0] * 100
            dist = (Ms[:, ix[x]] - Ms[:, ix[y]]) / Ms[:, 0] * 100
            ci_rows.append({"区分": "区間: capture差(pt)", "期間": scope, "比較": f"{LABEL[x]} − {LABEL[y]}",
                            "日数": len(X), "方式": how, "平均ブロック長": mb, "B": B, "点推定": pt,
                            "下限95": np.percentile(dist, 2.5), "上限95": np.percentile(dist, 97.5)})
            dist_y = (Ms[:, ix[x]] - Ms[:, ix[y]]) * len(X) / nfy
            ci_rows.append({"区分": "区間: 年平均差(円/kW-年)", "期間": scope, "比較": f"{LABEL[x]} − {LABEL[y]}",
                            "日数": len(X), "方式": how, "平均ブロック長": mb, "B": B,
                            "点推定": (Mbar[ix[x]] - Mbar[ix[y]]) * len(X) / nfy,
                            "下限95": np.percentile(dist_y, 2.5), "上限95": np.percentile(dist_y, 97.5)})
ci = pd.DataFrame(ci_rows)

out = pd.concat([dm, msedf, spa, mcsdf, seldf, ci], ignore_index=True)
order_cols = ["区分", "期間", "比較", "基準", "候補数", "日数", "NWラグ", "年平均差(円/kW-年)", "capture差(pt)", "差のρ1",
              "DM", "p", "DM_HLN", "p_HLN", "T_SPA", "p_SPA_l", "p_SPA_c", "p_SPA_u", "p_RC", "最良候補(t)",
              "最良候補の年平均差(円/kW-年)", "MCS_p", "除外順", "MCS90に残る", "MCS75に残る",
              "方式", "平均ブロック長", "B", "点推定", "下限95", "上限95", "損失の相対差(%)"]
out = out[order_cols]
for c_ in ("候補数", "日数", "NWラグ", "除外順", "平均ブロック長", "B"):
    out[c_] = out[c_].astype("Int64")
out.to_csv(os.path.join(PROC, "strategy_tests.csv"), index=False, encoding="utf-8-sig", float_format="%.6g")

print(f"\n=== Diebold-Mariano（NW ラグ{NW_MAIN}） ===")
print(dm[dm["NWラグ"] == NW_MAIN].drop(columns=["区分", "NWラグ"]).round(3).to_string(index=False))
print("\nラグ感度（FY2023-25、DM）:")
print(dm[dm["期間"] == "FY2023-25"].pivot(index="比較", columns="NWラグ", values="DM").round(2).to_string())
print("\n=== 価格カーブの予測としての精度（二乗誤差、(円/kWh)²）: X − c、NW ラグ7 ===")
print(msedf[["区分", "期間", "比較", "点推定", "損失の相対差(%)", "DM", "p"]].round(3).to_string(index=False))
print("\n=== SPA（Hansen 2005）・Reality Check（White 2000） ===")
print(spa.drop(columns=["区分", "候補数", "B"]).round(4).to_string(index=False))
print("\n=== モデル信頼集合（Hansen, Lunde & Nason 2011。T_R を主、T_max を感度、MCS p 値） ===")
print(mcsdf.pivot_table(index="比較", columns=["区分", "期間"], values="MCS_p").round(4).to_string())
print("\n=== 選択の偏り（9本の中の最大の capture率） ===")
print(seldf[["期間", "比較", "点推定", "下限95", "上限95"]].round(4).to_string(index=False))
print("\n=== capture率と差の95%区間 ===")
print(ci[ci["期間"] == "FY2023-25"].drop(columns=["区分", "期間", "日数", "B"]).round(2).to_string(index=False))
print(ci[(ci["期間"] != "FY2023-25") & (ci["方式"] == "定常ブートストラップ") & (ci["区分"] != "区間: 年平均差(円/kW-年)")]
      .drop(columns=["日数", "B", "方式", "平均ブロック長"]).round(2).to_string(index=False))

# ---------------------------------------------------------------- θ* の下限
surf = pd.read_csv(os.path.join(PROC, "equilibrium_surface.csv"))
PI_PF0 = float(surf[(surf["泊"] == "なし") & (surf["K_wind倍率"] == 1.0) & (surf["K(万kW)"] == 0)]["π_PF(円/kW-年)"].iloc[0])
th = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
TH22 = float(th.loc[th["ym"] == "FY2022", "theta_m"].iloc[0])
TH26 = float(th.loc[th["ym"] == "FY2026", "theta_m"].iloc[0])
PF_ACT = est["pf"].sum() / len(FYS)
TAIL = PF_ACT / PI_PF0
CHARGE_COST = 4 * 365 * 1.2
PF22 = float(bt.loc[bt["fy"] == 2022, "pf"].sum())                  # FY2022 の実績の完全予見粗利（365日）
CAP22_C = float(ann.loc[ann["FY"] == 2022, "capture_c(%)"].iloc[0]) / 100


def crf(w, n=20):
    return w * (1 + w) ** n / ((1 + w) ** n - 1)


CREQ_94 = (4 * 6.8 * crf(0.06) + 0.53 + 0.69) * 1e4
NEED = {"標準（8.4: 容量1.25万・c_req3.45万）": 34_500 - 12_500,
        "楽観（8.4: 容量1.25万・c_req3.2万）": 32_000 - 12_500,
        "保守（8.4: 容量0.83万・c_req3.7万）": 37_000 - 8_300,
        "現状（9.4: 資本費6.8万・WACC6%・容量1.25万）": CREQ_94 - 12_500}
cap_c = ci[(ci["期間"] == "FY2023-25") & (ci["区分"] == "区間: capture率(%)") & (ci["比較"] == "c")
           & (ci["方式"] == "定常ブートストラップ")].iloc[0]
CAPS = {"0.81（原稿）": 0.81, f"c の点推定 {cap_c['点推定']/100:.3f}": cap_c["点推定"] / 100,
        f"c の95%上限 {cap_c['上限95']/100:.3f}": cap_c["上限95"] / 100, "1（完全予見）": 1.0}
th_rows = []
for case, need in NEED.items():
    for clab, cv in CAPS.items():
        for tlab, tv in (("なし", 1.0), (f"あり（×{TAIL:.3f}）", TAIL)):
            t_ = (need + CHARGE_COST) / (cv * tv * PI_PF0)
            th_rows.append({"ケース": case, "必要水準(円/kW-年)": round(need), "capture": clab, "裾の補正": tlab,
                            "θ*": t_, "θ*/θ_FY2022": t_ / TH22, "θ*/θ_FY2026上期": t_ / TH26,
                            "FY2022実績での実現可能収益(円/kW-年)": cv * PF22 - CHARGE_COST,
                            "FY2022実績で必要水準に届く": cv * PF22 - CHARGE_COST >= need,
                            "FY2022実績で届くのに必要なcapture": (need + CHARGE_COST) / PF22})
thb = pd.DataFrame(th_rows)
thb.round(3).to_csv(os.path.join(PROC, "strategy_theta_bounds.csv"), index=False, encoding="utf-8-sig")
print(f"\n=== θ* の下限（π_PF(0)={PI_PF0:,.0f}、実績の完全予見粗利 {PF_ACT:,.0f}、裾の補正 ×{TAIL:.3f}、"
      f"θ_FY2022={TH22}、θ_FY2026上期={TH26}） ===")
print(thb.pivot_table(index="ケース", columns=["capture", "裾の補正"], values="θ*", sort=False).round(2).to_string())
print(f"\n=== FY2022 の実績の完全予見粗利 {PF22:,.0f}（FY2023〜25 平均の {PF22 / PF_ACT:.2f}倍、"
      f"c の FY2022 capture {CAP22_C:.3f}）をそのまま使う場合 ===")
print(thb[thb["裾の補正"] == "なし"].pivot_table(index="ケース", columns="capture", sort=False,
                                               values="FY2022実績での実現可能収益(円/kW-年)").round(0).to_string())
print("届くのに必要な capture:", thb.groupby("ケース", sort=False)["FY2022実績で届くのに必要なcapture"].first().round(3).to_dict())

# ---------------------------------------------------------------- 図: (a) capture率と95%区間（上）、(b) c との差（下）
# Word では本文幅15.5cm（6.1インチ）で載せるので、その大きさで描き、図中の文字は8.5〜9.5pt にする
FIG_W = 6.1
FS_TICK, FS_LAB, FS_TTL, FS_LEG, FS_ANN = 8.5, 9.0, 9.5, 8.5, 8.5
ORDER = ["a", "a2", "b", "b2", "AR", "DL1", "DL3", "DL5", "c"]
cc = ci[(ci["期間"] == "FY2023-25") & (ci["区分"] == "区間: capture率(%)") & (ci["方式"] == "定常ブートストラップ")]
cc = cc.set_index("比較").loc[[LABEL[k] for k in ORDER]]
byfy = ann[ann["FY"].isin(FYS)].set_index("FY")
X, Mbar, Mstar = boot["FY2023-25"]
ic = NAMES.index("c")
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(FIG_W, 6.0), sharey=True, layout="constrained")
fig.get_layout_engine().set(h_pad=0.04, hspace=0.06)
ACC, NEU, LIGHT = "#0079C2", "#7F7F7F", "#B3B3B3"
txt_a, txt_b = [], []
for yv, k in enumerate(ORDER):
    r = cc.loc[LABEL[k]]
    col = ACC if k == "c" else NEU
    ax.plot([r["下限95"], r["上限95"]], [yv, yv], color=col, lw=1.6, solid_capstyle="round")
    ax.plot(r["点推定"], yv, "o", color=col, ms=5, mec="white", mew=0.9, zorder=3)
    for fy, mk in zip(FYS, ("^", "s", "D")):
        ax.plot(byfy.loc[fy, f"capture_{LABEL[k]}(%)"], yv + 0.27, mk, color=LIGHT, ms=3.2, mew=0, zorder=2,
                label=f"FY{fy}" if yv == 0 else None)
    txt_a.append(f"{r['点推定']:.1f}%（{r['下限95']:.1f}〜{r['上限95']:.1f}）")
    if k == "c":
        txt_b.append("基準")
        continue
    j = NAMES.index(k)
    pt = (Mbar[j] - Mbar[ic]) / Mbar[0] * 100
    dist = (Mstar[:, j] - Mstar[:, ic]) / Mstar[:, 0] * 100
    lo, hi = np.percentile(dist, [2.5, 97.5])
    dmv = dm_test(X[:, j] - X[:, ic], NW_MAIN)[0]
    ax2.plot([lo, hi], [yv, yv], color=NEU, lw=1.6, solid_capstyle="round")
    ax2.plot(pt, yv, "o", color=NEU, ms=5, mec="white", mew=0.9, zorder=3)
    txt_b.append(f"{pt:+.1f}（{dmv:.1f}）".replace("-", "−"))
ax.axvline(81, color="#999999", lw=0.8, ls="--")
ax2.axvline(0, color="#999999", lw=0.8)
ax.set_yticks(range(len(ORDER)))
# 図の表示名（論文本文の戦略名にそろえる）
LONG_FIG = {"a": "a　前日の実現価格のランク", "a2": "a2　同じ曜日区分の直近日", "b": "b　残余需要の予測ランク",
            "b2": "b′　b＋風力の直近7日平均", "c": "c　平均価格（気候値）",
            "DL1": "DL1　動的因子予測（1因子）", "DL3": "DL3　動的因子予測（3因子）",
            "DL5": "DL5　動的因子予測（5因子）", "AR": "AR　時刻別 AR(1)"}
ax.set_yticklabels([LONG_FIG[k] for k in ORDER])
ax.set_ylim(-0.6, len(ORDER) - 0.35)
ax.set_xlim(63, 88)
ax.set_xticks([65, 70, 75, 80, 85])
ax2.set_xlim(-16, 2)
ax2.set_xticks([-15, -10, -5, 0])
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace("-", "−")))
# 点推定と区間の数値は各パネルの右に並べる
for a_, tx in ((ax, txt_a), (ax2, txt_b)):
    sec = a_.secondary_yaxis("right")
    sec.set_yticks(range(len(ORDER)), labels=tx)
    sec.tick_params(length=0, pad=3, labelsize=FS_ANN, colors="#333333")
    sec.spines["right"].set_visible(False)
ax.set_xlabel("実現率（完全予見粗利に対する比、%）", fontsize=FS_LAB, color=GRAY)
ax2.set_xlabel("戦略 c との差（ポイント）", fontsize=FS_LAB, color=GRAY)
ax.set_title("(a) 実現率と95%区間", fontsize=FS_TTL, color="#333333", loc="left", pad=4)
ax2.set_title("(b) 戦略 c との差と95%区間", fontsize=FS_TTL, color="#333333", loc="left", pad=4)
for a_ in (ax, ax2):
    a_.grid(axis="x", color="#DDDDDD", lw=0.5)
    a_.tick_params(colors=GRAY, labelsize=FS_TICK, length=2.5, pad=2)
    a_.tick_params(axis="y", labelcolor="#333333", labelleft=True)
    for sp_ in ("top", "right"):
        a_.spines[sp_].set_visible(False)
ax2.tick_params(axis="y", colors="#333333")
ax.legend(title="年度別の点推定", fontsize=FS_LEG, title_fontsize=FS_LEG, frameon=False, loc="upper left",
          handletextpad=0.2, borderaxespad=0.2, labelspacing=0.25)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "strategy_capture_ci.png"), dpi=300, bbox_inches="tight", pad_inches=0.03)
print("saved strategy_capture_ci.png")
