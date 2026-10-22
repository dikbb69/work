#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""市場分断の再分類（表6.3）と記述統計の頑健化（図6.4 の区間・表7.3 の分断列・第4章の記述統計・表6.1 の帯域分解）

監査 A6-6・A6-3-2（表6.3 の「本州」の誤称と直書きの代表値）、A6-7（風力の多い日に増える安値分断の内訳）、
A6-5（図6.4 の五分位の端点差の不確実性）、A4-6（記述統計の表の欠落）、A6-3（表6.1 の導入量の趨勢）に答える。

手法:
  (1) 市場分断の3者比較（data/raw/jepx/spot_summary_2016〜2025.csv、30分コマ、FY2016〜25。北海道エリアプライスが欠測の
      FY2018 の960コマ（胆振東部地震後）を除く）。判定はいずれも ±0.01円。
      (a) 北海道 vs システムプライス（表6.3 の旧定義。システムプライスは全国の無制約価格で「本州の価格」ではない）
      (b) 北海道 vs 東北（北本連系線の分断）  (c) 東北 vs 東京（東北東京間連系線）  (d) 東京 vs システム（東西の周波数変換設備 FC 等）
      年度別・期間プール（FY2016〜19・FY2016〜18・FY2019〜22・FY2020〜22・FY2023〜25）の構成比と、北海道≠システムのコマが
      どの連系線で分かれたかの内訳を出す。表の値はすべてこの出力から取る（直書きの代表値は使わない）。
      旧計算（10_hokkaido_quick_xlsx.py の h5。欠測コマを分母に含める）の値も並べ、FY2018 の 92.3% の由来を示す。
  (2) 風力三分位×安値分断の内訳（hokkaido_hourly_panel.csv の60分値、FY2023〜25、24時間そろう日。表7.3 と同じ三分位）:
      安値分断（北海道＜システム−0.01）を (i) 北本の拘束（かつ 北海道＜東北−0.01）と (ii) 東日本側（かつ |北海道−東北|≤0.01）に分け、
      季節×三分位の h/日 と、(i)・(ii) の時間の北本連系線の潮流（送電＝−interconn、MW）の分布を出す。三分位の「大−小」の差には
      14日の移動ブロック・ブートストラップ（日単位、B=999）の95%区間を付ける。
  (3) 図6.4 の五分位（FY2023〜25、季節内、日次の制御前発電量）の群平均と端点差（Q5−Q1）の95%区間: FY2023〜25 の暦日の並びで
      日を14日ブロックで復元抽出し（B=999）、抽出した日の中で季節別に五分位を作り直す。図に群平均の95%区間を誤差棒で付けた版を出す。
  (4) 第4章・付録A の記述統計: 北海道・九州の 24時間がそろう日（FY2016〜25 と FY2023〜25）について、日平均価格・TB4h・日内SD・
      需要・制御前太陽光・制御前風力・下限張り付き時間（≤0.011円）の N・平均・SD・最小・中央値・最大。時間値版、季節別版、
      2018-09-06（胆振東部地震の当日。価格は前日に約定済みだが需要・発電は停電で崩れた日）を除いた版、
      導入量（期首・期末）と年度平均の設備利用率（制御前出力÷月次導入量）を補足に出す。
  (5) 表6.1 の帯域分解を設備利用率（cf）の系列で: 21_band_comparison.py の band_shares を、制御前出力と、制御前出力÷月次導入量
      （area_capacity_series.csv。2026年1〜3月は2025年12月の値で延長）に当てる。FY2023〜25（6.4 と同じ期間）を主、
      FY2022〜25 の MWh 基準（現行の表6.1）を参考に並べ、太陽光の <6h 帯が日周の決定的な形から来ることを
      年月×時刻の平均で置き換えた系列で確かめる。

出力: data/processed/market_split_v3_by_fy.csv、market_split_v3_pooled.csv、market_split_v3_route.csv、
      market_split_v3_wind_tercile.csv、market_split_v3_export.csv、
      gen_quintile_ci_v3.csv、descriptive_stats_v3.csv、descriptive_stats_v3_hourly.csv、descriptive_stats_v3_season.csv、
      descriptive_capacity_v3.csv、band_shares_cf_v3.csv、figures/hokkaido/gen_vs_price_shape_ci.png
限界: 市場分断の判定はエリアプライスの一致で見るので、どの連系線が拘束したかは価格の並びからの推定である（約定時の連系線の空き容量の
      データはリポジトリにない）。(ii) の部分を北海道の風力の効果と識別することはできない（北海道と東北の風力は同じ気象で動く）。
      記述統計の五分位・三分位は他の要因を統制しない。2026年1〜3月の導入量は外挿（直近値の延長）である。
"""
import glob
import logging
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

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
RAW = os.path.join(ROOT, "data", "raw", "jepx")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
SEED = 20261021
EPS = 0.01
B_DESC = int(os.environ.get("B_DESC", "999"))
L_BLOCK = 14
SEASONS = {"夏": [7, 8, 9], "冬": [12, 1, 2], "不需要期": [3, 4, 5, 6, 10, 11]}
SMAP = {m: s for s, ms in SEASONS.items() for m in ms}
PERIODS = {"FY2016-19": (2016, 2019), "FY2016-18": (2016, 2018), "FY2019-22": (2019, 2022), "FY2020-22": (2020, 2022),
           "FY2023-25": (2023, 2025)}
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
rng_master = np.random.default_rng(SEED)


def save(df, name):
    df.to_csv(os.path.join(PROC, name), index=False, encoding="utf-8-sig")


def cls(a, b):
    return np.where(a > b + EPS, "高", np.where(a < b - EPS, "低", "同"))


def block_days(nd, rng):
    nb = int(np.ceil(nd / L_BLOCK))
    st = rng.integers(0, nd - L_BLOCK + 1, nb)
    return (st[:, None] + np.arange(L_BLOCK)[None, :]).ravel()[:nd]


# ================================================================ (1) 市場分断の3者比較
fs = sorted(glob.glob(os.path.join(RAW, "spot_summary_20*.csv")))
J = pd.concat([pd.read_csv(f, encoding="shift_jis") for f in fs], ignore_index=True)
J = J[["受渡日", "時刻コード", "システムプライス(円/kWh)", "エリアプライス北海道(円/kWh)", "エリアプライス東北(円/kWh)",
       "エリアプライス東京(円/kWh)"]]
J.columns = ["date", "koma", "sys", "hk", "th", "tk"]
J["date"] = pd.to_datetime(J["date"])
J = J.drop_duplicates(["date", "koma"])
J["fy"] = J["date"].dt.year - (J["date"].dt.month < 4).astype(int)
J = J[(J["fy"] >= 2016) & (J["fy"] <= 2025)].reset_index(drop=True)
n_all = len(J)
miss = J[["hk", "th", "tk", "sys"]].isna().any(axis=1)
print(f"=== (1) JEPX スポット 30分コマ: FY2016〜25 {n_all:,} コマ、価格の欠測 {int(miss.sum())} コマ"
      f"（{', '.join(f'FY{k} {v}' for k, v in J[miss].groupby('fy').size().items())}） ===")
# 旧計算（欠測コマを分母に含める、10 の h5）
old = J.assign(hi=J["hk"] > J["sys"] + EPS, lo=J["hk"] < J["sys"] - EPS).groupby("fy")[["hi", "lo"]].mean().mul(100)
J = J[~miss].reset_index(drop=True)
J["HS"] = cls(J["hk"], J["sys"])
J["HT"] = cls(J["hk"], J["th"])
J["TT"] = cls(J["th"], J["tk"])
J["KS"] = cls(J["tk"], J["sys"])
COMP = {"HS": "北海道 vs システムプライス", "HT": "北海道 vs 東北（北本連系線）", "TT": "東北 vs 東京（東北東京間）",
        "KS": "東京 vs システムプライス（東西）"}


# 北海道≠システムのコマを、価格の並びから分断の場所に割り当てる（北本→東北東京間→東京とシステムの順に最初の不一致）
J["route"] = np.select([J["HT"] != "同", J["TT"] != "同", J["KS"] != "同"],
                       ["北本で分断（北海道≠東北）", "北海道＝東北、東北東京間で分断（東北≠東京）",
                        "北海道＝東北＝東京、東京≠システム（東西など）"], "北海道＝東北＝東京＝システム±0.01（丸め）")

rows = []
for key, lab in COMP.items():
    for fy, g in J.groupby("fy"):
        vc = g[key].value_counts(normalize=True).mul(100)
        rows.append({"比較": lab, "記号": key, "年度": f"FY{fy}", "コマ数": len(g),
                     "高（左＞右+0.01）%": vc.get("高", 0.0), "同（±0.01円以内）%": vc.get("同", 0.0), "低（左＜右−0.01）%": vc.get("低", 0.0)})
byfy = pd.DataFrame(rows)
o2 = old.reset_index().rename(columns={"hi": "旧計算_高値分断%（欠測を分母に含む）", "lo": "旧計算_安値分断%（欠測を分母に含む）"})
o2["年度"] = "FY" + o2["fy"].astype(str)
byfy = byfy.merge(o2.drop(columns="fy"), on="年度", how="left")
byfy.loc[byfy["記号"] != "HS", ["旧計算_高値分断%（欠測を分母に含む）", "旧計算_安値分断%（欠測を分母に含む）"]] = np.nan
save(byfy, "market_split_v3_by_fy.csv")

prow = []
for per, (f0, f1) in PERIODS.items():
    g = J[(J["fy"] >= f0) & (J["fy"] <= f1)]
    for key, lab in COMP.items():
        vc = g[key].value_counts(normalize=True).mul(100)
        yr = byfy[(byfy["記号"] == key) & byfy["年度"].isin([f"FY{y}" for y in range(f0, f1 + 1)])]
        prow.append({"期間": per, "比較": lab, "記号": key, "コマ数": len(g),
                     "高%（プール）": vc.get("高", 0.0), "同%（プール）": vc.get("同", 0.0), "低%（プール）": vc.get("低", 0.0),
                     "高%の年度レンジ": f"{yr['高（左＞右+0.01）%'].min():.1f}〜{yr['高（左＞右+0.01）%'].max():.1f}",
                     "同%の年度レンジ": f"{yr['同（±0.01円以内）%'].min():.1f}〜{yr['同（±0.01円以内）%'].max():.1f}",
                     "低%の年度レンジ": f"{yr['低（左＜右−0.01）%'].min():.1f}〜{yr['低（左＜右−0.01）%'].max():.1f}"})
pooled = pd.DataFrame(prow)
save(pooled, "market_split_v3_pooled.csv")

rrows = []
for side, lab in (("高", "高値分断（北海道＞システム+0.01）"), ("低", "安値分断（北海道＜システム−0.01）")):
    sub = J[J["HS"] == side]
    for unit, grp in [("年度", sub["fy"].map(lambda v: f"FY{v}"))] + \
                     [("期間", sub["fy"].map(lambda v, p=p: p if PERIODS[p][0] <= v <= PERIODS[p][1] else None)) for p in PERIODS]:
        for k, g in sub.groupby(grp):
            if k is None:
                continue
            vc = g["route"].value_counts(normalize=True).mul(100)
            ht = g["HT"].value_counts(normalize=True).mul(100)
            rrows.append({"区分": lab, "単位": unit, "年度・期間": k, "コマ数": len(g),
                          "北本で分断%": vc.get("北本で分断（北海道≠東北）", 0.0),
                          "うち北海道＞東北%": ht.get("高", 0.0), "うち北海道＜東北%": ht.get("低", 0.0),
                          "北海道＝東北・東北東京間で分断%": vc.get("北海道＝東北、東北東京間で分断（東北≠東京）", 0.0),
                          "北海道＝東北＝東京・東京≠システム%": vc.get("北海道＝東北＝東京、東京≠システム（東西など）", 0.0),
                          "丸めの残り%": vc.get("北海道＝東北＝東京＝システム±0.01（丸め）", 0.0),
                          "北海道＝東北の計%": ht.get("同", 0.0)})
rt = pd.DataFrame(rrows).drop_duplicates(["区分", "単位", "年度・期間"])
save(rt, "market_split_v3_route.csv")

print("\n--- 表6.3 パネルA: 北海道 vs システムプライス（コマ構成比%、欠測を除く） ---")
print(pooled[pooled["記号"] == "HS"][["期間", "コマ数", "高%（プール）", "同%（プール）", "低%（プール）", "高%の年度レンジ", "低%の年度レンジ"]]
      .round(1).to_string(index=False))
print("--- 表6.3 パネルB: 北海道 vs 東北（北本連系線） ---")
print(pooled[pooled["記号"] == "HT"][["期間", "高%（プール）", "同%（プール）", "低%（プール）", "高%の年度レンジ", "同%の年度レンジ", "低%の年度レンジ"]]
      .round(1).to_string(index=False))
print("--- 参考: 東北 vs 東京、東京 vs システム ---")
print(pooled[pooled["記号"].isin(["TT", "KS"])][["期間", "比較", "高%（プール）", "同%（プール）", "低%（プール）"]].round(1).to_string(index=False))
print("--- 年度別（高/同/低%） ---")
tt = byfy.assign(v=[f"{a:.1f}/{b:.1f}/{c:.1f}" for a, b, c in zip(byfy["高（左＞右+0.01）%"], byfy["同（±0.01円以内）%"], byfy["低（左＜右−0.01）%"])])
print(tt.pivot(index="年度", columns="記号", values="v")[["HS", "HT", "TT", "KS"]].to_string())
print("旧計算（欠測を分母に含む）の高値分断%:", old["hi"].round(1).to_dict())
print("--- 北海道≠システムのコマの分断の場所（期間プール、%） ---")
print(rt[rt["単位"] == "期間"].drop(columns="単位").round(1).to_string(index=False))
print("--- 同（年度別、FY2023〜25） ---")
print(rt[(rt["単位"] == "年度") & rt["年度・期間"].isin(["FY2023", "FY2024", "FY2025"])].drop(columns="単位").round(1).to_string(index=False))

# ================================================================ 日次パネル（北海道、時間値）
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
hp["solar_pre"] = hp["solar"].fillna(0) + hp["solar_curt"].fillna(0)

# ================================================================ (2) 風力三分位×安値分断の内訳（表7.3 と同じ日・三分位）
p = hp[(hp["fy"] >= 2023) & (hp["fy"] <= 2025)].dropna(subset=["p_hokkaido"]).copy()
cnt = p.groupby("day")["hour"].count()
p = p[p["day"].isin(cnt[cnt == 24].index)].copy()
p["low"] = p["p_hokkaido"] < p["p_system"] - EPS
p["low_hb"] = p["low"] & (p["p_hokkaido"] < p["p_tohoku"] - EPS)
p["low_east"] = p["low"] & ((p["p_hokkaido"] - p["p_tohoku"]).abs() <= EPS)
p["low_other"] = p["low"] & ~p["low_hb"] & ~p["low_east"]
p["hk_lt_th"] = p["p_hokkaido"] < p["p_tohoku"] - EPS
p["hk_gt_th"] = p["p_hokkaido"] > p["p_tohoku"] + EPS
p["export"] = -p["interconn"]                     # パネルは「負＝域外送電」に統一（付録A）
dd = p.groupby("day").agg(wind=("wind_pre", "sum"), low=("low", "sum"), low_hb=("low_hb", "sum"), low_east=("low_east", "sum"),
                          low_other=("low_other", "sum"), hklt=("hk_lt_th", "sum"), hkgt=("hk_gt_th", "sum"))
dd["season"] = dd.index.month.map(SMAP)
# 三分位は表7.3（35_option_layers.py の tercile_table）と同じ規則: 1/3分位点以下を「小」、2/3分位点以上を「大」
dd["ter"] = dd.groupby("season")["wind"].transform(
    lambda x: pd.Series(np.select([x <= x.quantile(1 / 3), x >= x.quantile(2 / 3)], ["小", "大"], "中"), index=x.index))
VARS = {"low": "安値分断（北海道＜システム）h/日", "low_hb": "(i) 北本の拘束（かつ北海道＜東北）h/日",
        "low_east": "(ii) 東日本側（かつ北海道＝東北）h/日", "low_other": "その他（かつ北海道＞東北）h/日",
        "hklt": "参考: 北海道＜東北（全時間）h/日", "hkgt": "参考: 北海道＞東北（全時間）h/日"}
trow = []
for s in SEASONS:
    g = dd[dd["season"] == s]
    for t in ("小", "中", "大"):
        h = g[g["ter"] == t]
        trow.append({"季節": s, "風力三分位": t, "日数": len(h), "風力GWh/日": h["wind"].mean() / 1000,
                     **{VARS[v]: h[v].mean() for v in VARS}})
# 「大−小」の差の区間（14日の移動ブロック・ブートストラップ。FY2023〜25 の日の並びで抽出し、三分位は元の分類を保つ）
dsort = dd.sort_index()
rng = np.random.default_rng([SEED, 2])
bd = {s: {v: [] for v in VARS} for s in SEASONS}
for _ in range(B_DESC):
    smp = dsort.iloc[block_days(len(dsort), rng)]
    for s in SEASONS:
        g = smp[smp["season"] == s]
        m = g.groupby("ter")[list(VARS)].mean()
        for v in VARS:
            bd[s][v].append(m.loc["大", v] - m.loc["小", v])
for s in SEASONS:
    g = dd[dd["season"] == s]
    m = g.groupby("ter")[list(VARS)].mean()
    r = {"季節": s, "風力三分位": "大−小", "日数": np.nan, "風力GWh/日": np.nan}
    for v in VARS:
        lo, hi = np.percentile(bd[s][v], [2.5, 97.5])
        r[VARS[v]] = m.loc["大", v] - m.loc["小", v]
        r[VARS[v] + " 95%下限"] = lo
        r[VARS[v] + " 95%上限"] = hi
    r["(i)の増加が安値分断の増加に占める比率"] = (m.loc["大", "low_hb"] - m.loc["小", "low_hb"]) / (m.loc["大", "low"] - m.loc["小", "low"])
    r["(ii)の増加が安値分断の増加に占める比率"] = (m.loc["大", "low_east"] - m.loc["小", "low_east"]) / (m.loc["大", "low"] - m.loc["小", "low"])
    trow.append(r)
ter = pd.DataFrame(trow)
save(ter, "market_split_v3_wind_tercile.csv")
chk = ter[ter["風力三分位"].isin(["小", "大"])][["季節", "風力三分位", VARS["low"]]]
t73 = pd.read_csv(os.path.join(PROC, "table73_refresh.csv"))
t73 = t73[t73["区分"] == "本表（現データ）"][["季節", "風力三分位", "安値分断(h/日)"]]
mm = chk.merge(t73, on=["季節", "風力三分位"])
assert np.allclose(mm[VARS["low"]], mm["安値分断(h/日)"]), "表7.3（table73_refresh.csv）の安値分断を再現しない"
print(f"\n=== (2) 風力三分位×安値分断の内訳（FY2023〜25、{len(dd)} 日。安値分断の列は table73_refresh.csv と一致） ===")
print(ter[[c for c in ter.columns if "95%" not in c]].round(2).to_string(index=False))
print(f"--- 大−小の95%区間（14日ブロック、B={B_DESC}） ---")
print(ter[ter["風力三分位"] == "大−小"][["季節"] + [c for c in ter.columns if "95%" in c]].round(2).to_string(index=False))

erow = []
for lab, msk in [("(i) 北本の拘束（安値分断かつ北海道＜東北）", p["low_hb"]), ("(ii) 東日本側（安値分断かつ北海道＝東北）", p["low_east"]),
                 ("北海道＜東北の全時間", p["hk_lt_th"]), ("安値分断でない時間", ~p["low"]), ("全時間", p["low"] | ~p["low"])]:
    x = p.loc[msk, "export"].dropna()
    erow.append({"時間の区分": lab, "時間数": int(msk.sum()), "送電（MW）中央値": x.median(), "送電 p25": x.quantile(0.25),
                 "送電 p75": x.quantile(0.75), "送電 p90": x.quantile(0.9), "送電≥500MW の比率": (x >= 500).mean(),
                 "送電≥800MW の比率": (x >= 800).mean()})
exp_ = pd.DataFrame(erow)
save(exp_, "market_split_v3_export.csv")
print("--- 北本連系線の潮流（送電＝−interconn、MW、FY2023〜25 の60分値） ---")
print(exp_.round(3).to_string(index=False))

# ================================================================ (3) 図6.4 の五分位の端点差の区間
q = hp[(hp["ts"] >= "2023-04-01") & (hp["ts"] < "2026-04-01")].dropna(subset=["p_hokkaido"]).copy()
cnt = q.groupby("day")["hour"].count()
q = q[q["day"].isin(cnt[cnt == 24].index)]
P = q.pivot(index="day", columns="hour", values="p_hokkaido")
srt = np.sort(P.to_numpy(), axis=1)
D = pd.DataFrame(index=P.index)
D["level"] = P.mean(axis=1)
D["tb4"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
D["wind"] = q.groupby("day")["wind_pre"].sum() / 1000
D["solar"] = q.groupby("day")["solar_pre"].sum() / 1000
D["season"] = D.index.month.map(SMAP)
D = D.sort_index()


def quint(d, var):
    k = pd.qcut(d[var], 5, labels=False)
    return d.groupby(k).agg(x=(var, "mean"), level=("level", "mean"), tb4=("tb4", "mean"))


point = {(v, s): quint(D[D["season"] == s], v) for v in ("wind", "solar") for s in SEASONS}
rng = np.random.default_rng([SEED, 3])
boot = {k: [] for k in point}
for _ in range(B_DESC):
    smp = D.iloc[block_days(len(D), rng)]
    for (v, s) in point:
        boot[(v, s)].append(quint(smp[smp["season"] == s], v)[["level", "tb4"]].to_numpy())
qrows = []
for (v, s), g in point.items():
    bb = np.array(boot[(v, s)])                       # B×5×2
    for j, yv in enumerate(("level", "tb4")):
        dif = bb[:, 4, j] - bb[:, 0, j]
        lo, hi = np.percentile(dif, [2.5, 97.5])
        qlo, qhi = np.percentile(bb[:, :, j], [2.5, 97.5], axis=0)
        qrows.append({"電源": {"wind": "風力", "solar": "太陽光"}[v], "季節": s, "指標": {"level": "日平均価格", "tb4": "TB4h"}[yv],
                      "日数": int((D["season"] == s).sum()), "Q5−Q1": g[yv].iloc[4] - g[yv].iloc[0], "95%下限": lo, "95%上限": hi,
                      "区間が0を含む": bool(lo <= 0 <= hi),
                      **{f"Q{k + 1}平均": g[yv].iloc[k] for k in range(5)},
                      **{f"Q{k + 1}の95%下限": qlo[k] for k in range(5)}, **{f"Q{k + 1}の95%上限": qhi[k] for k in range(5)},
                      **{f"Q{k + 1}発電量GWh/日": g["x"].iloc[k] for k in range(5)}})
qci = pd.DataFrame(qrows)
save(qci, "gen_quintile_ci_v3.csv")
print(f"\n=== (3) 図6.4 の五分位の端点差 Q5−Q1（FY2023〜25、{len(D)} 日、14日ブロック・ブートストラップ B={B_DESC}） ===")
print(qci[["電源", "季節", "指標", "Q5−Q1", "95%下限", "95%上限", "区間が0を含む"] + [f"Q{k}平均" for k in range(1, 6)]].round(2).to_string(index=False))

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
C_LEVEL, C_SPREAD = "#2a78d6", "#eb6834"
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする。行を季節、列を電源（風力・太陽光）にする
SLAB_FIG = {"夏": "夏（7〜9月）", "冬": "冬（12〜2月）", "不需要期": "不需要期（3〜6・10〜11月）"}
fig, axes = plt.subplots(3, 2, figsize=(6.1, 7.6), sharey=True, layout="constrained")
for c, (v, collab) in enumerate([("wind", "風力の日次発電量（GWh/日、制御前）"), ("solar", "太陽光の日次発電量（GWh/日、制御前）")]):
    for r, s in enumerate(SEASONS):
        ax = axes[r, c]
        g = point[(v, s)]
        for yv, col, mk, lab in (("level", C_LEVEL, "o", "日平均価格（水準）"), ("tb4", C_SPREAD, "s", "TB4h（形状）")):
            rr = qci[(qci["電源"] == {"wind": "風力", "solar": "太陽光"}[v]) & (qci["季節"] == s) &
                     (qci["指標"] == {"level": "日平均価格", "tb4": "TB4h"}[yv])].iloc[0]
            lo = np.array([rr[f"Q{k}の95%下限"] for k in range(1, 6)])
            hi = np.array([rr[f"Q{k}の95%上限"] for k in range(1, 6)])
            ax.errorbar(g["x"], g[yv], yerr=[g[yv] - lo, hi - g[yv]], color=col, lw=1.4, ls="-" if yv == "level" else "--",
                        marker=mk, ms=4, capsize=0, elinewidth=1.0, markeredgecolor="white", markeredgewidth=0.6, label=lab)
            # 第5五分位と第1五分位の差と95%区間（図の注で説明する）
            _txt = (f"{'日平均価格の差' if yv == 'level' else 'TB4h の差'} {rr['Q5−Q1']:+.1f}円 "
                    f"[{rr['95%下限']:+.1f}, {rr['95%上限']:+.1f}]").replace("-", "−")
            ax.text(0.03, 0.03 if yv == "level" else 0.135, _txt, transform=ax.transAxes, fontsize=8.5, color=INK)
        if r == 0:
            ax.set_title({"wind": "風力", "solar": "太陽光"}[v], fontsize=9.5, color=INK)
        if r == 2:
            ax.set_xlabel(collab, fontsize=9, color=MUTED)
        if c == 0:
            ax.set_ylabel(f"{SLAB_FIG[s]}\n（円/kWh）", fontsize=9, color=INK)
        ax.set_ylim(1.0, 15.0)
        ax.grid(axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=8.5)
h_, l_ = axes[0, 0].get_legend_handles_labels()
fig.legend(h_, l_, fontsize=8.5, frameon=False, loc="outside upper center", ncol=2)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "gen_vs_price_shape_ci.png"), dpi=300)
plt.close(fig)


# ================================================================ (4) 記述統計
def area_daily(area, pcol):
    a = pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])
    a["fy"] = a["ts"].dt.year - (a["ts"].dt.month < 4).astype(int)
    a = a[(a["fy"] >= 2016) & (a["fy"] <= 2025)].copy()
    a["day"] = a["ts"].dt.normalize()
    a["hour"] = a["ts"].dt.hour
    a["solar_pre"] = a["solar"] + a["solar_curt"].fillna(0)
    a["wind_pre"] = a["wind"] + a["wind_curt"].fillna(0)
    Pp = a.pivot(index="day", columns="hour", values=pcol)
    s2 = np.sort(Pp.to_numpy(), axis=1)
    d = pd.DataFrame(index=Pp.index)
    d["日平均価格（円/kWh）"] = Pp.mean(axis=1, skipna=False)
    d["TB4h（円/kWh）"] = s2[:, -4:].mean(1) - s2[:, :4].mean(1)
    d["日内SD（円/kWh）"] = Pp.std(axis=1, skipna=False)
    g = a.groupby("day")
    d["需要（GWh/日）"] = g["demand"].sum(min_count=24) / 1000
    d["太陽光・制御前（GWh/日）"] = g["solar_pre"].sum(min_count=24) / 1000
    d["風力・制御前（GWh/日）"] = g["wind_pre"].sum(min_count=24) / 1000
    d["下限張り付き時間（h/日）"] = (Pp <= 0.011).sum(axis=1).astype(float)
    d.loc[Pp.isna().any(axis=1), "下限張り付き時間（h/日）"] = np.nan
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d = d.dropna()
    a = a[a["day"].isin(d.index)]
    return d, a


def describe(x):
    return {"N": int(x.count()), "平均": x.mean(), "SD": x.std(), "最小": x.min(), "中央値": x.median(), "最大": x.max()}


drows, hrows, srows = [], [], []
dailies = {}
for area, pcol, alab in (("hokkaido", "p_hokkaido", "北海道"), ("kyushu", "p_kyushu", "九州")):
    d, a = area_daily(area, pcol)
    dailies[alab] = d
    variants = [("FY2016-25", d), ("FY2023-25", d[d["fy"] >= 2023])]
    if area == "hokkaido":
        variants.append(("FY2016-25（2018-09-06 を除く）", d[d.index != pd.Timestamp("2018-09-06")]))
    for per, x in variants:
        for c in [c for c in d.columns if c != "fy"]:
            drows.append({"エリア": alab, "期間": per, "変数": c, **describe(x[c])})
    for per, (f0, f1) in (("FY2016-25", (2016, 2025)), ("FY2023-25", (2023, 2025))):
        x = d[(d["fy"] >= f0) & (d["fy"] <= f1)]
        sx = x.index.month.map(SMAP)
        for s in SEASONS:
            for c in [c for c in d.columns if c != "fy"]:
                srows.append({"エリア": alab, "期間": per, "季節": s, "変数": c, **describe(x.loc[sx == s, c])})
        ah = a[(a["fy"] >= f0) & (a["fy"] <= f1)]
        for c, lab in ((pcol, "価格（円/kWh）"), ("demand", "需要（MW）"), ("solar_pre", "太陽光・制御前（MW）"),
                       ("wind_pre", "風力・制御前（MW）")):
            hrows.append({"エリア": alab, "期間": per, "変数": lab, **describe(ah[c])})
        hrows.append({"エリア": alab, "期間": per, "変数": "下限張り付き（≤0.011円）の時間比率", "N": int(ah[pcol].count()),
                      "平均": float((ah[pcol] <= 0.011).mean()), "SD": np.nan, "最小": np.nan, "中央値": np.nan, "最大": np.nan})
desc = pd.DataFrame(drows)
save(desc, "descriptive_stats_v3.csv")
save(pd.DataFrame(hrows), "descriptive_stats_v3_hourly.csv")
save(pd.DataFrame(srows), "descriptive_stats_v3_season.csv")
nchk = desc[desc["変数"] == "日平均価格（円/kWh）"].set_index(["エリア", "期間"])["N"]
assert nchk[("北海道", "FY2016-25")] == 3632 and nchk[("九州", "FY2016-25")] == 3632, "日数が 3,632 と一致しない"
assert nchk[("北海道", "FY2023-25")] == 1096 and nchk[("九州", "FY2023-25")] == 1096, "日数が 1,096 と一致しない"
print("\n=== (4) 日次の記述統計（24時間がそろう日。N は北海道・九州とも FY2016〜25 3,632、FY2023〜25 1,096 と一致） ===")
print(desc.round(2).to_string(index=False))
print("--- 時間値 ---")
print(pd.DataFrame(hrows).round(3).to_string(index=False))
d9 = dailies["北海道"].loc["2018-09-06"]
print("2018-09-06 の北海道:", {k: round(float(v), 2) for k, v in d9.items()})

# 導入量（期首・期末）と年度平均の設備利用率
cap = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
crow = []
for area, f, alab in (("hokkaido", "hokkaido_hourly_panel.csv", "北海道"), ("kyushu", "kyushu_hourly_panel.csv", "九州")):
    c = cap[cap["area"] == area].set_index("date")[["solar_kw", "wind_kw"]].sort_index()
    for src in ("solar", "wind"):
        crow.append({"エリア": alab, "電源": {"solar": "太陽光", "wind": "風力"}[src], "区分": "導入量（万kW）",
                     "FY2016期首（2016-03末）": c.loc["2016-03-31", f"{src}_kw"] / 1e4,
                     "FY2023期首（2023-03末）": c.loc["2023-03-31", f"{src}_kw"] / 1e4,
                     "直近（2025-12末、FY2025期末の代わり）": c[f"{src}_kw"].iloc[-1] / 1e4})
    a = pd.read_csv(os.path.join(PROC, f), parse_dates=["ts"])
    a["fy"] = a["ts"].dt.year - (a["ts"].dt.month < 4).astype(int)
    a = a[(a["fy"] >= 2016) & (a["fy"] <= 2025)].copy()
    a["me"] = a["ts"].dt.to_period("M").dt.to_timestamp("M")
    full = pd.date_range(c.index.min(), "2026-03-31", freq="ME")
    cc = c.reindex(full.union(c.index)).ffill()
    a = a.merge(cc, left_on="me", right_index=True, how="left")
    for src in ("solar", "wind"):
        pre = a[src].fillna(0) + a[f"{src}_curt"].fillna(0)
        cf = (pre / (a[f"{src}_kw"] / 1000)).groupby(a["fy"]).mean()
        crow.append({"エリア": alab, "電源": {"solar": "太陽光", "wind": "風力"}[src], "区分": "年度平均の設備利用率（制御前、%）",
                     **{f"FY{fy}": 100 * v for fy, v in cf.items()}})
hcf = pd.read_csv(os.path.join(PROC, "hokkaido_cf_series.csv"), parse_dates=["ts"])
hcf["fy"] = hcf["ts"].dt.year - (hcf["ts"].dt.month < 4).astype(int)
for src in ("solar", "wind"):
    v = hcf[(hcf["fy"] >= 2016) & (hcf["fy"] <= 2025)].groupby("fy")[f"cf_{src}"].mean()
    crow.append({"エリア": "北海道", "電源": {"solar": "太陽光", "wind": "風力"}[src], "区分": "参考: hokkaido_cf_series.csv の年度平均（%）",
                 **{f"FY{fy}": 100 * x for fy, x in v.items()}})
capdf = pd.DataFrame(crow)
save(capdf, "descriptive_capacity_v3.csv")
print("--- 導入量と設備利用率 ---")
print(capdf.round(1).to_string(index=False))


# ================================================================ (5) 表6.1 の帯域分解を設備利用率の系列で
def band_shares(x):
    """21_band_comparison.py と同一（移動平均カスケード、分散シェア%）"""
    x = x.interpolate()
    ma6 = x.rolling(6, center=True, min_periods=3).mean()
    ma24 = x.rolling(24, center=True, min_periods=12).mean()
    ma168 = x.rolling(168, center=True, min_periods=84).mean()
    comps = {"<6時間": x - ma6, "6-24時間": ma6 - ma24, "1-7日": ma24 - ma168, ">7日": ma168 - x.mean()}
    tot = x.var()
    return {k: float(v.var() / tot * 100) for k, v in comps.items()}


brow = []
for area, f, alab in (("hokkaido", "hokkaido_hourly_panel.csv", "北海道"), ("kyushu", "kyushu_hourly_panel.csv", "九州")):
    a = pd.read_csv(os.path.join(PROC, f), parse_dates=["ts"])
    a["wind_pre"] = a["wind"].fillna(0) + a["wind_curt"].fillna(0)
    a["solar_pre"] = a["solar"].fillna(0) + a["solar_curt"].fillna(0)
    c = cap[cap["area"] == area].set_index("date")[["solar_kw", "wind_kw"]].sort_index()
    full = pd.date_range(c.index.min(), "2026-07-31", freq="ME")
    c = c.reindex(full.union(c.index)).ffill()
    a["me"] = a["ts"].dt.to_period("M").dt.to_timestamp("M")
    a = a.merge(c, left_on="me", right_index=True, how="left")
    a["cf_wind"] = a["wind_pre"] / (a["wind_kw"] / 1000)
    a["cf_solar"] = a["solar_pre"] / (a["solar_kw"] / 1000)
    a["fy"] = a["ts"].dt.year - (a["ts"].dt.month < 4).astype(int)
    a["ym"] = a["ts"].dt.to_period("M")
    a["h"] = a["ts"].dt.hour
    for per, (t0, t1) in (("FY2023-25", ("2023-04-01", "2026-04-01")), ("FY2022-25", ("2022-04-01", "2026-04-01"))):
        s = a[(a["ts"] >= t0) & (a["ts"] < t1)].set_index("ts")
        for src, col, basis in (("風力", "cf_wind", "設備利用率"), ("風力", "wind_pre", "MWh"),
                                ("太陽光", "cf_solar", "設備利用率"), ("太陽光", "solar_pre", "MWh")):
            brow.append({"エリア": alab, "電源": src, "期間": per, "系列": basis, **band_shares(s[col])})
        sd = a[(a["ts"] >= t0) & (a["ts"] < t1)].copy()
        for src, col in (("太陽光", "solar_pre"), ("風力", "wind_pre")):
            det = sd.groupby(["ym", "h"])[col].transform("mean")
            brow.append({"エリア": alab, "電源": src, "期間": per, "系列": "参考: 年月×時刻の平均（気象を含まない決定的な形）",
                         **band_shares(pd.Series(det.to_numpy(), index=sd["ts"]))})
    for src, col in (("風力", "cf_wind"), ("風力", "wind_pre")):
        for per, fys in (("FY2023-25 年度別の平均", range(2023, 2026)), ("FY2022-25 年度別の平均", range(2022, 2026))):
            r = pd.DataFrame([band_shares(a[a["fy"] == fy].set_index("ts")[col]) for fy in fys]).mean().to_dict()
            brow.append({"エリア": alab, "電源": src, "期間": per, "系列": "設備利用率" if col.startswith("cf") else "MWh", **r})
band = pd.DataFrame(brow)
band["日内（<6h+6-24h）"] = band["<6時間"] + band["6-24時間"]
band["1日超（1-7日+>7日）"] = band["1-7日"] + band[">7日"]
save(band, "band_shares_cf_v3.csv")
print("\n=== (5) 帯域分解（分散シェア%、非直交） ===")
print(band.round(1).to_string(index=False))
print("\nsaved market_split_v3_*.csv, gen_quintile_ci_v3.csv, descriptive_stats_v3*.csv, descriptive_capacity_v3.csv, "
      "band_shares_cf_v3.csv, figures/hokkaido/gen_vs_price_shape_ci.png")
