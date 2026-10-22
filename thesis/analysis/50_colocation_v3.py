#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""併設蓄電池の価値の再計算（v3）、5円超の抑制の再解釈、併設の参入が立つ抑制率の閾値、負価格の移転の年度推移、Weitzman の傾き

第9章 9.3（9.3.1・9.3.2・9.3.3、表9.1）と第10章 10.4・10.5 の数値を作り直す。30_btm_avoidable.py（表9.1）の
フリート集約の考え方を引き継ぎ、①（エリア価格の裁定）と②（抑制回避）の二重計上を除いて評価する。

手法:
  (A) 抑制の記述（9.3.1）: 北海道の風力の抑制率＝Σ出力制御量/(Σ発電実績＋Σ出力制御量) を年度・月別に。抑制が起きた時間の
      エリア価格の帯（下限0.01円・0.01〜5円・5円超）の構成を、時間ベースとエネルギーベースで。
  (B) 5円超の抑制の再解釈（9.3.1 の注・付録の表）: 2025/4〜2026/6 の wind_curt>0 かつ北海道価格>5円の時間を、
      (i) 太陽光の抑制が同じ時間にある、(ii) 同じ日に下限張り付きの時間がある、(iii) 再エネ（太陽光か風力）の抑制が
      連続する時間帯の最初か最後の時間、(iv) ローカル制御（66kV 岩松線・富川線）の日時にあたる、に分類し、時間数と電力量で集計する。
      ローカル制御の日・時間帯・量は OCCTO の検証資料「流通設備混雑による再生可能エネルギー発電設備（自然変動電源）の
      出力抑制の検証結果」（北海道電力ネットワーク、2025年11月分・2026年5月分・6月分。本体の「実施状況」と別紙1〜3）から
      転記し、data/processed/local_congestion_control_occto.csv に出す。別紙2 では、抑制の対象は両系統とも区分 F（太陽光）の
      ノンファーム電源だけで、区分 G（風力）は「―」（連系なし）。したがってローカル制御による風力の抑制は0で、
      パネルの風力の出力制御量はすべてエリア全体の需給バランス制約による。太陽光のローカル制御の量は、各日・各時間に
      最大抑制量が続いたとする上限で評価する。2025年12月〜2026年4月分の公表は見つからない（実施がなかったとみなす）。
      パネルの太陽光の出力制御量はローカル制御を含む（エリア全体の制御がない2026年5〜6月の日に、公表された時間帯だけに
      1〜2.5MW が現れる。2025年11月の0.4MW はパネルの 0.5MWh 刻みより小さく現れない）。2026-10-21 の検証で検算を追加。
      参考として、旧来の仮定（2025年11月以降の全日、各時間 min(風力抑制, 8MW)。監査の再計算と同じ）の上限も残す。
      30分値（JEPX スポットの北海道エリアプライス）で、該当時間に下限のコマを含むかも確かめる。
  (C) 併設蓄電池の価値（9.3.2・表9.1 の拡張）: 日ごとの線形計画（1日1サイクル、出力1kW、容量 d kWh、放電側効率0.85、
      日の終わりに空、充電と放電の合計が出力以内）で、蓄電池1kW あたりの
        ① V1 ＝ 系統からの裁定: Σ0.85·p·放電 − Σ(p+w)·系統充電（w＝充電従量負担 1,752/(365×4)＝1.2円/kWh）
        ①＋② V12 ＝ ①に、抑制電力量からの充電（費用0、放電1kWh につき0.85×FIP プレミアム）を加えて同時に最適化
        ② の増分 ＝ V12 − V1（系統から充電する場合に比べた増分。吸収した電力量×(0.85×プレミアム＋その時間のエリア価格＋w) に近い）
      を求める。抑制電力量は、併設仕様（風力1kW あたり E kWh、放電 d 時間 → 蓄電池 E/d kW）で風力フリートに比例配分する
      （一様）か、容量シェア20%のサイトに77%が集中する（集中。30 と同じ）。プレミアムは2・3・4円。
      比較に、14円/kWh×吸収量（エネルギー価値を含む粗い上限。①と加算できない）と、FIT 電源の併設（系統から充電できず
      ①がない。②＝0.85×FIT 価格×吸収量。FIT 価格は14円で代用）を出す。
      期間は 2025/4〜2026/6・FY2025（年度の実績）・FY2026 4〜6月。抑制率のシナリオは、FY2026 4〜6月の時間値を
      比例的に拡大する方法（イベントが大きくなり回避率が下がる、下限側。各時間は抑制前の出力を上限とする。年値は×365/91）と、
      回避率を表9.1 の値で一定とする方法（上限側）の2通りで、年率1.35〜37%。
  (D) 併設の参入条件（9.3.3、RQ4 の後半）: π_spot'＋②＋κP − c_req^併設 を、資本費2.3・4.0・6.8万円/kWh、WACC 6・8%、
      4時間・2時間、κP あり（4時間のみ、12,517円）・なし、c_req の2定義で計算し、ゼロになる抑制率（年率）を求める。
        c_req「系統用と同じ」＝ d×資本費×CRF＋運維・廃止＋託送等固定0.69万（①は充電従量負担を控除した値、②は系統充電に対する増分）
        c_req「併設」＝ 託送等固定を発電所と共有し系統から充電しない（①は自社の発電の時間移動: 充電従量負担がなく、
        貯めた分のプレミアムを0.15×プレミアムだけ失う。②は自社の発電の時間移動に対する増分＝吸収量×(p＋プレミアム)）
      ①の水準は D1 の実績整合（4時間: 戦略c の FY2023〜25 平均8,427−1,752＝6,675円/kW-年。2時間は実績価格の上で戦略c を
      2時間で直接計算した FY2023〜25 平均−876）を主に、4時間はモデル直値（5,850）と旧0.81×π_PF（4,943）、2時間は旧0.81×π_PF
      （2,948）を下側の参考にする。K=0（参入に有利な側）。
  (E) 負価格の移転と抑制の影の価格（10.4、表10.2 の再計算）: 下限張り付き時間の再エネの発電実績（販売された電力量）と
      抑制前の出力（32 の定義）の両方で、移転額 Σ出力×(0.01+c) と、抑制の影の価格 Σ抑制量×c の比を年度別に。
  (F) Weitzman (1974) の当てはめの点検（10.5）: 限界便益の傾き（π(K) の K に対する傾き、円/kW-年 per 万kW）を
      T1 の pi_k_curve_v3.csv（41。仕様A 26・完全予見の増分貪欲・刻み1万kW。D1 の実績整合を主、モデル直値・旧0.81×π_PF を併記）
      から、負価格の下限（−5・−10円）の場合を参考に negative_price_scenarios.csv（32、旧基準、K=0・50・100 の行だけ）から求め、
      限界費用の傾き（参入必要収益 c_req の K に対する傾き）を資本費の系列から示す。
出力: data/processed/curtailment_price_bands.csv, curtailment_above5_classification.csv, local_congestion_control_occto.csv, btm_local_value.csv,
      btm_entry_threshold.csv, btm_entry_breakeven_capex.csv, negative_price_transfer_v2.csv, weitzman_slopes.csv,
      figures/hokkaido/btm_entry_threshold.png
限界: 抑制電力量の地点別の分布は公表されておらず、一様と集中は境界として読む。抑制率のシナリオは観察された時間構造の
      比例拡大で、将来の抑制の時間帯・季節の変化は扱わない（年値は4〜6月の構造が通年に続くとした値）。価格は実績のまま
      （吸収による価格の変化はない、price taker）。1日1サイクルの線形計画は完全予見で上界。FIP の0.01円のコマの扱い
      （プレミアムを交付しない）により、抑制時に貯めた電力のプレミアムは放電した電力量に付く。本計算もそう置く。FIT 価格は案件ごとに違う。
      ローカル制御の量は暫定措置の日区分ごとの最大抑制量で、実際の時間別の抑制量は公表されていない（上限で評価）。
      FIP の0.01円のコマのプレミアム不交付（交付しない額を他のコマに割り付ける「調整後プレミアム単価」）は資源エネルギー庁の
      審議会資料の記述で確認したが、本文の頁は未照合。
"""
import os

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
from matplotlib import font_manager
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")
FIG = os.path.join(ROOT, "figures", "hokkaido")
for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
pd.set_option("display.width", 250)

FLOOR = 0.011
ETA = 0.85
W_CHG = 1752 / (365 * 4)   # 充電従量負担（円/kWh）。第8章の1,752円/kW-年（4時間×365日）を1kWh あたりに

P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
cap = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
cap = cap[cap["area"] == "hokkaido"].set_index("date")["wind_kw"]
full = pd.date_range(cap.index.min(), pd.Timestamp("2026-06-30"), freq="ME")
cap = cap.reindex(full.union(cap.index)).ffill()
P["wind_kw"] = P["ts"].dt.to_period("M").dt.to_timestamp("M").map(cap)
for c in ("wind_curt", "solar_curt", "wind", "solar"):
    P[c] = P[c].fillna(0.0)
P["date"] = P["ts"].dt.normalize()
P["floor"] = P["p_hokkaido"] <= FLOOR

# ============================================================================================
# (A) 抑制率と価格帯の構成
# ============================================================================================
rows = []
for fy, g in P[P["fy"] >= 2022].groupby("fy"):
    q = g[g["wind_curt"] > 0]
    band = np.where(q["p_hokkaido"] <= FLOOR, "下限", np.where(q["p_hokkaido"] <= 5, "0.01〜5円", "5円超"))
    r = dict(区分="年度", 期間=f"FY{fy}" + ("（4〜6月）" if fy == 2026 else ""),
             風力抑制率pct=round(g["wind_curt"].sum() / (g["wind"].sum() + g["wind_curt"].sum()) * 100, 3),
             抑制時間h=len(q), 抑制電力量MWh=round(q["wind_curt"].sum(), 1))
    for b in ("下限", "0.01〜5円", "5円超"):
        r[f"時間シェア_{b}pct"] = round((band == b).mean() * 100, 1) if len(q) else np.nan
        r[f"電力量シェア_{b}pct"] = round(q.loc[band == b, "wind_curt"].sum() / q["wind_curt"].sum() * 100, 1) if len(q) else np.nan
    rows.append(r)
win = P[(P["ts"] >= "2025-04-01") & (P["ts"] < "2026-07-01")]
qq = win[win["wind_curt"] > 0]
bb = np.where(qq["p_hokkaido"] <= FLOOR, "下限", np.where(qq["p_hokkaido"] <= 5, "0.01〜5円", "5円超"))
r = dict(区分="期間計", 期間="2025/4〜2026/6", 風力抑制率pct=round(win["wind_curt"].sum() / (win["wind"].sum() + win["wind_curt"].sum()) * 100, 3),
         抑制時間h=len(qq), 抑制電力量MWh=round(qq["wind_curt"].sum(), 1))
for b in ("下限", "0.01〜5円", "5円超"):
    r[f"時間シェア_{b}pct"] = round((bb == b).mean() * 100, 1)
    r[f"電力量シェア_{b}pct"] = round(qq.loc[bb == b, "wind_curt"].sum() / qq["wind_curt"].sum() * 100, 1)
rows.append(r)
mon = win.groupby(win["ts"].dt.to_period("M")).agg(c=("wind_curt", "sum"), w=("wind", "sum"))
for m, x in mon.iterrows():
    rows.append(dict(区分="月", 期間=str(m), 風力抑制率pct=round(x["c"] / (x["w"] + x["c"]) * 100, 3), 抑制電力量MWh=round(x["c"], 1)))
A = pd.DataFrame(rows)
A.to_csv(os.path.join(PROC, "curtailment_price_bands.csv"), index=False)
print("=== (A) 風力の抑制率と抑制時間のエリア価格の帯 ===")
print(A[A["区分"] != "月"].to_string(index=False))
print("月別の抑制率(%):", {r["期間"]: r["風力抑制率pct"] for r in rows if r["区分"] == "月" and r["風力抑制率pct"] > 0})

# ============================================================================================
# (B) 5円超の抑制の分類
# ============================================================================================
W = P[P["ts"] >= "2025-04-01"].reset_index(drop=True)
W["vre_c"] = (W["wind_curt"] > 0) | (W["solar_curt"] > 0)
prev = W["vre_c"].shift(1, fill_value=False); nxt = W["vre_c"].shift(-1, fill_value=False)
W["edge"] = W["vre_c"] & (~prev | ~nxt)
floor_days = set(W.loc[W["floor"], "date"])
W["floor_day"] = W["date"].isin(floor_days)
# 旧来の上限（監査の再計算と同じ仮定。参考）: 2025年11月以降の全日を対象とし、各時間 min(風力抑制, 8MW) を当てる
W["local_day"] = W["ts"] >= "2025-11-01"
W["local_mwh_ub"] = np.where(W["local_day"], np.minimum(W["wind_curt"], 8.0), 0.0)

# OCCTO の検証資料（流通設備混雑による出力抑制、北海道電力ネットワーク）からの転記。本体「4. 実施状況」と別紙2。
# 日区分ごとに同じ時間帯・同じ抑制量（暫定措置）。VRE＝別紙2 の「自然変動電源の最大抑制量」、need＝「誤差量を織り込んだ
# 抑制必要量（予想潮流−運用容量）」。別紙2 で抑制の対象は区分 F（太陽光）のノンファーム電源だけで、区分 G（風力）は
# 両系統とも「―」（風力の連系なし）。2025年12月〜2026年4月分の公表は見つからない（2026年10月21日に OCCTO の
# サイトと検索で確認。実施がなかったとみなす。かりに実施されていても、両系統の自然変動電源は太陽光だけ）。
_wd11 = [4, 5, 6, 7, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 25, 26, 27, 28]
_wd05 = [1, 7, 8, 11, 12, 13, 14, 15, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29]
_ho05 = [3, 4, 5, 6, 10, 17, 24, 31]
_wd06 = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 29, 30]
_U11 = "https://www.occto.or.jp/news/oshirase_shutsuryokuyokusei_2025_260107_shutsuryokuyokusei2_hokkaido.html"
_U05 = "https://www.occto.or.jp/news/oshirase_shutsuryokuyokusei_2026_260729_shutsuryokuyokusei2_hokkaido_1.html"
_U06 = "https://www.occto.or.jp/news/oshirase_shutsuryokuyokusei_2026_260826_shutsuryokuyokusei2_hokkaido_1_1.html"
LOCAL = [  # (年, 月, 系統, 日区分, 日, VRE最大抑制量[万kW], 抑制必要量[万kW], 開始時, 終了時, 出典)
    (2025, 11, "66kV岩松線", "平日", _wd11, 0.04, 0.04, 12, 13, _U11),
    (2025, 11, "66kV岩松線", "日祝日", [2, 3, 9, 16, 23, 24, 30], 0.02, 0.02, 10, 11, _U11),
    (2026, 5, "66kV岩松線", "平日", _wd05, 0.20, 0.74, 7, 14, _U05),
    (2026, 5, "66kV岩松線", "日祝日", _ho05, 0.20, 0.80, 7, 16, _U05),
    (2026, 5, "66kV富川線", "平日", _wd05, 0.18, 0.18, 10, 13, _U05),
    (2026, 5, "66kV富川線", "土曜", [2, 9, 16, 23, 30], 0.17, 0.17, 10, 13, _U05),
    (2026, 5, "66kV富川線", "日祝日", _ho05, 0.25, 0.25, 9, 14, _U05),
    (2026, 6, "66kV岩松線", "平日", _wd06, 0.13, 0.13, 7, 13, _U06),
    (2026, 6, "66kV富川線", "平日", _wd06, 0.09, 0.09, 12, 13, _U06),
    (2026, 6, "66kV富川線", "土曜", [6, 13, 20, 27], 0.16, 0.16, 10, 13, _U06),
    (2026, 6, "66kV富川線", "日祝日", [7, 14, 21, 28], 0.25, 0.25, 8, 14, _U06),
]
loc_rows = []
W["local_solar_ub"] = 0.0      # MW（その時間にローカル制御の時間帯にあたる系統の VRE 最大抑制量の合計）
W["local_window"] = False
for y, m, line, dtype, ds, vre, need, h0, h1, url in LOCAL:
    dates = pd.to_datetime([f"{y}-{m:02d}-{d:02d}" for d in ds])
    msk = W["date"].isin(dates) & (W["ts"].dt.hour >= h0) & (W["ts"].dt.hour < h1)
    W.loc[msk, "local_solar_ub"] += vre * 10.0
    W.loc[msk, "local_window"] = True
    loc_rows.append(dict(年月=f"{y}-{m:02d}", 系統=line, 日区分=dtype, 日数=len(ds), 実施日="・".join(map(str, ds)),
                         抑制時間=f"{h0}:00〜{h1}:00", 時間数=h1 - h0, 自然変動電源の最大抑制量_万kW=vre, 抑制必要量_万kW=need,
                         抑制の対象=("太陽光（別紙2 の区分 F のノンファーム電源。区分 G 風力は「―」）"),
                         電力量の上限MWh=round(len(ds) * (h1 - h0) * vre * 10.0, 1), 出典=url + "（本体・別紙1〜3、2026-10-21 閲覧）"))
LOC = pd.DataFrame(loc_rows)
LOC.to_csv(os.path.join(PROC, "local_congestion_control_occto.csv"), index=False)
print("\n=== (B0) ローカル系統混雑による出力抑制（OCCTO の検証資料からの転記）===")
print(LOC[["年月", "系統", "日区分", "日数", "抑制時間", "自然変動電源の最大抑制量_万kW", "抑制必要量_万kW", "電力量の上限MWh"]].to_string(index=False))
# 30分値: 該当時間に下限のコマがあるか
js = []
for y in (2025, 2026):
    j = pd.read_csv(os.path.join(RAW, "jepx", f"spot_summary_{y}.csv"), encoding="cp932")
    j.columns = [c.strip() for c in j.columns]
    j["ts"] = pd.to_datetime(j["受渡日"]) + pd.to_timedelta((j["時刻コード"] - 1) * 30, unit="min")
    js.append(j[["ts", "エリアプライス北海道(円/kWh)"]])
J = pd.concat(js); J["h"] = J["ts"].dt.floor("h")
jmin = J.groupby("h")["エリアプライス北海道(円/kWh)"].min()
W["min30"] = W["ts"].map(jmin)
H = W[(W["wind_curt"] > 0) & (W["p_hokkaido"] > 5)].copy()
L5 = W[(W["wind_curt"] > 0) & (W["p_hokkaido"] <= 5)]
tot_w = W["wind_curt"][W["ts"] < "2026-07-01"].sum()
cls = []


def addc(lab, mask, base=H):
    sub = base[mask]
    cls.append(dict(分類=lab, 時間=int(len(sub)), 時間シェアpct=round(len(sub) / len(base) * 100, 1),
                    電力量MWh=round(sub["wind_curt"].sum(), 1), 電力量シェアpct_5円超=round(sub["wind_curt"].sum() / H["wind_curt"].sum() * 100, 1),
                    電力量シェアpct_風力抑制全体=round(sub["wind_curt"].sum() / tot_w * 100, 2)))


addc("5円超の抑制（計）", np.ones(len(H), bool))
addc("(i) 太陽光の抑制が同じ時間にある", H["solar_curt"] > 0)
addc("(ii) 同じ日に下限張り付きの時間がある", H["floor_day"])
addc("(iii) 再エネ抑制の連続した時間帯の最初か最後", H["edge"])
addc("(i)〜(iii) のいずれか", (H["solar_curt"] > 0) | H["floor_day"] | H["edge"])
addc("(i)〜(iii) のどれにも当たらない", ~((H["solar_curt"] > 0) | H["floor_day"] | H["edge"]))
addc("(iv) ローカル制御の日時（OCCTO の公表、系統・日・時間帯）にあたる", H["local_window"])
addc("参考（旧来の仮定）: 2025/11 以降の全日をローカル制御の日とみなす", H["local_day"])
addc("参考: 30分値で下限のコマを含む", H["min30"] <= FLOOR)
addc("参考: 風力抑制 8MW 超（ローカル制御の上限を超える）", H["wind_curt"] > 8)
C = pd.DataFrame(cls)
loc_ub = H["local_mwh_ub"].sum()
Wp = W[W["ts"] < "2026-07-01"]
tot_s = Wp.loc[Wp["ts"] >= "2025-11-01", "solar_curt"].sum()
loc_solar_ub = LOC["電力量の上限MWh"].sum()
loc_solar_in_panel = Wp.loc[Wp["local_window"], "local_solar_ub"].sum()
C = pd.concat([C, pd.DataFrame([
    dict(分類="(iv) ローカル制御の風力の抑制量（OCCTO 別紙2: 両系統とも風力の連系なし）", 時間=0, 時間シェアpct=0.0,
         電力量MWh=0.0, 電力量シェアpct_5円超=0.0, 電力量シェアpct_風力抑制全体=0.0),
    dict(分類="(iv) ローカル制御の太陽光の抑制量の上限（各日・各時間に最大抑制量、2025/11〜2026/6 計）", 時間=int(Wp["local_window"].sum()),
         時間シェアpct=np.nan, 電力量MWh=round(loc_solar_ub, 1), 電力量シェアpct_5円超=np.nan,
         電力量シェアpct_風力抑制全体=np.nan),
    dict(分類="(iv) 同、太陽光の抑制（パネルの出力制御量、2025/11〜2026/6）に対する比(%)", 時間=np.nan, 時間シェアpct=np.nan,
         電力量MWh=round(tot_s, 1), 電力量シェアpct_5円超=np.nan, 電力量シェアpct_風力抑制全体=round(loc_solar_ub / tot_s * 100, 2)),
    dict(分類="参考（旧来の上限）: Σmin(風力抑制, 8MW)（5円超の時間、2025/11 以降の全日）", 時間=int(H["local_day"].sum()), 時間シェアpct=np.nan,
         電力量MWh=round(loc_ub, 1), 電力量シェアpct_5円超=round(loc_ub / H["wind_curt"].sum() * 100, 1),
         電力量シェアpct_風力抑制全体=round(loc_ub / tot_w * 100, 2)),
    dict(分類="参考（旧来の上限）: 同（すべての価格帯の抑制時間、2025/11〜2026/6）", 時間=int(((W["wind_curt"] > 0) & W["local_day"] & (W["ts"] < "2026-07-01")).sum()),
         時間シェアpct=np.nan, 電力量MWh=round(Wp["local_mwh_ub"].sum(), 1), 電力量シェアpct_5円超=np.nan,
         電力量シェアpct_風力抑制全体=round(Wp["local_mwh_ub"].sum() / tot_w * 100, 2)),
    dict(分類="比較: 5円以下の抑制時間のうち連続した時間帯の端", 時間=int(L5["edge"].sum()), 時間シェアpct=round(L5["edge"].mean() * 100, 1),
         電力量MWh=np.nan, 電力量シェアpct_5円超=np.nan, 電力量シェアpct_風力抑制全体=np.nan),
])], ignore_index=True)
assert abs(loc_solar_in_panel - loc_solar_ub) < 1e-6   # 転記した日・時間帯がパネルの時間に漏れなく対応している
# 検算（2026-10-21 の検証で追加）: パネルの太陽光の出力制御量はローカル制御を含むか。エリア全体の制御がない日
# （ローカル制御の時間帯の外に太陽光の抑制がなく、風力の抑制もない日）に、公表された時間帯だけに抑制が現れるかを見る。
# パネルは30分値（MW、整数）の時間平均で、0.5MWh 刻み。2025年11月の岩松線（0.04万kW＝0.4MW）は刻みより小さく現れない。
_dsum = Wp.groupby("date").agg(sc_out=("solar_curt", lambda s: s[~Wp.loc[s.index, "local_window"]].sum()),
                               wc=("wind_curt", "sum"), lw=("local_window", "any"))
loc_only_days = _dsum[_dsum["lw"] & (_dsum["sc_out"] == 0) & (_dsum["wc"] == 0)].index
_lo = Wp[Wp["date"].isin(loc_only_days) & Wp["local_window"]]
panel_local_mwh, ub_local_mwh = _lo["solar_curt"].sum(), _lo["local_solar_ub"].sum()
_lo26 = _lo[_lo["ts"] >= "2026-05-01"]
print(f"検算: エリア全体の制御がない日（{len(loc_only_days)}日、うち2026年5〜6月 {_lo26['date'].nunique()}日）のローカル制御の時間帯に、"
      f"パネルの太陽光の出力制御量 {panel_local_mwh:,.1f}MWh（2026年5〜6月 {_lo26['solar_curt'].sum():,.1f}MWh）が現れる。上限（最大抑制量×時間）"
      f"{ub_local_mwh:,.1f}MWh の {panel_local_mwh / ub_local_mwh * 100:.0f}%。パネルの太陽光の出力制御量はローカル制御を含む"
      f"（2025年11月の0.4MW は 0.5MWh 刻みより小さく現れない: 11月のパネルの値 "
      f"{Wp.loc[(Wp['ts'] >= '2025-11-01') & (Wp['ts'] < '2025-12-01'), ['solar_curt', 'wind_curt']].sum().to_dict()}）")
# (iii) の頑健性: ローカル制御の規模（≤2.5MW）の太陽光の抑制を連続の判定から除く
_vc = (W["wind_curt"] > 0) | (W["solar_curt"] > 2.5)
_edge2 = _vc & (~_vc.shift(1, fill_value=False) | ~_vc.shift(-1, fill_value=False))
_H5, _L5 = (W["wind_curt"] > 0) & (W["p_hokkaido"] > 5), (W["wind_curt"] > 0) & (W["p_hokkaido"] <= 5)
C = pd.concat([C, pd.DataFrame([
    dict(分類="検算: エリア全体の制御がない日のローカル制御の時間帯のパネルの太陽光の出力制御量（MWh。比は上限〔最大抑制量×時間〕に対する%）",
         時間=int(len(_lo)), 時間シェアpct=np.nan, 電力量MWh=round(panel_local_mwh, 1), 電力量シェアpct_5円超=np.nan,
         電力量シェアpct_風力抑制全体=round(panel_local_mwh / ub_local_mwh * 100, 1)),
    dict(分類="頑健性 (iii): 2.5MW 以下の太陽光の抑制（ローカル制御の規模）を連続の判定から除いた端", 時間=int(_edge2[_H5].sum()),
         時間シェアpct=round(_edge2[_H5].mean() * 100, 1), 電力量MWh=round(W.loc[_H5 & _edge2, "wind_curt"].sum(), 1),
         電力量シェアpct_5円超=round(W.loc[_H5 & _edge2, "wind_curt"].sum() / H["wind_curt"].sum() * 100, 1), 電力量シェアpct_風力抑制全体=np.nan),
    dict(分類="頑健性 (iii) の比較: 同じ定義で5円以下の抑制時間のうち端", 時間=int(_edge2[_L5].sum()), 時間シェアpct=round(_edge2[_L5].mean() * 100, 1),
         電力量MWh=np.nan, 電力量シェアpct_5円超=np.nan, 電力量シェアpct_風力抑制全体=np.nan),
])], ignore_index=True)
C.to_csv(os.path.join(PROC, "curtailment_above5_classification.csv"), index=False)
print("\n=== (B) 5円超の抑制（2025/4〜2026/6、wind_curt>0 かつ北海道価格>5円）の分類 ===")
print(C.to_string(index=False))
print("月別の時間数:", H.groupby(H["ts"].dt.to_period("M")).size().to_dict(), " 風力抑制の中央値・最大(MW):", H["wind_curt"].median(), H["wind_curt"].max(),
      " 日数:", H["date"].nunique(), "うち下限の時間がある日:", H.loc[H["floor_day"], "date"].nunique())

# ============================================================================================
# (C) 併設蓄電池の価値（日ごとの線形計画）
# ============================================================================================


def build_lp(D):
    """変数: xc[24], xg[24], dch[24], s[24]（蓄電池1kW あたり、kWh）。等式は SoC の推移、不等式は出力と1日1サイクル。"""
    n = 96
    Aeq = lil_matrix((24, n)); beq = np.zeros(24)
    for h in range(24):
        Aeq[h, 72 + h] = 1.0
        if h > 0:
            Aeq[h, 72 + h - 1] = -1.0
        Aeq[h, h] = -1.0; Aeq[h, 24 + h] = -1.0; Aeq[h, 48 + h] = 1.0
    Aub = lil_matrix((25, n)); bub = np.ones(25)
    for h in range(24):
        Aub[h, h] = 1.0; Aub[h, 24 + h] = 1.0; Aub[h, 48 + h] = 1.0
    Aub[24, :48] = 1.0; bub[24] = D
    return Aeq.tocsr(), beq, Aub.tocsr(), bub


LP = {d: build_lp(d) for d in (2, 4)}


def solve_day(price, cav, D, prem, grid=True, wcost=W_CHG, own_cost=None, maximize_abs=False):
    """1日の最適化。price[24]、cav[24]＝吸収できる抑制電力量（kWh/kW 蓄電池）。戻り値: (目的関数値, 吸収量の時間別, 放電量の時間別)"""
    Aeq, beq, Aub, bub = LP[D]
    if maximize_abs:
        cobj = np.concatenate([-np.ones(24), np.zeros(72)])
    else:
        gcost = price + (wcost if own_cost is None else own_cost)
        cobj = np.concatenate([-ETA * prem * np.ones(24), gcost, -ETA * price, np.zeros(24)])
    bounds = [(0, max(0.0, c)) for c in cav] + [(0, 1.0 if grid else 0.0)] * 24 + [(0, 1.0)] * 24 + [(0, D)] * 23 + [(0, 0)]
    res = linprog(cobj, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq, bounds=bounds, method="highs")
    assert res.status == 0, res.message
    x = res.x
    return -res.fun, x[:24], x[48:72]


def day_arrays(df):
    out = []
    for d, g in df.groupby("date"):
        if len(g) != 24:
            continue
        out.append((d, g["p_hokkaido"].to_numpy(), g["wind_curt"].to_numpy() * 1000, g["wind_kw"].to_numpy(),
                    (g["wind"] + g["wind_curt"]).to_numpy() * 1000))
    return out


WINDOWS = {"FY2025（年度の実績）": P[(P["ts"] >= "2025-04-01") & (P["ts"] < "2026-04-01")],
           "FY2026 4〜6月": P[(P["ts"] >= "2026-04-01") & (P["ts"] < "2026-07-01")]}
DAYS = {k: day_arrays(v) for k, v in WINDOWS.items()}
SPECS = [(0.64, 4), (0.64, 2), (1.28, 4), (2.0, 4)]   # (風力1kW あたり kWh, 放電時間)
GROUPS = {"一様": [(1.0, 1.0)], "集中": [(0.2, 0.77 / 0.2), (0.8, 0.23 / 0.8)]}  # (容量シェア, 抑制の集中倍率)
PREMS = (2.0, 3.0, 4.0)
V1_cache = {}


def v1_day(key, D, price):
    k = (key, D)
    if k not in V1_cache:
        V1_cache[k] = solve_day(price, np.zeros(24), D, 0.0)[0]
    return V1_cache[k]


def evaluate(days, E, D, scale=1.0, cap_pre=True):
    """期間の合計（蓄電池1kW あたり、円・kWh）と、フリート全体の回避率。scale は抑制電力量の比例拡大の倍率
    （各時間は抑制前の出力が上限）。"""
    out = {}
    for dist, groups in GROUPS.items():
        acc = {p: dict(incr=0.0, abs=0.0, abs_p=0.0, own_incr=0.0, fit_abs=0.0, abs_fleet=0.0, curt_fleet=0.0) for p in PREMS}
        for d, price, curt_kwh, wkw, pre_kwh in days:
            c_sc = np.minimum(curt_kwh * scale, pre_kwh) if cap_pre else curt_kwh * scale
            for p in PREMS:
                acc[p]["curt_fleet"] += c_sc.sum()
            if c_sc.sum() <= 0:
                continue
            batt_kw = wkw * E / D   # 風力フリートに併設される蓄電池の kW（時間別。月内は一定）
            base = v1_day(d, D, price)
            for share, conc in groups:
                cav = c_sc * conc / batt_kw     # kWh/kW 蓄電池
                fit_abs = solve_day(price, cav, D, 0.0, grid=False, maximize_abs=True)[1].sum()
                for p in PREMS:
                    val, xc, _ = solve_day(price, cav, D, p)
                    a = acc[p]
                    a["incr"] += share * (val - base)
                    a["abs"] += share * xc.sum()
                    a["abs_p"] += share * (xc * price).sum()
                    a["own_incr"] += share * (xc * (price + p)).sum()   # 自社の発電の時間移動に対する増分（併設・系統充電なし）
                    a["fit_abs"] += share * fit_abs
                    a["abs_fleet"] += share * xc.sum() * batt_kw.mean()
        for p in PREMS:
            out[(dist, p)] = acc[p]
    return out


def base_v1(days, D):
    return sum(v1_day(d, D, price) for d, price, *_ in days)


print("\n=== (C) 併設蓄電池の価値（日ごとの線形計画、1日1サイクル）===")
cfpre = {}
for k, df in WINDOWS.items():
    cfpre[k] = (df["wind"] + df["wind_curt"]).sum() / (df["wind_kw"].mean() / 1000 * len(df))
    print(f"{k}: 抑制前の出力の設備利用率 {cfpre[k]:.3f}、日数 {len(DAYS[k])}")
Q1 = DAYS["FY2026 4〜6月"]; FY25 = DAYS["FY2025（年度の実績）"]
dfq = WINDOWS["FY2026 4〜6月"]
rate_q1 = dfq["wind_curt"].sum() / (dfq["wind"].sum() + dfq["wind_curt"].sum())
YQ = 365 / len(Q1)
RATES = [1.35, 3, 5, 8, 10, 15, 20, 37]
share91 = pd.read_csv(os.path.join(PROC, "btm_avoidable_share.csv"))
SHARE = {(r["E(kWh/kW)"], int(round(r["E(kWh/kW)"] / r["P(kW/kW)"]))): {"一様": r["回避可能率_一様(%)"] / 100, "集中": r["回避可能率_集中20%/77%(%)"] / 100}
         for _, r in share91.iterrows()}
v1_ann = {D: base_v1(Q1, D) * YQ for D in (2, 4)}
v1_fy25 = {D: base_v1(FY25, D) for D in (2, 4)}
recs = []
RATE_W = {k: v["wind_curt"].sum() / (v["wind"].sum() + v["wind_curt"].sum()) for k, v in WINDOWS.items()}


def rec_from(a, mult, **kw):
    return dict(**kw, 回避率pct=a["abs_fleet"] / a["curt_fleet"] * 100 if a["curt_fleet"] > 0 else np.nan,
                吸収量kWh_per_kW蓄電池=a["abs"] * mult, 吸収時の平均価格=a["abs_p"] / a["abs"] if a["abs"] > 0 else np.nan,
                増分_円per_kW蓄電池=a["incr"] * mult, 自社発電移動に対する増分_円per_kW蓄電池=a["own_incr"] * mult,
                FIT併設_円per_kW蓄電池=ETA * 14 * a["fit_abs"] * mult, 上限14円_円per_kW蓄電池=14 * a["abs"] * mult)


for E, D in SPECS:
    # 現状の実績（FY2025 は年値そのもの、FY2026 4〜6月は×365/91 で年率とみなした上限）
    for wlab, wkey, mult in (("FY2025 実績（年の値）", "FY2025（年度の実績）", 1.0), ("FY2026 4〜6月の実績を年率とみなす（上限）", "FY2026 4〜6月", YQ)):
        res = evaluate(DAYS[wkey], E, D)
        for (dist, p), a in res.items():
            recs.append(rec_from(a, mult, 方法=wlab, 年率pct=round(RATE_W[wkey] * 100, 3), 達成した抑制率pct=round(RATE_W[wkey] * 100, 3),
                                 E_kWh_per_kW風力=E, 放電h=D, 分布=dist, プレミアム=p,
                                 V1_円per_kW蓄電池=(v1_fy25[D] if wkey.startswith("FY2025") else v1_ann[D])))
    # 比例拡大（下限側）
    for rt in RATES:
        f = (rt / 100) / rate_q1
        c_sc = np.concatenate([np.minimum(c * f, pre) for _, _, c, _, pre in Q1])
        achieved = c_sc.sum() / ((dfq["wind"] + dfq["wind_curt"]).sum() * 1000)
        res = evaluate(Q1, E, D, scale=f)
        for (dist, p), a in res.items():
            # 年率は達成した値で記録する（観察された抑制時間の出力をすべて抑制しても約12%で頭打ち）
            recs.append(rec_from(a, YQ, 方法="比例拡大（FY2026 4〜6月の時間値、下限側）", 年率pct=round(achieved * 100, 2), 目標の年率pct=rt,
                                 達成した抑制率pct=round(achieved * 100, 2),
                                 E_kWh_per_kW風力=E, 放電h=D, 分布=dist, プレミアム=p, V1_円per_kW蓄電池=v1_ann[D]))
    print(f"  仕様 {E}kWh/kW・{D}h: 計算済み")
R = pd.DataFrame(recs)
# 回避率一定（上限側）: ②＝年率×抑制前の出力×回避率（表9.1）×(0.85×プレミアム＋吸収時の価格＋w)
up = []
for E, D in SPECS:
    pbar = R[(R["方法"].str.startswith("比例拡大")) & (R["年率pct"] == 1.35) & (R["E_kWh_per_kW風力"] == E) & (R["放電h"] == D)]
    for dist in ("一様", "集中"):
        pb = float(pbar[(pbar["分布"] == dist) & (pbar["プレミアム"] == 3.0)]["吸収時の平均価格"].iloc[0])
        sh = SHARE[(E, D)][dist]
        for p in PREMS:
            for rt in RATES:
                abs_kwh_per_kw_wind = 8760 * cfpre["FY2025（年度の実績）"] * rt / 100 * sh
                per_b_raw = abs_kwh_per_kw_wind / (E / D)
                per_b = min(per_b_raw, 365 * D)   # 1日1サイクル（毎日 D kWh）を超えては吸収できない
                up.append(dict(方法="回避率一定（表9.1 の回避率、上限側）", 年率pct=rt, E_kWh_per_kW風力=E, 放電h=D, 分布=dist, プレミアム=p,
                               回避率pct=sh * 100 * per_b / per_b_raw, 備考=("1日1サイクルの上限で頭打ち" if per_b < per_b_raw else ""), 吸収量kWh_per_kW蓄電池=per_b, 吸収時の平均価格=pb,
                               増分_円per_kW蓄電池=per_b * (ETA * p + pb + W_CHG), 自社発電移動に対する増分_円per_kW蓄電池=per_b * (pb + p),
                               FIT併設_円per_kW蓄電池=per_b * ETA * 14, 上限14円_円per_kW蓄電池=per_b * 14, V1_円per_kW蓄電池=v1_ann[D]))
R = pd.concat([R, pd.DataFrame(up)], ignore_index=True)
R["増分_円per_kW風力"] = R["増分_円per_kW蓄電池"] * R["E_kWh_per_kW風力"] / R["放電h"]
R["増分_円per_kWh蓄電池"] = R["増分_円per_kW蓄電池"] / R["放電h"]
R["増分の吸収1kWhあたり"] = R["増分_円per_kW蓄電池"] / R["吸収量kWh_per_kW蓄電池"]
# ①の水準（K=0）。4時間は T1 の pi_k_curve_v3.csv（仕様A 26・現状・θ=1・刻み1万kW）の π(0)。2時間の実績整合は、実績価格の上で
# 戦略c（直近29日・同じ曜日区分の時刻別平均価格のランク、5日以上、同値は均等配分。41 と同じ定義）を2時間で直接計算した
# FY2023〜25 平均から充電従量負担 876円/kW-年（1,752 の半分）を引く。2時間のモデル直値は計算していない（T5 の 48 に従う）。
_V0 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
_V0 = _V0[(_V0["価格モデル"] == "仕様A（26、水準係数付き）") & (_V0["シナリオ"] == "現状") & (_V0["θ"] == 1.0)
          & (_V0["フリート配分"] == "完全予見の増分貪欲（主）") & (_V0["刻み(万kW)"].astype(str) == "1.0") & (_V0["K(万kW)"] == 0)].iloc[0]


def strategy_c_actual(hours):
    """実績価格（2022-02-01〜）の上の戦略c の FY2023〜25 平均（円/kW-年、充電従量負担の控除前）"""
    q = P[(P["ts"] >= "2022-02-01") & (P["ts"] < "2026-04-01")].copy()
    q["h"] = q["ts"].dt.hour
    M = q.pivot(index="date", columns="h", values="p_hokkaido")
    M = M[M.count(axis=1) == 24]
    dd = M.index; PA = M.to_numpy(float); wk = np.asarray(dd.dayofweek >= 5)
    n = len(dd); Wm = np.zeros((n, n)); has = np.zeros(n, bool)
    for i in range(n):
        hh = [j for j in range(max(0, i - 29), i) if wk[j] == wk[i]]
        if len(hh) >= 5:
            Wm[i, hh] = 1.0 / len(hh); has[i] = True
    Cm = Wm @ PA

    def tw(sig, k):
        srt = np.sort(sig, 1); thr_ = srt[:, k - 1:k]; w = (sig < thr_).astype(float); tied = sig == thr_
        return w + tied * ((k - w.sum(1, keepdims=True)) / tied.sum(1, keepdims=True))
    cday = ETA * (tw(-Cm, hours) * PA).sum(1) - (tw(Cm, hours) * PA).sum(1)
    fyv = np.asarray(dd.year - (dd.month < 4).astype(int))
    m = (fyv >= 2023) & (fyv <= 2025) & has
    return float(pd.Series(cday[m]).groupby(fyv[m]).sum().mean())


C4_ACT, C2_ACT = strategy_c_actual(4), strategy_c_actual(2)
assert abs(C4_ACT - 8427.2) < 1.0 and abs(C4_ACT - 1752 - _V0["π_実績整合"]) < 1.0, (C4_ACT, _V0["π_実績整合"])
print(f"\n実績価格の上の戦略c（FY2023〜25 平均）: 4時間 {C4_ACT:,.1f}・2時間 {C2_ACT:,.1f} 円/kW-年（充電従量負担の控除前）")
PI_BASIS = {4: {"実績整合（D1）": float(_V0["π_実績整合"]), "モデル直値（D1）": float(_V0["π_モデル直値"]), "旧0.81×π_PF": float(_V0["π_旧0.81PF"])},
            2: {"実績整合（D1）": C2_ACT - 876, "旧0.81×π_PF": 0.81 * 4721 - 876}}
print("①の水準 π_spot（K=0、充電従量負担の控除後）:", {D: {k: round(v) for k, v in d.items()} for D, d in PI_BASIS.items()})
R["増分÷π_spot（実績整合）"] = [r["増分_円per_kW蓄電池"] / PI_BASIS[int(r["放電h"])]["実績整合（D1）"] for _, r in R.iterrows()]
R["増分÷V1（同じ期間の①）"] = R["増分_円per_kW蓄電池"] / R["V1_円per_kW蓄電池"]
R = R.drop(columns=[c for c in R.columns if c.startswith("Unnamed")])
R.round(4).to_csv(os.path.join(PROC, "btm_local_value.csv"), index=False)
show = R[(R["E_kWh_per_kW風力"] == 0.64) & (R["放電h"] == 4) & (R["プレミアム"] == 3.0)]
print(show[["方法", "年率pct", "分布", "回避率pct", "吸収時の平均価格", "増分_円per_kW風力", "増分_円per_kWh蓄電池", "増分_円per_kW蓄電池",
            "増分÷π_spot（実績整合）", "上限14円_円per_kW蓄電池"]].round(2).to_string(index=False))

# ============================================================================================
# (D) 併設の参入条件と閾値
# ============================================================================================


def crf(r, n=20):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def creq(capex, D, r, colocated):
    capital = D * capex * crf(r)
    om = 5000 + 300 * (D * capex) / (4 * 68000)    # 運維0.5万＋廃止（4時間・6.8万で300円。9.4・9.5 の定義、2時間で23,907円と整合）
    return capital + om + (0 if colocated else 6900)


KP = 0.836 * 14972
thr = []
for D in (4, 2):
    for meth in ("比例拡大（FY2026 4〜6月の時間値、下限側）", "回避率一定（表9.1 の回避率、上限側）"):
        sub = R[(R["方法"] == meth) & (R["E_kWh_per_kW風力"] == 0.64) & (R["放電h"] == D)]
        for dist in ("一様", "集中"):
            for p in PREMS:
                s2 = sub[(sub["分布"] == dist) & (sub["プレミアム"] == p)].sort_values("年率pct")
                for basis, pi0 in PI_BASIS[D].items():
                    for defn in ("系統用と同じ", "併設（託送固定を共有・系統から充電しない）"):
                        col = defn.startswith("併設")
                        for capex in (23000, 40000, 68000):
                            for wacc in (0.06, 0.08):
                                for kp in ((KP, 0.0) if D == 4 else (0.0,)):
                                    cr = creq(capex, D, wacc, col)
                                    if col:
                                        pi1 = pi0 + W_CHG * 365 * D - 0.15 * p * 365 * D
                                        v2 = s2["自社発電移動に対する増分_円per_kW蓄電池"].to_numpy()
                                    else:
                                        pi1 = pi0
                                        v2 = s2["増分_円per_kW蓄電池"].to_numpy()
                                    gap = pi1 + v2 + kp - cr
                                    gap0 = pi1 + kp - cr          # ②を含まない（抑制なし）
                                    rts = s2["年率pct"].to_numpy()
                                    i10 = int(np.argmin(np.abs(rts - 10)))
                                    if gap0 >= 0:
                                        rstar = "抑制なしで成立（②は不要）"
                                    elif gap[0] >= 0:
                                        rstar = f"≤{rts[0]:.2f}%で成立"
                                    elif gap[-1] < 0:
                                        rstar = f"{rts[-1]:.1f}%でも不成立（不足 {gap[-1]:,.0f}）"
                                    else:
                                        k = int(np.argmax(gap >= 0))
                                        rstar = round(float(np.interp(0, [gap[k - 1], gap[k]], [rts[k - 1], rts[k]])), 1)
                                    # 解析的な上限: 毎日 D kWh を抑制から吸収
                                    pb = float(s2["吸収時の平均価格"].iloc[0])
                                    ceil2 = 365 * D * ((pb + p) if col else (ETA * p + pb + W_CHG))
                                    thr.append(dict(放電h=D, 方法=meth, 分布=dist, プレミアム=p, π_spot基準=basis, c_req定義=defn,
                                                    資本費_円per_kWh=capex, WACC=wacc, κP=round(kp), c_req=round(cr), π_spot_prime=round(pi1),
                                                    不足_抑制なし=round(gap0), 不足_1_35pct=round(gap[0]), 年率_10pct付近=rts[i10], 不足_10pct付近=round(float(gap[i10])),
                                                    最大の年率pct=rts[-1], 不足_最大の年率=round(gap[-1]),
                                                    閾値の年率pct=rstar, 毎日満充電の上限での不足=round(pi1 + ceil2 + kp - cr)))
T = pd.DataFrame(thr)


def _judge(x):
    if not isinstance(x, str):
        return "抑制率の閾値あり（②が参入を開く）"
    if x.startswith("抑制なし"):
        return "抑制なしで成立（②は不要）"
    if x.startswith("≤"):
        return "現状（1.35%）以下で成立"
    return "最大の抑制率でも不成立"


T["判定"] = T["閾値の年率pct"].apply(_judge)
T.to_csv(os.path.join(PROC, "btm_entry_threshold.csv"), index=False)
print("\n=== (D) 併設の参入条件（0.64kWh/kW 風力、プレミアム3円、実績整合の①、WACC 6%）===")
v = T[(T["プレミアム"] == 3.0) & (T["π_spot基準"] == "実績整合（D1）") & (T["WACC"] == 0.06)]
print(v[["放電h", "方法", "分布", "c_req定義", "資本費_円per_kWh", "κP", "不足_抑制なし", "不足_1_35pct", "不足_10pct付近", "最大の年率pct", "不足_最大の年率", "閾値の年率pct", "毎日満充電の上限での不足"]].to_string(index=False))
pos = T[T["閾値の年率pct"].apply(lambda x: not isinstance(x, str))]
print(f"\n閾値が 1.35〜37% の範囲に入る組合せ: {len(pos)} / {len(T)}")
print("判定の内訳（全組合せ）:", T["判定"].value_counts().to_dict())
print("判定の内訳（増分評価・比例拡大・実績整合）:",
      T[(T["方法"].str.startswith("比例拡大")) & (T["π_spot基準"] == "実績整合（D1）")].groupby(["c_req定義", "判定"]).size().to_dict())
print(pos.groupby(["放電h", "c_req定義", "資本費_円per_kWh", "WACC", "κP"]).size().to_string())
print("成立する組合せの例:")
print(pos[["放電h", "方法", "分布", "プレミアム", "π_spot基準", "c_req定義", "資本費_円per_kWh", "WACC", "κP", "閾値の年率pct"]].head(40).to_string(index=False))

# 損益分岐の資本費（抑制率ごと）: π_spot′＋②＋κP − c_req(資本費) = 0 を資本費について解く
bec = []
for D in (4, 2):
    for meth in ("比例拡大（FY2026 4〜6月の時間値、下限側）", "回避率一定（表9.1 の回避率、上限側）"):
        for dist in ("一様", "集中"):
            s2 = R[(R["方法"] == meth) & (R["E_kWh_per_kW風力"] == 0.64) & (R["放電h"] == D) & (R["分布"] == dist) & (R["プレミアム"] == 3.0)].sort_values("年率pct")
            for basis, pi0 in PI_BASIS[D].items():
                for defn in ("系統用と同じ", "併設（託送固定を共有・系統から充電しない）"):
                    col = defn.startswith("併設")
                    for wacc in (0.06, 0.08):
                        for kp in ((KP, 0.0) if D == 4 else (0.0,)):
                            pi1 = pi0 + (W_CHG * 365 * D - 0.15 * 3 * 365 * D if col else 0.0)
                            for _, r in s2.iterrows():
                                v2 = r["自社発電移動に対する増分_円per_kW蓄電池"] if col else r["増分_円per_kW蓄電池"]
                                num = pi1 + v2 + kp - 5000 - (0 if col else 6900)
                                c_star = num / (D * crf(wacc) + 300 * D / (4 * 68000))
                                c_star0 = (pi1 + kp - 5000 - (0 if col else 6900)) / (D * crf(wacc) + 300 * D / (4 * 68000))
                                bec.append(dict(放電h=D, 方法=meth, 分布=dist, プレミアム=3.0, π_spot基準=basis, c_req定義=defn, WACC=wacc, κP=round(kp),
                                                年率pct=r["年率pct"], 損益分岐の資本費_円per_kWh=round(c_star), 抑制なしの損益分岐の資本費=round(c_star0),
                                                抑制回避による上昇=round(c_star - c_star0)))
BEC = pd.DataFrame(bec)
BEC.to_csv(os.path.join(PROC, "btm_entry_breakeven_capex.csv"), index=False)
print("\n=== (D2) 併設4時間の損益分岐の資本費（円/kWh、プレミアム3円、①は実績整合、WACC 6%）===")
vv = BEC[(BEC["放電h"] == 4) & (BEC["π_spot基準"] == "実績整合（D1）") & (BEC["WACC"] == 0.06)]
print(vv.pivot_table(index=["c_req定義", "κP", "方法", "分布"], columns="年率pct", values="損益分岐の資本費_円per_kWh").round(0).to_string())

# 図: 抑制率と参入条件の過不足（4時間、0.64kWh/kW、プレミアム3円、実績整合、WACC 6%、κP あり）。左は c_req を系統用と同じ、右は併設
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする。凡例は色（資本費）と線種（方法）に分けて図の下に置く
fig, axes = plt.subplots(1, 2, figsize=(6.1, 4.0), sharey=True, layout="constrained")
colors = {23000: "#2a6f97", 40000: "#e76f51", 68000: "#264653"}
for ax, col in zip(axes, (False, True)):
    for capex in (23000, 40000, 68000):
        for meth, ls in (("比例拡大（FY2026 4〜6月の時間値、下限側）", "-"), ("回避率一定（表9.1 の回避率、上限側）", "--")):
            s2 = R[(R["方法"] == meth) & (R["E_kWh_per_kW風力"] == 0.64) & (R["放電h"] == 4) & (R["分布"] == "一様") & (R["プレミアム"] == 3.0)].sort_values("年率pct")
            if col:
                pi1 = PI_BASIS[4]["実績整合（D1）"] + W_CHG * 365 * 4 - 0.15 * 3 * 365 * 4
                gap = pi1 + s2["自社発電移動に対する増分_円per_kW蓄電池"] + KP - creq(capex, 4, 0.06, True)
            else:
                pi1 = PI_BASIS[4]["実績整合（D1）"]
                gap = pi1 + s2["増分_円per_kW蓄電池"] + KP - creq(capex, 4, 0.06, False)
            ax.plot(s2["年率pct"], gap / 1e4, ls=ls, lw=1.4, color=colors[capex])
        ax.axhline((pi1 + KP - creq(capex, 4, 0.06, col)) / 1e4, color=colors[capex], lw=0.6, ls=":")
    ax.axhline(0, color="#333", lw=0.8)
    ax.axvline(37, color="#888", lw=0.8, ls=":")
    if not col:
        ax.text(36.5, -1.32, "2035年度の見通し37%\n（太陽光・風力の合計）", ha="right", va="center", fontsize=8.5, color="#555")
    ax.set_xlabel("風力の抑制率（年率、%）", fontsize=9)
    ax.set_title("併設の定義\n（託送固定を共有・系統から充電しない）" if col else "系統用と同じ定義\n（託送固定0.69万円を含む）", loc="left", fontsize=9)
    ax.tick_params(labelsize=8.5)
# 縦軸は参入条件の過不足（左辺と c_req^co の差。記号は図の注で説明する）
axes[0].set_ylabel("参入条件の過不足（万円/kW-年）", fontsize=9)
_hc = [plt.Line2D([], [], color=colors[c], lw=1.4) for c in (23000, 40000, 68000)]
_lc = [f"資本費{c / 1e4:.1f}万円/kWh" for c in (23000, 40000, 68000)]
_hm = [plt.Line2D([], [], color="#555", lw=1.4, ls="-"), plt.Line2D([], [], color="#555", lw=1.4, ls="--")]
_lm = ["比例拡大（〜12%で頭打ち）", "回避率一定（1日1サイクルで頭打ち）"]
fig.legend([_hc[0], _hm[0], _hc[1], _hm[1], _hc[2]], [_lc[0], _lm[0], _lc[1], _lm[1], _lc[2]], fontsize=8.5, frameon=False, loc="outside lower center", ncol=3, columnspacing=1.2, handlelength=2.0)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIG, "btm_entry_threshold.png"), dpi=300)

# ============================================================================================
# (E) 負価格の移転と抑制の影の価格（表10.2 の再計算）
# ============================================================================================
tr = []
for fy, g in P[P["fy"].between(2023, 2026)].groupby("fy"):
    fl = g[g["floor"]]
    gen = (fl["solar"] + fl["wind"]).sum(); pre = gen + (fl["solar_curt"] + fl["wind_curt"]).sum()
    curt = (g["solar_curt"] + g["wind_curt"]).sum()
    r = dict(FY=f"FY{fy}" + ("（4〜6月）" if fy == 2026 else ""), 下限張り付き時間h=len(fl), 下限時間の再エネ発電実績GWh=round(gen / 1000, 1),
             下限時間の抑制前出力GWh=round(pre / 1000, 1), 下限時間の抑制量GWh=round((pre - gen) / 1000, 1), 抑制量計GWh=round(curt / 1000, 1),
             抑制時間h=int(((g["solar_curt"] + g["wind_curt"]) > 0).sum()))
    for c in (5.0, 10.0):
        r[f"移転_発電実績_c{c:.0f}_億円"] = round(gen * (0.01 + c) / 1e5, 1)
        r[f"移転_抑制前_c{c:.0f}_億円"] = round(pre * (0.01 + c) / 1e5, 1)
        r[f"影の価格_c{c:.0f}_億円"] = round(curt * c / 1e5, 2)
        r[f"比_発電実績_c{c:.0f}"] = round(gen * (0.01 + c) / (curt * c), 1) if curt > 0 else np.nan
        r[f"比_抑制前_c{c:.0f}"] = round(pre * (0.01 + c) / (curt * c), 1) if curt > 0 else np.nan
    tr.append(r)
TR = pd.DataFrame(tr)
TR.to_csv(os.path.join(PROC, "negative_price_transfer_v2.csv"), index=False)
print("\n=== (E) 負価格の移転と抑制の影の価格（発電実績ベースを主、抑制前は 32 の定義）===")
print(TR.to_string(index=False))

# ============================================================================================
# (F) Weitzman の傾き
# ============================================================================================
ws = []
# (F1) 主: T1 の π(K) v3（41_equilibrium_v3.py の pi_k_curve_v3.csv。仕様A（26）、完全予見の増分貪欲、刻み1万kW で K は正確）。
#      下限は現行（0.01円）。収益基準は D1 の実績整合（主）・モデル直値・旧0.81×π_PF。
V3 = pd.read_csv(os.path.join(PROC, "pi_k_curve_v3.csv"))
V3 = V3[(V3["価格モデル"] == "仕様A（26、水準係数付き）") & (V3["フリート配分"] == "完全予見の増分貪欲（主）")
        & (V3["刻み(万kW)"].astype(str) == "1.0")]
for (scen, th), g in V3.groupby(["シナリオ", "θ"], sort=False):
    if not ((scen in ("現状", "泊3号再稼働") and th in (1.0, 1.567)) or (scen == "泊＋風力2倍" and th == 1.0)):
        continue
    assert not g["K(万kW)"].duplicated().any()
    g = g.set_index("K(万kW)")
    for col, lab in (("π_実績整合", "実績整合（D1、主）"), ("π_モデル直値", "モデル直値"), ("π_旧0.81PF", "旧0.81×π_PF")):
        for k0, k1 in ((0, 25), (25, 50), (0, 50), (50, 100)):
            if k0 in g.index and k1 in g.index:
                ws.append(dict(出典="pi_k_curve_v3.csv（41、T1）", シナリオ=f"{scen}・θ={th:g}", 収益基準=lab, 下限="現行（下限0.01円）",
                               区間=f"K={k0}→{k1}万kW", π_K0=round(g.loc[k0, col]), π_K1=round(g.loc[k1, col]),
                               限界便益の傾き_円per_kW年_per万kW=round((g.loc[k1, col] - g.loc[k0, col]) / (k1 - k0), 1),
                               相対の傾き_pct_per万kW=round((g.loc[k1, col] - g.loc[k0, col]) / (k1 - k0) / g.loc[0, col] * 100, 2)))
# (F2) 参考: 負価格の下限 −5・−10円（32 の negative_price_scenarios.csv、旧0.81×π_PF 基準。K=0・50・100 の行だけ使う。
#      K=25 の行は格子の不具合で実際は K=30）。D1 基準での再計算は T2a（43_negative_price_v3.py）に従う。
NS = pd.read_csv(os.path.join(PROC, "negative_price_scenarios.csv"))
for (lv, fl), g in NS.groupby(["水準", "下限"], sort=False):
    g = g.set_index("K(万kW)")["π_実現可能(円/kW-年)"]
    for k0, k1 in ((0, 50), (50, 100)):
        if k0 in g.index and k1 in g.index:
            ws.append(dict(出典="negative_price_scenarios.csv（32、旧基準・参考）", シナリオ=lv, 収益基準="旧0.81×π_PF", 下限=fl, 区間=f"K={k0}→{k1}万kW",
                           π_K0=g[k0], π_K1=g[k1], 限界便益の傾き_円per_kW年_per万kW=round((g[k1] - g[k0]) / (k1 - k0), 1),
                           相対の傾き_pct_per万kW=round((g[k1] - g[k0]) / (k1 - k0) / g[0] * 100, 2)))
capex = pd.read_csv(os.path.join(PROC, "battery_capex_series.csv"))
cs = capex[capex["category"] == "grid_by_fy"].set_index("fy_or_bin")["total_man_yen_kwh"].astype(float)
creq_series = {fy: creq(v * 1e4, 4, 0.06, False) for fy, v in cs.items()}
ws.append(dict(出典="—", シナリオ="限界費用（c_req、4時間、WACC 6%）", 収益基準="—", 下限="—", 区間="K に対する傾き",
               π_K0=np.nan, π_K1=np.nan, 限界便益の傾き_円per_kW年_per万kW=0.0, 相対の傾き_pct_per万kW=0.0))
WS = pd.DataFrame(ws)
WS["備考"] = ""
WS.loc[WS.index[-1], "備考"] = ("資本費は世界市場で決まり北海道の導入量（数十万kW）に依存しない（K に対する傾き≈0）。資本費の水準は年度で "
                               + "・".join(f"FY{k} {v:.1f}" for k, v in cs.items()) + "万円/kWh と動き、c_req は "
                               + "・".join(f"{v:,.0f}" for v in creq_series.values()) + "円/kW-年（不確実性 σ の源）")
WS.to_csv(os.path.join(PROC, "weitzman_slopes.csv"), index=False)
print("\n=== (F) Weitzman: 限界便益（π(K)）の傾きと限界費用の傾き ===")
print(WS[["出典", "シナリオ", "収益基準", "下限", "区間", "π_K0", "π_K1", "限界便益の傾き_円per_kW年_per万kW", "相対の傾き_pct_per万kW"]].to_string(index=False))
print(WS["備考"].iloc[-1])
print("saved curtailment_price_bands.csv, curtailment_above5_classification.csv, local_congestion_control_occto.csv, btm_local_value.csv, btm_entry_threshold.csv, btm_entry_breakeven_capex.csv, "
      "negative_price_transfer_v2.csv, weitzman_slopes.csv, figures/hokkaido/btm_entry_threshold.png")
