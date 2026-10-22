#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""損益分岐面と均衡容量の格子 v3: 表8.6（π(K; 風力, 泊) と下端の扱い）・表9.2（θ* の格子）・表9.3（K*）・図9.1

目的（決定事項 D1・D2・D3・D5、監査 A8-5-1・A9-4-1・A9-4-2・L-9 への対応）:
  旧版（28）は、限界参入者の収益を 0.81·π_PF(K)−1,752（π_PF はモデルの完全予見粗利）とし、K の格子は
  [0,10,25,50,100,150,200] を10万kW 刻みで回したため K=25 は実際には30で計算され、θ≠1 の π(K) は θ=1 の曲線の θ 倍で
  置いていた。容量価格の内生化は2029年度向け曲線の平行移動で、起点を1.75万・2.5万円に上げると下がらない床が残った。
  本スクリプトは 41（T1）の π_c(K)（モデル価格の経路の上で戦略c の実現粗利を直接計算）に基準を置き換え、格子・θ・
  容量価格の扱いを直す。

手法:
  (0) 部品: 41_equilibrium_v3.py の前半（価格関数・戦略c・増分貪欲ディスパッチ・仕様A′。"curves = []" の行より前の
      定義部分）を exec で読み込む（その間 pandas.DataFrame.to_csv を無効にし、標準出力は捨てる。41 自体は実行しない）。
      41 の出力 pi_k_curve_v3.csv と重なる曲線は再計算して一致を assert で確かめる（c・π_PF の差 <0.01円）。
      評価は FY2023〜25 の1,096日（年度合計の3年平均、円/kW-年）。蓄電池 1MW/4MWh・往復効率0.85（放電側）・1日1サイクル。
      収益の基準（D1）: 実績整合（主）π = λ·c_model(K) − 1,752、λ = 実績の戦略c 8,427円 ÷ モデルの c(K=0, θ=1, 現状)
      （in-sample 校正。下端の扱い・仕様ごとに現状で校正）。モデル直値 π = c_model(K) − 1,752（下側の参考）。
      旧 π = 0.81·π_PF(K) − 1,752。フリートは完全予見の増分貪欲（主、刻み1万kW、目標の K に正確に到達）。
  (1) 表8.6: 仕様A（26、θ=1）の上で風力導入量を現行（121万kW、FY2023〜25 の B表平均）の 0.5〜3倍、泊3号（820.8MW）
      なし／ありの 10 セルについて、K=0〜200万kW を1万kW ごとに評価する。供給曲線 g の下端の扱いを
      (i) 段差（現行。各季節の最下位ビンの中心より下を 0.01円）、(ii) 線形外挿・下限あり（33 と同じ。最初の打ち切られて
      いない8ビンの傾きで延長し 0.01円で打ち切る）、(iii) 仕様A′（μ×日次風力三分位、段差）の3通りにする。各セルに K=0 で
      推定範囲外（最下位ビンの中心より純需要が低い時間）の割合と、モデルの下限張り付き時間を付ける。
  (2) θ 別の π(K): 現状の仕様A（26）で θ=1・1.22（恒久成分）・1.567（FY2026上期）・1.715（FY2022）・2.0・2.5・3.0 を
      K=0〜150 は1万kW ごと、160〜300 は10万kW ごとに直接計算する（θ·π(K;1) の比例で置かない）。D3 の感応度として
      フリートが戦略c の窓に従う配分（K≤150）も計算する。旧 28 の格子（10万kW 刻み・K=25 は実際30）も再現する。
  (3) 表9.2: θ*（K=0 で参入が開く価格水準係数）を資本費 2.3〜6.8万円/kWh × 実効容量収入 0〜2.5万円 × WACC 5・6・8% で
      解く。need = c_req − κP_cap + 1,752、c_req = 4h資本費×CRF(WACC,20年) + 運維・廃止0.53万 + 託送等固定0.69万。
      比例の式 θ* = need/a(0;θ=1) と、a(0;θ)=α+βθ を (2) の7点に当てはめた直接解を併記する。λ の95%区間
      （1.030〜1.191、41 の定常ブートストラップ）の幅も出す。図9.1 は実績整合の等高線に旧基準の θ*=1・1.57 を重ねる。
  (4) 表9.3: K* は「π(K;θ) + 実効容量収入(K) ≥ c_req」が K_exo から途切れずに成り立つ最大の総容量（0.1万kW 格子上の
      線形補間。π は (2) の曲線の線形補間）。マーチャント分は K*−K_exo。容量価格の扱いは、定数／北海道ブロック按分
      （H3 シェア 529/16,208）／全国連系 × {平行移動（旧28、参考）、比例縮小 ci0·P(K)/P0、2030年度向け近似（主）}。
      2030年度向け近似は4点折れ線で、価格軸は上限約30,700円（notes/13）・目標調達量の指標価格20,911円（Net CONE）・0、
      数量軸は2029年度向けの公表値（上限価格の調達量188,813,656kW・目標189,966,340kW・価格ゼロ195,652,080kW）を
      そのまま使う（2030年度向けの数量は未取得）。現在点を P=ci0/κ の点に置き、κ·(K−K_exo＋K_exo の非LTDA分) だけ
      右に動かす（ブロック按分では数量軸をシェアで縮める）。κ=0.836（2029年度向け北海道4h）。
      外生の契約型容量 K_exo（D5）: 0（主、参入に有利な側）、20（接続済み）、76.8（20＋LTDA 第3回別解56.8）、
      87.4（20＋LTDA 訂正値67.4、T6）、99.1（4時間換算）。LTDA 電源は容量市場に参加しないので容量価格には
      接続済み20万kW だけを入れる（主）。2029年度向けの約定価格14,972円が既設の蓄電池の応札を既に含む場合は二重計上に
      なるので、20万kW も入れない版を併記する。
出力: data/processed/breakeven_surface_v3_pik.csv（表8.6 の全曲線、K=0〜200）、breakeven_surface_v3_table86.csv（表8.6 の
      セル・π=0 の K・推定範囲外の割合）、pi_k_theta_v3.csv（θ 別の π(K)）、breakeven_frontier_v3.csv（θ* の格子）、
      capacity_price_of_k_v3.csv（P_cap(K) と実効容量収入の扱い別の値）、kstar_grid_v3.csv（K* の全格子）、
      kstar_table93_v3.csv（表9.3 の行と旧値の分解）、figures/hokkaido/breakeven_frontier_v3.png、
      figures/hokkaido/equilibrium_surface_v3.png
限界: 部分均衡（揚水・連系線潮流・入札行動は g に埋め込まれた歴史的応答のまま）。λ は K=0・θ=1 の in-sample 校正で、
      K>0 ではフリートが裾を先に削るので実績整合は上側の値になりうる。増分貪欲は刻みに対してほぼ1次で収束し、刻み1万kW
      でも K≥70 では π(K) が刻み0への外挿より約1〜3%低い（41 の docstring）。泊を重ねたセル、とくに風力2〜3倍との重ねでは
      純需要が g の推定範囲より下に大きく出るので、π は下端の置き方（段差か外挿か）で決まり、データでは判定できない。
      仕様A′ の μ は最上位の風力三分位より先へ外挿しない。2030年度向けの需要曲線は数量軸を2029年度向けで代用した近似で、
      分断ブロックの按分規則（約定処理仕様）も未確認の仮定である。K_exo は既設・契約型の容量が価格テイカーとして同じ
      増分貪欲で動くと置いたもので、FY2023〜25 の価格（g の推定）には当時稼働していた蓄電池の影響が既に入っている
      （二重計上の上限側）。容量市場の約定価格の K 依存は需要曲線に沿う移動だけで、他の電源の応札の変化は含めない。
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
price_A, g_curve, net_scenario = m41["price_A"], m41["g_curve"], m41["net_scenario"]
pf_Aprime, AP3 = m41["pf_Aprime"], m41["AP3"]
G26, MU26B, SEASB, BLK = m41["G26"], m41["MU26B"], m41["SEASB"], m41["BLK"]
W_B, FYB, EVB = m41["W_B"], m41["FYB"], m41["EVB"]
FLOOR, ETA, WHEEL, C_FIX = m41["FLOOR"], m41["ETA"], m41["WHEEL"], m41["C_FIX"]
C_ACT, TH26, TH22, K_WIND_NOW, TOMARI = m41["C_ACT"], m41["TH26"], m41["TH22"], m41["K_WIND_NOW"], m41["TOMARI"]
K_EVAL = m41["K_EVAL"]
CAPTURE_OLD = 0.81
KAPPA = 0.836
TH_PERM = 1.22                                         # 恒久成分（8.7、2026年6月）
print(f"41 の部品を読み込み: 実績の戦略c {C_ACT:,.1f}円/kW-年、θ_2026={TH26:.3f}、θ_2022={TH22:.3f}、風力現行 {K_WIND_NOW:.1f}万kW")

CV41 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
LVL41 = pd.read_csv(os.path.join(PROC, "price_model_level_ratios.csv"))
_lr = LVL41[LVL41["期間"].astype(str).str.startswith("λ の95%区間")].iloc[0]
LAM_CI = (float(_lr["c比_下限95"]), float(_lr["c比_上限95"]))


def with_bases(df, lam):
    df = df.copy()
    df["capture_c"] = (df["c"] / df["π_PF"]).where(df["π_PF"] > 1.0)
    df["校正係数λ"] = lam
    df["π_実績整合"] = lam * df["c"] - WHEEL
    df["π_モデル直値"] = df["c"] - WHEEL
    df["π_旧0.81PF"] = CAPTURE_OLD * df["π_PF"] - WHEEL
    return df


def check41(df, model, theta, wm, tom, mode="完全予見の増分貪欲（主）"):
    """41 の pi_k_curve_v3.csv と重なる K で c・π_PF が一致することを確かめる"""
    r = CV41[(CV41["価格モデル"] == model) & np.isclose(CV41["θ"], round(theta, 3)) & (CV41["風力倍率"] == wm)
             & (CV41["泊3号"] == ("あり" if tom else "なし")) & (CV41["フリート配分"] == mode)
             & (CV41["刻み(万kW)"].astype(str) == "1.0")].drop_duplicates("K(万kW)").set_index("K(万kW)")
    if r.empty:
        return None
    k = df.set_index("K(万kW)")
    ks = k.index.intersection(r.index)
    dmax = max(np.abs(k.loc[ks, "c"] - r.loc[ks, "c"]).max(), np.abs(k.loc[ks, "π_PF"] - r.loc[ks, "π_PF"]).max())
    assert dmax < 0.01, (model, theta, wm, tom, mode, dmax)
    return len(ks)


def crossing(K, y, target=0.0):
    for i in range(1, len(K)):
        if (y[i - 1] - target) > 0 >= (y[i] - target):
            return float(np.interp(0.0, [y[i] - target, y[i - 1] - target], [K[i], K[i - 1]]))
    return np.nan


# 下端の線形外挿（33 と同じ: 最初の打ち切られていないビンから8ビンの傾き）
EXT26 = {}
for s in range(4):
    x, y = G26[s]
    i0 = int(np.argmax(y > FLOOR + 0.001))
    EXT26[s] = (x[i0], y[i0], np.polyfit(x[i0:i0 + 8], y[i0:i0 + 8], 1)[0])


def g_ext26(net):
    out = np.empty_like(net, dtype=float)
    for s in range(4):
        m = SEASB == s
        x, y = G26[s]
        xa, ya, sl = EXT26[s]
        v = np.interp(net[m], x, y, right=y[-1])
        lo = net[m] < xa
        v[lo] = ya + sl * (net[m][lo] - xa)
        out[m] = v
    return out


def price_ext26(net, theta=1.0):
    """外挿・下限あり（33 と同じ定義を 26 の g・μ に当てる）: max{0.01, max(g_ext, 0.01) + μ} を θ で伸縮"""
    base = np.maximum(np.maximum(g_ext26(net), FLOOR) + MU26B, FLOOR)
    return np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)


def below_support(net):
    ab = np.zeros_like(net, bool)
    for s in range(4):
        m = SEASB == s
        ab[m] = net[m] < G26[s][0][0]
    return ab


M26, MAP = "仕様A（26、水準係数付き）", "仕様A′（26、μ×日次風力三分位）"

# ---------------------------------------------------------------- (1) 表8.6: π(K; 風力, 泊) × 下端の扱い
print("\n[1] 表8.6（風力0.5〜3倍×泊、K=0〜200、下端の扱い3通り）...")
LOWER = {"段差（仕様A 26、現行）": "step", "線形外挿・下限あり（仕様A 26、33と同じ）": "ext", "仕様A′（26、段差）": "aprime"}
WM86 = (0.5, 1.0, 1.5, 2.0, 3.0)
K86 = list(range(0, 201))
rows86 = []
lam86 = {}
nchk = 0
for vlab, vk in LOWER.items():
    for tom in (False, True):
        for wm in WM86:
            net0 = net_scenario(BLK, tom, wm)
            if vk == "step":
                pfun = lambda n: price_A(n, G26, MU26B, 1.0, SEASB)
            elif vk == "ext":
                pfun = lambda n: price_ext26(n, 1.0)
            else:
                pfun = pf_Aprime(AP3, 1.0, wm)
            df = run_curve(pfun, net0, "PF", K86, 1.0)
            P0 = pfun(net0.copy())
            df["推定範囲外の割合(%)_K0"] = below_support(net0)[EVB].mean() * 100
            df["下限張り付き(h/年)_K0"] = (P0[EVB] <= FLOOR + 1e-6).sum() / 3
            df.insert(0, "泊3号", "あり" if tom else "なし")
            df.insert(0, "風力(万kW)", round(K_WIND_NOW * wm))
            df.insert(0, "風力倍率", wm)
            df.insert(0, "下端の扱い", vlab)
            if vk in ("step", "aprime"):
                nchk += check41(df, M26 if vk == "step" else MAP, 1.0, wm, tom) or 0
            if wm == 1.0 and not tom:
                lam86[vlab] = C_ACT / float(df["c"].iloc[0])
            rows86.append(df)
print(f"  41 の曲線と一致（{nchk} 点）")
S86 = pd.concat(rows86, ignore_index=True)
S86 = pd.concat([with_bases(g, lam86[v]) for v, g in S86.groupby("下端の扱い", sort=False)], ignore_index=True)
S86.round(4).to_csv(os.path.join(PROC, "breakeven_surface_v3_pik.csv"), index=False, encoding="utf-8-sig")
print("  λ（下端の扱い別、現状 K=0 で校正）:", {k: round(v, 4) for k, v in lam86.items()})

KT86 = [0, 10, 25, 50, 75, 100, 150, 200]
t86 = []
for key, g in S86.groupby(["下端の扱い", "泊3号", "風力倍率"], sort=False):
    g = g.set_index("K(万kW)")
    r = dict(zip(["下端の扱い", "泊3号", "風力倍率"], key))
    r["推定範囲外の割合(%)_K0"] = g["推定範囲外の割合(%)_K0"].iloc[0]
    r["下限張り付き(h/年)_K0"] = g["下限張り付き(h/年)_K0"].iloc[0]
    r["π_PF(0)"] = g.loc[0, "π_PF"]
    r["capture_c(0)"] = g.loc[0, "capture_c"]
    for bl in ("π_実績整合", "π_モデル直値", "π_旧0.81PF"):
        for k in KT86:
            r[f"{bl}({k})"] = g.loc[k, bl]
        r[f"{bl}=0のK"] = crossing(g.index.to_numpy(float), g[bl].to_numpy())
    t86.append(r)
T86 = pd.DataFrame(t86)
T86.round(4).to_csv(os.path.join(PROC, "breakeven_surface_v3_table86.csv"), index=False, encoding="utf-8-sig")
assert (S86[["π_実績整合", "π_モデル直値", "π_旧0.81PF"]].max() < 19_500).all()   # 判定基準: 面上のすべてのセルが参入必要水準未満
for bl in ("π_実績整合", "π_旧0.81PF"):
    print(f"\n  表8.6（{bl}）: 行=K、列=風力倍率、各セル 泊なし / 泊あり")
    for vlab in LOWER:
        d = T86[T86["下端の扱い"] == vlab]
        print("   ", vlab)
        for k in (0, 25, 50, 100, 150):
            cells = []
            for wm in WM86:
                a = d[(d["風力倍率"] == wm) & (d["泊3号"] == "なし")][f"{bl}({k})"].iloc[0]
                b = d[(d["風力倍率"] == wm) & (d["泊3号"] == "あり")][f"{bl}({k})"].iloc[0]
                cells.append(f"{a:,.0f}/{b:,.0f}")
            print(f"     K{k:>3}: " + "  ".join(cells))
        z = [f"{d[(d['風力倍率'] == wm) & (d['泊3号'] == 'なし')][f'{bl}=0のK'].iloc[0]:.1f}/"
             f"{d[(d['風力倍率'] == wm) & (d['泊3号'] == 'あり')][f'{bl}=0のK'].iloc[0]:.1f}" for wm in WM86]
        print("     π=0 の K: " + "  ".join(z))
print("\n  K=0 の推定範囲外の割合（%）と下限張り付き（h/年）、段差: 泊なし / 泊あり")
d = T86[T86["下端の扱い"].str.startswith("段差")]
for wm in WM86:
    a, b = d[(d["風力倍率"] == wm) & (d["泊3号"] == "なし")].iloc[0], d[(d["風力倍率"] == wm) & (d["泊3号"] == "あり")].iloc[0]
    e_ = T86[T86["下端の扱い"].str.startswith("線形") & (T86["風力倍率"] == wm)]
    print(f"   ×{wm}: 範囲外 {a['推定範囲外の割合(%)_K0']:.1f}/{b['推定範囲外の割合(%)_K0']:.1f}%  下限 段差 {a['下限張り付き(h/年)_K0']:.0f}/{b['下限張り付き(h/年)_K0']:.0f}"
          f"  外挿 {e_[e_['泊3号'] == 'なし']['下限張り付き(h/年)_K0'].iloc[0]:.0f}/{e_[e_['泊3号'] == 'あり']['下限張り付き(h/年)_K0'].iloc[0]:.0f} h/年")

# ---------------------------------------------------------------- (2) θ 別の π(K)（直接計算）
print("\n[2] θ 別の π(K)（現状、仕様A 26）...")
THETAS = [1.0, TH_PERM, TH26, TH22, 2.0, 2.5, 3.0]
net_now = net_scenario(BLK)
rowsT = []
for th in THETAS:
    df = run_curve(lambda n, t=th: price_A(n, G26, MU26B, t, SEASB), net_now, "PF", K_EVAL, 1.0)
    df.insert(0, "θ", th)
    df.insert(0, "フリート配分", "完全予見の増分貪欲（主）")
    check41(df, M26, th, 1.0, False)
    rowsT.append(df)
for th in (1.0, TH26, TH22, 2.5, 3.0):
    df = run_curve(lambda n, t=th: price_A(n, G26, MU26B, t, SEASB), net_now, "c", list(range(0, 151)), 1.0)
    df.insert(0, "θ", th)
    df.insert(0, "フリート配分", "戦略cの窓")
    check41(df, M26, th, 1.0, False, "戦略cの窓")
    rowsT.append(df)
LAM = C_ACT / float(rowsT[0]["c"].iloc[0])
assert abs(LAM - 1.1085) < 1e-3
PIT = with_bases(pd.concat(rowsT, ignore_index=True), LAM)
PIT.insert(0, "価格モデル", M26)
PIT.round(4).to_csv(os.path.join(PROC, "pi_k_theta_v3.csv"), index=False, encoding="utf-8-sig")
print(f"  λ = {LAM:.4f}（41 と同じ）。41 と重なる θ（1・1.567・1.715・3.0、窓は1・1.567）の曲線は一致")
for th in THETAS:
    d = PIT[(PIT["θ"] == th) & (PIT["フリート配分"].str.startswith("完全"))].set_index("K(万kW)")
    print(f"  θ={th:.3f}: " + " ".join(f"K{k}:{d.loc[k, 'π_実績整合']:,.0f}" for k in (0, 25, 50, 75, 100, 150, 200, 300))
          + f"  π=0 の K {crossing(d.index.to_numpy(float), d['π_実績整合'].to_numpy()):.1f}")

# 旧 28 の格子（10万kW 刻み・K=25 は実際30）の再現: 旧基準の θ=1 曲線
OLDK = [0, 10, 25, 50, 100, 150, 200]
OLD = run_curve(lambda n: price_A(n, G26, MU26B, 1.0, SEASB), net_now.copy(), "PF", OLDK, 10.0, old_bug=True)
_es = pd.read_csv(os.path.join(PROC, "equilibrium_surface.csv"))
_es = _es[(_es["泊"] == "なし") & (_es["K_wind倍率"] == 1.0)].set_index("K(万kW)")["π_PF(円/kW-年)"]
_dold = (OLD.set_index("K(万kW)")["π_PF"] - _es).abs().max()
assert _dold < 5.0, _dold                            # 41 の検証と同じ（旧0.81PF で ±3円）
print(f"  旧 28 の θ=1 曲線（equilibrium_surface.csv）を再現（π_PF の差 最大 {_dold:.2f}円）")


# ---------------------------------------------------------------- (3) 表9.2: θ* の格子
print("\n[3] θ* の格子（表9.2）...")


def crf(r, n=20):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def c_req(capex_man, wacc):
    return 4 * capex_man * 1e4 * crf(wacc) + C_FIX


CAPEX = [2.3, 3.0, 4.0, 5.0, 6.0, 6.8]
CAPINC = {"0（容量収入なし）": 0.0, "0.83万（発動指令）": 8_300.0, "1.25万（現行・安定電源）": 12_500.0,
          "1.75万（2030年度向け Net CONE 20,911円×κ）": 20_911 * KAPPA, "2.5万（上限近傍3万円×κ）": 30_000 * KAPPA}
K0 = PIT[(PIT["K(万kW)"] == 0) & PIT["フリート配分"].str.startswith("完全")].set_index("θ")
GROSS = {"実績整合": LAM * K0["c"], "実績整合（λ下限95）": LAM_CI[0] * K0["c"], "実績整合（λ上限95）": LAM_CI[1] * K0["c"],
         "モデル直値": K0["c"], "旧0.81PF": CAPTURE_OLD * K0["π_PF"]}
FIT = {}
for b, a in GROSS.items():
    A = np.column_stack([np.ones(len(a)), a.index.to_numpy(float)])
    al, be = np.linalg.lstsq(A, a.to_numpy(float), rcond=None)[0]
    FIT[b] = (al, be, float(np.abs(A @ [al, be] - a.to_numpy(float)).max()), float(a.loc[1.0]))
    print(f"  {b}: a(0;θ=1)={a.loc[1.0]:,.1f}  a(θ)≈{al:,.1f}+{be:,.1f}θ（最大残差 {FIT[b][2]:.1f}円）  "
          f"a(θ)/(θ·a(1)) {min(a / (a.index * a.loc[1.0])):.4f}〜{max(a / (a.index * a.loc[1.0])):.4f}")
fr = []
for wacc in (0.05, 0.06, 0.08):
    for cx in CAPEX:
        for clab, ci in CAPINC.items():
            need = c_req(cx, wacc) - ci + WHEEL
            for b, (al, be, res, a1) in FIT.items():
                tp = need / a1
                td = (need - al) / be
                fr.append({"WACC": wacc, "資本費(万円/kWh)": cx, "実効容量収入": clab, "κP_cap(円/kW-年)": ci,
                           "c_req(円/kW-年)": c_req(cx, wacc), "必要粗収益(円/kW-年)": need, "基準": b, "a(0;θ=1)(円/kW-年)": a1,
                           "θ*（比例）": tp, "θ*（直接解）": td, "直接解の当てはめ最大残差(円)": res,
                           "θ=1で開く": tp <= 1.0, "θ=1.22で開く": tp <= TH_PERM, "θ=1.57で開く": tp <= TH26, "θ=1.72で開く": tp <= TH22})
FR = pd.DataFrame(fr)
FR.round(4).to_csv(os.path.join(PROC, "breakeven_frontier_v3.csv"), index=False, encoding="utf-8-sig")
print(f"  比例と直接解の差の最大（WACC6%、θ*≤6）: "
      f"{(FR[(FR['WACC'] == 0.06) & (FR['θ*（比例）'].between(0, 6))].eval('`θ*（直接解）` - `θ*（比例）`').abs().max()):.3f}")
for b in ("実績整合", "旧0.81PF"):
    print(f"\n  θ*（比例、WACC6%、{b}）: 行=資本費、列=実効容量収入")
    p = FR[(FR["WACC"] == 0.06) & (FR["基準"] == b)].pivot(index="資本費(万円/kWh)", columns="実効容量収入", values="θ*（比例）")[list(CAPINC)]
    print(p.round(2).to_string())
lo_ = FR[(FR["WACC"] == 0.06) & (FR["基準"] == "実績整合（λ上限95）")].pivot(index="資本費(万円/kWh)", columns="実効容量収入", values="θ*（比例）")[list(CAPINC)]
hi_ = FR[(FR["WACC"] == 0.06) & (FR["基準"] == "実績整合（λ下限95）")].pivot(index="資本費(万円/kWh)", columns="実効容量収入", values="θ*（比例）")[list(CAPINC)]
print("\n  λ の95%区間による幅（実績整合、WACC6%）:")
print((lo_.round(2).astype(str) + "〜" + hi_.round(2).astype(str)).to_string())
main92 = FR[(FR["WACC"] == 0.06) & (FR["基準"] == "実績整合")]
for lab, col in (("θ=1（FY2023〜25）", "θ=1で開く"), ("θ=1.22（恒久成分）", "θ=1.22で開く"), ("θ=1.57（FY2026上期）", "θ=1.57で開く"),
                 ("θ=1.72（FY2022）", "θ=1.72で開く")):
    d = main92[main92[col] & (main92["実効容量収入"] != "0（容量収入なし）")]
    print(f"  {lab} で開く組合せ（実績整合、WACC6%）: " +
          "、".join(f"({r['資本費(万円/kWh)']},{r['実効容量収入'].split('（')[0]})={r['θ*（比例）']:.2f}" for _, r in d.iterrows()))

# ---------------------------------------------------------------- (4) 容量価格の K 依存と K*
print("\n[4] 容量価格の K 依存と K*（表9.3）...")
CURVE29 = {"ceil": 15_112.5, "cone": 10_075.0}
CURVE30 = {"ceil": 30_700.0, "cone": 20_911.0}
Q_CAP, Q_TGT, Q_ZERO = 188_813_656.0, 189_966_340.0, 195_652_080.0
P0_29 = 14_972.0
SHARE = {"北海道ブロック按分": 529 / 16_208, "全国連系": 1.0}


def curve_p(q, cv):
    """4点折れ線の価格（q は全国の調達量 kW）"""
    q = np.asarray(q, float)
    up = cv["ceil"] - (cv["ceil"] - cv["cone"]) * (q - Q_CAP) / (Q_TGT - Q_CAP)
    lo = cv["cone"] * (Q_ZERO - q) / (Q_ZERO - Q_TGT)
    return np.where(q <= Q_CAP, cv["ceil"], np.where(q <= Q_TGT, up, np.maximum(lo, 0.0)))


def curve_q(p, cv):
    """価格 p に対応する調達量（p≥上限は上限価格の調達量）"""
    if p >= cv["ceil"]:
        return Q_CAP
    if p >= cv["cone"]:
        return Q_CAP + (cv["ceil"] - p) / (cv["ceil"] - cv["cone"]) * (Q_TGT - Q_CAP)
    return Q_TGT + (cv["cone"] - p) / cv["cone"] * (Q_ZERO - Q_TGT)


Q0_29 = curve_q(P0_29, CURVE29)
assert abs(float(curve_p(Q0_29, CURVE29)) - P0_29) < 1e-6


def cap_income(dK, ci0, mode, share):
    """実効容量収入（円/kW-年）。dK は容量市場に加わる蓄電池（万kW）。mode: 定数・平行移動・比例縮小・2030近似"""
    dq = KAPPA * np.asarray(dK, float) * 1e4 / share
    if mode == "定数":
        return np.full_like(dq, ci0)
    if mode == "平行移動（旧28、参考）":
        return KAPPA * np.maximum(0.0, curve_p(Q0_29 + dq, CURVE29) - P0_29 + ci0 / KAPPA)
    if mode == "比例縮小":
        return ci0 * curve_p(Q0_29 + dq, CURVE29) / P0_29
    if mode == "2030年度向け近似（主）":
        return KAPPA * curve_p(curve_q(ci0 / KAPPA, CURVE30) + dq, CURVE30)
    raise ValueError(mode)


# 旧 28 の p_cap_of_k と一致することを確認（平行移動、起点1.25万）
for K in (0, 5, 10, 25, 50, 100, 200):
    for s in SHARE.values():
        up = (CURVE29["ceil"] - CURVE29["cone"]) / ((Q_TGT - Q_CAP) * s)
        lo = CURVE29["cone"] / ((Q_ZERO - Q_TGT) * s)
        dq = KAPPA * K * 1e4
        room = (P0_29 - CURVE29["cone"]) / up
        old = P0_29 - up * dq if dq <= room else max(0.0, CURVE29["cone"] - lo * (dq - room))
        assert abs(float(curve_p(Q0_29 + dq / s, CURVE29)) - old) < 1e-6
CAPMODES = ["平行移動（旧28、参考）", "比例縮小", "2030年度向け近似（主）"]
CI0 = {"1.25万": 12_500.0, "1.75万": 20_911 * KAPPA, "2.5万": 30_000 * KAPPA}
cp_rows = []
for K in (0, 5, 10, 20, 25, 30, 50, 75, 100, 150, 200, 300):
    r = {"K(万kW)": K}
    for lab, s in SHARE.items():
        dq = KAPPA * K * 1e4 / s
        r[f"P_cap 2029年度向け {lab}(円/kW)"] = float(curve_p(Q0_29 + dq, CURVE29))
        for cl, ci0 in CI0.items():
            for md in CAPMODES:
                r[f"κP {lab}・起点{cl}・{md}(円/kW-年)"] = float(cap_income(K, ci0, md, s))
    cp_rows.append(r)
CP = pd.DataFrame(cp_rows)
CP.round(1).to_csv(os.path.join(PROC, "capacity_price_of_k_v3.csv"), index=False, encoding="utf-8-sig")
print("  実効容量収入（北海道按分、起点2.5万）: K=" + " ".join(
    f"{r['K(万kW)']}: 平行{r['κP 北海道ブロック按分・起点2.5万・平行移動（旧28、参考）(円/kW-年)']:,.0f}/比例{r['κP 北海道ブロック按分・起点2.5万・比例縮小(円/kW-年)']:,.0f}"
    f"/2030 {r['κP 北海道ブロック按分・起点2.5万・2030年度向け近似（主）(円/kW-年)']:,.0f}" for _, r in CP.iterrows() if r["K(万kW)"] in (0, 10, 25, 50, 200)))
# 判定基準: 北海道按分の2.5万ケースで K が大きいとき実効容量収入が0に近づく（床が消える）
assert cap_income(200, CI0["2.5万"], "2030年度向け近似（主）", SHARE["北海道ブロック按分"]) < 1.0
assert cap_income(200, CI0["2.5万"], "比例縮小", SHARE["北海道ブロック按分"]) < 1.0
for lab, s in SHARE.items():
    for cl, ci0 in CI0.items():
        q0 = curve_q(ci0 / KAPPA, CURVE30)
        kz = (Q_ZERO - q0) * s / KAPPA / 1e4
        print(f"  2030年度向け近似 {lab}・起点{cl}: 価格ゼロまで K≈{kz:,.1f}万kW")

K_EXO = {"0（主）": 0.0, "20（接続済み）": 20.0, "76.8（20＋LTDA第3回別解56.8）": 76.8, "87.4（20＋LTDA訂正値67.4）": 87.4,
         "99.1（20＋LTDA 4時間換算79.1）": 99.1}
KCAP_RULE = {"接続済み20万kWを容量価格に入れる（主）": True, "既設は約定価格に含まれ入れない": False}
TH_KS = {"θ=1（FY2023〜25）": 1.0, "θ=1.22（恒久成分）": TH_PERM, "θ=1.57（FY2026上期）": TH26, "θ=1.72（FY2022）": TH22,
         "θ=2.5": 2.5, "θ=3.0": 3.0}
CX_KS = [2.3, 3.0, 4.0, 5.0, 6.0, 6.8]


def curve_of(th, mode, base):
    d = PIT[np.isclose(PIT["θ"], th) & (PIT["フリート配分"] == mode)].sort_values("K(万kW)")
    return d["K(万kW)"].to_numpy(float), d[base].to_numpy(float)


def k_star(Kc, pic, need, ci0, capmode, share, kexo, kcap_in):
    """π(K)+ci(K) ≥ need が K_exo から途切れずに成り立つ最大の総容量（0.1万kW 格子、線形補間）。
    戻り値 (K*, 状態)。状態: 'ok'・'K_exoで不成立'・'上端超'"""
    Kf = np.round(np.arange(kexo, Kc.max() + 1e-9, 0.1), 6)
    pif = np.interp(Kf, Kc, pic)
    dcap = (Kf - kexo) + (20.0 if (kcap_in and kexo >= 20.0) else 0.0)
    f = pif + cap_income(dcap, ci0, capmode, share) - need
    if f[0] < 0:
        return kexo, "K_exoで不成立"
    neg = np.where(f < 0)[0]
    if len(neg) == 0:
        return float(Kc.max()), "上端超"
    i = neg[0]
    return float(np.interp(0.0, [f[i], f[i - 1]], [Kf[i], Kf[i - 1]])), "ok"


ks_rows = []
for thl, th in TH_KS.items():
    for mode in ("完全予見の増分貪欲（主）", "戦略cの窓"):
        if not (np.isclose(PIT["θ"], th) & (PIT["フリート配分"] == mode)).any():
            continue                                              # 窓フリートは θ=1.22・2.0 を計算していない
        for base in ("π_実績整合", "π_モデル直値", "π_旧0.81PF"):
            if mode == "戦略cの窓" and base != "π_実績整合":
                continue
            Kc, pic = curve_of(th, mode, base)
            for cx in CX_KS:
                for cl, ci0 in CI0.items():
                    need = c_req(cx, 0.06)
                    for kel, kexo in K_EXO.items():
                        for rl, rin in KCAP_RULE.items():
                            if (not rin) and (kexo < 20 or base != "π_実績整合" or mode != "完全予見の増分貪欲（主）"):
                                continue
                            r = {"θ": thl, "θ値": th, "資本費(万円/kWh)": cx, "κP_cap起点": cl, "フリート配分": mode, "基準": base,
                                 "K_exo": kel, "K_exo値": kexo, "容量価格に入れる既設": rl}
                            for capl in ["定数"] + [f"{sl}・{m}" for sl in SHARE for m in CAPMODES]:
                                if capl == "定数":
                                    ks, st = k_star(Kc, pic, need, ci0, "定数", 1.0, kexo, rin)
                                else:
                                    sl, m = capl.split("・", 1)
                                    ks, st = k_star(Kc, pic, need, ci0, m, SHARE[sl], kexo, rin)
                                r[f"K*_{capl}"] = ks
                                r[f"状態_{capl}"] = st
                                r[f"マーチャント分_{capl}"] = ks - kexo
                            ks_rows.append(r)
KS = pd.DataFrame(ks_rows)
KS.round(2).to_csv(os.path.join(PROC, "kstar_grid_v3.csv"), index=False, encoding="utf-8-sig")
print(f"  kstar_grid_v3.csv（{len(KS)} 行）")

# 旧 28 の K* の再現（旧基準・旧格子・θ·π(K;1)・平行移動・整数の K）
Kfine = np.arange(0, 201, 1)
pf_old = np.interp(Kfine, OLD["K(万kW)"].to_numpy(float), OLD["π_PF"].to_numpy(float))


def k_star_old(theta, cx, ci0, share=None):
    need, best = c_req(cx, 0.06), 0.0
    for K, pf in zip(Kfine, pf_old):
        ci = ci0 if share is None else float(cap_income(K, ci0, "平行移動（旧28、参考）", share))
        if theta * pf * CAPTURE_OLD - WHEEL + ci - need >= 0:
            best = K
        else:
            break
    return best


_ksold = pd.read_csv(os.path.join(PROC, "kstar_grid.csv"))
_thmap = {"θ=1（FY2023-25）": 1.0, "θ=1.57（FY2026上期）": TH26, "θ=1.72（FY2022）": TH22, "θ=2.5": 2.5, "θ=3.0": 3.0}
_mis = 0
for _, r in _ksold.iterrows():
    th, ci0 = _thmap[r["θ"]], CI0[r["κP_cap"]]
    rep = (k_star_old(th, r["資本費(万円/kWh)"], ci0), k_star_old(th, r["資本費(万円/kWh)"], ci0, SHARE["北海道ブロック按分"]),
           k_star_old(th, r["資本費(万円/kWh)"], ci0, SHARE["全国連系"]))
    _mis += int(rep != (r["K*_容量定数(万kW)"], r["K*_北海道按分(万kW)"], r["K*_全国連系(万kW)"]))
print(f"  旧 kstar_grid.csv（45行）の再現: 不一致 {_mis} 行")
assert _mis == 0

# 表9.3 の行: 旧表の9行＋実績整合で K=0 に参入が開く組合せ
OLD93 = [(1.0, 2.3, "1.75万"), (1.0, 2.3, "2.5万"), (TH26, 2.3, "1.25万"), (TH26, 2.3, "1.75万"), (TH26, 2.3, "2.5万"),
         (TH26, 4.0, "2.5万"), (TH22, 4.0, "1.75万"), (2.5, 4.0, "1.25万"), (3.0, 6.8, "2.5万")]
OLDV = {(1.0, 2.3, "1.75万"): (21, 2, 17), (1.0, 2.3, "2.5万"): ("200超", 15, 119), (TH26, 2.3, "1.25万"): (7, 0, 5),
        (TH26, 2.3, "1.75万"): (48, 6, 35), (TH26, 2.3, "2.5万"): ("200超", 20, 125), (TH26, 4.0, "2.5万"): (74, 10, 49),
        (TH22, 4.0, "1.75万"): (6, 0, 5), (2.5, 4.0, "1.25万"): (5, 1, 5), (3.0, 6.8, "2.5万"): (24, 7, 22)}
sel = KS[(KS["フリート配分"].str.startswith("完全")) & (KS["容量価格に入れる既設"].str.endswith("（主）"))]
t93 = []
combos = list(OLD93)
for th in TH_KS.values():
    for cx in CX_KS:
        for cl in CI0:
            m = sel[np.isclose(sel["θ値"], th) & (sel["資本費(万円/kWh)"] == cx) & (sel["κP_cap起点"] == cl)
                    & (sel["基準"] == "π_実績整合") & (sel["K_exo値"] == 0)]
            if m["状態_定数"].iloc[0] != "K_exoで不成立" and (th, cx, cl) not in combos:
                combos.append((th, cx, cl))
for th, cx, cl in combos:
    r = {"θ": th, "資本費(万円/kWh)": cx, "κP_cap起点": cl, "旧表にある行": (th, cx, cl) in OLDV}
    if (th, cx, cl) in OLDV:
        r.update({"旧表_定数": OLDV[(th, cx, cl)][0], "旧表_北海道": OLDV[(th, cx, cl)][1], "旧表_全国": OLDV[(th, cx, cl)][2]})
    r["旧の再現_定数"] = k_star_old(th, cx, CI0[cl])
    r["旧の再現_北海道"] = k_star_old(th, cx, CI0[cl], SHARE["北海道ブロック按分"])
    r["旧の再現_全国"] = k_star_old(th, cx, CI0[cl], SHARE["全国連系"])
    for base in ("π_旧0.81PF", "π_モデル直値", "π_実績整合"):
        for kel, kexo in K_EXO.items():
            if base != "π_実績整合" and kexo > 0:
                continue
            m = sel[np.isclose(sel["θ値"], th) & (sel["資本費(万円/kWh)"] == cx) & (sel["κP_cap起点"] == cl)
                    & (sel["基準"] == base) & (sel["K_exo値"] == kexo)].iloc[0]
            tag = f"{base.replace('π_', '')}・K_exo{kexo:g}"
            r[f"{tag}_定数"] = m["K*_定数"] if m["状態_定数"] != "上端超" else 300.1
            for sl in SHARE:
                for md in CAPMODES:
                    v = m[f"K*_{sl}・{md}"]
                    r[f"{tag}_{sl}・{md}"] = v if m[f"状態_{sl}・{md}"] != "上端超" else 300.1
            if kexo > 0:                                          # マーチャント分 K*−K_exo（総容量が上端超なら上端超）
                for col in ["定数"] + [f"{sl}・{md}" for sl in SHARE for md in CAPMODES]:
                    r[f"{tag}_マーチャント分_{col}"] = r[f"{tag}_{col}"] - kexo if r[f"{tag}_{col}"] <= 300 else 300.1
    # 戦略c の窓のフリート（K≤150）
    mc = KS[np.isclose(KS["θ値"], th) & (KS["資本費(万円/kWh)"] == cx) & (KS["κP_cap起点"] == cl) & (KS["フリート配分"] == "戦略cの窓")
            & (KS["K_exo値"] == 0)]
    if len(mc):
        mc = mc.iloc[0]
        r["実績整合・窓フリート_定数"] = mc["K*_定数"] if mc["状態_定数"] != "上端超" else 150.1
        for sl in SHARE:
            v = mc[f"K*_{sl}・2030年度向け近似（主）"]
            r[f"実績整合・窓フリート_{sl}・2030"] = v if mc[f"状態_{sl}・2030年度向け近似（主）"] != "上端超" else 150.1
    t93.append(r)
T93 = pd.DataFrame(t93)
T93.round(2).to_csv(os.path.join(PROC, "kstar_table93_v3.csv"), index=False, encoding="utf-8-sig")


def fmt(v, cap=300.0):
    if isinstance(v, str):
        return v
    if pd.isna(v):
        return "—"
    return f"{cap:.0f}超" if v > cap else f"{v:.1f}"


print("\n  表9.3（K*、万kW。主: 実績整合・完全予見フリート・2030年度向け近似。300.1 は300超、窓フリートの150.1 は150超）")
hdr = ["θ", "資本費", "κP", "旧表(定/北/全)", "旧の再現", "旧基準・正しい格子(定/北平行/全平行)", "実績整合 定数", "北海道 平行/比例/2030",
       "全国 平行/比例/2030", "K_exo20 (定/北2030/全2030)", "K_exo87.4 (定/全2030)", "窓フリート(定/全2030)"]
print("   " + " | ".join(hdr))
for _, r in T93.iterrows():
    old = f"{r.get('旧表_定数', '—')}/{r.get('旧表_北海道', '—')}/{r.get('旧表_全国', '—')}" if r["旧表にある行"] else "—"
    rep = f"{r['旧の再現_定数']:.0f}/{r['旧の再現_北海道']:.0f}/{r['旧の再現_全国']:.0f}"
    og = f"{fmt(r['旧0.81PF・K_exo0_定数'])}/{fmt(r['旧0.81PF・K_exo0_北海道ブロック按分・平行移動（旧28、参考）'])}/{fmt(r['旧0.81PF・K_exo0_全国連系・平行移動（旧28、参考）'])}"
    t = "実績整合・K_exo0"
    hk = "/".join(fmt(r[f"{t}_北海道ブロック按分・{m}"]) for m in CAPMODES)
    nt = "/".join(fmt(r[f"{t}_全国連系・{m}"]) for m in CAPMODES)
    e20 = f"{fmt(r['実績整合・K_exo20_定数'])}/{fmt(r['実績整合・K_exo20_北海道ブロック按分・2030年度向け近似（主）'])}/{fmt(r['実績整合・K_exo20_全国連系・2030年度向け近似（主）'])}"
    e87 = f"{fmt(r['実績整合・K_exo87.4_定数'])}/{fmt(r['実績整合・K_exo87.4_全国連系・2030年度向け近似（主）'])}"
    wf = (f"{fmt(r.get('実績整合・窓フリート_定数'), 150)}/{fmt(r.get('実績整合・窓フリート_全国連系・2030'), 150)}"
          if "実績整合・窓フリート_定数" in r and not pd.isna(r.get("実績整合・窓フリート_定数")) else "—")
    print(f"   {r['θ']:.2f} | {r['資本費(万円/kWh)']} | {r['κP_cap起点']} | {old} | {rep} | {og} | {fmt(r[f'{t}_定数'])} | {hk} | {nt} | {e20} | {e87} | {wf}")

# 既設の容量を容量価格に入れない版（K_exo=20）の差
alt = KS[(KS["容量価格に入れる既設"] == "既設は約定価格に含まれ入れない") & (KS["K_exo値"] == 20)]
mainx = KS[(KS["容量価格に入れる既設"].str.endswith("（主）")) & (KS["K_exo値"] == 20) & (KS["基準"] == "π_実績整合")
           & (KS["フリート配分"].str.startswith("完全"))]
mm = alt.merge(mainx, on=["θ", "資本費(万円/kWh)", "κP_cap起点"], suffixes=("_alt", "_main"))
for col in ("全国連系・2030年度向け近似（主）", "北海道ブロック按分・2030年度向け近似（主）"):
    print(f"  K_exo=20 で既設を容量価格に入れない版との差（{col}）: 最大 {(mm[f'K*_{col}_alt'] - mm[f'K*_{col}_main']).abs().max():.1f}万kW")

# ---------------------------------------------------------------- 図
print("\n[図] breakeven_frontier_v3.png・equilibrium_surface_v3.png ...")
cx_axis = np.linspace(2.0, 7.0, 101)
ci_axis = np.linspace(0, 26_000, 105)
CXg, CIg = np.meshgrid(cx_axis, ci_axis)
REQ = np.vectorize(lambda c: c_req(c, 0.06))(CXg)
TH_NEW = (REQ - CIg + WHEEL) / FIT["実績整合"][3]
TH_REF = (REQ - CIg + WHEEL) / FIT["旧0.81PF"][3]   # 参考: 実現率0.81×モデルの完全予見粗利（取り逃しを二重に差し引く置き方）
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする（2つの図とも）
fig, ax = plt.subplots(figsize=(6.1, 4.3), layout="constrained")
lev = [-5, 0, 1, TH_PERM, TH26, TH22, 2, 2.5, 3, 4, 6]
cols = ["#E8F3FA", "#C7E4F5", "#9DC3E6", "#7FB2DE", "#6FA8DC", "#4A90C8", "#2F6FA8", "#1F4E79", "#143452", "#0B1F33"]
cf = ax.contourf(CXg, CIg / 1e4, TH_NEW, levels=lev, colors=cols, alpha=0.92)
cs = ax.contour(CXg, CIg / 1e4, TH_NEW, levels=[1.0, TH26, TH22], colors=["#D95B20"] * 3, linewidths=[2.2, 1.6, 1.6],
                linestyles=["-", "--", ":"])
ax.clabel(cs, fmt={1.0: "θ*=1（FY2023〜25の水準で参入）", TH26: "θ*=1.57（FY2026上期）", TH22: "θ*=1.72（FY2022）"},
          fontsize=8.5, inline=True, manual=[(3.8, 1.88), (4.6, 1.68), (5.85, 1.99)])   # ラベルが図の端で切れないよう位置を指定
co = ax.contour(CXg, CIg / 1e4, TH_REF, levels=[1.0, TH26], colors=["#7B3F9E", "#7B3F9E"], linewidths=[1.3, 1.0],
                linestyles=[(0, (4, 2)), (0, (1, 2))])
ax.clabel(co, fmt={1.0: "参考 θ*=1", TH26: "参考 θ*=1.57"}, fontsize=8.5, inline=True, manual=[(2.6, 1.63), (5.3, 2.19)])
cb = fig.colorbar(cf, ax=ax, pad=0.02, format="%.2f")
cb.set_label("参入に必要な価格水準係数 θ*（FY2023〜25=1）", fontsize=9, color=GRAY)
cb.ax.tick_params(labelsize=8.5)
ax.scatter([6.8], [1.25], color="#D95B20", s=40, zorder=5)
ax.text(6.75, 1.30, f"現状（6.8万円/kWh・1.25万円）\nθ*={FR[(FR['WACC'] == 0.06) & (FR['基準'] == '実績整合') & (FR['資本費(万円/kWh)'] == 6.8) & (FR['実効容量収入'].str.startswith('1.25'))]['θ*（比例）'].iloc[0]:.2f}",
        ha="right", va="bottom", fontsize=8.5, color="#D95B20", bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.5))
ax.scatter([2.3], [1.25], color="#176871", s=36, zorder=5)
ax.text(2.35, 1.36, "揚水並み2.3万円/kWh", va="bottom", fontsize=8.5, color="#176871", bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.5))
ax.set_xlabel("蓄電池の資本費（万円/kWh、4時間仕様）", fontsize=9, color=GRAY)
ax.set_ylabel("実効容量収入（万円/kW-年）", fontsize=9, color=GRAY)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
ax.tick_params(colors=GRAY, labelsize=8.5)
fig.savefig(os.path.join(FIGDIR, "breakeven_frontier_v3.png"), dpi=300)
plt.close(fig)

C = {0.5: "#9DC3E6", 1.0: "#0079C2", 1.5: "#176871", 2.0: "#D95B20", 3.0: "#7B3F9E"}
fig, axes = plt.subplots(1, 2, figsize=(6.1, 4.0), sharey=True, layout="constrained")
for ax, vlab in zip(axes, ["段差（仕様A 26、現行）", "線形外挿・下限あり（仕様A 26、33と同じ）"]):
    for wm, c_ in C.items():
        for tl, ls in (("なし", "-"), ("あり", "--")):
            d = S86[(S86["下端の扱い"] == vlab) & (S86["風力倍率"] == wm) & (S86["泊3号"] == tl)]
            ax.plot(d["K(万kW)"], d["π_実績整合"], color=c_, lw=1.5 if tl == "なし" else 1.0, ls=ls,
                    label=f"風力×{wm}（{round(K_WIND_NOW * wm)}万kW）" if tl == "なし" else None)
    ax.axhline(0, color=GRAY, lw=0.9)
    ax.set_title(f"({'a' if vlab.startswith('段差') else 'b'}) 下端：{vlab.split('（')[0]}", fontsize=9.5, fontweight="bold", loc="left")
    ax.set_xlabel("フリート容量 K（万kW、4時間換算）", fontsize=9, color=GRAY)
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    for sp_ in ("top", "right"):
        ax.spines[sp_].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=8.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}".replace("-", "−")))
axes[0].set_ylabel("限界参入者の実現可能収益\nπ(K)（円/kW-年）", fontsize=9, color=GRAY)
_h, _l = axes[0].get_legend_handles_labels()
_h += [plt.Line2D([], [], color=GRAY, lw=1.5, ls="-"), plt.Line2D([], [], color=GRAY, lw=1.0, ls="--")]
_l += ["泊なし", "泊3号の再稼働"]
fig.legend(_h, _l, fontsize=8.5, frameon=False, loc="outside lower center", ncol=3, handlelength=1.8, columnspacing=1.2)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "equilibrium_surface_v3.png"), dpi=300)
plt.close(fig)
print("saved")
