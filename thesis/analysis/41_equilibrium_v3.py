#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""均衡分析 v3: 戦略c の実現粗利を直接計算した π_c(K)、損益分岐の θ*、価格モデルの条件付き応答の検証（8.1〜8.5・9.4）

目的（決定事項 D1〜D5、監査 A7-14・A8-1・A8-3-1・A8-4・A8-4-2・L-2〜L-5 への対応）:
  旧版（23・27・28）は、限界参入者の実現可能収益を π(K)=0.81·π_PF(K)−充電従量負担 とした。0.81 は実績価格の上での
  戦略c の capture率であり、日々の形状の変動の多くを持たない価格過程モデルの π_PF に掛けると取り逃しを二重に引く
  （モデル価格の上での c の capture は約0.92）。本スクリプトは、モデル価格の経路の上で戦略c の実現粗利を直接計算する。

手法:
  (0) 部品: 13（仕様A・分断混合、水準固定）と 26（水準係数付き仕様A）を exec で読み込む。exec の間は
      pandas.DataFrame.to_csv を無効にし（13 の hokkaido_cf_series.csv・26 の price_level_theta.csv を上書きしない）、
      標準出力を捨てる。価格関数はベクトル化して書き直し、元の predict_A・simulate_B と一致することを assert で確かめる。
      日の行列は 2022-02-01〜2026-06-30（1,611日、全日24時間がそろう）。評価は FY2023〜25 の1,096日、年度合計の3年平均。
  (1) 戦略c（36 と同じ定義）: 直近29日のうち同じ曜日区分（土日／平日）の日の時刻別平均価格（5日以上）でランクを付け、
      最安4時間に充電・最高4時間に放電（往復効率0.85 を放電側、1日1サイクル、休止なし）。ランク境界の同値は均等配分。
      最初の履歴は FY2022 末（2023-02-01〜03-31）のモデル価格（評価と同じ θ・同じフリート）。事前休止つき（気候値で
      期待粗利が負の日は休止）も感応度として出す。実績価格の上の c（FY2023〜25 平均）を同じ関数で計算し 8,427円を再現する。
  (2) π(K): 増分貪欲ディスパッチ（23・27 と同じ。フリートは各増分でその時点の価格の最安4hに充電・最高4hに放電、
      完全予見の粗利が正の日のみ）。刻みは 1万kW（10MW）で、K は 0〜150万kW を 1万kW ごと、160〜300万kW を 10万kW ごとに
      評価する（D2: 目標の K に正確に到達。旧版の K=25 は実際には30で計算されていた）。刻みの感応度（10・5・2.5・0.5）と
      旧格子の再現を併記する。フリートの配分（D3）は主が完全予見の増分貪欲、感応度として戦略c の窓（気候値で期待粗利が
      正の日だけ稼働）と半々。各 K の価格で限界参入者の π_PF(K)・c(K)・capture_c(K)=c/π_PF を計算する。
      収益の基準（D1）:
        実績整合（主）: π = λ·c_model(K) − 1,752、λ = 実績の c ÷ モデルの c(K=0, θ=1, 現状)（in-sample 校正）
        モデル直値（下側の参考）: π = c_model(K) − 1,752
        旧: π = 0.81·π_PF(K) − 1,752、旧・裾補正: 0.81 × 1.248（実績PF/モデルPF）× π_PF(K) − 1,752
      λ の不確実性は、日次の (実績 c, モデル c) の組を定常ブートストラップ（平均ブロック長20日、B=2,000）で求める。
      out-of-sample の安定性として、FY2022（θ_2022）と FY2026 4〜6月（θ_2026）の 実績c/モデルc を出す。
  (3) θ*（K=0 で参入が開く価格水準係数）: θ=1・1.57・1.72・3.0 で π(K) を直接計算し、収益 a(K;θ)（充電従量控除前）が
      θ に比例するかを確かめる。a(θ)=α+βθ を4点に当てはめて需要 need=c_req−κP_cap+1,752 を直接解いた値と、比例を仮定した
      need/a(1) を併記する。ケースは 8.4 の標準・楽観・保守（c_req 3.45万・3.2万・3.7万、容量1.25万／0.83万）と 9.4 の式
      （資本費6.8万円/kWh×4h×CRF(WACC,20年)+運維・廃止0.53万+託送等固定0.69万、容量1.25万、WACC 6%・8%・9%、資本費2.3万・4.0万）。
      外生の契約型容量（D5）: K_exo=0（主、参入に有利な側）、20万kW（接続済み）、20万+LTDA北海道分（57.7万→77.7万、
      訂正値67.4万→87.4万）。K_exo は 1万kW 格子の線形補間。損益分岐の年間固定費と資本費（θ=1・1.22・1.57）も出す。
      IRR（L-5）: 投資27.2万円/kW、20年、年間CF = a − 1,752 + 12,500 − 12,200。FY2022 の実績価格そのもの（c の実績と0.81×PF）を含む。
  (4) 価格モデルの条件付き応答の検証（D4）: FY2023〜25 の1,096日、表6.2 の主仕様（報告用季節×太陽光・風力（制御前、GWh/日）
      ＋需要＋FY・季節FE）と年月FE版。被説明変数は日平均・上位4h・下位4h・TB4h・完全予見粗利（円/kW-日、3.4·上位−4·下位の
      正の部分）。系列は実績、仕様A（13）、分断混合（13）、仕様A（26、θ_FY）、仕様A′。差（モデル−実績）の系列を同じ右辺に
      回帰し、EWC（Lazarus et al. 2018、ν=⌊0.4T^{2/3}⌋=42、t_ν）で差の SE と p 値を求める。風力×3季節の族で Holm 補正。
      仕様A′: μ を (気象学的季節, 時刻, 日次風力三分位) に依存させる。三分位の境界は季節ごとに FY2023〜25 の日次の制御前
      風力発電量で定め、μ は θ で割り戻した価格の g 残差の平均（仕様A の μ は中央値）。g は 26 のまま。風力の反実仮想では
      日次風力が境界を越えると上の三分位の μ を使い、最上位の三分位より先へは外挿しない。中央値版・五分位版、および μ を
      年度抜き取り（LOFO）で推定した版を頑健性として出す。仕様A′ が主仕様で全季節・全脚の風力の差が p>0.10 なら、
      風力スイープ（K=0 の完全予見粗利の分解）と π(K; 風力倍率, 泊) を仕様A′ でも計算する。
  (5) DC 需要の上端外挿（A8-4）: 供給曲線の最上位ビンの中心より上を (a) 一定（現行）、(b) 最上位8ビンの傾きで線形外挿、
      (c) 傾き2倍（実績の季節別上位十分位の傾きは最上位8ビンの0.5〜1.9倍。冬・春・秋では2倍が実績を上回るが、夏は
      8.6 の夏7〜9月の上端の傾き0.85〜1.15 に届かない）、(d) 実績の季節別（気象学的4季）上位十分位の傾き（監査の指定）、
      (e) (d) の冬・夏を 8.6 の上端の傾きの上限（冬0.81・夏1.15円/kWh per 100MW）に置き換えた版、の5通りにし、
      仕様A・分断混合（13）で ②泊3号・④DC+80万kW・⑤泊+DC の ΔPF と、上端より上にある時間の割合を出す。
  (6) K=0 の変種の直接計算（検証で追加）: 8.2 のベースロード減（泊3号・2基相当・全基）を 仕様A（13）・外挿・下限あり（33）・
      分断混合（13）で、10.1 の負価格（32 の段差モデル、θ=1・1.57・3.0、現状・泊・泊＋風力2倍）を 26 で、それぞれ戦略c を直接計算する。
      λ は各仕様の現状・K=0 で実績の戦略c に校正（負価格は 26 の λ）。旧基準の粗収益を 8,427/6,695 倍する一律換算と比べる
      （分断混合ではベースロード減で capture が0.80→0.41 と崩れ、一律換算は収益を最大2.4倍に過大に出す）。
      段差モデルでは下限時間の価格 −c 円が θ で動かず収益が θ に比例しないので、θ* は 32 と同じ比例の値（need/a(1)）に加え、
      a(θ)=α+βθ を3点に当てはめた直接解も出す（比例の値は参入に有利な側に偏る。泊＋風力2倍・−10円で1.54 対 2.00）。
出力: data/processed/pi_k_curve_v3.csv（π(K) の全曲線）、pi_k_curve_v3_zero.csv（π=0・半減の K）、theta_star_v3.csv、
      equilibrium_v3_irr.csv、price_model_validation.csv、price_model_level_ratios.csv、wind_sweep_v3.csv、
      dc_upper_end_sensitivity.csv、k0_variants_direct_c_v3.csv、figures/hokkaido/pi_k_curve_v3.png
限界: 部分均衡（揚水・連系線潮流・入札行動は g に埋め込まれた歴史的応答のまま）。λ は K=0・θ=1 の in-sample 校正で、
      K>0 ではフリートが裾を先に削るので実績整合ケースは上側の値になりうる。K_exo は既設・契約型の容量が価格テイカーとして
      同じ増分貪欲で動くと置いたもので、FY2023〜25 の価格（g の推定）には当時稼働していた蓄電池の影響が既に入っている
      （二重計上の上限側）。戦略c の窓に従うフリートは、監査の10万kW 刻みでは K≥75万kW でディスパッチが振動した
      （1万kW 刻みの本計算では K≤150 で単調）ので、K≥75 は参考値。刻み1万kW と0.5万kW の差は実績整合の π で K≤70 では
      41円以内、K=100 で60円。ただし刻みを細かくすると実績整合の π(K) は K≥50 で単調に上がり続け（K=70 で刻み10・5・2.5・1・0.5
      の順に −114・−45・+9・+92・+133）、収束していない（π=0 の K は刻み0.5で約72.5万kW、刻み1で71.5万kW。capture_c(100) は
      刻み1で0.59、0.5で0.67）。capture_c は π_PF≈0（K≥約200）では定義しない。K≥100 では休止しない戦略c の粗利が負になり、
      π は −1,752 を下回る（休止つきは列 c_事前休止）。π=0 の K は休止の有無で0.2〜0.8万kW しか変わらない。仕様A′ は同じ標本で
      μ を推定して同じ標本で検証する in-sample の検定であり（LOFO 版を併記）、変種の中から選んだ（状態変数4種×分位数×
      中央値・平均を試した）ことによる選択の偏りが残る。
"""
import contextlib
import io
import logging
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import optimize, stats
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
SEED = 20261021
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

ETA = 0.85
FLOOR = 0.01
CAPTURE_OLD = 0.81
WHEEL = 1.2 * 4 * 365                      # 充電従量負担 1,752 円/kW-年
TOMARI = 912_000 * 0.9 / 1000              # 泊3号 820.8MW
KP_CAP = {"1.25万": 12_500.0, "0.83万": 8_300.0}
C_FIX = 5_300.0 + 6_900.0                  # 運維・廃止 + 託送等固定（円/kW-年）
SLICE = 1.0                                # 増分の刻み（万kW）
K_EVAL = list(range(0, 151)) + list(range(160, 301, 10))
K_EXO = {"0（主）": 0.0, "20（接続済み）": 20.0, "57.7（LTDA旧値のみ）": 57.7, "67.4（LTDA訂正値のみ）": 67.4,
         "77.7（20＋LTDA旧値57.7）": 77.7, "87.4（20＋LTDA訂正値67.4）": 87.4}


# ---------------------------------------------------------------- (0) 部品の読み込み
def load_module(fn):
    ns = {"__file__": os.path.join(HERE, fn), "__name__": "mod_" + fn[:2]}
    _to = pd.DataFrame.to_csv
    pd.DataFrame.to_csv = lambda *a, **k: None          # 既存の出力ファイルを上書きしない
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(open(os.path.join(HERE, fn), encoding="utf-8").read(), ns)
    finally:
        pd.DataFrame.to_csv = _to
    return ns


n26 = load_module("26_price_process_v2.py")
n13 = load_module("13_price_process_v1.py")
THETA = n26["THETA"]
TH26, TH22 = THETA[2026], THETA[2022]
K_WIND_NOW = n26["est"]["wind_kw"].mean() / 1e4
assert abs(K_WIND_NOW - n13["K_WIND_NOW"]) < 1e-9

# 日の行列（2022-02-01〜2026-06-30）
pp = n13["p"]
pp = pp[(pp["ts"] >= "2022-02-01") & (pp["ts"] < "2026-07-01")].sort_values("ts").copy()
pp["date"] = pp["ts"].dt.normalize()
pp["hour"] = pp["ts"].dt.hour


def mat(col, df=pp):
    return df.pivot_table(index="date", columns="hour", values=col).to_numpy(float)


DAYS = pd.DatetimeIndex(sorted(pp["date"].unique()))
assert (np.diff(DAYS.values).astype("timedelta64[D]").astype(int) == 1).all()
NM = len(DAYS)
NETM, PACTM, PSYSM = mat("net"), mat("p_hokkaido"), mat("p_system")
WINDM, SOLM, DEMM, CFWM = mat("wind_pre"), mat("solar_pre"), mat("demand"), mat("cf_wind")
assert not np.isnan(NETM).any() and not np.isnan(PACTM).any() and not np.isnan(PSYSM).any()
SEASM = np.repeat(((DAYS.month % 12) // 3).to_numpy()[:, None], 24, 1)    # 気象学的4季（モデル用）
HOURM = np.repeat(np.arange(24)[None, :], NM, 0)
FYM = np.asarray(DAYS.year - (DAYS.month < 4).astype(int))
WKM = np.asarray(DAYS.dayofweek >= 5)
RSM = np.where(np.isin(DAYS.month, [7, 8, 9]), "夏", np.where(np.isin(DAYS.month, [12, 1, 2]), "冬", "不需要期"))
SEAS_DAY = SEASM[:, 0]


def mu_matrix(adj_series, seas=SEASM, hour=HOURM):
    return adj_series.reindex(pd.MultiIndex.from_arrays([seas.ravel(), hour.ravel()])).fillna(0).to_numpy().reshape(seas.shape)


MU26, MU13 = mu_matrix(n26["ADJ"]), mu_matrix(n13["ADJ_A"])
MU_LOW, MU_HIGH = mu_matrix(n13["ADJ_low"]), mu_matrix(n13["ADJ_high"])
G26, G13, GB_LOW, GB_HIGH = n26["G"], n13["GA"], n13["GB_low"], n13["GB_high"]


def top_slope(G, s, nb=8):
    x, y = G[s]
    return max(np.polyfit(x[-nb:], y[-nb:], 1)[0], 0.0)


def g_curve(net, G, seas, upper_mult=0.0):
    """供給曲線 g（季節別の分位ビン中央値の折れ線。推定範囲より下は0.01、上は一定。upper_mult>0 なら上端を
    最上位8ビンの傾き×upper_mult で線形外挿。upper_mult が dict なら {気象学的季節: 傾き（円/kWh per MW）} で外挿）"""
    per_season = isinstance(upper_mult, dict)
    out = np.empty_like(net, dtype=float)
    for s in range(4):
        m = seas == s
        x, y = G[s]
        v = np.interp(net[m], x, y, left=FLOOR, right=y[-1])
        if per_season or upper_mult > 0:
            hi = net[m] > x[-1]
            sl = upper_mult[s] if per_season else upper_mult * top_slope(G, s)
            v[hi] = y[-1] + sl * (net[m][hi] - x[-1])
        out[m] = v
    return np.maximum(out, FLOOR)


def price_A(net, G, MU, theta=1.0, seas=SEASM, upper_mult=0.0):
    """仕様A: p = 0.01 ∨ {0.01 + θ·[0.01 ∨ (g(net)+μ) − 0.01]}（13 は θ=1）"""
    base = np.maximum(g_curve(net, G, seas, upper_mult) + MU, FLOOR)
    return np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)


# 分断混合（13 の simulate_B と同じ。評価日の一様乱数は 13 と同じ列、履歴日は別の種）
_mn = n13["mn"]


def regime_probs(net, seas):
    Xn = sm.add_constant(np.column_stack([net / 1000, (net / 1000) ** 2,
                                          np.column_stack([(seas == s).astype(float) for s in (1, 2, 3)])]), has_constant="add")
    return _mn.predict(Xn)


U_B = np.random.default_rng(20260729).random((NM, 24))
_ev13 = (FYM >= 2023) & (FYM <= 2025)
_est13 = n13["est"]
assert _est13["ts"].is_monotonic_increasing and len(_est13) == _ev13.sum() * 24
U_B[_ev13] = np.random.default_rng(20260728).random(len(_est13)).reshape(-1, 24)


def price_B(net, rows, upper_mult=0.0):
    seas, psys, u = SEASM[rows], PSYSM[rows], U_B[rows]
    pr = regime_probs(net.ravel(), seas.ravel())
    uu = u.ravel()
    reg = np.select([uu < pr[:, 0], uu < pr[:, 0] + pr[:, 1]], [0, 1], default=2).reshape(net.shape)
    lo = np.maximum(g_curve(net, GB_LOW, seas, upper_mult) + MU_LOW[rows], FLOOR)
    hi = np.maximum(g_curve(net, GB_HIGH, seas, upper_mult) + MU_HIGH[rows], FLOOR)
    out = np.where(reg == 0, lo, np.where(reg == 2, hi, psys))
    return np.maximum(out, FLOOR), reg


# 元の関数との一致（FY2023〜25）
_e26 = n26["est"].sort_values("ts")
_chk = n26["predict_A"](_e26, theta=1.0).reshape(-1, 24)
assert np.abs(_chk - price_A(NETM[_ev13], G26, MU26[_ev13], 1.0, SEASM[_ev13])).max() < 1e-9
_chk = n13["predict_A"](_est13).reshape(-1, 24)
assert np.abs(_chk - price_A(NETM[_ev13], G13, MU13[_ev13], 1.0, SEASM[_ev13])).max() < 1e-9
_chk = n13["simulate_B"](_est13).reshape(-1, 24)
assert np.abs(_chk - price_B(NETM[_ev13], np.where(_ev13)[0])[0]).max() < 1e-9
print("価格関数: 26 の predict_A・13 の predict_A・simulate_B と一致（最大差 <1e-9）")


# ---------------------------------------------------------------- (1) 戦略c と完全予見の評価
def make_W(wk):
    n = len(wk)
    W = np.zeros((n, n))
    has = np.zeros(n, bool)
    for i in range(n):
        h = [j for j in range(max(0, i - 29), i) if wk[j] == wk[i]]
        if len(h) >= 5:
            W[i, h] = 1.0 / len(h)
            has[i] = True
    return W, has


def tie_w(sig, k=4):
    """信号の下位 k 時間の重み（境界の同値は均等配分。36 と同じ）"""
    s = np.sort(sig, 1)
    thr = s[:, k - 1:k]
    w = (sig < thr).astype(float)
    tied = sig == thr
    return w + tied * ((k - w.sum(1, keepdims=True)) / tied.sum(1, keepdims=True))


def daily_eval(P, W):
    """日次の 完全予見粗利 pf・戦略c の粗利 c・事前休止つき cp・稼働日の上位4h/下位4h 平均（円/kW-日・円/kWh）"""
    C = W @ P
    wc, wd = tie_w(C), tie_w(-C)
    c = ETA * (wd * P).sum(1) - (wc * P).sum(1)
    expm = ETA * (wd * C).sum(1) - (wc * C).sum(1)
    s = np.sort(P, 1)
    top, bot = s[:, -4:].mean(1), s[:, :4].mean(1)
    pf = np.maximum(0.0, 4 * (ETA * top - bot))
    return {"pf": pf, "c": c, "cp": np.where(expm > 0, c, 0.0), "top": top, "bot": bot}


def annual(v, fy, mask):
    """年度合計の平均（円/kW-年）"""
    return float(pd.Series(v[mask]).groupby(fy[mask]).sum().mean())


W_M, HAS_M = make_W(WKM)
EV = _ev13                                                  # FY2023〜25
assert HAS_M[EV].all()
D_ACT = daily_eval(PACTM, W_M)
C_ACT = annual(D_ACT["c"], FYM, EV)
PF_ACT = annual(D_ACT["pf"], FYM, EV)
print(f"\n実績価格（FY2023〜25）: 戦略c {C_ACT:,.1f}  完全予見 {PF_ACT:,.1f}  capture {C_ACT / PF_ACT:.4f}")
_sdm = pd.read_csv(os.path.join(PROC, "strategy_daily_margins.csv"), parse_dates=["day"])
_c36 = _sdm.groupby("fy")["c"].sum().mean()
assert abs(_c36 - C_ACT) < 1.0, (_c36, C_ACT)
print(f"  36 の strategy_daily_margins.csv の c（{_c36:,.1f}）と一致")
_st = pd.read_csv(os.path.join(PROC, "strategy_tests.csv"))
_ci = _st[(_st["区分"] == "区間: capture率(%)") & (_st["期間"] == "FY2023-25") & (_st["比較"] == "c")
          & (_st["方式"] == "定常ブートストラップ")].iloc[0]
print(f"  capture率の95%区間（36、定常ブートストラップ）: {_ci['下限95']:.1f}〜{_ci['上限95']:.1f}%")

# フリート用のブロック: 2023-02-01〜2026-03-31（FY2022 末の59日を履歴に使う）
BLK = np.where((DAYS >= "2023-02-01") & (FYM <= 2025))[0]
NB = len(BLK)
W_B, HAS_B = make_W(WKM[BLK])
EVB = EV[BLK]
FYB = FYM[BLK]
SEASB, MU26B, MU13B, CFWB, NETB = SEASM[BLK], MU26[BLK], MU13[BLK], CFWM[BLK], NETM[BLK]
WIND_DAY = WINDM.sum(1) / 1000                              # 日次の制御前風力（GWh/日）
RB = np.arange(NB)[:, None]


def net_scenario(rows, tomari=False, wind_mult=1.0, ddem=0.0):
    net = NETM[rows] - (TOMARI if tomari else 0.0) + ddem
    if wind_mult != 1.0:
        net = net - (wind_mult - 1.0) * K_WIND_NOW * 1e4 * CFWM[rows] / 1000
    return net


def wind_day_scenario(rows, wind_mult=1.0):
    return (WINDM[rows] + (wind_mult - 1.0) * K_WIND_NOW * 1e4 * CFWM[rows] / 1000).sum(1) / 1000


# ---------------------------------------------------------------- 仕様A′（μ × 日次風力の分位）
def deflate(P, fy):
    th = np.array([THETA.get(int(f), 1.0) for f in fy])[:, None]
    return FLOOR + (P - FLOOR) / th, th


PDEF_EV, TH_EV = deflate(PACTM[EV], FYM[EV])
RES_EV = PDEF_EV - g_curve(NETM[EV], G26, SEASM[EV])         # g の残差（θ で割り戻した尺度）


def fit_aprime(nb=3, stat="mean", train=None):
    """μ′(季節, 分位, 時刻) と分位の境界。train は評価日（FY2023〜25）のうち推定に使う日のマスク"""
    sd, wd = SEAS_DAY[EV], WIND_DAY[EV]
    train = np.ones(len(sd), bool) if train is None else train
    cuts, mu = {}, np.zeros((4, nb, 24))
    for s in range(4):
        m = (sd == s) & train
        cuts[s] = np.quantile(wd[m], np.linspace(0, 1, nb + 1)[1:-1])
        b = np.searchsorted(cuts[s], wd[m], side="right")
        for k in range(nb):
            r = RES_EV[m][b == k]
            mu[s, k] = np.median(r, axis=0) if stat == "median" else r.mean(0)
    return {"cuts": cuts, "mu": mu, "nb": nb, "stat": stat}


def aprime_mu(spec, seas_day, wind_day):
    b = np.zeros(len(seas_day), int)
    for s in range(4):
        m = seas_day == s
        b[m] = np.searchsorted(spec["cuts"][s], wind_day[m], side="right")
    return spec["mu"][seas_day, b]


AP3 = fit_aprime(3, "mean")                                 # 仕様A′（主）
AP3MED = fit_aprime(3, "median")
AP5 = fit_aprime(5, "mean")


# ---------------------------------------------------------------- (2) π(K) の計算
def run_curve(pfun, net0, mode="PF", Ks=K_EVAL, slice_=SLICE, old_bug=False):
    """増分貪欲ディスパッチ。pfun(net) は (NB,24) の価格。mode: PF（完全予見）・c（戦略c の窓）・half（半々）"""
    adj = net0.copy()
    done = 0.0
    out = []
    fr = {"PF": (1.0, 0.0), "c": (0.0, 1.0), "half": (0.5, 0.5)}[mode]
    for K in Ks:
        while done < K - 1e-9:
            st = slice_ if old_bug else min(slice_, K - done)
            p = pfun(adj)
            if fr[0] > 0:
                o = np.argsort(p, 1)
                chg, dis = o[:, :4], o[:, -4:]
                mg = np.take_along_axis(p, dis, 1).sum(1) * ETA - np.take_along_axis(p, chg, 1).sum(1)
                a = mg > 0
                adj[RB[a], chg[a]] += fr[0] * st * 10.0
                adj[RB[a], dis[a]] -= fr[0] * st * 10.0 * ETA
            if fr[1] > 0:
                C = W_B @ p
                wc, wd = tie_w(C), tie_w(-C)
                a = HAS_B & (ETA * (wd * C).sum(1) - (wc * C).sum(1) > 0)
                adj[a] += fr[1] * st * 10.0 * (wc[a] - ETA * wd[a])
            done += st
        d = daily_eval(pfun(adj), W_B)
        out.append({"K(万kW)": K, "π_PF": annual(d["pf"], FYB, EVB), "c": annual(d["c"], FYB, EVB),
                    "c_事前休止": annual(d["cp"], FYB, EVB)})
    return pd.DataFrame(out)


def pf_A26(theta, mu=MU26B):
    return lambda net: price_A(net, G26, mu, theta, SEASB)


def pf_A13():
    return lambda net: price_A(net, G13, MU13B, 1.0, SEASB)


def pf_B13():
    return lambda net: price_B(net, BLK)[0]


def pf_Aprime(spec, theta, wind_mult=1.0):
    mu = aprime_mu(spec, SEAS_DAY[BLK], wind_day_scenario(BLK, wind_mult))
    return lambda net: price_A(net, G26, mu, theta, SEASB)


curves = []


def add_curve(model, scen, theta, wind_mult, tomari, mode, pfun, net0, Ks=K_EVAL, slice_=SLICE, label_slice=None, old_bug=False):
    df = run_curve(pfun, net0, mode, Ks, slice_, old_bug)
    df.insert(0, "刻み(万kW)", label_slice if label_slice is not None else slice_)
    df.insert(0, "フリート配分", {"PF": "完全予見の増分貪欲（主）", "c": "戦略cの窓", "half": "半々"}[mode])
    df.insert(0, "泊3号", "あり" if tomari else "なし")
    df.insert(0, "風力倍率", wind_mult)
    df.insert(0, "θ", round(theta, 3))
    df.insert(0, "シナリオ", scen)
    df.insert(0, "価格モデル", model)
    curves.append(df)
    return df


M26, M13, MB, MAP = "仕様A（26、水準係数付き）", "仕様A（13、水準固定）", "分断混合（13）", "仕様A′（26、μ×日次風力三分位）"
SC = {"現状": (False, 1.0), "泊3号再稼働": (True, 1.0), "泊＋風力2倍": (True, 2.0)}
print("\n[2] π(K) 曲線（刻み1万kW）を計算中 ...")
for scen, (tom, wm) in SC.items():
    net0 = net_scenario(BLK, tom, wm)
    add_curve(M26, scen, 1.0, wm, tom, "PF", pf_A26(1.0), net0)
    add_curve(M13, scen, 1.0, wm, tom, "PF", pf_A13(), net0)
net_now, net_tom = net_scenario(BLK), net_scenario(BLK, True)
for th in (TH26, TH22, 3.0):
    add_curve(M26, "現状", th, 1.0, False, "PF", pf_A26(th), net_now)
add_curve(M26, "泊3号再稼働", TH26, 1.0, True, "PF", pf_A26(TH26), net_tom)
for th in (1.0, TH26):
    for mode in ("c", "half"):
        add_curve(M26, "現状", th, 1.0, False, mode, pf_A26(th), net_now, Ks=list(range(0, 151)))
add_curve(M13, "現状", 1.0, 1.0, False, "c", pf_A13(), net_now, Ks=list(range(0, 151)))
for mode in ("PF", "c", "half"):
    add_curve(MB, "現状", 1.0, 1.0, False, mode, pf_B13(), net_now, Ks=list(range(0, 151)))
# 刻みの感応度と旧格子の再現（仕様A 26、θ=1、現状）
KS_SENS = [0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 100, 150]
for sl in (10.0, 5.0, 2.5, 0.5):
    add_curve(M26, "現状", 1.0, 1.0, False, "PF", pf_A26(1.0), net_now, Ks=KS_SENS, slice_=sl)
add_curve(M26, "現状", 1.0, 1.0, False, "PF", pf_A26(1.0), net_now, Ks=[0, 10, 25, 50, 100, 150],
          slice_=10.0, label_slice="10（旧格子の再現: K=25 は実際30）", old_bug=True)
print("  主要曲線 完了")

# ---------------------------------------------------------------- 校正係数 λ と収益の基準
CV = pd.concat(curves, ignore_index=True)


def c0_of(model, mode="完全予見の増分貪欲（主）"):
    r = CV[(CV["価格モデル"] == model) & (CV["シナリオ"] == "現状") & (CV["θ"] == 1.0) & (CV["フリート配分"] == mode)
           & (CV["刻み(万kW)"] == SLICE) & (CV["K(万kW)"] == 0)]
    return float(r["c"].iloc[0]), float(r["π_PF"].iloc[0])


LAMBDA = {}
for m in (M26, M13, MB):
    c0, pf0 = c0_of(m)
    LAMBDA[m] = C_ACT / c0
    print(f"  {m}: K=0・θ=1 のモデル c {c0:,.0f}  π_PF {pf0:,.0f}  capture {c0 / pf0:.4f}  λ=実績c/モデルc {LAMBDA[m]:.4f}")

# 裾補正（27 と同じ: FY2023〜25 の実績PF ÷ θ_FY 付きモデルPF）
P26FY_EV = price_A(NETM[EV], G26, MU26[EV], np.array([THETA[f] for f in FYM[EV]])[:, None], SEASM[EV])
TAIL = PF_ACT / annual(daily_eval(P26FY_EV, W_M[np.ix_(EV, EV)])["pf"], FYM[EV], np.ones(EV.sum(), bool))
print(f"  裾補正（実績PF/モデルPF θ_FY）= {TAIL:.3f}")

# 仕様A′ の曲線（K=0〜150）と風力スイープ
AP_C0 = {}
for nm, spec in (("仕様A′（26、μ×日次風力三分位）", AP3), ("仕様A′（五分位）", AP5), ("仕様A′（中央値版）", AP3MED)):
    df = add_curve(nm, "現状", 1.0, 1.0, False, "PF", pf_Aprime(spec, 1.0), net_now, Ks=list(range(0, 151)))
    AP_C0[nm] = float(df["c"].iloc[0])
    LAMBDA[nm] = C_ACT / AP_C0[nm]
print("  仕様A′ λ:", {k: round(v, 4) for k, v in LAMBDA.items() if "A′" in k})


def add_bases(df):
    lam = df["価格モデル"].map(lambda m: LAMBDA.get(m, LAMBDA[M26]))
    df["capture_c"] = (df["c"] / df["π_PF"]).where(df["π_PF"] > 1.0)        # π_PF≈0 では定義しない
    df["校正係数λ"] = lam
    df["π_実績整合"] = lam * df["c"] - WHEEL
    df["π_モデル直値"] = df["c"] - WHEEL
    df["π_旧0.81PF"] = CAPTURE_OLD * df["π_PF"] - WHEEL
    df["π_旧裾補正"] = CAPTURE_OLD * TAIL * df["π_PF"] - WHEEL
    return df


# ---------------------------------------------------------------- (4) 価格モデルの検証（D4）
print("\n[4] 価格モデルの条件付き応答の検証 ...")
DAYS_EV = DAYS[EV]
T = int(EV.sum())
NU = int(np.floor(0.4 * T ** (2 / 3)))
_tt = np.arange(1, T + 1) - 0.5
COS = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, NU + 1), _tt) / T)
RS_EV, FY_EV = RSM[EV], FYM[EV]
Xb = pd.DataFrame(index=DAYS_EV)
for s in ["夏", "冬", "不需要期"]:
    Xb[f"solar_{s}"] = SOLM[EV].sum(1) / 1000 * (RS_EV == s)
    Xb[f"wind_{s}"] = WINDM[EV].sum(1) / 1000 * (RS_EV == s)
Xb["demand"] = DEMM[EV].sum(1) / 1000
X_MAIN = sm.add_constant(pd.concat([Xb, pd.get_dummies(pd.Series(FY_EV, index=DAYS_EV), prefix="fy", drop_first=True).astype(float),
                                    pd.get_dummies(pd.Series(RS_EV, index=DAYS_EV), prefix="s", drop_first=True).astype(float)], axis=1))
X_YM = sm.add_constant(pd.concat([Xb, pd.get_dummies(pd.Series(DAYS_EV.to_period("M").astype(str), index=DAYS_EV),
                                                     prefix="ym", drop_first=True).astype(float)], axis=1))


def ols_ewc(y, Xd):
    Xn = Xd.to_numpy(float)
    XtXi = np.linalg.inv(Xn.T @ Xn)
    b = XtXi @ Xn.T @ y
    e = y - Xn @ b
    psi = (Xn * e[:, None]) @ XtXi
    return b, np.sqrt(((COS @ psi) ** 2).mean(0))


def day_metrics(P):
    s = np.sort(P, 1)
    top, bot = s[:, -4:].mean(1), s[:, :4].mean(1)
    return {"日平均": P.mean(1), "上位4h": top, "下位4h": bot, "TB4h": top - bot, "完全予見粗利": np.maximum(0, 3.4 * top - 4 * bot)}


DM_ACT = day_metrics(PACTM[EV])
THFY_EV = np.array([THETA[f] for f in FY_EV])[:, None]
B_EV, _ = price_B(NETM[EV], np.where(EV)[0])
SERIES = {
    "仕様A（13、水準固定）": price_A(NETM[EV], G13, MU13[EV], 1.0, SEASM[EV]),
    "分断混合（13）": B_EV,
    "仕様A（26、θ_FY）": P26FY_EV,
    "仕様A′（26、θ_FY、μ×日次風力三分位・平均）": price_A(NETM[EV], G26, aprime_mu(AP3, SEAS_DAY[EV], WIND_DAY[EV]), THFY_EV, SEASM[EV]),
    "仕様A′（中央値版）": price_A(NETM[EV], G26, aprime_mu(AP3MED, SEAS_DAY[EV], WIND_DAY[EV]), THFY_EV, SEASM[EV]),
    "仕様A′（五分位）": price_A(NETM[EV], G26, aprime_mu(AP5, SEAS_DAY[EV], WIND_DAY[EV]), THFY_EV, SEASM[EV]),
}
# 年度抜き取り（μ のみ。g は全標本の推定のまま）
for lab, nb, stat in (("仕様A（26、θ_FY）μをLOFO", 1, "median"), ("仕様A′ μをLOFO", 3, "mean")):
    P = np.zeros((T, 24))
    for f in (2023, 2024, 2025):
        tr = FY_EV != f
        if nb == 1:
            mu = np.zeros((4, 24))
            for s in range(4):
                mu[s] = np.median(RES_EV[(SEAS_DAY[EV] == s) & tr], axis=0)
            MUf = mu[SEAS_DAY[EV]]
        else:
            MUf = aprime_mu(fit_aprime(nb, stat, tr), SEAS_DAY[EV], WIND_DAY[EV])
        Pf = price_A(NETM[EV], G26, MUf, THFY_EV, SEASM[EV])
        P[~tr] = Pf[~tr]
    SERIES[lab] = P

val_rows = []
for spec_lab, Xd in (("主仕様（表6.2）", X_MAIN), ("年月FE", X_YM)):
    cols = list(Xd.columns)
    for ylab in DM_ACT:
        bA, seA = ols_ewc(DM_ACT[ylab], Xd)
        for slab, P in SERIES.items():
            dmm = day_metrics(P)[ylab]
            bM, seM = ols_ewc(dmm, Xd)
            bD, seD = ols_ewc(dmm - DM_ACT[ylab], Xd)
            for var in ("wind", "solar"):
                for s in ["夏", "冬", "不需要期"]:
                    i = cols.index(f"{var}_{s}")
                    t = bD[i] / seD[i]
                    val_rows.append({"検証の仕様": spec_lab, "系列": slab, "被説明変数": ylab, "係数": "風力" if var == "wind" else "太陽光",
                                     "季節": s, "実績の係数": bA[i], "実績のSE(EWC)": seA[i], "モデルの係数": bM[i], "モデルのSE(EWC)": seM[i],
                                     "差(モデル−実績)": bD[i], "差のSE(EWC)": seD[i], "t": t, "p(t_ν)": 2 * stats.t.sf(abs(t), NU),
                                     "ν": NU, "日数": T})
VAL = pd.DataFrame(val_rows)
VAL["p_Holm(風力3季節)"] = np.nan
for key, g in VAL.groupby(["検証の仕様", "系列", "被説明変数", "係数"]):
    p = g["p(t_ν)"].to_numpy()
    o = np.argsort(p)
    adj = np.maximum.accumulate(np.minimum(1, (len(p) - np.arange(len(p))) * p[o]))
    out = np.empty_like(p)
    out[o] = adj
    VAL.loc[g.index, "p_Holm(風力3季節)"] = out
VAL.loc[VAL["係数"] == "太陽光", "p_Holm(風力3季節)"] = np.nan
VAL.round(4).to_csv(os.path.join(PROC, "price_model_validation.csv"), index=False, encoding="utf-8-sig")
vw = VAL[VAL["係数"] == "風力"]
summ = vw.groupby(["検証の仕様", "系列"]).agg(差のp010未満=("p(t_ν)", lambda x: int((x < 0.10).sum())), 最小p=("p(t_ν)", "min"),
                                             差のp005未満=("p(t_ν)", lambda x: int((x < 0.05).sum())))
print(summ.round(3).to_string())
APRIME_PASS = bool((vw[(vw["検証の仕様"] == "主仕様（表6.2）") & (vw["系列"].str.startswith("仕様A′（26"))]["p(t_ν)"] > 0.10).all())
print("仕様A′ は主仕様で全季節・全脚の風力の差が p>0.10:", APRIME_PASS)
show = vw[(vw["検証の仕様"] == "主仕様（表6.2）") & vw["系列"].isin(["仕様A（13、水準固定）", "分断混合（13）", "仕様A′（26、θ_FY、μ×日次風力三分位・平均）"])]
print(show.pivot_table(index=["被説明変数", "季節"], columns="系列", values=["差(モデル−実績)", "p(t_ν)"]).round(3).to_string())
print(show.drop_duplicates(["被説明変数", "季節"]).set_index(["被説明変数", "季節"])[["実績の係数"]].round(3).T.to_string())

# 水準の比（PF と c、期間別）と μ を外した場合
print("\n[4b] 水準の再現（期間別）...")
lvl = []


TH_ALL = np.array([THETA.get(int(f), 1.0) if f in THETA else (THETA[2022] if f < 2022 else 1.0) for f in FYM])[:, None]
# FY2022 の履歴（FY2021 末）は θ_2022、FY2026 の履歴（FY2025 末）は θ_2025 のまま（水準係数は年度単位）
TH_ALL[FYM == 2021] = TH22
P_A_ALL = price_A(NETM, G26, MU26, TH_ALL, SEASM)
P_AP_ALL = price_A(NETM, G26, aprime_mu(AP3, SEAS_DAY, WIND_DAY), TH_ALL, SEASM)
P_A_NOMU = price_A(NETM, G26, np.zeros_like(MU26), TH_ALL, SEASM)
P_A_TH1 = price_A(NETM, G26, MU26, 1.0, SEASM)
P_A_NOMU1 = price_A(NETM, G26, np.zeros_like(MU26), 1.0, SEASM)
PERIODS = {"FY2023": FYM == 2023, "FY2024": FYM == 2024, "FY2025": FYM == 2025, "FY2023〜25（in-sample）": EV,
           "FY2022（OOS、θ=1.72）": FYM == 2022, "FY2026 4〜6月（OOS、θ=1.57）": FYM == 2026}
dA_ = D_ACT
for lab, P in (("仕様A（26、θ_FY）", P_A_ALL), ("仕様A′（26、θ_FY）", P_AP_ALL), ("仕様A（26、θ_FY）μ=0", P_A_NOMU)):
    dM = daily_eval(P, W_M)
    for per, m in PERIODS.items():
        pfa, ca = annual(dA_["pf"], FYM, m), annual(dA_["c"], FYM, m)
        pfm, cm = annual(dM["pf"], FYM, m), annual(dM["c"], FYM, m)
        lvl.append({"モデル": lab, "期間": per, "実績PF": pfa, "モデルPF": pfm, "PF比(実績/モデル)": pfa / pfm,
                    "実績c": ca, "モデルc": cm, "c比(実績/モデル)": ca / cm, "実績capture": ca / pfa, "モデルcapture": cm / pfm,
                    "実績の平均価格": PACTM[m].mean(), "モデルの平均価格": P[m].mean(),
                    "実績の下限張り付き(h/年)": (PACTM[m] <= FLOOR + 0.001).sum() / len(np.unique(FYM[m])),
                    "モデルの下限張り付き(h/年)": (P[m] <= FLOOR + 0.001).sum() / len(np.unique(FYM[m]))})
for lab, P in (("仕様A（26、θ=1）", P_A_TH1), ("仕様A（26、θ=1）μ=0", P_A_NOMU1)):
    dM = daily_eval(P, W_M)
    m = EV
    lvl.append({"モデル": lab, "期間": "FY2023〜25（in-sample）", "実績PF": PF_ACT, "モデルPF": annual(dM["pf"], FYM, m),
                "PF比(実績/モデル)": PF_ACT / annual(dM["pf"], FYM, m), "実績c": C_ACT, "モデルc": annual(dM["c"], FYM, m),
                "c比(実績/モデル)": C_ACT / annual(dM["c"], FYM, m)})
LVL = pd.DataFrame(lvl)
# λ のブートストラップ（日次の組、定常ブートストラップ、平均ブロック長20日）
dM1 = daily_eval(P_A_TH1, W_M)
ca_d, cm_d = D_ACT["c"][EV], dM1["c"][EV]
B_BOOT, LB = 2000, 20
lam_b = np.empty(B_BOOT)
for b in range(B_BOOT):
    idx = np.empty(T, int)
    i = rng.integers(T)
    for t in range(T):
        idx[t] = i
        i = rng.integers(T) if rng.random() < 1 / LB else (i + 1) % T
    lam_b[b] = ca_d[idx].sum() / cm_d[idx].sum()
LAM_CI = np.quantile(lam_b, [0.025, 0.975])
print(f"  λ（仕様A 26、θ=1）= {LAMBDA[M26]:.4f}、95%区間（定常ブートストラップ）{LAM_CI[0]:.3f}〜{LAM_CI[1]:.3f}")
LVL = pd.concat([LVL, pd.DataFrame([{"モデル": "仕様A（26、θ=1）", "期間": "λ の95%区間（定常ブートストラップ、B=2000、ブロック20日）",
                                     "c比(実績/モデル)": LAMBDA[M26], "c比_下限95": LAM_CI[0], "c比_上限95": LAM_CI[1]}])], ignore_index=True)
LVL.round(4).to_csv(os.path.join(PROC, "price_model_level_ratios.csv"), index=False, encoding="utf-8-sig")
print(LVL[["モデル", "期間", "PF比(実績/モデル)", "c比(実績/モデル)", "実績capture", "モデルcapture", "モデルPF"]].round(3).to_string(index=False))

# ---------------------------------------------------------------- 風力スイープ（K=0 の分解）と π(K; 風力, 泊)
print("\n[4c] 風力スイープ ...")


def decompose(d1, d0, mask):
    """ΔPF を スプレッドの変化 3.4ΔTB4h・往復損失の水準効果 −0.6Δ下位4h・休止の切替 に分ける（年度合計の平均）"""
    both = (d1["pf"] > 0) & (d0["pf"] > 0)
    tb1, tb0 = d1["top"] - d1["bot"], d0["top"] - d0["bot"]
    spread = np.where(both, 3.4 * (tb1 - tb0), 0.0)
    level = np.where(both, -0.6 * (d1["bot"] - d0["bot"]), 0.0)
    sw = (d1["pf"] - d0["pf"]) - spread - level
    return annual(spread, FYB, mask), annual(level, FYB, mask), annual(sw, FYB, mask)


ws_rows = []
WMULTS = (0.5, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
for model in ("仕様A（26、θ=1）", "仕様A（13）", "仕様A′（三分位・平均）", "仕様A′（五分位・平均）", "分断混合（13）"):
    for tom in (False, True):
        ref = None
        for wm in WMULTS:
            net = net_scenario(BLK, tom, wm)
            if model.startswith("仕様A（26"):
                P = price_A(net, G26, MU26B, 1.0, SEASB)
            elif model.startswith("仕様A（13"):
                P = price_A(net, G13, MU13B, 1.0, SEASB)
            elif model.startswith("仕様A′（三"):
                P = price_A(net, G26, aprime_mu(AP3, SEAS_DAY[BLK], wind_day_scenario(BLK, wm)), 1.0, SEASB)
            elif model.startswith("仕様A′（五"):
                P = price_A(net, G26, aprime_mu(AP5, SEAS_DAY[BLK], wind_day_scenario(BLK, wm)), 1.0, SEASB)
            else:
                P = price_B(net, BLK)[0]
            d = daily_eval(P, W_B)
            if wm == 1.0:
                ref = d
            ws_rows.append({"モデル": model, "泊3号": "あり" if tom else "なし", "風力倍率": wm, "風力(万kW)": round(K_WIND_NOW * wm),
                            "π_PF(0)": annual(d["pf"], FYB, EVB), "c(0)": annual(d["c"], FYB, EVB), "_d": d,
                            "下限張り付き(h/年)": (P[EVB] <= FLOOR + 0.001).sum() / 3})
        for r in ws_rows[-len(WMULTS):]:
            sp, lv, sw = decompose(r["_d"], ref, EVB)
            r.update({"ΔPF(対風力1倍)": r["π_PF(0)"] - annual(ref["pf"], FYB, EVB), "うちスプレッドの変化": sp, "うち往復損失の水準効果": lv, "うち休止の切替": sw})
WS = pd.DataFrame(ws_rows).drop(columns="_d")
_num = [c for c in WS.columns if c not in ("モデル", "泊3号", "風力倍率", "風力(万kW)")]
WS[_num] = WS[_num].round(1)
WS.to_csv(os.path.join(PROC, "wind_sweep_v3.csv"), index=False, encoding="utf-8-sig")
print(WS[WS["泊3号"] == "なし"].pivot(index="風力倍率", columns="モデル", values="ΔPF(対風力1倍)").round(0).to_string())
print(WS[WS["泊3号"] == "なし"].pivot(index="風力倍率", columns="モデル", values="うちスプレッドの変化").round(0).to_string())

if APRIME_PASS:
    print("  仕様A′ が検証を通ったので、π(K; 風力, 泊) を仕様A′ でも計算する")
for wm in (0.5, 1.0, 1.5, 2.0, 3.0):
    for tom in (False, True):
        if wm == 1.0 and not tom:
            continue                                               # 現状は上で計算済み（M26 は K_EVAL、仕様A′ は 0〜150）
        net = net_scenario(BLK, tom, wm)
        scen = f"風力×{wm}" + ("＋泊3号" if tom else "")
        if not (wm == 2.0 and tom):
            add_curve(M26, scen, 1.0, wm, tom, "PF", pf_A26(1.0), net, Ks=list(range(0, 151)))
        if APRIME_PASS:
            add_curve(MAP, scen, 1.0, wm, tom, "PF", pf_Aprime(AP3, 1.0, wm), net, Ks=list(range(0, 151)))
if APRIME_PASS:
    add_curve(MAP, "泊3号再稼働", TH26, 1.0, True, "PF", pf_Aprime(AP3, TH26, 1.0), net_tom, Ks=list(range(0, 151)))
    add_curve(MAP, "現状", TH26, 1.0, False, "PF", pf_Aprime(AP3, TH26, 1.0), net_now, Ks=list(range(0, 151)))

CV = add_bases(pd.concat(curves, ignore_index=True))
CV.round(4).to_csv(os.path.join(PROC, "pi_k_curve_v3.csv"), index=False, encoding="utf-8-sig")
print(f"  saved pi_k_curve_v3.csv（{len(CV)} 行）")

# ---------------------------------------------------------------- π=0・半減の K
BASES = {"実績整合": "π_実績整合", "モデル直値": "π_モデル直値", "旧0.81PF": "π_旧0.81PF", "旧裾補正": "π_旧裾補正"}
GKEYS = ["価格モデル", "シナリオ", "θ", "風力倍率", "泊3号", "フリート配分", "刻み(万kW)"]


def crossing(K, y, target):
    for i in range(1, len(K)):
        if (y[i - 1] - target) > 0 >= (y[i] - target):
            return float(np.interp(0.0, [y[i] - target, y[i - 1] - target], [K[i], K[i - 1]]))
    return np.nan


zrows = []
for key, g in CV.groupby(GKEYS, sort=False):
    g = g.sort_values("K(万kW)")
    if len(g) < 20:
        continue
    K = g["K(万kW)"].to_numpy(float)
    r = dict(zip(GKEYS, key))
    for bl, col in BASES.items():
        y = g[col].to_numpy()
        r[f"π(0)_{bl}"] = y[0]
        r[f"π=0のK_{bl}"] = crossing(K, y, 0.0)
        r[f"半減のK_{bl}"] = crossing(K, y, y[0] / 2)
        for kk in (25, 30, 50):
            if kk in K:
                r[f"π({kk})/π(0)_{bl}"] = y[K == kk][0] / y[0]
    zrows.append(r)
ZERO = pd.DataFrame(zrows)
ZERO.round(4).to_csv(os.path.join(PROC, "pi_k_curve_v3_zero.csv"), index=False, encoding="utf-8-sig")


def sel(model=M26, scen="現状", theta=1.0, mode="完全予見の増分貪欲（主）", slice_=SLICE, wm=None):
    d = CV[(CV["価格モデル"] == model) & (CV["シナリオ"] == scen) & (np.isclose(CV["θ"], round(theta, 3)))
           & (CV["フリート配分"] == mode) & (CV["刻み(万kW)"].astype(str) == str(slice_))]
    if wm is not None:
        d = d[d["風力倍率"] == wm]
    return d.set_index("K(万kW)")


KT = [0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 100, 150]
print("\n=== 表8.4 相当（仕様A 26、θ=1、完全予見フリート、刻み1万kW）: 実績整合 / モデル直値 / 旧0.81PF ===")
for scen in SC:
    d = sel(scen=scen)
    print(scen, " ".join(f"K{k}:{d.loc[k,'π_実績整合']:,.0f}/{d.loc[k,'π_モデル直値']:,.0f}/{d.loc[k,'π_旧0.81PF']:,.0f}" for k in KT))
print("\n=== 同（仕様A 13、水準固定） ===")
for scen in SC:
    d = sel(model=M13, scen=scen)
    print(scen, " ".join(f"K{k}:{d.loc[k,'π_実績整合']:,.0f}/{d.loc[k,'π_モデル直値']:,.0f}/{d.loc[k,'π_旧0.81PF']:,.0f}" for k in KT))
print("\n=== capture_c(K)（限界参入者の戦略c / π_PF） ===")
for model, mode in ((M26, "完全予見の増分貪欲（主）"), (M26, "戦略cの窓"), (M26, "半々"), (M13, "完全予見の増分貪欲（主）"),
                    (M13, "戦略cの窓"), (MB, "完全予見の増分貪欲（主）"), (MB, "戦略cの窓"), (MB, "半々")):
    d = sel(model=model, mode=mode)
    print(f"{model[:12]} {mode[:8]}:", " ".join(f"K{k}:{d.loc[k,'capture_c']:.3f}" for k in KT if k in d.index))
for th in (TH26,):
    for mode in ("完全予見の増分貪欲（主）", "戦略cの窓", "半々"):
        d = sel(theta=th, mode=mode)
        print(f"θ={th:.2f} {mode[:8]}:", " ".join(f"K{k}:{d.loc[k,'capture_c']:.3f}" for k in KT if k in d.index))
print("\n=== π=0 の K（万kW） ===")
print(ZERO[ZERO["刻み(万kW)"].astype(str) == str(SLICE)][GKEYS[:6] + [f"π=0のK_{b}" for b in BASES] + [f"半減のK_{b}" for b in BASES]]
      .round(1).to_string(index=False))
print("\n=== 刻みの感応度（仕様A 26、θ=1、現状、π_旧0.81PF と π_実績整合） ===")
for sl in ("10（旧格子の再現: K=25 は実際30）", 10.0, 5.0, 2.5, SLICE, 0.5):
    d = sel(slice_=sl)
    print(f"刻み{sl}:", " ".join(f"K{k}:{d.loc[k,'π_旧0.81PF']:,.0f}/{d.loc[k,'π_実績整合']:,.0f}" for k in KS_SENS if k in d.index))
_old = pd.read_csv(os.path.join(PROC, "pi_k_curve_v2.csv"))
_old = _old[_old["シナリオ"].str.startswith("現状")].set_index("K(万kW)")["π_実現可能(円/kW-年)"]
_rep = sel(slice_="10（旧格子の再現: K=25 は実際30）")["π_旧0.81PF"]
print("旧CSV（pi_k_curve_v2.csv 現状）との差:", {k: round(_rep.loc[k] - _old.loc[k], 1) for k in (0, 10, 25, 50, 100, 150)})

# ---------------------------------------------------------------- (3) θ*
print("\n[3] 損益分岐の θ* ...")


def crf(r, n=20):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def c_req(capex_man, wacc):
    return 4 * capex_man * 1e4 * crf(wacc) + C_FIX


CASES = {"8.4 標準（c_req 3.45万・容量1.25万）": (34_500.0, 12_500.0), "8.4 楽観（c_req 3.2万・容量1.25万）": (32_000.0, 12_500.0),
         "8.4 保守（c_req 3.7万・容量0.83万）": (37_000.0, 8_300.0)}
for capex, wacc in ((6.8, 0.06), (6.8, 0.05), (6.8, 0.08), (6.8, 0.09), (4.0, 0.06), (2.3, 0.06)):
    CASES[f"9.4 式（資本費{capex}万円/kWh・WACC{int(wacc*100)}%・容量1.25万）"] = (c_req(capex, wacc), 12_500.0)
GROSS = {"実績整合": lambda d, lam: lam * d["c"], "モデル直値": lambda d, lam: d["c"],
         "旧0.81PF": lambda d, lam: CAPTURE_OLD * d["π_PF"], "旧裾補正": lambda d, lam: CAPTURE_OLD * TAIL * d["π_PF"]}


def a_at(d, base, lam, K):
    v = GROSS[base](d, lam)
    return float(np.interp(K, d.index.to_numpy(float), v.to_numpy(float)))


th_rows = []
prop_rows = []
for model, mode in ((M26, "完全予見の増分貪欲（主）"), (M26, "戦略cの窓"), (M13, "完全予見の増分貪欲（主）"),
                    (MAP if APRIME_PASS else None, "完全予見の増分貪欲（主）")):
    if model is None:
        continue
    lam = LAMBDA[model]
    thetas = [1.0] + ([TH26, TH22, 3.0] if (model == M26 and mode.startswith("完全")) else ([TH26] if model in (M26, MAP) else []))
    dd = {th: sel(model=model, theta=th, mode=mode) for th in thetas}
    for base in GROSS:
        for kl, Kx in K_EXO.items():
            if Kx > dd[1.0].index.max():
                continue
            a = {th: a_at(dd[th], base, lam, Kx) for th in thetas}
            if len(thetas) > 1:
                prop_rows.append({"価格モデル": model, "フリート配分": mode, "基準": base, "K_exo(万kW)": kl,
                                  **{f"a(θ={th:.2f})/(θ·a(1))": a[th] / (th * a[1.0]) for th in thetas[1:]}})
            if len(thetas) >= 3:
                A = np.column_stack([np.ones(len(thetas)), thetas])
                al, be = np.linalg.lstsq(A, np.array([a[t] for t in thetas]), rcond=None)[0]
                resid = max(abs(al + be * t - a[t]) for t in thetas)
            else:
                al, be, resid = np.nan, np.nan, np.nan
            for case, (creq, kp) in CASES.items():
                need = creq - kp + WHEEL
                ts_prop = need / a[1.0] if a[1.0] > 0 else np.inf          # 粗収益が0以下ならどの θ でも開かない
                ts_dir = ((need - al) / be if be > 0 else np.inf) if np.isfinite(be) else np.nan
                th_rows.append({"価格モデル": model, "フリート配分": mode, "基準": base, "K_exo(万kW)": kl, "K_exo値": Kx, "ケース": case,
                                "c_req(円/kW-年)": creq, "κP_cap(円/kW-年)": kp, "必要粗収益(円/kW-年)": need,
                                "a(K_exo;θ=1)(円/kW-年)": a[1.0], "θ*（比例）": ts_prop, "θ*（直接解）": ts_dir,
                                "直接解の当てはめ最大残差(円)": resid, "θ*/1.57": ts_prop / TH26, "θ*/1.72": ts_prop / TH22,
                                "θ*/1.22": ts_prop / 1.22})
TS = pd.DataFrame(th_rows)
# λ の95%区間を実績整合（K=0）に反映した行
for case, (creq, kp) in CASES.items():
    need = creq - kp + WHEEL
    a0 = sel()["c"].loc[0]
    for lab, lam in (("実績整合（λ下限95）", LAM_CI[0]), ("実績整合（λ上限95）", LAM_CI[1])):
        TS = pd.concat([TS, pd.DataFrame([{"価格モデル": M26, "フリート配分": "完全予見の増分貪欲（主）", "基準": lab, "K_exo(万kW)": "0（主）",
                                           "K_exo値": 0.0, "ケース": case, "c_req(円/kW-年)": creq, "κP_cap(円/kW-年)": kp,
                                           "必要粗収益(円/kW-年)": need, "a(K_exo;θ=1)(円/kW-年)": lam * a0, "θ*（比例）": need / (lam * a0),
                                           "θ*/1.57": need / (lam * a0) / TH26, "θ*/1.72": need / (lam * a0) / TH22, "θ*/1.22": need / (lam * a0) / 1.22}])],
                       ignore_index=True)
PROP = pd.DataFrame(prop_rows)
# 損益分岐の年間固定費と資本費（K=0）
be_rows = []
for model in (M26, M13) + ((MAP,) if APRIME_PASS else ()):
    d1 = sel(model=model)
    for base in GROSS:
        a1 = a_at(d1, base, LAMBDA[model], 0.0)
        for th in (1.0, 1.22, TH26, TH22):
            for kl, kp in KP_CAP.items():
                afc = th * a1 - WHEEL + kp - C_FIX
                for wacc in (0.06, 0.08):
                    be_rows.append({"価格モデル": model, "基準": base, "θ": round(th, 3), "容量収入": kl, "WACC": wacc,
                                    "損益分岐の年間固定費(円/kW-年)": afc, "損益分岐の資本費(万円/kWh)": afc / (4 * crf(wacc)) / 1e4})
BE = pd.DataFrame(be_rows)
TS["区分"] = "θ*"
PROP["区分"] = "比例の確認"
BE["区分"] = "損益分岐の資本費"
pd.concat([TS, PROP, BE], ignore_index=True).round(4).to_csv(os.path.join(PROC, "theta_star_v3.csv"), index=False, encoding="utf-8-sig")
print("比例の確認（a(θ)/(θ·a(1))、K_exo 別）:")
print(PROP.round(4).to_string(index=False))
main = TS[(TS["価格モデル"] == M26) & (TS["フリート配分"] == "完全予見の増分貪欲（主）")]
print("\nθ*（仕様A 26、完全予見フリート、比例）: 行=ケース×K_exo、列=基準")
print(main.pivot_table(index=["ケース", "K_exo(万kW)"], columns="基準", values="θ*（比例）", sort=False).round(2).to_string())
print("\n直接解との差の最大:", (main["θ*（直接解）"] - main["θ*（比例）"]).abs().max().round(4))
print("\nθ*（仕様A 13、K=0）:")
print(TS[(TS["価格モデル"] == M13) & (TS["K_exo値"] == 0)].pivot_table(index="ケース", columns="基準", values="θ*（比例）", sort=False).round(2).to_string())
print("\nθ*（戦略c の窓のフリート、仕様A 26）:")
print(TS[(TS["価格モデル"] == M26) & (TS["フリート配分"] == "戦略cの窓") & TS["ケース"].str.contains("標準|6%")]
      .pivot_table(index=["ケース", "K_exo(万kW)"], columns="基準", values="θ*（比例）", sort=False).round(2).to_string())
print("\n損益分岐の資本費（万円/kWh、K=0、容量1.25万、WACC6%）:")
print(BE[(BE["容量収入"] == "1.25万") & (BE["WACC"] == 0.06)].pivot_table(index=["価格モデル", "基準"], columns="θ",
      values="損益分岐の資本費(万円/kWh)", sort=False).round(2).to_string())

# ---------------------------------------------------------------- IRR（L-5）
print("\n[3b] IRR ...")
INVEST = 4 * 68_000.0


def irr(cf):
    f = lambda r: -INVEST + cf * (1 - (1 + r) ** -20) / r if abs(r) > 1e-12 else -INVEST + 20 * cf
    if cf <= 0:
        return np.nan
    return optimize.brentq(f, -0.5, 1.0)


FY22 = FYM == 2022
pf22, c22 = annual(D_ACT["pf"], FYM, FY22), annual(D_ACT["c"], FYM, FY22)
irr_rows = []
for lab, a in (("FY2022 実績価格・戦略c の実績", c22), ("FY2022 実績価格・0.81×完全予見粗利", CAPTURE_OLD * pf22),
               ("FY2022 実績価格・完全予見粗利（上界）", pf22)):
    cf = a - WHEEL + 12_500.0 - C_FIX
    irr_rows.append({"ケース": lab, "θ": np.nan, "基準": "実績価格", "粗収益a(円/kW-年)": a, "年間CF(円/kW)": cf, "IRR": irr(cf),
                     "NPV@3%(円/kW)": -INVEST + cf / crf(0.03), "NPV@6%(円/kW)": -INVEST + cf / crf(0.06)})
d1 = sel()
for base in GROSS:
    a1 = a_at(d1, base, LAMBDA[M26], 0.0)
    for th in (1.0, 1.22, TH26, TH22):
        cf = th * a1 - WHEEL + 12_500.0 - C_FIX
        irr_rows.append({"ケース": "仕様A（26）K=0", "θ": round(th, 3), "基準": base, "粗収益a(円/kW-年)": th * a1, "年間CF(円/kW)": cf,
                         "IRR": irr(cf), "NPV@3%(円/kW)": -INVEST + cf / crf(0.03), "NPV@6%(円/kW)": -INVEST + cf / crf(0.06)})
IRR = pd.DataFrame(irr_rows)
IRR.round(4).to_csv(os.path.join(PROC, "equilibrium_v3_irr.csv"), index=False, encoding="utf-8-sig")
print(f"FY2022 実績: 完全予見 {pf22:,.0f}  戦略c {c22:,.0f}（capture {c22 / pf22:.3f}）")
print(IRR.round(4).to_string(index=False))

# ---------------------------------------------------------------- (5) DC 需要の上端外挿（A8-4）
print("\n[5] 上端の扱いと DC 需要 ...")
EVR = np.where(EV)[0]
NET_EV = NETM[EV]


def pf_of(P):
    s = np.sort(P, 1)
    return annual(np.maximum(0, ETA * s[:, -4:].sum(1) - s[:, :4].sum(1)), FYM[EV], np.ones(T, bool))


def above_top(net, G):
    ab = np.zeros_like(net, bool)
    for s in range(4):
        m = SEASM[EV] == s
        ab[m] = net[m] > G[s][0][-1]
    return ab


# 実績の上位十分位の傾き（気象学的季節、円/kWh per 100MW）と最上位8ビンの傾き
slope_tab = []
for s in range(4):
    m = SEASM[EV] == s
    x, y = NET_EV[m], PACTM[EV][m]
    q = np.quantile(x, np.linspace(0, 1, 11))
    b = np.clip(np.searchsorted(q, x, side="right") - 1, 0, 9)
    med = [np.median(y[b == k]) for k in range(10)]
    ctr = [x[b == k].mean() for k in range(10)]
    slope_tab.append({"季節": ["冬", "春", "夏", "秋"][s], "実績の上位十分位の傾き": (med[9] - med[8]) / (ctr[9] - ctr[8]) * 100,
                      "仕様A 最上位8ビンの傾き": top_slope(G13, s) * 100})
print(pd.DataFrame(slope_tab).round(2).to_string(index=False))
up_rows = []
LEVERS = {"②泊3号": -TOMARI, "④DC+80万kW": 800.0, "⑤泊+DC": 800.0 - TOMARI}
# (d) 実績の季節別上位十分位の傾き（監査の指定）、(e) 冬・夏を 8.6 の上端の傾きの上限（冬0.81・夏1.15）に置き換えた版
SL_ACT = {s: max(slope_tab[s]["実績の上位十分位の傾き"], 0.0) / 100 for s in range(4)}
SL_86 = {**SL_ACT, 0: 0.81 / 100, 2: 1.15 / 100}
for mult, lab in ((0.0, "(a) 一定（現行）"), (1.0, "(b) 最上位8ビンの傾きで線形外挿"), (2.0, "(c) 傾き2倍"),
                  (SL_ACT, "(d) 実績の季節別上位十分位の傾き"), (SL_86, "(e) (d) の冬・夏を 8.6 の上端の傾きの上限（0.81・1.15）に")):
    for spec in ("仕様A（13）", "分断混合（13）"):
        f = (lambda n, mm=mult: price_A(n, G13, MU13[EV], 1.0, SEASM[EV], upper_mult=mm)) if spec.startswith("仕様A") else \
            (lambda n, mm=mult: price_B(n, EVR, upper_mult=mm)[0])
        base = pf_of(f(NET_EV))
        r = {"上端の扱い": lab, "仕様": spec, "基準PF(円/kW-年)": base}
        for lv, dn in LEVERS.items():
            Pn = f(NET_EV + dn)
            r[f"ΔPF {lv}"] = pf_of(Pn) - base
            ab = above_top(NET_EV + dn, G13)
            o = np.argsort(price_A(NET_EV + dn, G13, MU13[EV], 1.0, SEASM[EV]), 1)
            r[f"上端より上の時間割合(%) {lv}"] = ab.mean() * 100
            r[f"上位4hのうち上端より上(%) {lv}"] = np.take_along_axis(ab, o[:, -4:], 1).mean() * 100
        up_rows.append(r)
UP = pd.DataFrame(up_rows)
UP.round(2).to_csv(os.path.join(PROC, "dc_upper_end_sensitivity.csv"), index=False, encoding="utf-8-sig")
print(UP[["上端の扱い", "仕様", "基準PF(円/kW-年)"] + [f"ΔPF {lv}" for lv in LEVERS]].round(0).to_string(index=False))
print(UP[["上端の扱い", "仕様"] + [f"上端より上の時間割合(%) {lv}" for lv in LEVERS] + [f"上位4hのうち上端より上(%) {lv}" for lv in LEVERS]]
      .iloc[:1].round(1).to_string(index=False))

# ---------------------------------------------------------------- (6) K=0 の変種で戦略c を直接計算（8.2 のベースロード減・10.1 の負価格）
print("\n[6] K=0 の変種（戦略c の直接計算と、粗収益×8,427/6,695 の換算の比較）...")
TOM2, TOMALL = 2 * TOMARI, (579_000 * 2 + 912_000) * 0.9 / 1000
EXT_LO = {}
for s in range(4):
    x, y = G13[s]
    i0 = int(np.argmax(y > FLOOR + 0.001))                  # 最初の打ち切られていないビン（33 と同じ）
    EXT_LO[s] = (x[i0], y[i0], np.polyfit(x[i0:i0 + 8], y[i0:i0 + 8], 1)[0])


def price_ext(net):
    """33 の「外挿・下限あり」: 仕様A（13）の g の下端を最下位の打ち切られていない8ビンの傾きで線形外挿し、0.01円で打ち切る"""
    out = np.empty_like(net, dtype=float)
    for s in range(4):
        m = SEASB == s
        x, y = G13[s]
        xa, ya, sl = EXT_LO[s]
        v = np.interp(net[m], x, y, right=y[-1])
        lo = net[m] < xa
        v[lo] = ya + sl * (net[m][lo] - xa)
        out[m] = v
    return np.maximum(np.maximum(out, FLOOR) + MU13B, FLOOR)


def price_negfloor(net, theta, depth):
    """32 の段差モデル: 26 の g+μ が下限に達する時間だけ −depth 円（depth=None は現行の下限0.01円）"""
    base = np.maximum(g_curve(net, G26, SEASB) + MU26B, FLOOR)
    p = np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)
    return p if depth is None else np.where(base <= FLOOR + 1e-9, -depth, p)


CONV = C_ACT / (CAPTURE_OLD * c0_of(M26)[1])                # 旧基準→実績整合の一律換算（=8,427/6,695）
k0_rows = []
VARS = [("8.2 ベースロード減", "仕様A（13）", lambda n: price_A(n, G13, MU13B, 1.0, SEASB)),
        ("8.2 ベースロード減", "外挿・下限あり（33）", price_ext),
        ("8.2 ベースロード減", "分断混合（13）", lambda n: price_B(n, BLK)[0])]
for grp, model, f in VARS:
    lam = None
    for sh_lab, dnet in (("現状", 0.0), ("泊3号（−821MW）", -TOMARI), ("泊2基相当（−1,642MW）", -TOM2), ("泊全基（−1,863MW）", -TOMALL)):
        d = daily_eval(f(NETB + dnet), W_B)
        pf, c = annual(d["pf"], FYB, EVB), annual(d["c"], FYB, EVB)
        lam = C_ACT / c if lam is None else lam                 # 各仕様の現状・K=0 で実績の戦略c に校正
        k0_rows.append({"区分": grp, "価格モデル": model, "シナリオ": sh_lab, "下限": "現行（0.01円）", "θ": 1.0, "π_PF(0)": pf, "c(0)": c,
                        "capture_c": c / pf, "校正係数λ": lam})
for scen, (tom, wm) in SC.items():
    for th in (1.0, TH26, 3.0):
        for depth, dl in ((None, "現行（0.01円）"), (0.0, "0円"), (5.0, "−5円"), (10.0, "−10円")):
            d = daily_eval(price_negfloor(net_scenario(BLK, tom, wm), th, depth), W_B)
            pf, c = annual(d["pf"], FYB, EVB), annual(d["c"], FYB, EVB)
            k0_rows.append({"区分": "10.1 負価格（段差モデル）", "価格モデル": M26, "シナリオ": scen, "下限": dl, "θ": round(th, 3),
                            "π_PF(0)": pf, "c(0)": c, "capture_c": c / pf, "校正係数λ": LAMBDA[M26]})
K0V = pd.DataFrame(k0_rows)
_need84 = CASES["8.4 標準（c_req 3.45万・容量1.25万）"][0] - 12_500 + WHEEL
_need94 = c_req(6.8, 0.06) - 12_500 + WHEEL
K0V["π_実績整合(0)"] = K0V["校正係数λ"] * K0V["c(0)"] - WHEEL
K0V["π_旧0.81PF(0)"] = CAPTURE_OLD * K0V["π_PF(0)"] - WHEEL
K0V["π_換算(旧×8427/6695)(0)"] = CONV * CAPTURE_OLD * K0V["π_PF(0)"] - WHEEL
K0V["θ*_8.4標準_実績整合"] = _need84 / (K0V["校正係数λ"] * K0V["c(0)"] / K0V["θ"])        # θ≠1 の行も FY2023〜25=1 の尺度
K0V["θ*_9.4式_実績整合"] = _need94 / (K0V["校正係数λ"] * K0V["c(0)"] / K0V["θ"])
K0V["θ*_8.4標準_旧"] = _need84 / (CAPTURE_OLD * K0V["π_PF(0)"] / K0V["θ"])
K0V["θ*_9.4式_旧"] = _need94 / (CAPTURE_OLD * K0V["π_PF(0)"] / K0V["θ"])
K0V["θ*_9.4式_換算"] = _need94 / (CONV * CAPTURE_OLD * K0V["π_PF(0)"] / K0V["θ"])
# 負価格の段差モデルでは下限時間の価格 −c 円が θ で動かないので、収益は θ に比例しない（a(θ)≈α+βθ、α>0）。
# 比例を仮定した θ*（上の列、32 と同じ）は参入に有利な側に偏るので、θ=1・1.57・3.0 の3点に a=α+βθ を当てはめて直接解く。
for col in ("θ*_8.4標準_実績整合_直接解", "θ*_9.4式_実績整合_直接解", "θ*_8.4標準_旧_直接解", "θ*_9.4式_旧_直接解", "直接解の当てはめ最大残差(円)"):
    K0V[col] = np.nan
_neg = K0V["区分"].str.startswith("10.1")
for _, g in K0V[_neg].groupby(["シナリオ", "下限"], sort=False):
    A = np.column_stack([np.ones(len(g)), g["θ"].to_numpy(float)])
    res = 0.0
    for base, a in (("実績整合", (g["校正係数λ"] * g["c(0)"]).to_numpy(float)), ("旧", (CAPTURE_OLD * g["π_PF(0)"]).to_numpy(float))):
        al, be = np.linalg.lstsq(A, a, rcond=None)[0]
        res = max(res, float(np.abs(A @ [al, be] - a).max()))
        K0V.loc[g.index, f"θ*_8.4標準_{base}_直接解"] = (_need84 - al) / be
        K0V.loc[g.index, f"θ*_9.4式_{base}_直接解"] = (_need94 - al) / be
    K0V.loc[g.index, "直接解の当てはめ最大残差(円)"] = res
K0V.round(4).to_csv(os.path.join(PROC, "k0_variants_direct_c_v3.csv"), index=False, encoding="utf-8-sig")
print(K0V[["区分", "価格モデル", "シナリオ", "下限", "θ", "π_PF(0)", "c(0)", "capture_c", "π_実績整合(0)", "π_換算(旧×8427/6695)(0)", "π_旧0.81PF(0)",
           "θ*_8.4標準_実績整合", "θ*_9.4式_実績整合", "θ*_9.4式_換算"]].round(3).to_string(index=False))
print("\n10.1 負価格: θ* の比例（32 と同じ）と直接解（a=α+βθ を θ=1・1.57・3.0 に当てはめ）")
print(K0V[_neg & (K0V["θ"] == 1.0)][["シナリオ", "下限", "θ*_9.4式_実績整合", "θ*_9.4式_実績整合_直接解", "θ*_8.4標準_実績整合_直接解",
                                       "θ*_9.4式_旧", "θ*_9.4式_旧_直接解", "直接解の当てはめ最大残差(円)"]].round(3).to_string(index=False))

# ---------------------------------------------------------------- 図
# (a) を上、(b) を下に並べる。Word では本文幅15.5cm（6.1インチ）で載せるので、その大きさで描き、図中の文字は8.5〜9.5pt にする
print("\n[図] pi_k_curve_v3.png ...")
FIG_W = 6.1
FS_TICK, FS_LAB, FS_TTL, FS_LEG, FS_ANN = 8.5, 9.0, 9.5, 8.5, 8.5
C_BLUE, C_ORG, C_PUR, C_GRY = "#0079C2", "#D95B20", "#7B3F9E", "#8C8C8C"
fig, axes = plt.subplots(2, 1, figsize=(FIG_W, 5.9), layout="constrained")
fig.get_layout_engine().set(h_pad=0.04, hspace=0.06)
ax = axes[0]
d = sel()
dc = sel(mode="戦略cの窓")
Kx = d.index.to_numpy()
mK = Kx <= 150
ax.axhline(0, color=GRAY, lw=0.7)
for col, c_, ls, lab in (("π_実績整合", C_BLUE, "-", "実績整合ケース（主）"),
                         ("π_モデル直値", C_ORG, "--", "モデル直値（モデル価格の上の戦略 c）")):
    ax.plot(Kx[mK], d[col].to_numpy()[mK], color=c_, lw=1.5, ls=ls, label=lab)
    z = crossing(Kx[mK].astype(float), d[col].to_numpy()[mK], 0.0)
    ax.plot([z], [0], marker="o", ms=4.5, color=c_, mec="white", mew=0.8, zorder=5)
ax.plot(dc.index, dc["π_実績整合"], color=C_BLUE, lw=1.0, ls="-.", label="実績整合ケース・フリートも戦略 c の窓（感応度）")
z0 = {b: ZERO[(ZERO["価格モデル"] == M26) & (ZERO["シナリオ"] == "現状") & (ZERO["θ"] == 1.0)
               & (ZERO["フリート配分"] == "完全予見の増分貪欲（主）") & (ZERO["刻み(万kW)"].astype(str) == str(SLICE))][f"π=0のK_{b}"].iloc[0]
      for b in ("実績整合", "モデル直値")}
ax.text(z0["実績整合"] + 2, 350, f"π=0：実績整合ケース {z0['実績整合']:.0f}万kW\nモデル直値 {z0['モデル直値']:.0f}万kW",
        fontsize=FS_ANN, color=GRAY, va="bottom")
ax.set_xlim(0, 150)
ax.set_ylim(-3_200, 7_600)
ax.set_xlabel("フリート容量 K（万kW、4時間換算）", fontsize=FS_LAB, color=GRAY)
ax.set_ylabel("実現可能収益 π(K)（円/kW-年）", fontsize=FS_LAB, color=GRAY)
ax.set_title("(a) π(K)（θ=1、現状）", fontsize=FS_TTL, loc="left", pad=4)
ax.legend(fontsize=FS_LEG, frameon=False, loc="upper right", handlelength=2.2, borderaxespad=0.2, labelspacing=0.3)
ax.grid(axis="y", color="#E5E5E5", lw=0.5)
ax2 = axes[1]
ths = np.linspace(0, 4.2, 100)
for base, c_, ls in (("実績整合", C_BLUE, "-"), ("モデル直値", C_ORG, "--")):
    a1 = a_at(d, base, LAMBDA[M26], 0.0)
    ax2.plot(ths, ths * a1 - WHEEL, color=c_, lw=1.5, ls=ls, label={"実績整合": "実績整合ケース"}.get(base, base))
need84 = 34_500 - 12_500
need94 = c_req(6.8, 0.06) - 12_500
for v, lab, ls in ((need94, f"参入に必要な水準（式(4.6)、WACC 6%）{need94:,.0f}円", "--"), (need84, f"同（標準ケース）{need84:,.0f}円", ":")):
    ax2.axhline(v, color=C_GRY, lw=0.9, ls=ls)
    ax2.text(0.05, v + (350 if v == need94 else -400), lab, fontsize=FS_ANN, color=GRAY, ha="left",
             va="bottom" if v == need94 else "top")
# 価格水準の縦線と年度のラベル（ラベルは線の脇に、互いに重ならない高さで置く）
for th, lab, ha, dx, yl in ((1.0, "FY2023〜25", "right", -0.03, 31_200), (TH26, "FY2026上期", "right", -0.03, 28_600),
                            (TH22, "FY2022", "left", 0.03, 31_200)):
    ax2.axvline(th, color="#CCCCCC", lw=0.7)
    ax2.text(th + dx, yl, lab, fontsize=FS_ANN, color=GRAY, ha=ha, va="top")
for base, c_, ha, dx in (("実績整合", C_BLUE, "right", -0.04), ("モデル直値", C_ORG, "left", 0.04)):
    ts = main[(main["基準"] == base) & (main["K_exo値"] == 0) & main["ケース"].str.contains("資本費6.8万円/kWh・WACC6%")]["θ*（比例）"].iloc[0]
    ax2.plot([ts], [need94], marker="o", ms=4.5, color=c_, mec="white", mew=0.8, zorder=5)
    ax2.plot([ts, ts], [0, need94], color=c_, lw=0.7, ls=(0, (2, 2)))
    ax2.text(ts + dx, 600, f"θ*={ts:.2f}", color=GRAY, fontsize=FS_ANN, ha=ha, va="bottom",
             bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
ax2.set_xlim(0, 4.2)
ax2.set_ylim(-2_500, 31_800)
ax2.set_xlabel("価格水準係数 θ（FY2023〜25=1）", fontsize=FS_LAB, color=GRAY)
ax2.set_ylabel("π(0; θ)（円/kW-年）", fontsize=FS_LAB, color=GRAY)
ax2.set_title("(b) K=0 の収益と参入に必要な水準", fontsize=FS_TTL, loc="left", pad=4)
ax2.legend(fontsize=FS_LEG, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.6), handlelength=2.2, labelspacing=0.3)
ax2.grid(axis="y", color="#E5E5E5", lw=0.5)
for a_ in axes:
    a_.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}".replace("-", "−")))
    for sp_ in ("top", "right"):
        a_.spines[sp_].set_visible(False)
    a_.tick_params(colors=GRAY, labelsize=FS_TICK, length=2.5, pad=2)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "pi_k_curve_v3.png"), dpi=300, bbox_inches="tight", pad_inches=0.03)
print("saved figures/hokkaido/pi_k_curve_v3.png")
