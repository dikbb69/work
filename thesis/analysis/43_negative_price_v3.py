#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""負価格シナリオ v3: 表10.1 の π(K) と θ* の直接解、下限張り付き時間の再現度の感応度、実績価格での直接計算、
8.6 の「線形外挿は下限が削る価値の上限側」の検証

目的（決定事項 D1・D2、監査 A10-2・A10-3・L-10 への対応）:
  旧版（32）は、段差モデル（価格が下限に達する時間だけ −c 円/kWh）の収益を 0.81·π_PF とし、θ* を比例の式
  need/(0.81·π_PF(θ=1)) で解いた。しかし −c は θ で伸縮しない（32 の predict() も伸縮させない）ので、収益は θ に比例せず
  （a(θ)≈α+βθ、α>0）、比例の式は θ* を参入に有利な側に偏らせる。本スクリプトは戦略c の実現粗利を直接計算した
  実績整合の収益（41 の D1）で π(K) を求め、θ* を θ について直接解く。

手法:
  (0) 部品: 41_equilibrium_v3.py の前半（"curves = []" の行より前の定義部分）を exec で読み込む（to_csv は無効、
      標準出力は捨てる。41 自体は実行しない）。評価は FY2023〜25 の1,096日、年度合計の3年平均（円/kW-年）。
      戦略c は直近29日・同じ曜日区分の平均価格のランク（5日以上、同値は均等配分、最初の履歴は FY2022 末の同じ変換を
      かけたモデル価格）。蓄電池 1MW/4MWh・往復効率0.85（放電側）・1日1サイクル。充電従量負担1,752円/kW-年を控除。
  (1) 段差モデル（主、32 の再現）: 仕様A（26）の base = max{0.01, g(net)+μ} が 0.01 に達する時間だけ価格を −c とし、
      それ以外は 0.01 + θ(base − 0.01)。c は 現行（0.01円のまま）・0円・5円・10円。−c は θ で伸縮させない
      （c は余剰時に運転を続ける電源の支払意思の目安で、燃料価格の水準には依存しないと置く）。
      感応度（下限張り付き時間の再現度。モデル 115h/年は実績 202.7h/年の57%）:
        (1b) 外挿: 32 の predict に 33 の線形外挿の g（最初の打ち切られていないビンから8ビンの傾き）を入れ、
             g_ext+μ（下限なしの潜在価格）が 0.01 以下になる時間だけ −c（現行は max{0.01, g_ext+μ}）。
             33・42 の「外挿・下限あり」は g_ext を 0.01 で打ち切ってから μ を足す max{0.01, max(g_ext,0.01)+μ} なので、
             現行の行の価格と下限の時間は少し違う（泊＋風力2倍・K=0 で下限1,092h 対 1,017h、π(0) 6,027 対 6,052円）。
        (1c) 下限時間の較正: 現状・K=0 で季節（気象学的4季）別のモデルの下限張り付き時間が実績と同じになるよう、
             base の閾値 τ_s 以下の時間を下限の時間とする（実績のほうが少ない季節は τ_s=0.01 のまま）。
        (1d) 仕様A′（段差、決定事項 D4）: μ を (気象学的季節, 時刻, 日次風力三分位) に依存させた 41 の仕様A′ の base
             が 0.01 に達する時間だけ −c。風力の反実仮想では日次風力が三分位の境界を越えると上の三分位の μ を使う
             （最上位より先へは外挿しない）。λ は仕様A′ の現状・現行・K=0 で校正。
      シナリオは 現状（θ=1）・FY2026上期水準（θ=1.567）・泊3号再稼働（−820.8MW）・泊＋風力2倍。π(K) は増分貪欲
      （刻み1万kW、目標の K に正確に到達）で K=0〜150。基準は 実績整合（λ＝実績の戦略c 8,427円 ÷ 各仕様の現状・現行・
      θ=1・K=0 のモデル c、in-sample 校正）・モデル直値・旧（0.81·π_PF）。
  (2) θ*: 参入条件 a(0; θ, c) − 1,752 + κP_cap = c_req を θ について直接解く（brentq、a は各 θ で戦略c を計算し直す）。
      c_req は 9.4 の式（4h資本費×CRF(WACC,20年)＋0.53万＋0.69万）で、資本費2.3・4.0・6.8万円/kWh × 実効容量収入
      1.25・1.75・2.5万円（WACC 6%）と 8.4 の標準ケース（c_req 3.45万、容量1.25万）。比較のため 32 と同じ比例の値
      need/a(θ=1) も出す。θ* での残差 |π(0)+κP−c_req| を増分貪欲の関数で計算し直して ±5円以内であることを確かめる。
  (3) 実績価格での直接計算（現状のみ）: FY2023〜25 の実績価格（2022-02〜2026-03 の日の行列）のうち 0.011円以下の時間を
      −c に置き、完全予見粗利と戦略c の実現粗利を計算する（校正は不要）。θ は 0.01 + θ(p − 0.01) で伸縮し（−c は伸縮
      させない）、θ* を同じく直接解く。増分の捕捉率 Δc/ΔPF をモデルと比べる。
  (4) 8.6 の線形外挿（下限なし）が与える負の価格の深さ: 仕様A の 13（8.6 の v1）と 26（第10章の v2）で、g の下端を
      線形外挿し下限も外した価格 g_ext+μ が 0.01円を下回る時間の年間時間数・平均・中央値・10%点と、−5円・−10円より深い
      割合を、現状・泊3号・泊2基相当・全基・風力2倍・3倍（K=0）で出す（全時間と、各日の最安4時間に限った値。監査の
      「泊3号で−10円より深いのは20.4%」は後者の定義で、前者では14.5%）。「下限が削る価値」（各シナリオの増分のうち
      下限価格が削る分）を、線形外挿（下限あり−下限なし）と段差モデル（c=1〜10円）で比べ、外挿に相当する段差の深さ c を
      補間で求める。
  (5) 表10.2 の比: 実績の価格・出力で、下限張り付き時間の制御前の再エネ（太陽光＋風力）出力×(0.01+c) と、出力制御量×c の
      比を年度別と4〜6月どうしで出す（32 と同じ定義。T6 の negative_price_transfer_v2.csv は発電実績ベースも併記）。
出力: data/processed/negative_price_v3_pik.csv（π(K) の全曲線）、negative_price_v3_table101.csv（表10.1 の行）、
      negative_price_breakeven_v3.csv（θ* の格子、直接解と比例の値、残差）、negative_price_actual_v3.csv（実績価格での
      直接計算）、negative_price_extrap_depth_v3.csv（8.6 の外挿の負価格の深さと下限が削る価値）、
      negative_price_transfer_ratio_v3.csv（(5) 移転額と出力制御の影の価格の比、年度と4〜6月）、
      figures/hokkaido/negative_price_pi_k_v3.png
限界: 負の領域の供給曲線は 0.01円で打ち切られたデータから識別できないので、c は外生である。段差モデルの下限張り付き
      時間は、現状でも実績の57% しか再現せず、泊のシナリオでは下限張り付き時間の6〜7割が推定範囲外を 0.01円とする段差の
      仮定から生じる（外挿・較正の感応度で幅を示す）。実績価格での直接計算は現状についてだけ可能で、泊・風力の反実仮想は
      モデルに依存する。λ は K=0・θ=1・現行の下限で校正した in-sample の係数で、負価格の下での戦略c の取り分の変化は
      モデル価格の上の計算に依存する。部分均衡（揚水・連系線・入札行動は g に埋め込まれた歴史的応答のまま）で、
      負価格による火力・再エネの運転の変化（供給曲線の変化）は含めない。仕様A′ は同じ標本で μ を推定して検証した
      in-sample の仕様で（41）、変種の中から選んだことによる選択の偏りが残る。
"""
import contextlib
import io
import logging
import os

import numpy as np
import pandas as pd
from scipy import optimize
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
np.random.seed(SEED)                                  # 乱数は使わないが作法として固定
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

run_curve, daily_eval, annual = m41["run_curve"], m41["daily_eval"], m41["annual"]
g_curve, net_scenario = m41["g_curve"], m41["net_scenario"]
G26, G13, MU26B, MU13B, SEASB, BLK = m41["G26"], m41["G13"], m41["MU26B"], m41["MU13B"], m41["SEASB"], m41["BLK"]
W_B, FYB, EVB, W_M, EV, FYM = m41["W_B"], m41["FYB"], m41["EVB"], m41["W_M"], m41["EV"], m41["FYM"]
PACTM, SEASM, NETB = m41["PACTM"], m41["SEASM"], m41["NETB"]
FLOOR, ETA, WHEEL, C_FIX = m41["FLOOR"], m41["ETA"], m41["WHEEL"], m41["C_FIX"]
C_ACT, PF_ACT, TH26, TOMARI = m41["C_ACT"], m41["PF_ACT"], m41["TH26"], m41["TOMARI"]
AP3, aprime_mu, SEAS_DAY, wind_day_scenario = m41["AP3"], m41["aprime_mu"], m41["SEAS_DAY"], m41["wind_day_scenario"]


def mu_aprime(wm):
    """仕様A′ の μ（BLK の日、風力倍率 wm の日次風力で三分位を決める）"""
    return aprime_mu(AP3, SEAS_DAY[BLK], wind_day_scenario(BLK, wm))
CAPTURE_OLD = 0.81
KAPPA = 0.836
TOM2, TOMALL = 2 * TOMARI, (579_000 * 2 + 912_000) * 0.9 / 1000
print(f"41 の部品を読み込み: 実績の戦略c {C_ACT:,.1f}・完全予見 {PF_ACT:,.1f}円/kW-年（FY2023〜25）")


def crf(r, n=20):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def c_req(capex_man, wacc=0.06):
    return 4 * capex_man * 1e4 * crf(wacc) + C_FIX


def ext_params(G):
    E = {}
    for s in range(4):
        x, y = G[s]
        i0 = int(np.argmax(y > FLOOR + 0.001))         # 最初の打ち切られていないビン（33 と同じ）
        E[s] = (x[i0], y[i0], np.polyfit(x[i0:i0 + 8], y[i0:i0 + 8], 1)[0])
    return E


EXT = {"26": ext_params(G26), "13": ext_params(G13)}
GG = {"26": G26, "13": G13}
MUB = {"26": MU26B, "13": MU13B}


def g_ext(net, ver):
    out = np.empty_like(net, dtype=float)
    for s in range(4):
        m = SEASB == s
        x, y = GG[ver][s]
        xa, ya, sl = EXT[ver][s]
        v = np.interp(net[m], x, y, right=y[-1])
        lo = net[m] < xa
        v[lo] = ya + sl * (net[m][lo] - xa)
        out[m] = v
    return out


# 下限時間の較正（1c）: 現状・K=0 の季節別の下限張り付き時間を実績に合わせる閾値 τ_s（θ=1 の base の尺度）
BASE_NOW = np.maximum(g_curve(NETB, G26, SEASB) + MU26B, FLOOR)
ACT_FLOOR_EV = PACTM[EV] <= FLOOR + 0.001
TAU = {}
cal_rows = []
for s in range(4):
    ma, mb = SEASM[EV] == s, SEASB[EVB] == s
    n_act = int(ACT_FLOOR_EV[ma].sum())
    b = np.sort(BASE_NOW[EVB][mb])
    n_mod = int((b <= FLOOR + 1e-9).sum())
    TAU[s] = float(b[n_act - 1]) if n_act > n_mod else FLOOR + 1e-9
    cal_rows.append({"季節": ["冬", "春", "夏", "秋"][s], "実績の下限張り付き(h/年)": n_act / 3, "モデルの下限張り付き(h/年)": n_mod / 3,
                     "閾値τ(円/kWh)": TAU[s]})
CAL = pd.DataFrame(cal_rows)
print("下限張り付き時間（FY2023〜25、h/年）と較正の閾値:")
print(CAL.round(3).to_string(index=False))
TAUB = np.vectorize(TAU.get)(SEASB)


def price_neg(net, theta=1.0, depth=None, var="step", mu=None):
    """var: step（段差、主）・ext（外挿の g を 32 の predict に入れる）・cal（下限時間を実績に較正）・
    aprime（仕様A′ の μ で段差。mu に mu_aprime(wm) を渡す）"""
    if var == "ext":
        lat = g_ext(net, "26") + MU26B
        base = np.maximum(lat, FLOOR)
        flo = lat <= FLOOR + 1e-9
    elif var == "aprime":
        base = np.maximum(g_curve(net, G26, SEASB) + mu, FLOOR)
        flo = base <= FLOOR + 1e-9
    else:
        base = np.maximum(g_curve(net, G26, SEASB) + MU26B, FLOOR)
        flo = base <= (TAUB if var == "cal" else FLOOR + 1e-9)
    p = np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)
    p = np.where(flo, FLOOR, p)
    return p if depth is None else np.where(flo, -depth, p)


# 32 の段差モデルの再現（K=0、旧基準 π_PF）
_ns = pd.read_csv(os.path.join(PROC, "negative_price_scenarios.csv"))
SCEN = {"現状（θ=1）": (False, 1.0, 1.0), "FY2026上期水準（θ=1.567）": (False, 1.0, TH26), "泊3号再稼働（θ=1）": (True, 1.0, 1.0),
        "泊＋風力2倍（θ=1）": (True, 2.0, 1.0)}
SCEN32 = {"現状（θ=1）": "θ=1（FY2023-25水準）", "FY2026上期水準（θ=1.567）": f"θ={TH26:.2f}（FY2026上期水準）",
          "泊3号再稼働（θ=1）": "θ=1・泊3号再稼働", "泊＋風力2倍（θ=1）": "θ=1・泊＋風力2倍"}
DEPTH = {"現行（下限0.01円）": None, "下限 0円": 0.0, "下限 −5円": 5.0, "下限 −10円": 10.0}
_dmax = 0.0
for sl, (tom, wm, th) in SCEN.items():
    net0 = net_scenario(BLK, tom, wm)
    for dl, dp in DEPTH.items():
        d = daily_eval(price_neg(net0, th, dp), W_B)
        ref = _ns[(_ns["水準"] == SCEN32[sl]) & (_ns["下限"] == dl) & (_ns["K(万kW)"] == 0)]["π_PF(円/kW-年)"].iloc[0]
        _dmax = max(_dmax, abs(annual(d["pf"], FYB, EVB) - ref))
assert _dmax < 5.0, _dmax
print(f"32 の negative_price_scenarios.csv（K=0 の π_PF、整数丸め）を再現: 最大差 {_dmax:.2f}円")

# ---------------------------------------------------------------- (1) π(K)
print("\n[1] π(K)（K=0〜150、刻み1万kW）...")
VARS = {"段差（主、32 と同じ）": "step", "外挿（33 の g を 32 の predict に）": "ext", "下限時間を実績に較正": "cal",
        "仕様A′（段差、μ×日次風力三分位）": "aprime"}
KS = list(range(0, 151))
rows = []
LAM = {}
for vl, vk in VARS.items():
    for sl, (tom, wm, th) in SCEN.items():
        if vk != "step" and sl.startswith("FY2026"):
            continue
        net0 = net_scenario(BLK, tom, wm)
        mu_ = mu_aprime(wm) if vk == "aprime" else None
        for dl, dp in DEPTH.items():
            df = run_curve(lambda n, t=th, d_=dp, v_=vk, m_=mu_: price_neg(n, t, d_, v_, m_), net0, "PF", KS, 1.0)
            P0 = price_neg(net0, th, dp, vk, mu_)
            df["負価格の時間(h/年)_K0"] = (P0[EVB] < 0).sum() / 3
            df["下限の時間(h/年)_K0"] = (P0[EVB] <= FLOOR + 1e-6).sum() / 3
            _bs = np.zeros_like(net0, bool)
            for s_ in range(4):
                _bs[SEASB == s_] = net0[SEASB == s_] < G26[s_][0][0]
            _fl = (P0 <= FLOOR + 1e-6)[EVB]
            df["下限の時間のうち推定範囲外(%)_K0"] = _bs[EVB][_fl].mean() * 100 if _fl.any() else np.nan
            df.insert(0, "θ", th)
            df.insert(0, "下限", dl)
            df.insert(0, "シナリオ", sl)
            df.insert(0, "下端の扱い", vl)
            if sl.startswith("現状") and dp is None:
                LAM[vl] = C_ACT / float(df["c"].iloc[0])
            rows.append(df)
PIK = pd.concat(rows, ignore_index=True)
PIK["校正係数λ"] = PIK["下端の扱い"].map(LAM)
PIK["capture_c"] = (PIK["c"] / PIK["π_PF"]).where(PIK["π_PF"] > 1.0)
PIK["π_実績整合"] = PIK["校正係数λ"] * PIK["c"] - WHEEL
PIK["π_モデル直値"] = PIK["c"] - WHEEL
PIK["π_旧0.81PF"] = CAPTURE_OLD * PIK["π_PF"] - WHEEL
PIK.round(4).to_csv(os.path.join(PROC, "negative_price_v3_pik.csv"), index=False, encoding="utf-8-sig")
print("  λ:", {k: round(v, 4) for k, v in LAM.items()})
_k41 = pd.read_csv(os.path.join(PROC, "k0_variants_direct_c_v3.csv"))
_k41 = _k41[_k41["区分"].str.startswith("10.1")]
_m = PIK[(PIK["下端の扱い"].str.startswith("段差")) & (PIK["K(万kW)"] == 0)]
_mp = {"現状（θ=1）": ("現状", 1.0), "FY2026上期水準（θ=1.567）": ("現状", round(TH26, 3)), "泊3号再稼働（θ=1）": ("泊3号再稼働", 1.0),
       "泊＋風力2倍（θ=1）": ("泊＋風力2倍", 1.0)}
_dl41 = {"現行（下限0.01円）": "現行（0.01円）", "下限 0円": "0円", "下限 −5円": "−5円", "下限 −10円": "−10円"}
_dd = 0.0
for _, r in _m.iterrows():
    s41, t41 = _mp[r["シナリオ"]]
    q = _k41[(_k41["シナリオ"] == s41) & np.isclose(_k41["θ"], t41) & (_k41["下限"] == _dl41[r["下限"]])].iloc[0]
    _dd = max(_dd, abs(q["c(0)"] - r["c"]), abs(q["π_PF(0)"] - r["π_PF"]))
assert _dd < 0.01, _dd
print(f"  41 の k0_variants_direct_c_v3.csv（K=0 の c・π_PF）と一致（最大差 {_dd:.4f}円）")
# 42 の表8.6（breakeven_surface_v3_pik.csv）の現行の曲線と一致すること（段差・仕様A′、K=0〜150）
_s86 = pd.read_csv(os.path.join(PROC, "breakeven_surface_v3_pik.csv"))
_m86 = {"段差（主、32 と同じ）": "段差（仕様A 26、現行）", "仕様A′（段差、μ×日次風力三分位）": "仕様A′（26、段差）"}
_sc86 = {"現状（θ=1）": ("なし", 1.0), "泊3号再稼働（θ=1）": ("あり", 1.0), "泊＋風力2倍（θ=1）": ("あり", 2.0)}
_d86 = 0.0
for vl, v86 in _m86.items():
    for sl, (tl, wm) in _sc86.items():
        a_ = PIK[(PIK["下端の扱い"] == vl) & (PIK["シナリオ"] == sl) & PIK["下限"].str.startswith("現行")].set_index("K(万kW)")
        b_ = _s86[(_s86["下端の扱い"] == v86) & (_s86["泊3号"] == tl) & (_s86["風力倍率"] == wm)].set_index("K(万kW)")
        ks_ = a_.index.intersection(b_.index)
        _d86 = max(_d86, (a_.loc[ks_, "c"] - b_.loc[ks_, "c"]).abs().max(), (a_.loc[ks_, "π_PF"] - b_.loc[ks_, "π_PF"]).abs().max())
assert _d86 < 0.01, _d86
print(f"  42 の breakeven_surface_v3_pik.csv（段差・仕様A′、現行、K=0〜150 の c・π_PF）と一致（最大差 {_d86:.4f}円）")

# ---------------------------------------------------------------- (2) θ* の直接解
print("\n[2] θ* の直接解 ...")


def a0_fun(var, tom, wm, depth, base):
    net0 = net_scenario(BLK, tom, wm)
    lam = LAM[[k for k, v in VARS.items() if v == var][0]]
    mu_ = mu_aprime(wm) if var == "aprime" else None

    def a(theta):
        d = daily_eval(price_neg(net0, theta, depth, var, mu_), W_B)
        return lam * annual(d["c"], FYB, EVB) if base == "実績整合" else CAPTURE_OLD * annual(d["pf"], FYB, EVB)
    return a


CASES = {"9.4 式（資本費6.8万・容量1.25万・WACC6%）": (c_req(6.8), 12_500.0), "8.4 標準（c_req 3.45万・容量1.25万）": (34_500.0, 12_500.0)}
SHORT = {"9.4 式（資本費6.8万・容量1.25万・WACC6%）": "9.4式", "8.4 標準（c_req 3.45万・容量1.25万）": "8.4標準"}
for cx in (2.3, 4.0, 6.8):
    for cl, ci in (("1.25万", 12_500.0), ("1.75万", 20_911 * KAPPA), ("2.5万", 30_000 * KAPPA)):
        CASES.setdefault(f"資本費{cx}万・容量{cl}", (c_req(cx), ci))


def solve_theta(a, need, hi=12.0):
    f0 = a(0.0) - need
    if f0 >= 0:
        return 0.0, "θ*≤0（容量収入と負価格の時間だけで足りる）"
    fh = a(hi) - need
    if fh < 0:
        return np.nan, f"θ*>{hi}"
    return optimize.brentq(lambda t: a(t) - need, 0.0, hi, xtol=1e-5), "ok"


be_rows = []
for vl, vk in VARS.items():
    for sl, (tom, wm, th) in SCEN.items():
        if sl.startswith("FY2026"):
            continue
        for dl, dp in DEPTH.items():
            for base in ("実績整合", "旧0.81PF"):
                a = a0_fun(vk, tom, wm, dp, base)
                a1 = a(1.0)
                for case, (creq, kp) in CASES.items():
                    need = creq - kp + WHEEL
                    ts, st = solve_theta(a, need)
                    be_rows.append({"下端の扱い": vl, "シナリオ": sl, "下限": dl, "基準": base, "ケース": case, "c_req(円/kW-年)": creq,
                                    "κP_cap(円/kW-年)": kp, "必要粗収益(円/kW-年)": need, "a(0;θ=1)": a1,
                                    "θ*（直接解）": ts, "状態": st, "θ*（比例、32 と同じ式）": need / a1})
BE = pd.DataFrame(be_rows)
# 検証: θ* で増分貪欲の関数（run_curve, K=0）を回し π(0)+κP−c_req を求める（主ケース、実績整合と旧）
res = []
for i, r in BE[BE["ケース"].str.startswith("9.4") & (BE["状態"] == "ok")].iterrows():
    vk = VARS[r["下端の扱い"]]
    tom, wm, _ = SCEN[r["シナリオ"]]
    dp = DEPTH[r["下限"]]
    mu_ = mu_aprime(wm) if vk == "aprime" else None
    d = run_curve(lambda n, t=r["θ*（直接解）"], d_=dp, v_=vk, m_=mu_: price_neg(n, t, d_, v_, m_), net_scenario(BLK, tom, wm), "PF", [0], 1.0).iloc[0]
    pi0 = (LAM[r["下端の扱い"]] * d["c"] if r["基準"] == "実績整合" else CAPTURE_OLD * d["π_PF"]) - WHEEL
    BE.loc[i, "検証の残差 π(0)+κP−c_req(円)"] = pi0 + r["κP_cap(円/kW-年)"] - r["c_req(円/kW-年)"]
assert BE["検証の残差 π(0)+κP−c_req(円)"].abs().max() < 5.0
BE.round(4).to_csv(os.path.join(PROC, "negative_price_breakeven_v3.csv"), index=False, encoding="utf-8-sig")
print(f"  検証: θ* での残差の最大 {BE['検証の残差 π(0)+κP−c_req(円)'].abs().max():.3f}円（9.4 式、{BE['検証の残差 π(0)+κP−c_req(円)'].notna().sum()} 件）")
# 判定基準（監査 L-10）: 下限0.01円（現行）の行で、比例の値と直接解が一致する
_chk = BE[(BE["下限"].str.startswith("現行")) & BE["ケース"].str.startswith("9.4") & BE["下端の扱い"].str.startswith("段差")]
assert (_chk["θ*（直接解）"] - _chk["θ*（比例、32 と同じ式）"]).abs().max() < 0.01
for base in ("実績整合", "旧0.81PF"):
    print(f"\n  θ*（9.4 式、{base}）: 直接解 / 比例（32 の式）")
    d = BE[BE["ケース"].str.startswith("9.4") & (BE["基準"] == base)]
    print(d.pivot_table(index=["下端の扱い", "シナリオ"], columns="下限", values="θ*（直接解）", sort=False)[list(DEPTH)].round(2).to_string())
    print(d[d["下端の扱い"].str.startswith("段差")].pivot_table(index="シナリオ", columns="下限", values="θ*（比例、32 と同じ式）", sort=False)[list(DEPTH)].round(2).to_string())

# ---------------------------------------------------------------- (3) 実績価格での直接計算
print("\n[3] 実績価格での直接計算（現状、FY2023〜25）...")
ACT_FLOOR = PACTM <= FLOOR + 0.001


def act_price(theta=1.0, depth=None):
    p = FLOOR + theta * (PACTM - FLOOR)
    p = np.where(ACT_FLOOR, FLOOR, p)
    return p if depth is None else np.where(ACT_FLOOR, -depth, p)


def act_eval(theta=1.0, depth=None):
    d = daily_eval(act_price(theta, depth), W_M)
    return annual(d["pf"], FYM, EV), annual(d["c"], FYM, EV)


pf_a0, c_a0 = act_eval()
assert abs(c_a0 - C_ACT) < 0.5 and abs(pf_a0 - PF_ACT) < 0.5
act_rows = []
mod0 = PIK[(PIK["下端の扱い"].str.startswith("段差")) & (PIK["シナリオ"].str.startswith("現状")) & (PIK["K(万kW)"] == 0)].set_index("下限")
for dl, dp in DEPTH.items():
    pf_, c_ = act_eval(1.0, dp)
    r = {"下限": dl, "実績の下限の時間(h/年)": ACT_FLOOR[EV].sum() / 3, "実績PF": pf_, "実績c": c_, "ΔPF(対現行)": pf_ - pf_a0,
         "Δc(対現行)": c_ - c_a0, "増分の捕捉率Δc/ΔPF": (c_ - c_a0) / (pf_ - pf_a0) if dp else np.nan,
         "π(0)=c−1,752": c_ - WHEEL,
         "モデルのΔPF(段差)": mod0.loc[dl, "π_PF"] - mod0.loc["現行（下限0.01円）", "π_PF"],
         "モデルのΔπ_実績整合(段差)": mod0.loc[dl, "π_実績整合"] - mod0.loc["現行（下限0.01円）", "π_実績整合"],
         "モデルの増分の捕捉率Δc/ΔPF": ((mod0.loc[dl, "c"] - mod0.loc["現行（下限0.01円）", "c"]) / (mod0.loc[dl, "π_PF"] - mod0.loc["現行（下限0.01円）", "π_PF"]))
         if dp else np.nan}
    r["実績/モデルの増分比(π)"] = r["Δc(対現行)"] / r["モデルのΔπ_実績整合(段差)"] if dp else np.nan
    for case in ("9.4 式（資本費6.8万・容量1.25万・WACC6%）", "8.4 標準（c_req 3.45万・容量1.25万）"):
        creq, kp = CASES[case]
        need = creq - kp + WHEEL
        ts, st = solve_theta(lambda t, d_=dp: act_eval(t, d_)[1], need)
        r[f"θ*（直接解）{SHORT[case]}"] = ts
        r[f"θ*（比例）{SHORT[case]}"] = need / c_
    act_rows.append(r)
ACT = pd.DataFrame(act_rows)
ACT.round(4).to_csv(os.path.join(PROC, "negative_price_actual_v3.csv"), index=False, encoding="utf-8-sig")
print(ACT.round(3).T.to_string())

# ---------------------------------------------------------------- (4) 8.6 の線形外挿（下限なし）の負価格の深さ
print("\n[4] 8.6 の線形外挿・下限なしが与える負の価格の深さと、下限が削る価値（K=0）...")
SH = {"現状": (0.0, 1.0), "泊3号（−821MW）": (-TOMARI, 1.0), "泊2基相当（−1,642MW）": (-TOM2, 1.0), "泊1〜3号全基（−1,863MW）": (-TOMALL, 1.0),
      "風力2倍": (0.0, 2.0), "風力3倍": (0.0, 3.0)}
C_STEP = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0]


def pvar(net, ver, kind, c=None):
    mu, G = MUB[ver], GG[ver]
    if kind == "段差":
        base = np.maximum(g_curve(net, G, SEASB) + mu, FLOOR)
        return base if c is None else np.where(base <= FLOOR + 1e-9, -c, base)
    if kind == "外挿・下限あり":
        return np.maximum(np.maximum(g_ext(net, ver), FLOOR) + mu, FLOOR)
    if kind == "外挿・下限なし":
        return g_ext(net, ver) + mu
    raise ValueError(kind)


def ev(P):
    d = daily_eval(P, W_B)
    return annual(d["pf"], FYB, EVB), annual(d["c"], FYB, EVB)


dep_rows = []
for ver in ("13", "26"):
    lam = C_ACT / ev(pvar(NETB, ver, "段差"))[1]
    vals = {}
    for sl, (dn, wm) in SH.items():
        net = net_scenario(BLK, False, wm) + dn
        lat = pvar(net, ver, "外挿・下限なし")[EVB]
        neg = lat[lat < FLOOR]
        r = {"価格モデル": f"仕様A（{ver}）", "シナリオ": sl, "0.01円未満の時間(h/年)": len(neg) / 3,
             "平均(円/kWh)": neg.mean() if len(neg) else np.nan, "中央値": np.median(neg) if len(neg) else np.nan,
             "10%点": np.quantile(neg, 0.1) if len(neg) else np.nan, "最小": neg.min() if len(neg) else np.nan,
             "−5円より深い割合(%)": (neg < -5).mean() * 100 if len(neg) else np.nan,
             "−10円より深い割合(%)": (neg < -10).mean() * 100 if len(neg) else np.nan}
        _b4 = np.sort(lat, 1)[:, :4]                         # 各日の最安4時間（充電の候補）に限る（監査の定義）
        _b4 = _b4[_b4 < FLOOR]
        r.update({"最安4h: 0.01円未満の時間(h/年)": len(_b4) / 3, "最安4h: 平均(円/kWh)": _b4.mean() if len(_b4) else np.nan,
                  "最安4h: −5円より深い割合(%)": (_b4 < -5).mean() * 100 if len(_b4) else np.nan,
                  "最安4h: −10円より深い割合(%)": (_b4 < -10).mean() * 100 if len(_b4) else np.nan})
        for kind in ("外挿・下限あり", "外挿・下限なし"):
            r[f"PF_{kind}"], r[f"c_{kind}"] = ev(pvar(net, ver, kind))
        for c in [None] + C_STEP:
            k = "段差・現行" if c is None else f"段差・−{c:g}円"
            r[f"PF_{k}"], r[f"c_{k}"] = ev(pvar(net, ver, "段差", c))
        r["段差の下限張り付き(h/年)"] = (pvar(net, ver, "段差")[EVB] <= FLOOR + 1e-9).sum() / 3
        r["λ（各仕様の段差で校正）"] = lam
        vals[sl] = r
        dep_rows.append(r)
    ref = vals["現状"]
    for sl, r in vals.items():
        if sl == "現状":
            continue
        for m_, sc in (("PF", 1.0), ("c", lam)):
            dA = lambda k: sc * (r[f"{m_}_{k}"] - ref[f"{m_}_{k}"])
            r[f"Δ{m_}_外挿・下限あり"] = dA("外挿・下限あり")
            r[f"Δ{m_}_外挿・下限なし"] = dA("外挿・下限なし")
            r[f"下限が削る価値_外挿({m_})"] = dA("外挿・下限なし") - dA("外挿・下限あり")
            steps = [dA(f"段差・−{c:g}円") - dA("段差・現行") for c in C_STEP]
            for c, v in zip(C_STEP, steps):
                r[f"下限が削る価値_段差c={c:g}({m_})"] = v
            r[f"外挿に相当する段差の深さc({m_})"] = float(np.interp(r[f"下限が削る価値_外挿({m_})"], steps, C_STEP)) \
                if np.all(np.diff(steps) > 0) else np.nan
DEP = pd.DataFrame(dep_rows)
DEP.round(4).to_csv(os.path.join(PROC, "negative_price_extrap_depth_v3.csv"), index=False, encoding="utf-8-sig")
show = ["価格モデル", "シナリオ", "0.01円未満の時間(h/年)", "平均(円/kWh)", "中央値", "10%点", "−5円より深い割合(%)", "−10円より深い割合(%)",
        "最安4h: 0.01円未満の時間(h/年)", "最安4h: 平均(円/kWh)", "最安4h: −5円より深い割合(%)", "最安4h: −10円より深い割合(%)",
        "段差の下限張り付き(h/年)", "ΔPF_外挿・下限あり", "ΔPF_外挿・下限なし", "下限が削る価値_外挿(PF)",
        "下限が削る価値_段差c=5(PF)", "下限が削る価値_段差c=10(PF)", "外挿に相当する段差の深さc(PF)",
        "下限が削る価値_外挿(c)", "下限が削る価値_段差c=5(c)", "下限が削る価値_段差c=10(c)", "外挿に相当する段差の深さc(c)"]
print(DEP[[c for c in show if c in DEP.columns]].round(2).T.to_string())

# ---------------------------------------------------------------- (5) 再エネ側の移転と出力制御の影の価格の比（表10.2 の比、L-10）
print("\n[5] 移転額と出力制御の影の価格の比（実績、32 と同じ定義: 下限時間の制御前再エネ出力×(0.01+c)、抑制量×c）...")
_p = m41["n26"]["p"].dropna(subset=["p_hokkaido"]).copy()
_p["vre"] = _p["solar_pre"] + _p["wind_pre"]
_p["curt"] = _p["solar_curt"].fillna(0) + _p["wind_curt"].fillna(0)
_p["floor"] = _p["p_hokkaido"] <= 0.011
tr_rows = []
for per, sub in (("年度", _p), ("4〜6月", _p[_p["ts"].dt.month.isin([4, 5, 6])])):
    for fy, g in sub[sub["fy"].between(2023, 2026)].groupby("fy"):
        fl = g[g["floor"]]
        for c in (5.0, 10.0):
            tr_ = fl["vre"].sum() * (0.01 + c) / 1e5
            sh_ = g["curt"].sum() * c / 1e5
            tr_rows.append({"期間": per, "FY": int(fy), "c": c, "下限張り付き(h)": len(fl), "移転(億円)": tr_, "影の価格(億円)": sh_,
                            "比": tr_ / sh_ if sh_ > 0 else np.nan})
TRR = pd.DataFrame(tr_rows)
TRR.round(3).to_csv(os.path.join(PROC, "negative_price_transfer_ratio_v3.csv"), index=False, encoding="utf-8-sig")
print(TRR[TRR["c"] == 5.0].round(2).to_string(index=False))

# ---------------------------------------------------------------- 表10.1 の行
print("\n[表10.1] ...")
t_rows = []
for vl in VARS:
    for sl in SCEN:
        for dl in DEPTH:
            d = PIK[(PIK["下端の扱い"] == vl) & (PIK["シナリオ"] == sl) & (PIK["下限"] == dl)].set_index("K(万kW)")
            if d.empty:
                continue
            r = {"下端の扱い": vl, "シナリオ": sl, "下限": dl, "負価格の時間(h/年)": d["負価格の時間(h/年)_K0"].iloc[0],
                 "下限の時間(h/年)": d["下限の時間(h/年)_K0"].iloc[0],
                 "下限の時間のうち推定範囲外(%)": d["下限の時間のうち推定範囲外(%)_K0"].iloc[0], "capture_c(0)": d.loc[0, "capture_c"]}
            for b in ("π_実績整合", "π_モデル直値", "π_旧0.81PF"):
                for k in (0, 25, 50, 100):
                    r[f"{b}({k})"] = d.loc[k, b]
            if not sl.startswith("FY2026"):
                for base in ("実績整合", "旧0.81PF"):
                    for case in ("9.4 式（資本費6.8万・容量1.25万・WACC6%）", "8.4 標準（c_req 3.45万・容量1.25万）"):
                        q = BE[(BE["下端の扱い"] == vl) & (BE["シナリオ"] == sl) & (BE["下限"] == dl) & (BE["基準"] == base) & (BE["ケース"] == case)].iloc[0]
                        r[f"θ*直接解_{SHORT[case]}_{base}"] = q["θ*（直接解）"]
                        r[f"θ*比例_{SHORT[case]}_{base}"] = q["θ*（比例、32 と同じ式）"]
            t_rows.append(r)
for _, r in ACT.iterrows():
    t_rows.append({"下端の扱い": "実績価格（FY2023〜25）", "シナリオ": "現状（θ=1）", "下限": r["下限"], "負価格の時間(h/年)": r["実績の下限の時間(h/年)"] if r["下限"] not in ("現行（下限0.01円）", "下限 0円") else 0.0,
                   "下限の時間(h/年)": r["実績の下限の時間(h/年)"], "π_実績整合(0)": r["π(0)=c−1,752"],
                   "θ*直接解_9.4式_実績整合": r["θ*（直接解）9.4式"], "θ*比例_9.4式_実績整合": r["θ*（比例）9.4式"],
                   "θ*直接解_8.4標準_実績整合": r["θ*（直接解）8.4標準"], "θ*比例_8.4標準_実績整合": r["θ*（比例）8.4標準"]})
T101 = pd.DataFrame(t_rows)
T101.round(4).to_csv(os.path.join(PROC, "negative_price_v3_table101.csv"), index=False, encoding="utf-8-sig")
cols = ["下端の扱い", "シナリオ", "下限", "負価格の時間(h/年)", "π_実績整合(0)", "π_実績整合(50)", "π_実績整合(100)", "θ*直接解_9.4式_実績整合",
        "θ*比例_9.4式_実績整合", "θ*直接解_9.4式_旧0.81PF", "θ*比例_9.4式_旧0.81PF", "π_旧0.81PF(0)", "π_旧0.81PF(50)", "π_旧0.81PF(100)"]
print(T101[cols].round(2).to_string(index=False))
print("\n  下限の時間のうち推定範囲外（%、K=0、現行）:", {f"{r['下端の扱い'][:2]}・{r['シナリオ'][:4]}": round(r["下限の時間のうち推定範囲外(%)"], 1)
      for _, r in T101[T101["下限"].str.startswith("現行") & ~T101["下端の扱い"].str.startswith("実績")].iterrows()})
print("\n  θ*（直接解、実績整合、段差）の資本費×容量収入の格子:")
g = BE[(BE["下端の扱い"].str.startswith("段差")) & (BE["基準"] == "実績整合") & BE["ケース"].str.startswith("資本費")]
print(g.pivot_table(index=["シナリオ", "ケース"], columns="下限", values="θ*（直接解）", sort=False)[list(DEPTH)].round(2).to_string())

# ---------------------------------------------------------------- 図
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする
fig, axes = plt.subplots(1, 2, figsize=(6.1, 3.7), sharey=True, layout="constrained")
colsD = {"現行（下限0.01円）": "#0079C2", "下限 0円": "#9DC3E6", "下限 −5円": "#D95B20", "下限 −10円": "#7B3F9E"}
DL_LABEL = {"現行（下限0.01円）": "下限0.01円（現行）", "下限 0円": "下限0円", "下限 −5円": "下限−5円", "下限 −10円": "下限−10円"}
for ax, sls in zip(axes, (("現状（θ=1）", "泊3号再稼働（θ=1）"), ("泊＋風力2倍（θ=1）",))):
    for dl, c_ in colsD.items():
        for sl, ls in zip(sls, ("-", "--")):
            d = PIK[(PIK["下端の扱い"].str.startswith("段差")) & (PIK["シナリオ"] == sl) & (PIK["下限"] == dl)]
            ax.plot(d["K(万kW)"], d["π_実績整合"], color=c_, ls=ls, lw=1.5 if ls == "-" else 1.1,
                    label=DL_LABEL[dl] if ls == "-" else None)
    ax.axhline(0, color=GRAY, lw=0.9)
    ax.set_xlabel("フリート容量 K（万kW、4時間換算）", fontsize=9, color=GRAY)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    for sp_ in ("top", "right"):
        ax.spines[sp_].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=8.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}".replace("-", "−")))
axes[0].set_title("(a) 現状（実線）・泊3号再稼働（破線）", fontsize=9, fontweight="bold", loc="left")
axes[1].set_title("(b) 泊＋風力2倍", fontsize=9, fontweight="bold", loc="left")
axes[0].set_ylabel("限界参入者の実現可能収益\nπ(K)（円/kW-年）", fontsize=9, color=GRAY)
axes[0].legend(fontsize=8.5, frameon=False, loc="upper right", handlelength=1.6)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "negative_price_pi_k_v3.png"), dpi=300)
plt.close(fig)
print("saved")
