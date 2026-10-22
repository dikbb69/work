#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""契約型とマーチャントのリスク・リターン: 事業 IRR、資産の資本コスト r_A と θ*、APV による乖離の分解、確実性等価

第9章の節「契約型とマーチャントのリスク・リターン」（9.5）、8.5 の WACC 感応度、9.2(b)、5.5 の数値を作る。

手法:
  (A) マーチャント4h の事業 IRR（無レバレッジ・税前・20年・期末に毎年の CF。物価上昇は織り込まない実質の扱い）。
      CF_t = π(0) + κP_cap,t − 運維・廃止0.53万 − 託送等固定0.69万（9.4 の c_req と同じ費用の定義）。
      π(0) は限界参入者の K=0 の実現可能収益（充電従量1,752 を控除）で、主は実績整合（pi_k_curve_v3.csv の
      π_実績整合: θ=1 6,675、θ=1.567 11,452、θ=1.715 12,705円/kW-年。価格過程モデルの価格経路の上で戦略c の実現粗利を
      直接計算し、FY2023〜25 の実績の戦略c 8,427 に in-sample で校正した値）。モデル直値・旧0.81×π_PF・旧裾補正を併記。
      FY2022 の実績価格そのもの（戦略c の実績21,017、0.81×完全予見粗利25,160）の行も置く（連系線増強前の分断構造）。
      κP_cap は一定の4通り（0.836×14,972=12,517（2029年度向け）、0.836×8,749=7,314（2026年度向け）、
      0.836×20,911=17,482（2030年度向け Net CONE）、2.5万（上限近傍））と、運開を FY2027 とした年度別の経路3通り
      （FY2027〜29 は既約定の 0.836×13,287・14,812・14,972、FY2030 以降は 0.836×20,911、0.836×1.5×20,911=26,222
      （上限価格）、または 12,517）。IRR=0 となる容量収入と θ（CF 一定の場合は20年の CF の合計が投資額に等しい点）も出す。
      参考として、SII 補助（1/3・1/2、上限なし）を受けた場合の IRR と、マーチャント6h（容量収入 0.932×14,972）の IRR も出す。
  (B) LTDA 6h の事業 IRR。収入＝応札価格 F×契約容量＋他市場収益の1割（約款第28条の還付後）。F は北海道の上限価格
      71,768（応札年度2026）・77,033（第3回）と、事業報酬率 w=4/5/6% で費用を積み上げた価格。契約容量は
      設備容量（q=1）と期待容量（q=κ_6h=0.932）の2通り。応札年度2026 の募集要綱（pp.32–33、様式6）では
      応札容量の上限は期待容量（送電端の設備容量に調整係数を掛けて自動計算）で、契約は応札容量で成立する。
      落札電源は制度適用期間中メインオークションに参加できない（同 pp.47–48）ので、容量市場の収入は得ない。
      6h のスポット純収入は、主は実績価格（FY2023〜25）の上で戦略c を6時間で直接計算した粗利（実績整合）から充電従量
      2,628 を引いた値。旧基準（モデルの π_PF(0) に実績の 6h/4h 完全予見粗利比を掛け、0.81 と ×1.25 を掛ける）も併記。
      参考に、法人税（τ=30.64%、定額法20年、借入なし）を引いた税引後 IRR も出す。
  (C) θ*(r_A): 9.4 の式 θ* = (c_req(r_A) − κP_cap + 充電従量1,752)/a を r_A=4〜10% で。a は K=0・θ=1 の粗収益で、
      主は実績整合の 8,427（モデル直値 7,602、旧 0.81×π_PF(0)=6,695、旧裾補正 8,350 を併記）。
      c_req は 9.4 基準（4h資本費×CRF＋0.53万＋0.69万、6%で35,914円）を主とし、廃止費（資本費の5%）を
      20年目の支出として置く版を併記。8.4 の c_req 3.45万が相当する割引率も逆算する。
  (D) 節税効果: Miles-Ezzell の WACC = r_A − τ·k_d·L·(1+r_A)/(1+k_d)（τ=30.64%、k_d=2.5%、L=30〜60%）と θ* への効果。
  (E) APV（Myers 1974）: 基礎 NPV（マーチャント、r_A^M で割引、借入なし）＋容量市場＋補助金（4h）。
      6h では LTDA 電源を「マーチャントの資産＋レベニュースワップ（固定 F·q を受け取り、他市場収益の9割を還付し、
      容量市場への参加を手放す）」とみて、スワップ価値＝固定側 PV(r_C) − 変動側 PV(r_A^M) を、
      期待値の移転 PV_rC(F·q − E[変動側]) と、リスク移転（割引率の差）PV_rC(E[変動側]) − PV_rM(E[変動側]) に分ける。
      公正な固定価格 F_fair（スワップ価値がゼロになる F）も求める。r_C は 1〜6%（固定側を20年国債程度の率で割り引く
      場合まで）、r_A^M は 8〜11%（9.5.2 のマーチャントの上乗せ4.0〜5.1ポイントと整合する範囲）で動かす。
      計算は税前なので、APV の合計には節税効果を入れない（税前の CF に節税効果だけを足すと、営業利益への課税を
      無視した分だけ過大になる）。節税効果は「法人税を入れた場合に資本構成が加える価値の上限」として別に示す。
      元利均等返済の負債（4h は補助後の投資額×L、6h は投資額×L）の支払利息×τ を k_d で割り引く（Myers 1974 の
      負債額を固定した場合）。補助金を圧縮記帳した場合の課税所得も示す。
  (F) 確実性等価（Fama 1977）: θ の対数の過程を2通り置く。(i) 定常 AR(1)（φ=0・0.5・0.9）で、FY2016〜25 の年次の
      SD を定常 SD とみなし、革新 SD = σ·√(1−φ²)。(ii) 恒久成分のランダムウォーク（φ=1、8.7 の主仕様と整合）で、
      革新 SD に 8.7 の σ_ξ（0.10・0.112・0.20・0.30）を直接使う（√(1−φ²) は掛けない）。各期の価値の更新（イノベーション）
      の SD に CAPM のリスク調整 λρ を掛けて現在価値に積み上げる。20年分の現在価値の SD に λρ を一度だけ掛ける方法
      （時間分散の誤謬）も比較のために出す。θ の年次 SD は FY2016〜25 のシステムプライス年平均の比（FY2023〜25 平均＝1）で
      代理する（北海道エリア価格の比より大きく、リスク調整を大きく出す側）。
      9.4 の基準（割引率6%＝契約型の水準）の不足額 gap に、マーチャントが負うリスク調整 RP を足したものが、
      マーチャントの参入に足りない額である。リスクを全部移したときに埋まる比率 RP/(gap+RP) を出す
      （RP/gap も参考に残す）。期待スポット粗収入 G は実績整合 8,427（主）、モデル直値、旧、旧裾補正。
  (G) 参考: Gohdes, Simshauser & Wilson (2022) の調査値（株式の期待収益率・信用スプレッド・負債比率）から、
      マーチャントと契約型の加重平均資本コストを当方で計算する（r_A の位置づけの根拠）。調査値は名目なので、
      使うのは水準ではなく契約型との差である。
出力: data/processed/irr_cost_of_capital.csv, apv_decomposition.csv, certainty_equivalent.csv,
      figures/hokkaido/apv_decomposition.png
限界: 税前・物価上昇を織り込まない CF（調達価格等算定委員会の想定 IRR の算定と同じ扱い。IRR と割引率は実質と読む。
      LTDA の物価補正、劣化、DoD、建設期間は扱わない）。λ（0.2〜0.4）と ρ（0.3〜1）は仮定で、
      ρ>0 は保険価値を大きく出す側の仮定（燃料高は株価に負の場合が多い）。確実性等価のリスク源は θ だけで、
      競合参入 K と容量価格のリスクは含めない（σ を2倍にしたケースで代用）。節税効果は課税所得がある場合の上限で、
      マーチャント4h は SPC 単体では課税所得が負になり使えない。マーチャントの r_A 8〜11% は文献と実務の範囲で、
      本スクリプトの推定値ではない。補助金の上限額（1/2 補助で40億円）は案件規模で効き方が変わる。
      APV の基礎ケースは運転費用も r_A^M で割り引く（単一率）。実績整合の π(0) は K=0・θ=1 の in-sample 校正
      （λ=1.1085）で、θ>1 にも同じ比を当てている。

v3 での修正（2026-10-21、主任の決定 D1 と監査 A9-5-1・A9-5-3・A9-5-4・L-5 への対応）:
  1. 収益の基準を D1 に合わせ、主を実績整合にした（旧版の主は旧0.81×π_PF の 4,943、×1.25 上限ケース 6,598）。
     入力を pi_k_curve_v2.csv から pi_k_curve_v3.csv（26、K=0）に替えた。旧基準の行も残す。
  2. (A) の IRR を年度別 CF の IRR に一般化し、容量収入の一定4通りと年度別の経路3通りを入れた。IRR=0 となる容量収入と
     θ（判定が割引率に依存しない条件）、FY2022 の実績価格そのものの IRR（例外）を加えた。
  3. (B)(E2) の 6h のスポット純収入を、実績価格の上の戦略c（6時間）に替えた（主）。
  4. (E2) の r_C に 1・1.5・2・2.5・3%（固定側を国債程度で割り引く場合）、r_A^M に 10・11% を加え、手放す側の内訳
     （容量収入とスポット9割の割合）を出す。
  5. (F) に φ=1（恒久成分のランダムウォーク、革新 σ=0.10・0.112・0.20・0.30）の行を加えた（列「θ の過程」）。
  6. 図: 実績整合の基準、(b) は r_C=5%・r_A^M=9%（9.5.2 の上乗せ4ポイントと整合）で描き直した。
"""
import logging
import os

import numpy as np
import pandas as pd
from scipy.optimize import brentq
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
pd.set_option("display.width", 240)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------- 諸元（9.4・notes/20・募集要綱）
T = 20
CAPEX_KWH = 6.8e4                       # 円/kWh（FY2024 実勢、notes/20）
OM, DECOM_4H, WHEEL = 5_000.0, 300.0, 6_900.0   # 9.4 の「運維・廃止0.53万」＝運維5,000＋廃止の年額300、託送等固定0.69万
FIXED = {4: OM + DECOM_4H + WHEEL, 6: OM + DECOM_4H * 1.5 + WHEEL}   # 4h 12,200、6h 12,350（廃止は資本費に比例）
CAPTURE, CHG_YEN, ETA = 0.81, 1.2, 0.85
CHG = {h: CHG_YEN * h * 365 for h in (4, 6)}    # 充電従量負担 4h 1,752、6h 2,628 円/kW-年
P_CAP = {"2029年度向け": 14_972.0, "2026年度向け": 8_749.0, "2027年度向け": 13_287.0, "2028年度向け": 14_812.0,
         "2030年度向け Net CONE": 20_911.0}
KAPPA = {4: 0.836, 6: 0.932}
KP4 = {"容量1.25万（2029年度向け）": KAPPA[4] * P_CAP["2029年度向け"],
       "容量0.73万（2026年度向け）": KAPPA[4] * P_CAP["2026年度向け"]}
KP4_MORE = {"容量1.75万（2030年度向け Net CONE）": KAPPA[4] * P_CAP["2030年度向け Net CONE"],
            "容量2.5万（上限近傍）": 25_000.0}
_known = [KAPPA[4] * P_CAP[k] for k in ("2027年度向け", "2028年度向け", "2029年度向け")]   # FY2027〜29 の既約定
KP4_PATH = {"既約定→FY2030〜1.75万（Net CONE）": _known + [KAPPA[4] * P_CAP["2030年度向け Net CONE"]] * (T - 3),
            "既約定→FY2030〜2.62万（上限価格1.5×Net CONE）": _known + [KAPPA[4] * 1.5 * P_CAP["2030年度向け Net CONE"]] * (T - 3),
            "既約定→FY2030〜1.25万（2029年度向けのまま）": _known + [KAPPA[4] * P_CAP["2029年度向け"]] * (T - 3)}
KP6 = KAPPA[6] * P_CAP["2029年度向け"]          # 13,954
LTDA_CAP = {"上限7.2万（応札年度2026・北海道71,768）": 71_768.0, "上限7.7万（第3回・北海道77,033）": 77_033.0}
RETAIN = 0.10                                   # 他市場収益の約9割を還付（約款第28条）→ 1割を保持
# 法人実効税率: 財務省の標準税率ベースで、防衛特別法人税（2026年4月1日以後に開始する事業年度）を含めた 30.64%。
# 東京都の外形標準課税適用法人では 30.62%（防衛特別法人税なし）→ 31.52%（あり）。借入金利 k_d は 2.5%。
TAU, KD = 0.3064, 0.025
SII_CAP_HALF = 40e8                             # 1/2 補助の上限40億円（SII 公募要領）
SIZE_KW = 50_000                                # 上限が効く例示の案件規模（5万kW・4h）

ann = lambda r, n=T: float(n) if abs(r) < 1e-12 else (1 - (1 + r) ** -n) / r
crf = lambda r, n=T: 1 / ann(r, n)
sff = lambda r, n=T: 1 / n if abs(r) < 1e-12 else r / ((1 + r) ** n - 1)


def irr_stream(I, cfs, decom=0.0):
    """期首 −I、1〜n 年目 cfs[t−1]、n 年目に −decom の IRR。CF の合計が投資額に届かず、根が [−95%, 300%] にない場合は
    負の IRR を探し、それもなければ NaN"""
    cfs = np.asarray(cfs, float)
    n = len(cfs)
    t = np.arange(1, n + 1)
    f = lambda r: -I + (cfs / (1 + r) ** t).sum() - decom * (1 + r) ** -n
    try:
        return brentq(f, -0.95, 3.0)
    except ValueError:
        return np.nan


def irr_flat(I, cf, n=T, decom=0.0):
    """期首 −I、1〜n 年目 cf、n 年目に −decom の IRR。cf≤0 なら NaN"""
    if cf <= 0:
        return np.nan
    return irr_stream(I, np.full(n, cf), decom)


def npv_stream(I, cfs, r):
    cfs = np.asarray(cfs, float)
    return -I + (cfs / (1 + r) ** np.arange(1, len(cfs) + 1)).sum()


def pvts(D0, kd=KD, tenor=15, tau=TAU, disc=None):
    """元利均等返済の負債 D0 の支払利息の節税効果の現在価値（disc=None なら kd で割引）"""
    disc = kd if disc is None else disc
    pay = D0 / ann(kd, tenor)
    bal, pv = D0, 0.0
    for t in range(1, tenor + 1):
        intr = bal * kd
        pv += tau * intr / (1 + disc) ** t
        bal -= pay - intr
    return pv


rows_irr = []


def add(block, target, case, sub, r, metric, value, unit, basis=""):
    rows_irr.append({"ブロック": block, "対象": target, "収入の基準": basis, "ケース": case, "容量・契約": sub,
                     "割引率": r, "指標": metric, "値": value, "単位": unit})


# ---------------------------------------------------------------- 入力（π(0)・a・実績価格の戦略c）
pk = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
pk = pk[(pk["価格モデル"] == "仕様A（26、水準係数付き）") & (pk["シナリオ"] == "現状") & (pk["フリート配分"] == "完全予見の増分貪欲（主）")
        & (pk["刻み(万kW)"] == "1.0") & (pk["K(万kW)"] == 0)].set_index("θ")
PI_PF0 = float(pk.loc[1.0, "π_PF"])                           # 8,265.5（モデルの完全予見粗利、θ=1）
C0 = float(pk.loc[1.0, "c"])                                  # 7,602.4（モデルの戦略c、θ=1）
LAM = float(pk.loc[1.0, "校正係数λ"])                          # 1.1085
TAIL = (float(pk.loc[1.0, "π_旧裾補正"]) + CHG[4]) / (CAPTURE * PI_PF0)   # 旧版の ×1.25（1.2472）
BASIS_COL = {"実績整合": "π_実績整合", "モデル直値": "π_モデル直値", "旧0.81PF": "π_旧0.81PF", "旧裾補正": "π_旧裾補正"}
A_BASIS = {"実績整合": LAM * C0, "モデル直値": C0, "旧0.81PF": CAPTURE * PI_PF0, "旧裾補正": CAPTURE * TAIL * PI_PF0}
TH_LAB = {1.0: "θ=1（FY2023〜25）", 1.567: "FY2026上期水準 θ=1.567", 1.715: "FY2022水準 θ=1.715"}

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
PA = P.to_numpy(float)
srt = np.sort(PA, axis=1)
fyd = np.asarray(P.index.year - (P.index.month < 4).astype(int))
wk = np.asarray(P.index.dayofweek >= 5)
pf_fy = {}
for h in (4, 6):
    d = np.maximum(ETA * srt[:, -h:].sum(1) - srt[:, :h].sum(1), 0.0)
    pf_fy[h] = pd.Series(d).groupby(fyd).sum()
pf_act = {h: float(pf_fy[h].loc[[2023, 2024, 2025]].mean()) for h in (4, 6)}
# 実績価格の上の戦略c（36 と同じ規則: 直近29日・同じ曜日区分の平均価格のランク、5日以上、同値は均等配分）
clim = np.full_like(PA, np.nan)
for i in range(len(P.index)):
    hist = [j for j in range(max(0, i - 29), i) if wk[j] == wk[i]]
    if len(hist) >= 5:
        clim[i] = PA[hist].mean(axis=0)


def tie_w(sig, k):
    thr = np.sort(sig)[k - 1]
    w = (sig < thr).astype(float)
    tied = sig == thr
    w[tied] = (k - w.sum()) / tied.sum()
    return w


strat_c = {}
for h in (4, 6):
    m = np.full(len(P.index), np.nan)
    for i in range(len(P.index)):
        if not np.isnan(clim[i]).any():
            m[i] = ETA * (tie_w(-clim[i], h) @ PA[i]) - tie_w(clim[i], h) @ PA[i]
    strat_c[h] = pd.Series(m).groupby(fyd).sum()
C4_ACT = float(strat_c[4].loc[[2023, 2024, 2025]].mean())
C6_ACT = float(strat_c[6].loc[[2023, 2024, 2025]].mean())
C4_FY22, PF4_FY22 = float(strat_c[4].loc[2022]), float(pf_fy[4].loc[2022])
assert abs(C4_ACT - LAM * C0) < 1.0, (C4_ACT, LAM * C0)
print(f"a（K=0・θ=1、粗収益）: 実績整合 {A_BASIS['実績整合']:,.1f}（実績の戦略c {C4_ACT:,.1f}）、モデル直値 {C0:,.1f}、"
      f"旧0.81PF {A_BASIS['旧0.81PF']:,.1f}、旧裾補正 {A_BASIS['旧裾補正']:,.1f}（係数 {TAIL:.4f}）")
print(f"FY2022 実績価格: 戦略c {C4_FY22:,.1f}（capture {C4_FY22 / PF4_FY22:.3f}）、完全予見粗利 {PF4_FY22:,.1f}")

# 収入ケース: (ラベル, 基準, θ, π(0)=充電従量控除後)
PI_CASES = []
for th in (1.0, 1.567, 1.715):
    for b, col in BASIS_COL.items():
        PI_CASES.append((f"{TH_LAB[th]}・{b}", b, th, float(pk.loc[th, col])))
PI_CASES.append(("恒久成分 θ=1.22・実績整合（θ に比例）", "実績整合", 1.22, A_BASIS["実績整合"] * 1.22 - CHG[4]))
PI_CASES.append(("FY2022 実績価格・戦略c の実績", "実績価格", np.nan, C4_FY22 - CHG[4]))
PI_CASES.append(("FY2022 実績価格・0.81×完全予見粗利", "実績価格", np.nan, CAPTURE * PF4_FY22 - CHG[4]))
PI_CASES.append(("FY2022 実績価格・完全予見粗利（上界）", "実績価格", np.nan, PF4_FY22 - CHG[4]))
PI = {lab: (b, th, pi) for lab, b, th, pi in PI_CASES}
MAIN1 = f"{TH_LAB[1.0]}・実績整合"

# 6h のスポット純収入（設備1kWあたり、充電従量控除後）
R64 = pf_act[6] / pf_act[4]
PF6_MODEL = PI_PF0 * R64
X6 = {"実績整合（戦略c 6h の実績）": C6_ACT - CHG[6],
      "旧×1.25（上限ケース）": max(0.0, CAPTURE * PF6_MODEL * TAIL - CHG[6]),
      "旧モデル": max(0.0, CAPTURE * PF6_MODEL - CHG[6])}
X6_MAIN = "実績整合（戦略c 6h の実績）"
print(f"実績価格の完全予見粗利 FY2023-25: 4h {pf_act[4]:,.0f}  6h {pf_act[6]:,.0f}（比 {R64:.3f}）; 戦略c 6h {C6_ACT:,.0f}"
      f" → 6h のスポット純収入 X6: " + "、".join(f"{k} {v:,.0f}" for k, v in X6.items()) + " 円/kW-年")

# ---------------------------------------------------------------- (A) マーチャント4h の事業 IRR
I4 = 4 * CAPEX_KWH
print("\n=== (A) マーチャント4h の事業 IRR（無レバレッジ・税前・20年、資本費6.8万円/kWh×4＝27.2万円/kW）===")
KP_ALL = {**{k: [v] * T for k, v in KP4.items()}, **{k: [v] * T for k, v in KP4_MORE.items()}, **KP4_PATH}
tabA = []
for pn, (b, th, pi) in PI.items():
    for kn, kps in KP_ALL.items():
        cfs = pi + np.asarray(kps) - FIXED[4]
        irr = irr_stream(I4, cfs) if cfs.sum() > 0 else np.nan
        rec = {"収入ケース": pn, "基準": b, "θ": th, "容量": kn, "π(円/kW-年)": pi, "年間CF(1年目)": cfs[0], "年間CF(平均)": cfs.mean(),
               "20年累計CF": cfs.sum(), "回収倍率": cfs.sum() / I4, "IRR": irr}
        for r in (0.03, 0.06, 0.08, 0.09):
            rec[f"NPV({r:.0%})"] = npv_stream(I4, cfs, r)
        tabA.append(rec)
        for m, v, u in (("π(0)", pi, "円/kW-年"), ("年間CF（1年目）", cfs[0], "円/kW-年"), ("年間CF（20年平均）", cfs.mean(), "円/kW-年"),
                        ("20年累計CF", cfs.sum(), "円/kW"), ("回収倍率（20年累計CF÷投資額）", cfs.sum() / I4, "倍"), ("事業IRR", irr, "")):
            add("A マーチャント4h IRR", "4h マーチャント", pn, kn, np.nan, m, v, u, b)
        for r in (0.03, 0.06, 0.08, 0.09):
            add("A マーチャント4h IRR", "4h マーチャント", pn, kn, r, "NPV", npv_stream(I4, cfs, r), "円/kW", b)
tabA = pd.DataFrame(tabA)
_show = tabA[tabA["容量"].isin(["容量1.25万（2029年度向け）", "容量0.73万（2026年度向け）", "容量1.75万（2030年度向け Net CONE）",
                                "既約定→FY2030〜1.75万（Net CONE）", "既約定→FY2030〜2.62万（上限価格1.5×Net CONE）", "容量2.5万（上限近傍）"])]
print(_show.pivot_table(index=["収入ケース"], columns="容量", values="IRR", sort=False).round(4).to_string())
# IRR=0 となる条件（割引率に依存しない判定が成り立つ境界）: CF 一定なら 20·(π+κP−12,200) = I
print("IRR=0 となる条件（容量収入一定）: π(0)+κP = I/20 + 12,200 = %s 円/kW-年" % f"{I4 / T + FIXED[4]:,.0f}")
for b in ("実績整合", "モデル直値", "旧0.81PF", "旧裾補正"):
    a = A_BASIS[b]
    for kn, kp in {**KP4, **KP4_MORE}.items():
        th0 = (I4 / T + FIXED[4] - kp + CHG[4]) / a
        add("A マーチャント4h IRR", "IRR=0 の境界", f"基準 {b}", kn, 0.0, "IRR=0 となる θ（容量収入一定）", th0, "", b)
        for rr in (0.06, 0.08):
            add("A マーチャント4h IRR", "IRR=r の境界", f"基準 {b}", kn, rr, f"IRR={rr:.0%} となる θ（容量収入一定）",
                ((I4 * crf(rr) + FIXED[4] - kp + CHG[4]) / a), "", b)
    for th in (1.0, 1.22, 1.567, 1.715):
        kp0 = I4 / T + FIXED[4] - (a * th - CHG[4])
        add("A マーチャント4h IRR", "IRR=0 の境界", f"基準 {b}・θ={th}", "—", 0.0, "IRR=0 となる実効容量収入（一定）", kp0, "円/kW-年", b)
    print(f"  {b}: IRR=0 となる θ は 容量1.25万で {(I4 / T + FIXED[4] - KP4['容量1.25万（2029年度向け）'] + CHG[4]) / a:.3f}、"
          f"1.75万で {(I4 / T + FIXED[4] - KP4_MORE['容量1.75万（2030年度向け Net CONE）'] + CHG[4]) / a:.3f}、"
          f"2.5万で {(I4 / T + FIXED[4] - 25_000 + CHG[4]) / a:.3f}；θ=1・1.567・1.715 で IRR=0 となる容量収入 "
          + "、".join(f"{I4 / T + FIXED[4] - (a * th - CHG[4]):,.0f}" for th in (1.0, 1.567, 1.715)))
# 参考: SII 補助（上限なし）を受けた場合の IRR（容量1.25万・1.75万経路）。補助後の投資額 (1−s)·I に対する IRR
print("参考: 補助を受けた場合のマーチャント4h の事業 IRR（補助は建設時に受け取る）")
for kn in ("容量1.25万（2029年度向け）", "既約定→FY2030〜1.75万（Net CONE）"):
    kps = np.asarray(KP_ALL[kn])
    for pn, (b, th, pi) in PI.items():
        if b not in ("実績整合", "旧0.81PF", "旧裾補正"):
            continue
        cfs = pi + kps - FIXED[4]
        out = []
        for s_lab, s in (("補助1/3", 1 / 3), ("補助1/2", 0.5)):
            irr_s = irr_stream((1 - s) * I4, cfs) if cfs.sum() > 0 else np.nan
            out.append(f"{s_lab} {irr_s:.4f}（回収倍率 {cfs.sum() / ((1 - s) * I4):.2f}）")
            add("A マーチャント4h IRR", "4h マーチャント（補助あり・参考）", pn, f"{kn}・{s_lab}（上限なし）",
                np.nan, "事業IRR（補助後の投資額に対して）", irr_s, "", b)
            add("A マーチャント4h IRR", "4h マーチャント（補助あり・参考）", pn, f"{kn}・{s_lab}（上限なし）",
                np.nan, "回収倍率（20年累計CF÷補助後の投資額）", cfs.sum() / ((1 - s) * I4), "倍", b)
        if kn.startswith("容量1.25"):
            print(f"  {pn}: " + "、".join(out))
# 参考: マーチャント6h（LTDA と同じ資産をマーチャントで持つ場合。容量収入 0.932×14,972）
print("参考: マーチャント6h の事業 IRR（資本費6.8万円/kWh×6＝40.8万円/kW、容量収入 κ6·P_cap）")
for xn, x6v in X6.items():
    cf6m = x6v + KAPPA[6] * P_CAP["2029年度向け"] - FIXED[6]
    irr6m = irr_flat(6 * CAPEX_KWH, cf6m)
    print(f"  6hスポット {xn}: 年間CF {cf6m:,.0f}、回収倍率 {T * cf6m / (6 * CAPEX_KWH):.3f}、IRR {irr6m:.4f}")
    for m, v, u in (("年間CF", cf6m, "円/kW-年"), ("回収倍率（20年累計CF÷投資額）", T * cf6m / (6 * CAPEX_KWH), "倍"),
                    ("事業IRR", irr6m, "")):
        add("A マーチャント6h IRR（参考）", "6h マーチャント", f"6hスポット{xn}", "容量1.40万（2029年度向け）", np.nan, m, v, u,
            "実績整合" if xn == X6_MAIN else "旧")

# ---------------------------------------------------------------- (B) LTDA 6h の事業 IRR
print("\n=== (B) LTDA 6h の事業 IRR（無レバレッジ・税前・20年、他市場収益の1割を保持、容量市場の収入なし）===")
tabB = []
for unit in (6.8e4, 6.0e4):
    I6 = 6 * unit
    fixed6 = OM + DECOM_4H * 1.5 * unit / 6.8e4 + WHEEL
    for xn, x6 in X6.items():
        prices = dict(LTDA_CAP)
        for w in (0.04, 0.05, 0.06):
            prices[f"積み上げ（事業報酬率{w:.0%}）"] = ("stack", w)
        for pn, pv in prices.items():
            for qn, q in (("契約容量＝設備容量", 1.0), ("契約容量＝期待容量（κ=0.932）", KAPPA[6])):
                if isinstance(pv, tuple):
                    F = (I6 * crf(pv[1]) + fixed6) / q          # 費用（資本費年額＋運維・廃止＋託送等固定）÷契約容量
                else:
                    F = pv
                cf = F * q + RETAIN * x6 - fixed6
                irr = irr_flat(I6, cf)
                cf_at = cf - TAU * max(0.0, cf - I6 / T)       # 参考: 税引後（定額法20年、借入なし）
                irr_at = irr_flat(I6, cf_at)
                rec = {"資本費(円/kWh)": unit, "6hスポット": xn, "価格": pn, "契約容量": qn,
                       "F(円/契約kW-年)": F, "設備kWあたり固定収入": F * q, "年間CF": cf, "IRR": irr,
                       "IRR税引後(参考)": irr_at}
                for r in (0.04, 0.05, 0.06):
                    rec[f"NPV({r:.0%})"] = -I6 + cf * ann(r)
                tabB.append(rec)
                case = f"{pn}・資本費{unit / 1e4:.1f}万・6hスポット{xn}"
                bb = "実績整合" if xn == X6_MAIN else "旧"
                for m, v, u in (("応札価格F（契約kWあたり）", F, "円/kW-年"), ("固定収入（設備kWあたり）", F * q, "円/kW-年"),
                                ("年間CF", cf, "円/kW-年"), ("事業IRR", irr, ""),
                                ("事業IRR（税引後・定額法20年、参考）", irr_at, "")):
                    add("B LTDA 6h IRR", "6h LTDA", case, qn, np.nan, m, v, u, bb)
                for r in (0.04, 0.05, 0.06):
                    add("B LTDA 6h IRR", "6h LTDA", case, qn, r, "NPV", -I6 + cf * ann(r), "円/kW", bb)
tabB = pd.DataFrame(tabB)
print(tabB[(tabB["6hスポット"] == X6_MAIN) & (tabB["資本費(円/kWh)"] == 6.8e4)].round(3).to_string(index=False))
print("参考（6hスポットの基準による IRR の差、上限7.2万・期待容量）:",
      {xn: round(float(tabB[(tabB["資本費(円/kWh)"] == 6.8e4) & (tabB["6hスポット"] == xn) & tabB["価格"].str.startswith("上限7.2")
                               & tabB["契約容量"].str.contains("期待")]["IRR"].iloc[0]), 4) for xn in X6})
# 廃止費を20年目に一括で置いた場合（パイロット rv1 の定義）との比較
for F, q in ((71_768.0, KAPPA[6]), (72_000.0, 1.0), (72_000.0, KAPPA[6])):
    cf_e = F * q + RETAIN * X6[X6_MAIN] - OM - WHEEL
    print(f"  廃止費を20年目に一括（資本費の5%）: F={F:,.0f} q={q} → IRR {irr_flat(6 * CAPEX_KWH, cf_e, decom=0.05 * 6 * CAPEX_KWH):.4f}")


# ---------------------------------------------------------------- (C) θ*(r_A)
def c_req94(r, s=0.0):
    return (1 - s) * I4 * crf(r) + FIXED[4]


def c_req_exp(r):
    return I4 * crf(r) + OM + 0.05 * I4 * sff(r) + WHEEL


def theta_star(c, kp, a=A_BASIS["実績整合"]):
    return (c - kp + CHG[4]) / a


print("\n=== (C) θ* を資産の資本コスト r_A 別に（資本費6.8万円/kWh、K=0。a は実績整合が主）===")
tabC = []
KP_C = {**KP4, **KP4_MORE}
for r in (0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10):
    for kn, kp in KP_C.items():
        rec = {"r_A": r, "容量": kn, "c_req(9.4基準)": c_req94(r),
               "θ*(実績整合)": theta_star(c_req94(r), kp), "θ*(モデル直値)": theta_star(c_req94(r), kp, A_BASIS["モデル直値"]),
               "θ*(旧0.81PF)": theta_star(c_req94(r), kp, A_BASIS["旧0.81PF"]),
               "θ*(旧裾補正)": theta_star(c_req94(r), kp, A_BASIS["旧裾補正"]),
               "c_req(廃止費20年目)": c_req_exp(r), "θ*(実績整合・廃止費20年目)": theta_star(c_req_exp(r), kp),
               "θ*(実績整合・補助1/3)": theta_star(c_req94(r, 1 / 3), kp), "θ*(実績整合・補助1/2)": theta_star(c_req94(r, 0.5), kp),
               "θ*(旧0.81PF・補助1/2)": theta_star(c_req94(r, 0.5), kp, A_BASIS["旧0.81PF"])}
        tabC.append(rec)
        for m in [k for k in rec if k not in ("r_A", "容量")]:
            add("C θ*(r_A)", "4h マーチャント", "資本費6.8万円/kWh", kn, r, m, rec[m], "円/kW-年" if m.startswith("c_req") else "")
tabC = pd.DataFrame(tabC)
print(tabC[tabC["容量"].str.startswith("容量1.25")].round(3).to_string(index=False))
print(tabC[tabC["r_A"] == 0.06].round(3).to_string(index=False))
# 8.4 の c_req（3.45万・3.2万・3.7万）が相当する割引率
for lab, c84, kp84 in (("8.4 標準 c_req 3.45万・容量1.25万", 34_500.0, 12_500.0), ("8.4 楽観 3.2万", 32_000.0, 12_500.0),
                       ("8.4 保守 3.7万・容量0.83万", 37_000.0, 8_300.0)):
    r_eq = brentq(lambda r: c_req94(r) - c84, 0.001, 0.3)
    th84 = theta_star(c84, kp84)
    print(f"{lab}: θ*（実績整合）={th84:.3f}（旧 {theta_star(c84, kp84, A_BASIS['旧0.81PF']):.3f}）、9.4 の式で同じ c_req になる割引率 {r_eq:.4f}")
    add("C θ*(r_A)", "4h マーチャント", lab, "8.4 のケース値", r_eq, "θ*（8.4 の c_req をそのまま使用、実績整合）", th84, "")
    add("C θ*(r_A)", "4h マーチャント", lab, "8.4 のケース値", np.nan, "同じ c_req になる割引率（9.4 の式）", r_eq, "")
print(f"9.4 基準 6%: c_req={c_req94(0.06):,.0f}、θ*（実績整合、κP=12,517）={theta_star(c_req94(0.06), KP4['容量1.25万（2029年度向け）']):.4f}、"
      f"θ*（κP=12,500、28・38 と同じ丸め）={theta_star(c_req94(0.06), 12_500.0):.4f}")

# ---------------------------------------------------------------- (D) 節税効果（Miles-Ezzell）
print("\n=== (D) 節税効果: Miles-Ezzell の WACC と θ*（τ=30.64%、k_d=2.5%、実績整合）===")
kp_main = KP4["容量1.25万（2029年度向け）"]
tabD = []
for r in (0.06, 0.08, 0.09):
    for L in (0.0, 0.30, 0.45, 0.60):
        dW = TAU * KD * L * (1 + r) / (1 + KD)
        w = r - dW
        tabD.append({"r_A": r, "負債比率L": L, "WACCの低下(pt)": dW * 100, "税引後WACC": w,
                     "θ*(r_A)": theta_star(c_req94(r), kp_main), "θ*(税引後WACC)": theta_star(c_req94(w), kp_main),
                     "c_reqの低下(円/kW-年)": c_req94(r) - c_req94(w)})
        add("D 節税効果", "4h マーチャント", f"L={L:.0%}", "容量1.25万", r, "WACC の低下（%ポイント）", dW * 100, "%pt")
        add("D 節税効果", "4h マーチャント", f"L={L:.0%}", "容量1.25万", r, "θ*（税引後 WACC で近似、実績整合）", theta_star(c_req94(w), kp_main), "")
        add("D 節税効果", "4h マーチャント", f"L={L:.0%}", "容量1.25万", r, "c_req の低下", c_req94(r) - c_req94(w), "円/kW-年")
tabD = pd.DataFrame(tabD)
print(tabD.round(3).to_string(index=False))

# ---------------------------------------------------------------- (G) 文献の資本構成による加重平均（参考）
# Gohdes, Simshauser & Wilson (2022) の Table 3（豪州 NEM の調査値）: 株式の期待収益率・信用スプレッド・負債比率。
# 同論文のモデルの BBSW 0.89%＋金利上昇の上乗せ0.69% にスプレッドを足した借入金利と、日本の想定 k_d=2.5% の2通りで
# 負債の節税効果を含めない加重平均と、含めた加重平均（τ=30%、豪州）を当方で計算する（論文が報告する WACC そのものでは
# ない）。株式の期待収益率は法人税後・名目の値なので、本研究の税前・毎年同額の CF に当てるときは、水準ではなく
# 契約型との差（マーチャントの上乗せ）を使う。
print("\n=== (G) 文献の資本構成による加重平均（Gohdes, Simshauser & Wilson 2022 の調査値から当方で計算）===")
wacc_g = {}
for nm, ke, spr, L in (("マーチャント", 0.1225, 0.0260, 0.40), ("全量コーポレートPPA", 0.08, 0.0180, 0.67),
                       ("全量政府CfD", 0.0625, 0.0140, 0.72)):
    for kd_lab, kd in (("BBSW0.89%+0.69%+スプレッド", 0.0089 + 0.0069 + spr), ("k_d=2.5%", 0.025)):
        pre, post = L * kd + (1 - L) * ke, L * kd * (1 - 0.30) + (1 - L) * ke
        wacc_g[(nm, kd_lab)] = pre
        print(f"  {nm}（株式{ke:.2%}・負債比率{L:.0%}）{kd_lab}: 節税効果なし {pre:.2%}／節税効果込み {post:.2%}")
        add("G 文献の資本構成", nm, f"株式{ke:.2%}・スプレッド{spr * 1e4:.0f}bp・負債比率{L:.0%}", kd_lab, kd,
            "加重平均（負債の節税効果なし）", pre, "")
        add("G 文献の資本構成", nm, f"株式{ke:.2%}・スプレッド{spr * 1e4:.0f}bp・負債比率{L:.0%}", kd_lab, kd,
            "加重平均（負債の節税効果込み τ=30%）", post, "")
for kd_lab in ("BBSW0.89%+0.69%+スプレッド", "k_d=2.5%"):
    for ref in ("全量コーポレートPPA", "全量政府CfD"):
        prem = wacc_g[("マーチャント", kd_lab)] - wacc_g[(ref, kd_lab)]
        print(f"  マーチャントの上乗せ（対 {ref}、{kd_lab}）: {prem * 100:.2f}pt")
        add("G 文献の資本構成", "マーチャント − " + ref, "加重平均の差（節税効果なし）", kd_lab, np.nan,
            "マーチャントの上乗せ（%ポイント）", prem * 100, "%pt")

# ---------------------------------------------------------------- (E) APV
rows_apv = []


def add_apv(panel, case, r_c, r_m, comp, pv, annuity_rate, basis=""):
    rows_apv.append({"パネル": panel, "収入の基準": basis, "ケース": case, "r_C": r_c, "r_A^M": r_m, "成分": comp,
                     "現在価値(円/kW)": pv, "年額換算(円/kW-年)": pv / ann(annuity_rate) if annuity_rate is not None else np.nan})


s_cap = min(0.5, SII_CAP_HALF / (SIZE_KW * I4))
print(f"\n補助1/2 の上限40億円: 5万kW・4h（総額{SIZE_KW * I4 / 1e8:.0f}億円）では実効補助率 {s_cap:.3f}。"
      f"上限が効き始める規模 {SII_CAP_HALF / 0.5 / I4 / 1e4:.1f}万kW")
print("\n=== (E1) APV: マーチャント4h ===")
apv1 = []
E1_CASES = [f"{TH_LAB[1.0]}・実績整合", f"{TH_LAB[1.567]}・実績整合", f"{TH_LAB[1.715]}・実績整合",
            f"{TH_LAB[1.0]}・モデル直値", f"{TH_LAB[1.0]}・旧0.81PF", f"{TH_LAB[1.0]}・旧裾補正", f"{TH_LAB[1.567]}・旧裾補正"]
for r_m in (0.06, 0.08, 0.09, 0.10):
    A = ann(r_m)
    for pn in E1_CASES:
        b, th, pi = PI[pn]
        for kn, kp in KP4.items():
            case = f"{pn}・{kn}"
            base = -I4 + (pi - FIXED[4]) * A
            cap = kp * A
            sub = {"補助1/3": I4 / 3, f"補助1/2（上限40億・5万kW、実効{s_cap:.0%}）": s_cap * I4, "補助1/2": 0.5 * I4}
            # 節税効果（上限・参考）。負債は補助後の投資額×L（補助で賄う部分は借りない）
            tax = {f"節税効果 L={L:.0%}（補助なし、投資額×L）": pvts(L * I4, tenor=15) for L in (0.3, 0.6)}
            tax_sub = pvts(0.6 * 0.5 * I4, tenor=15)            # 1/2 補助後の投資額×60%
            tax_ra = pvts(0.6 * I4, tenor=15, disc=r_m)
            ebit = pi + kp - FIXED[4] - I4 / T                  # 定額法20年の減価償却後（利息前）
            ebit_sub = pi + kp - FIXED[4] - 0.5 * I4 / T        # 1/2 補助を圧縮記帳した場合
            add_apv("4h マーチャント", case, np.nan, r_m, "基礎NPV（スポットのみ・借入なし）", base, r_m, b)
            add_apv("4h マーチャント", case, np.nan, r_m, "容量市場", cap, r_m, b)
            for k, v in sub.items():
                add_apv("4h マーチャント", case, np.nan, r_m, k, v, r_m, b)
            tot = {"APV: 基礎＋容量": base + cap,
                   "APV: 基礎＋容量＋補助1/3": base + cap + sub["補助1/3"],
                   "APV: 基礎＋容量＋補助1/2（上限40億・5万kW）": base + cap + s_cap * I4,
                   "APV: 基礎＋容量＋補助1/2": base + cap + sub["補助1/2"]}
            for k, v in tot.items():
                add_apv("4h マーチャント", case, np.nan, r_m, k, v, r_m, b)
            for k, v in tax.items():
                add_apv("4h マーチャント", case, np.nan, r_m, "参考: " + k, v, r_m, b)
            add_apv("4h マーチャント", case, np.nan, r_m, "参考: 節税効果 L=60%（補助1/2、補助後の投資額×L）", tax_sub, r_m, b)
            add_apv("4h マーチャント", case, np.nan, r_m, "参考: 節税効果 L=60%（補助なし、r_A^M で割引）", tax_ra, r_m, b)
            add_apv("4h マーチャント", case, np.nan, r_m, "参考: APV 基礎＋容量＋補助1/2＋節税効果（上限）",
                    tot["APV: 基礎＋容量＋補助1/2"] + tax_sub, r_m, b)
            # APV=0 に必要な θ（容量＋補助、π は θ に比例: π(θ)=θ·a − 充電従量）
            a_b = A_BASIS.get(b, np.nan)
            for s_lab, s in (("補助なし", 0.0), ("補助1/3", 1 / 3), ("補助1/2", 0.5), ("補助1/2（上限40億・5万kW）", s_cap)):
                for with_tax in (False, True):
                    ts = pvts(0.6 * (1 - s) * I4, tenor=15) if with_tax else 0.0
                    need = ((1 - s) * I4 - ts) / A + FIXED[4] + CHG[4] - kp
                    th_need = need / a_b
                    lab = f"APV=0 に必要な θ（{s_lab}{'＋節税効果の上限（負債＝補助後の投資額×60%）' if with_tax else ''}）"
                    rows_apv.append({"パネル": "4h マーチャント", "収入の基準": b, "ケース": case, "r_C": np.nan, "r_A^M": r_m,
                                     "成分": lab, "現在価値(円/kW)": np.nan, "年額換算(円/kW-年)": np.nan, "θ": th_need})
            rows_apv.append({"パネル": "4h マーチャント", "収入の基準": b, "ケース": case, "r_C": np.nan, "r_A^M": r_m,
                             "成分": "SPC 単体の課税所得（利息前、定額法20年）", "現在価値(円/kW)": np.nan,
                             "年額換算(円/kW-年)": ebit})
            rows_apv.append({"パネル": "4h マーチャント", "収入の基準": b, "ケース": case, "r_C": np.nan, "r_A^M": r_m,
                             "成分": "SPC 単体の課税所得（利息前、定額法20年、1/2補助を圧縮記帳）", "現在価値(円/kW)": np.nan,
                             "年額換算(円/kW-年)": ebit_sub})
            need0 = lambda s: (((1 - s) * I4) / A + FIXED[4] + CHG[4] - kp) / a_b
            apv1.append({"r_A^M": r_m, "ケース": case, "基礎": base, "容量": cap, "補助1/2": sub["補助1/2"],
                         "APV(容量)": base + cap, "APV(容量+補助1/3)": tot["APV: 基礎＋容量＋補助1/3"],
                         "APV(容量+補助1/2)": tot["APV: 基礎＋容量＋補助1/2"],
                         "θ(APV=0,補助なし)": need0(0.0), "θ(APV=0,1/2)": need0(0.5), "θ(APV=0,1/3)": need0(1 / 3),
                         "θ(APV=0,上限40億)": need0(s_cap),
                         "参考:節税(補助後×60%)": tax_sub, "課税所得(利息前)": ebit, "課税所得(圧縮記帳)": ebit_sub})
apv1 = pd.DataFrame(apv1)
print(apv1[apv1["ケース"].str.contains("容量1.25")].round(3).to_string(index=False))

print("\n=== (E2) APV: LTDA 6h ＝ マーチャント6h ＋ レベニュースワップ ===")
I6 = 6 * CAPEX_KWH
apv2 = []
for xn, x6 in X6.items():
    if xn == "旧モデル":
        continue
    bb = "実績整合" if xn == X6_MAIN else "旧裾補正"
    for r_c in (0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.06):
        for r_m in (0.08, 0.09, 0.10, 0.11):
            A_c, A_m = ann(r_c), ann(r_m)
            prices = dict(LTDA_CAP)
            prices["積み上げ（事業報酬率5%）"] = None
            for pn, F0 in prices.items():
                for qn, q in (("設備容量", 1.0), ("期待容量κ=0.932", KAPPA[6])):
                    F = (I6 * crf(0.05) + FIXED[6]) / q if F0 is None else F0
                    case = f"{pn}・契約容量＝{qn}"
                    base6 = -I6 + (x6 - FIXED[6]) * A_m
                    cap6 = KP6 * A_m
                    var = (1 - RETAIN) * x6 + KP6            # 手放す側（還付する他市場収益の9割＋容量市場の収入）
                    fixed_leg = F * q * A_c
                    var_leg = var * A_m
                    exp_tr = (F * q - var) * A_c
                    risk_tr = var * (A_c - A_m)
                    swap = fixed_leg - var_leg
                    tax60, tax80 = pvts(0.6 * I6, tenor=18), pvts(0.8 * I6, tenor=18)
                    apv_l = base6 + cap6 + swap
                    f_fair = var_leg / (q * A_c)
                    npv_single = -I6 + (F * q + RETAIN * x6 - FIXED[6]) * A_c
                    comps = [("基礎NPV（6h・スポットのみ・借入なし）", base6), ("容量市場（マーチャント時）", cap6),
                             ("マーチャント6h の NPV", base6 + cap6), ("固定側 PV（F·q を r_C で）", fixed_leg),
                             ("変動側 PV（他市場収益9割＋容量収入を r_A^M で）", -var_leg),
                             ("期待値の移転", exp_tr), ("リスク移転（割引率の差）", risk_tr), ("スワップ価値", swap),
                             ("LTDA 電源の APV", apv_l),
                             ("参考: 節税効果 L=60%（18年、上限）", tax60), ("参考: 節税効果 L=80%（18年、上限）", tax80),
                             ("参考: APV＋節税効果 L=80%（上限）", apv_l + tax80),
                             ("参考: 全体を r_C で割り引いた NPV", npv_single)]
                    for k, v in comps:
                        add_apv("6h LTDA", case, r_c, r_m, k, v, r_c, bb)
                    rows_apv.append({"パネル": "6h LTDA", "収入の基準": bb, "ケース": case, "r_C": r_c, "r_A^M": r_m,
                                     "成分": "リスク移転の比率（÷スワップ価値）", "現在価値(円/kW)": np.nan,
                                     "年額換算(円/kW-年)": np.nan, "比率": risk_tr / swap})
                    rows_apv.append({"パネル": "6h LTDA", "収入の基準": bb, "ケース": case, "r_C": r_c, "r_A^M": r_m,
                                     "成分": "公正な固定価格 F_fair（契約kWあたり）", "現在価値(円/kW)": np.nan,
                                     "年額換算(円/kW-年)": f_fair, "比率": F / f_fair})
                    rows_apv.append({"パネル": "6h LTDA", "収入の基準": bb, "ケース": case, "r_C": r_c, "r_A^M": r_m,
                                     "成分": "需要家からの移転の割合 (F−F_fair)/F", "現在価値(円/kW)": np.nan,
                                     "年額換算(円/kW-年)": np.nan, "比率": 1 - f_fair / F})
                    apv2.append({"6hスポット": xn, "r_C": r_c, "r_A^M": r_m, "上乗せ(pt)": round((r_m - r_c) * 100, 2), "価格": pn,
                                 "契約容量": qn, "F": F, "手放す側": var, "うち容量": KP6, "容量の割合": KP6 / var,
                                 "マーチャント6h": base6 + cap6, "期待値の移転": exp_tr, "リスク移転": risk_tr,
                                 "リスク比率": risk_tr / swap, "APV": apv_l, "参考:節税L80%": tax80, "NPV単一r_C": npv_single,
                                 "F_fair": f_fair, "F/F_fair": F / f_fair, "(F−F_fair)/F": 1 - f_fair / F})
apv2 = pd.DataFrame(apv2)
_a2 = apv2[apv2["6hスポット"] == X6_MAIN]
print(f"変動側（設備kWあたり、実績整合）= 0.9×{X6[X6_MAIN]:,.0f} ＋ {KP6:,.0f} = {(1 - RETAIN) * X6[X6_MAIN] + KP6:,.0f} 円/kW-年"
      f"（容量の割合 {KP6 / ((1 - RETAIN) * X6[X6_MAIN] + KP6):.1%}）")
print(_a2[_a2["r_C"].isin([0.025, 0.04, 0.05, 0.06])].pivot_table(index=["価格", "契約容量", "r_C"], columns="r_A^M", values="リスク比率").round(3).to_string())
_cap = _a2[_a2["価格"].str.startswith("上限")]
_cons = _cap[(_cap["上乗せ(pt)"] >= 4.0 - 1e-9) & (_cap["上乗せ(pt)"] <= 5.1 + 1e-9) & (_cap["r_C"] >= 0.04)]
print(f"リスク比率（上限価格）: r_C=5%・r_A^M=9〜10% {_cap[(_cap['r_C'] == 0.05) & _cap['r_A^M'].isin([0.09, 0.10])]['リスク比率'].min():.3f}〜"
      f"{_cap[(_cap['r_C'] == 0.05) & _cap['r_A^M'].isin([0.09, 0.10])]['リスク比率'].max():.3f}；上乗せ4.0〜5.1pt（r_C 4〜6%）"
      f" {_cons['リスク比率'].min():.3f}〜{_cons['リスク比率'].max():.3f}；r_C 2.5〜6%・r_A^M 8〜11% "
      f"{_cap[_cap['r_C'].between(0.025, 0.06)]['リスク比率'].min():.3f}〜{_cap[_cap['r_C'].between(0.025, 0.06)]['リスク比率'].max():.3f}；"
      f"r_C 1〜6% {_cap['リスク比率'].min():.3f}〜{_cap['リスク比率'].max():.3f}；積み上げ5% "
      f"{_a2[_a2['価格'].str.startswith('積み上げ') & _a2['r_C'].between(0.025, 0.06)]['リスク比率'].min():.3f}〜"
      f"{_a2[_a2['価格'].str.startswith('積み上げ') & _a2['r_C'].between(0.025, 0.06)]['リスク比率'].max():.3f}")
print(f"F/F_fair（上限価格）: r_C=5%・r_A^M=8〜9% {_cap[(_cap['r_C'] == 0.05) & _cap['r_A^M'].isin([0.08, 0.09])]['F/F_fair'].min():.2f}〜"
      f"{_cap[(_cap['r_C'] == 0.05) & _cap['r_A^M'].isin([0.08, 0.09])]['F/F_fair'].max():.2f}；r_C=5%・r_A^M=9〜10% "
      f"{_cap[(_cap['r_C'] == 0.05) & _cap['r_A^M'].isin([0.09, 0.10])]['F/F_fair'].min():.2f}〜{_cap[(_cap['r_C'] == 0.05) & _cap['r_A^M'].isin([0.09, 0.10])]['F/F_fair'].max():.2f}；"
      f"r_C 2.5% {_cap[_cap['r_C'] == 0.025]['F/F_fair'].min():.2f}〜{_cap[_cap['r_C'] == 0.025]['F/F_fair'].max():.2f}；"
      f"(F−F_fair)/F 上限価格 r_C 2.5〜6% {_cap[_cap['r_C'].between(0.025, 0.06)]['(F−F_fair)/F'].min():.3f}〜{_cap[_cap['r_C'].between(0.025, 0.06)]['(F−F_fair)/F'].max():.3f}")

# ---------------------------------------------------------------- (F) 確実性等価
print("\n=== (F) 確実性等価（期ごとの CAPM 調整）===")
lvl = hp.groupby("fy")["p_system"].mean()
base_sys = hp.loc[hp["fy"].isin([2023, 2024, 2025]), "p_system"].mean()
lth = np.log((lvl / base_sys).loc[2016:2025])
SIG = {"FY2016〜25（FY2022除く）": float(lth.drop(index=2022).std(ddof=1)),
       "FY2016〜25": float(lth.std(ddof=1))}
SIG["FY2016〜25 の2倍（K・容量価格のリスクの代用）"] = 2 * SIG["FY2016〜25"]
print("θ の年次 SD（log、システムプライス比で代理）:", {k: round(v, 3) for k, v in SIG.items()})
# 参考: 北海道エリア価格の年平均の比で測った場合（システムプライス比の方が大きく、リスク調整を大きく出す側）
lvl_h = hp.groupby("fy")["p_hokkaido"].mean()
lth_h = np.log((lvl_h / hp.loc[hp["fy"].isin([2023, 2024, 2025]), "p_hokkaido"].mean()).loc[2016:2025])
for lab, v in (("システムプライス比 FY2016〜25", SIG["FY2016〜25"]),
               ("システムプライス比 FY2016〜25（FY2022除く）", SIG["FY2016〜25（FY2022除く）"]),
               ("北海道エリア価格比 FY2016〜25（参考）", float(lth_h.std(ddof=1))),
               ("北海道エリア価格比 FY2016〜25（FY2022除く、参考）", float(lth_h.drop(index=2022).std(ddof=1)))):
    print(f"  σ_logθ {lab}: {v:.3f}")
    add("F 確実性等価", "θ の年次 SD（対数）", lab, "", np.nan, "σ_logθ", v, "")
# 恒久成分のランダムウォーク（8.7 の主仕様）の革新 σ: 格子と 38 の推定値（2023-04〜 0.112、全期間 0.299）
SIG_RW = {"σ_ξ=0.10（8.7 の格子の下端）": 0.10, "σ_ξ=0.112（8.7 の推定、2023-04〜）": 0.112,
          "σ_ξ=0.20（8.7 の格子）": 0.20, "σ_ξ=0.30（8.7 の格子の上端、全期間の推定0.299）": 0.30}
R_C = 0.06
d = 1 / (1 + R_C)
G_CASES = {"実績整合（a=8,427）": A_BASIS["実績整合"], "モデル直値（a=7,602）": A_BASIS["モデル直値"],
           "旧0.81×π_PF(0)（a=6,695）": A_BASIS["旧0.81PF"], "旧裾補正（×1.25、a=8,350）": A_BASIS["旧裾補正"]}
need94 = c_req94(R_C) - kp_main                    # 9.4 基準の参入必要スポット収益（6%）
need84 = 34_500.0 - 12_500.0                       # 8.4 標準
rows_ce = []


def ce_rows(gn, G, proc, sn, sig, phi, se):
    e_pi = G - CHG[4]
    B = np.array([sum((phi * d) ** k for k in range(T - j + 1)) for j in range(1, T + 1)])
    dj = d ** np.arange(1, T + 1)
    s_per = se * G * (dj * B).sum()                     # Σ_t d^t·SD(時点 t の価値の更新)
    s_fal = se * G * np.sqrt(((dj * B) ** 2).sum())     # SD(20年の PV)
    for lam in (0.2, 0.3, 0.4):
        for rho in (0.3, 0.6, 1.0):
            rp_pv = lam * rho * s_per
            rp_ann = rp_pv * crf(R_C)
            rp_fal = lam * rho * s_fal * crf(R_C)
            try:
                r_eq = brentq(lambda r: G * ann(r) - (G * ann(R_C) - rp_pv), R_C - 0.05, 3.0)
            except ValueError:
                r_eq = np.nan
            gap94, gap84 = need94 - e_pi, need84 - e_pi
            # 6%（契約型の水準）で測った不足額 gap に、マーチャントが負うリスク調整 RP を足したものが
            # マーチャントの参入に足りない額。リスクを全部移して埋まるのは RP/(gap+RP)
            sh94, sh84 = rp_ann / (gap94 + rp_ann), rp_ann / (gap84 + rp_ann)
            rows_ce.append({"収入の基準": gn, "θ の過程": proc, "σ_logθ": sn, "σ": sig, "φ": phi, "革新SD": se,
                            "λ": lam, "ρ": rho, "λρ": lam * rho,
                            "期待スポット粗収入G": G, "期待π": e_pi,
                            "RP現在価値(円/kW)": rp_pv, "RP年額(円/kW-年)": rp_ann, "RP/G": rp_ann / G,
                            "RP/期待π": rp_ann / e_pi,
                            "RP年額_20年PVのSD版": rp_fal, "期ごと÷20年PVのSD版": rp_ann / rp_fal,
                            "同値の収入割引率": r_eq, "収入のリスクプレミアム(pt)": (r_eq - R_C) * 100,
                            "不足額_9.4基準(円/kW-年)": gap94,
                            "RP÷(不足額+RP)_9.4基準": sh94, "期待値の移転の比率_下限_9.4基準": 1 - sh94,
                            "LTDA保険価値上限(0.9RP)": (1 - RETAIN) * rp_ann,
                            "不足額_8.4基準": gap84, "RP÷(不足額+RP)_8.4基準": sh84,
                            "期待値の移転の比率_下限_8.4基準": 1 - sh84,
                            "参考:RP÷不足額_9.4基準": rp_ann / gap94, "参考:RP÷不足額_8.4基準": rp_ann / gap84})


for gn, G in G_CASES.items():
    for sn, sig in SIG.items():
        for phi in (0.0, 0.5, 0.9):
            ce_rows(gn, G, "定常 AR(1)（年次 SD を定常 SD とみなす）", sn, sig, phi, sig * np.sqrt(1 - phi ** 2))
    for sn, sig in SIG_RW.items():
        ce_rows(gn, G, "恒久成分のランダムウォーク（φ=1、革新 σ_ξ、8.7 と整合）", sn, sig, 1.0, sig)
ce = pd.DataFrame(rows_ce)
main_ce = ce[(ce["σ_logθ"] == "FY2016〜25") & (ce["θ の過程"].str.startswith("定常"))]
print(main_ce.pivot_table(index=["収入の基準", "φ"], columns=["λ", "ρ"], values="RP年額(円/kW-年)").round(0).to_string())
for gn in G_CASES:
    print(f"--- 収入の基準 {gn}（gap 9.4 基準 {need94 - (G_CASES[gn] - CHG[4]):,.0f}、8.4 基準 {need84 - (G_CASES[gn] - CHG[4]):,.0f}）")
    for proc in ce["θ の過程"].unique():
        for sn in ce[ce["θ の過程"] == proc]["σ_logθ"].unique():
            sub = ce[(ce["収入の基準"] == gn) & (ce["θ の過程"] == proc) & (ce["σ_logθ"] == sn) & (ce["λ"].isin([0.2, 0.4])) & (ce["ρ"].isin([0.3, 1.0]))]
            mid = ce[(ce["収入の基準"] == gn) & (ce["θ の過程"] == proc) & (ce["σ_logθ"] == sn) & (ce["λ"] == 0.3) & (ce["ρ"] == 0.6)]
            print(f"  [{proc[:6]}|{sn}] RP年額 {sub['RP年額(円/kW-年)'].min():,.0f}〜{sub['RP年額(円/kW-年)'].max():,.0f}、"
                  f"RP/G 最大 {sub['RP/G'].max():.3f}、"
                  f"RP÷(不足額+RP)(9.4) {sub['RP÷(不足額+RP)_9.4基準'].min():.3f}〜{sub['RP÷(不足額+RP)_9.4基準'].max():.3f}"
                  f"（λρ=0.18 で {mid['RP÷(不足額+RP)_9.4基準'].min():.3f}〜{mid['RP÷(不足額+RP)_9.4基準'].max():.3f}）、"
                  f"(8.4) {sub['RP÷(不足額+RP)_8.4基準'].min():.3f}〜{sub['RP÷(不足額+RP)_8.4基準'].max():.3f}、"
                  f"収入のプレミアム {sub['収入のリスクプレミアム(pt)'].min():.2f}〜{sub['収入のリスクプレミアム(pt)'].max():.2f}pt、"
                  f"期ごと÷PVのSD版 {sub['期ごと÷20年PVのSD版'].min():.2f}〜{sub['期ごと÷20年PVのSD版'].max():.2f}")

# ---------------------------------------------------------------- 書き出し
irr_df = pd.DataFrame(rows_irr)
irr_df.to_csv(os.path.join(PROC, "irr_cost_of_capital.csv"), index=False)
apv_df = pd.DataFrame(rows_apv)
apv_df.to_csv(os.path.join(PROC, "apv_decomposition.csv"), index=False)
ce.to_csv(os.path.join(PROC, "certainty_equivalent.csv"), index=False)
print(f"\n書き出し: irr_cost_of_capital.csv {len(irr_df)}行, apv_decomposition.csv {len(apv_df)}行, certainty_equivalent.csv {len(ce)}行")

# ---------------------------------------------------------------- 図: APV のウォーターフォール
BLUE, RED, NEUT = "#2a78d6", "#e34948", "#595959"


def waterfall(ax, steps, title):
    """steps: (ラベル, 値, "total"|"delta")。描いた範囲（最小, 最大）を返す"""
    run, xs, ext = 0.0, [], [0.0]
    for i, (lab, v, kind) in enumerate(steps):
        if kind == "total":
            lo, hi, col = min(0, v), max(0, v), NEUT
            run = v
        else:
            lo, hi = (run, run + v) if v >= 0 else (run + v, run)
            col = BLUE if v >= 0 else RED
            run += v
        ax.bar(i, hi - lo, bottom=lo, width=0.62, color=col, edgecolor="white", linewidth=2)
        ext += [lo, hi]
        txt = (f"{v / 1e4:+.1f}" if kind != "total" else f"{v / 1e4:.1f}").replace("-", "−")
        ytxt, va = (hi, "bottom") if (v >= 0 or kind != "total") else (lo, "top")
        if kind != "total" and v < 0:
            ytxt, va = lo, "top"
        ax.text(i, ytxt + (0.6e4 if va == "bottom" else -0.6e4), txt, ha="center", va=va, fontsize=8.5, color="#0b0b0b")
        if i < len(steps) - 1:
            ax.plot([i + 0.31, i + 0.69], [run, run], color="#999999", lw=0.8, ls=":")
        xs.append(lab)
    ax.axhline(0, color=GRAY, lw=0.8)
    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels(xs, fontsize=8.5, color=GRAY)
    ax.set_title(title, fontsize=9.5, color="#0b0b0b", loc="left")
    ax.grid(axis="y", color="#DDDDDD", lw=0.6)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=8.5)
    return min(ext), max(ext)


r_m_fig, r_c_fig = 0.09, 0.05
A_m, A_c = ann(r_m_fig), ann(r_c_fig)
pi_fig = PI[MAIN1][2]
kp_fig = KP4["容量1.25万（2029年度向け）"]
base_f = -I4 + (pi_fig - FIXED[4]) * A_m
steps1 = [("基礎NPV\n（スポットのみ）", base_f, "total"), ("容量市場\n（1.25万円）", kp_fig * A_m, "delta"),
          ("補助金\n（1/2）", 0.5 * I4, "delta")]
steps1.append(("APV", sum(v for _, v, _ in steps1), "total"))
tax_f1 = pvts(0.6 * 0.5 * I4, tenor=15)
F_fig, q_fig = LTDA_CAP["上限7.2万（応札年度2026・北海道71,768）"], KAPPA[6]
x6_fig = X6[X6_MAIN]
var_f = (1 - RETAIN) * x6_fig + KP6
base6_f = -I6 + (x6_fig - FIXED[6]) * A_m
steps2 = [("基礎NPV\n（6時間・\nスポットのみ）", base6_f, "total"), ("容量市場\n（マーチャント時）", KP6 * A_m, "delta"),
          ("期待値の移転", (F_fig * q_fig - var_f) * A_c, "delta"), ("リスク移転\n（割引率の差）", var_f * (A_c - A_m), "delta")]
steps2.append(("APV", sum(v for _, v, _ in steps2), "total"))
tax_f2 = pvts(0.8 * I6, tenor=18)
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする。条件（割引率・π(0)・上限価格）は図の注に書く
fig, axes = plt.subplots(2, 1, figsize=(6.1, 5.6), sharey=True, layout="constrained")
e1 = waterfall(axes[0], steps1, "(a) マーチャント4時間")
e2 = waterfall(axes[1], steps2, "(b) LTDA 6時間")
axes[0].set_ylim(min(e1[0], e2[0]) - 7e4, max(e1[1], e2[1]) + 6e4)
for a_ in axes:
    a_.set_ylabel("現在価値（万円/kW）", fontsize=9, color=GRAY)
    a_.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v / 1e4:.0f}".replace("-", "−")))
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "apv_decomposition.png"), dpi=300)
print("図: figures/hokkaido/apv_decomposition.png")
for lab, v, k in steps1 + steps2:
    print(f"  {lab.replace(chr(10), '')}: {v:,.0f}")
print(f"  参考: 節税効果 (a) {tax_f1:,.0f}、(b) {tax_f2:,.0f}")
