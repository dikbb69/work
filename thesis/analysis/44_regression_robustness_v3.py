#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日次回帰の頑健化（v3）: 風力→TB4h の区間と上限、暦月4季節（表6.9 パネルC）、冬の上位・下位の比の集合と検出力、
F&O 型（表6.6・6.7）の推論、九州の原子力（表8.11）、相対価格（6.5.4）、主成分分解（6.6・表6.10）の2021年1月除外と EWC

監査（T3_regressions）の確認済みの問題 A6-2-1・A6-5-2（2件）・A6-5-5・A6-5-3・A6-6-1・A6-6-2（2件）・A6-6-4・A8-10（2件）に答える。
推論はすべて 37_robust_inference.py の実装（実行部の前までを exec で読み込む）を使う: EWC（Lazarus, Lewis, Stock and Watson 2018。
ν=⌊0.4T^{2/3}⌋、t_ν、暦日の格子で欠測日は影響関数0）、HC3、Newey-West（14日、暦日の格子）、設計に合わせたふるいブートストラップ
（Bühlmann 1997。X を固定し、同じ標本の主仕様の残差の AR(p) から帰無の y を作る。R=1,999）。

手法:
  (A) 表6.2 の主仕様（S1: 季節×太陽光・風力の制御前 GWh/日、需要、FY・季節FE）と年月FE（S4: 需要・曜日・祝日・年月FE）で、
      TB4h への係数の EWC 95%区間、ブートストラップ‐t 区間（係数 ± ふるいブートストラップの |t| の95%分位 × EWC SE）、
      年度内の日次発電量1SD（その季節の日の、年度平均からの偏差の SD）あたりの効果と区間の上限、その季節の平均 TB4h に対する比。
      標本は FY2016〜25・FY2023〜25・2021年1月を除く FY2016〜25。北海道・九州。
  (B) 暦月4季節（春3〜6月・夏7〜9月・秋10〜11月・冬12〜2月）で S1・S4・S5（S4＋日平均価格の1〜7日ラグ）を推定し、
      太陽光・風力の TB4h 係数、EWC の p、補正 p（S1・S4。S5 は X が y に依存するので出さない）、95%区間、1SD あたりの効果（表6.9 パネルC）。
  (C) FY2023〜25 の春（3〜6月）の日を日次の純需要の三分位に分け、風力×三分位の交互作用（三分位の主効果つき、S1・S4）。
      純需要は (i) 需要−太陽光−風力（監査の仕様）と (ii) 需要−太陽光（風力で条件付けない版）の2通り。
  (D) 北海道・冬の風力: 上位4h・下位4h の係数の比 c の95%集合（y=top4−c·bot4 の EWC 検定を反転する Fieller 型。2本の影響関数の
      EWC 共分散から解析的に解き、格子でも確かめる）、平行（c=1）と比例（c=r、r は冬の上位・下位4時間の平均価格の比）の EWC の p と補正 p、
      2点検定の検出力（真が比例のときに平行を棄却する確率、真が平行のときに比例を棄却する確率。非心 t）と、
      日単位の14日移動ブロック・ブートストラップ（B=999）で r と係数を同時に再標本化した比と差の区間。
  (E) Fuke and Ohashi (2025) 型（25_fo_replication.py の build_daily・design をそのまま使う）: 同じ日次標本・同じ右辺の TB4h の OLS に
      EWC（暦日の格子）を付け、HC3 と並べる。IQR 係数（τ=0.9 と0.1 の分位点回帰の係数差）に、i.i.d. のペア・ブートストラップと
      日単位の14日移動ブロック・ブートストラップ（各 B=299）の SE・正規近似の p・パーセンタイル区間を付ける
      （分位点回帰は 45_quantile_moe_v3.py の Frisch–Newton 法）。
  (F) 九州の原子力（33_price_curve_sensitivity.py の表8.11 の仕様）: 季節×原子力の係数の EWC・NW14（暦日の格子）・HC3 の p、
      片側95%上限と泊3号相当（820.8MW×24h=19.7GWh/日）への換算、非優越の片側検定（H0: 19.7β ≥ 0.5円/kWh）の p、
      補正 p（TB4h・完全予見粗利）。年月FE は 33 と同じ（曜日・祝日なし）版と、5.2.3 にそろえた曜日・祝日つきの版を並べる。
  (G) 相対価格（被説明変数をその年度の日平均価格の平均で割る）で、燃料危機期（FY2021〜22）を除いた推定と主分析の係数の比（6.5.4）。
  (H) 2018-09-06（胆振東部地震の当日。価格は前日に約定済みだが需要15GWh・太陽光0の外れ値）を除いた表6.2 の主仕様。
  (I) 主成分分解（34_price_curve_pca.py の関数を読み込む）: 2021年1月（31日）を除いた寄与率・負荷の安定性・相関行列とセル内標準化の PCA、
      TB4h の PC1 による説明率、TB4h 係数の経路分解、因子スコア回帰（PC1〜3 と平均0にした PC2 負荷による非一様部分）、
      夕方−昼・夕方−夜のコントラスト、時刻別係数を EWC（＋補正 p）で再推論する（全標本・2021年1月除外・FY2023〜25）。

出力（data/processed/）:
  regv3_wind_tb4_ci.csv（A）、regv3_cal4_panelC.csv（B）、regv3_spring_netdemand.csv（C）、regv3_winter_ratio.csv（D）、
  regv3_fo_tables.csv（E）、regv3_kyushu_nuclear.csv（F）、regv3_relative_price.csv（G）、regv3_ex20180906.csv（H）、
  regv3_pca_variance.csv・regv3_pca_tb4_channels.csv・regv3_pca_factor_ewc.csv・regv3_pca_contrasts_ewc.csv・regv3_pca_hourly_ewc.csv・
  regv3_pca_shape_ewc.csv（I。表6.10 の平行・比例シフトの検定を EWC の Wald＋F 補正（LLSW 2018）でやり直したもの）
  figures/hokkaido/price_curve_pca_v3.png（J。図6.6 を EWC の95%帯・EWC の星で描き直したもの。FIG66_ONLY=1 で保存済み CSV から図だけを作る）
限界:
  気温は統制していない。S5・F&O 型（ラグ価格を右辺に含む）は、残差が自己相関する下でラグ価格が内生的になり、係数そのものに偏りがありうる
  （EWC はこれを直さない）。ふるいブートストラップの誤差は X と独立な AR(p) で、補正 p は歪みをやや小さめに示す（37 の限界と同じ）。
  (C) の (i) は風力そのものを含む量で日を分けるので、三分位内の風力の係数は選択の影響を受けうる（(ii) はこれを避ける）。
  (F) の泊3号相当への換算は、九州の原子力の年月内 SD の約3倍の外挿で、九州と北海道の市場規模の違い（需要比約2.8）は扱わない。
"""
import importlib.util
import logging
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
T0 = time.time()

# ---- 37 の推論の実装（実行部の前まで）
_src37 = open(os.path.join(HERE, "37_robust_inference.py"), encoding="utf-8").read()
L37 = {"__file__": os.path.join(HERE, "37_robust_inference.py"), "__name__": "lib37"}
exec(_src37.split("# ================================================================ 実行")[0], L37)
build_daily, design, Fit, inference, boot_summary = (L37[k] for k in ("build_daily", "design", "Fit", "inference", "boot_summary"))
ewc_nu, stars, JAN21, calendar_dummies, SEASON_MAP = (L37[k] for k in ("ewc_nu", "stars", "JAN21", "calendar_dummies", "SEASON_MAP"))
_COS37 = L37["_COS"]
SEED = L37["SEED"]
rng = np.random.default_rng(SEED)
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# ---- 45 の分位点回帰（Frisch–Newton）
_sp = importlib.util.spec_from_file_location("q45", os.path.join(HERE, "45_quantile_moe_v3.py"))
q45 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(q45)
rq_fn = q45.rq_fn

pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 40)
CAL4 = {12: "冬", 1: "冬", 2: "冬", 3: "春", 4: "春", 5: "春", 6: "春", 7: "夏", 8: "夏", 9: "夏", 10: "秋", 11: "秋"}
S3 = ["夏", "冬", "春秋"]
S4N = ["春", "夏", "秋", "冬"]
SLAB = {"夏": "夏", "冬": "冬", "春秋": "不需要期", "春": "春(3-6月)", "秋": "秋(10-11月)"}
SRC = {"solar": "太陽光", "wind": "風力"}
AREAS = [("hokkaido", "p_hokkaido", "北海道"), ("kyushu", "p_kyushu", "九州")]
TOMARI_GWH = 820.8 * 24 / 1000          # 泊3号（91.2万kW×稼働率0.9）の日次発電量
BLOCK = 14


def save(df, name):
    df.to_csv(os.path.join(PROC, name), index=False, encoding="utf-8-sig")


def make_fig66():
    """図6.6 の EWC 版（figures/hokkaido/price_curve_pca_v3.png）。(I) の出力（regv3_pca_hourly_ewc.csv・regv3_pca_contrasts_ewc.csv・
    regv3_pca_shape_ewc.csv・regv3_pca_variance.csv）と、34 の負荷（price_curve_pca_loadings.csv）・比例シフトの当てはめ
    （price_curve_pca_hourly_coef.csv の最小二乗の列。時刻別係数の点推定は OLS で同じ）を読むだけで、推定はしない。
    環境変数 FIG66_ONLY=1 で実行すると、保存済みの CSV から図だけを作る。"""
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
        try:
            font_manager.fontManager.addfont(f)
        except Exception:
            pass
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
    GRAY, C_WIND, C_SOLAR, C_PC = "#595959", "#0079C2", "#D95B20", "#8A5AAB"
    SL = {"夏": "夏\n（7〜9月）", "冬": "冬\n（12〜2月）", "春秋": "不需要期\n（3〜6・10〜11月）"}
    load = pd.read_csv(os.path.join(PROC, "price_curve_pca_loadings.csv"))
    hr = pd.read_csv(os.path.join(PROC, "regv3_pca_hourly_ewc.csv"))
    h34 = pd.read_csv(os.path.join(PROC, "price_curve_pca_hourly_coef.csv"))
    con = pd.read_csv(os.path.join(PROC, "regv3_pca_contrasts_ewc.csv"))
    shp = pd.read_csv(os.path.join(PROC, "regv3_pca_shape_ewc.csv"))
    var = pd.read_csv(os.path.join(PROC, "regv3_pca_variance.csv")).set_index("標本")
    ex21 = var.loc["2021年1月を除く"]
    hcols = [f"h{h:02d}" for h in range(24)]
    specA, specD = "A: FY×季節内の偏差（主仕様、FY2016-25）", "D: FY2023-25（FY×季節内の偏差）"
    names = {1: "第1主成分（水準）", 2: "第2主成分（昼と夕方の差）", 3: "第3主成分（夜と夕方の差）"}

    def st(p):
        return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""

    def fp(p):
        return "<0.01" if p < 0.01 else f"={p:.2f}"

    # 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする。上段・中段・下段を subfigure に分け、
    # 段の見出しに標本を書く。各パネルの夕方−昼・夕方−夜の差と形の検定の p 値は付録の表C.9 にあるので、図には書かない。
    # 主成分の寄与率は図の注に書く（標準出力にも出す）
    fig = plt.figure(figsize=(6.1, 8.8), layout="constrained")
    sf_top, sf_mid, sf_bot = fig.subfigures(3, 1, height_ratios=[0.95, 1.1, 1.12], hspace=0.02)
    sf_top.suptitle("主成分負荷", fontsize=9.5, fontweight="bold")
    axes_top = sf_top.subplots(1, 3)
    for k in (1, 2, 3):
        ax = axes_top[k - 1]
        la = load[(load["仕様"] == specA) & (load["PC"] == k)].iloc[0]
        ld = load[(load["仕様"] == specD) & (load["PC"] == k)].iloc[0]
        ax.axhline(0, color="#BBBBBB", lw=0.8)
        ax.plot(range(24), la[hcols].to_numpy(float), color=C_PC, lw=1.5, label="FY2016〜25")
        ax.plot(range(24), ld[hcols].to_numpy(float), color=C_PC, lw=1.2, ls="--", label="FY2023〜25")
        ax.set_title(names[k], fontsize=8.5, pad=4)
        print(f"  {names[k]}: 寄与率 FY2016〜25 {la['寄与率'] * 100:.0f}%、FY2023〜25 {ld['寄与率'] * 100:.0f}%、"
              f"2021年1月除く {ex21[f'寄与率 PC{k}（共分散）'] * 100:.0f}%")
        ax.set_xticks(range(0, 24, 6))
        ax.set_xlim(-0.5, 23.5)
        ax.tick_params(labelsize=8.5, colors=GRAY)
        ax.set_xlabel("時刻", fontsize=8.5, color=GRAY)
        if k == 1:
            ax.set_ylabel("負荷（単位ベクトル）", fontsize=9, color=GRAY)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    sf_top.legend(*axes_top[0].get_legend_handles_labels(), loc="outside lower center", ncol=2, fontsize=8.5, frameon=False,
                  handlelength=2.0, columnspacing=1.5)
    handles = None
    for sfig, tag in ((sf_mid, "FY2016-25"), (sf_bot, "FY2023-25")):
        sfig.suptitle(f"風力・太陽光の時刻別係数（{tag.replace('-', '〜')}）", fontsize=9.5, fontweight="bold")
        axs = sfig.subplots(1, 3)
        for c, s in enumerate(S3):
            ax = axs[c]
            hs = hr[(hr["標本"] == tag) & hr["係数"].isin([f"wind_{s}", f"solar_{s}"])]
            ymin, ymax = hs["95%下限_EWC"].min(), max(0.25, hs["95%上限_EWC"].max()) + 0.1
            for lo, hi in ((0, 5), (11, 13), (17, 19)):
                ax.axvspan(lo - 0.5, hi + 0.5, color="#F0F0F0", lw=0, zorder=0)
            ax.axhline(0, color="#BBBBBB", lw=0.8)
            for src, col, lab in (("wind", C_WIND, "風力"), ("solar", C_SOLAR, "太陽光")):
                g = hr[(hr["標本"] == tag) & (hr["係数"] == f"{src}_{s}")].sort_values("時刻")
                ax.fill_between(g["時刻"], g["95%下限_EWC"], g["95%上限_EWC"], color=col, alpha=0.15, lw=0)
                ax.plot(g["時刻"], g["推定値"], color=col, lw=1.5, ls="-" if src == "wind" else "--", label=lab)
                if src == "wind":
                    g34 = h34[(h34["標本"] == tag) & (h34["係数"] == f"wind_{s}")].sort_values("時刻")
                    assert np.allclose(g34["推定値"].to_numpy(), g["推定値"].to_numpy(), atol=1e-6)
                    ax.plot(g34["時刻"], g34["比例シフトの当てはめ λ·p̄_h(最小二乗)"], color=col, lw=1.0, ls=":",
                            label="風力の比例シフトの当てはめ（季節の平均価格の定数倍）")
            ax.set_ylim(ymin - 0.05, ymax + 0.05)
            ax.set_xticks(range(0, 24, 6))
            ax.set_xlim(-0.5, 23.5)
            ax.tick_params(labelsize=8.5, colors=GRAY)
            ax.set_title(SL[s], fontsize=8.5, pad=4)
            if tag == "FY2016-25":
                for lo, hi, nm in ((0, 5, "夜"), (11, 13, "昼"), (17, 19, "夕方")):
                    ax.text((lo + hi) / 2, 0.985, nm, ha="center", va="top", fontsize=8.5, color=GRAY, transform=ax.get_xaxis_transform())
            if c == 0:
                ax.set_ylabel("時刻別係数（円/kWh per GWh/日）", fontsize=9, color=GRAY)
            if tag == "FY2023-25":
                ax.set_xlabel("時刻", fontsize=8.5, color=GRAY)
            if tag == "FY2016-25" and c == 0:
                handles, _ = ax.get_legend_handles_labels()
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
    # 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
    sf_bot.legend([handles[0], handles[2], handles[1]],
                  ["風力（95%帯つき）", "太陽光（95%帯つき）", "風力の比例シフトの当てはめ（季節の平均価格の定数倍）"],
                  loc="outside lower center", ncol=2, fontsize=8.5, frameon=False, handlelength=2.0, columnspacing=1.2)
    fig.savefig(os.path.join(ROOT, "figures", "hokkaido", "price_curve_pca_v3.png"), dpi=300)
    plt.close(fig)
    print("saved figures/hokkaido/price_curve_pca_v3.png")


if os.environ.get("FIG66_ONLY") == "1":
    make_fig66()
    sys.exit(0)


def tq(nu, a=0.975):
    return stats.t.ppf(a, nu)


def sd_within(d, src, season, scol):
    """その季節の日の日次発電量の、年度平均からの偏差の SD（年度FE で除いた後に残る変動）"""
    m = d[scol] == season
    x = d.loc[m, src]
    return float((x - x.groupby(d.loc[m, "fy"]).transform("mean")).std())


def ewc_omega(fit, e_list):
    """同じ X の回帰の残差の組から、係数の影響関数の EWC 共分散（係数ごとに len(e_list)×len(e_list)）"""
    nu = ewc_nu(fit.T)
    T = fit.T
    if (T, nu) not in _COS37:
        t = np.arange(1, T + 1) - 0.5
        _COS37[(T, nu)] = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, nu + 1), t) / T)
    C = _COS37[(T, nu)]
    Ls = [C @ fit.grid_of(fit.B * e[:, None]) for e in e_list]     # 各 ν×m
    m = fit.B.shape[1]
    out = np.empty((m, len(e_list), len(e_list)))
    for a in range(len(e_list)):
        for b in range(len(e_list)):
            out[:, a, b] = (Ls[a] * Ls[b]).mean(axis=0)
    return out, nu


def block_index(n, rng_, L=BLOCK):
    nb = int(np.ceil(n / L))
    st = rng_.integers(0, n - L + 1, nb)
    return (st[:, None] + np.arange(L)[None, :]).ravel()[:n]


D = {area: build_daily(area, pcol) for area, pcol, _ in AREAS}
for area in D:
    D[area]["ssn4"] = D[area].index.month.map(CAL4)
ALAB = {a: l for a, _, l in AREAS}


def samples(d):
    return [("FY2016-25", d), ("FY2023-25", d[d["fy"] >= 2023]), ("除2021年1月", d[~JAN21(d.index)])]


# ================================================================ (A) 3季節: 風力・太陽光→TB4h の区間と1SDあたりの上限
print("=== (A) 主仕様（3季節）・年月FE の TB4h 係数の区間と1SDあたりの効果 ===", flush=True)
KEYS3 = [f"{s}_{x}" for x in S3 for s in ("solar", "wind")]
rowsA = []
BASE = {}
for area, _, alab in AREAS:
    for smp, dd in samples(D[area]):
        base = Fit(dd["tb4"], design(dd, "S1"), KEYS3)
        BASE[(area, smp, "tb4")] = base
        for spec in ("S1", "S4"):
            X = design(dd, spec)
            fit = base if spec == "S1" else Fit(dd["tb4"], X, KEYS3)
            res = inference(fit, rng)
            pb, q95, _, info = boot_summary(fit, base, rng, {})
            for k in KEYS3:
                src, s = k.split("_")
                sdw = sd_within(dd, src, s, "season")
                b, se, nu = res.loc[k, "推定値"], res.loc[k, "SE_EWC"], int(res.loc[k, "EWC_ν"])
                lo, hi = b - tq(nu) * se, b + tq(nu) * se
                mtb = float(dd.loc[dd["season"] == s, "tb4"].mean())
                rowsA.append({"エリア": alab, "標本": smp, "仕様": spec, "係数": k, "電源": SRC[src], "季節": SLAB[s], "n": fit.n,
                              "推定値": b, "SE_EWC": se, "EWC_ν": nu, "p_HC3": res.loc[k, "p_HC3"], "p_EWC": res.loc[k, "p_EWC"],
                              "p_補正": pb[k], "95%下限_EWC": lo, "95%上限_EWC": hi,
                              "ブート|t|95%分位": q95[k], "95%下限_ブートt": b - q95[k] * se, "95%上限_ブートt": b + q95[k] * se,
                              "季節内・年度内の日次発電量SD（GWh/日）": sdw, "1SDあたりの効果（円/kWh）": b * sdw,
                              "1SDあたり 95%下限_EWC": lo * sdw, "1SDあたり 95%上限_EWC": hi * sdw,
                              "1SDあたり 95%上限_ブートt": (b + q95[k] * se) * sdw,
                              "その季節の平均TB4h（円/kWh）": mtb, "上限_EWC÷平均TB4h": hi * sdw / mtb,
                              "上限_ブートt÷平均TB4h": (b + q95[k] * se) * sdw / mtb, "点推定÷平均TB4h": b * sdw / mtb})
A = pd.DataFrame(rowsA)
save(A, "regv3_wind_tb4_ci.csv")
show = A[A["電源"] == "風力"].copy()
show["区間(EWC)"] = [f"[{a:+.3f},{b:+.3f}]" for a, b in zip(show["95%下限_EWC"], show["95%上限_EWC"])]
print(show[["エリア", "標本", "仕様", "季節", "推定値", "p_EWC", "p_補正", "区間(EWC)", "季節内・年度内の日次発電量SD（GWh/日）",
            "1SDあたりの効果（円/kWh）", "1SDあたり 95%上限_EWC", "1SDあたり 95%上限_ブートt", "その季節の平均TB4h（円/kWh）",
            "上限_EWC÷平均TB4h", "上限_ブートt÷平均TB4h"]].round(3).to_string(index=False))
print(f"  ({time.time() - T0:.0f}s)", flush=True)

# ================================================================ (B) 暦月4季節（表6.9 パネルC）
print("\n=== (B) 暦月4季節（春3〜6・夏7〜9・秋10〜11・冬12〜2月）の TB4h 係数（表6.9 パネルC） ===", flush=True)
KEYS4 = [f"{s}_{x}" for x in S4N for s in ("solar", "wind")]
rowsB = []
for area, _, alab in AREAS:
    for smp, dd in samples(D[area]):
        Xb = design(dd, "S1", seasons=S4N, season_col="ssn4")
        base = Fit(dd["tb4"], Xb, KEYS4)
        for spec in ("S1", "S4", "S5"):
            X = design(dd, spec, seasons=S4N, season_col="ssn4")
            ok = X.notna().all(axis=1)
            fit = Fit(dd.loc[ok, "tb4"], X[ok], KEYS4)
            res = inference(fit, rng)
            if spec != "S5":
                pb, q95, _, _ = boot_summary(fit, base, rng, {})
            else:
                pb = q95 = pd.Series(np.nan, index=KEYS4)
            for k in KEYS4:
                src, s = k.split("_")
                sdw = sd_within(dd, src, s, "ssn4")
                b, se, nu = res.loc[k, "推定値"], res.loc[k, "SE_EWC"], int(res.loc[k, "EWC_ν"])
                mtb = float(dd.loc[dd["ssn4"] == s, "tb4"].mean())
                rowsB.append({"エリア": alab, "標本": smp, "仕様": spec, "係数": k, "電源": SRC[src], "季節": SLAB[s], "n": fit.n,
                              "推定値": b, "SE_EWC": se, "EWC_ν": nu, "p_HC3": res.loc[k, "p_HC3"], "p_EWC": res.loc[k, "p_EWC"],
                              "p_補正": pb[k], "95%下限_EWC": b - tq(nu) * se, "95%上限_EWC": b + tq(nu) * se,
                              "季節内・年度内の日次発電量SD（GWh/日）": sdw, "1SDあたりの効果（円/kWh）": b * sdw,
                              "1SDあたり 95%上限_EWC": (b + tq(nu) * se) * sdw, "その季節の平均TB4h（円/kWh）": mtb,
                              "星_EWC": stars(res.loc[k, "p_EWC"]), "星_補正": stars(pb[k]) if pb[k] == pb[k] else "",
                              "残差ρ1": fit.resid_rho1()})
        print(f"  {alab} {smp} ({time.time() - T0:.0f}s)", flush=True)
Bt = pd.DataFrame(rowsB)
save(Bt, "regv3_cal4_panelC.csv")
Bt["表示"] = [f"{b:+.3f}{s1}/{s2 if s2 else ('-' if q == q else '.')} (p={p:.3f}, 補正{q:.3f})" if q == q else f"{b:+.3f}{s1} (p={p:.3f})"
              for b, s1, s2, p, q in zip(Bt["推定値"], Bt["星_EWC"], Bt["星_補正"], Bt["p_EWC"], Bt["p_補正"])]
for alab in ("北海道", "九州"):
    g = Bt[Bt["エリア"] == alab]
    print(f"--- {alab} ---")
    print(g.pivot_table(index=["電源", "季節"], columns=["標本", "仕様"], values="表示", aggfunc="first").to_string())
print("--- 1SDあたりの効果（北海道、FY2023-25、春） ---")
print(Bt[(Bt["エリア"] == "北海道") & (Bt["標本"] == "FY2023-25") & (Bt["季節"] == "春(3-6月)")]
      [["仕様", "電源", "推定値", "季節内・年度内の日次発電量SD（GWh/日）", "1SDあたりの効果（円/kWh）", "1SDあたり 95%上限_EWC",
        "その季節の平均TB4h（円/kWh）"]].round(3).to_string(index=False))

# ================================================================ (C) FY2023-25 春の純需要三分位×風力
print("\n=== (C) FY2023〜25 春（3〜6月）: 風力×純需要三分位（EWC） ===", flush=True)
rowsC = []
dh = D["hokkaido"]
d23 = dh[dh["fy"] >= 2023].copy()
for nd_lab, nd in (("(i) 需要−太陽光−風力", d23["demand"] - d23["solar"] - d23["wind"]), ("(ii) 需要−太陽光（風力で条件付けない）", d23["demand"] - d23["solar"])):
    spring = d23["ssn4"] == "春"
    q1, q2 = nd[spring].quantile([1 / 3, 2 / 3])
    ter = pd.Series(np.select([nd <= q1, nd >= q2], ["低", "高"], "中"), index=d23.index).where(spring, "")
    for spec in ("S1", "S4"):
        X = design(d23, spec, seasons=S4N, season_col="ssn4")
        for t in ("低", "中", "高"):
            X[f"wind_春_{t}"] = X["wind_春"] * (ter == t)
        for t in ("中", "高"):
            X[f"ter_{t}"] = (ter == t).astype(float)
        X = X.drop(columns="wind_春")
        keys = [f"wind_春_{t}" for t in ("低", "中", "高")]
        fit = Fit(d23["tb4"], X, keys)
        res = inference(fit, rng)
        # 低−高 の差（同じ回帰の2係数の差: 影響関数の差の EWC）
        i_lo, i_hi = keys.index("wind_春_低"), keys.index("wind_春_高")
        Om, nu = ewc_omega(fit, [fit.e])
        g = fit.grid_of(fit.psi[:, [i_lo]] - fit.psi[:, [i_hi]])
        se_d = float(np.sqrt(L37["ewc_var"](g, nu))[0])
        dlh = res.loc["wind_春_低", "推定値"] - res.loc["wind_春_高", "推定値"]
        for t in ("低", "中", "高"):
            k = f"wind_春_{t}"
            m = ter == t
            rowsC.append({"純需要の定義": nd_lab, "仕様": spec, "三分位": t, "日数": int(m.sum()),
                          "純需要の平均（GWh/日）": float(nd[m].mean()), "風力の平均（GWh/日）": float(d23.loc[m, "wind"].mean()),
                          "TB4h の平均": float(d23.loc[m, "tb4"].mean()), "風力の係数": res.loc[k, "推定値"],
                          "SE_EWC": res.loc[k, "SE_EWC"], "p_EWC": res.loc[k, "p_EWC"], "p_HC3": res.loc[k, "p_HC3"], "EWC_ν": nu,
                          "低−高の差": dlh, "差のSE_EWC": se_d, "差のp_EWC": 2 * stats.t.sf(abs(dlh / se_d), nu)})
C_ = pd.DataFrame(rowsC)
save(C_, "regv3_spring_netdemand.csv")
print(C_.round(3).to_string(index=False))

# ================================================================ (D) 冬の風力: 上位・下位の係数比の集合、平行・比例の検定と検出力
print("\n=== (D) 北海道・冬の風力: 係数比 c の95%集合、平行(c=1)・比例(c=r)、検出力、ブロック・ブートストラップ ===", flush=True)
rowsD = []
k = "wind_冬"
for spec in ("S1", "S4"):
    for smp, dd in samples(dh):
        X = design(dd, spec)
        w = dd["season"] == "冬"
        r = float(dd.loc[w, "top4"].mean() / dd.loc[w, "bot4"].mean())
        ft = Fit(dd["top4"], X, KEYS3)
        fb = Fit(dd["bot4"], X, KEYS3)
        fm = Fit(dd["mean_p"], X, KEYS3)
        i = ft.keys.index(k)
        bt, bb, bm = ft.b()[k], fb.b()[k], fm.b()[k]
        Om, nu = ewc_omega(ft, [ft.e, fb.e])
        Vtt, Vtb, Vbb = Om[i, 0, 0], Om[i, 0, 1], Om[i, 1, 1]
        t2 = tq(nu) ** 2
        a2, a1, a0 = bb ** 2 - t2 * Vbb, -2 * (bt * bb - t2 * Vtb), bt ** 2 - t2 * Vtt
        disc = a1 ** 2 - 4 * a2 * a0
        if a2 > 0 and disc > 0:
            c_lo, c_hi = sorted([(-a1 - np.sqrt(disc)) / (2 * a2), (-a1 + np.sqrt(disc)) / (2 * a2)])
            kind = "有界の区間"
        else:
            c_lo, c_hi, kind = np.nan, np.nan, "非有界（下位の係数が0と区別できない）"
        # 格子での確認
        grid = np.round(np.arange(-3, 8.0001, 0.01), 2)
        tg = (bt - grid * bb) / np.sqrt(Vtt - 2 * grid * Vtb + grid ** 2 * Vbb)
        acc = grid[np.abs(tg) <= tq(nu)]
        se_par = np.sqrt(Vtt - 2 * Vtb + Vbb)
        se_pro = np.sqrt(Vtt - 2 * r * Vtb + r ** 2 * Vbb)
        d_par, d_pro = bt - bb, bt - r * bb
        p_par = 2 * stats.t.sf(abs(d_par / se_par), nu)
        p_pro = 2 * stats.t.sf(abs(d_pro / se_pro), nu)
        # 補正 p（ふるいブートストラップ）: 平行は TB4h、比例は top4−r·bot4。基準は同じ y・同じ標本の S1
        y_par, y_pro = dd["top4"] - dd["bot4"], dd["top4"] - r * dd["bot4"]
        f_par, f_pro = Fit(y_par, X, KEYS3), Fit(y_pro, X, KEYS3)
        pb_par, q_par, _, _ = boot_summary(f_par, Fit(y_par, design(dd, "S1"), KEYS3), rng, {})
        pb_pro, q_pro, _, _ = boot_summary(f_pro, Fit(y_pro, design(dd, "S1"), KEYS3), rng, {})
        # 検出力（5%両側、EWC の t_ν と補正の臨界値）
        tc = tq(nu)
        delta_h1pro = (r - 1) * bb / se_par           # 真が比例（β_top=r·β_bot、β_bot は推定値）のときの平行検定の非心度
        delta_h1par = (1 - r) * bm / se_pro           # 真が平行（両脚とも日平均への効果 β_mean だけ動く）のときの比例検定の非心度
        pw = lambda dl, c: float(1 - stats.nct.cdf(c, nu, dl) + stats.nct.cdf(-c, nu, dl))
        mde = (tc + stats.t.ppf(0.80, nu)) * se_par
        # 日単位の14日移動ブロック・ブートストラップ（r と係数を同時に再標本化）
        rr = np.random.default_rng([SEED, 44, ["S1", "S4"].index(spec), ["FY2016-25", "FY2023-25", "除2021年1月"].index(smp)])
        Xn = X.to_numpy(float)
        Yt, Yb = dd["top4"].to_numpy(), dd["bot4"].to_numpy()
        wv = w.to_numpy()
        jk = list(X.columns).index(k)
        bs = []
        for _ in range(999):
            ix = block_index(len(dd), rr)
            co = np.linalg.lstsq(Xn[ix], np.column_stack([Yt[ix], Yb[ix]]), rcond=None)[0][jk]
            rb = Yt[ix][wv[ix]].mean() / Yb[ix][wv[ix]].mean()
            bs.append((co[0] / co[1], rb, co[0] - rb * co[1], co[0] - co[1]))
        bs = np.array(bs)
        rowsD.append({"仕様": spec, "標本": smp, "n": ft.n, "EWC_ν": nu, "上位の係数": bt, "下位の係数": bb, "日平均への係数": bm,
                      "係数比": bt / bb, "平均価格の比r": r, "冬の上位4h平均": float(dd.loc[w, "top4"].mean()),
                      "冬の下位4h平均": float(dd.loc[w, "bot4"].mean()),
                      "c の95%集合_下": c_lo, "c の95%集合_上": c_hi, "集合の形": kind,
                      "格子での確認_下": acc.min() if len(acc) else np.nan, "格子での確認_上": acc.max() if len(acc) else np.nan,
                      "平行: 上位−下位（=TB4h 係数）": d_par, "平行 SE_EWC": se_par, "平行 p_EWC": p_par, "平行 p_補正": pb_par[k],
                      "比例: 上位−r×下位": d_pro, "比例 SE_EWC": se_pro, "比例 p_EWC": p_pro, "比例 p_補正": pb_pro[k],
                      "比例が真のときの TB4h 係数 (r−1)β_bot": (r - 1) * bb, "その非心度": delta_h1pro,
                      "検出力: 真が比例のとき平行を棄却（EWC）": pw(delta_h1pro, tc),
                      "検出力: 真が比例のとき平行を棄却（補正臨界値）": pw(delta_h1pro, q_par[k]),
                      "検出力: 真が平行のとき比例を棄却（EWC）": pw(delta_h1par, tc),
                      "検出力: 真が平行のとき比例を棄却（補正臨界値）": pw(delta_h1par, q_pro[k]),
                      "80%検出力の最小検出差（TB4h 係数、EWC）": mde,
                      "ブロックBS 係数比 95%下限": np.percentile(bs[:, 0], 2.5), "ブロックBS 係数比 95%上限": np.percentile(bs[:, 0], 97.5),
                      "ブロックBS r 95%下限": np.percentile(bs[:, 1], 2.5), "ブロックBS r 95%上限": np.percentile(bs[:, 1], 97.5),
                      "ブロックBS 上位−r×下位 95%下限": np.percentile(bs[:, 2], 2.5), "ブロックBS 上位−r×下位 95%上限": np.percentile(bs[:, 2], 97.5),
                      "ブロックBS 上位−下位 95%下限": np.percentile(bs[:, 3], 2.5), "ブロックBS 上位−下位 95%上限": np.percentile(bs[:, 3], 97.5)})
    print(f"  {spec} ({time.time() - T0:.0f}s)", flush=True)
Dt = pd.DataFrame(rowsD)
save(Dt, "regv3_winter_ratio.csv")
print(Dt.T.to_string())

# ================================================================ (E) F&O 型（表6.6・6.7）
print("\n=== (E) Fuke and Ohashi 型: TB4h の EWC と IQR 係数のブロック・ブートストラップ ===", flush=True)
_src25 = open(os.path.join(HERE, "25_fo_replication.py"), encoding="utf-8").read().split("all_rows = []")[0]
# 25 は jpholiday（土日＋国民の祝日・振替休日・国民の休日）で祝日を判定した。fenv には jpholiday がないので、
# 同じ規則で作った 37 の祝日の集合に差し替える（25 の代替の「土日＋年末年始・GW」は使わない）
_i0, _i1 = _src25.index("try:\n    import jpholiday"), _src25.index("def fo_season")
_src25 = _src25[:_i0] + "def is_hol(d):\n    return d.weekday() >= 5 or d.date() in HOLIDAYS37\n\n\n" + _src25[_i1:]
L25 = {"__file__": os.path.join(HERE, "25_fo_replication.py"), "__name__": "lib25", "HOLIDAYS37": L37["HOLIDAYS"]}
exec(_src25, L25)
fo_old = pd.read_csv(os.path.join(PROC, "fo_replication_results.csv"))
FO_SPECS = [("kyushu", "p_kyushu", "九州 FY2016–19（F&O再現）", (2016, 2019), False, True),
            ("kyushu", "p_kyushu", "九州 FY2023–25", (2023, 2025), True, False),
            ("hokkaido", "p_hokkaido", "北海道 FY2016–19", (2016, 2019), True, False),
            ("hokkaido", "p_hokkaido", "北海道 FY2023–25", (2023, 2025), True, False)]
B_FO = int(os.environ.get("B_FO", "299"))
rowsE = []
for si, (area, pcol, lab, (f0, f1), ww, bio) in enumerate(FO_SPECS):
    d = L25["build_daily"](area, pcol)
    d = d[(d["fy"] >= f0) & (d["fy"] <= f1)]
    X = L25["design"](d, ww, bio)
    keys = [c for c in X.columns if c.split("_")[0] in ("solar", "wind", "load")]
    fit = Fit(d["tb4"], X, keys)
    res = inference(fit, rng)
    Xn, yv = X.to_numpy(float), d["price"].to_numpy(float)
    cols = list(X.columns)
    jj = [cols.index(c) for c in keys]
    iqr0 = rq_fn(Xn, yv, 0.9)[jj] - rq_fn(Xn, yv, 0.1)[jj]
    rr = np.random.default_rng([SEED, 25, si])
    boots = {"iid": [], "block": []}
    n = len(d)
    for scheme in ("iid", "block"):
        for _ in range(B_FO):
            ix = rr.integers(0, n, n) if scheme == "iid" else block_index(n, rr)
            Xb = Xn[ix]
            keep = Xb.std(axis=0) > 0
            keep[cols.index("const")] = True
            Xb = Xb[:, keep]
            pos = {c: i for i, c in enumerate(np.array(cols)[keep])}
            try:
                b9, b1 = rq_fn(Xb, yv[ix], 0.9), rq_fn(Xb, yv[ix], 0.1)
                boots[scheme].append([b9[pos[c]] - b1[pos[c]] if c in pos else np.nan for c in keys])
            except Exception:
                pass
    old = fo_old[fo_old["sample"] == lab].set_index(["y", "var"])
    for j, kk in enumerate(keys):
        o_iqr = old.loc[("PV時間平均価格（水準）", kk)]
        o_tb = old.loc[("TB4hスプレッド（日内・OLS）", kk)]
        row = {"標本": lab, "係数": kk, "電源": {"solar": "太陽光", "wind": "風力", "load": "需要"}[kk.split("_")[0]],
               "季節": kk.split("_")[1], "n": n, "EWC_ν": int(res.loc[kk, "EWC_ν"]), "残差ρ1(TB4h)": fit.resid_rho1(),
               "TB4h 係数": res.loc[kk, "推定値"], "TB4h p_HC3": res.loc[kk, "p_HC3"], "TB4h p_EWC": res.loc[kk, "p_EWC"],
               "TB4h p_NW14": res.loc[kk, "p_NW14"], "TB4h 星_HC3": stars(res.loc[kk, "p_HC3"]), "TB4h 星_EWC": stars(res.loc[kk, "p_EWC"]),
               "TB4h 95%下限_EWC": res.loc[kk, "推定値"] - tq(res.loc[kk, "EWC_ν"]) * res.loc[kk, "SE_EWC"],
               "TB4h 95%上限_EWC": res.loc[kk, "推定値"] + tq(res.loc[kk, "EWC_ν"]) * res.loc[kk, "SE_EWC"],
               "照合: 25 の TB4h 係数": o_tb["OLS"], "照合: 25 の TB4h p_HC3": o_tb["OLS_p"],
               "IQR 係数": iqr0[j], "照合: 25 の IQR 係数": o_iqr["IQR"], "25 の IQR p（i.i.d. 150回、正規近似）": o_iqr["IQR_p_norm"]}
        for scheme, lab_s in (("iid", "i.i.d. ペア"), ("block", "14日ブロック")):
            bb_ = np.array(boots[scheme])[:, j]
            bb_ = bb_[np.isfinite(bb_)]
            se = bb_.std(ddof=1)
            row[f"IQR SE（{lab_s}、B={B_FO}）"] = se
            row[f"IQR p（{lab_s}、正規近似）"] = 2 * stats.norm.sf(abs(iqr0[j] / se))
            row[f"IQR 95%下限（{lab_s}）"] = np.percentile(bb_, 2.5)
            row[f"IQR 95%上限（{lab_s}）"] = np.percentile(bb_, 97.5)
            row[f"IQR 星（{lab_s}）"] = stars(row[f"IQR p（{lab_s}、正規近似）"])
        rowsE.append(row)
    print(f"  {lab}: n={n}, ν={int(res['EWC_ν'].iloc[0])} ({time.time() - T0:.0f}s)", flush=True)
E = pd.DataFrame(rowsE)
assert np.allclose(E["TB4h 係数"], E["照合: 25 の TB4h 係数"], atol=1e-8), "25 の TB4h 係数を再現しない"
# 分位点回帰は線形計画の厳密解（Frisch–Newton）で、25 の statsmodels（反復重み付き最小二乗）と目的関数値は同じか小さい。
# 目的関数が平らな方向では係数が少し違いうる（九州 FY2023〜25 の τ=0.1 で最大0.03）
dmax = float((E["IQR 係数"] - E["照合: 25 の IQR 係数"]).abs().max())
assert dmax < 0.05, "25 の IQR 係数を再現しない"
save(E, "regv3_fo_tables.csv")
print(f"（25 の TB4h 係数を完全に再現。IQR 係数の 25 との差は最大 {dmax:.4f}）")
print(E[E["電源"] != "需要"][["標本", "係数", "TB4h 係数", "TB4h p_HC3", "TB4h p_EWC", "IQR 係数", "25 の IQR p（i.i.d. 150回、正規近似）",
                             f"IQR p（i.i.d. ペア、正規近似）", f"IQR p（14日ブロック、正規近似）"]].round(3).to_string(index=False))

# ================================================================ (F) 九州の原子力（表8.11）
print("\n=== (F) 九州の原子力（表8.11）: EWC、片側95%上限と泊3号相当、非優越の検定 ===", flush=True)


def build_kyushu_nuclear():
    """33_price_curve_sensitivity.py の build_daily と同じ（九州）"""
    p = pd.read_csv(os.path.join(PROC, "kyushu_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=["p_kyushu"]).copy()
    p["day"] = p["ts"].dt.normalize()
    p["hour"] = p["ts"].dt.hour
    c = p.groupby("day")["hour"].count()
    p = p[p["day"].isin(c[c == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    P = p.pivot(index="day", columns="hour", values="p_kyushu")
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["日平均価格"] = P.mean(axis=1)
    d["上位4h"] = srt[:, -4:].mean(axis=1)
    d["下位4h"] = srt[:, :4].mean(axis=1)
    d["TB4h"] = d["上位4h"] - d["下位4h"]
    d["効率調整後スプレッド"] = 0.85 * d["上位4h"] - d["下位4h"]
    d["完全予見粗利/日"] = np.maximum(0, 3.4 * d["上位4h"] - 4 * d["下位4h"])
    d["下限張り付き時間"] = (P <= 0.011).sum(axis=1)
    g = p.groupby("day")
    d["solar"] = g["solar_pre"].sum() / 1000
    d["wind"] = g["wind_pre"].sum() / 1000
    d["nuclear"] = g["nuclear"].sum(min_count=24) / 1000
    d["demand"] = g["demand"].sum(min_count=24) / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    return d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()


ky = build_kyushu_nuclear()


def design_nuc(d, fe):
    X = pd.DataFrame(index=d.index)
    for s in S3:
        m = (d["season"] == s).astype(float)
        for src in ("solar", "wind", "nuclear"):
            X[f"{src}_{s}"] = d[src] * m
    X["demand"] = d["demand"]
    if fe == "main":
        X = pd.concat([X, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                       pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    else:
        if fe == "ym_cal":
            X = pd.concat([X, calendar_dummies(d.index)], axis=1)
        ym = pd.Series(d.index.year * 100 + d.index.month, index=d.index)
        X = pd.concat([X, pd.get_dummies(ym, prefix="ym", drop_first=True).astype(float)], axis=1)
    X = X.loc[:, X.std() > 0]
    return sm.add_constant(X, has_constant="add")


NKEYS = [f"nuclear_{s}" for s in S3]
YN = ["日平均価格", "上位4h", "下位4h", "TB4h", "効率調整後スプレッド", "完全予見粗利/日", "下限張り付き時間"]
FE_LAB = {"main": "主仕様（FY・季節FE）", "ym": "年月FE（33 と同じ、曜日・祝日なし）", "ym_cal": "年月FE＋曜日・祝日（5.2.3 にそろえた版）"}
kc = pd.read_csv(os.path.join(PROC, "kyushu_nuclear_coef.csv"))
wsd = float((ky["nuclear"] - ky.groupby("fy")["nuclear"].transform("mean")).std())
ymsd = float((ky["nuclear"] - ky.groupby(ky.index.year * 100 + ky.index.month)["nuclear"].transform("mean")).std())
rowsF = []
for fe in ("main", "ym", "ym_cal"):
    X = design_nuc(ky, fe)
    Xmain = design_nuc(ky, "main")
    for y in YN:
        fit = Fit(ky[y], X, NKEYS)
        res = inference(fit, rng)
        if y in ("TB4h", "完全予見粗利/日") and fe in ("main", "ym_cal"):
            pb, _, _, _ = boot_summary(fit, Fit(ky[y], Xmain, NKEYS), rng, {})
        else:
            pb = pd.Series(np.nan, index=NKEYS)
        for kk in NKEYS:
            b, se, nu = res.loc[kk, "推定値"], res.loc[kk, "SE_EWC"], int(res.loc[kk, "EWC_ν"])
            up1 = b + stats.t.ppf(0.95, nu) * se
            delta = 0.5 if y in ("TB4h", "効率調整後スプレッド") else np.nan
            p_ni = float(stats.t.cdf((b - delta / TOMARI_GWH) / se, nu)) if delta == delta else np.nan
            s_ = kk.split("_")[1]
            ref = kc[(kc["仕様"] == ("主仕様・NW14" if fe == "main" else "年月FE・NW14")) & (kc["被説明変数"] == y) &
                     (kc["季節"] == {"春秋": "不需要期"}.get(s_, s_)) & (kc["説明変数"] == "原子力")]
            rowsF.append({"仕様": FE_LAB[fe], "被説明変数": y, "季節": SLAB[s_], "n": fit.n, "EWC_ν": nu, "係数(per GWh/日)": b,
                          "SE_EWC": se, "p_EWC": res.loc[kk, "p_EWC"], "p_NW14(暦日格子)": res.loc[kk, "p_NW14"],
                          "p_HC3": res.loc[kk, "p_HC3"], "p_補正": pb[kk], "星_EWC": stars(res.loc[kk, "p_EWC"]),
                          "95%下限_EWC": b - tq(nu) * se, "95%上限_EWC": b + tq(nu) * se, "片側95%上限": up1,
                          "片側95%上限×19.7GWh/日（泊3号相当）": up1 * TOMARI_GWH, "点推定×19.7GWh/日": b * TOMARI_GWH,
                          "非優越 δ（円/kWh、泊3号相当）": delta, "非優越の片側 p（H0: 19.7β≥δ）": p_ni,
                          "照合: 33 の係数": ref["係数(per GWh/日)"].iloc[0] if (len(ref) and fe != "ym_cal") else np.nan,
                          "照合: 33 の p（NW14、行連続）": ref["p値"].iloc[0] if (len(ref) and fe != "ym_cal") else np.nan})
F = pd.DataFrame(rowsF)
chk = F.dropna(subset=["照合: 33 の係数"])
assert np.allclose(chk["係数(per GWh/日)"], chk["照合: 33 の係数"], atol=6e-5), "33（表8.11）の係数を再現しない"
F["原子力の年度内SD（GWh/日）"] = wsd
F["原子力の年月内SD（GWh/日）"] = ymsd
F["19.7GWh/日÷年月内SD"] = TOMARI_GWH / ymsd
F["九州の日需要÷北海道の日需要"] = ky["demand"].mean() / D["hokkaido"]["demand"].mean()
save(F, "regv3_kyushu_nuclear.csv")
print(f"九州 {len(ky)} 日、原子力 平均 {ky['nuclear'].mean():.1f}、年度内SD {wsd:.1f}、年月内SD {ymsd:.1f} GWh/日"
      f"（19.7GWh/日は年月内SD の {TOMARI_GWH / ymsd:.1f} 倍）、需要比 {F['九州の日需要÷北海道の日需要'].iloc[0]:.2f}")
print(F[F["被説明変数"].isin(["TB4h", "完全予見粗利/日", "上位4h", "下位4h"])]
      [["仕様", "被説明変数", "季節", "係数(per GWh/日)", "p_EWC", "p_NW14(暦日格子)", "p_補正", "片側95%上限×19.7GWh/日（泊3号相当）",
        "非優越の片側 p（H0: 19.7β≥δ）", "照合: 33 の p（NW14、行連続）"]].round(3).to_string(index=False))

# ================================================================ (G) 相対価格（6.5.4）
print("\n=== (G) 相対価格（年度平均で割る）での燃料危機期除外の比較 ===", flush=True)
rowsG = []
for area, _, alab in AREAS:
    d = D[area]
    fym = d.groupby("fy")["mean_p"].transform("mean")
    dd0 = d.assign(rel=d["mean_p"] / fym, rel_tb4=d["tb4"] / fym)
    coefs = {}
    for smp, dd in (("主分析", dd0), ("除FY2021-22", dd0[~dd0["fy"].isin([2021, 2022])])):
        X = design(dd, "S1")
        for y in ("mean_p", "rel", "tb4", "rel_tb4"):
            fit = Fit(dd[y], X, KEYS3)
            res = inference(fit, rng)
            for kk in KEYS3:
                coefs[(smp, y, kk)] = (res.loc[kk, "推定値"], res.loc[kk, "p_EWC"])
    for y in ("mean_p", "rel", "tb4", "rel_tb4"):
        for kk in KEYS3:
            b0, p0 = coefs[("主分析", y, kk)]
            b1, p1 = coefs[("除FY2021-22", y, kk)]
            rowsG.append({"エリア": alab, "被説明変数": {"mean_p": "日平均価格（円）", "rel": "日平均価格（年度平均比）", "tb4": "TB4h（円）",
                                                    "rel_tb4": "TB4h（年度平均価格比）"}[y],
                          "係数": kk, "電源": SRC[kk.split("_")[0]], "季節": SLAB[kk.split("_")[1]], "主分析": b0, "p_EWC 主分析": p0,
                          "除FY2021-22": b1, "p_EWC 除外": p1, "比（除外÷主分析）": b1 / b0})
G = pd.DataFrame(rowsG)
save(G, "regv3_relative_price.csv")
print(G[G["被説明変数"].str.startswith("日平均")].pivot_table(index=["エリア", "電源", "季節"], columns="被説明変数",
                                                         values="比（除外÷主分析）").round(3).to_string())

# ================================================================ (H) 2018-09-06 を除く
print("\n=== (H) 2018-09-06（胆振東部地震の当日）を除いた表6.2 の主仕様（北海道） ===", flush=True)
rowsH = []
d = D["hokkaido"]
dx = d[d.index != pd.Timestamp("2018-09-06")]
for y in ("mean_p", "tb4", "sd"):
    for spec in ("S1", "S4"):
        r0 = inference(Fit(d[y], design(d, spec), KEYS3), rng)
        r1 = inference(Fit(dx[y], design(dx, spec), KEYS3), rng)
        for kk in KEYS3:
            rowsH.append({"被説明変数": L37["YLAB"][y], "仕様": spec, "係数": kk, "全標本": r0.loc[kk, "推定値"], "p_EWC 全標本": r0.loc[kk, "p_EWC"],
                          "2018-09-06 を除く": r1.loc[kk, "推定値"], "p_EWC 除く": r1.loc[kk, "p_EWC"],
                          "差": r1.loc[kk, "推定値"] - r0.loc[kk, "推定値"]})
H = pd.DataFrame(rowsH)
save(H, "regv3_ex20180906.csv")
print(f"係数の差の最大（絶対値）: {H['差'].abs().max():.4f}（{H.loc[H['差'].abs().idxmax(), ['被説明変数', '仕様', '係数']].tolist()}）、"
      f"星（EWC）が変わる係数: {int((H['p_EWC 全標本'].map(stars) != H['p_EWC 除く'].map(stars)).sum())} 本")
print(H[H["差"].abs() > 0.01].round(3).to_string(index=False))

# ================================================================ (I) 主成分分解: 2021年1月除外と EWC
print("\n=== (I) 価格カーブの主成分分解: 2021年1月除外の感応度と EWC ===", flush=True)
_sp34 = importlib.util.spec_from_file_location("pca34", os.path.join(HERE, "34_price_curve_pca.py"))
m34 = importlib.util.module_from_spec(_sp34)
_sp34.loader.exec_module(m34)
d34, P34 = m34.build_daily()
assert len(d34) == 3632
cell = (d34["fy"].astype(str) + "_" + d34["season"]).to_numpy()
jan = JAN21(d34.index)
fyv = d34["fy"].to_numpy()
is23 = fyv >= 2023
KEYS34 = m34.KEYS


def dev_within(keep):
    Pk = P34[keep]
    return Pk - Pk.groupby(cell[keep]).transform("mean").to_numpy()


variants = {"全標本（FY2016-25）": np.ones(len(d34), bool), "2021年1月を除く": ~jan,
            "FY2020冬を除く": ~((fyv == 2020) & (d34["season"] == "冬").to_numpy()), "FY2020-22を除く": ~np.isin(fyv, [2020, 2021, 2022]),
            "FY2023-25": is23}
ss = (dev_within(np.ones(len(d34), bool)).to_numpy() ** 2).sum(axis=1)
rowsV = []
wA, VA = m34.pca(dev_within(np.ones(len(d34), bool)).to_numpy())
for lab, keep in variants.items():
    dev = dev_within(keep).to_numpy()
    w, V = m34.pca(dev)
    wc = np.linalg.eigvalsh(np.corrcoef(dev.T))[::-1]
    Pk = P34[keep]
    gk = Pk.groupby(cell[keep])
    zs = ((Pk - gk.transform("mean")) / gk.transform("std")).to_numpy()
    wz = np.linalg.eigvalsh(np.cov(zs.T))[::-1]
    Fw = pd.DataFrame(dev @ V[:, :5], index=d34.index[keep], columns=[f"PC{k}" for k in range(1, 6)])
    yc = d34.loc[keep, "tb4"] - d34.loc[keep, "tb4"].groupby(cell[keep]).transform("mean")
    rowsV.append({"標本": lab, "日数": int(keep.sum()),
                  **{f"寄与率 PC{k}（共分散）": w[k - 1] / w.sum() for k in (1, 2, 3)},
                  **{f"寄与率 PC{k}（相関行列）": wc[k - 1] / wc.sum() for k in (1, 2, 3)},
                  **{f"寄与率 PC{k}（セル内標準化）": wz[k - 1] / wz.sum() for k in (1, 2, 3)},
                  **{f"cos(負荷PC{k}, 全標本)": abs(float(V[:, k - 1] @ VA[:, k - 1])) for k in (1, 2, 3)},
                  "PC2 負荷の和": float(V[:, 1].sum()), "PC1 負荷 12時": V[12, 0], "PC1 負荷 18時": V[18, 0], "PC1 負荷 3時": V[3, 0],
                  "TB4h（セル内）の PC1 だけの R2": sm.OLS(yc, sm.add_constant(Fw[["PC1"]])).fit().rsquared,
                  "TB4h（セル内）の PC1-5 の R2": sm.OLS(yc, sm.add_constant(Fw)).fit().rsquared,
                  "偏差平方和に占める2021年1月の割合（全標本のみ）": float(ss[jan].sum() / ss.sum()) if lab.startswith("全標本") else np.nan})
Vt = pd.DataFrame(rowsV)
save(Vt, "regv3_pca_variance.csv")
print(Vt.round(3).T.to_string())

# 経路分解（TB4h、全標本・2021年1月除外・FY2023-25）と因子回帰の EWC
rowsT, rowsFa = [], []
for lab, keep, load_lab in (("FY2016-25", np.ones(len(d34), bool), "A（自標本の主成分）"), ("FY2016-25 除2021年1月", ~jan, "A′（除外後の主成分）"),
                            ("FY2023-25", is23, "D（FY2023-25 の主成分）")):
    ds = d34[keep]
    Ps = P34[keep]
    if lab == "FY2023-25":
        _, V = m34.pca(dev_within(np.ones(len(d34), bool)).to_numpy()[is23])
        devB = (P34 - P34.mean()).to_numpy()[keep]
    else:
        _, V = m34.pca(dev_within(keep).to_numpy())
        devB = (Ps - Ps.mean()).to_numpy()
    F_ = pd.DataFrame(devB @ V[:, :5], index=ds.index, columns=[f"PC{k}" for k in range(1, 6)])
    Xs = design(ds, "S1")
    beta = {k: sm.OLS(F_[f"PC{k}"], Xs).fit().params for k in range(1, 6)}
    cz = sm.OLS(ds["tb4"], pd.concat([Xs, F_], axis=1)).fit()
    direct = sm.OLS(ds["tb4"], Xs).fit()
    for kk in KEYS34:
        lvl = cz.params["PC1"] * beta[1][kk]
        shp = sum(cz.params[f"PC{k}"] * beta[k][kk] for k in range(2, 6))
        rowsT.append({"標本": lab, "負荷": load_lab, "係数": kk, "TB4h への効果": direct.params[kk], "PC1（水準）経由": lvl,
                      "PC2-5（形状）経由": shp, "残差（PC6以下と非線形）": direct.params[kk] - lvl - shp})
    v2c = V[:, 1] - V[:, 1].mean()
    ys = {"PC1": F_["PC1"], "PC2": F_["PC2"], "PC3": F_["PC3"], "PC2 の非一様部分 (v2−mean v2)'p": pd.Series(devB @ v2c, index=ds.index)}
    base_tb = None
    for ylab, yv in ys.items():
        fit = Fit(yv, Xs, KEYS34)
        res = inference(fit, rng)
        for kk in KEYS34:
            rowsFa.append({"標本": lab, "負荷": load_lab, "被説明変数": ylab, "係数": kk, "推定値": res.loc[kk, "推定値"],
                           "SE_EWC": res.loc[kk, "SE_EWC"], "p_EWC": res.loc[kk, "p_EWC"], "p_NW14(暦日格子)": res.loc[kk, "p_NW14"],
                           "p_HC3": res.loc[kk, "p_HC3"], "星_EWC": stars(res.loc[kk, "p_EWC"]), "PC2 負荷の和": float(V[:, 1].sum()),
                           "EWC_ν": int(res.loc[kk, "EWC_ν"])})
Tt = pd.DataFrame(rowsT)
Fa = pd.DataFrame(rowsFa)
save(Tt, "regv3_pca_tb4_channels.csv")
save(Fa, "regv3_pca_factor_ewc.csv")
old_ch = pd.read_csv(os.path.join(PROC, "price_curve_pca_tb4_channels.csv"))
o = old_ch[(old_ch["標本"] == "FY2016-25") & (old_ch["係数"] == "wind_冬")].iloc[0]
n_ = Tt[(Tt["標本"] == "FY2016-25") & (Tt["係数"] == "wind_冬")].iloc[0]
assert abs(o["PC1（水準）経由"] - n_["PC1（水準）経由"]) < 1e-6, "34 の経路分解を再現しない"
print("経路分解（34 の全標本の値を再現）:")
print(Tt.round(3).to_string(index=False))
fa_show = Fa[Fa["被説明変数"].isin(["PC1", "PC2", "PC2 の非一様部分 (v2−mean v2)'p"])].copy()
fa_show["表示"] = [f"{b:+.3f}{s or '-'} (p={p:.3f}; NW14 {q:.3f})" for b, s, p, q in zip(fa_show["推定値"], fa_show["星_EWC"], fa_show["p_EWC"], fa_show["p_NW14(暦日格子)"])]
print(fa_show.pivot_table(index=["被説明変数", "係数"], columns="標本", values="表示", aggfunc="first").to_string())

# コントラストの EWC と補正 p
rowsK = []
for lab, keep in (("FY2016-25", np.ones(len(d34), bool)), ("FY2016-25 除2021年1月", ~jan), ("FY2023-25", is23)):
    ds = d34[keep]
    Xs = design(ds, "S1")
    for ycol, ylab in (("eve_mid", "夕方(17-19)−昼(11-13)"), ("eve_night", "夕方(17-19)−夜(0-5)")):
        fit = Fit(ds[ycol], Xs, KEYS34)
        res = inference(fit, rng)
        pb, _, _, _ = boot_summary(fit, fit, rng, {})
        for kk in KEYS34:
            b, se, nu = res.loc[kk, "推定値"], res.loc[kk, "SE_EWC"], int(res.loc[kk, "EWC_ν"])
            rowsK.append({"標本": lab, "被説明変数": ylab, "係数": kk, "推定値": b, "SE_EWC": se, "EWC_ν": nu,
                          "p_EWC": res.loc[kk, "p_EWC"], "p_補正": pb[kk], "p_NW14(暦日格子)": res.loc[kk, "p_NW14"],
                          "p_HC3": res.loc[kk, "p_HC3"], "95%下限_EWC": b - tq(nu) * se, "95%上限_EWC": b + tq(nu) * se,
                          "星_EWC": stars(res.loc[kk, "p_EWC"]), "星_補正": stars(pb[kk])})
    print(f"  コントラスト {lab} ({time.time() - T0:.0f}s)", flush=True)
K = pd.DataFrame(rowsK)
old_con = pd.read_csv(os.path.join(PROC, "price_curve_pca_contrasts.csv"))
oc = old_con[(old_con["標本"] == "FY2016-25") & (old_con["被説明変数"] == "夕方(17-19)−昼(11-13)") & (old_con["係数"] == "wind_冬")]["推定値"].iloc[0]
assert abs(oc - K[(K["標本"] == "FY2016-25") & (K["被説明変数"].str.startswith("夕方(17-19)−昼")) & (K["係数"] == "wind_冬")]["推定値"].iloc[0]) < 1e-8
save(K, "regv3_pca_contrasts_ewc.csv")
K["表示"] = [f"{b:+.3f}{s or '-'}/{t or '-'} (EWC {p:.3f}, 補正 {q:.3f}, NW14 {r:.3f})" for b, s, t, p, q, r in
             zip(K["推定値"], K["星_EWC"], K["星_補正"], K["p_EWC"], K["p_補正"], K["p_NW14(暦日格子)"])]
print(K.pivot_table(index=["被説明変数", "係数"], columns="標本", values="表示", aggfunc="first").to_string())

# 時刻別係数の EWC の95%帯
rowsHr = []
for lab, keep in (("FY2016-25", np.ones(len(d34), bool)), ("FY2023-25", is23)):
    ds = d34[keep]
    Xs = design(ds, "S1")
    for h in range(24):
        fit = Fit(P34.loc[keep, h], Xs, KEYS34)
        res = inference(fit, rng)
        for kk in KEYS34:
            b, se, nu = res.loc[kk, "推定値"], res.loc[kk, "SE_EWC"], int(res.loc[kk, "EWC_ν"])
            rowsHr.append({"標本": lab, "係数": kk, "時刻": h, "推定値": b, "SE_EWC": se, "SE_NW14(暦日格子)": res.loc[kk, "SE_NW14"],
                           "95%下限_EWC": b - tq(nu) * se, "95%上限_EWC": b + tq(nu) * se, "EWC_ν": nu})
save(pd.DataFrame(rowsHr), "regv3_pca_hourly_ewc.csv")

# 時刻別係数ベクトルの平行・比例シフトの検定（表6.10）を EWC で: 24本の影響関数の EWC 長期分散 Ω（24×24）から
# Wald 統計量 W = (Rb)'(RΩR')^{-1}(Rb) を作り、LLSW (2018) の F 補正 F=(ν−q+1)/(νq)·W ~ F(q, ν−q+1) で p を求める。
# 制約は 34 と同じ（平行: 全時刻の係数が等しい、比例: b ∈ span(p̄)、p̄ はその標本・季節の時刻別平均価格。4時間ブロック平均の5制約と23制約）
rowsS = []
for lab, keep in (("FY2016-25", np.ones(len(d34), bool)), ("FY2016-25 除2021年1月", ~jan), ("FY2023-25", is23)):
    ds = d34[keep]
    Ps = P34[keep]
    Xs = design(ds, "S1")
    fit0 = Fit(Ps[0], Xs, KEYS34)
    Bh = np.linalg.lstsq(fit0.Xn, Ps.to_numpy(float), rcond=None)[0]
    Eh = Ps.to_numpy(float) - fit0.Xn @ Bh
    nu = ewc_nu(fit0.T)
    if (fit0.T, nu) not in _COS37:
        tt_ = np.arange(1, fit0.T + 1) - 0.5
        _COS37[(fit0.T, nu)] = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, nu + 1), tt_) / fit0.T)
    Cm = _COS37[(fit0.T, nu)]
    for i, kk in enumerate(KEYS34):
        b = Bh[fit0.rows[i]]
        Lam = Cm @ fit0.grid_of(fit0.B[:, [i]] * Eh)               # ν×24
        Om = Lam.T @ Lam / nu
        pbar = Ps[(ds["season"] == kk.split("_")[1]).to_numpy()].mean().to_numpy()
        tests = {"平行(縮約5)": m34.R_PAR5, "平行(23)": m34.R_PAR23,
                 "比例(縮約5)": m34.null_basis(m34.BLK @ pbar) @ m34.BLK, "比例(23)": m34.null_basis(pbar)}
        row = {"標本": lab, "係数": kk, "EWC_ν": nu, "時刻平均": b.mean(), "最小": b.min(), "最大": b.max()}
        for nm, R in tests.items():
            q_ = R.shape[0]
            Rb = R @ b
            W = float(Rb @ np.linalg.solve(R @ Om @ R.T, Rb))
            Fst = (nu - q_ + 1) / (nu * q_) * W
            row[f"p {nm}（EWC・F補正）"] = float(stats.f.sf(Fst, q_, nu - q_ + 1)) if nu - q_ + 1 > 0 else np.nan
        rowsS.append(row)
Sh = pd.DataFrame(rowsS)
save(Sh, "regv3_pca_shape_ewc.csv")
print("\n=== 時刻別係数の平行・比例シフトの検定（EWC、F 補正） ===")
print(Sh.round(3).to_string(index=False))
print(f"\nsaved regv3_*.csv（{time.time() - T0:.0f}s）")

# ================================================================ (J) 図6.6 の EWC 版
make_fig66()
