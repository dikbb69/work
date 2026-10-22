#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""蓄電池の価値の補足: 北海道と九州の「脚」の比較と、duration 別（2〜8時間）の参入閾値（監査 A7-1・A7-6）

目的:
  A7-1 原稿（7.1・7.6・要旨・表5.1・12）の「九州は充電脚（昼の深い窪み）、北海道は放電脚（夕方のスパイク）が価値の源泉で、
       オプションの脚が入れ替わっている」という主張を、両エリアの共通日で検証する。
  A7-6 7.4 の結び「より長い duration の価値が両市場で残る。…4時間固定は保守的な仮定である」を、限界収入と限界費用で検証する。
       41（T1）と同じ方法（価格過程モデル 26 の経路の上で戦略c の実現粗利を直接計算し、K=0・4時間で実績の戦略c に校正）で
       duration 別の π_c(0) を求め、資本費（kWh 比例＋PCS 等の kW 部分）と容量市場の調整係数を入れた θ* を出す。

手法:
  A. 脚の比較（実績価格、JEPX エリアプライスの60分平均。北海道 hokkaido_hourly_panel.csv・九州 kyushu_hourly_panel.csv）
     両エリアとも24時間そろう共通日（FY2016-04-01〜FY2026-06-30、北海道の胆振東部地震の欠測20日を除く）。
     日ごとに上位4時間の平均 T、下位4時間の平均 B、日平均 m を求め、完全予見粗利（休止前）を恒等式
       4(ηT−B) = 4η(T−m)［放電脚のプレミアム］ + 4(m−B)［充電脚のディスカウント］ − 4(1−η)m［往復損失の水準項］
     で分ける（η=0.85、円/kW-日）。日平均で基準化した脚は T/m−1（放電脚）と 1−B/m（充電脚）、放電脚の比率は
     (T−m)/(T−B)（いずれも期間平均の比）。北海道−九州の差を、脚ごとに水準の寄与（m の差）と形状の寄与（T/m・B/m の差）に
     分ける: Δ4η(T−m) = 4η[Δm·(T/m−1)_九州 + m_北海道·Δ(T/m)]、Δ4(m−B) = 4[Δm·(1−B/m)_九州 − m_北海道·Δ(B/m)]。
     差の推論は、共通日の日次の差（比は線形化した影響関数）の平均に EWC（Lazarus et al. 2018、ν=⌊0.4T^{2/3}⌋、余弦基底、
     t_ν）を当てる（季節の部分標本は日を時系列順につないだ系列）。期間は FY2016〜22・FY2016〜21・FY2023〜25・年度別、
     季節（夏7〜9月・冬12〜2月・不需要期）は FY2016〜22・FY2023〜25・年度別。完全予見の窓（上位・下位4時間、同値は均等配分）の
     時刻分布を時刻別に出す。戦略c（36 と同じ定義。直近29暦日のうち同じ曜日区分の日の時刻別平均でランク、5日以上）の実現粗利と
     capture も両エリアで出す（履歴は各エリア自身の価格）。
     判定: 原稿の主張が成り立つには、(i) 北海道の放電脚の比率が九州より有意に大きいか、(ii) 基準化した放電脚のプレミアム
     T/m−1 が北海道で有意に大きい期間・季節がなければならない。円額の放電脚が北海道で大きい期間は、その差が水準と形状の
     どちらから来るかで判定する。
  B. duration 別の価値（h=2〜8時間、1MW/h MWh、1日1サイクル、往復効率0.85 を放電側）
     B1 実績価格（FY2023〜25）: 完全予見粗利 PF(h)（上位 h 時間に放電・下位 h 時間に充電、負なら休止）と戦略c(h)（窓を h 時間に）。
     B2 モデル価格（41 と同じ部品）: 13・26 を exec で読み込み（pandas.DataFrame.to_csv を無効化。hokkaido_cf_series.csv・
        price_level_theta.csv を上書きしない）、仕様A（26、水準係数付き）の K=0 の価格を 2023-02-01〜2026-03-31 の日の行列で作り、
        最初の履歴は FY2022 末（2023-02-01〜03-31）のモデル価格とする。θ=1・1.57・1.72 で c(h)・PF(h) を計算（比例の確認）。
        収益の基準（41 の D1 と同じ）: 実績整合（主）a(h)=λ·c_model(h)、λ=実績c(4h)/モデルc(4h)（K=0・θ=1・4時間で校正し、
        h には同じ λ を使う）。h別校正 a(h)=実績c(h)（=λ_h·c_model(h)）、モデル直値 c_model(h)、旧 0.81·PF_model(h) を併記。
     B3 頑健性: (a) 充放電の順序（各日0時に空から始めて24時に空で終わる、SoC 0〜h の動的計画）。完全予見は実現価格に対する
        最適スケジュール、戦略c は気候値 C に対して同じ動的計画で選んだスケジュールを実現価格で評価する（計画値が負なら休止）。
        「満充電・満放電か休止」（35 と同じ）と「部分充放電可」の2通り。(b) 1日2サイクル（充電量の上限 2h MWh/日）を h=2・3・4 で
        （充電従量負担は実際の充電量で計算。劣化の追加費用は入れない）。(c) λ の定常ブートストラップ（日次の組、平均ブロック長20日、
        B=2,000）で θ*(h) の区間と θ*(h)<θ*(4) となる割合。
  C. 費用と θ*（9.4 の式を duration に拡張、K=0、静学、寿命20年）
     need(h) = I(h)·CRF(WACC,20) + 運維5,000 + 廃止300·I(h)/I(4) + 託送等固定6,900 − κP(h) + 充電従量1.2·h·365、θ*=need/a(h)。
     資本費 I(h)=c_E·h+c_P（円/kW）。4時間で I(4)=4×（資本費 万円/kWh）となるよう、kW 部分の比率 s を
     0（全部 kWh 比例。監査の検算と同じ）、8.8%（PCS 0.6万円/kWh のみ）、24.3%（主: PCS＋「その他」0.7万と工事費1.4万の半分）、
     39.7%（電池部分4.1万以外すべて）で振る（内訳は METI 定置用蓄電システム普及拡大検討会 2024年度とりまとめ p.25 の
     FY2024 系統用の値。battery_capex_series.csv）。資本費は 6.8（FY2024 平均）・6.0（50MWh 以上）・4.0・2.3万円/kWh。
     容量収入 κP(h): 主は 2029年度向け北海道（約定14,972円/kW）の純揚水・蓄電池の調整係数の月平均で、4時間の12,500円
     （41 と同じ）を κ(h)/κ(4) で按分（3h 77.38%・4h 83.59%・5h 88.85%・6h 93.15%・7h 96.50%・8h 98.31%）。2時間は安定電源の
     要件（3時間以上）を満たさないので0。感応度は容量収入0、2026年度向けの約定8,749円×κ(h)、2時間を出力2/3で3時間として
     応札する仮定（参考）。WACC 6%（主）・8%。
     参入が開く θ の比較に加え、4時間に対する h 時間の切替点 θ_sw（h の年額 NPV が4時間を上回る θ）、4→6時間の限界収入と
     限界費用、4時間が θ* 最小となる資本費の範囲を出す。動学の競争均衡の閾値 θ_c は、38 の表8.16 の6仕様で θ_c/θ* が
     一定（σ=0.10 で1.166、0.30 で1.592。real_option_short_duration.csv から読む）なので、その比を掛けた近似値を併記する。
出力:
  data/processed/legs_hokkaido_kyushu.csv   期間×季節×（北海道・九州・差）の m・T・B・脚・基準化した脚・放電脚の比率・PF・戦略c、
                                             差の EWC 推論と水準／形状の分解、判定の列
  data/processed/legs_window_hours.csv      完全予見の充電・放電の窓の時刻分布（期間×季節×エリア×時刻、h/日）
  data/processed/duration_value_v3.csv      h 別の PF・戦略c・capture（実績・モデル θ=1/1.57/1.72）、λ、順序制約・2サイクルの値
  data/processed/duration_theta_star_v3.csv h×資本費×kW 比率×WACC×容量収入×収益の基準の need・a・θ*・θ_c 近似・切替点、
                                             ブートストラップ区間、4時間が最小となる資本費の範囲。区分=表8.16改訂案には
                                             表注用の参考値（2時間を出力2/3・3時間で応札した θ*、6時間の θ_sw。表と同じ実績 c(h)）、
                                             区分=4時間からの最大低下（全組合せでの 1−minθ*/θ*(4)）・主の基準とh別λ_hのθ*の差（検証で追加）
  figures/hokkaido/duration_legs.png        (a) 基準化した脚の比較、(b) duration 別の θ*
限界:
  A: 60分平均の価格（30分の差を捨てる）。上位・下位4時間はランク法で順序を無視する。九州の価格には連系線と出力制御の
     影響が入っており、エリアの「構造の違い」と「価格水準の違い」の分け方は恒等式の上の会計的な分解で因果ではない。
     季節の部分標本の EWC は3年分の同じ季節の日をつないだ系列に当てたもので、年の境目の不連続を無視する。
  B・C: K=0（限界参入者自身の価格インパクトなし）、1日1サイクルを主とする。λ は4時間・K=0・θ=1 の in-sample 校正で、h 別の
     λ_h（1.10〜1.13）との差は小さい。duration が変わると最適なフリートの構成も変わりうるが、π(K;h) は計算していない（K*=0 の
     判定は π(0) で決まる）。2サイクルは劣化の追加費用を入れない上側の値。資本費の kW／kWh の分け方は METI の内訳の按分に
     よる仮定で、劣化・オーグメンテーション、運維の kWh 依存、セル価格の将来の低下に伴う kW 比率の上昇は扱わない（kW 比率の
     上限39.7%で代える）。需給調整市場の収入は入れない（41 と同じゼロレント）。θ_c は π(K)/π(0) の形を4時間の曲線と置いた
     38 の近似の比を流用したもので、h 別に解き直していない。
"""
import contextlib
import io
import logging
import os

import numpy as np
import pandas as pd
from scipy import stats
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
pd.set_option("display.max_columns", 60)

ETA = 0.85
FLOOR = 0.01
CAPTURE_OLD = 0.81
WHEEL_KWH = 1.2                         # 充電従量負担（円/kWh）
HS = [2, 3, 4, 5, 6, 7, 8]              # duration（時間）
SEASONS = ["夏", "冬", "不需要期"]


def season_of(months):
    m = np.asarray(months)
    return np.where(np.isin(m, [7, 8, 9]), "夏", np.where(np.isin(m, [12, 1, 2]), "冬", "不需要期"))


def fy_of(days):
    return np.asarray(days.year - (days.month < 4).astype(int))


def tie_w(sig, k=4):
    """信号の下位 k 時間の重み（境界の同値は均等配分。36・41 と同じ）"""
    s = np.sort(sig, 1)
    thr = s[:, k - 1:k]
    w = (sig < thr).astype(float)
    tied = sig == thr
    return w + tied * ((k - w.sum(1, keepdims=True)) / tied.sum(1, keepdims=True))


def ewc_mean(z):
    """平均の EWC 標準誤差（LLSW 2018。41 の ols_ewc を定数項だけの回帰に当てたものと同じ）。戻り値 (平均, SE, ν)"""
    z = np.asarray(z, float)
    T = len(z)
    nu = max(int(np.floor(0.4 * T ** (2 / 3))), 1)
    tt = np.arange(1, T + 1) - 0.5
    cos = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, nu + 1), tt) / T)
    lam = cos @ (z - z.mean()) / T
    return float(z.mean()), float(np.sqrt((lam ** 2).mean())), nu


def pval(est, se, nu):
    return float(2 * stats.t.sf(abs(est / se), nu)) if se > 0 else np.nan


# =====================================================================================
# A. 北海道と九州の脚の比較（実績価格）
# =====================================================================================
print("=" * 100)
print("A. 北海道と九州の脚の比較（実績価格、共通日）")


def load_panel(fn, col):
    x = pd.read_csv(os.path.join(PROC, fn), usecols=["ts", col], parse_dates=["ts"]).dropna()
    x["day"] = x["ts"].dt.normalize()
    x["hour"] = x["ts"].dt.hour
    P = x.pivot(index="day", columns="hour", values=col)
    return P[P.count(axis=1) == 24].sort_index()


def climatology(P):
    """戦略c の気候値 C（直近29暦日のうち同じ曜日区分の日の時刻別平均、5日以上）。暦日で窓を取る（欠測日があっても36と同じ定義）"""
    days = P.index
    A = P.to_numpy(float)
    wk = np.asarray(days.dayofweek >= 5)
    dn = days.values.astype("datetime64[D]").astype(np.int64)
    C = np.full_like(A, np.nan)
    for i in range(len(days)):
        lo = np.searchsorted(dn, dn[i] - 29)
        j = np.arange(lo, i)
        j = j[wk[j] == wk[i]]
        if len(j) >= 5:
            C[i] = A[j].mean(0)
    return C


def strat_c(A, C, k):
    """戦略c（窓 k 時間、休止なし）の日次実現粗利（円/kW-日）。C が NaN の日は NaN"""
    ok = ~np.isnan(C).any(1)
    out = np.full(len(A), np.nan)
    Cc = C[ok]
    wc, wd = tie_w(Cc, k), tie_w(-Cc, k)
    out[ok] = ETA * (wd * A[ok]).sum(1) - (wc * A[ok]).sum(1)
    return out


PH = load_panel("hokkaido_hourly_panel.csv", "p_hokkaido")
PK = load_panel("kyushu_hourly_panel.csv", "p_kyushu")
cH_all = pd.Series(strat_c(PH.to_numpy(float), climatology(PH), 4), index=PH.index)
cK_all = pd.Series(strat_c(PK.to_numpy(float), climatology(PK), 4), index=PK.index)
COMMON = PH.index.intersection(PK.index)
COMMON = COMMON[COMMON <= "2026-06-30"]
AH, AK = PH.loc[COMMON].to_numpy(float), PK.loc[COMMON].to_numpy(float)
FYC, RSC = fy_of(COMMON), season_of(COMMON.month)
CH, CK = cH_all.reindex(COMMON).to_numpy(), cK_all.reindex(COMMON).to_numpy()
print(f"共通日 {len(COMMON)}日（{COMMON.min().date()}〜{COMMON.max().date()}）、北海道 {len(PH)}日・九州 {len(PK)}日")


def legs(A):
    s = np.sort(A, 1)
    T, B, m = s[:, -4:].mean(1), s[:, :4].mean(1), A.mean(1)
    return {"m": m, "T": T, "B": B, "TB": T - B, "dis": 4 * ETA * (T - m), "chg": 4 * (m - B), "lvl": -4 * (1 - ETA) * m,
            "pf": np.maximum(0.0, 4 * (ETA * T - B)), "Bfloor": (B <= 0.5).astype(float),
            "wc": tie_w(A, 4), "wd": tie_w(-A, 4)}


LH, LK = legs(AH), legs(AK)
# 検算: 恒等式と、表7.1 の年度別完全予見粗利（北海道 9,873・9,586・11,493、九州 12,521・12,401・10,366）
assert np.allclose(LH["dis"] + LH["chg"] + LH["lvl"], 4 * (ETA * LH["T"] - LH["B"]))
for fy_, h7, k7 in ((2023, 9873, 12521), (2024, 9586, 12401), (2025, 11493, 10366)):
    m_ = FYC == fy_
    assert abs(LH["pf"][m_].sum() - h7) < 3 and abs(LK["pf"][m_].sum() - k7) < 3, (fy_, LH["pf"][m_].sum(), LK["pf"][m_].sum())
_ev = (FYC >= 2023) & (FYC <= 2025)
_c36 = pd.read_csv(os.path.join(PROC, "strategy_daily_margins.csv"), parse_dates=["day"]).groupby("fy")["c"].sum().mean()
assert abs(pd.Series(CH[_ev]).groupby(FYC[_ev]).sum().mean() - _c36) < 1.0
print(f"検算: 恒等式・表7.1 の完全予見粗利（±3円）・36 の戦略c（{_c36:,.1f}円）と一致")

BINS = {"0〜5時": range(0, 6), "6〜8時": range(6, 9), "9〜15時": range(9, 16), "16〜21時": range(16, 22), "22〜23時": range(22, 24)}


def full_fy(mask):
    """mask が含む年度がすべて通年（その年度の共通日の95%以上）か"""
    fys = np.unique(FYC[mask])
    return all((mask & (FYC == f)).sum() >= 0.95 * (FYC == f).sum() and (FYC == f).sum() >= 340 for f in fys)


def area_row(L, c, mask, annual_ok):
    n = int(mask.sum())
    g = {k: L[k][mask].mean() for k in ("m", "T", "B", "TB", "dis", "chg", "lvl", "pf", "Bfloor")}
    r = {"日数": n, "日平均m(円/kWh)": g["m"], "上位4h平均T(円/kWh)": g["T"], "下位4h平均B(円/kWh)": g["B"], "TB4h(円/kWh)": g["TB"],
         "放電脚4η(T−m)(円/kW-日)": g["dis"], "充電脚4(m−B)(円/kW-日)": g["chg"], "水準項−4(1−η)m(円/kW-日)": g["lvl"],
         "完全予見粗利(円/kW-日)": g["pf"], "T/m": g["T"] / g["m"], "B/m": g["B"] / g["m"],
         "基準化した放電脚T/m−1": g["T"] / g["m"] - 1, "基準化した充電脚1−B/m": 1 - g["B"] / g["m"],
         "放電脚の比率(T−m)/(T−B)": (g["T"] - g["m"]) / g["TB"], "B≤0.5円の日の比率": g["Bfloor"]}
    cm = mask & ~np.isnan(c)
    r["戦略c(円/kW-日)"] = float(np.nanmean(c[cm])) if cm.any() else np.nan
    r["capture_c"] = float(c[cm].sum() / L["pf"][cm].sum()) if cm.any() else np.nan
    if annual_ok:
        r["完全予見粗利(円/kW-年、年度合計の平均)"] = float(pd.Series(L["pf"][mask]).groupby(FYC[mask]).sum().mean())
        r["戦略c(円/kW-年、年度合計の平均)"] = float(pd.Series(c[cm]).groupby(FYC[cm]).sum().mean()) if cm.sum() == n else np.nan
    for lab, hrs in BINS.items():
        r[f"充電窓_{lab}(h/日)"] = L["wc"][mask][:, list(hrs)].sum(1).mean()
        r[f"放電窓_{lab}(h/日)"] = L["wd"][mask][:, list(hrs)].sum(1).mean()
    return r


def ratio_infl(num, den):
    """比 R=mean(num)/mean(den) の線形化した影響関数 (num−R·den)/mean(den)"""
    R = num.mean() / den.mean()
    return R, (num - R * den) / den.mean()


def diff_row(mask):
    h, k = {kk: v[mask] for kk, v in LH.items() if kk not in ("wc", "wd")}, {kk: v[mask] for kk, v in LK.items() if kk not in ("wc", "wd")}
    r = {"日数": int(mask.sum())}
    for key, lab in (("dis", "放電脚4η(T−m)(円/kW-日)"), ("chg", "充電脚4(m−B)(円/kW-日)"), ("lvl", "水準項−4(1−η)m(円/kW-日)"),
                     ("pf", "完全予見粗利(円/kW-日)"), ("TB", "TB4h(円/kWh)"), ("m", "日平均m(円/kWh)"), ("T", "上位4h平均T(円/kWh)"),
                     ("B", "下位4h平均B(円/kWh)")):
        est, se, nu = ewc_mean(h[key] - k[key])
        r[lab] = est
        r[f"{lab}_SE"] = se
        r[f"{lab}_p"] = pval(est, se, nu)
    r["EWC_ν"] = nu
    # 基準化した脚と放電脚の比率（比の差、影響関数の差に EWC）
    for lab, nh, dh, nk, dk in (("T/m", h["T"], h["m"], k["T"], k["m"]), ("B/m", h["B"], h["m"], k["B"], k["m"]),
                                ("放電脚の比率(T−m)/(T−B)", h["T"] - h["m"], h["TB"], k["T"] - k["m"], k["TB"])):
        Rh, zh = ratio_infl(nh, dh)
        Rk, zk = ratio_infl(nk, dk)
        _, se, nu = ewc_mean(zh - zk)
        r[lab] = Rh - Rk
        r[f"{lab}_SE"] = se
        r[f"{lab}_p"] = pval(Rh - Rk, se, nu)
    r["基準化した放電脚T/m−1"] = r["T/m"]
    r["基準化した充電脚1−B/m"] = -r["B/m"]
    # 完全予見粗利の比（北海道/九州）
    Q, zq = ratio_infl(h["pf"], k["pf"])
    _, se, nu = ewc_mean(zq)
    tcrit = stats.t.ppf(0.975, nu)
    r["完全予見粗利の比(北海道/九州)"] = Q
    r["完全予見粗利の比_下限95"], r["完全予見粗利の比_上限95"] = Q - tcrit * se, Q + tcrit * se
    cm = ~np.isnan(CH[mask]) & ~np.isnan(CK[mask])
    if cm.sum() > 30:
        Qc, zc = ratio_infl(CH[mask][cm], CK[mask][cm])
        _, sec, nuc = ewc_mean(zc)
        r["戦略cの比(北海道/九州)"] = Qc
        r["戦略cの比_下限95"], r["戦略cの比_上限95"] = Qc - stats.t.ppf(0.975, nuc) * sec, Qc + stats.t.ppf(0.975, nuc) * sec
    # 水準と形状の分解（期間平均の上で正確）
    mh, mk = h["m"].mean(), k["m"].mean()
    RTh, RTk = h["T"].mean() / mh, k["T"].mean() / mk
    RBh, RBk = h["B"].mean() / mh, k["B"].mean() / mk
    dm = mh - mk
    r["放電脚の差_水準の寄与"] = 4 * ETA * dm * (RTk - 1)
    r["放電脚の差_形状の寄与"] = 4 * ETA * mh * (RTh - RTk)
    r["充電脚の差_水準の寄与"] = 4 * dm * (1 - RBk)
    r["充電脚の差_形状の寄与"] = -4 * mh * (RBh - RBk)
    r["水準項の差（すべて水準）"] = -4 * (1 - ETA) * dm
    r["粗利の差_水準の寄与計"] = r["放電脚の差_水準の寄与"] + r["充電脚の差_水準の寄与"] + r["水準項の差（すべて水準）"]
    r["粗利の差_形状の寄与計"] = r["放電脚の差_形状の寄与"] + r["充電脚の差_形状の寄与"]
    assert abs(r["粗利の差_水準の寄与計"] + r["粗利の差_形状の寄与計"]
               - (r["放電脚4η(T−m)(円/kW-日)"] + r["充電脚4(m−B)(円/kW-日)"] + r["水準項−4(1−η)m(円/kW-日)"])) < 1e-9
    # 判定（p<0.10 で北海道が上回るか）
    r["判定_放電脚の円額で北海道が上回る"] = bool(r["放電脚4η(T−m)(円/kW-日)"] > 0 and r["放電脚4η(T−m)(円/kW-日)_p"] < 0.10)
    r["判定_基準化した放電脚で北海道が上回る"] = bool(r["T/m"] > 0 and r["T/m_p"] < 0.10)
    r["判定_放電脚の比率で北海道が上回る"] = bool(r["放電脚の比率(T−m)/(T−B)"] > 0 and r["放電脚の比率(T−m)/(T−B)_p"] < 0.10)
    r["判定_基準化した充電脚で九州が上回る"] = bool(r["B/m"] > 0 and r["B/m_p"] < 0.10)
    return r


def share_vs_half(L, mask):
    """エリア内の放電脚の比率 S と、S=0.5（両脚が半々）の検定"""
    S, z = ratio_infl((L["T"] - L["m"])[mask], L["TB"][mask])
    _, se, nu = ewc_mean(z)
    return S, se, pval(S - 0.5, se, nu)


PERIODS = [("FY2016〜22", FYC <= 2022), ("FY2016〜21", FYC <= 2021), ("FY2023〜25", (FYC >= 2023) & (FYC <= 2025))]
PERIODS += [(f"FY{y}", FYC == y) for y in range(2016, 2026)]
PERIODS += [("FY2026（4〜6月）", FYC == 2026)]
leg_rows = []
for plab, pm in PERIODS:
    for slab in ["通年"] + SEASONS:
        mask = pm if slab == "通年" else (pm & (RSC == slab))
        if mask.sum() < 30:
            continue
        annual_ok = slab == "通年" and full_fy(mask)
        base = {"期間": plab, "季節": slab}
        for area, L, c in (("北海道", LH, CH), ("九州", LK, CK)):
            r = area_row(L, c, mask, annual_ok)
            S, se, p = share_vs_half(L, mask)
            r["放電脚の比率_SE"], r["放電脚の比率=0.5の p"] = se, p
            leg_rows.append({**base, "区分": area, **r})
        leg_rows.append({**base, "区分": "差（北海道−九州）", **diff_row(mask)})
LEGS = pd.DataFrame(leg_rows)
LEGS.to_csv(os.path.join(PROC, "legs_hokkaido_kyushu.csv"), index=False, encoding="utf-8-sig")

# 窓の時刻分布（時刻別、h/日）
win_rows = []
for plab, pm in [p for p in PERIODS if p[0] in ("FY2016〜22", "FY2023〜25")]:
    for slab in ["通年"] + SEASONS:
        mask = pm if slab == "通年" else (pm & (RSC == slab))
        for area, L in (("北海道", LH), ("九州", LK)):
            for leg, key in (("充電（下位4h）", "wc"), ("放電（上位4h）", "wd")):
                v = L[key][mask].mean(0)
                win_rows.append({"期間": plab, "季節": slab, "エリア": area, "窓": leg, **{f"{hh}時": v[hh] for hh in range(24)}})
pd.DataFrame(win_rows).to_csv(os.path.join(PROC, "legs_window_hours.csv"), index=False, encoding="utf-8-sig")

show_cols = ["日数", "日平均m(円/kWh)", "上位4h平均T(円/kWh)", "下位4h平均B(円/kWh)", "放電脚4η(T−m)(円/kW-日)", "充電脚4(m−B)(円/kW-日)",
             "水準項−4(1−η)m(円/kW-日)", "完全予見粗利(円/kW-日)", "T/m", "B/m", "放電脚の比率(T−m)/(T−B)", "放電脚の比率=0.5の p",
             "完全予見粗利(円/kW-年、年度合計の平均)", "戦略c(円/kW-年、年度合計の平均)", "capture_c", "B≤0.5円の日の比率"]
print("\n[A1] エリア別（主要期間・季節）")
_m = LEGS["区分"] != "差（北海道−九州）"
_sel = LEGS["期間"].isin(["FY2016〜22", "FY2023〜25"])
print(LEGS[_m & _sel][["期間", "季節", "区分"] + show_cols].round(3).to_string(index=False))
print("\n[A2] 差（北海道−九州）と EWC の p、水準／形状の分解（円/kW-日）")
dcols = ["日数", "放電脚4η(T−m)(円/kW-日)", "放電脚4η(T−m)(円/kW-日)_p", "充電脚4(m−B)(円/kW-日)", "充電脚4(m−B)(円/kW-日)_p",
         "水準項−4(1−η)m(円/kW-日)", "完全予見粗利(円/kW-日)", "完全予見粗利(円/kW-日)_p", "T/m", "T/m_p", "B/m", "B/m_p",
         "放電脚の比率(T−m)/(T−B)", "放電脚の比率(T−m)/(T−B)_p", "放電脚の差_水準の寄与", "放電脚の差_形状の寄与",
         "充電脚の差_水準の寄与", "充電脚の差_形状の寄与", "粗利の差_水準の寄与計", "粗利の差_形状の寄与計",
         "完全予見粗利の比(北海道/九州)", "完全予見粗利の比_下限95", "完全予見粗利の比_上限95", "戦略cの比(北海道/九州)"]
D_ = LEGS[LEGS["区分"] == "差（北海道−九州）"]
print(D_[["期間", "季節"] + dcols].round(3).to_string(index=False))
print("\n[A3] 判定の集計（p<0.10 で北海道が上回る期間・季節。年度別×季節を含む）")
for col in ["判定_放電脚の円額で北海道が上回る", "判定_基準化した放電脚で北海道が上回る", "判定_放電脚の比率で北海道が上回る",
            "判定_基準化した充電脚で九州が上回る"]:
    hit = D_[D_[col] == True]
    print(f"  {col}: {len(hit)}/{len(D_)} 件 → " + ", ".join(f"{a}{'' if b == '通年' else '・' + b}" for a, b in zip(hit["期間"], hit["季節"])))
print("\n[A4] 完全予見の窓の時刻（h/日、FY2023〜25 通年）")
_w = LEGS[(LEGS["期間"] == "FY2023〜25") & (LEGS["季節"] == "通年") & _m]
print(_w[["区分"] + [c for c in LEGS.columns if c.startswith("充電窓_") or c.startswith("放電窓_")]].round(2).to_string(index=False))

# =====================================================================================
# B. duration 別の価値（実績価格とモデル価格、K=0）
# =====================================================================================
print("\n" + "=" * 100)
print("B. duration 別の価値（K=0）")


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
pp = n13["p"]
pp = pp[(pp["ts"] >= "2022-02-01") & (pp["ts"] < "2026-07-01")].sort_values("ts").copy()
pp["date"] = pp["ts"].dt.normalize()
pp["hour"] = pp["ts"].dt.hour


def mat(col):
    return pp.pivot_table(index="date", columns="hour", values=col).to_numpy(float)


DAYS = pd.DatetimeIndex(sorted(pp["date"].unique()))
assert (np.diff(DAYS.values).astype("timedelta64[D]").astype(int) == 1).all()
NM = len(DAYS)
NETM, PACTM = mat("net"), mat("p_hokkaido")
SEASM = np.repeat(((DAYS.month % 12) // 3).to_numpy()[:, None], 24, 1)
HOURM = np.repeat(np.arange(24)[None, :], NM, 0)
FYM = fy_of(DAYS)
WKM = np.asarray(DAYS.dayofweek >= 5)
MU26 = n26["ADJ"].reindex(pd.MultiIndex.from_arrays([SEASM.ravel(), HOURM.ravel()])).fillna(0).to_numpy().reshape(SEASM.shape)
G26 = n26["G"]


def g_curve(net, G, seas):
    out = np.empty_like(net, dtype=float)
    for s in range(4):
        m = seas == s
        x, y = G[s]
        out[m] = np.interp(net[m], x, y, left=FLOOR, right=y[-1])
    return np.maximum(out, FLOOR)


def price_A(net, MU, theta, seas):
    base = np.maximum(g_curve(net, G26, seas) + MU, FLOOR)
    return np.maximum(FLOOR + theta * (base - FLOOR), FLOOR)


EV = (FYM >= 2023) & (FYM <= 2025)
_e26 = n26["est"].sort_values("ts")
assert np.abs(n26["predict_A"](_e26, theta=1.0).reshape(-1, 24) - price_A(NETM[EV], MU26[EV], 1.0, SEASM[EV])).max() < 1e-9
print("価格関数: 26 の predict_A と一致（最大差 <1e-9）")


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


def annual(v, fy, mask):
    return float(pd.Series(v[mask]).groupby(fy[mask]).sum().mean())


W_M, HAS_M = make_W(WKM)
BLK = np.where((DAYS >= "2023-02-01") & (FYM <= 2025))[0]
W_B, HAS_B = make_W(WKM[BLK])
EVB, FYB = EV[BLK], FYM[BLK]
assert HAS_M[EV].all() and HAS_B[EVB].all()
assert (DAYS[BLK][EVB] == DAYS[EV]).all()


def eval_rank(P, W, h):
    """ランク法: 戦略c（休止なし）・事前休止つき・完全予見の日次粗利（円/kW-日）と気候値 C"""
    C = W @ P
    wc, wd = tie_w(C, h), tie_w(-C, h)
    c = ETA * (wd * P).sum(1) - (wc * P).sum(1)
    expm = ETA * (wd * C).sum(1) - (wc * C).sum(1)
    s = np.sort(P, 1)
    pf = np.maximum(0.0, ETA * s[:, -h:].sum(1) - s[:, :h].sum(1))
    return {"c": c, "cp": np.where(expm > 0, c, 0.0), "pf": pf, "C": C}


def dp_schedule(V, h, ncyc=1, full_only=False):
    """順序制約つきの最適スケジュール（各日0時に空・24時に空、SoC 0〜h MWh、1時間に1MWh 充電／放電、充電量 ≤ ncyc·h）。
    V は計画に使う価格 (n,24)。full_only=True なら充電量は0か ncyc·h（35 と同じ「満充電・満放電か休止」）。
    戻り値: act (n,24)（+1 充電、−1 放電、0 休止）"""
    n = V.shape[0]
    N = ncyc * h
    NEG = -1e18
    val = np.full((n, h + 1, N + 1), NEG)
    val[:, 0, 0] = 0.0
    choice = np.zeros((n, 24, h + 1, N + 1), np.int8)
    for t in range(24):
        p = V[:, t][:, None, None]
        idle = val
        chg = np.full_like(val, NEG)
        chg[:, 1:, 1:] = val[:, :-1, :-1] - p
        dis = np.full_like(val, NEG)
        dis[:, :-1, :] = val[:, 1:, :] + ETA * p
        stack = np.stack([idle, chg, dis])
        ch = stack.argmax(0)                               # 同値は休止を優先
        val = np.take_along_axis(stack, ch[None], 0)[0]
        val[val < NEG / 2] = NEG
        choice[:, t] = ch
    endv = val[:, 0, :]
    if full_only:
        endv = np.where(np.isin(np.arange(N + 1), [0, N])[None, :], endv, NEG)
    nstar = endv.argmax(1)
    act = np.zeros((n, 24), np.int8)
    s = np.zeros(n, int)
    k = nstar.copy()
    r = np.arange(n)
    for t in range(23, -1, -1):
        ch = choice[r, t, s, k]
        act[:, t] = np.where(ch == 1, 1, np.where(ch == 2, -1, 0))
        s = s - (ch == 1) + (ch == 2)
        k = k - (ch == 1)
    assert (s == 0).all() and (k == 0).all()
    return act


def realize(P, act):
    return ETA * (P * (act == -1)).sum(1) - (P * (act == 1)).sum(1), (act == 1).sum(1).astype(float)


P_MOD = {th: price_A(NETM[BLK], MU26[BLK], th, SEASM[BLK]) for th in (1.0, TH26, TH22)}
val_rows = []
DAILY = {}          # bootstrap 用の日次系列（FY2023〜25 の1,096日）
for h in HS:
    ra = eval_rank(PACTM, W_M, h)
    rm = {th: eval_rank(P_MOD[th], W_B, h) for th in P_MOD}
    row = {"h": h,
           "PF_実績": annual(ra["pf"], FYM, EV), "c_実績": annual(ra["c"], FYM, EV), "c事前休止_実績": annual(ra["cp"], FYM, EV),
           "PF_モデル(θ=1)": annual(rm[1.0]["pf"], FYB, EVB), "c_モデル(θ=1)": annual(rm[1.0]["c"], FYB, EVB),
           "c事前休止_モデル(θ=1)": annual(rm[1.0]["cp"], FYB, EVB),
           "c_モデル(θ=1.57)/(1.57·c(θ=1))": annual(rm[TH26]["c"], FYB, EVB) / (TH26 * annual(rm[1.0]["c"], FYB, EVB)),
           "c_モデル(θ=1.72)/(1.72·c(θ=1))": annual(rm[TH22]["c"], FYB, EVB) / (TH22 * annual(rm[1.0]["c"], FYB, EVB)),
           "PF_モデル(θ=1.57)/(1.57·PF(θ=1))": annual(rm[TH26]["pf"], FYB, EVB) / (TH26 * annual(rm[1.0]["pf"], FYB, EVB))}
    DAILY[h] = {"c_act": ra["c"][EV], "c_mod": rm[1.0]["c"][EVB]}
    # 順序制約（実績価格・モデル価格）
    for lab, P, C, msk, fy in (("実績", PACTM, ra["C"], EV, FYM), ("モデル(θ=1)", P_MOD[1.0], rm[1.0]["C"], EVB, FYB)):
        Pm, Cm, fm = P[msk], C[msk], fy[msk]
        one = np.ones(msk.sum(), bool)
        for full, flab in ((True, "満充放電か休止"), (False, "部分充放電可")):
            pf_o, _ = realize(Pm, dp_schedule(Pm, h, 1, full))
            c_o, q_o = realize(Pm, dp_schedule(Cm, h, 1, full))
            row[f"PF順序制約_{flab}_{lab}"] = annual(pf_o, fm, one)
            row[f"c順序制約_{flab}_{lab}"] = annual(c_o, fm, one)
            row[f"c順序制約_{flab}_{lab}_充電量(kWh/kW-年)"] = annual(q_o, fm, one)
            if lab == "実績" and not full:
                DAILY[h]["c_act_ord"] = c_o
        if h <= 4:
            pf2, q2p = realize(Pm, dp_schedule(Pm, h, 2, False))
            c2, q2 = realize(Pm, dp_schedule(Cm, h, 2, False))
            row[f"PF2サイクル_{lab}"] = annual(pf2, fm, one)
            row[f"PF2サイクル_{lab}_充電量(kWh/kW-年)"] = annual(q2p, fm, one)
            row[f"c2サイクル_{lab}"] = annual(c2, fm, one)
            row[f"c2サイクル_{lab}_充電量(kWh/kW-年)"] = annual(q2, fm, one)
    val_rows.append(row)
    print(f"  h={h}: PF 実績 {row['PF_実績']:,.0f}・モデル {row['PF_モデル(θ=1)']:,.0f}、c 実績 {row['c_実績']:,.0f}・モデル {row['c_モデル(θ=1)']:,.0f}")
DV = pd.DataFrame(val_rows).set_index("h")
LAM = DV.loc[4, "c_実績"] / DV.loc[4, "c_モデル(θ=1)"]
DV["capture_c_実績"] = DV["c_実績"] / DV["PF_実績"]
DV["capture_c_モデル"] = DV["c_モデル(θ=1)"] / DV["PF_モデル(θ=1)"]
DV["λ（4時間で校正）"] = LAM
DV["λ_h（h別、実績c/モデルc）"] = DV["c_実績"] / DV["c_モデル(θ=1)"]
DV["a_実績整合(=λ·c_モデル)"] = LAM * DV["c_モデル(θ=1)"]
DV["充電従量(円/kW-年)"] = WHEEL_KWH * DV.index.to_numpy() * 365
DV["π_c(0)_実績整合(=a−充電従量)"] = DV["a_実績整合(=λ·c_モデル)"] - DV["充電従量(円/kW-年)"]
DV["π_c(0)_モデル直値"] = DV["c_モデル(θ=1)"] - DV["充電従量(円/kW-年)"]
DV["π_旧0.81PF"] = CAPTURE_OLD * DV["PF_モデル(θ=1)"] - DV["充電従量(円/kW-年)"]
DV["PF_実績/PF_実績(4h)"] = DV["PF_実績"] / DV.loc[4, "PF_実績"]
DV["c_実績/c_実績(4h)"] = DV["c_実績"] / DV.loc[4, "c_実績"]
DV["a_実績整合/a(4h)"] = DV["a_実績整合(=λ·c_モデル)"] / DV.loc[4, "a_実績整合(=λ·c_モデル)"]
# 検算: 41 と監査の値（4h: 実績 c 8,427・PF 10,317、モデル c 7,602・PF 8,265、λ 1.1085、モデル PF 2h 4,721）
assert abs(DV.loc[4, "c_実績"] - 8427.2) < 1 and abs(DV.loc[4, "PF_実績"] - 10317.5) < 1
assert abs(DV.loc[4, "c_モデル(θ=1)"] - 7602.4) < 1 and abs(DV.loc[4, "PF_モデル(θ=1)"] - 8265.5) < 1
assert abs(DV.loc[2, "PF_モデル(θ=1)"] - 4721.1) < 1 and abs(LAM - 1.1085) < 1e-3
print(f"検算: 41 の c（実績8,427・モデル7,602）・PF（10,317・8,265）、λ={LAM:.4f}、38 の2時間 PF 4,721 と一致")
DV.reset_index().round(4).to_csv(os.path.join(PROC, "duration_value_v3.csv"), index=False, encoding="utf-8-sig")
print(DV[["PF_実績", "c_実績", "capture_c_実績", "PF_モデル(θ=1)", "c_モデル(θ=1)", "capture_c_モデル", "λ_h（h別、実績c/モデルc）",
          "a_実績整合(=λ·c_モデル)", "a_実績整合/a(4h)", "π_c(0)_実績整合(=a−充電従量)", "π_c(0)_モデル直値", "π_旧0.81PF",
          "c_モデル(θ=1.57)/(1.57·c(θ=1))", "c_モデル(θ=1.72)/(1.72·c(θ=1))"]].round(4).to_string())
print("順序制約・2サイクル（円/kW-年）:")
print(DV[[c for c in DV.columns if ("順序制約" in c or "2サイクル" in c) and "充電量" not in c]].round(0).to_string())

# =====================================================================================
# C. 費用と θ*
# =====================================================================================
print("\n" + "=" * 100)
print("C. duration 別の θ*（静学、K=0）")


def crf(r, n=20):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


_cx = pd.read_csv(os.path.join(PROC, "battery_capex_series.csv"))
_c24 = _cx[(_cx["category"] == "grid_by_fy") & (_cx["fy_or_bin"].astype(str) == "2024")].iloc[0]
assert abs(_c24["total_man_yen_kwh"] - 6.8) < 1e-9
SHARES = {"kWh比例のみ（kW部分0）": 0.0,
          "PCSのみkW（8.8%）": _c24["pcs_man_yen_kwh"] / _c24["total_man_yen_kwh"],
          "PCS＋その他・工事費の半分をkW（主、24.3%）": (_c24["pcs_man_yen_kwh"] + 0.5 * (_c24["other_man_yen_kwh"] + _c24["construction_man_yen_kwh"]))
          / _c24["total_man_yen_kwh"],
          "電池以外すべてkW（39.7%）": 1 - _c24["battery_man_yen_kwh"] / _c24["total_man_yen_kwh"]}
SH_MAIN = "PCS＋その他・工事費の半分をkW（主、24.3%）"
_cc = pd.read_csv(os.path.join(PROC, "capacity_adjustment_coefficients.csv"))
_k = _cc[(_cc["category"] == "純揚水・蓄電池") & (_cc["area"] == "北海道") & (_cc["file"] == "2029_chouseikeisu") & (_cc["month"] != "年間")]
KAPPA = {h: _k[_k["duration"] == f"{h}h"]["coef_pct"].mean() / 100 for h in HS if h >= 3}
KAPPA[2] = 0.0
KP4 = 12_500.0
CAP_CASES = {"2029年度向け（主）": {h: KP4 * KAPPA[h] / KAPPA[4] for h in HS},
             "容量収入0": {h: 0.0 for h in HS},
             "2026年度向け約定8,749円×κ(h)": {h: 8_749.0 * KAPPA[h] for h in HS},
             "2時間を出力2/3で3時間として応札（参考）": {h: (KP4 * (2 / 3) * KAPPA[3] / KAPPA[4] if h == 2 else KP4 * KAPPA[h] / KAPPA[4]) for h in HS}}
print("調整係数 κ(h)（2029年度向け北海道、月平均）:", {h: round(KAPPA[h], 4) for h in HS})
_ro = pd.read_csv(os.path.join(PROC, "real_option_short_duration.csv"))
if "収入の基準" not in _ro.columns:                     # 38 の版により収入の基準の列がない
    _ro["収入の基準"] = "旧0.81PF"
_ro["key"] = _ro["収入の基準"].astype(str) + "|" + _ro["項目"].str.split(": ").str[0]
_st = _ro[(_ro["区分"] == "静学閾値") & _ro["項目"].str.contains("θ\\*（WACC6%）", regex=True)].set_index("key")["値"]
RATIO_C = {}
for sig in ("0.10", "0.30"):
    d_ = _ro[(_ro["区分"] == "動学閾値") & _ro["項目"].str.contains(f"θ_c 競争均衡（σ={sig}", regex=False)]
    rr = [float(v) / float(_st[k_]) for k_, v in zip(d_["key"], d_["値"])]
    assert len(rr) >= 6 and np.ptp(rr) < 2e-3, rr                # 仕様・収入の基準によらず一定であることを確かめる
    RATIO_C[sig] = float(np.mean(rr))
_pl = pd.read_csv(os.path.join(PROC, "real_option_price_level.csv"))
XI_NOW = float(_pl[(_pl["ブロック"] == "2因子分解") & (_pl["系列"] == "システムプライス代理") & (_pl["標本"] == "全期間 2016-04〜2026-06")
                   & (_pl["項目"] == "ξ 期末（2026-06 または標本末、フィルタ）")]["値"].iloc[0])
print(f"恒久成分の推定値 ξ（38、2026-06）= {XI_NOW:.4f}")
print("38 の θ_c/θ*（6仕様で一定）:", {k: round(v, 4) for k, v in RATIO_C.items()})

A_BASES = {"実績整合（主、λ=4時間で校正）": {h: LAM * DV.loc[h, "c_モデル(θ=1)"] for h in HS},
           "実績整合（h別の λ_h＝実績c(h)）": {h: DV.loc[h, "c_実績"] for h in HS},
           "モデル直値": {h: DV.loc[h, "c_モデル(θ=1)"] for h in HS},
           "旧0.81×PF_モデル": {h: CAPTURE_OLD * DV.loc[h, "PF_モデル(θ=1)"] for h in HS},
           "実績価格・順序制約つき戦略c（部分充放電可）": {h: DV.loc[h, "c順序制約_部分充放電可_実績"] for h in HS},
           "実績価格・2サイクル戦略c（h≤4）": {h: DV.loc[h, "c2サイクル_実績"] for h in HS if h <= 4}}
WHEEL_BASE = {"実績価格・順序制約つき戦略c（部分充放電可）": {h: WHEEL_KWH * DV.loc[h, "c順序制約_部分充放電可_実績_充電量(kWh/kW-年)"] for h in HS},
              "実績価格・2サイクル戦略c（h≤4）": {h: WHEEL_KWH * DV.loc[h, "c2サイクル_実績_充電量(kWh/kW-年)"] for h in HS if h <= 4}}
CAPEXES = [6.8, 6.0, 4.0, 2.3]
WACCS = [0.06, 0.08]


def cost_parts(h, capex4, s, wacc, kp, wheel):
    I4 = 4 * capex4 * 1e4
    cP, cE = s * I4, (1 - s) * I4 / 4
    I = cE * h + cP
    om = 5_000.0 + 300.0 * I / I4
    need = I * crf(wacc) + om + 6_900.0 - kp + wheel
    return I, cE, cP, om, need


ts_rows = []
for base, A in A_BASES.items():
    for capex4 in CAPEXES:
        for slab, s in SHARES.items():
            for wacc in WACCS:
                for clab, KP in CAP_CASES.items():
                    if base != "実績整合（主、λ=4時間で校正）" and not (wacc == 0.06 and clab == "2029年度向け（主）"):
                        continue
                    hs = [h for h in HS if h in A]
                    rec = {}
                    for h in hs:
                        wheel = WHEEL_BASE.get(base, {}).get(h, WHEEL_KWH * h * 365)
                        I, cE, cP, om, need = cost_parts(h, capex4, s, wacc, KP[h], wheel)
                        rec[h] = (need, A[h], I, cE, cP, om, wheel, KP[h])
                    th = {h: rec[h][0] / rec[h][1] for h in hs}
                    hmin = min(th, key=th.get)
                    for h in hs:
                        need, a, I, cE, cP, om, wheel, kp = rec[h]
                        r = {"収益の基準": base, "資本費(万円/kWh、4時間換算)": capex4, "kW部分の比率": slab, "kW比率s": s, "WACC": wacc,
                             "容量収入": clab, "h": h, "資本費I(h)(円/kW)": I, "c_E(円/kWh)": cE, "c_P(円/kW)": cP,
                             "資本費年額(円/kW-年)": I * crf(wacc), "運維・廃止(円/kW-年)": om, "託送等固定(円/kW-年)": 6_900.0,
                             "κP(h)(円/kW-年)": kp, "充電従量(円/kW-年)": wheel, "必要粗収益need(円/kW-年)": need,
                             "粗収益a(θ=1)(円/kW-年)": a, "θ*（静学）": th[h],
                             "θ_c近似（σ=0.10）": th[h] * RATIO_C["0.10"], "θ_c近似（σ=0.30）": th[h] * RATIO_C["0.30"],
                             "θ*/θ*(4h)": th[h] / th[4] if 4 in th else np.nan, "θ*最小のh": hmin, "4時間が最小": hmin == 4}
                        if 4 in rec and h != 4:
                            dn, da = need - rec[4][0], a - rec[4][1]
                            r["θ_sw（hの年額NPVが4時間を上回るθ）"] = dn / da if da != 0 else np.nan
                            r["θ_swの向き"] = "θ_sw より上で h が有利" if da > 0 else "θ_sw より下で h が有利"
                            r["Δa(h−4)(円/kW-年)"] = da
                            r["Δneed(h−4)(円/kW-年)"] = dn
                        ts_rows.append(r)
TSD = pd.DataFrame(ts_rows)

# λ のブートストラップ（主の基準・費用の主ケース。日次の組の定常ブートストラップ）
n_ev = int(EV.sum())
B_BOOT, LBLK = 2000, 20


def stationary_idx(n, L, rg):
    idx = np.empty(n, int)
    idx[0] = rg.integers(n)
    for t in range(1, n):
        idx[t] = rg.integers(n) if rg.random() < 1 / L else (idx[t - 1] + 1) % n
    return idx


boot = {h: [] for h in HS}
boot_h = {h: [] for h in HS}
for b in range(B_BOOT):
    ix = stationary_idx(n_ev, LBLK, rng)
    lam_b = DAILY[4]["c_act"][ix].sum() / DAILY[4]["c_mod"][ix].sum()
    for h in HS:
        boot[h].append(lam_b * DAILY[h]["c_mod"][ix].sum() / 3)
        boot_h[h].append(DAILY[h]["c_act"][ix].sum() / 3)
boot = {h: np.array(v) for h, v in boot.items()}
boot_h = {h: np.array(v) for h, v in boot_h.items()}
bs_rows = []
for capex4 in CAPEXES:
    for slab, s in SHARES.items():
        for blab, BB in (("実績整合（主、λ=4時間で校正）", boot), ("実績整合（h別の λ_h＝実績c(h)）", boot_h)):
            need = {h: cost_parts(h, capex4, s, 0.06, CAP_CASES["2029年度向け（主）"][h], WHEEL_KWH * h * 365)[4] for h in HS}
            thb = {h: need[h] / BB[h] for h in HS}
            for h in HS:
                bs_rows.append({"収益の基準": blab, "資本費(万円/kWh、4時間換算)": capex4, "kW部分の比率": slab, "WACC": 0.06,
                                "容量収入": "2029年度向け（主）", "h": h,
                                "θ*_下限95": np.quantile(thb[h], 0.025), "θ*_上限95": np.quantile(thb[h], 0.975),
                                "θ*(h)−θ*(4)_下限95": np.quantile(thb[h] - thb[4], 0.025),
                                "θ*(h)−θ*(4)_上限95": np.quantile(thb[h] - thb[4], 0.975),
                                "θ*(h)<θ*(4) の割合": float((thb[h] < thb[4]).mean()) if h != 4 else np.nan})
BS = pd.DataFrame(bs_rows)
TSD = TSD.merge(BS, on=["収益の基準", "資本費(万円/kWh、4時間換算)", "kW部分の比率", "WACC", "容量収入", "h"], how="left")

# 4時間が θ* 最小となる資本費の範囲（主の基準・容量の主ケース・WACC 6%、資本費 1.0〜12.0万円/kWh を0.01刻み）
rng_rows = []
grid = np.round(np.arange(1.0, 12.0001, 0.01), 2)
for slab, s in SHARES.items():
    for clab in ("2029年度向け（主）", "容量収入0", "2026年度向け約定8,749円×κ(h)"):
        arg = []
        for cx in grid:
            th = {h: cost_parts(h, cx, s, 0.06, CAP_CASES[clab][h], WHEEL_KWH * h * 365)[4] / A_BASES["実績整合（主、λ=4時間で校正）"][h] for h in HS}
            arg.append(min(th, key=th.get))
        arg = np.array(arg)
        segs = []
        start = 0
        for i in range(1, len(grid) + 1):
            if i == len(grid) or arg[i] != arg[start]:
                segs.append(f"{grid[start]:.2f}〜{grid[i - 1]:.2f}: {arg[start]}h")
                start = i
        four = grid[arg == 4]
        rng_rows.append({"収益の基準": "実績整合（主、λ=4時間で校正）", "kW部分の比率": slab, "容量収入": clab, "WACC": 0.06,
                         "4時間が最小の資本費_下限(万円/kWh)": four.min() if len(four) else np.nan,
                         "4時間が最小の資本費_上限(万円/kWh)": four.max() if len(four) else np.nan,
                         "θ*最小のhの区間（資本費1〜12万円/kWh）": " / ".join(segs)})
RNG_ = pd.DataFrame(rng_rows)
# 表8.16 の改訂案（実績の戦略c(h)、WACC 6%。θ_c は 38 の比、年数は 38 と同じ式: 恒久成分の水準 ξ でのスポット収入に
# 追加収入 R が続くとき静学 NPV が0になる年数 T、annuity(T)=−NPV/R）
def annuity(r, n=20):
    return (1 - (1 + r) ** -n) / r


t816 = []
for capex4 in (6.8, 4.0):
    for h, clab in ((2, "容量収入0"), (3, "2029年度向け（主）"), (4, "2029年度向け（主）"), (4, "容量収入0"), (5, "2029年度向け（主）"),
                    (6, "2029年度向け（主）"), (8, "2029年度向け（主）")):
        a = A_BASES["実績整合（h別の λ_h＝実績c(h)）"][h]
        r = {"仕様": f"{h}時間" + ("（容量収入0）" if (clab == "容量収入0" and h != 2) else ""), "h": h, "資本費(万円/kWh、4時間換算)": capex4,
             "実効容量収入(円/kW-年)": CAP_CASES[clab][h], "戦略c(h)(実績、円/kW-年)": a, "完全予見粗利PF(h)(実績、円/kW-年)": DV.loc[h, "PF_実績"]}
        for slab, s_ in SHARES.items():
            I, cE, cP, om, need = cost_parts(h, capex4, s_, 0.06, CAP_CASES[clab][h], WHEEL_KWH * h * 365)
            r[f"θ*（{slab}）"] = need / a
            if slab in ("kWh比例のみ（kW部分0）", SH_MAIN):
                tag = "kWh比例" if s_ == 0 else "kW24.3%"
                r[f"θ_c σ=0.10（{tag}）"] = need / a * RATIO_C["0.10"]
                r[f"θ_c σ=0.30（{tag}）"] = need / a * RATIO_C["0.30"]
                npv = (a * XI_NOW - (om + 6_900.0 + WHEEL_KWH * h * 365 - CAP_CASES[clab][h])) * annuity(0.06) - I
                for R in (30_000, 40_000):
                    q = 0.06 * max(0.0, -npv) / R
                    r[f"NPV0の年数・追加{R // 10_000}万円（{tag}）"] = -np.log(1 - q) / np.log(1.06) if q < 1 else np.inf
            if h == 2:                                   # 表注の参考値（表と同じ収益の基準＝実績の c(2h)）
                kp23 = CAP_CASES["2時間を出力2/3で3時間として応札（参考）"][2]
                r[f"θ*（2時間を出力2/3で3時間として応札、参考）（{slab}）"] = cost_parts(2, capex4, s_, 0.06, kp23, WHEEL_KWH * 2 * 365)[4] / a
            if h == 6 and clab == "2029年度向け（主）":   # 6時間が4時間を上回る θ（表と同じ収益の基準）
                need4 = cost_parts(4, capex4, s_, 0.06, CAP_CASES[clab][4], WHEEL_KWH * 4 * 365)[4]
                need6 = cost_parts(6, capex4, s_, 0.06, CAP_CASES[clab][6], WHEEL_KWH * 6 * 365)[4]
                r[f"θ_sw 6時間が4時間を上回るθ（{slab}）"] = (need6 - need4) / (a - A_BASES["実績整合（h別の λ_h＝実績c(h)）"][4])
        t816.append(r)
T816 = pd.DataFrame(t816)
print("\n[D] 表8.16 の改訂案（実績の戦略c(h)、WACC 6%）")
print(T816.round(2).to_string(index=False))

# 検証で追加（表注・本文の数値の裏付け）: (i) θ*(4) から duration を選び直したときの最大の低下、(ii) 主の基準と h別 λ_h の θ* の差
red_rows = []
for (base, clab, wacc), g_ in TSD.groupby(["収益の基準", "容量収入", "WACC"], sort=False):
    best = None
    for (cx, slab), gg in g_.groupby(["資本費(万円/kWh、4時間換算)", "kW部分の比率"], sort=False):
        th_ = gg.set_index("h")["θ*（静学）"]
        if 4 not in th_.index:
            continue
        rel, ab = 1 - th_.min() / th_[4], th_[4] - th_.min()
        if best is None or rel > best[0]:
            best = (rel, ab, cx, slab, int(th_.idxmin()), th_.min(), th_[4])
    red_rows.append({"区分": "4時間からの最大低下", "収益の基準": base, "容量収入": clab, "WACC": wacc,
                     "最大低下率 1−minθ*/θ*(4)": best[0], "そのときの差 θ*(4)−minθ*": best[1], "資本費(万円/kWh、4時間換算)": best[2],
                     "kW部分の比率": best[3], "θ*最小のh": best[4], "minθ*": best[5], "θ*(4h)": best[6]})
_mm = TSD[(TSD["収益の基準"] == "実績整合（主、λ=4時間で校正）") & (TSD["WACC"] == 0.06) & (TSD["容量収入"] == "2029年度向け（主）")]
_hh = TSD[TSD["収益の基準"] == "実績整合（h別の λ_h＝実績c(h)）"]
_dd = _mm.merge(_hh, on=["資本費(万円/kWh、4時間換算)", "kW部分の比率", "h"], suffixes=("_主", "_h別"))
for (cx, slab), g_ in _dd.groupby(["資本費(万円/kWh、4時間換算)", "kW部分の比率"], sort=False):
    dif = (g_["θ*（静学）_主"] - g_["θ*（静学）_h別"]).abs()
    red_rows.append({"区分": "主の基準とh別λ_hのθ*の差", "収益の基準": "主−h別", "容量収入": "2029年度向け（主）", "WACC": 0.06,
                     "資本費(万円/kWh、4時間換算)": cx, "kW部分の比率": slab, "|θ*主−θ*h別|の最大": dif.max(),
                     "そのときのh": int(g_.loc[dif.idxmax(), "h"])})
RED = pd.DataFrame(red_rows)
print("\n[E] 4時間からの最大低下（収益の基準×容量×WACC、資本費・kW比率の全組合せのうち最大）と、主の基準と h別 λ_h の差")
print(RED.round(4).to_string(index=False))
OUT_TS = pd.concat([TSD.assign(区分="θ*"), RNG_.assign(区分="4時間が最小となる資本費の範囲"), T816.assign(区分="表8.16改訂案"), RED],
                   ignore_index=True)
OUT_TS.round(4).to_csv(os.path.join(PROC, "duration_theta_star_v3.csv"), index=False, encoding="utf-8-sig")

# 表示
MAINB = "実績整合（主、λ=4時間で校正）"
m0 = (TSD["収益の基準"] == MAINB) & (TSD["WACC"] == 0.06) & (TSD["容量収入"] == "2029年度向け（主）")
print("[C1] θ*（主の基準、WACC 6%、容量2029年度向け）: 行=資本費×kW比率、列=h")
print(TSD[m0].pivot_table(index=["資本費(万円/kWh、4時間換算)", "kW部分の比率"], columns="h", values="θ*（静学）", sort=False).round(2).to_string())
print("\n[C2] 費用の内訳（主: 資本費6.8・kW比率24.3%・WACC6%・容量2029）")
_c2 = TSD[m0 & (TSD["資本費(万円/kWh、4時間換算)"] == 6.8) & (TSD["kW部分の比率"] == SH_MAIN)]
print(_c2[["h", "資本費I(h)(円/kW)", "資本費年額(円/kW-年)", "運維・廃止(円/kW-年)", "κP(h)(円/kW-年)", "充電従量(円/kW-年)",
           "必要粗収益need(円/kW-年)", "粗収益a(θ=1)(円/kW-年)", "θ*（静学）", "θ_c近似（σ=0.10）", "θ_c近似（σ=0.30）",
           "θ_sw（hの年額NPVが4時間を上回るθ）", "θ*_下限95", "θ*_上限95", "θ*(h)<θ*(4) の割合"]].round(3).to_string(index=False))
print("\n[C3] 4時間が θ* 最小か（すべての組合せ）:")
for base in A_BASES:
    sub = TSD[(TSD["収益の基準"] == base) & (TSD["h"] == 4)]
    bad = sub[~sub["4時間が最小"]]
    print(f"  {base}: {len(sub) - len(bad)}/{len(sub)} で4時間が最小" + ("" if bad.empty else " ／ 例外: " + "; ".join(
        f"資本費{r['資本費(万円/kWh、4時間換算)']}・{r['kW部分の比率']}・WACC{r['WACC']:.0%}・{r['容量収入']} → {r['θ*最小のh']}h" for _, r in bad.iterrows())))
print("\n[C4] 4時間が最小となる資本費の範囲（主の基準、WACC 6%）")
print(RNG_.to_string(index=False))
print("\n[C5] 2時間・6時間の比較（主の基準、WACC 6%）: 資本費×kW比率×容量")
_c5 = TSD[(TSD["収益の基準"] == MAINB) & (TSD["WACC"] == 0.06) & TSD["h"].isin([2, 3, 4, 6, 8])]
print(_c5.pivot_table(index=["容量収入", "資本費(万円/kWh、4時間換算)", "kW部分の比率"], columns="h", values="θ*（静学）", sort=False).round(2).to_string())
print("\n[C6] 他の収益の基準（WACC 6%、容量2029、kW比率は主と0）")
_c6 = TSD[(TSD["WACC"] == 0.06) & (TSD["容量収入"] == "2029年度向け（主）") & TSD["kW部分の比率"].isin([SH_MAIN, "kWh比例のみ（kW部分0）"])]
print(_c6.pivot_table(index=["収益の基準", "資本費(万円/kWh、4時間換算)", "kW部分の比率"], columns="h", values="θ*（静学）", sort=False).round(2).to_string())
# 4→6時間の限界収入と限界費用（主: θ=1）
for slab in (SH_MAIN, "kWh比例のみ（kW部分0）", "電池以外すべてkW（39.7%）"):
    r4 = TSD[m0 & (TSD["資本費(万円/kWh、4時間換算)"] == 6.8) & (TSD["kW部分の比率"] == slab) & (TSD["h"] == 4)].iloc[0]
    r6 = TSD[m0 & (TSD["資本費(万円/kWh、4時間換算)"] == 6.8) & (TSD["kW部分の比率"] == slab) & (TSD["h"] == 6)].iloc[0]
    mr = (r6["粗収益a(θ=1)(円/kW-年)"] - r4["粗収益a(θ=1)(円/kW-年)"]) + (r6["κP(h)(円/kW-年)"] - r4["κP(h)(円/kW-年)"])
    mc = (r6["資本費年額(円/kW-年)"] - r4["資本費年額(円/kW-年)"]) + (r6["運維・廃止(円/kW-年)"] - r4["運維・廃止(円/kW-年)"]) \
        + (r6["充電従量(円/kW-年)"] - r4["充電従量(円/kW-年)"])
    print(f"  4→6時間（資本費6.8、{slab}）: 限界収入 {mr:,.0f}（スポット {r6['粗収益a(θ=1)(円/kW-年)'] - r4['粗収益a(θ=1)(円/kW-年)']:,.0f}"
          f"＋容量 {r6['κP(h)(円/kW-年)'] - r4['κP(h)(円/kW-年)']:,.0f}）、限界費用 {mc:,.0f}、θ_sw={r6['θ_sw（hの年額NPVが4時間を上回るθ）']:.2f}")

# =====================================================================================
# 図
# =====================================================================================
C_H, C_K = "#2a78d6", "#eb6834"
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、2つのパネルを縦に並べ、文字は8.5pt 以上にする。
# 基準化の方法、kW 部分の比率（線24.3%、帯0〜39.7%）、K=0・静学・割引率6% は図の注に書く
fig, axes = plt.subplots(2, 1, figsize=(6.1, 7.4), gridspec_kw={"height_ratios": [1.1, 1.0]}, layout="constrained")


def style(ax):
    for sp_ in ("top", "right"):
        ax.spines[sp_].set_visible(False)
    for sp_ in ("left", "bottom"):
        ax.spines[sp_].set_color("#b9b8b3")
    ax.tick_params(colors=GRAY, labelsize=8.5)
    ax.grid(axis="y", color="#e4e3df", lw=0.8)
    ax.set_axisbelow(True)


ax = axes[0]
style(ax)
grp = [("FY2016〜22", "通年"), ("FY2023〜25", "通年"), ("FY2023〜25", "夏"), ("FY2023〜25", "冬"), ("FY2023〜25", "不需要期")]
x = np.arange(len(grp))
wdt = 0.19
for j, (area, col) in enumerate((("北海道", C_H), ("九州", C_K))):
    vT = [LEGS[(LEGS["期間"] == p) & (LEGS["季節"] == s) & (LEGS["区分"] == area)]["基準化した放電脚T/m−1"].iloc[0] for p, s in grp]
    vB = [LEGS[(LEGS["期間"] == p) & (LEGS["季節"] == s) & (LEGS["区分"] == area)]["基準化した充電脚1−B/m"].iloc[0] for p, s in grp]
    ax.bar(x - 1.5 * wdt + j * wdt, vT, wdt, color=col, label=f"{area} 放電脚 $T/m-1$")
    ax.bar(x + 0.5 * wdt + j * wdt, vB, wdt, color=col, alpha=0.45, hatch="//", edgecolor="white", label=f"{area} 充電脚 $1-B/m$")
_q = [LEGS[(LEGS["期間"] == p) & (LEGS["季節"] == s) & (LEGS["区分"] == "差（北海道−九州）")]["完全予見粗利の比(北海道/九州)"].iloc[0]
      for p, s in grp]
ax.set_xticks(x)
ax.set_xticklabels([f"{p}\n{s}\n完全予見粗利の比\n{q:.2f}" for (p, s), q in zip(grp, _q)], fontsize=8.5)
ax.set_ylim(0, 0.85)
ax.set_ylabel("日平均で基準化した\nプレミアム／ディスカウント", color=GRAY, fontsize=9)
ax.legend(frameon=False, fontsize=8.5, ncol=2, loc="upper center", columnspacing=1.5)
ax.set_title("(a) 放電脚 $T/m-1$ と充電脚 $1-B/m$", loc="left", fontsize=9.5)
ax = axes[1]
style(ax)
for capex4, ls in ((6.8, "-"), (4.0, "--"), (2.3, ":")):
    sub = TSD[m0 & (TSD["資本費(万円/kWh、4時間換算)"] == capex4)]
    mid = sub[sub["kW部分の比率"] == SH_MAIN].sort_values("h")
    lo = sub.groupby("h")["θ*（静学）"].min()
    hi = sub.groupby("h")["θ*（静学）"].max()
    ax.fill_between(lo.index, lo.values, hi.values, color=C_H, alpha=0.10)
    ax.plot(mid["h"], mid["θ*（静学）"], ls, color=C_H, marker="o", ms=3.5, lw=1.4, label=f"資本費 {capex4}万円/kWh（4時間換算）")
for yv in (TH26, TH22):
    ax.axhline(yv, color="#8a8986", lw=0.8, ls="-.")
ax.plot([], [], color="#8a8986", lw=0.8, ls="-.", label=f"価格水準：FY2022（{TH22:.2f}）、FY2026上期（{TH26:.2f}）")
ax.set_xlabel("duration（時間）", color=GRAY, fontsize=9)
ax.set_ylabel("参入が開く価格水準係数 θ*", color=GRAY, fontsize=9)
ax.set_xticks(HS)
ax.legend(frameon=False, fontsize=8.5, loc="upper right", handlelength=2.2)
ax.set_title("(b) duration 別の θ*", loc="left", fontsize=9.5)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "duration_legs.png"), dpi=300)
print("\n出力: legs_hokkaido_kyushu.csv, legs_window_hours.csv, duration_value_v3.csv, duration_theta_star_v3.csv, figures/hokkaido/duration_legs.png")
