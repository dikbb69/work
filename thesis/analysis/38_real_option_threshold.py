#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""不確実性の下での参入閾値（実物オプション）: 静学の損益分岐 θ* と待機を考慮した参入閾値（競争均衡 θ_c・単独企業 θ̄）、参入が開く確率、接続枠の待機価値

手法:
  A. 価格水準の2因子分解（Schwartz-Smith 型）
     月平均システムプライス ÷ FY2023〜25 の同月平均を θ の代理とし（2016-04〜2026-06、123か月）、対数を
     ランダムウォークの恒久成分 ξ と AR(1) の一時成分 χ に分ける（statsmodels UnobservedComponents、カルマンフィルタ・
     平滑化）。全期間と部分標本（2016-04〜2021-03、2023-04〜2026-06）で推定し、σ_ξ のプロファイル尤度、
     ADF・KPSS・分散比（Lo-MacKinlay、不均一分散に頑健な z*）を併記する。北海道エリア価格の代理は参考。
     恒久成分のドリフト（対数）も参考として推定する（ドリフト付きランダムウォーク＋AR(1)、平滑化した状態の分散で標準誤差）。
  B. 年次の動的計画法（対数 θ の格子 2,001点）
     年間キャッシュフロー = a·θ·G(K)/G(0) − F_s。a は限界参入者の粗収益（K=0・θ=1、充電従量控除前）で、主は
     実績整合の a = λ·c_モデル(0) = 1.1085×7,602 = 8,427円/kW-年（価格過程モデルの価格経路の上で戦略c の実現粗利を
     直接計算し、FY2023〜25 の実績の戦略c に in-sample で校正した値。41_equilibrium_v3.py・pi_k_curve_v3.csv）。
     G(K) は同じ曲線の戦略c の粗利 c(K)（仕様A（26）、完全予見の増分貪欲フリート、1万kW 刻み）。
     F_s = 運維・廃止0.53万 + 託送等固定0.69万 + 充電従量1,752 − 実効容量収入（円/kW-年。s は暦年、s=1 が FY2027）。
     投資額 I_t = 4h × 資本費（6.8万円/kWh から年率 g で低下、下限2.3万円/kWh）、寿命20年。θ は年次の対数正規
     マルチンゲール（α=0、D-P の記法で δ=r−α=r）。実物確率の下で割引率 r（WACC）で割り引く（リスク中立化はしない）。
     静学 θ*_t = (I_t + Σ_k F_{t+k}/(1+r)^k)/(a·年金現価)（F 一定なら 9.4 の式 (I·CRF+F)/a）。
     単独企業（排他的な権利を持つ主体）の最適行使閾値 θ̄_t を後ろ向きに解く（他社の参入を無視して自分の待機は考慮する、
     Leahy (1993) の「近視眼的」な閾値と同じ形）。
  C. 検算
     C1 g=0 の閉形式 β/(β−1)（ρ=ln(1+r)、β=1/2+√(1/4+2ρ/σ²)）と、年1回判断の補正 exp(−0.5826σ√Δt)
        （Broadie-Glasserman-Kou の定数。Howison (2007) はバミューダ型の最適行使境界が連続行使の境界から
        1次のオーダーでこの定数だけずれることを示している）。
     C2 σ→0 の使用者費用（Jorgenson）: θ̄ = (I·CRF·(r+g)/r + F)/a。
     C3 Dixit-Pindyck 第8章の競争産業均衡（連続時間・永久寿命）: 上側に反射壁 P̄ を持つ価格の収入現在価値を
        モンテカルロ（ブラウン橋で区間内の最大値を正確に生成）で求め、正しく計算した NPV=0 となる P̄/(ρI) が
        β/(β−1) に一致することを確かめる。
     C4 本研究の設定（年次・20年寿命）での競争均衡の参入閾値 θ_c: 閾値で参入した者の NPV を、将来の参入で
        X=θ·G(K)/G(0) が閾値に押さえられることを織り込んで計算し（モンテカルロ5万本・共通乱数、1年の建設ラグ）、
        NPV=0 となる閾値を、資本費が下限に達する年（容量収入が時変なら、それと FY2029 の遅い方）から後ろ向きに解く
        （ブレント法）。全社が θ̄ で参入した場合の参入者 NPV、寿命を40・100年に延ばした検算（寿命100年で θ_c=θ̄ となり、
        Leahy の命題の離散版を再現）を含む。
     C5 収益の基準の換算: a を m 倍すると θ の閾値はちょうど 1/m 倍になる（θ と a は積でしか入らない）。基準別の閾値の比が
        a の比の逆数に一致することを確かめる（確率は出発点を m 倍するのと同値）。
  D. 参入が開く確率と E[K]（2030・2035・2040年度まで）
     恒久成分の推定値（2026-06）から θ を生成し、競争均衡（θ_c,t）・単独企業（θ̄_t）・静学（θ*_t）の3ルールで比べる。
     参入が開く確率は格子上の前進計算（吸収壁）、フリートはモンテカルロ20万本（K_t は max_s≤t の不可逆、
     X=θ·G(K)/G(0) が閾値で押さえられる）。収益の基準（実績整合・モデル直値・旧0.81×π_PF・旧裾補正・λ の95%区間）別。
  E. 排他的な接続枠の待機価値 W0（永久および期限3・5・10年）と、保証金（概算工事費負担金の5%・10%）との比較。
  F. 参考: 2時間仕様（Helios 型）の静学閾値と、回収に必要な一時的な追加収入。実績整合の基準では、実績価格
     （FY2023〜25）の上で戦略c を2時間・4時間で直接計算した粗利（4h 8,427、2h 4,955円/kW-年）を a とする。旧基準は
     26 を部品として読み込み、θ=1 の FY2023〜25 パスで2時間の完全予見粗利を計算して0.81を掛ける。4時間仕様も
     容量収入0 の行を併記し、条件を揃えて比べる。
  G. 感応度: θ の期待成長 α>0（年2%、および対数のドリフト0 に当たる α=exp(σ²/2)−1）の下での閾値と参入が開く確率。
     α>0 では静学の損益分岐を「期待経路で評価した静学」θ*_α=(I+F·年金現価)/(a·成長年金現価) と、9.4 の一定価格の θ* の
     両方で示す。費用 F は一定（F は純額1,452円と小さいので、費用も同率で上がる場合との差は小さい）。
  H. 感応度（v3 で新設）: (1) 実効容量収入の時変（FY2027〜29 は1.25万円、FY2030 以降は1.75万円＝0.836×20,911、
     または2.5万円）と FY2026 から1.75万円一定、(2) SII 補助（1/2・1/3（上限なし）、1/2 で上限40億円が効く5万kW
     の実効29.4%。投資額と下限を (1−s) 倍）、(3) 既設・契約型の容量 K_exo（20万kW＝接続済み、76.8万kW＝接続済み＋
     LTDA 北海道の第3回の別解、87.4万kW＝接続済み＋LTDA 北海道67.42万kW（主）。a=λ·c(K_exo)、
     X=θ·c(K_exo+K)/c(K_exo)。逆向きの偏り（参入に不利な側）の目安）。旧基準の行は監査の検算の再現。
  I. 感応度（D3、検証で追加）: フリート配分を戦略c の窓に従う配分にした c(K)（pi_k_curve_v3.csv「戦略cの窓」）で
     E[K]・分位点を再計算する（主の容量収入1.25万円と1.75万円（FY2030〜）、r=6%、g=0/5%）。閾値と確率は配分によらない。
出力:
  data/processed/real_option_threshold.csv      参入閾値の格子（収入の基準×σ×g×r×容量収入×仕様）と検算 C1〜C4
  data/processed/real_option_entry_prob.csv     参入が開く確率・E[K]・95%/99%点（競争均衡・単独企業・静学、収入の基準別）
  data/processed/real_option_price_level.csv    2因子分解の推定値・プロファイル尤度・単位根/分散比検定・年度分解
  data/processed/real_option_waiting_value.csv  接続枠の待機価値 W0 と行使確率、保証金との比較
  data/processed/real_option_short_duration.csv 2時間仕様の参考試算（実績整合・旧の2基準）
  data/processed/real_option_drift_sensitivity.csv θ の期待成長 α>0 の感応度（閾値と参入が開く確率）
  data/processed/real_option_sensitivity_v3.csv 容量収入の時変・補助・K_exo の感応度（v3 で新設）
  data/processed/real_option_fleet_alloc_v3.csv フリート配分（増分貪欲・戦略c の窓）別の E[K]・分位点（D3、検証で追加）
  figures/hokkaido/real_option_threshold.png
限界:
  恒久成分の σ は識別が弱い（全期間0.30は FY2021〜22 の燃料危機で決まり、部分標本では0〜0.11）ので σ は0.10〜0.30 の
  幅で示す。θ の期待成長 α=0（水準のマルチンゲール。推定した UC モデルは対数のドリフト0 で、水準では年 exp(σ²/2)−1 の
  成長にあたる。ドリフトは識別できず、G で感応度を示す）、容量収入は K によらず一定（時変は暦年だけ）、
  π(K;θ)∝θ（c(K;θ=1.567)/(1.567·c(K;1)) は K≤100（1万kW 刻みの全格子点）で0.9994〜1.0012。下限価格0.01円の上の
  部分が θ に比例するため）。
  λ は K=0・θ=1 の in-sample 校正で、K>0 でも同じ比を当てている（out-of-sample の比は FY2026 4〜6月 1.23、FY2022 1.60）。
  Leahy (1993) の「近視眼的な閾値＝競争均衡の閾値」は無限寿命で成り立ち（C3・C4 の寿命100年で再現）、
  20年寿命では競争均衡の閾値が単独企業の閾値より1〜2割低い。参入が開く確率は主に θ_c で評価する。年1回の判断・1年の
  建設ラグ、容量市場の K 依存（表8.7）・退役は扱わない。代理変数はシステムプライスで、θ（北海道エリア価格の水準係数）
  との対数相関は0.93。補助の競争均衡は後続の参入者も補助を受けると置いた近似（実際は予算の制約で後続は補助なしになり
  うるので、補助を受けた参入者の閾値は θ_c と θ* の間にある。静学の規則の確率を上限として併記）。K_exo は推定期間の
  価格に既に入っている既設の蓄電池との二重計上を含み、c(K) の K≥72万kW は推定範囲外の外挿の性格が強い。
  フリート配分は完全予見の増分貪欲（刻み1万kW）で、刻みを細かくすると K≥50 で π(K) がわずかに上がる（41 の注記）。

v3 での修正（2026-10-21、主任の決定 D1・D2・D5 と監査 A8-7-2・A8-7-3・L-5・L-6 への対応）:
  1. 収益の基準を D1 に合わせた。旧版の a = capture率0.81×π_PF(0) = 6,695（二重割引）をやめ、実績整合の
     a = λ·c(0) = 8,427 を主にした。モデル直値（a=c(0)=7,602）、旧0.81×π_PF（6,695）、旧裾補正（×1.2472、8,350）、
     λ の95%区間（1.030・1.191）を感応度として D に併記する（列「収入の基準」）。旧版の「裾の補正×1.25」の行は
     旧裾補正の基準に置き換えた（θ を1.25倍するのと同値なのは旧版と同じ）。
  2. π(K) の形を pi_k_curve_v3.csv の戦略c の粗利 c(K)（1万kW 刻み、K=0〜150、以降10万kW 刻みで300 まで）にした。
     旧版は equilibrium_surface.csv の π_PF(K)（0・10・25・50・100・150・200、K=25 は実際には30 で計算された格子）。
     閾値と確率は π(K) の形によらず（X で書くため）、E[K] と分位点だけが変わる。旧基準の形には v3 の π_PF(K) を使う。
  3. 費用 F を暦年の列 F_s にした（容量収入の時変ケース。F 一定のときは旧版と同じ式）。entrant_npv・solve・
     competitive_boundary・theta_static に参入年 t を渡す。容量収入が時変のとき、競争均衡の境界は
     tf=max(資本費が下限に達する年, 3) から後ろ向きに解く（t≥3 の参入なら CF はすべて FY2030 以降）。
  4. ブロック H（新設）: 容量収入の時変、補助、K_exo。出力は real_option_sensitivity_v3.csv。
  5. ブロック F: 実績整合の基準の2h・4h を、実績価格の上で戦略c（直近29日・同じ曜日区分の平均ランク、5日以上、
     同値は均等配分。36 と同じ）を直接計算した粗利にした。旧基準の行も残す。
  6. 図: 主の基準（実績整合）で描き直した。脚注に旧基準の θ*（3.76）を併記。
  7. 静学の損益分岐が0以下（容量収入だけで費用を賄える）の年は、競争均衡の閾値を格子の下端（0.02）に置く（どの θ でも
     参入）。容量収入2.5万円（FY2030〜）は、資本費低下5%/年ではこの状態になり、K によらず一定の容量価格の下では参入が
     際限なく続くので、g=0 だけを計算する。
  8. ブロック I（検証で追加、D3）: 戦略c の窓に従うフリート配分での E[K]。k_of_ratio は仕様ごとの K 格子（"KG"）を
     受け付ける（既定は従来の格子なので、A〜H の出力は変わらない）。
"""
import contextlib
import io
import os
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib import font_manager
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from scipy.stats import norm
from statsmodels.tsa.stattools import adfuller, kpss

warnings.filterwarnings("ignore")
for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
PROC = os.path.join(ROOT, "data", "processed")
GRAY = "#595959"
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 40)
SEED = 20261020

# =====================================================================================
# 0. 諸元（9.4・28_equilibrium_surface.py と同じ費用。収益は v3 の D1 基準）
# =====================================================================================
_cv = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
_cv = _cv[(_cv["価格モデル"] == "仕様A（26、水準係数付き）") & (_cv["シナリオ"] == "現状") & (_cv["θ"] == 1.0)
          & (_cv["フリート配分"] == "完全予見の増分貪欲（主）") & (_cv["刻み(万kW)"] == "1.0")].sort_values("K(万kW)")
assert _cv["K(万kW)"].is_unique and _cv["K(万kW)"].iloc[0] == 0
K_GRID = _cv["K(万kW)"].to_numpy(float)                       # 0〜150（1万kW）、160〜300（10万kW）
C_GRID = np.minimum.accumulate(_cv["c"].to_numpy(float))       # 戦略c の粗利 c(K)（モデル直値、充電従量控除前）
PF_GRID = np.minimum.accumulate(_cv["π_PF"].to_numpy(float))   # 完全予見粗利 π_PF(K)（旧基準の形）
LAM = float(_cv["校正係数λ"].iloc[0])                          # 1.1085（実績c ÷ モデルc、K=0・θ=1、FY2023〜25）
TAIL_OLD = float((_cv["π_旧裾補正"].iloc[0] + 1752.0) / (0.81 * _cv["π_PF"].iloc[0]))   # 旧版の ×1.25（1.2472）
_lr = pd.read_csv(os.path.join(PROC, "price_model_level_ratios.csv"))
_lr = _lr[_lr["期間"].str.startswith("λ の95%区間")].iloc[0]
LAM_LO, LAM_HI = float(_lr["c比_下限95"]), float(_lr["c比_上限95"])   # 1.030・1.191（定常ブートストラップ）
PI_PF0 = float(PF_GRID[0])                                     # 8,265.5
C0 = float(C_GRID[0])                                          # 7,602.4
CAPTURE, WHEEL_KWH, KPCAP = 0.81, 1.2, 12_500.0
WHEEL_FIX = 6_900.0
CAPEX0, CAPEX_FLOOR, LIFE = 6.8e4, 2.3e4, 20
SIGMAS = [0.10, 0.15, 0.20, 0.30]
GS = [0.0, 0.03, 0.05, 0.08]
RS = [0.06, 0.08]
BGK = 0.5826
FY0 = 2026                                              # 判断の起点（t=0）
SMAX = 320                                              # 費用の暦年列 F_s の長さ
S_SW = 2030 - FY0                                       # 容量収入が切り替わる暦年（s=4 が FY2030）
KP2030 = 20_911 * 0.836                                 # 2030年度向け Net CONE × κ（17,482）
KP25 = 25_000.0                                         # 上限近傍（9.2(a)・表9.2 の2.5万円）
# 収益の基準: a（K=0・θ=1 の粗収益、充電従量控除前）と π(K) の形 G(K)
BASES = {"実績整合": (LAM * C0, C_GRID), "モデル直値": (C0, C_GRID), "旧0.81PF": (CAPTURE * PI_PF0, PF_GRID),
         "旧裾補正": (CAPTURE * TAIL_OLD * PI_PF0, PF_GRID),
         "実績整合（λ下限）": (LAM_LO * C0, C_GRID), "実績整合（λ上限）": (LAM_HI * C0, C_GRID)}
MAIN_BASIS = "実績整合"


def om_cost(hours):
    """運維5,000円/kW-年＋廃止措置（建設費の5%）の年額。4h で0.53万（notes/20・28 と同じ）、h に比例して廃止分を按分"""
    return 5_000.0 + 300.0 * hours / 4


def make_spec(hours=4, capex=CAPEX0, basis=MAIN_BASIS, kpcap=KPCAP, kp_hi=None, subsidy=0.0, kexo=0.0,
              A=None, label="4時間（標準）"):
    """参入者の仕様。kp_hi を与えると FY2030（s=4）以降の実効容量収入を kp_hi に切り替える（FY2027〜29 は kpcap）。
    subsidy は投資額と下限に掛ける補助率、kexo は既設・契約型の容量（万kW）。A を与えるとその粗収益を使う（2h 用）"""
    a0, G = BASES[basis]
    g0 = float(np.interp(kexo, K_GRID, G))
    A_ = a0 * g0 / G[0] if A is None else A
    f_lo = om_cost(hours) + WHEEL_FIX + hours * 365 * WHEEL_KWH - kpcap
    Fs = np.full(SMAX, f_lo)
    if kp_hi is not None:
        Fs[S_SW:] = f_lo + kpcap - kp_hi
    key = f"{basis}|h{hours}|cx{capex:.0f}|kp{kpcap:.1f}|hi{kp_hi}|s{subsidy:.4f}|kx{kexo}|A{A_:.4f}"
    return {"label": label, "basis": basis, "hours": hours, "capex": capex, "kpcap": kpcap, "kp_hi": kp_hi,
            "subsidy": subsidy, "kexo": kexo, "A": A_, "F": float(Fs[-1]), "Fs": Fs, "S_sw": S_SW if kp_hi is not None else 0,
            "I0": hours * capex * (1 - subsidy), "Ifloor": hours * CAPEX_FLOOR * (1 - subsidy), "G": G, "g0": g0,
            "key": key, "_pvF": {}}


SP4 = make_spec()
SPB = {b: make_spec(basis=b) for b in BASES}


def crf(r, n=LIFE):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def annuity(r, n=LIFE):
    return (1 - (1 + r) ** -n) / r


def grow_annuity(r, alpha, n=LIFE):
    """Σ_{k=1..n} ((1+α)/(1+r))^k（α=0 なら年金現価係数）"""
    if alpha == 0:
        return annuity(r, n)
    q = (1 + alpha) / (1 + r)
    return q * (1 - q ** n) / (1 - q)


def pvF(sp, r, life=LIFE):
    """t 年に参入判断した者の費用の現在価値 Σ_{k=1..life} F_{t+k}/(1+r)^k（t=0..SMAX−life−1）"""
    key = (round(r, 10), life)
    if key not in sp["_pvF"]:
        d = (1 + r) ** -np.arange(1, life + 1)
        Fs = sp["Fs"]
        sp["_pvF"][key] = np.array([Fs[t + 1:t + 1 + life] @ d for t in range(len(Fs) - life)])
    return sp["_pvF"][key]


def theta_static(I, r, sp=SP4, t=0, alpha=0.0, life=LIFE):
    """t 年に参入する場合の静学の損益分岐（期待経路で評価。α=0・F 一定なら 9.4 の θ* = (I·CRF+F)/a）"""
    return (I + pvF(sp, r, life)[t]) / (sp["A"] * grow_annuity(r, alpha, life))


def theta_static_alpha(I, r, sp=SP4, alpha=0.0):
    return theta_static(I, r, sp, 0, alpha)


TH_STAR6 = theta_static(SP4["I0"], 0.06)
TH_STAR6_OLD = theta_static(SPB["旧0.81PF"]["I0"], 0.06, SPB["旧0.81PF"])
print(f"[0] 収益の基準（a=K=0・θ=1 の粗収益、円/kW-年）: " + "、".join(f"{b} {v[0]:,.1f}" for b, v in BASES.items()))
print(f"    λ={LAM:.4f}（95%区間 {LAM_LO:.4f}〜{LAM_HI:.4f}）、旧裾補正の係数 {TAIL_OLD:.4f}、c(0)={C0:,.1f}、π_PF(0)={PI_PF0:,.1f}")
print(f"    F={SP4['F']:,.0f}, I0={SP4['I0']:,.0f}円/kW。静学 θ*(6.8万円/kWh, WACC6%) = {TH_STAR6:.3f}（実績整合）、"
      f"{TH_STAR6_OLD:.3f}（旧0.81PF、原稿 表9.2: 3.76）、WACC8% = {theta_static(SP4['I0'], 0.08):.3f}")
for b in BASES:
    print(f"    θ*({b}, 6%) = {theta_static(SPB[b]['I0'], 0.06, SPB[b]):.3f}")

# =====================================================================================
# A. 価格水準 θ の2因子分解
# =====================================================================================
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"],
                 usecols=["ts", "p_system", "p_hokkaido", "fy"])
hp["m"] = hp["ts"].dt.to_period("M").dt.to_timestamp()
mon = hp.groupby("m").agg(p_system=("p_system", "mean"), p_hokkaido=("p_hokkaido", "mean"), fy=("fy", "first"))
mon["fy"] = mon["fy"].astype(int)
mon["cal"] = mon.index.month
_base = mon[mon["fy"].between(2023, 2025)].groupby("cal")[["p_system", "p_hokkaido"]].mean()
mon["proxy_sys"] = mon["p_system"] / mon["cal"].map(_base["p_system"])
mon["proxy_hkd"] = mon["p_hokkaido"] / mon["cal"].map(_base["p_hokkaido"])
mon = mon[mon.index >= "2016-04-01"]

pl_rows = []   # real_option_price_level.csv（縦持ち）


def add_pl(block, series, sample, item, value):
    pl_rows.append({"ブロック": block, "系列": series, "標本": sample, "項目": item, "値": value})


th_csv = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
thm = th_csv[th_csv["ym"].str.contains("-")].copy()
thm["m"] = pd.to_datetime(thm["ym"] + "-01")
ov = mon.join(thm.set_index("m")["theta_m"], how="inner")
for col, lab in (("proxy_sys", "システムプライス代理"), ("proxy_hkd", "北海道価格代理")):
    c = float(np.corrcoef(np.log(ov["theta_m"]), np.log(ov[col]))[0, 1])
    add_pl("代理変数の妥当性", lab, f"重複{len(ov)}か月（2022-04〜2026-06）", "月次 θ_m との対数相関", c)
    print(f"[A] 月次 θ_m と{lab}の対数相関: {c:.3f}（重複{len(ov)}か月）")

SAMPLES = {"全期間 2016-04〜2026-06": ("2016-04-01", "2026-06-01"),
           "2016-04〜2021-03": ("2016-04-01", "2021-03-01"),
           "2023-04〜2026-06": ("2023-04-01", "2026-06-01")}


def fit_uc(y, fix_level_var=None):
    """対数代理 = ξ（ランダムウォーク）+ χ（AR(1)）。複数の初期値で最尤推定し、対数尤度が最大のものを返す"""
    mod = sm.tsa.UnobservedComponents(y, level="random walk", autoregressive=1)
    v = np.var(np.diff(y))
    best = None
    for s_lvl in (0.05, 0.3, 1.0):
        for s_ar in (0.3, 1.0):
            for phi in (0.3, 0.6, 0.9):
                st = np.array([s_lvl * v, s_ar * v, phi])
                try:
                    if fix_level_var is None:
                        res = mod.fit(start_params=st, disp=False, maxiter=3000)
                    else:
                        res = mod.fit_constrained({"sigma2.level": fix_level_var}, start_params=st[1:], disp=False, maxiter=3000)
                except Exception:
                    continue
                if np.isfinite(res.llf) and (best is None or res.llf > best.llf + 1e-9):
                    best = res
    return mod, best


uc_store = {}
for col, lab in (("proxy_sys", "システムプライス代理"), ("proxy_hkd", "北海道価格代理")):
    for sname, (a, b) in SAMPLES.items():
        s = mon.loc[a:b]
        y = np.log(s[col].to_numpy())
        mod, res = fit_uc(y)
        p = dict(zip(mod.param_names, res.params))
        sig_xi = float(np.sqrt(max(p["sigma2.level"], 0.0) * 12))
        phi = float(p["ar.L1"])
        s_chi = float(np.sqrt(p["sigma2.ar"]))
        xi_s, chi_s = res.smoothed_state[0], res.smoothed_state[1]
        comp = pd.DataFrame({"log_proxy": y, "xi": xi_s, "chi": chi_s, "xi_filt": res.filtered_state[0],
                             "fy": s["fy"].to_numpy()}, index=s.index)
        uc_store[(col, sname)] = comp
        out = {"σ_ξ（年率）": sig_xi, "φ_χ（月）": phi,
               "χ の半減期（月）": float(np.log(0.5) / np.log(phi)) if 0 < phi < 1 else np.nan,
               "σ_χ（月）": s_chi, "χ の定常SD": s_chi / np.sqrt(1 - phi ** 2) if abs(phi) < 1 else np.nan,
               "対数尤度": float(res.llf), "月数": len(y),
               "ξ 期末（2026-06 または標本末、フィルタ）": float(np.exp(res.filtered_state[0][-1]))}
        for k, v in out.items():
            add_pl("2因子分解", lab, sname, k, v)
        fyx = comp.groupby("fy")[["log_proxy", "xi", "chi"]].mean().apply(np.exp)
        for fy in fyx.index:
            if fy in (2020, 2021, 2022, 2023, 2024, 2025, 2026):
                tag = "FY2026（4〜6月）" if fy == 2026 else f"FY{fy}"
                add_pl("年度分解（対数平均: 実績＝恒久×一時）", lab, sname, f"{tag} 実績", float(fyx.loc[fy, "log_proxy"]))
                add_pl("年度分解（対数平均: 実績＝恒久×一時）", lab, sname, f"{tag} 恒久 ξ", float(fyx.loc[fy, "xi"]))
                add_pl("年度分解（対数平均: 実績＝恒久×一時）", lab, sname, f"{tag} 一時 χ", float(fyx.loc[fy, "chi"]))
        print(f"[A] {lab} {sname}: σ_ξ={sig_xi:.3f}/年, φ={phi:.3f}/月, σ_χ={s_chi:.3f}, ξ_end={out['ξ 期末（2026-06 または標本末、フィルタ）']:.3f}, llf={res.llf:.2f}"
              + (f", FY2026: {fyx.loc[2026, 'log_proxy']:.2f}={fyx.loc[2026, 'xi']:.2f}×{fyx.loc[2026, 'chi']:.2f}" if 2026 in fyx.index else ""))

UC_FULL = uc_store[("proxy_sys", "全期間 2016-04〜2026-06")]
UC_SUB = uc_store[("proxy_sys", "2023-04〜2026-06")]
_PL = pd.DataFrame(pl_rows)


def _get(sname, item):
    m = (_PL["ブロック"] == "2因子分解") & (_PL["系列"] == "システムプライス代理") & (_PL["標本"] == sname) & (_PL["項目"] == item)
    return float(_PL.loc[m, "値"].iloc[0])



SIG_FULL = _get("全期間 2016-04〜2026-06", "σ_ξ（年率）")
SIG_SUB = _get("2023-04〜2026-06", "σ_ξ（年率）")
SIG_PRE = _get("2016-04〜2021-03", "σ_ξ（年率）")
XI_NOW = _get("全期間 2016-04〜2026-06", "ξ 期末（2026-06 または標本末、フィルタ）")
XI_NOW_SUB = _get("2023-04〜2026-06", "ξ 期末（2026-06 または標本末、フィルタ）")

# σ_ξ のプロファイル尤度（他のパラメータは再最適化）。LR ≤ 3.84 を95%区間とする（境界0では保守的）
for sname in ("全期間 2016-04〜2026-06", "2023-04〜2026-06"):
    a, b = SAMPLES[sname]
    y = np.log(mon.loc[a:b, "proxy_sys"].to_numpy())
    _, res_u = fit_uc(y)
    prof = []
    for sg in np.round(np.arange(0.0, 0.801, 0.025), 3):
        _, rc = fit_uc(y, fix_level_var=(sg ** 2) / 12)
        prof.append((sg, max(rc.llf, -1e9)))
        add_pl("σ_ξ のプロファイル尤度", "システムプライス代理", sname, f"σ_ξ={sg:.3f} の LR 統計量", float(2 * (res_u.llf - rc.llf)))
    prof = np.array(prof)
    lr = np.maximum(2 * (res_u.llf - prof[:, 1]), 0.0)
    imin = int(np.argmin(lr))
    lo = 0.0 if lr[0] <= 3.84 else float(np.interp(3.84, lr[:imin + 1][::-1], prof[:imin + 1, 0][::-1]))
    hi = float(np.interp(3.84, lr[imin:], prof[imin:, 0])) if lr[-1] > 3.84 else np.nan
    add_pl("σ_ξ のプロファイル尤度", "システムプライス代理", sname, "LR(σ_ξ=0)（境界、片側の臨界値は2.71）", float(lr[0]))
    add_pl("σ_ξ のプロファイル尤度", "システムプライス代理", sname, "95%区間 下限（LR=3.84 の線形補間）", lo)
    add_pl("σ_ξ のプロファイル尤度", "システムプライス代理", sname, "95%区間 上限（LR=3.84 の線形補間）", hi)
    print(f"[A] σ_ξ のプロファイル尤度 {sname}: LR(σ=0)={lr[0]:.2f}、95%区間 ≈ [{lo:.3f}, {hi:.3f}]（LR≤3.84）")


# 恒久成分のドリフト（参考）: 対数代理 = ξ（ドリフト付きランダムウォーク）+ χ（AR(1)）。ドリフトは拡散初期値の状態として
# 推定され、平滑化した状態の分散が標準誤差を与える。DP は水準のマルチンゲール（対数のドリフト −σ²/2）を仮定している。
def fit_uc_drift(y):
    mod = sm.tsa.UnobservedComponents(y, level="random walk with drift", autoregressive=1)
    v = np.var(np.diff(y))
    best = None
    for s_lvl in (0.05, 0.3, 1.0):
        for s_ar in (0.3, 1.0):
            for phi in (0.3, 0.6, 0.9):
                try:
                    res = mod.fit(start_params=np.array([s_lvl * v, s_ar * v, phi]), disp=False, maxiter=3000)
                except Exception:
                    continue
                if np.isfinite(res.llf) and (best is None or res.llf > best.llf + 1e-9):
                    best = res
    return mod, best


for sname in ("全期間 2016-04〜2026-06", "2023-04〜2026-06"):
    a, b = SAMPLES[sname]
    y = np.log(mon.loc[a:b, "proxy_sys"].to_numpy())
    mod_d, res_d = fit_uc_drift(y)
    i_tr = mod_d.state_names.index("trend")
    dr, dr_se = 12 * float(res_d.smoothed_state[i_tr, -1]), 12 * float(np.sqrt(res_d.smoothed_state_cov[i_tr, i_tr, -1]))
    sg_d = float(np.sqrt(max(dict(zip(mod_d.param_names, res_d.params))["sigma2.level"], 0.0) * 12))
    add_pl("恒久成分のドリフト（参考）", "システムプライス代理", sname, "対数のドリフト（年率）", dr)
    add_pl("恒久成分のドリフト（参考）", "システムプライス代理", sname, "同 標準誤差（年率）", dr_se)
    add_pl("恒久成分のドリフト（参考）", "システムプライス代理", sname, "ドリフト付きモデルの σ_ξ（年率）", sg_d)
    print(f"[A] 恒久成分の対数のドリフト {sname}: {dr:+.3f}/年（SE {dr_se:.3f}）、このモデルの σ_ξ={sg_d:.3f}")


# 単位根・定常性・分散比（全期間、システムプライス代理の対数、月次）
def variance_ratio(x, q):
    """Lo & MacKinlay (1988) の重複分散比。z は均一分散、z* は不均一分散に頑健"""
    x = np.asarray(x, float)
    T = len(x) - 1
    dx = np.diff(x)
    mu = (x[-1] - x[0]) / T
    s2a = ((dx - mu) ** 2).sum() / (T - 1)
    m = q * (T - q + 1) * (1 - q / T)
    s2c = ((x[q:] - x[:-q] - q * mu) ** 2).sum() / m
    vr = s2c / s2a
    z = (vr - 1) / np.sqrt(2 * (2 * q - 1) * (q - 1) / (3 * q * T))
    e2 = (dx - mu) ** 2
    den = e2.sum() ** 2
    theta = 0.0
    for j in range(1, q):
        delta = T * (e2[j:] * e2[:-j]).sum() / den
        theta += (2 * (q - j) / q) ** 2 * delta
    zs = (vr - 1) / np.sqrt(theta / T)
    return vr, z, zs


y_full = np.log(mon["proxy_sys"].to_numpy())
adf = adfuller(y_full, regression="c", autolag="AIC")
kp = kpss(y_full, regression="c", nlags="auto")
add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", "ADF 統計量（定数、AIC）", float(adf[0]))
add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", "ADF p 値（帰無: 単位根）", float(adf[1]))
add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", "KPSS 統計量（定数）", float(kp[0]))
add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", "KPSS p 値（帰無: 定常、表の範囲で打ち切り）", float(kp[1]))
print(f"[A] ADF（定数・AIC）: 統計量 {adf[0]:.3f}, p={adf[1]:.3f} ／ KPSS: 統計量 {kp[0]:.3f}, p={kp[1]:.3f}")
for q in (3, 6, 12, 24, 36):
    vr, z, zs = variance_ratio(y_full, q)
    add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", f"分散比 VR({q})", float(vr))
    add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", f"VR({q}) の z（均一分散）", float(z))
    add_pl("検定", "システムプライス代理", "全期間 2016-04〜2026-06", f"VR({q}) の z*（不均一分散に頑健）", float(zs))
    print(f"    VR({q:2d}) = {vr:.3f}  z = {z:+.2f}  z* = {zs:+.2f}")
# 年度（FY2016〜25）の対数代理の AR(1)（参考、標本10）
fy_sys = hp[hp["fy"] <= 2025].groupby("fy")["p_system"].mean()
ly = np.log(fy_sys / fy_sys.loc[2023:2025].mean()).to_numpy()
ar_fy = sm.OLS(ly[1:], sm.add_constant(ly[:-1])).fit()
add_pl("検定", "システムプライス代理（年度平均）", "FY2016〜25（10年）", "AR(1) 係数", float(ar_fy.params[1]))
add_pl("検定", "システムプライス代理（年度平均）", "FY2016〜25（10年）", "対数差分の SD", float(np.diff(ly).std(ddof=1)))
print(f"[A] 年度 log 代理の AR(1)={ar_fy.params[1]:.3f}（n=10）, 対数差分SD={np.diff(ly).std(ddof=1):.3f}")

pd.DataFrame(pl_rows).to_csv(os.path.join(PROC, "real_option_price_level.csv"), index=False)


# =====================================================================================
# B. 参入閾値（年次の動的計画法）
# =====================================================================================
NX = 2001
XG = np.linspace(np.log(0.02), np.log(80.0), NX)
HX = XG[1] - XG[0]
TH_G = np.exp(XG)
TH_MIN = float(TH_G[0])
_EDGES = np.concatenate([[-np.inf], (XG[:-1] + XG[1:]) / 2, [np.inf]])
_P_CACHE = {}


def trans(sig, alpha=0.0):
    """対数 θ の格子上の1年遷移確率（α=0 では θ はマルチンゲール: x' ~ N(x − σ²/2, σ)。α>0 では E[θ']=(1+α)θ）。
    端は吸収して行和=1"""
    key = (round(float(sig), 6), round(float(alpha), 10))
    if key not in _P_CACHE:
        if len(_P_CACHE) > 10:
            _P_CACHE.clear()
        mu = XG - 0.5 * sig ** 2 if alpha == 0 else XG + np.log1p(alpha) - 0.5 * sig ** 2
        _P_CACHE[key] = np.diff(norm.cdf((_EDGES[None, :] - mu[:, None]) / sig), axis=1)
    return _P_CACHE[key]


def capex_path(g, H, sp=SP4):
    return np.maximum(sp["Ifloor"], sp["I0"] * (1 - g) ** np.arange(H + 1))


_SOLVE_CACHE = {}


def solve(sig, r, g, sp=SP4, H=80, alpha=0.0):
    """θ̄_t（t=0..H−1）、W_0(θ)、pv(θ)（t=0 に参入判断した場合の投資額控除前の20年 PV）。H 年目に権利が消える
    （H=80 は実質的に永久）。費用は暦年の列 F_s（t 年に判断した参入者の費用 PV は pvF[t]）"""
    key = (round(float(sig), 6), r, g, sp["key"], H, round(float(alpha), 10))
    if key in _SOLVE_CACHE:
        return _SOLVE_CACHE[key]
    disc = 1 / (1 + r)
    It = capex_path(g, H, sp)
    ga = grow_annuity(r, alpha)
    pf = pvF(sp, r)

    def pv_of(t):
        return sp["A"] * TH_G * ga - pf[t]

    P = trans(sig, alpha)
    W = np.maximum(pv_of(H) - It[H], 0.0)
    thr = np.full(H + 1, np.nan)
    thr[H] = theta_static(It[H], r, sp, H, alpha)
    for t in range(H - 1, -1, -1):
        npv = pv_of(t) - It[t]
        cont = disc * (P @ W)
        d = npv - cont
        ex = (d >= 0) & (npv > 0)
        W = np.where(ex, npv, cont)
        if ex.any():
            i = int(np.argmax(ex))
            assert ex[i:].all(), "行使域が上側集合でない"
            x = XG[i - 1] + (-d[i - 1]) / (d[i] - d[i - 1]) * HX if (i > 0 and d[i - 1] < 0) else XG[i]
            thr[t] = float(np.exp(x))
    out = (thr, W, pv_of(0), It)
    if len(_SOLVE_CACHE) > 400:
        _SOLVE_CACHE.clear()
    _SOLVE_CACHE[key] = out
    return out


def interp_log(vec, theta0):
    return float(np.interp(np.log(theta0), XG, vec))


def beta_cont(sig, r):
    rho = np.log(1 + r)
    return 0.5 + np.sqrt(0.25 + 2 * rho / sig ** 2)


# ---------- C3. 連続時間・永久寿命の競争産業均衡（D-P 第8章）: 反射壁モンテカルロ ----------
def reflected_pv_mc(sig, rho, dt=1 / 26, T=150, n=20000, seed=SEED):
    """P_t = Y_t / max_{s≤t} Y_s（P̄=1 で上側に反射、Y は対数正規マルチンゲール）。E∫e^{−ρt}P_t dt を返す。
    区間内の最大値はブラウン橋の分布から正確に生成し、積分は台形則"""
    rng = np.random.default_rng(seed)
    y = np.zeros(n)
    M = np.zeros(n)
    Pp = np.ones(n)
    pv = np.zeros(n)
    dprev = 1.0
    sq = sig * np.sqrt(dt)
    for k in range(int(T / dt)):
        yn = y - 0.5 * sig ** 2 * dt + sq * rng.standard_normal(n)
        u = rng.random(n)
        mstep = 0.5 * (y + yn + np.sqrt((yn - y) ** 2 - 2 * sig ** 2 * dt * np.log(u)))
        M = np.maximum(M, mstep)
        Pn = np.exp(yn - M)
        dn = np.exp(-rho * (k + 1) * dt)
        pv += 0.5 * (dprev * Pp + dn * Pn) * dt
        y, Pp, dprev = yn, Pn, dn
    return pv.mean(), pv.std(ddof=1) / np.sqrt(n)


def k_of_ratio(sp, ratio):
    """X が閾値に押さえられたときのフリート増分（万kW）: G(k0+K)/G(k0) = ratio を K について解く（ratio≥1 なら0）。
    G は収益の基準の π(K) の形（実績整合・モデル直値は戦略c の粗利 c(K)、旧基準は π_PF(K)）、k0=K_exo"""
    G = sp["G"]
    KG = sp.get("KG", K_GRID)          # G の K 格子（既定は完全予見の増分貪欲の格子。I の窓配分は0〜150）
    Ktot = np.interp(sp["g0"] * np.asarray(ratio, float), G[::-1], KG[::-1])
    return np.maximum(Ktot - sp["kexo"], 0.0)


# ---------- 競争均衡の参入閾値（年次・有限寿命）: 後ろ向き帰納とモンテカルロ ----------
_G_CACHE = {}


def growth_draws(sig, life=LIFE, n=50_000, alpha=0.0):
    """X の1年あたりの成長因子 (1+α)·exp(−σ²/2 + σε)（共通乱数。α=0 がマルチンゲール）"""
    key = (round(float(sig), 6), life, n, round(float(alpha), 10))
    if key not in _G_CACHE:
        z = np.random.default_rng(SEED + 4).standard_normal((n, life))
        _G_CACHE[key] = np.exp(-0.5 * sig ** 2 + sig * z)
        if alpha != 0:
            _G_CACHE[key] = _G_CACHE[key] * (1 + alpha)
    return _G_CACHE[key]


def entrant_npv(x0, sig, r, future_bnd, I, sp=SP4, life=LIFE, return_se=False, alpha=0.0, t_entry=0):
    """X=θ·G(K)/G(0) が x0 のときに t_entry 年に参入判断した者の NPV（円/kW）。X は年次の対数正規過程（α=0 で
    マルチンゲール）で動き、各年の参入判断で他社が参入して future_bnd[k] に押さえられる（不可逆、1年の建設ラグ:
    X_{k+1} = min(X_k, bnd_k)·exp(ε)）。費用は暦年 t_entry+k+1 の F_s。X で書くと π(K) の形によらない"""
    G = growth_draws(sig, life, alpha=alpha)
    Fs = sp["Fs"]
    X = np.full(G.shape[0], float(x0))
    pv = np.zeros(G.shape[0])
    for k in range(life):
        X = X * G[:, k]
        pv += (sp["A"] * X - Fs[t_entry + k + 1]) / (1 + r) ** (k + 1)
        X = np.minimum(X, future_bnd[k])
    v = pv - I
    if return_se:
        return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v)))
    return float(v.mean())


def _root(f, lo, hi):
    for _ in range(60):
        if f(hi) > 0:
            return brentq(f, lo, hi, xtol=1e-5)
        hi *= 2
    raise RuntimeError("参入者 NPV が正になる上端が見つからない")


_COMP_CACHE = {}


def competitive_boundary(sig, r, g, sp=SP4, life=LIFE, H=200, alpha=0.0):
    """競争均衡の参入閾値の経路 θ_c,t（t=0..H）。資本費が下限に達し、かつ容量収入が切り替わった後（t≥S_sw−1 なら
    CF はすべて切り替え後）は定常（一定の閾値）とし、そこから後ろ向きに「閾値で参入した者の、将来の参入で X が
    押さえられることを織り込んだ NPV = 0」を解く（自由参入で超過 NPV が消える条件）。
    探索の下端は期待経路で評価した静学の損益分岐の0.8倍（将来の参入は NPV を下げるだけなので、根はその上にある）"""
    key = (round(float(sig), 6), r, g, sp["key"], life, H, round(float(alpha), 10))
    if key in _COMP_CACHE:
        return _COMP_CACHE[key]
    It = capex_path(g, H, sp)
    tf_cap = int(np.argmax(It <= sp["Ifloor"] + 1e-6)) if g > 0 else 0
    tf = max(tf_cap, sp["S_sw"] - 1)
    ts = theta_static(It[tf], r, sp, tf, alpha, life)
    # 静学の損益分岐が0以下（容量収入だけで費用を賄える）なら、どの θ でも参入する（閾値を格子の下端に置く）
    th_inf = TH_MIN if ts <= 0 else _root(
        lambda x: entrant_npv(x, sig, r, np.full(life, x), It[tf], sp, life, alpha=alpha, t_entry=tf), 0.8 * ts, 3 * ts)
    bnd = np.full(H + life + 2, th_inf)
    for t in range(tf - 1, -1, -1):
        fut = bnd[t + 1:t + 1 + life].copy()
        ts_t = theta_static(It[t], r, sp, t, alpha, life)
        bnd[t] = TH_MIN if ts_t <= 0 else _root(
            lambda x: entrant_npv(x, sig, r, fut, It[t], sp, life, alpha=alpha, t_entry=t), 0.8 * ts_t, 3 * ts_t)
    _COMP_CACHE[key] = bnd
    return bnd


rows_thr = []
print("\n[B] 参入閾値（t=0 = FY2026、資本費6.8万円/kWh、容量収入1.25万円、収入の基準=実績整合 a=%.0f）" % SP4["A"])
print("    θ* = 静学の損益分岐、θ_c = 競争均衡の参入閾値（年次・20年寿命）、θ̄ = 単独企業（排他的な権利）の最適行使閾値")
SIG_LIST = [(0.005, "σ→0（確定的）"), (0.10, "格子"), (round(SIG_SUB, 3), "推定（2023-04〜）"), (0.15, "格子"),
            (0.20, "格子"), (round(SIG_FULL, 3), "推定（全期間）"), (0.30, "格子")]


def thr_row(sp, r, g, sig, src, thr, It, bnd):
    ts = theta_static(It[0], r, sp)
    return {"収入の基準": sp["basis"], "a(円/kW-年)": sp["A"], "仕様": sp["label"], "資本費(万円/kWh)": sp["capex"] / 1e4,
            "実効容量収入(円/kW-年)": sp["kpcap"],
            "実効容量収入FY2030〜(円/kW-年)": sp["kp_hi"] if sp["kp_hi"] is not None else sp["kpcap"],
            "補助率": sp["subsidy"], "K_exo(万kW)": sp["kexo"], "r": r, "g": g,
            "σ": sig, "σの出所": src, "θ*静学": ts,
            "θ_c競争均衡": bnd[0], "倍率θ_c/θ*": bnd[0] / ts,
            "θ̄単独企業": thr[0], "倍率θ̄/θ*": thr[0] / ts,
            "θ*（FY2030）": theta_static(It[4], r, sp, 4), "θ_c（FY2030）": bnd[4], "θ̄（FY2030）": thr[4],
            "θ*（FY2040）": theta_static(It[14], r, sp, 14), "θ_c（FY2040）": bnd[14], "θ̄（FY2040）": thr[14]}


for r in RS:
    for g in GS:
        for sig, src in SIG_LIST:
            thr, W, pv, It = solve(sig, r, g)
            bnd = competitive_boundary(sig, r, g)
            row = thr_row(SP4, r, g, sig, src, thr, It, bnd)
            ts = row["θ*静学"]
            if g == 0 and sig > 0.01:
                b = beta_cont(sig, r)
                row["閉形式β/(β−1)（連続判断）"] = b / (b - 1)
                row["年1回判断の補正後 β/(β−1)·exp(−0.5826σ)"] = b / (b - 1) * np.exp(-BGK * sig)
                row["θ̄倍率と補正後閉形式の差(%)"] = 100 * (thr[0] / ts / (b / (b - 1) * np.exp(-BGK * sig)) - 1)
            if sig < 0.01:
                row["使用者費用の閉形式θ̄（σ→0）"] = (SP4["I0"] * crf(r) * (r + g) / r + SP4["F"]) / SP4["A"]
            rows_thr.append(row)
dfT = pd.DataFrame(rows_thr)
print(dfT[dfT["r"] == 0.06][["g", "σ", "σの出所", "θ*静学", "θ_c競争均衡", "倍率θ_c/θ*", "θ̄単独企業", "倍率θ̄/θ*",
                            "θ*（FY2040）", "θ_c（FY2040）", "θ̄（FY2040）"]].round(3).to_string(index=False))
print(dfT[(dfT["r"] == 0.08)][["g", "σ", "θ*静学", "θ_c競争均衡", "倍率θ_c/θ*", "θ̄単独企業", "倍率θ̄/θ*"]].round(3).to_string(index=False))
chk = dfT[(dfT["g"] == 0) & dfT["σ"].isin(SIGMAS)][["r", "σ", "倍率θ̄/θ*", "閉形式β/(β−1)（連続判断）",
                                                     "年1回判断の補正後 β/(β−1)·exp(−0.5826σ)", "θ̄倍率と補正後閉形式の差(%)"]]
print("\n[C1] 単独企業の DP の倍率と閉形式（g=0）")
print(chk.round(3).to_string(index=False))
print("[C2] σ→0 の使用者費用（Jorgenson）: DP（σ=0.005）と閉形式")
print(dfT[dfT["σ"] == 0.005][["r", "g", "θ̄単独企業", "使用者費用の閉形式θ̄（σ→0）", "θ_c競争均衡"]].round(3).to_string(index=False))

# 他の収益の基準（モデル直値・旧0.81PF）の閾値（σ=0.10〜0.30、g=0・5%）。C5: 閾値の比は a の比の逆数に一致する
print("\n[C5] 収益の基準の換算: 閾値 × a は基準によらない（θ と a は積でしか入らない）")
for bname in ("モデル直値", "旧0.81PF"):
    spb = SPB[bname]
    for r in RS:
        for g in (0.0, 0.05):
            for sig in SIGMAS:
                thr, W, pv, It = solve(sig, r, g, spb)
                bnd = competitive_boundary(sig, r, g, spb)
                rows_thr.append(thr_row(spb, r, g, sig, "格子", thr, It, bnd))
                if r == 0.06 and sig in (0.10, 0.30):
                    thm, _, _, _ = solve(sig, r, g)
                    bm = competitive_boundary(sig, r, g)
                    print(f"  {bname} r={r:.0%} g={g:.0%} σ={sig:.2f}: θ_c={bnd[0]:.3f}（実績整合 {bm[0]:.3f}）、"
                          f"θ_c·a の比 {bnd[0] * spb['A'] / (bm[0] * SP4['A']):.5f}、θ̄·a の比 {thr[0] * spb['A'] / (thm[0] * SP4['A']):.5f}")

# 容量収入1.75万円（2030年度向け Net CONE 20,911円×κ0.836）を FY2026 から一定とした感応度（時変は H で扱う）
SP4_2030 = make_spec(kpcap=KP2030, label="4時間（容量収入1.75万円、FY2026〜一定）")
for sig in SIGMAS:
    for g in (0.0, 0.05):
        thr, W, pv, It = solve(sig, 0.06, g, SP4_2030)
        rows_thr.append(thr_row(SP4_2030, 0.06, g, sig, "格子", thr, It, competitive_boundary(sig, 0.06, g, SP4_2030)))

# ---------- C3 の実行 ----------
print("\n[C3] 連続時間・永久寿命の競争産業均衡（D-P 第8章）: 反射壁モンテカルロ（2万本、2週刻み、ブラウン橋で最大値を生成）")
c3 = {}
for sig in (0.15, 0.30):
    rho = np.log(1.06)
    m, se = reflected_pv_mc(sig, rho)
    b = beta_cont(sig, 0.06)
    theo = (b - 1) / (b * rho)
    c3[sig] = (m, se, theo, 1 / (rho * m), b / (b - 1))
    print(f"  σ={sig:.2f}: 反射壁つき収入の PV（P̄=1当たり）MC={m:.3f}（SE {se:.3f}）理論 (β−1)/(βρ)={theo:.3f}、反射なし 1/ρ={1/rho:.3f}"
          f" ⇒ 正しく計算した NPV=0 の P̄/(ρI)={1/(rho*m):.3f}（理論 β/(β−1)={b/(b-1):.3f}、静学なら1）")

# ---------- C4: 本研究の設定（年次・20年寿命）での競争均衡と、単独企業の閾値との関係 ----------
print("\n[C4] 本研究の設定（年次・20年寿命、g=0）: 全社が単独企業の閾値 θ̄ で参入する場合の参入者の NPV と、NPV=0 の競争閾値 θ_c")
c4 = {}
for r in RS:
    for sig in SIGMAS:
        thr0 = solve(sig, r, 0.0)[0][0]
        th_c = competitive_boundary(sig, r, 0.0)[0]
        npv_m, se_m = entrant_npv(thr0, sig, r, np.full(LIFE, thr0), SP4["I0"], return_se=True)
        npv_s_bar = (SP4["A"] * thr0 - SP4["F"]) * annuity(r) - SP4["I0"]
        npv_s_c = (SP4["A"] * th_c - SP4["F"]) * annuity(r) - SP4["I0"]
        c4[(sig, r)] = {"C4: θ̄で全社が参入する場合の参入者NPV(円/kW)": npv_m, "C4: 同SE": se_m,
                        "C4: θ̄での静学NPV(円/kW)": npv_s_bar, "C4: θ_cでの静学NPV(円/kW)": npv_s_c}
        print(f"  r={r:.0%} σ={sig:.2f}: θ̄={thr0:.3f} で参入者 NPV={npv_m:+,.0f}（SE {se_m:,.0f}、I の{npv_m/SP4['I0']:+.1%}）→ 競争で閾値は"
              f" θ_c={th_c:.3f}（θ̄比 {th_c/thr0-1:+.1%}）へ下がる。θ_c での静学 NPV={npv_s_c:+,.0f}（I の{npv_s_c/SP4['I0']:+.0%}）、正しい NPV=0")
# 寿命を延ばすと θ_c → θ̄（Leahy の命題の離散版）
print("  寿命の効果（r=6%、g=0）: 寿命 L 年の単独企業閾値 θ̄_L と競争閾値 θ_c,L")
for sig in (0.15, 0.30):
    for life in (20, 40, 100):
        r = 0.06
        P = trans(sig)
        pvL = (SP4["A"] * TH_G - SP4["F"]) * annuity(r, life)
        WL = np.maximum(pvL - SP4["I0"], 0.0)
        for _ in range(300):
            npv = pvL - SP4["I0"]
            cont = (P @ WL) / (1 + r)
            d = npv - cont
            ex = (d >= 0) & (npv > 0)
            WL = np.where(ex, npv, cont)
        i = int(np.argmax(ex))
        thL = float(np.exp(XG[i - 1] + (-d[i - 1]) / (d[i] - d[i - 1]) * HX))
        thcL = competitive_boundary(sig, r, 0.0, life=life)[0]
        tsL = (SP4["I0"] * crf(r, life) + SP4["F"]) / SP4["A"]
        c4[(sig, r, life)] = (tsL, thL, thcL)
        print(f"    σ={sig:.2f} L={life:3d}: θ*={tsL:.3f}, θ̄_L={thL:.3f}（{thL/tsL:.3f}倍）, θ_c,L={thcL:.3f}（{thcL/tsL:.3f}倍、θ̄_L比 {thcL/thL-1:+.1%}）")
for row in rows_thr:
    if row["収入の基準"] != MAIN_BASIS:
        continue
    if row["仕様"] == SP4["label"] and row["g"] == 0 and (row["σ"], row["r"]) in c4:
        row.update(c4[(row["σ"], row["r"])])
    if row["仕様"] == SP4["label"] and row["g"] == 0 and row["r"] == 0.06 and row["σ"] in c3:
        m, se, theo, mult_mc, mult_th = c3[row["σ"]]
        row["C3: 連続時間MCのP̄/(ρI)"] = mult_mc
        row["C3: 理論β/(β−1)"] = mult_th
    if row["仕様"] == SP4["label"] and row["g"] == 0 and row["r"] == 0.06 and (row["σ"], 0.06, 100) in c4:
        tsL, thL, thcL = c4[(row["σ"], 0.06, 100)]
        row["C4: 寿命100年のθ̄"] = thL
        row["C4: 寿命100年のθ_c"] = thcL
        tsL, thL, thcL = c4[(row["σ"], 0.06, 40)]
        row["C4: 寿命40年のθ̄"] = thL
        row["C4: 寿命40年のθ_c"] = thcL

# =====================================================================================
# D. 参入が開く確率と E[K]
# =====================================================================================
H_D = 2040 - FY0
YEARS = (2030, 2035, 2040)
RULES = ("競争均衡", "単独企業", "静学")


def first_passage(theta0, thr_seq, sig, alpha=0.0):
    """格子上の前進計算: t=1..len(thr_seq) の各年に θ_t ≥ thr_t となった確率の累積（吸収壁）"""
    P = trans(sig, alpha)
    dist = np.zeros(NX)
    x0 = np.log(theta0)
    j = int(np.searchsorted(XG, x0))
    w = (x0 - XG[j - 1]) / HX
    dist[j - 1], dist[j] = 1 - w, w
    cum, out = 0.0, []
    for th in thr_seq:
        dist = dist @ P
        hit = TH_G >= th
        cum += dist[hit].sum()
        dist[hit] = 0.0
        out.append(cum)
    return np.array(out)


def fleet_mc(theta0, sig, rules, sp=SP4, n=200_000, seed=SEED, alpha=0.0, kcap=None):
    """rules: {名前: 閾値の列（t=1..H）}。K_t = max_s≤t K(thr_s/θ_s)（θ_s ≥ thr_s のとき。不可逆）。
    K(·) は G(k0+K)/G(k0) = thr/θ の解（k_of_ratio）。kcap を与えると E[min(K, kcap)] も返す"""
    rng = np.random.default_rng(seed)
    H = len(next(iter(rules.values())))
    if alpha == 0:
        th = theta0 * np.exp(np.cumsum(-0.5 * sig ** 2 + sig * rng.standard_normal((n, H)), axis=1))
    else:
        th = theta0 * np.exp(np.cumsum(np.log1p(alpha) - 0.5 * sig ** 2 + sig * rng.standard_normal((n, H)), axis=1))
    out = {}
    for name, thr in rules.items():
        K = np.zeros(n)
        op = np.zeros(n, bool)
        res = []
        for t in range(H):
            x = th[:, t]
            hit = x >= thr[t]
            K = np.maximum(K, np.where(hit, k_of_ratio(sp, thr[t] / x), 0.0))
            op |= hit
            res.append((op.mean(), K.mean(), np.percentile(K, 95), np.percentile(K, 99),
                        np.minimum(K, kcap).mean() if kcap is not None else np.nan))
        out[name] = res
    return out


rows_D = []
TH0S = (("恒久成分の推定値（2026-06、全期間モデル）", XI_NOW), ("FY2026（4〜6月）の水準係数1.57が恒久と仮定", 1.57), ("θ=1（FY2023〜25 の水準）", 1.0))
D_MAIN3 = ("実績整合", "モデル直値", "旧0.81PF")
cum_for_fig = {}
for bname in BASES:
    spb = SPB[bname]
    th0s = TH0S if bname in D_MAIN3 else TH0S[:1]
    rs = RS if bname in D_MAIN3 else (0.06,)
    for r in rs:
        for g in (0.0, 0.05):
            for sig in SIGMAS:
                thr, W, pv, It = solve(sig, r, g, spb)
                rules = {"競争均衡": competitive_boundary(sig, r, g, spb)[1:H_D + 1], "単独企業": thr[1:H_D + 1],
                         "静学": np.array([theta_static(It[t], r, spb, t) for t in range(1, H_D + 1)])}
                for lab0, th0 in th0s:
                    fp = {k: first_passage(th0, v, sig) for k, v in rules.items()}
                    mc = fleet_mc(th0, sig, rules, spb)
                    if bname == MAIN_BASIS and lab0.startswith("恒久") and r == 0.06:
                        cum_for_fig[(sig, g)] = fp
                    for fy in YEARS:
                        t = fy - FY0 - 1
                        row = {"収入の基準": bname, "a(円/kW-年)": spb["A"], "出発点": lab0, "θ0": th0, "r": r, "g": g, "σ": sig,
                               "年度まで": fy}
                        for k in RULES:
                            row[f"P(開く)_{k}"] = fp[k][t]
                        for k in RULES:
                            row[f"P(開く)_{k}(MC検算)"] = mc[k][t][0]
                        for k in RULES:
                            row[f"E[K]_{k}(万kW)"] = mc[k][t][1]
                        for k in RULES:
                            row[f"K95%点_{k}(万kW)"] = mc[k][t][2]
                        for k in RULES:
                            row[f"K99%点_{k}(万kW)"] = mc[k][t][3]
                        row["θ_c（その年度）"] = rules["競争均衡"][t]
                        row["θ̄（その年度）"] = rules["単独企業"][t]
                        row["θ*（その年度）"] = rules["静学"][t]
                        rows_D.append(row)
dfD = pd.DataFrame(rows_D)
dfD.to_csv(os.path.join(PROC, "real_option_entry_prob.csv"), index=False)
_cols = ["g", "σ", "年度まで", "P(開く)_競争均衡", "P(開く)_単独企業", "P(開く)_静学", "P(開く)_競争均衡(MC検算)",
         "E[K]_競争均衡(万kW)", "E[K]_単独企業(万kW)", "E[K]_静学(万kW)", "K95%点_競争均衡(万kW)", "K99%点_競争均衡(万kW)", "K95%点_静学(万kW)"]
_m = (dfD["出発点"].str.startswith("恒久"))
print("\n[D] 参入が開く確率と E[K]（出発点=恒久成分の推定値 %.3f、r=6%%、実績整合）" % XI_NOW)
print(dfD[_m & (dfD["r"] == 0.06) & (dfD["収入の基準"] == MAIN_BASIS)][_cols].round(4).to_string(index=False))
print("  （r=6%、2040年度、収入の基準別）")
print(dfD[_m & (dfD["r"] == 0.06) & (dfD["年度まで"] == 2040)][["収入の基準"] + _cols].round(4).to_string(index=False))
print("  （出発点=恒久成分の推定値、r=8%、2040年度）")
print(dfD[_m & (dfD["r"] == 0.08) & (dfD["年度まで"] == 2040)][["収入の基準"] + _cols].round(4).to_string(index=False))
print("  （出発点1.57、r=6%、2040年度）")
print(dfD[(dfD["θ0"] == 1.57) & (dfD["r"] == 0.06) & (dfD["年度まで"] == 2040)][["収入の基準"] + _cols].round(4).to_string(index=False))

# =====================================================================================
# E. 排他的な接続枠の待機価値 W0（実績整合）
# =====================================================================================
rows_E = []
for r in RS:
    for g in GS:
        for sig in SIGMAS:
            for mat in (3, 5, 10, 80):
                thr, W, pv, It = solve(sig, r, g, H=mat)
                for lab0, th0 in (("θ=1", 1.0), ("恒久成分の推定値", XI_NOW), ("1.57", 1.57)):
                    w0 = interp_log(W, th0)
                    npv0 = interp_log(pv, th0) - It[0]
                    pex = first_passage(th0, thr[1:mat + 1], sig)[-1] if mat < 80 else first_passage(th0, thr[1:61], sig)[-1]
                    rows_E.append({"収入の基準": MAIN_BASIS, "r": r, "g": g, "σ": sig, "満期(年)": "永久（80年）" if mat == 80 else mat,
                                   "θ0": lab0, "θ0の値": th0,
                                   "静学NPV(円/kW)": npv0, "待機価値W0(円/kW)": w0, "W0/I0": w0 / SP4["I0"],
                                   "期限内に行使する確率": pex,
                                   "W0と等しい保証金10%の工事費負担金(円/kW)": w0 / 0.10,
                                   "W0と等しい保証金5%の工事費負担金(円/kW)": w0 / 0.05})
dfE = pd.DataFrame(rows_E)
dfE.to_csv(os.path.join(PROC, "real_option_waiting_value.csv"), index=False)
print("\n[E] 接続枠の待機価値 W0（円/kW、r=6%、θ0=恒久成分の推定値、実績整合）")
print(dfE[(dfE["r"] == 0.06) & (dfE["θ0"] == "恒久成分の推定値") & (dfE["g"].isin([0.0, 0.05]))]
      .pivot_table(index=["g", "σ"], columns="満期(年)", values="待機価値W0(円/kW)", aggfunc="first").round(0).to_string())
print(dfE[(dfE["r"] == 0.06) & (dfE["θ0"] == "恒久成分の推定値") & (dfE["g"].isin([0.0, 0.05]))]
      .pivot_table(index=["g", "σ"], columns="満期(年)", values="期限内に行使する確率", aggfunc="first").round(4).to_string())
print(dfE[(dfE["r"] == 0.06) & (dfE["θ0"] == "恒久成分の推定値") & (dfE["g"].isin([0.0, 0.05])) & (dfE["満期(年)"] == 5)]
      [["g", "σ", "待機価値W0(円/kW)", "W0と等しい保証金5%の工事費負担金(円/kW)", "W0と等しい保証金10%の工事費負担金(円/kW)"]]
      .round(0).to_string(index=False))

# =====================================================================================
# G. 感応度: θ の期待成長 α>0（WACC 6%、実績整合）
#    α=2%/年（名目の物価上昇程度）と、推定した UC モデルどおり対数のドリフトを0 とした場合（水準では α=exp(σ²/2)−1）
# =====================================================================================
rows_G = []
ALPHAS = (("α=2%/年", lambda s: 0.02), ("対数のドリフト0（α=exp(σ²/2)−1）", lambda s: float(np.expm1(0.5 * s * s))))
print("\n[G] θ の期待成長 α>0 の感応度（r=6%、出発点=恒久成分の推定値、2040年度まで、実績整合）")
for alab, afn in ALPHAS:
    for g in (0.0, 0.05):
        for sig in SIGMAS:
            al = afn(sig)
            thr, W, pv, It = solve(sig, 0.06, g, alpha=al)
            bnd = competitive_boundary(sig, 0.06, g, alpha=al)
            rules = {"競争均衡": bnd[1:H_D + 1], "単独企業": thr[1:H_D + 1],
                     "静学（期待経路）": np.array([theta_static(It[t], 0.06, SP4, t, al) for t in range(1, H_D + 1)]),
                     "静学（一定価格）": np.array([theta_static(It[t], 0.06, SP4, t) for t in range(1, H_D + 1)])}
            for lab0, th0 in (("恒久成分の推定値（2026-06、全期間モデル）", XI_NOW), ("FY2026（4〜6月）の水準係数1.57が恒久と仮定", 1.57)):
                fp = {k: first_passage(th0, v, sig, alpha=al) for k, v in rules.items()}
                mc = fleet_mc(th0, sig, {"競争均衡": rules["競争均衡"]}, alpha=al)
                row = {"収入の基準": MAIN_BASIS, "α の置き方": alab, "α": al, "r": 0.06, "g": g, "σ": sig, "出発点": lab0, "θ0": th0,
                       "θ*（一定価格、FY2026）": theta_static(It[0], 0.06), "θ*_α（期待経路、FY2026）": theta_static_alpha(It[0], 0.06, SP4, al),
                       "θ_c（FY2026）": bnd[0], "θ̄（FY2026）": thr[0], "θ_c/θ*_α": bnd[0] / theta_static_alpha(It[0], 0.06, SP4, al),
                       "θ_c（FY2040）": bnd[14], "θ*_α（FY2040）": theta_static(It[14], 0.06, SP4, 14, al)}
                for fy in YEARS:
                    t = fy - FY0 - 1
                    for k in rules:
                        row[f"P(開く)_{k}_{fy}"] = fp[k][t]
                row["E[K]_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][1]
                row["K99%点_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][3]
                rows_G.append(row)
                if th0 == XI_NOW:
                    print(f"  {alab} g={g:.0%} σ={sig:.2f}（α={al:.3%}）: θ*={row['θ*（一定価格、FY2026）']:.2f}, θ*_α={row['θ*_α（期待経路、FY2026）']:.2f},"
                          f" θ_c={bnd[0]:.2f}, θ̄={thr[0]:.2f}; P(2030) 競争均衡 {fp['競争均衡'][3]:.2%}; P(2040) 競争均衡 {fp['競争均衡'][-1]:.2%} 単独 {fp['単独企業'][-1]:.2%}"
                          f" 静学(期待経路) {fp['静学（期待経路）'][-1]:.2%} 静学(一定価格) {fp['静学（一定価格）'][-1]:.2%}; E[K]2040 {row['E[K]_競争均衡_2040(万kW)']:.2f}万kW"
                          f"（99%点 {row['K99%点_競争均衡_2040(万kW)']:.1f}）")
dfG = pd.DataFrame(rows_G)
dfG.to_csv(os.path.join(PROC, "real_option_drift_sensitivity.csv"), index=False)
print("  （出発点1.57、2040年度）")
print(dfG[dfG["θ0"] == 1.57][["α の置き方", "g", "σ", "θ_c（FY2026）", "P(開く)_競争均衡_2030", "P(開く)_競争均衡_2040",
                              "P(開く)_静学（期待経路）_2040", "E[K]_競争均衡_2040(万kW)"]].round(4).to_string(index=False))

# =====================================================================================
# F. 参考: 2時間仕様（Helios 型）
#    実績整合: 実績価格（FY2023〜25）の上で戦略c（36 と同じ規則）を2h・4h で直接計算した粗利を a とする。
#    旧基準: 26 を部品として読み込み、θ=1 の FY2023〜25 パスで 2h の完全予見粗利を求めて0.81 を掛ける。
# =====================================================================================
_hd = hp.dropna(subset=["p_hokkaido"]).assign(day=lambda d: d["ts"].dt.normalize(), hour=lambda d: d["ts"].dt.hour)
_PA = _hd.pivot(index="day", columns="hour", values="p_hokkaido")
_PA = _PA[_PA.count(axis=1) == 24]
_days = _PA.index
_PAv = _PA.to_numpy(float)
_wk = np.asarray(_days.dayofweek >= 5)
_fyd = np.asarray(_days.year - (_days.month < 4).astype(int))
_clim = np.full_like(_PAv, np.nan)
for i in range(len(_days)):
    _h = [j for j in range(max(0, i - 29), i) if _wk[j] == _wk[i]]
    if len(_h) >= 5:
        _clim[i] = _PAv[_h].mean(axis=0)


def _tie_w(sig, k):
    """信号の下位 k 時間の重み。境界の同値は均等に配分する（36 と同じ）"""
    thr = np.sort(sig)[k - 1]
    w = (sig < thr).astype(float)
    tied = sig == thr
    w[tied] = (k - w.sum()) / tied.sum()
    return w


def strat_c_actual(hours, eta=0.85):
    """実績価格の上の戦略c の実現粗利（年度別、円/kW-年）"""
    m = np.full(len(_days), np.nan)
    for i in range(len(_days)):
        if not np.isnan(_clim[i]).any():
            m[i] = eta * (_tie_w(-_clim[i], hours) @ _PAv[i]) - _tie_w(_clim[i], hours) @ _PAv[i]
    return pd.Series(m).groupby(_fyd).sum()


c4_act = strat_c_actual(4)
c2_act = strat_c_actual(2)
A4_ACT = float(c4_act.loc[[2023, 2024, 2025]].mean())
A2_ACT = float(c2_act.loc[[2023, 2024, 2025]].mean())
print(f"\n[F] 実績価格の戦略c（FY2023〜25 平均）: 4h {A4_ACT:,.1f}（λ·c(0)={LAM * C0:,.1f} と照合）、2h {A2_ACT:,.1f}円/kW-年（4h比 {A2_ACT/A4_ACT:.3f}）")
assert abs(A4_ACT - LAM * C0) < 1.0

ns = {"__file__": os.path.join(HERE, "26_price_process_v2.py"), "__name__": "pp_v2"}
_to_csv = pd.DataFrame.to_csv
pd.DataFrame.to_csv = lambda *a, **k: None
try:
    with contextlib.redirect_stdout(io.StringIO()):
        exec(open(os.path.join(HERE, "26_price_process_v2.py"), encoding="utf-8").read(), ns)
finally:
    pd.DataFrame.to_csv = _to_csv
est = ns["est"].copy().sort_values("ts").reset_index(drop=True)
predict_A, ETA = ns["predict_A"], ns["ETA"]
est["date"] = est["ts"].dt.normalize()
piv = est.pivot_table(index="date", columns="hour", values="net").dropna()
tmp = est.loc[est["date"].isin(piv.index)].sort_values("ts").copy()
nday = len(piv.index)
fyd = piv.index.year - (piv.index.month < 4).astype(int)


def pi_pf_hours(hours, theta=1.0):
    pr = predict_A(tmp.assign(net=piv.to_numpy().reshape(-1)), net_col="net", theta=theta).reshape(nday, 24)
    srt = np.sort(pr, axis=1)
    m = np.maximum(0.0, (srt[:, -hours:].sum(1) * ETA - srt[:, :hours].sum(1)) * 1000)
    return float(pd.Series(m, index=piv.index).groupby(fyd).sum().mean() / 1000)


pi4, pi2 = pi_pf_hours(4), pi_pf_hours(2)
pi4_157 = pi_pf_hours(4, 1.57)
print(f"    完全予見粗利（モデル、θ=1、FY2023〜25パス）: 4h {pi4:,.0f}（pi_k_curve_v3.csv の {PI_PF0:,.0f} と照合）、2h {pi2:,.0f}円/kW-年（4h比 {pi2/pi4:.3f}）")
print(f"    θ への比例: π_PF(4h; θ=1.57)/π_PF(4h; θ=1) = {pi4_157/pi4:.4f}（1.57 に対し）")
rows_F = [{"収入の基準": "検算", "区分": "検算", "項目": "π_PF 4h θ=1（再計算）", "値": pi4},
          {"収入の基準": "検算", "区分": "検算", "項目": "π_PF 4h θ=1（pi_k_curve_v3.csv）", "値": PI_PF0},
          {"収入の基準": "検算", "区分": "検算", "項目": "π_PF 4h θ=1.57 ÷ θ=1", "値": pi4_157 / pi4},
          {"収入の基準": "検算", "区分": "検算", "項目": "戦略c 4h 実績 FY2023〜25（λ·c(0) と一致）", "値": A4_ACT},
          {"収入の基準": "旧0.81PF", "区分": "2時間", "項目": "π_PF 2h θ=1", "値": pi2},
          {"収入の基準": "実績整合", "区分": "2時間", "項目": "戦略c 2h 実績 FY2023〜25", "値": A2_ACT}]
for y in (2022, 2023, 2024, 2025):
    rows_F.append({"収入の基準": "実績整合", "区分": "年度別", "項目": f"戦略c 2h 実績 FY{y}", "値": float(c2_act.loc[y])})
    rows_F.append({"収入の基準": "実績整合", "区分": "年度別", "項目": f"戦略c 4h 実績 FY{y}", "値": float(c4_act.loc[y])})
F_A = {"実績整合": {4: A4_ACT, 2: A2_ACT}, "旧0.81PF": {4: CAPTURE * PI_PF0, 2: CAPTURE * pi2}}
for bname, AA in F_A.items():
    for cx in (6.8e4, 4.0e4):
        for hours, kp in ((2, 0.0), (4, KPCAP), (4, 0.0)):
            if hours == 2:
                lab_sp = "2時間（参考）"
            elif kp == 0:
                lab_sp = f"4時間（容量収入0、資本費{cx/1e4:.1f}万円/kWh、参考）"
            else:
                lab_sp = SP4["label"] if cx == CAPEX0 else f"4時間（資本費{cx/1e4:.1f}万円/kWh）"
            sp = make_spec(hours=hours, capex=cx, basis=bname, kpcap=kp, A=AA[hours], label=lab_sp)
            ts = theta_static(sp["I0"], 0.06, sp)
            lab = f"{hours}h・資本費{cx/1e4:.1f}万円/kWh・容量収入{kp:,.0f}"
            base = {"収入の基準": bname}
            rows_F.append({**base, "区分": "粗収益a", "項目": f"{lab}: a（θ=1、円/kW-年）", "値": sp["A"]})
            rows_F.append({**base, "区分": "静学閾値", "項目": f"{lab}: θ*（WACC6%）", "値": ts})
            rows_F.append({**base, "区分": "静学閾値", "項目": f"{lab}: c_req(円/kW-年)", "値": sp["I0"] * crf(0.06) + om_cost(hours) + WHEEL_FIX})
            for sig in (0.10, 0.30):
                thr, W, pv, It = solve(sig, 0.06, 0.0, sp)
                bnd = competitive_boundary(sig, 0.06, 0.0, sp)
                rows_F.append({**base, "区分": "動学閾値", "項目": f"{lab}: θ_c 競争均衡（σ={sig:.2f}, g=0）", "値": bnd[0]})
                rows_F.append({**base, "区分": "動学閾値", "項目": f"{lab}: θ̄ 単独企業（σ={sig:.2f}, g=0）", "値": thr[0]})
                if hours == 2 or cx != CAPEX0 or kp == 0:      # 4h・6.8万円・容量収入1.25万円は B の格子に既にある
                    rows_thr.append(thr_row(sp, 0.06, 0.0, sig, "格子", thr, It, bnd))
            for lab0, th0 in (("θ=1", 1.0), ("恒久成分の推定値", XI_NOW), ("1.57", 1.57)):
                npv = (sp["A"] * th0 - sp["F"]) * annuity(0.06) - sp["I0"]
                rows_F.append({**base, "区分": "静学NPV", "項目": f"{lab}: 静学NPV θ0={lab0}（円/kW）", "値": npv})
                rows_F.append({**base, "区分": "スポット実現収益", "項目": f"{lab}: a·θ − 充電従量 θ0={lab0}（円/kW-年）",
                               "値": sp["A"] * th0 - hours * 365 * WHEEL_KWH})
                for TR in (3, 5, 10):
                    need = max(0.0, -npv) / annuity(0.06, TR)
                    rows_F.append({**base, "区分": "回収に必要な追加収入", "項目": f"{lab}: θ0={lab0}、{TR}年間の一時収入（円/kW-年）", "値": need})
                # スポット以外の追加収入 R（円/kW-年）が何年続けば静学 NPV の不足を埋めるか（annuity(T)=不足/R を T について解く）
                for R in (10_000, 20_000, 30_000, 40_000):
                    q = 0.06 * max(0.0, -npv) / R
                    yrs_need = -np.log(1 - q) / np.log(1.06) if q < 1 else np.inf
                    rows_F.append({**base, "区分": "回収に必要な年数", "項目": f"{lab}: θ0={lab0}、追加収入{R:,}円/kW-年が続く必要年数", "値": yrs_need})
dfF = pd.DataFrame(rows_F)
dfF.to_csv(os.path.join(PROC, "real_option_short_duration.csv"), index=False)
print(dfF[dfF["区分"].isin(["粗収益a", "静学閾値", "動学閾値"]) | dfF["項目"].str.contains("恒久成分")].round(3).to_string(index=False))

# =====================================================================================
# H. 感応度（v3 で新設）: 容量収入の時変・補助・K_exo（実績整合が主。旧基準の行は監査の検算の再現）
# =====================================================================================
S_CAP = 40e8 / (50_000 * 4 * CAPEX0)               # 1/2 補助の上限40億円が5万kW・4h で効くときの実効補助率（0.294）
SII_HKD = 131.6e8 + 49.0e8                          # SII の北海道の交付決定額（2024・2025年度、180.6億円。9.2(c)）
H_CASES = [
    ("容量収入", "1.75万円（FY2030〜。FY2027〜29 は1.25万円）", dict(kp_hi=KP2030), True),
    ("容量収入", "2.5万円（FY2030〜。FY2027〜29 は1.25万円。g=0 のみ）", dict(kp_hi=KP25), True),
    ("容量収入", "1.75万円（FY2026〜一定）", dict(kpcap=KP2030), True),
    ("容量収入", "旧0.81PF・1.75万円（FY2030〜）［監査の再現］", dict(basis="旧0.81PF", kp_hi=KP2030), False),
    ("補助", "1/2（上限なし）", dict(subsidy=0.5), True),
    ("補助", "1/3（上限なし）", dict(subsidy=1 / 3), True),
    ("補助", f"1/2・上限40億円（5万kW、実効{S_CAP:.1%}）", dict(subsidy=S_CAP), True),
    ("補助", "1/2（上限なし）・容量収入1.75万円（FY2030〜）", dict(subsidy=0.5, kp_hi=KP2030), False),
    ("補助", "旧0.81PF・1/2（上限なし）［監査の再現］", dict(basis="旧0.81PF", subsidy=0.5), False),
    ("K_exo", "20万kW（接続済み）", dict(kexo=20.0), False),
    ("K_exo", "76.8万kW（接続済み＋LTDA 北海道 第3回の別解）", dict(kexo=76.8), False),
    ("K_exo", "87.4万kW（接続済み＋LTDA 北海道67.42万kW、主）", dict(kexo=87.4), False),
    ("K_exo", "旧0.81PF・20万kW", dict(basis="旧0.81PF", kexo=20.0), False),
    ("K_exo", "旧0.81PF・87.4万kW", dict(basis="旧0.81PF", kexo=87.4), False),
]
rows_H = []
print("\n[H] 感応度: 容量収入の時変・補助・K_exo（出発点=恒久成分の推定値 %.3f）" % XI_NOW)
for cat, clab, kw, with8 in H_CASES:
    sp = make_spec(label=f"4時間（{cat}: {clab}）", **kw)
    kcap = SII_HKD / (sp["subsidy"] * 4 * CAPEX0) / 1e4 if sp["subsidy"] > 0 else None
    for r in (RS if with8 else (0.06,)):
        # 2.5万円・資本費低下では静学の損益分岐が0以下（容量収入だけで費用を賄う）になり、容量価格を K によらず一定と
        # 置く本モデルでは参入が際限なく続くので、g=0 だけを計算する（容量価格の K 依存は 28・9.4 の表9.3 で扱う）
        for g in ((0.0,) if sp["kp_hi"] == KP25 else (0.0, 0.05)):
            for sig in SIGMAS:
                thr, W, pv, It = solve(sig, r, g, sp)
                bnd = competitive_boundary(sig, r, g, sp)
                rules = {"競争均衡": bnd[1:H_D + 1], "単独企業": thr[1:H_D + 1],
                         "静学": np.array([theta_static(It[t], r, sp, t) for t in range(1, H_D + 1)])}
                for lab0, th0 in ((("恒久成分の推定値（2026-06、全期間モデル）", XI_NOW), ("FY2026（4〜6月）の水準係数1.57が恒久と仮定", 1.57))
                                  if r == 0.06 else (("恒久成分の推定値（2026-06、全期間モデル）", XI_NOW),)):
                    fp = {k: first_passage(th0, v, sig) for k, v in rules.items()}
                    mc = fleet_mc(th0, sig, {"競争均衡": rules["競争均衡"], "静学": rules["静学"]}, sp, kcap=kcap)
                    row = {"区分": cat, "ケース": clab, "収入の基準": sp["basis"], "a(円/kW-年)": sp["A"],
                           "F（FY2027〜29）": sp["Fs"][1], "F（FY2030〜）": sp["Fs"][S_SW], "補助率": sp["subsidy"],
                           "K_exo(万kW)": sp["kexo"], "r": r, "g": g, "σ": sig, "出発点": lab0, "θ0": th0,
                           "θ*（FY2026）": theta_static(It[0], r, sp, 0), "θ*（FY2030）": theta_static(It[4], r, sp, 4),
                           "θ_c（FY2026）": bnd[0], "θ_c（FY2030）": bnd[4], "θ_c（FY2040）": bnd[14],
                           "θ̄（FY2026）": thr[0], "θ̄（FY2030）": thr[4]}
                    for fy in YEARS:
                        t = fy - FY0 - 1
                        for k in RULES:
                            row[f"P(開く)_{k}_{fy}"] = fp[k][t]
                    row["E[K]_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][1]
                    row["K95%点_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][2]
                    row["K99%点_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][3]
                    row["E[K]_静学_2040(万kW)"] = mc["静学"][H_D - 1][1]
                    if kcap is not None:
                        row["補助予算で賄える容量(万kW)"] = kcap
                        row["E[min(K,予算容量)]_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][4]
                        row["E[min(K,予算容量)]_静学_2040(万kW)"] = mc["静学"][H_D - 1][4]
                    rows_H.append(row)
    sub = [x for x in rows_H if x["ケース"] == clab and x["θ0"] == XI_NOW and x["r"] == 0.06]
    for g in sorted({x["g"] for x in sub}):
        s2 = [x for x in sub if x["g"] == g]
        p40 = ", ".join(f"{x['P(開く)_競争均衡_2040']:.2%}" for x in s2)
        print(f"  [{cat}] {clab} g={g:.0%}（r=6%）: θ*={s2[0]['θ*（FY2026）']:.2f}（FY2030 {s2[0]['θ*（FY2030）']:.2f}）、"
              f"θ_c(FY2026) {min(x['θ_c（FY2026）'] for x in s2):.2f}〜{max(x['θ_c（FY2026）'] for x in s2):.2f}、"
              f"θ_c(FY2030) {min(x['θ_c（FY2030）'] for x in s2):.2f}〜{max(x['θ_c（FY2030）'] for x in s2):.2f}、"
              f"P2030 競争均衡 最大 {max(x['P(開く)_競争均衡_2030'] for x in s2):.2%}、"
              f"P2040 競争均衡（σ=0.10〜0.30）{p40}、"
              f"静学 最大 {max(x['P(開く)_静学_2040'] for x in s2):.2%}、E[K]2040 最大 {max(x['E[K]_競争均衡_2040(万kW)'] for x in s2):.2f}万kW"
              f"（99%点 {max(x['K99%点_競争均衡_2040(万kW)'] for x in s2):.1f}）")
dfH = pd.DataFrame(rows_H)
dfH.to_csv(os.path.join(PROC, "real_option_sensitivity_v3.csv"), index=False)

# =====================================================================================
# I. 感応度（D3、検証で追加）: フリート配分を「戦略c の窓に従う配分」にした c(K) での E[K]・分位点
#    閾値と確率は X=θ·G(K)/G(0) で書くので G の形によらない（D と同じ値）。変わるのは K への換算だけ。
#    窓配分の c(K) は pi_k_curve_v3.csv の「戦略cの窓」（K=0〜150、1万kW 刻み。c(0) は主と同じ 7,602.4）。
# =====================================================================================
_cw = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
_cw = _cw[(_cw["価格モデル"] == "仕様A（26、水準係数付き）") & (_cw["シナリオ"] == "現状") & (_cw["θ"] == 1.0)
          & (_cw["フリート配分"] == "戦略cの窓") & (_cw["刻み(万kW)"] == "1.0")].sort_values("K(万kW)")
assert _cw["K(万kW)"].is_unique and abs(float(_cw["c"].iloc[0]) - C0) < 1e-6
KG_WIN = _cw["K(万kW)"].to_numpy(float)
G_WIN = np.minimum.accumulate(_cw["c"].to_numpy(float))
rows_I = []
print("\n[I] フリート配分の感応度（D3）: 完全予見の増分貪欲（主）と戦略c の窓に従う配分の E[K]2040（出発点 %.3f、r=6%%、実績整合）" % XI_NOW)
for clab, kw in (("容量収入1.25万円（主）", {}), ("容量収入1.75万円（FY2030〜）", dict(kp_hi=KP2030))):
    sp_m = make_spec(label=f"4時間（{clab}）", **kw)
    sp_w = make_spec(label=f"4時間（{clab}・窓配分）", **kw)
    sp_w["G"], sp_w["KG"], sp_w["g0"] = G_WIN, KG_WIN, float(G_WIN[0])
    for g in (0.0, 0.05):
        for sig in SIGMAS:
            thr, W, pv, It = solve(sig, 0.06, g, sp_m)
            bnd = competitive_boundary(sig, 0.06, g, sp_m)
            rules = {"競争均衡": bnd[1:H_D + 1], "静学": np.array([theta_static(It[t], 0.06, sp_m, t) for t in range(1, H_D + 1)])}
            fp = first_passage(XI_NOW, rules["競争均衡"], sig)
            for alloc, spx in (("完全予見の増分貪欲（主）", sp_m), ("戦略cの窓", sp_w)):
                mc = fleet_mc(XI_NOW, sig, rules, spx)
                row = {"ケース": clab, "フリート配分": alloc, "収入の基準": MAIN_BASIS, "r": 0.06, "g": g, "σ": sig, "θ0": XI_NOW,
                       "P(開く)_競争均衡_2040": fp[-1], "P(開く)_競争均衡_2040(MC検算)": mc["競争均衡"][H_D - 1][0]}
                for fy in YEARS:
                    t = fy - FY0 - 1
                    row[f"E[K]_競争均衡_{fy}(万kW)"] = mc["競争均衡"][t][1]
                row["K95%点_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][2]
                row["K99%点_競争均衡_2040(万kW)"] = mc["競争均衡"][H_D - 1][3]
                row["E[K]_静学_2040(万kW)"] = mc["静学"][H_D - 1][1]
                row["K99%点_静学_2040(万kW)"] = mc["静学"][H_D - 1][3]
                rows_I.append(row)
dfI = pd.DataFrame(rows_I)
dfI.to_csv(os.path.join(PROC, "real_option_fleet_alloc_v3.csv"), index=False)
print(dfI.pivot_table(index=["ケース", "g", "σ"], columns="フリート配分",
                      values=["E[K]_競争均衡_2040(万kW)", "K99%点_競争均衡_2040(万kW)", "E[K]_静学_2040(万kW)"], sort=False).round(2).to_string())

dfT = pd.DataFrame(rows_thr)
dfT.to_csv(os.path.join(PROC, "real_option_threshold.csv"), index=False)

# =====================================================================================
# 図: (a) 価格水準の代理と恒久成分（上段）、(b) 参入閾値と σ、(c) 参入が開く累積確率（実績整合）（下段の左右）
#     Word では本文幅15.5cm（6.1インチ）で載せるので、その大きさで描き、図中の文字は8.5〜9.5pt にする
# =====================================================================================
FIG_W = 6.1
FS_TICK, FS_LAB, FS_TTL, FS_LEG, FS_ANN = 8.5, 9.0, 9.5, 8.5, 8.5
C_BLUE, C_ORANGE = "#2a78d6", "#eb6834"
C_REF, C_GRID, C_LIGHT = "#8a8986", "#e4e3df", "#b9b8b3"
fig, axd = plt.subplot_mosaic([["a", "a"], ["b", "c"]], figsize=(FIG_W, 5.9), layout="constrained",
                              gridspec_kw={"height_ratios": [1.0, 1.15]})
fig.get_layout_engine().set(h_pad=0.04, w_pad=0.04, hspace=0.05, wspace=0.05)
axes = [axd["a"], axd["b"], axd["c"]]


def style(ax):
    for sp_ in ("top", "right"):
        ax.spines[sp_].set_visible(False)
    for sp_ in ("left", "bottom"):
        ax.spines[sp_].set_color(C_LIGHT)
    ax.tick_params(colors=GRAY, labelsize=FS_TICK, length=2.5, pad=2)
    ax.grid(axis="y", color=C_GRID, lw=0.6)
    ax.set_axisbelow(True)


_base6 = dfT[(dfT["収入の基準"] == MAIN_BASIS) & (dfT["仕様"] == SP4["label"]) & (dfT["資本費(万円/kWh)"] == CAPEX0 / 1e4)
             & (dfT["実効容量収入(円/kW-年)"] == KPCAP) & (dfT["補助率"] == 0) & (dfT["K_exo(万kW)"] == 0)
             & (dfT["r"] == 0.06) & (dfT["g"] == 0)].set_index("σ")
assert _base6.index.is_unique
# (a)
ax = axes[0]
style(ax)
ax.plot(mon.index, mon["proxy_sys"], color=C_LIGHT, lw=0.9, label="価格水準の月次の代理")
ax.plot(UC_FULL.index, np.exp(UC_FULL["xi"]), color=C_BLUE, lw=1.5, label=f"恒久成分 $\\xi$（全期間、$\\sigma_\\xi$={SIG_FULL:.2f}）")
ax.plot(UC_SUB.index, np.exp(UC_SUB["xi"]), color=C_ORANGE, lw=1.5, ls="--", label=f"恒久成分 $\\xi$（2023年4月以降、$\\sigma_\\xi$={SIG_SUB:.2f}）")
ax.set_yscale("log")
ax.set_yticks([0.4, 0.6, 1, 1.5, 2, 3, 4, 6])
ax.set_yticklabels(["0.4", "0.6", "1", "1.5", "2", "3", "4", "6"])
ax.yaxis.set_minor_formatter(plt.NullFormatter())
ax.axhline(TH_STAR6, color=C_REF, lw=0.9, ls="--")
ax.text(mon.index[2], TH_STAR6 * 0.95, f"静学の損益分岐 $\\theta^*$={TH_STAR6:.2f}", fontsize=FS_ANN, color=GRAY, va="top")
_c_lo, _c_hi = _base6.loc[0.10, "θ_c競争均衡"], _base6.loc[0.30, "θ_c競争均衡"]
_m_lo, _m_hi = _base6.loc[0.10, "θ̄単独企業"], _base6.loc[0.30, "θ̄単独企業"]
ax.axhspan(_c_lo, _m_hi, color=C_BLUE, alpha=0.07, lw=0)   # θ_c(σ=0.10) から θ̄(σ=0.30) まで
ax.text(mon.index[2], _c_lo * 1.04, f"待機を考慮した参入閾値\n（$\\sigma$=0.10〜0.30、$g_I$=0）\n$\\theta_c$ {_c_lo:.1f}〜{_c_hi:.1f}、$\\bar\\theta$ {_m_lo:.1f}〜{_m_hi:.1f}",
        fontsize=FS_ANN, color=GRAY, va="bottom")
ax.set_ylim(0.25, 9.0)
ax.set_title("(a) 価格水準の代理と恒久成分（対数目盛、FY2023〜25=1）", fontsize=FS_TTL, loc="left", color="#222222", pad=4)
ax.set_ylabel("価格水準（FY2023〜25=1）", fontsize=FS_LAB, color=GRAY)
ax.legend(fontsize=FS_LEG, frameon=False, loc="lower right", handlelength=2.0, borderaxespad=0.2, labelspacing=0.3)
ax.text(pd.Timestamp("2021-03-01"), float(mon.loc["2021-01-01", "proxy_sys"]) * 0.97, "← 2021年1月の高騰（一時成分）",
        fontsize=FS_ANN, color=GRAY, va="center")

# (b)
ax = axes[1]
style(ax)
sig_fine = np.round(np.arange(0.02, 0.351, 0.01), 3)
sig_coarse = [0.005, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
gcol = {0.0: C_BLUE, 0.05: C_ORANGE}
for g in (0.0, 0.05):
    ys = [solve(s, 0.06, g)[0][0] for s in sig_fine]
    yc = [competitive_boundary(s, 0.06, g)[0] for s in sig_coarse]
    ax.plot(sig_fine, ys, color=gcol[g], lw=1.5, ls="--", label=f"単独企業 $\\bar\\theta$（$g_I$={g:.0%}）")
    ax.plot(sig_coarse, yc, color=gcol[g], lw=1.5, marker="o", ms=3.2, mec="white", mew=0.6, label=f"競争均衡 $\\theta_c$（$g_I$={g:.0%}）")
ax.axhline(TH_STAR6, color=C_REF, lw=0.9, ls=":")
ax.text(0.012, TH_STAR6 - 0.15, f"静学 $\\theta^*$={TH_STAR6:.2f}", fontsize=FS_ANN, color=GRAY, va="top")
ax.axhline(XI_NOW, color=C_REF, lw=0.8, ls=":")
ax.text(0.012, XI_NOW + 0.15, f"恒久成分の推定値 {XI_NOW:.2f}（2026年6月）", fontsize=FS_ANN, color=GRAY, va="bottom")
ax.axvspan(0.10, 0.30, color=C_BLUE, alpha=0.06, lw=0)
for sv, lab in ((SIG_SUB, "2023年4月〜"), (SIG_FULL, "全期間")):
    ax.plot([sv], [0.0], marker="^", ms=5.5, color=GRAY, mec="white", mew=0.8, clip_on=False, zorder=5)
    ax.text(sv, 0.3, f"$\\sigma_\\xi$（{lab}）", fontsize=FS_ANN, color=GRAY, ha="center", va="bottom")
ax.set_xlim(0.0, 0.37)
ax.set_xticks([0, 0.1, 0.2, 0.3])
ax.set_ylim(0, 10)
ax.set_xlabel("恒久成分のボラティリティ $\\sigma$（年率）", fontsize=FS_LAB, color=GRAY)
ax.set_ylabel("参入に必要な価格水準係数", fontsize=FS_LAB, color=GRAY)
ax.set_title("(b) 待機を考慮した参入閾値（WACC 6%）", fontsize=FS_TTL, loc="left", color="#222222", pad=4)
ax.legend(fontsize=FS_LEG, frameon=False, loc="upper left", handlelength=2.0, borderaxespad=0.2, labelspacing=0.3)

# (c)
ax = axes[2]
style(ax)
yrs = np.arange(FY0 + 1, 2041)
for sig, col in ((0.15, C_BLUE), (0.30, C_ORANGE)):
    fp = cum_for_fig[(sig, 0.05)]
    ax.plot(yrs, 100 * fp["静学"], color=col, lw=1.5, ls="--", label=f"静学ルール $\\theta^*$（$\\sigma$={sig:.2f}）")
    ax.plot(yrs, 100 * fp["競争均衡"], color=col, lw=1.5, label=f"競争均衡 $\\theta_c$（$\\sigma$={sig:.2f}）")
    for k in ("静学", "競争均衡"):
        ax.plot([yrs[-1]], [100 * fp[k][-1]], marker="o", ms=3.8, color=col, mec="white", mew=0.8)
        ax.text(yrs[-1] + 0.4, 100 * fp[k][-1], f"{100*fp[k][-1]:.1f}%", fontsize=FS_ANN, color=GRAY, va="center")
ax.set_xlim(FY0 + 0.5, 2043.3)
ax.set_xticks([2028, 2032, 2036, 2040])
ax.set_ylim(0, 44)
ax.set_xlabel("年度", fontsize=FS_LAB, color=GRAY)
ax.set_ylabel("参入が開く累積確率（%）", fontsize=FS_LAB, color=GRAY)
ax.set_title("(c) 参入が開く累積確率（$g_I$=5%）", fontsize=FS_TTL, loc="left", color="#222222", pad=4)
ax.legend(fontsize=FS_LEG, frameon=False, loc="upper left", handlelength=2.0, borderaxespad=0.2, labelspacing=0.3)

# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "real_option_threshold.png"), dpi=300, bbox_inches="tight", pad_inches=0.03)
print("\nsaved: real_option_threshold.csv, real_option_entry_prob.csv, real_option_price_level.csv, "
      "real_option_waiting_value.csv, real_option_short_duration.csv, real_option_drift_sensitivity.csv, "
      "real_option_sensitivity_v3.csv, real_option_fleet_alloc_v3.csv, real_option_threshold.png")
