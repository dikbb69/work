#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""マーチャント4h蓄電池の多因子 Cash-Flow-at-Risk と、上場先物によるヘッジ有効性・市場の非完備（北海道）

手法:
  (A) 年次エクスポージャー（Andrén, Jankensgård & Oxelheim 2005 の exposure-based CFaR の第1段）
      FY2016〜25 の年度別完全予見粗利（4h・η0.85・1日1サイクル・負の日は休止。analysis/03・16 と同一仕様）を、
      価格水準 θ の代理（年平均システムプライスの FY2023〜25 平均比。北海道エリアプライス比も併記）に対数で回帰し、
      log PF = log θ + log S と分けたときの分散分解（水準 θ と年度単位の形状 S）を、FY2022・FY2020〜22 の有無で比較する。
  (B) 多因子 CFaR: 年次の市場収入 R = π_spot + 実効容量収入 を5因子で組み立て、モンテカルロ（N=200,000、乱数種固定）で
        π_spot = θ^β · S · w · a(K) − 充電従量 1,752。a(K) は K のフリートがいるときの限界参入者の粗収益（θ=1）で、主は
        実績整合 a(K) = λ·c(K)（pi_k_curve_v3.csv の仕様A（26）・現状・完全予見の増分貪欲フリート・1万kW 刻みの戦略c の粗利
        c(K) に λ=1.1085 を掛けた値。a(K)−1,752 が π_実績整合(K)。π(0)=6,675）を PCHIP で補間（線形補間を感応度）。
        モデル直値（c(K)、π(0)=5,850）、旧0.81×π_PF(K)（v3 の π_PF、π(0)=4,943）、旧版（pi_k_curve.csv＝旧表8.4 の
        0.81×π_PF(K)、π(0)=4,944）と旧版の実績価格基準（×1.2473）を感応度に置く。
        実効容量収入 = κP_cap(K; L)（κ=0.836。約定水準 L は 2026〜2029年度向けの北海道約定価格×κ の4値＝7,314〜12,517、
        K 依存は表8.7 の需要曲線を 28_equilibrium_surface.py と同じ式で再現し、水準差を加法で移す）
      因子: 価格水準 θ（対数正規 σ=0.267／FY2022除く 0.169、または FY2016〜25 の経験分布）、他者の参入 K（4h換算、
      主ケース U[20, 87.4]万kW＝接続済み約20万kW から LTDA 北海道67.42万kW（49・notes/33 の照合: 第1回32.47・第2回20.95・
      第3回14.01（推定）万kW）の全量運開まで。LTDA の供給力の提供は実需給2027年度以降なので、2026年5月末の接続済み約20万kW
      とは供給力の提供時期が重ならない（ただし LTDA 案件の物理的な連系が先行して接続済み20万kW に含まれているかは一次資料で
      確認できず、含まれていれば K の上端はその分過大。ltda_hokkaido_summary.csv の注記）。感応度は U[20, 76.8]（第3回の別解3.37万kW）、U[20, 99.1]（6時間級23.26万kW を kWh で4h換算）、
      U[20, 120]、K=0）、容量価格の約定水準 L、
      年度単位の形状 S（対数正規・平均1、σ = √(σ_logS² − CV_w²) ≈ 0.23）、日々の天候 w（FY2023〜25 の θ=1 に割り戻した
      日次粗利の暦月層別の循環ブロック・ブートストラップ（Politis & Romano 1992）。ブロックごとに FY2023〜25 の同じ暦月から
      1年を選び、月内で循環させて長さ7日の連続ブロックを取る。31日は暦月をまるごと引く。B=4,000）。
      R は「投資判断の時点から見た、運転期間中の代表的な1年」の市場収入で、1年先の予算の CFaR ではない
      （容量収入は4年前のオークションで決まるので、直近の年度については容量価格の不確実性は解消している）。
      5% CFaR = E[R] − q05、5% ES = E[R] − E[R | R ≤ q05]（いずれも期待値からの差で測る。ES の定義は
      Artzner et al. 1999; Acerbi & Tasche 2002）。
      あわせて原稿の基準（他者の参入なし K=0・θ=1・容量1.25万＝R_ref 19,192円（実績整合）、旧 17,461円）から5%点までの
      下振れ R_ref − q05 を出す。
      因子別の寄与は (i) 単独（その因子だけを確率変数にし、他は基準値に固定。基準は「原稿の基準」と「各因子の基準値」
      の2通り）と、(ii) 5因子の全32部分集合について、含めない因子を基準値（θ=1（中央値）・S=w=1（平均）・K=E[K]・L=E[L]）に
      固定して共通乱数で計算した CFaR05・分散を価値関数とする Shapley 配分（Shapley 1953; Shorrocks 2013 の要因分解）。
      LTDA（容量確保契約）は固定収入＋他市場収益の1割（還付9割、段階で85〜95%）なので、容量価格の因子を全量、
      スポット側の因子を約9割移転する。その残余リスクを同じ物差しで計算し、移転される CFaR（マーチャントの CFaR −
      LTDA の CFaR）の因子別の内訳を、両者の Shapley 寄与の差で示す。
      感応度として、年間のスポット収益が負になる年を0で下げ止める（休止する）ケース、約定水準に2030年度向け Net CONE
      （0.836×20,911）を加えるケース、容量価格の K 依存を非 LTDA 分（接続済み20万kW）だけにするケース（LTDA 電源は
      メインオークションに参加しない。ただし LTDA の容量が需要曲線の側で差し引かれれば価格を下げうるので、どちらとも
      決めず感応度にとどめる）を加える（原稿は充電従量を毎日控除する）。
  (C) ヘッジ有効性（Ederington 1979）: JEPX 実績（data/raw/jepx、FY2016/4〜FY2026/6）の月間蓄電池粗利（北海道）を、
      上場先物の最終決済価格の代理（東京エリアの月平均: ベース、ピーク＝平日8〜20時・祝日除く）で最小分散ヘッジ。
      季節（暦月平均）はサブサンプル内で除く。全期間・FY2020〜22除外・FY2023〜26 の3標本、k か月前からの変化
      （k=1,3,6,12。先物の事前価格の粗い代理）でも計算。水準の HE には月の移動ブロック・ブートストラップ（Künsch 1989、
      長さ6、B=2,000）の90%区間を付す（季節平均は再推定しない）。HE は標本内で推定した h* によるので上限側の値であり、
      h* を先行期間（FY2016〜19、FY2016〜22）で推定して FY2023/4〜2026/6 に当てた標本外の HE も出す。ピークの祝日除外の
      有無も比べる。日次 TB4h の北海道–東京相関の年度推移（FY2026 は4〜6月のみ）。
  (D) テナー不一致: 上場先物で最長 m 年度先（JPX 年度物2（2027年4月から5に拡充予定）、EEX 年度物6）の収入を完全に
      固定できたとしても消せる、20年の収入の現在価値（6%）の分散の割合（log θ の AR(1)、φ=0〜1、線形近似）。

出力: data/processed/cfar_multifactor.csv（多因子 CFaR の各ケース・単独 CFaR・Shapley 配分・LTDA 残余）
      data/processed/cfar_annual_exposure.csv（年度別の完全予見粗利・θ 代理・形状、年次回帰と分散分解）
      data/processed/hedge_effectiveness.csv（最小分散ヘッジ比率と HE）
      data/processed/hedge_basis_corr.csv（日次 TB4h の北海道–東京相関、年度別）
      data/processed/hedge_tenor_share.csv（テナー m 年でヘッジできる20年 PV 分散の上限）
      figures/hokkaido/cfar_decomposition.png（因子別の単独 CFaR と Shapley 配分）

限界: θ の分布は FY2016〜25 の10年（θ は全年度ともシステムプライス比の代理）から校正し、FY2022 の1年で σ が大きく変わる。
      形状 S の σ は分断構造が今と違う FY2016〜19 を含む。K の分布は仮定（LTDA の蓄電池（第2回までは3時間以上、第3回から
      6時間以上）も4h換算の kW で数え、還付下の運用の違いは無視。推定期間の価格に既に入っている既設の蓄電池との二重計上を含む）。
      π(K) は充電従量を毎日控除する原稿の約束に従うので、実績整合では K が約71.5万kW を超えると負になる（休止を最適化すれば
      0で下げ止まる。感応度で確認）。K≥72万kW の π(K) は推定範囲外の外挿の性格が強い。λ は K=0・θ=1 の in-sample 校正。
      K と容量価格の約定水準は年々
      独立に振れるショックではなく、投資時点での状態の不確実性である。因子は独立と置く（θ と S の年次の同時分布は
      感応度で確認）。容量オークションの応札価格は他市場収益の見込みを差し引くので、θ と約定水準は負に相関しうる
      （その場合、独立の仮定は CFaR を過大にする）。容量価格の K 依存は2029年度向け需要曲線の形を約定水準に関わらず使う。
      ヘッジは事後分析で、実際の先物価格ではなく季節除去した実現月平均を最終決済価格の代理にしている（取引コスト・
      証拠金・流動性は無視）。北海道エリアの上場商品はない。

v3 での修正（2026-10-21、主任の決定 D1・D5、T6 の LTDA の訂正、監査 A9-3・A9-5-6 への対応）:
  1. スポット収入の基準を実績整合 a(K)=λ·c(K)（pi_k_curve_v3.csv）にした（旧版の主は 0.81×π_PF(K)、pi_k_curve.csv の
     旧表8.4、K=25 は実際には30 の格子）。旧版の主と実績価格基準は感応度として残す（列「基準」）。
  2. 他者の参入 K の主ケースを U[20, 77.7] から U[20, 87.4] に改めた（LTDA 北海道の落札蓄電池は「少なくとも57.7万kW」
     ではなく67.42万kW。旧版の内訳は森町睦実２（静岡県）5.6万kW を誤って含み、第2回の地名のない案件約7.8万kW を
     落としていた）。U[20, 57.7] の感応度は U[20, 76.8]（第3回の別解）に替え、U[20, 99.1] を加えた。
  3. 約定水準の分布に「3値＋2030年度向け」「4値＋2030年度向け」を加え（CASES と Shapley）、容量価格の K 依存を
     非 LTDA 分だけにする感応度を加えた。
  4. LTDA が移転する CFaR の因子別の内訳（マーチャントと LTDA の Shapley 寄与の差）を出力に加えた。
  5. Shapley の基準値の K（主ケースの E[K]）は 48.85 から 53.7万kW になる。図の脚注を更新した。
  (A)(C)(D) は変更していない（乱数の消費順も変えていないので、ヘッジの出力は旧版と同じ）。
"""
import glob
import logging
import os
from datetime import date, timedelta
from itertools import combinations
from math import factorial

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib import font_manager
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

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
RAW = os.path.join(ROOT, "data", "raw", "jepx")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY = "#595959"

ETA, H, CAPTURE = 0.85, 4, 0.81
W_CHG = 1.2 * H * 365                 # 充電従量負担 1,752 円/kW-年
FIXED_OPEX = 5_300 + 6_900            # 運維・廃止0.53万＋託送等固定0.69万（c_req の固定費部分）
KAPPA = 0.836                         # 4h 蓄電池の調整係数（2029年度向け、表8.7）
P_HKD_AUCTION = {"2026年度向け": 8_749, "2027年度向け": 13_287, "2028年度向け": 14_812, "2029年度向け": 14_972}  # 3.x
L_LEVELS = np.array([KAPPA * v for v in P_HKD_AUCTION.values()])              # 7,314〜12,517
N_SIM = 200_000
rng = np.random.default_rng(20261020)


def crf(r, n=20):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


C_REQ = 4 * 68_000 * crf(0.06) + FIXED_OPEX   # 9.4 の CRF 版（資本費6.8万円/kWh・WACC6%）= 35,914
fy_of = lambda idx: idx.year - (idx.month < 4).astype(int)


def pf_daily(M):
    s = np.sort(M, axis=1)
    raw = ETA * s[:, -H:].sum(axis=1) - s[:, :H].sum(axis=1)     # 円/kW-日
    return np.maximum(raw, 0.0)


def risk_stats(x, alpha=0.05):
    q = np.quantile(x, alpha)
    return dict(mean=x.mean(), sd=x.std(), q05=q, CFaR05=x.mean() - q, ES05=x.mean() - x[x <= q].mean())


# =====================================================================================================
# (A) 年次エクスポージャーと分散分解
# =====================================================================================================
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
FY = pd.Series(fy_of(P.index), index=P.index)
daily = pd.DataFrame({"pf": pf_daily(P.to_numpy()), "fy": FY.values, "month": P.index.month}, index=P.index)

ann = daily.groupby("fy").agg(PF=("pf", "sum"), n_days=("pf", "size"))
ann["PF_365"] = ann["PF"] / ann["n_days"] * 365
ann["pi"] = CAPTURE * ann["PF"] - W_CHG
lvl = hp.assign(fy=fy_of(hp["ts"].dt)).groupby("fy")[["p_system", "p_hokkaido"]].mean()
base_lvl = lvl.loc[[2023, 2024, 2025]].mean()
th = pd.read_csv(os.path.join(PROC, "price_level_theta.csv"))
th_fy = th[th["ym"].str.startswith("FY")].set_index("fy")["theta_m"]
ann["theta_model"] = th_fy.reindex(ann.index)                 # 価格過程の θ_FY（FY2022〜26）
ann["theta_sys"] = (lvl["p_system"] / base_lvl["p_system"]).reindex(ann.index)
ann["theta_hkd"] = (lvl["p_hokkaido"] / base_lvl["p_hokkaido"]).reindex(ann.index)
ann["S_sys"] = ann["PF_365"] / ann["theta_sys"]
print("=== (A) 年度別の完全予見粗利と価格水準の代理（円/kW-年）===")
print(ann.round(3).to_string())
chk = {2022: 25_160, 2023: 9_873, 2024: 9_586, 2025: 11_493}
for y, v in chk.items():
    assert abs(ann.loc[y, "PF"] - v) < 1.0, (y, ann.loc[y, "PF"], v)
print("表7.1・8.2 の完全予見粗利（FY2022〜25）と一致")
m = ann.loc[2022:2025]
print(f"θ_sys と θ_model（FY2022〜25）の差: 平均絶対差 {np.abs(m.theta_sys - m.theta_model).mean():.3f}")

full = ann.loc[2016:2025]
exp_rows = []
for px in ["theta_sys", "theta_hkd"]:
    for lab, sub in {"FY2016〜25": full, "FY2016〜25（FY2022除く）": full.drop(index=[2022]),
                     "FY2016〜25（FY2020〜22除く）": full.drop(index=[2020, 2021, 2022])}.items():
        lp, lt = np.log(sub["PF_365"]), np.log(sub[px])
        ls = lp - lt
        r = sm.OLS(lp, sm.add_constant(lt)).fit()
        exp_rows.append({"区分": "年次回帰・分散分解", "θ代理": "システム比" if px == "theta_sys" else "北海道比",
                         "標本": lab, "n": len(sub), "β(logPF on logθ)": r.params.iloc[1], "β_SE": r.bse.iloc[1],
                         "R2": r.rsquared, "Var(logPF)": lp.var(ddof=1), "Var(logθ)": lt.var(ddof=1),
                         "Var(logS)": ls.var(ddof=1), "2Cov(logθ,logS)": 2 * np.cov(lt, ls, ddof=1)[0, 1],
                         "σ_logθ": lt.std(ddof=1), "σ_logS": ls.std(ddof=1)})
expo = pd.DataFrame(exp_rows)
print("\n=== (A) log PF の年次回帰と分散分解（365日換算）===")
print(expo.round(3).to_string(index=False))
ann_out = ann.reset_index().rename(columns={"fy": "年度", "PF": "完全予見粗利(円/kW-年)", "n_days": "日数",
                                            "PF_365": "完全予見粗利_365日換算", "pi": "実現可能収益π(円/kW-年)",
                                            "theta_model": "θ_FY(価格過程)", "theta_sys": "θ代理_システム比",
                                            "theta_hkd": "θ代理_北海道比", "S_sys": "形状S(=PF_365/θ代理)"})
ann_out.insert(0, "区分", "年度別")
pd.concat([ann_out, expo], ignore_index=True).to_csv(os.path.join(PROC, "cfar_annual_exposure.csv"),
                                                     index=False, encoding="utf-8-sig")

SIG_TH = {"FY2016〜25": float(expo.query("θ代理=='システム比' and 標本=='FY2016〜25'")["σ_logθ"].iloc[0]),
          "FY2022除く": float(expo.query("θ代理=='システム比' and 標本=='FY2016〜25（FY2022除く）'")["σ_logθ"].iloc[0])}
SIG_S_RAW = float(expo.query("θ代理=='システム比' and 標本=='FY2016〜25'")["σ_logS"].iloc[0])
TH_EMP = {"FY2016〜25": full["theta_sys"].to_numpy(), "FY2022除く": full.drop(index=[2022])["theta_sys"].to_numpy()}
BETA_ANN = {k: float(expo.query("θ代理=='システム比' and 標本==@k")["β(logPF on logθ)"].iloc[0])
            for k in ["FY2016〜25", "FY2016〜25（FY2022除く）"]}

# =====================================================================================================
# (B-1) 日々の天候ノイズ: θ=1 に割り戻した FY2023〜25 の日次粗利の暦月層別の循環ブロック・ブートストラップ
# =====================================================================================================
EST = [2023, 2024, 2025]
mask = FY.isin(EST).values
thd = FY[mask].map(ann["theta_sys"]).to_numpy()
Pn = 0.01 + (P.to_numpy()[mask] - 0.01) / thd[:, None]     # 5.4.1 と同じく下限価格より上だけをスケール
dn = pd.DataFrame({"pf": pf_daily(Pn), "fy": FY[mask].values, "month": P.index[mask].month}, index=P.index[mask])
ann_n = dn.groupby("fy")["pf"].sum()
FY_MONTHS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
MDAYS = {4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31, 1: 31, 2: 28, 3: 31}
seqs = {(y, mm): g["pf"].to_numpy() for (y, mm), g in dn.groupby(["fy", "month"])}


def boot_year(L, B):
    out = np.empty(B)
    for b in range(B):
        tot = 0.0
        for mm in FY_MONTHS:
            need, got, n_got = MDAYS[mm], [], 0
            while n_got < need:
                s = seqs[(EST[rng.integers(0, 3)], mm)]
                if L >= 28:
                    blk = s
                else:
                    st = rng.integers(0, len(s))
                    blk = np.take(s, np.arange(st, st + L), mode="wrap")
                got.append(blk)
                n_got += len(blk)
            tot += np.concatenate(got)[:need].sum()
        out[b] = tot
    return out


WBOOT = {L: boot_year(L, 4000) for L in [1, 7, 14, 31]}
print("\n=== (B-1) 日々の天候ノイズ（θ=1、FY2023〜25 の暦月層別の循環ブロック・ブートストラップ、B=4,000）===")
for L, s in WBOOT.items():
    print(f"ブロック {L:>2}日: 年間完全予見粗利 平均 {s.mean():,.0f}、SD {s.std():,.0f}、CV {s.std() / s.mean():.3f}")
CV_W = WBOOT[7].std() / WBOOT[7].mean()
SIG_S = float(np.sqrt(SIG_S_RAW ** 2 - CV_W ** 2))
cv_cur = ann_n.std(ddof=1) / ann_n.mean()
SIG_S_CUR = float(np.sqrt(max(cv_cur ** 2 - CV_W ** 2, 0.0)))
print(f"θ=1 に割り戻した FY2023〜25 の年間粗利: {ann_n.round(0).to_dict()}（CV {cv_cur:.3f}）")
print(f"年度単位の形状: σ_logS（FY2016〜25）{SIG_S_RAW:.3f} → 天候分 CV_w {CV_W:.3f} を除いて σ_u={SIG_S:.3f}"
      f"（現行構造 FY2023〜25 のみなら {SIG_S_CUR:.3f}）")

# =====================================================================================================
# (B-2) π(K) と容量価格の K 依存
# =====================================================================================================
# 旧版の π(K)（pi_k_curve.csv＝旧表8.4。a(K)=0.81×π_PF(K)=π(K)+1,752、格子点で旧表8.4 の π(K) を正確に再現）
pk = pd.read_csv(os.path.join(PROC, "pi_k_curve.csv"))
pk = pk[pk["シナリオ"] == "現状"].drop_duplicates("K(万kW)").sort_values("K(万kW)")
PK_K_OLD = pk["K(万kW)"].to_numpy(float)
G_OLD = pk["π_実現可能(円/kW-年)"].to_numpy(float) + W_CHG
v2 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v2.csv"))
v2a = v2[v2["θ"] == 1.0].set_index("K(万kW)")
TAIL = float((v2a.loc[0, "π_実現可能_裾補正(円/kW-年)"] + W_CHG) / (CAPTURE * v2a.loc[0, "π_PF(円/kW-年)"]))
# v3 の π(K)（D1: 価格過程モデルの価格経路の上で戦略c の実現粗利を直接計算、実績整合は λ で校正）
v3 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
v3 = v3[(v3["価格モデル"] == "仕様A（26、水準係数付き）") & (v3["シナリオ"] == "現状") & (v3["フリート配分"] == "完全予見の増分貪欲（主）")
        & (v3["刻み(万kW)"] == "1.0")]
v3a = v3[v3["θ"] == 1.0].sort_values("K(万kW)").set_index("K(万kW)")
v3b = v3[v3["θ"] == 1.567].sort_values("K(万kW)").set_index("K(万kW)")
LAM = float(v3a["校正係数λ"].iloc[0])
PK_K = v3a.index.to_numpy(float)
G_GRID = {"A": LAM * v3a["c"].to_numpy(float), "M": v3a["c"].to_numpy(float), "O": CAPTURE * v3a["π_PF"].to_numpy(float)}
assert np.allclose(G_GRID["A"] - W_CHG, v3a["π_実績整合"].to_numpy(float), atol=0.05)
assert np.allclose(G_GRID["M"] - W_CHG, v3a["π_モデル直値"].to_numpy(float), atol=0.05)
G_PCHIP = {k: PchipInterpolator(PK_K, v) for k, v in G_GRID.items()}
G_PCHIP["O1"] = PchipInterpolator(PK_K_OLD, G_OLD)
G_LIN = {k: (lambda kk, y=v: np.interp(kk, PK_K, y)) for k, v in G_GRID.items()}
G_LIN["O1"] = lambda kk: np.interp(kk, PK_K_OLD, G_OLD)
BASE_LAB = {"A": "実績整合（a(K)=λ·c(K)、π(0)=6,675）", "M": "モデル直値（c(K)、π(0)=5,850）",
            "O": "旧0.81×π_PF(K)（v3 の曲線、π(0)=4,943）", "O1": "旧版のモデル基準（pi_k_curve.csv、π(0)=4,944）",
            "T1": "旧版の実績価格基準（×1.2473、π(0)≈6,600）"}


def g_of_k(base, K, interp="pchip"):
    """θ=1 の限界参入者の粗収益 a(K)（充電従量控除前、円/kW-年）"""
    b = "O1" if base == "T1" else base
    f = G_PCHIP[b] if interp == "pchip" else G_LIN[b]
    return (TAIL if base == "T1" else 1.0) * np.asarray(f(K), float)


K_ZERO = brentq(lambda k: float(g_of_k("A", k)) - W_CHG, 50.0, 100.0)    # π(K)=0 となる K（実績整合）
K_ZERO_OLD = brentq(lambda k: float(g_of_k("O1", k)) - W_CHG, 50.0, 100.0)
ratio = (v3b["c"] / v3a["c"] / 1.567).loc[[0, 10, 25, 50, 70, 100]]
print(f"\n=== (B-2) π(K) ===\nc(K;θ=1.567)/(1.567·c(K;1))（K=0〜100）: {ratio.round(4).to_list()} → c は θ に比例")
print(f"λ={LAM:.4f}；旧版の実績価格基準の係数 B={TAIL:.4f}；"
      f"ブートストラップの θ=1 平均 {WBOOT[7].mean():,.0f}（完全予見粗利、実績）÷ λ·c(0) {float(g_of_k('A', 0)):,.0f} = {WBOOT[7].mean() / float(g_of_k('A', 0)):.3f}")
for k in [0, 10, 20, 25, 30, 43.7, 50, 53.7, 57.7, 67.4, 76.8, 77.7, 87.4, 99.1, 100, 120]:
    print(f"  K={k:>5}万kW: π 実績整合={float(g_of_k('A', k)) - W_CHG:,.0f}（線形 {float(g_of_k('A', k, 'linear')) - W_CHG:,.0f}）"
          f"  モデル直値={float(g_of_k('M', k)) - W_CHG:,.0f}  旧v3={float(g_of_k('O', k)) - W_CHG:,.0f}  旧版={float(g_of_k('O1', k)) - W_CHG:,.0f}")
print(f"π(K)=0 となる K: 実績整合 {K_ZERO:.1f}万kW、旧版 {K_ZERO_OLD:.1f}万kW（PCHIP）")

P0_CAP, P_CEIL, NET_CONE = 14_972.0, 15_112.5, 10_075.0                    # 28_equilibrium_surface.py と同じ
Q_CAP, Q_TGT, Q_ZERO = 188_813_656, 189_966_340, 195_652_080
SHARE = {"北海道ブロック按分": 529 / 16_208, "全国連系": 1.0}


def p_cap_of_k(K, share):
    dq = KAPPA * np.asarray(K, float) * 1e4
    up = (P_CEIL - NET_CONE) / ((Q_TGT - Q_CAP) * share)
    lo = NET_CONE / ((Q_ZERO - Q_TGT) * share)
    room = (P0_CAP - NET_CONE) / up
    return np.where(dq <= room, P0_CAP - up * dq, np.maximum(0.0, NET_CONE - lo * (dq - room)))


capk = pd.read_csv(os.path.join(PROC, "capacity_price_of_k.csv"))
for lab, s in SHARE.items():
    assert np.allclose(np.round(p_cap_of_k(capk["K(万kW)"], s)), capk[f"P_cap {lab}(円/kW)"], atol=1), lab
print("表8.7（capacity_price_of_k.csv）を再現")


def cap_income(K, L, regime):
    if regime == "定数":
        return np.asarray(L, float) * np.ones_like(np.asarray(K, float))
    return np.maximum(0.0, KAPPA * p_cap_of_k(K, SHARE[regime]) - (KAPPA * P0_CAP - L))


# =====================================================================================================
# (B-3) 多因子 CFaR のシミュレーター
# =====================================================================================================
FACTORS = ["θ", "K", "容量", "形状", "天候"]
FLAB = {"θ": "価格水準 θ", "K": "他者の参入 K", "容量": "容量価格の約定水準", "形状": "年度単位の形状", "天候": "日々の天候"}
Z = {"θ": rng.standard_normal(N_SIM), "θu": rng.random(N_SIM), "K": rng.random(N_SIM),
     "容量": rng.random(N_SIM), "形状": rng.standard_normal(N_SIM),
     "天候": rng.integers(0, 4000, N_SIM), "年": rng.integers(0, 10, N_SIM)}
L2030 = KAPPA * 20_911                                  # 2030年度向け Net CONE × κ（17,482）
L_SETS = {"4値": L_LEVELS, "3値（2027〜29年度向け）": L_LEVELS[1:],
          "3値＋2030年度向け（Net CONE）": np.append(L_LEVELS[1:], L2030), "4値＋2030年度向け（Net CONE）": np.append(L_LEVELS, L2030)}
K_NONLTDA = 20.0                                         # 接続済み（非 LTDA）の容量。容量価格の K 依存の感応度で使う
MAIN = dict(base="A", theta="LN", th_sample="FY2016〜25", beta=1.0, th_med=1.0, cap="全国連系", K=(20.0, 87.4),
            sig_s=None, wblock=7, joint=False, L_set="4値", K_fix=None, L_fix=None, interp="pchip", floor0=False,
            capK="全量")
REF_MS = dict(K_fix=0.0, L_fix=float(L_LEVELS[-1]))      # 原稿の基準: 他者の参入なし・容量1.25万（2029年度向け）


def L_draw(sp):
    if sp["L_set"] == "一様":
        return L_LEVELS.min() + (L_LEVELS.max() - L_LEVELS.min()) * Z["容量"]
    v = L_SETS[sp["L_set"]]
    return v[np.floor(Z["容量"] * len(v)).astype(int)]


def L_mean(sp):
    return (L_LEVELS.min() + L_LEVELS.max()) / 2 if sp["L_set"] == "一様" else float(L_SETS[sp["L_set"]].mean())


def simulate(spec, rand=tuple(FACTORS), parts=False):
    sp = {**MAIN, **spec}
    sig_s = SIG_S if sp["sig_s"] is None else sp["sig_s"]
    if "θ" in rand:
        if sp["theta"] == "LN":
            theta = sp["th_med"] * np.exp(SIG_TH[sp["th_sample"]] * Z["θ"])
        else:
            emp = TH_EMP[sp["th_sample"]]
            theta = emp[np.floor(Z["θu"] * len(emp)).astype(int)]
    else:
        theta = np.full(N_SIM, sp["th_med"])
    shape = np.exp(sig_s * Z["形状"] - sig_s ** 2 / 2) if "形状" in rand else np.ones(N_SIM)
    if sp["joint"]:                                        # (θ_y, S_y) を年の組で同時に引く（天候を含むので w=1）
        s_y = (full["PF_365"] / full["theta_sys"]).to_numpy()
        yi = Z["年"]
        theta = full["theta_sys"].to_numpy()[yi] if "θ" in rand else np.ones(N_SIM)
        shape = (s_y / s_y.mean())[yi] if "形状" in rand else np.ones(N_SIM)
    wb = WBOOT[sp["wblock"]]
    w = (wb / wb.mean())[Z["天候"]] if ("天候" in rand and not sp["joint"]) else np.ones(N_SIM)
    a, b = sp["K"]
    if "K" in rand:
        K = a + (b - a) * Z["K"]
    else:
        K = np.full(N_SIM, (a + b) / 2 if sp["K_fix"] is None else sp["K_fix"])
    if "容量" in rand:
        L = L_draw(sp)
    else:
        L = np.full(N_SIM, L_mean(sp) if sp["L_fix"] is None else sp["L_fix"])
    gk = g_of_k(sp["base"], K, sp["interp"])                # θ=1 の粗収益 a(K)（充電従量控除前）
    spot = theta ** sp["beta"] * shape * w * gk - W_CHG
    if sp["floor0"]:                                        # 年間のスポット収益が負の年は休止（0で下げ止め）
        spot = np.maximum(spot, 0.0)
    Kc = np.minimum(K, K_NONLTDA) if sp["capK"] == "非LTDA" else K   # 容量価格を下げる K（感応度では非 LTDA 分だけ）
    cap = cap_income(Kc, L, sp["cap"])
    if parts:
        return spot, cap
    return spot + cap


def ref_value(base):
    return float(g_of_k(base, 0.0)) - W_CHG + float(L_LEVELS[-1])


def summarize(spot, cap, base):
    R = spot + cap
    r = risk_stats(R)
    ref = ref_value(base)
    r["R_ref(原稿の基準)"] = ref
    r["期待値の低下(R_ref−E[R])"] = ref - r["mean"]
    r["基準からの5%下振れ(R_ref−q05)"] = ref - r["q05"]
    r["P(R<固定費1.22万)"] = (R < FIXED_OPEX).mean()
    r["P(R≥c_req3.59万)"] = (R >= C_REQ).mean()
    r["E[π_spot]"], r["E[κP_cap]"] = spot.mean(), cap.mean()
    r["CFaR05_スポットのみ"] = risk_stats(spot)["CFaR05"]
    return r


def spec_text(sp):
    sp = {**MAIN, **sp}
    th = (f"対数正規 σ={SIG_TH[sp['th_sample']]:.3f}（{sp['th_sample']}）" if sp["theta"] == "LN"
          else f"経験分布（{sp['th_sample']}）")
    if sp["th_med"] != 1.0:
        th += f"・中央値{sp['th_med']}"
    if sp["beta"] != 1.0:
        th += f"・β={sp['beta']:.2f}"
    if sp["joint"]:
        th = "θ と形状を年の組で同時に経験分布（FY2016〜25）"
    k = "K=0" if sp["K"] == (0.0, 0.0) else f"U[{sp['K'][0]:g}, {sp['K'][1]:g}]万kW"
    return dict(基準=BASE_LAB[sp["base"]],
                スポット下げ止め="負の年は0（休止）" if sp["floor0"] else "なし（充電従量を毎日控除）",
                θ仕様=th, 容量仕様=f"{sp['cap']}・約定水準{sp['L_set']}" + ("・K 依存は非 LTDA 分のみ" if sp["capK"] == "非LTDA" else ""),
                K仕様=k,
                形状σ=round(SIG_S if sp["sig_s"] is None else sp["sig_s"], 3), 天候ブロック日=sp["wblock"])


CASES = [
    ("主ケース", {}),
    ("θ: FY2022を除く σ", dict(th_sample="FY2022除く")),
    ("θ: 経験分布（FY2016〜25）", dict(theta="EMP")),
    ("θ: 経験分布（FY2022除く）", dict(theta="EMP", th_sample="FY2022除く")),
    ("θ と形状を年の組で同時に（経験分布）", dict(joint=True)),
    ("θ: 中央値1.57（FY2026上期水準が定着）", dict(th_med=1.567)),
    ("容量: K に依存しない（約定水準のみ）", dict(cap="定数")),
    ("容量: 約定水準を2027〜29年度向けの3値に", dict(L_set="3値（2027〜29年度向け）")),
    ("容量: 約定水準を一様分布 U[7,314, 12,517] に", dict(L_set="一様")),
    ("容量: 北海道ブロック按分", dict(cap="北海道ブロック按分")),
    ("容量: 北海道ブロック按分・θ FY2022除く", dict(cap="北海道ブロック按分", th_sample="FY2022除く")),
    ("容量: 約定水準に2030年度向け（Net CONE 0.836×20,911）を加えた3値＋1", dict(L_set="3値＋2030年度向け（Net CONE）")),
    ("容量: 約定水準に2030年度向け（Net CONE）を加えた4値＋1", dict(L_set="4値＋2030年度向け（Net CONE）")),
    ("容量: 価格の K 依存は非 LTDA 分（接続済み20万kW）のみ", dict(capK="非LTDA")),
    ("K=0（他者の参入なし）", dict(K=(0.0, 0.0))),
    ("K=0・θ FY2022除く", dict(K=(0.0, 0.0), th_sample="FY2022除く")),
    ("K: U[20, 76.8]（LTDA 北海道 第3回の別解）", dict(K=(20.0, 76.8))),
    ("K: U[20, 99.1]（6時間級を kWh で4h換算）", dict(K=(20.0, 99.1))),
    ("K: U[20, 77.7]（旧版の主ケース）", dict(K=(20.0, 77.7))),
    ("K: U[20, 120]", dict(K=(20.0, 120.0))),
    ("π(K) の補間を線形に（PCHIP の代わり）", dict(interp="linear")),
    ("スポット収益が負の年は0（休止）", dict(floor0=True)),
    ("K: U[20, 120]・スポット収益が負の年は0（休止）", dict(K=(20.0, 120.0), floor0=True)),
    ("形状: 現行構造の σ（FY2023〜25）", dict(sig_s=SIG_S_CUR)),
    ("天候: ブロック31日", dict(wblock=31)),
    ("基準: モデル直値", dict(base="M")),
    ("基準: 旧0.81×π_PF（v3 の曲線）", dict(base="O")),
    ("基準: 旧版のモデル基準（pi_k_curve.csv）・K U[20, 87.4]（T6 の予備値の再現）", dict(base="O1")),
    ("基準: 旧版のモデル基準・K U[20, 77.7]（旧版の主ケースの再現）", dict(base="O1", K=(20.0, 77.7))),
    ("基準: 旧版の実績価格基準（×1.25）・K U[20, 77.7]（旧版の再現）", dict(base="T1", K=(20.0, 77.7))),
]
rows = []
for name, sp in CASES:
    spot, cap = simulate(sp, parts=True)
    rows.append({"区分": "多因子（5因子同時）", "ケース": name, **spec_text(sp),
                 **summarize(spot, cap, {**MAIN, **sp}["base"])})

# 単独（1因子だけを確率変数に）: 基準は「原稿の基準」と「各因子の基準値（θ は中央値、他は期待値）」の2通り
STAND = [
    ("θ", "価格水準 θ（FY2016〜25）", {}),
    ("θ", "価格水準 θ（FY2022除く）", dict(th_sample="FY2022除く")),
    ("θ", "価格水準 θ（経験分布 FY2016〜25）", dict(theta="EMP")),
    ("θ", f"価格水準 θ（年次の露出 β={BETA_ANN['FY2016〜25']:.2f}）", dict(beta=BETA_ANN["FY2016〜25"])),
    ("θ", f"価格水準 θ（FY2022除く・β={BETA_ANN['FY2016〜25（FY2022除く）']:.2f}）",
     dict(th_sample="FY2022除く", beta=BETA_ANN["FY2016〜25（FY2022除く）"])),
    ("K", "他者の参入 K（U[20, 87.4]、全国連系）", {}),
    ("K", "他者の参入 K（U[20, 76.8]）", dict(K=(20.0, 76.8))),
    ("K", "他者の参入 K（U[20, 99.1]）", dict(K=(20.0, 99.1))),
    ("K", "他者の参入 K（U[20, 120]）", dict(K=(20.0, 120.0))),
    ("K", "他者の参入 K（北海道ブロック按分、容量価格の低下を含む）", dict(cap="北海道ブロック按分")),
    ("K", "他者の参入 K（容量価格の K 依存なし、スポットのみ）", dict(cap="定数")),
    ("容量", "容量価格の約定水準（4値 7,314〜12,517）", {}),
    ("容量", "容量価格の約定水準（2027〜29年度向けの3値）", dict(L_set="3値（2027〜29年度向け）")),
    ("形状", f"年度単位の形状（σ={SIG_S:.2f}）", {}),
    ("形状", f"年度単位の形状（現行構造 σ={SIG_S_CUR:.2f}）", dict(sig_s=SIG_S_CUR)),
    ("天候", "日々の天候（ブロック1日）", dict(wblock=1)),
    ("天候", "日々の天候（ブロック7日）", {}),
    ("天候", "日々の天候（ブロック14日）", dict(wblock=14)),
    ("天候", "日々の天候（ブロック31日）", dict(wblock=31)),
]
for ref_lab, ref_sp in [("原稿の基準（K=0・θ=1・容量12,517）", REF_MS), ("各因子の基準値（θ=1・K=E[K]・L=E[L]）", {})]:
    for fac, name, sp in STAND:
        spot, cap = simulate({**ref_sp, **sp}, rand=(fac,), parts=True)
        rows.append({"区分": f"単独・基準={ref_lab}", "ケース": name, "因子": FLAB[fac], **spec_text(sp),
                     **summarize(spot, cap, {**MAIN, **sp}["base"])})


# Shapley 配分（5因子、全32部分集合、共通乱数。含めない因子は基準値（θ=1（中央値）・S=w=1・K=E[K]・L=E[L]）に固定）
def shapley(sp, ltda_refund=None):
    """ltda_refund を与えると、LTDA の収入（固定収入＋(1−還付率)·π_spot）について配分する。"""
    val_c, val_v = {(): 0.0}, {(): 0.0}
    for r in range(1, len(FACTORS) + 1):
        for A in combinations(FACTORS, r):
            if ltda_refund is None:
                R = simulate(sp, rand=A)
            else:
                R = (1 - ltda_refund) * simulate(sp, rand=A, parts=True)[0]
            val_c[A], val_v[A] = R.mean() - np.quantile(R, 0.05), R.var()
    n = len(FACTORS)
    out = {}
    for j in FACTORS:
        others = [f for f in FACTORS if f != j]
        phc = phv = 0.0
        for r in range(0, n):
            for A in combinations(others, r):
                wgt = factorial(r) * factorial(n - r - 1) / factorial(n)
                Aj = tuple(f for f in FACTORS if f in A or f == j)
                phc += wgt * (val_c[Aj] - val_c[A])
                phv += wgt * (val_v[Aj] - val_v[A])
        out[j] = (phc, phv)
    return out, val_c[tuple(FACTORS)], val_v[tuple(FACTORS)]


SHAP_SC = [
    ("全国連系・θ FY2016〜25", {}),
    ("全国連系・θ FY2022除く", dict(th_sample="FY2022除く")),
    ("北海道ブロック按分・θ FY2016〜25", dict(cap="北海道ブロック按分")),
    ("北海道ブロック按分・θ FY2022除く", dict(cap="北海道ブロック按分", th_sample="FY2022除く")),
    ("K=0（他者の参入なし）・θ FY2016〜25", dict(K=(0.0, 0.0))),
    ("K=0（他者の参入なし）・θ FY2022除く", dict(K=(0.0, 0.0), th_sample="FY2022除く")),
    ("全国連系・θ FY2016〜25・約定水準は2027〜29年度向けの3値", dict(L_set="3値（2027〜29年度向け）")),
    ("全国連系・θ FY2016〜25・約定水準は3値＋2030年度向け", dict(L_set="3値＋2030年度向け（Net CONE）")),
    ("全国連系・θ FY2016〜25・約定水準は4値＋2030年度向け", dict(L_set="4値＋2030年度向け（Net CONE）")),
    ("全国連系・θ FY2016〜25・容量価格の K 依存は非 LTDA 分のみ", dict(capK="非LTDA")),
    ("全国連系・θ FY2016〜25・K U[20, 76.8]", dict(K=(20.0, 76.8))),
    ("全国連系・θ FY2016〜25・K U[20, 99.1]", dict(K=(20.0, 99.1))),
    ("基準: モデル直値・全国連系・θ FY2016〜25", dict(base="M")),
    ("基準: 旧版のモデル基準・K U[20, 87.4]（T6 の予備値の再現）", dict(base="O1")),
    ("基準: 旧版のモデル基準・K U[20, 77.7]（旧版の主ケースの再現）", dict(base="O1", K=(20.0, 77.7))),
]
SHAP = {}
print("\n=== (B-3) Shapley 配分（CFaR05 と分散、含めない因子は基準値に固定）===")
for name, sp in SHAP_SC:
    out, tc, tv = shapley(sp)
    SHAP[name] = (out, tc)
    print(f"[{name}] 合計 CFaR05={tc:,.0f}  SD={np.sqrt(tv):,.0f}")
    for j in FACTORS:
        print(f"   {FLAB[j]:<10} CFaR寄与 {out[j][0]:>8,.0f}（{out[j][0] / tc:6.1%}）  分散シェア {out[j][1] / tv:6.1%}")
        rows.append({"区分": "Shapley 配分", "ケース": name, "因子": FLAB[j], **spec_text(sp),
                     "CFaR05": tc, "Shapley_CFaR05": out[j][0], "Shapley_CFaR05シェア": out[j][0] / tc,
                     "Shapley_分散シェア": out[j][1] / tv, "sd": np.sqrt(tv)})

# LTDA（容量確保契約）の残余リスク: 収入 = 固定 F + (1−還付率)·π_spot。容量価格の因子は全量移転
print("\n=== (B-4) LTDA が移転するリスク（主ケースの因子分布）===")
spot_all, cap_all = simulate({}, parts=True)
merch = risk_stats(spot_all + cap_all)
for refund in [0.85, 0.90, 0.95]:
    rr = risk_stats((1 - refund) * spot_all)
    rows.append({"区分": "LTDA 残余", "ケース": f"LTDA（還付率{refund:.0%}）: 固定収入＋π_spot×{1 - refund:.2f}",
                 **spec_text({}), "sd": rr["sd"], "CFaR05": rr["CFaR05"], "ES05": rr["ES05"],
                 "移転された CFaR の割合": 1 - rr["CFaR05"] / merch["CFaR05"]})
    print(f"還付率 {refund:.0%}: 残る CFaR05 {rr['CFaR05']:,.0f}（マーチャント {merch['CFaR05']:,.0f} の "
          f"{rr['CFaR05'] / merch['CFaR05']:.1%}）")
out_main = SHAP["全国連系・θ FY2016〜25"][0]
out_l, tc_l, tv_l = shapley({}, ltda_refund=0.90)
SHAP["LTDA（還付9割）・全国連系・θ FY2016〜25"] = (out_l, tc_l)
for j in FACTORS:
    print(f"  {FLAB[j]:<10}: マーチャントの Shapley 寄与 {out_main[j][0]:>7,.0f} → LTDA（還付9割）の Shapley 寄与 {out_l[j][0]:>6,.0f}")
    rows.append({"区分": "Shapley 配分", "ケース": "LTDA（還付9割）・全国連系・θ FY2016〜25", "因子": FLAB[j],
                 **spec_text({}), "CFaR05": tc_l, "Shapley_CFaR05": out_l[j][0],
                 "Shapley_CFaR05シェア": out_l[j][0] / tc_l, "Shapley_分散シェア": out_l[j][1] / tv_l,
                 "sd": np.sqrt(tv_l)})
# LTDA（還付9割）が移転する CFaR の因子別の内訳: マーチャントと LTDA の Shapley 寄与の差（移転 = 合計の差）
print("  LTDA が移転する CFaR の内訳（マーチャントの Shapley 寄与 − LTDA の Shapley 寄与）")
for name, sp in (("全国連系・θ FY2016〜25", {}), ("全国連系・θ FY2016〜25・約定水準は2027〜29年度向けの3値", dict(L_set="3値（2027〜29年度向け）")),
                 ("全国連系・θ FY2016〜25・約定水準は3値＋2030年度向け", dict(L_set="3値＋2030年度向け（Net CONE）")),
                 ("北海道ブロック按分・θ FY2016〜25", dict(cap="北海道ブロック按分"))):
    om, tm = SHAP[name]
    ol, tl, _ = (out_l, tc_l, tv_l) if not sp else shapley(sp, ltda_refund=0.90)
    tr = tm - tl
    dtr = {j: om[j][0] - ol[j][0] for j in FACTORS}
    print(f"   [{name}] マーチャント {tm:,.0f} → LTDA {tl:,.0f}、移転 {tr:,.0f}（{tr / tm:.1%}）: "
          + "、".join(f"{FLAB[j]} {dtr[j]:,.0f}（{dtr[j] / tr:.1%}）" for j in FACTORS)
          + f"；容量＋K {(dtr['容量'] + dtr['K']) / tr:.1%}")
    for j in FACTORS:
        rows.append({"区分": "LTDA が移転する CFaR の内訳", "ケース": name, "因子": FLAB[j], **spec_text(sp),
                     "CFaR05": tm, "LTDA_CFaR05": tl, "移転された CFaR": tr, "移転された CFaR の割合": tr / tm,
                     "Shapley_CFaR05": dtr[j], "Shapley_CFaR05シェア": dtr[j] / tr})

cf = pd.DataFrame(rows)
cf.to_csv(os.path.join(PROC, "cfar_multifactor.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250)
print(f"\n=== (B) 多因子 CFaR（円/kW-年、R_ref={ref_value('A'):,.0f}（実績整合）、旧版 {ref_value('O1'):,.0f}）===")
show = cf[~cf["区分"].isin(["Shapley 配分", "LTDA が移転する CFaR の内訳"])][["区分", "ケース", "mean", "sd", "q05", "CFaR05", "ES05",
                                       "期待値の低下(R_ref−E[R])", "基準からの5%下振れ(R_ref−q05)",
                                       "P(R<固定費1.22万)", "P(R≥c_req3.59万)", "E[π_spot]", "E[κP_cap]",
                                       "CFaR05_スポットのみ"]]
print(show.round(3).to_string(index=False))

# =====================================================================================================
# 図: (a) 原稿の基準からの1因子ごとの5%下振れ、(b) 5因子同時の CFaR の Shapley 配分
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、2つのパネルを縦に並べ、文字は8.5pt 以上にする。
# 基準（他者の参入なし・θ=1・容量収入12,517円、R_ref）は図の注に書く
# =====================================================================================================
COL = {"θ": "#2a78d6", "K": "#eb6834", "容量": "#1baf7a", "形状": "#eda100", "天候": "#e87ba4"}
fig, axes = plt.subplots(2, 1, figsize=(6.1, 7.8), gridspec_kw={"height_ratios": [6.2, 6.0]}, layout="constrained")
ax = axes[0]
sel = [("K", "他者の参入 K（北海道ブロック按分、容量価格の低下を含む）", "他者の参入 K\n（容量は北海道ブロック按分）"),
       ("K", "他者の参入 K（U[20, 87.4]、全国連系）", "他者の参入 K\n（容量は全国連系）"),
       ("容量", "容量価格の約定水準（4値 7,314〜12,517）", "容量価格の約定水準\n（7,314〜12,517）"),
       ("θ", "価格水準 θ（FY2016〜25）", "価格水準 θ\n（FY2016〜25、σ=%.2f）" % SIG_TH["FY2016〜25"]),
       ("θ", "価格水準 θ（FY2022除く）", "価格水準 θ\n（FY2022除く、σ=%.2f）" % SIG_TH["FY2022除く"]),
       ("形状", f"年度単位の形状（σ={SIG_S:.2f}）", f"年度単位の形状\n（σ={SIG_S:.2f}）"),
       ("天候", "日々の天候（ブロック7日）", "日々の天候\n（ブロック7日）")]
st = cf[cf["区分"] == "単独・基準=原稿の基準（K=0・θ=1・容量12,517）"].set_index("ケース")
ypos = np.arange(len(sel))[::-1]
xmax_a = 0.0
for y, (fac, c, lab) in zip(ypos, sel):
    tot = float(st.loc[c, "基準からの5%下振れ(R_ref−q05)"])
    mshift = float(st.loc[c, "期待値の低下(R_ref−E[R])"])
    hatch = "///" if ("北海道ブロック" in c or "FY2022除く" in c) else None
    ax.barh(y, tot, height=0.55, color=COL[fac], linewidth=0, hatch=hatch, edgecolor="white")
    txt = f"{tot:,.0f}"
    if mshift > 0.1 * tot:
        txt += f"\n（うち期待値の低下 {mshift:,.0f}）"
    ax.text(tot + 150, y, txt, va="center", fontsize=8.5, color="#222222", linespacing=1.1)
    xmax_a = max(xmax_a, tot)
ax.set_yticks(ypos)
ax.set_yticklabels([lab for _, _, lab in sel], fontsize=8.5, color="#222222")
ax.set_xlabel("基準から5%点までの下振れ（円/kW-年）", fontsize=9, color=GRAY)
ax.set_title("(a) 1因子だけを動かした場合の5%下振れ", fontsize=9.5, loc="left", fontweight="bold")
ax.set_xlim(0, xmax_a * 1.62)

ax = axes[1]
order = ["全国連系・θ FY2016〜25", "全国連系・θ FY2022除く", "北海道ブロック按分・θ FY2016〜25", "北海道ブロック按分・θ FY2022除く"]
labels = ["マーチャント\n容量: 全国連系\nθ: FY2016〜25", "マーチャント\n容量: 全国連系\nθ: FY2022除く",
          "マーチャント\n容量: 北海道ブロック按分\nθ: FY2016〜25", "マーチャント\n容量: 北海道ブロック按分\nθ: FY2022除く",
          "LTDA（還付9割）\n容量: 全国連系\nθ: FY2016〜25"]
yb = np.arange(5)[::-1]
GAP = 22
for y, i in zip(yb, range(5)):
    if i < 4:
        out_i, tot = SHAP[order[i]]
        contrib = {j: out_i[j][0] for j in FACTORS}
    else:
        contrib = {j: out_l[j][0] for j in FACTORS}
        tot = tc_l
    left = 0.0
    for j in FACTORS:
        v = contrib[j]
        if v > 0:
            ax.barh(y, max(v - GAP, 1.0), left=left, height=0.55, color=COL[j], linewidth=0)
            left += v
    ax.text(left + 100, y, f"計 {tot:,.0f}", va="center", fontsize=8.5, color="#222222")
ax.set_yticks(yb)
ax.set_yticklabels(labels, fontsize=8.5, color="#222222")
ax.set_xlabel("5因子同時の5% CFaR の Shapley 配分（円/kW-年）", fontsize=9, color=GRAY)
ax.set_title("(b) 5因子同時の5% CFaR と因子別の寄与", fontsize=9.5, loc="left", fontweight="bold")
ax.set_xlim(0, max(SHAP[o][1] for o in order) * 1.2)
handles = [plt.Rectangle((0, 0), 1, 1, color=COL[j]) for j in FACTORS]
ax.legend(handles, [FLAB[j] for j in FACTORS], ncol=1, fontsize=8.5, frameon=False, loc="lower right",
          bbox_to_anchor=(1.0, 0.0), handlelength=1.2, title="因子", title_fontsize=8.5)
for a_ in axes:
    a_.grid(axis="x", color="#e6e6e6", lw=0.8)
    a_.set_axisbelow(True)
    for s in ["top", "right"]:
        a_.spines[s].set_visible(False)
    a_.spines["left"].set_color("#bbbbbb")
    a_.spines["bottom"].set_color("#bbbbbb")
    a_.tick_params(axis="x", colors=GRAY, labelsize=8.5)
    a_.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "cfar_decomposition.png"), dpi=300)
plt.close(fig)
print("\n図: figures/hokkaido/cfar_decomposition.png")

# =====================================================================================================
# (C) ヘッジ有効性（Ederington 1979）と北海道–東京のベーシス
# =====================================================================================================


def jp_holidays(y0, y1):
    """国民の祝日（振替休日・国民の休日を含む）。2016〜2026年の特例（2019年の即位関連、2020・21年の五輪移動）を反映。"""
    def nth_monday(y, mth, n):
        d = date(y, mth, 1)
        d += timedelta(days=(0 - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    hol = set()
    for y in range(y0, y1 + 1):
        k = (y - 1980) // 4
        spring = int(20.8431 + 0.242194 * (y - 1980)) - k
        autumn = int(23.2488 + 0.242194 * (y - 1980)) - k
        hs = [date(y, 1, 1), nth_monday(y, 1, 2), date(y, 2, 11), date(y, 3, spring), date(y, 4, 29),
              date(y, 5, 3), date(y, 5, 4), date(y, 5, 5), nth_monday(y, 9, 3), date(y, 9, autumn),
              date(y, 11, 3), date(y, 11, 23)]
        if y <= 2018:
            hs.append(date(y, 12, 23))
        if y >= 2020:
            hs.append(date(y, 2, 23))
        if y == 2020:
            hs += [date(2020, 7, 23), date(2020, 7, 24), date(2020, 8, 10)]
        elif y == 2021:
            hs += [date(2021, 7, 22), date(2021, 7, 23), date(2021, 8, 8)]
        else:
            hs += [nth_monday(y, 7, 3), date(y, 8, 11), nth_monday(y, 10, 2)]
        if y == 2019:
            hs += [date(2019, 5, 1), date(2019, 10, 22)]
        hol.update(hs)
    for d in sorted(hol):                                   # 国民の休日（祝日に挟まれた平日）
        mid = d + timedelta(days=1)
        if mid not in hol and (mid + timedelta(days=1)) in hol and mid.weekday() != 6:
            hol.add(mid)
    for d in sorted(hol):                                   # 振替休日
        if d.weekday() == 6:
            nd = d + timedelta(days=1)
            while nd in hol:
                nd += timedelta(days=1)
            hol.add(nd)
    return hol


HOL = jp_holidays(2016, 2026)
for d in [date(2019, 4, 30), date(2019, 5, 2), date(2019, 5, 6), date(2020, 7, 24), date(2021, 8, 9),
          date(2024, 2, 12), date(2025, 3, 20), date(2026, 5, 6)]:
    assert d in HOL, d
assert date(2020, 10, 12) not in HOL

frames = []
for f in sorted(glob.glob(os.path.join(RAW, "spot_summary_*.csv"))):
    d = pd.read_csv(f, encoding="cp932").iloc[:, [0, 1, 5, 6, 8]]
    d.columns = ["date", "slot", "sys", "hkd", "tky"]
    frames.append(d)
j = pd.concat(frames, ignore_index=True)
j["date"] = pd.to_datetime(j["date"])
j["hour"] = (j["slot"] - 1) // 2
for c in ["sys", "hkd", "tky"]:
    j[c] = pd.to_numeric(j[c], errors="coerce")
hr = j.groupby(["date", "hour"])[["sys", "hkd", "tky"]].mean().reset_index()
hr = hr[(hr["date"] >= "2016-04-01") & (hr["date"] <= "2026-06-30")]


def mat(col):
    M = hr.pivot(index="date", columns="hour", values=col)
    return M[M.count(axis=1) == 24]


Mh, Mt = mat("hkd"), mat("tky")
days = Mh.index.intersection(Mt.index)
Mh, Mt = Mh.loc[days], Mt.loc[days]
sh, stk = np.sort(Mh.to_numpy(), axis=1), np.sort(Mt.to_numpy(), axis=1)
D = pd.DataFrame(index=days)
D["X"] = pf_daily(Mh.to_numpy())
D["Xt"] = pf_daily(Mt.to_numpy())
D["tb4_h"] = sh[:, -H:].mean(1) - sh[:, :H].mean(1)
D["tb4_t"] = stk[:, -H:].mean(1) - stk[:, :H].mean(1)
D["base_h"] = Mh.mean(axis=1)
D["base_t"] = Mt.mean(axis=1)
is_peakday = np.array([(d.weekday() < 5) and (d.date() not in HOL) for d in days])
D["peak_t"] = np.where(is_peakday, Mt.loc[:, 8:19].mean(axis=1), np.nan)
D["peak_t_h"] = np.where(days.weekday < 5, Mt.loc[:, 8:19].mean(axis=1), np.nan)   # 祝日を除かない版（感応度）
D["fy"] = fy_of(days)
D["ym"] = days.to_period("M")
print("\n=== (C) ヘッジ有効性 ===")
print("年度別完全予見粗利（JEPX 生データ、北海道）:", D[D.fy.between(2022, 2025)].groupby("fy")["X"].sum().round(0).to_dict())
print(f"ピーク日（平日・祝日除く）の割合 {is_peakday.mean():.3f}（祝日除外で {(days.weekday < 5).sum() - is_peakday.sum()} 日を除外）")

Mo = D.groupby("ym").agg(X=("X", "sum"), Xt=("Xt", "sum"), base_h=("base_h", "mean"), base_t=("base_t", "mean"),
                         peak_t=("peak_t", "mean"), peak_t_h=("peak_t_h", "mean"), n=("X", "size"))
Mo = Mo[Mo["n"] >= 25]
Mo["cal"] = Mo.index.month
Mo["fy"] = Mo.index.year - (Mo.index.month < 4)
INSTR = [("東京ベース", "base_t", True), ("東京ピーク（平日8〜20時・祝日除く）", "peak_t", True),
         ("北海道ベース（非上場）", "base_h", False), ("東京4h蓄電池粗利（非上場）", "Xt", False),
         ("東京ピーク（平日8〜20時・祝日を含む）", "peak_t_h", None)]      # None: 上場商品の定義と違う感応度（区間なし）
SAMPLES = {"FY2016/4〜2026/6": Mo, "FY2020〜22 除外": Mo[~Mo.fy.isin([2020, 2021, 2022])],
           "FY2023/4〜2026/6": Mo[Mo.fy >= 2023]}


def hedge_stats(x, f):
    h = np.cov(x, f, ddof=1)[0, 1] / np.var(f, ddof=1)
    return h, 1 - np.var(x - h * f, ddof=1) / np.var(x, ddof=1)


def block_boot_he(x, f, L=6, B=2000):
    n = len(x)
    out = np.empty(B)
    nb = int(np.ceil(n / L))
    for b in range(B):
        st_ = rng.integers(0, n - L + 1, nb)
        idx = (st_[:, None] + np.arange(L)[None, :]).ravel()[:n]
        out[b] = hedge_stats(x[idx], f[idx])[1]
    return np.quantile(out, [0.05, 0.95])


LISTED_LAB = {True: True, False: False, None: "感応度（祝日を含む）"}
hrows = []
for sname, sub in SAMPLES.items():
    sub = sub.copy()
    for c in ["X", "Xt", "base_h", "base_t", "peak_t", "peak_t_h"]:
        sub[c + "_ds"] = sub[c] - sub.groupby("cal")[c].transform("mean")
    for k in [0, 1, 3, 6, 12]:
        for iname, c, listed in INSTR:
            if k == 0:
                x, fser = sub["X_ds"], sub[c + "_ds"]
            else:
                lag = sub[["X_ds", c + "_ds"]].copy()
                lag.index = lag.index + k
                x = sub["X_ds"] - lag["X_ds"].reindex(sub.index)
                fser = sub[c + "_ds"] - lag[c + "_ds"].reindex(sub.index)
            z = pd.DataFrame({"x": x, "f": fser}).dropna()
            h, he = hedge_stats(z["x"].to_numpy(), z["f"].to_numpy())
            lo = hi = np.nan
            if k == 0 and listed is True:
                lo, hi = block_boot_he(z["x"].to_numpy(), z["f"].to_numpy())
            hrows.append({"標本": sname, "k(か月前からの変化, 0=水準)": k, "ヘッジ手段": iname, "上場の代理": LISTED_LAB[listed],
                          "n(月)": len(z), "h*(kWh/kW-月)": h, "HE": he, "HE_90%下限": lo, "HE_90%上限": hi,
                          "相関": np.corrcoef(z["x"], z["f"])[0, 1], "SD_ヘッジ前(円/kW-月)": z["x"].std(ddof=1),
                          "SD_ヘッジ後(円/kW-月)": (z["x"] - h * z["f"]).std(ddof=1)})


def deseason(sub, cols):
    sub = sub.copy()
    for c in cols:
        sub[c + "_ds"] = sub[c] - sub.groupby("cal")[c].transform("mean")
    return sub


# 標本外: h* を先行期間で推定し、FY2023/4〜2026/6 に当てる（季節は各期間の中で除く。h* だけを標本外にする）
TEST = deseason(Mo[Mo.fy >= 2023], ["X", "Xt", "base_t", "peak_t"])
for tr_lab, tr in [("FY2016〜19", Mo[Mo.fy.between(2016, 2019)]), ("FY2016〜22", Mo[Mo.fy.between(2016, 2022)])]:
    tr = deseason(tr, ["X", "Xt", "base_t", "peak_t"])
    for iname, c, listed in INSTR:
        if c not in ["base_t", "peak_t", "Xt"]:
            continue
        h_tr, he_tr = hedge_stats(tr["X_ds"].to_numpy(), tr[c + "_ds"].to_numpy())
        x, f = TEST["X_ds"].to_numpy(), TEST[c + "_ds"].to_numpy()
        he_oos = 1 - np.var(x - h_tr * f, ddof=1) / np.var(x, ddof=1)
        hrows.append({"標本": f"標本外: h* を {tr_lab} で推定 → FY2023/4〜2026/6", "k(か月前からの変化, 0=水準)": 0,
                      "ヘッジ手段": iname, "上場の代理": LISTED_LAB[listed], "n(月)": len(x), "h*(kWh/kW-月)": h_tr, "HE": he_oos,
                      "HE_90%下限": np.nan, "HE_90%上限": np.nan, "相関": np.corrcoef(x, f)[0, 1],
                      "SD_ヘッジ前(円/kW-月)": x.std(ddof=1), "SD_ヘッジ後(円/kW-月)": (x - h_tr * f).std(ddof=1),
                      "注記": f"推定期間の HE {he_tr:.3f}"})
hg = pd.DataFrame(hrows)
hg.to_csv(os.path.join(PROC, "hedge_effectiveness.csv"), index=False, encoding="utf-8-sig")
print(hg.pivot_table(index=["標本", "k(か月前からの変化, 0=水準)"], columns="ヘッジ手段", values="HE").round(3).to_string())
print(hg[(hg["k(か月前からの変化, 0=水準)"] == 0)][["標本", "ヘッジ手段", "n(月)", "h*(kWh/kW-月)", "HE", "HE_90%下限",
                                               "HE_90%上限", "SD_ヘッジ前(円/kW-月)", "SD_ヘッジ後(円/kW-月)"]].round(3).to_string(index=False))

bc = pd.DataFrame({fy: {
    "日数": len(g), "相関_TB4h(北海道,東京)": g["tb4_h"].corr(g["tb4_t"]), "相関_日次粗利": g["X"].corr(g["Xt"]),
    "TB4h平均_北海道": g["tb4_h"].mean(), "TB4h平均_東京": g["tb4_t"].mean(),
    "完全予見粗利_北海道": g["X"].sum(), "完全予見粗利_東京": g["Xt"].sum()} for fy, g in D.groupby("fy")}).T
bc.index.name = "fy"
bc["注記"] = np.where(bc.index == 2026, "FY2026 は4〜6月のみ（季節が偏るため年度とは比較できない）", "")
bc.reset_index().rename(columns={"fy": "年度"}).to_csv(os.path.join(PROC, "hedge_basis_corr.csv"), index=False,
                                                       encoding="utf-8-sig")
print("\n日次 TB4h の北海道–東京相関（年度別）:")
print(bc[["日数", "相関_TB4h(北海道,東京)", "相関_日次粗利", "完全予見粗利_北海道", "完全予見粗利_東京"]].round(3).to_string())

# =====================================================================================================
# (D) テナー不一致: 最長 m 年度先まで固定できても消せる20年 PV 分散の割合
# =====================================================================================================
T, R_ = 20, 0.06
dsc = (1 + R_) ** -np.arange(1, T + 1)
trows = []
for phi in [0.0, 0.5, 0.9, 1.0]:
    # 線形近似: PV ≈ Σ_t d^t (1 + x_t)、x_t = Σ_{s≤t} φ^{t−s} e_s（x_0 は既知）。Var(PV) ∝ Σ_s (Σ_{t≥s} d^t φ^{t−s})²
    def var_pv(m):
        tot = 0.0
        for s in range(1, T + 1):
            g = sum(dsc[t - 1] * phi ** (t - s) for t in range(max(s, m + 1), T + 1))
            tot += g ** 2
        return tot
    v0 = var_pv(0)
    for mm, lab in [(1, "1年度"), (2, "2年度（JPX 年度物、現行）"), (5, "5年度（JPX 年度物、2027年4月から予定）"),
                    (6, "6年度（EEX 年度物）")]:
        trows.append({"φ(log θ の AR(1))": phi, "テナー": lab, "m(年)": mm,
                      "PV に占める m 年分の割合": dsc[:mm].sum() / dsc.sum(),
                      "完全ヘッジで消せる PV 分散の上限": 1 - var_pv(mm) / v0})
tn = pd.DataFrame(trows)
tn.to_csv(os.path.join(PROC, "hedge_tenor_share.csv"), index=False, encoding="utf-8-sig")
print("\n=== (D) テナー不一致（20年・6%）===")
print(tn.round(3).to_string(index=False))
