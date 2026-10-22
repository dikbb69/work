#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道風力の設備利用率（cf）系列の計上時期のずれの補正と、風力の反実仮想（K_wind 実験・λ 実験）への感応度

問題:
  12 が作る導入容量（FIT/FIP 情報公表用ウェブサイトの表B、四半期末値を月次に線形補間）は、認定設備の運転開始の
  時点で容量を計上する。試運転中の発電（と非FIT設備の発電）は需給実績の風力出力に先に現れるので、出力が容量に
  先行する月がある。2023年12月には制御前の風力出力（最大887MW）が表Bの容量（86.4万kW）を上回り、
  hokkaido_cf_series.csv（13 の出力）の cf が4時間で1を超える。FY2023 の年度平均 cf（30.4%）は他の年度より高い。

手法:
  1. 表Bの四半期の網羅: fit_capacity_pref_quarterly.csv（12 の出力）の日付を 2014年6月〜2025年12月の四半期末と
     照合し、欠落四半期を列挙する。data/raw/fit_b/B_pref202103.xlsx（12 の glob「B_city*」に掛からず未使用）を
     12 の parse_sheet（exec で関数だけを読み込む。12 の main は実行しない）で読み、2021年3月末の値を月次補間値と比べる。
  2. 月次の診断（FY2016〜FY2026 4〜6月、北海道パネル 89,832時間）: 制御前風力（実績＋抑制量）の月間発電量 ÷
     （表Bの月次容量×時間）の cf、月内の最大時間出力 ÷ 容量（ピーク cf）、同じ暦月の他の年（2023年3月〜2024年3月を
     除く）の cf の中央値・最小・最大・標準偏差に対する比と z 値、中央値の cf で逆算した容量（実効容量）。
  3. 補正した容量（月次、kW）と cf 系列（13 と同じく、月内一定の容量で時間別の出力を割る）:
       主（前倒し）: 容量の計上を次の四半期末の値に前倒しする。2023年4〜5月は2023年6月末の82.9万kW、
         2023年11月〜2024年2月は2024年3月末の126.5万kW（監査 v_cf_kwind.py の B_stepfwd と同じ）。
       代替1（実効容量）: 2023年4・5・10〜12月と2024年1〜3月を、同じ暦月の他の年の cf の中央値で逆算した容量に置く。
         ただし表Bの値を下限、各エピソードの前倒し先（82.9万kW・126.5万kW）を上限とする。
       代替2（ピーク下限）: 全月で、容量を「月内の最大時間出力 ÷ 0.830」以上にする。0.830 は 2023年3月〜2024年3月を
         除く全月のピーク cf の最大値で、物理的にあり得ない出力をなくす最小の補正にあたる。
     3通りは補正の大きさの幅を与える（代替2が最小、主が最大）。太陽光の cf は変更しない（ピーク cf の最大0.958、
     cf>1 の時間なし）。
  4. 感応度。価格過程の推定（純需要＝需要−制御前太陽光−制御前風力−原子力）は容量を使わないので変わらない。
     変わるのは、反実仮想で風力を加える cf の時間配分と、現行導入量 K_now（FY2023〜25 の時間平均）だけである。
     (a) 18 の風力スイープ（分断混合仕様＝13 の simulate_B、共通乱数）: 風力倍率0.5〜3×泊なし／あり の
         下限張り付き時間・TB4h中央値・完全予見粗利。13 のレバー①（風力+50万kW、絶対量）の Δ完全予見粗利。
     (b) 33 の分解（13 の仕様A・下端の線形外挿（下限あり／なし）・分断混合）: 風力1.25・2・2.5・3倍の
         Δ完全予見粗利と、稼働日の恒等式による「スプレッドの変化 3.4ΔTB4h」「往復損失の水準効果 −0.6Δ下位4h」
         「休止の切替」（表8.10 下段・8.2 の本文）。
     (c) π(K; K_wind)（26 の仕様A、θ=1。表8.6・表10.1 の泊＋風力2倍の基準行）。主任の決定 D1〜D3 に従い、限界参入者の
         収益を価格過程の価格経路の上で戦略 c（直近29日のうち同じ曜日区分の日の時刻別平均価格のランク、5日以上、同値は均等配分。
         36 と同じ定義）の実現粗利 c(K) で直接計算する。最初の履歴は FY2022 のモデル価格（同じシナリオ・θ=1）。
           π_c 実績整合(K) = (実績の c ÷ モデルの c(0))·c(K) − 1,752（主。校正係数は現状・泊なし・K=0 の
             FY2023〜25 in-sample の値で固定し、全シナリオに同じ係数を使う）
           π_c モデル直値(K) = c(K) − 1,752（下側の参考）
           旧値: 0.81·π_PF(K) − 1,752
         フリートは完全予見の増分貪欲（D3 の主）で FY2022〜25 の全日に1万kW 刻みで投入し（41 の主と同じ刻み）、
         K=0〜150万kW の1万kW ごとの各点で評価する（K=25 に正確に到達する。28 は刻み10で K=25 の行が実際には30で
         計算されている）。π=0 となる K は1万kW 格子の線形補間。補正前のシナリオは 41 の pi_k_curve_v3.csv
         （1万kW 刻み）と一致する（照合を表示）。補正前との差は K≤100万kW の全格子点での最大絶対値も出す。
         風力の加え方は二通り: 同じ倍率（(m−1)×各補正の K_now。補正後は K_now が大きいので加える量も大きい）と、
         同じ絶対量（(m−1)×補正前の K_now。cf の時間配分の違いだけを取り出す）。
     (d) 29 の λ 実験（26 の仕様A、θ=1）: 合成系列を0〜設備容量で打ち切る上限の容量だけを差し替える。
         λ=1・1.5・2・3・4 の打ち切りの割合、日内帯域の分散シェア、下限張り付き時間、TB4h中央値、p95、完全予見粗利、
         日次回帰の風力→TB4h 係数（29 と同じ HC3。推論は T4 が作り直すので点推定の差だけを見る）。
     (e) 表10.1 の泊＋風力2倍の行（32 の段差モデル、θ=1、K=0）: 下限 0.01円・0円・−5円・−10円の π(0)
         （旧値 0.81·π_PF−1,752）と θ*（資本費6.8万円/kWh・容量1.25万円・WACC 6%）。同じ行を D1 の基準
         （(c) と同じパス・校正係数で戦略 c の実現粗利を直接計算した π_c 実績整合(0)・モデル直値(0)）でも出す。
         θ*_c は 32 と同じく収益が θ に比例するとした値（(CREQ−容量収入+1,752)÷(校正係数×c(0))）。
         K>0 はフリートの配分が同値の扱い（numpy の argsort）に依存し、この環境では 32 の出力を再現しないので出さない。
     判定基準: 主要な数値（完全予見粗利・π(0)・π(K)）の変化が1%未満か。
     各部で補正前（btable）の再計算が既存の出力（kwind_sweep.csv・baseload_shift_response.csv・
     equilibrium_surface.csv・spatial_dispersion.csv・negative_price_scenarios.csv の K=0）と一致することを assert で確かめる。
出力:
  data/processed/hokkaido_cf_series_corrected.csv（時間別。cf_wind は主（前倒し）、cf_wind_btable は補正前で
    hokkaido_cf_series.csv の cf_wind と同一（有効数字10桁）。代替は cf_wind_eff・cf_wind_peak。wind_kw は主の容量（kW）、
    corrected は主で容量を差し替えた時間。代替の容量は cf_correction_monthly.csv）
  data/processed/cf_correction_monthly.csv（月次の診断と補正容量）
  data/processed/cf_correction_fy.csv（年度平均 cf、補正前後）
  data/processed/cf_correction_btable_quarters.csv（四半期の網羅と2021年3月の照合）
  data/processed/cf_correction_kwind_specB.csv（(a)）
  data/processed/cf_correction_decomp.csv（(b)）
  data/processed/cf_correction_pik.csv（(c) の全格子）、data/processed/cf_correction_pik_summary.csv（(c) の要約）
  data/processed/cf_correction_lambda.csv（(d)）、data/processed/cf_correction_negprice.csv（(e)）
  figures/hokkaido/cf_correction.png
  既存の出力は上書きしない（13・26 は exec 時に pandas.DataFrame.to_csv を一時的に無効化して読み込む）。
限界:
  - 真の運転中容量は観測できない。3通りの補正は幅を示すだけで、どれが正しいかは識別できない。前倒しは2023年12月と
    2024年2月の cf を同じ月の他の年の中央値より1割強低くするので、補正の上側（cf の下側）にあたる。
  - 主（前倒し）と代替1は2023年3月（FY2022。月 cf は同じ月の他年の中央値の1.25倍、ピーク cf 0.859 で
    他の月の最大0.830を上回る）を補正しない（3月末は表Bの観測値で、前倒しの規則の外）。代替2だけが66.1万kWに上げる。
    FY2022 は FY2023〜25 の評価には入らず、(c)(e) の戦略 c の最初の履歴（FY2023 の4月初めの窓）にだけ入る。
  - 補正の向きの外部情報は一様でない。JWPA の年末導入量（2023年末83万kW）は表B（86.4万kW）より小さく、
    2023年12月の出力が表Bの容量を上回ることは非FIT設備だけでは説明しにくく、試運転中の発電の先行が主因とみられる
    （JWPA と表Bの計上基準の違いは確かめていない）。主（2023年11月〜2024年2月を126.5万kW）は補正の上側（cf の下側）として読む。
  - 同じ暦月の中央値による逆算は、風の強い月と容量の過小計上を区別できない（月次 cf の年々の標準偏差は0.02〜0.06）。
    このため逆算は、ピーク cf の外れ（2023年4月・11月〜2024年2月）と表Bの跳び（2023年3月→6月、2023年12月→2024年3月）が
    重なるエピソードに限る。
  - 容量の水準の偏り（非FIT設備を含まないこと）は cf の水準を上げるが、反実仮想で加える風力（(m−1)×K_now×cf_t）では
    K_now と cf_t の比として打ち消し合うので効かない。効くのは容量の時間配分のずれだけである。
  - π_c の校正係数は FY2023〜25 の in-sample の値。風力・泊のシナリオ（推定範囲外への外挿を含む。風力3倍では純需要が
    g の推定範囲より下に出る時間が増える。33 参照）でも同じ係数が成り立つとは限らない。
  - 分断混合仕様は共通乱数（乱数種20260728、13 と同じ）の単一パス。乱数種による ΔPF の SD は約30〜50円/kW-年（監査）。
  - K>0 の π(K) は増分貪欲の経路に依存し、補正前後の差は格子点ごとに数十円〜110円程度ばらつく（経路の雑音を含む）。
    刻みを5万kW にすると π=0 の K の補正前後差が変わる（旧基準・泊あり×3 で +2.9万kW、1万kW 刻みでは +0.2万kW）ので、
    本スクリプトは 41 と同じ1万kW 刻みを使う。
"""
import contextlib
import io
import logging
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib import font_manager
import matplotlib.dates as mdates
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
RAW = os.path.join(ROOT, "data", "raw", "fit_b")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY, INK = "#595959", "#1a1a1a"
C_ORIG, C_MAIN = "#D95B20", "#0079C2"

ETA = 0.85
FLOOR = 0.01
CAPTURE = 0.81
CHARGE_COST = 4 * 365 * 1.2                  # 1,752 円/kW-年（充電従量負担）
TOMARI = 912_000 * 0.9 / 1000                 # 820.8 MW（泊3号 91.2万kW×稼働率90%）
SLICE = 1                                     # 万kW（フリートの刻み。41 の主と同じ）
K_GRID = list(range(0, 151, SLICE))           # 0〜150万kW を1万kW ごとに評価（D2: 目標の K に正確に到達）
SUSPECT = [str(x) for x in pd.period_range("2023-03", "2024-03", freq="M")]   # 参照分布から除く月
VARS = ["btable", "step", "eff", "peak"]
VLAB = {"btable": "補正前（表B）", "step": "主（前倒し）", "eff": "代替1（実効容量）", "peak": "代替2（ピーク下限）"}
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)


def fy_of(ts):
    return ts.dt.year - (ts.dt.month < 4).astype(int)


def load_module(fname, modname):
    """既存スクリプトを exec で読み込む（to_csv を無効化し、標準出力を捨てる。既存の出力は書かない）"""
    ns = {"__file__": os.path.join(HERE, fname), "__name__": modname}
    _to_csv = pd.DataFrame.to_csv
    pd.DataFrame.to_csv = lambda *a, **k: None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(open(os.path.join(HERE, fname), encoding="utf-8").read(), ns)
    finally:
        pd.DataFrame.to_csv = _to_csv
    return ns


# ====================================================================
# 1. 表Bの四半期の網羅と 2021年3月の照合
# ====================================================================
q = pd.read_csv(os.path.join(PROC, "fit_capacity_pref_quarterly.csv"), parse_dates=["date"])
qh = q[q["pref"] == "北海道"].set_index("date").sort_index()
all_q = pd.date_range("2014-06-30", "2025-12-31", freq="QE")
missing_q = all_q.difference(qh.index)
raw_files = sorted(f for f in os.listdir(RAW) if f.lower().endswith((".xls", ".xlsx")))
used_files = [f for f in raw_files if "B_city" in f]
unused_files = [f for f in raw_files if "B_city" not in f]
print(f"表B: 四半期 {len(all_q)}（2014年6月〜2025年12月）、集計に使われた日付 {qh.index.nunique()}、"
      f"欠落 {[d.strftime('%Y-%m') for d in missing_q]}")
print(f"data/raw/fit_b: {len(raw_files)} ファイル、12 の glob（B_city）で読まれる {len(used_files)}、"
      f"読まれない {unused_files}")

area_cap = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
ns12 = {"__file__": os.path.join(HERE, "12_fit_capacity_series.py"), "__name__": "fit_cap_12"}
exec(open(os.path.join(HERE, "12_fit_capacity_series.py"), encoding="utf-8").read(), ns12)   # 関数定義のみ
f202103 = os.path.join(RAW, "B_pref202103.xlsx")
tot = None
for sheet in ["表B②－１", "表B②－２"]:
    g_ = ns12["parse_sheet"](f202103, sheet)
    tot = g_ if tot is None else tot.add(g_, fill_value=0)
chk_rows = []
for area, prefs in ns12["AREAS"].items():
    act = tot.loc[prefs].sum()
    itp = area_cap[(area_cap["area"] == area) & (area_cap["date"] == pd.Timestamp("2021-03-31"))].iloc[0]
    for src in ("solar_kw", "wind_kw"):
        chk_rows.append({"area": area, "電源": "太陽光" if src == "solar_kw" else "風力",
                         "B_pref202103(万kW)": round(act[src] / 1e4, 2), "月次補間値(万kW)": round(itp[src] / 1e4, 2),
                         "差(万kW)": round((act[src] - itp[src]) / 1e4, 2),
                         "差(%)": round((act[src] / itp[src] - 1) * 100, 2)})
chk = pd.DataFrame(chk_rows)
print("2021年3月末: B_pref202103.xlsx と月次線形補間の比較"); print(chk.to_string(index=False))
qrows = []
hk_area = area_cap[area_cap["area"] == "hokkaido"].set_index("date")
for d in all_q:
    inq = d in qh.index
    src = qh.loc[d] if inq else hk_area.loc[d]
    r = {"四半期末": d.strftime("%Y-%m-%d"), "表Bの集計に含む": inq,
         "北海道風力(万kW)": round(src["wind_kw"] / 1e4, 2), "北海道太陽光(万kW)": round(src["solar_kw"] / 1e4, 2),
         "備考": "" if inq else "欠落（12 で線形補間）"}
    if d == pd.Timestamp("2021-03-31"):
        hk = tot.loc["北海道"]
        r["備考"] = (f"欠落（12 で線形補間）。B_pref202103.xlsx（未使用）では風力{hk['wind_kw']/1e4:.2f}万kW・"
                   f"太陽光{hk['solar_kw']/1e4:.2f}万kW")
    qrows.append(r)
pd.DataFrame(qrows).to_csv(os.path.join(PROC, "cf_correction_btable_quarters.csv"), index=False)

# ====================================================================
# 2. 月次の診断
# ====================================================================
p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
p["ym"] = p["ts"].dt.strftime("%Y-%m")
cap = hk_area[["solar_kw", "wind_kw"]]
full = pd.date_range(cap.index.min(), pd.Timestamp("2026-06-30"), freq="ME")    # 13 と同じ（2025/12 以降は直近値）
cap = cap.reindex(full.union(cap.index)).ffill()
cap.index = cap.index.strftime("%Y-%m")
capB = cap["wind_kw"].copy()
capS = cap["solar_kw"].copy()

mon = p.groupby("ym").agg(energy_mwh=("wind_pre", "sum"), hours=("wind_pre", "size"), peak_mw=("wind_pre", "max"),
                          solar_mwh=("solar_pre", "sum"), solar_peak_mw=("solar_pre", "max"))
mon["month"] = [int(s[5:7]) for s in mon.index]
mon["fy"] = [int(s[:4]) - (int(s[5:7]) < 4) for s in mon.index]
mon["cap_btable_kw"] = capB.reindex(mon.index).to_numpy()
mon["cf_btable"] = mon["energy_mwh"] * 1000 / (mon["cap_btable_kw"] * mon["hours"])
mon["peakcf_btable"] = mon["peak_mw"] * 1000 / mon["cap_btable_kw"]
mon["solar_cf"] = mon["solar_mwh"] * 1000 / (capS.reindex(mon.index).to_numpy() * mon["hours"])
mon["solar_peakcf"] = mon["solar_peak_mw"] * 1000 / capS.reindex(mon.index).to_numpy()
clean = ~mon.index.isin(SUSPECT)
ref = mon[clean].groupby("month")["cf_btable"].agg(["median", "min", "max", "std", "count"])
for c_ in ["median", "min", "max", "std", "count"]:
    mon[f"ref_{c_}"] = mon["month"].map(ref[c_]).to_numpy()
mon["ratio_to_ref_median"] = mon["cf_btable"] / mon["ref_median"]
mon["z_vs_ref"] = (mon["cf_btable"] - mon["ref_median"]) / mon["ref_std"]
mon["cap_implied_kw"] = mon["energy_mwh"] * 1000 / (mon["ref_median"] * mon["hours"])
PEAK_Q = float(mon.loc[clean, "peakcf_btable"].max())
print(f"\nピーク cf（月内の最大時間出力÷容量）: 2023/3〜2024/3 を除く {int(clean.sum())} か月の最大 {PEAK_Q:.3f}、"
      f"95%点 {mon.loc[clean, 'peakcf_btable'].quantile(.95):.3f}")

# ---------- 3. 補正容量 ----------
STEP_RULE = {"2023-04": "2023-06", "2023-05": "2023-06",
             "2023-11": "2024-03", "2023-12": "2024-03", "2024-01": "2024-03", "2024-02": "2024-03"}
EFF_RULE = {"2023-04": "2023-06", "2023-05": "2023-06", "2023-10": "2024-03", "2023-11": "2024-03",
            "2023-12": "2024-03", "2024-01": "2024-03", "2024-02": "2024-03", "2024-03": "2024-03"}
cap_step = capB.copy()
for ym, tgt in STEP_RULE.items():
    cap_step[ym] = capB[tgt]
cap_eff = capB.copy()
for ym, tgt in EFF_RULE.items():
    cap_eff[ym] = min(max(capB[ym], mon.loc[ym, "cap_implied_kw"]), capB[tgt])
cap_peak = capB.copy()
pk = (mon["peak_mw"] * 1000 / PEAK_Q).reindex(cap_peak.index)
cap_peak = pd.Series(np.where(pk.notna(), np.maximum(cap_peak.to_numpy(), pk.fillna(0).to_numpy()), cap_peak.to_numpy()),
                     index=cap_peak.index)
CAPMAP = {"btable": capB, "step": cap_step, "eff": cap_eff, "peak": cap_peak}
assert abs(capB["2023-06"] - 828_915.3) < 1 and abs(capB["2024-03"] - 1_264_545.6) < 1

for v in VARS:
    mon[f"cap_{v}_kw"] = CAPMAP[v].reindex(mon.index).to_numpy()
    mon[f"cf_{v}"] = mon["energy_mwh"] * 1000 / (mon[f"cap_{v}_kw"] * mon["hours"])
    mon[f"peakcf_{v}"] = mon["peak_mw"] * 1000 / mon[f"cap_{v}_kw"]
    mon[f"ratio_{v}"] = mon[f"cf_{v}"] / mon["ref_median"]

# 時間別の cf 系列
for v in VARS:
    p[f"wind_kw_{v}"] = p["ym"].map(CAPMAP[v]).to_numpy()
    p[f"cf_wind_{v}"] = p["wind_pre"] / (p[f"wind_kw_{v}"] / 1000)
p["solar_kw"] = p["ym"].map(capS).to_numpy()
p["cf_solar"] = p["solar_pre"] / (p["solar_kw"] / 1000)
old = pd.read_csv(os.path.join(PROC, "hokkaido_cf_series.csv"), parse_dates=["ts"])
assert (old["ts"].to_numpy() == p["ts"].to_numpy()).all()
assert np.allclose(old["cf_wind"], p["cf_wind_btable"], equal_nan=True, rtol=0, atol=1e-12)
assert np.allclose(old["cf_solar"], p["cf_solar"], equal_nan=True, rtol=0, atol=1e-12)
for v in VARS:
    over = p[f"cf_wind_{v}"] > 1
    print(f"  {VLAB[v]}: cf>1 の時間 {int(over.sum())}"
          f"{(' ' + str(sorted(p.loc[over, 'ym'].unique()))) if over.any() else ''}、時間 cf の最大 {p[f'cf_wind_{v}'].max():.3f}")
out_cf = pd.DataFrame({
    "ts": p["ts"], "cf_solar": p["cf_solar"], "cf_wind": p["cf_wind_step"],
    "cf_wind_btable": p["cf_wind_btable"], "cf_wind_eff": p["cf_wind_eff"], "cf_wind_peak": p["cf_wind_peak"],
    "wind_kw": p["wind_kw_step"], "corrected": p["wind_kw_step"] != p["wind_kw_btable"]})
# 代替の容量（月次）は cf_correction_monthly.csv にある。有効数字10桁で書く（補正前の列は既存の cf と1e-9 以内で一致）
out_cf.to_csv(os.path.join(PROC, "hokkaido_cf_series_corrected.csv"), index=False, float_format="%.10g")

mon_out = mon.copy()
mon_out.insert(0, "ym", mon_out.index)
for c_ in [c for c in mon_out.columns if c.endswith("_kw")]:
    mon_out[c_.replace("_kw", "(万kW)")] = (mon_out.pop(c_) / 1e4).round(2)
mon_out["energy(GWh)"] = (mon_out.pop("energy_mwh") / 1000).round(1)
mon_out["solar_energy(GWh)"] = (mon_out.pop("solar_mwh") / 1000).round(1)
num = mon_out.select_dtypes("number").columns
mon_out[num] = mon_out[num].round(4)
mon_out["参照分布から除外"] = mon_out["ym"].isin(SUSPECT)
mon_out.to_csv(os.path.join(PROC, "cf_correction_monthly.csv"), index=False)
show = mon.loc["2023-01":"2024-06", ["cap_btable_kw", "peak_mw", "cf_btable", "peakcf_btable", "ref_median",
                                      "ratio_to_ref_median", "z_vs_ref", "cap_implied_kw", "cap_step_kw",
                                      "cap_eff_kw", "cap_peak_kw", "ratio_step", "ratio_eff", "ratio_peak"]].copy()
for c_ in [c for c in show.columns if c.endswith("_kw")]:
    show[c_] = show[c_] / 1e4
print("\n=== 月次の診断（容量は万kW） ==="); print(show.round(3).to_string())

# 年度平均
p["fy_"] = fy_of(p["ts"])
fy_rows = []
for fy, g_ in p.groupby("fy_"):
    r = {"FY": int(fy), "時間数": len(g_), "通年": len(g_) >= 8760}
    for v in VARS:
        r[f"cf_wind_{v}"] = g_[f"cf_wind_{v}"].mean()
    r["cf_solar"] = g_["cf_solar"].mean()
    fy_rows.append(r)
fyc = pd.DataFrame(fy_rows)
full_fy = fyc[fyc["通年"] & fyc["FY"].between(2016, 2025)]
for lab, agg in (("FY2016〜25 最小", "min"), ("FY2016〜25 最大", "max")):
    r = {"FY": lab, "時間数": np.nan, "通年": True}
    for c_ in [c for c in fyc.columns if c.startswith("cf_")]:
        r[c_] = getattr(full_fy[c_], agg)()
    fy_rows.append(r)
fyc = pd.DataFrame(fy_rows)
fyc_out = fyc.copy()
for c_ in [c for c in fyc_out.columns if c.startswith("cf_")]:
    fyc_out[c_] = fyc_out[c_].astype(float).round(4)
fyc_out.to_csv(os.path.join(PROC, "cf_correction_fy.csv"), index=False)
print("\n=== 年度平均 cf（時間平均） ==="); print(fyc_out.to_string(index=False))

# ====================================================================
# 4(a). 分断混合仕様の風力スイープ（18）とレバー①（13）
# ====================================================================
ns13 = load_module("13_price_process_v1.py", "pp_v1")
est13 = ns13["est"]
simulate_B = ns13["simulate_B"]
assert est13["ts"].is_monotonic_increasing and len(est13) % 24 == 0
assert (est13.groupby("day").size() == 24).all()


def attach(df, v):
    d = df.copy()
    ym = d["ts"].dt.strftime("%Y-%m")
    d["wind_kw"] = ym.map(CAPMAP[v]).to_numpy()
    d["cf_wind"] = d["wind_pre"] / (d["wind_kw"] / 1000)
    return d


assert np.allclose(attach(est13, "btable")["cf_wind"], est13["cf_wind"])
K_NOW = {v: attach(est13, v)["wind_kw"].mean() / 1e4 for v in VARS}
print("\n現行の風力導入量 K_now（FY2023〜25 の時間平均、万kW）:", {VLAB[v]: round(k, 2) for v, k in K_NOW.items()})


def fast_metrics(df, pcol):
    """13 の metrics と同じ定義（日がすべて24時間であることを前提に配列で計算）。年度ごとの値を返す"""
    P = df[pcol].to_numpy().reshape(-1, 24)
    fy = df["fy"].to_numpy()[::24]
    srt = np.sort(P, axis=1)
    tb = srt[:, -4:].mean(1) - srt[:, :4].mean(1)
    pf = np.maximum(0.0, ETA * srt[:, -4:].sum(1) - srt[:, :4].sum(1))
    fl = (P <= 0.011).sum(1)
    out = {}
    for f_ in np.unique(fy):
        m = fy == f_
        out[int(f_)] = {"floor": fl[m].sum(), "tb_med": np.median(tb[m]), "pf": pf[m].sum(),
                        "p95": np.quantile(P[m].ravel(), 0.95)}
    return pd.DataFrame(out).T


base13 = est13.copy()
base13["p_B"] = simulate_B(base13)
_m13 = ns13["metrics"](base13, "p_B")
_fm = fast_metrics(base13, "p_B")
# 13 の metrics の列名（既存の出力の列名なので変えない）と照合
assert np.allclose(_m13["PF価値(円/kW-年)"].to_numpy(), _fm["pf"].round(0).to_numpy(), atol=0.51)
assert np.allclose(_m13["床(≤0.01円)時間"].to_numpy(), _fm["floor"].to_numpy())

MULTS18 = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
ks_old = pd.read_csv(os.path.join(PROC, "kwind_sweep.csv"))
rows_a = []
for v in VARS:
    e = attach(est13, v)
    for tl, tom in (("なし", 0.0), ("あり", TOMARI)):
        for m in MULTS18:
            for mode in ("同じ倍率", "同じ絶対量"):
                if mode == "同じ絶対量" and (v == "btable" or m == 1.0):
                    continue
                knw = K_NOW[v] if mode == "同じ倍率" else K_NOW["btable"]
                add = (m - 1.0) * knw * 1e4 * e["cf_wind"] / 1000
                sc = e.copy()
                sc["net"] = sc["net"] - add - tom
                sc["p_B"] = simulate_B(sc)
                fm = fast_metrics(sc, "p_B")
                rows_a.append({"補正": v, "補正名": VLAB[v], "泊": tl, "風力の加え方": mode, "K_wind倍率": m,
                               "K_now(万kW)": round(K_NOW[v], 2), "K_wind(万kW)": round(knw * (m - 1) + K_NOW[v], 1),
                               "加えた風力(GWh/年)": round(add.sum() / 3 / 1000, 1),
                               "下限張り付き時間(h/年)": fm["floor"].mean(), "TB4h中央値(円/kWh)": fm["tb_med"].mean(),
                               "p95(円/kWh)": fm["p95"].mean(), "完全予見粗利(円/kW-年)": fm["pf"].mean(),
                               "完全予見粗利_FY2023": fm.loc[2023, "pf"], "完全予見粗利_FY2024": fm.loc[2024, "pf"],
                               "完全予見粗利_FY2025": fm.loc[2025, "pf"]})
                if v == "btable":   # 18 の再現（18 は年度値を丸めてから平均する）
                    o = ks_old[(ks_old["泊"] == tl) & np.isclose(ks_old["K_wind倍率"], m)].iloc[0]
                    assert abs(fm["pf"].round(0).mean() - o["PF価値(円/kW-年)"]) <= 0.51, (tl, m)
                    assert abs(fm["floor"].mean() - o["床時間(h/年)"]) <= 0.51, (tl, m)
                    assert abs(fm["tb_med"].round(2).mean() - o["TB4h中央値(円/kWh)"]) <= 0.0051, (tl, m)
# レバー①（風力+50万kW、絶対量）
for v in VARS:
    e = attach(est13, v)
    sc = e.copy()
    sc["net"] = sc["net"] - 500_000 * sc["cf_wind"] / 1000
    sc["p_B"] = simulate_B(sc)
    fm1, fm0 = fast_metrics(sc, "p_B"), fast_metrics(e.assign(p_B=base13["p_B"].to_numpy()), "p_B")
    d = fm1["pf"] - fm0["pf"]
    rows_a.append({"補正": v, "補正名": VLAB[v], "泊": "なし", "風力の加え方": "レバー①（+50万kW）", "K_wind倍率": np.nan,
                   "K_now(万kW)": round(K_NOW[v], 2), "K_wind(万kW)": round(K_NOW[v] + 50, 1),
                   "加えた風力(GWh/年)": round((500_000 * e["cf_wind"] / 1000).sum() / 3 / 1000, 1),
                   "下限張り付き時間(h/年)": fm1["floor"].mean(), "TB4h中央値(円/kWh)": fm1["tb_med"].mean(),
                   "p95(円/kWh)": fm1["p95"].mean(), "完全予見粗利(円/kW-年)": fm1["pf"].mean(),
                   "完全予見粗利_FY2023": d.loc[2023], "完全予見粗利_FY2024": d.loc[2024], "完全予見粗利_FY2025": d.loc[2025],
                   "ΔPF平均": d.mean(), "ΔPF最小": d.min(), "ΔPF最大": d.max()})
res_a = pd.DataFrame(rows_a)
num = res_a.select_dtypes("number").columns
res_a[num] = res_a[num].round(3)
res_a.to_csv(os.path.join(PROC, "cf_correction_kwind_specB.csv"), index=False)
print("\n=== (a) 分断混合仕様の風力スイープ（18）: 完全予見粗利（円/kW-年） ===")
pv = res_a[res_a["風力の加え方"] == "同じ倍率"].pivot_table(index=["泊", "K_wind倍率"], columns="補正",
                                                         values="完全予見粗利(円/kW-年)")[VARS]
for v in VARS[1:]:
    pv[f"Δ{v}(%)"] = (pv[v] / pv["btable"] - 1) * 100
print(pv.round(2).to_string())
pv2 = res_a[res_a["風力の加え方"] == "同じ倍率"].pivot_table(index=["泊", "K_wind倍率"], columns="補正",
                                                          values="下限張り付き時間(h/年)")[VARS]
print("下限張り付き時間（h/年）"); print(pv2.round(1).to_string())
print("同じ絶対量（補正前の K_now×(m−1) を加える）:")
print(res_a[res_a["風力の加え方"] == "同じ絶対量"].pivot_table(index=["泊", "K_wind倍率"], columns="補正",
                                                         values="完全予見粗利(円/kW-年)").round(1).to_string())
print("レバー①:"); print(res_a[res_a["風力の加え方"].str.startswith("レバー")][
    ["補正名", "ΔPF平均", "ΔPF最小", "ΔPF最大"]].to_string(index=False))

# ====================================================================
# 4(b). 33 の分解（仕様A・線形外挿・分断混合、13 の部品）
# ====================================================================
GA, ADJ_A = ns13["GA"], ns13["ADJ_A"]
e33 = est13.sort_values("ts").reset_index(drop=True).copy()
e33["hour"] = e33["ts"].dt.hour
N_DAYS = e33["day"].nunique()
assert len(e33) == N_DAYS * 24
SEAS = e33["season"].to_numpy()
MU = ADJ_A.reindex(pd.MultiIndex.from_arrays([SEAS, e33["hour"].to_numpy()])).fillna(0).to_numpy()
DAYS = pd.DatetimeIndex(e33["day"].to_numpy().reshape(N_DAYS, 24)[:, 0])
FY_D = np.asarray(DAYS.year - (DAYS.month < 4).astype(int))
NET0 = e33["net"].to_numpy()
EXT = {}
for s_ in range(4):
    x_, y_ = GA[s_]
    i0 = int(np.argmax(y_ > FLOOR + 0.001))
    EXT[s_] = (x_[i0], y_[i0], np.polyfit(x_[i0:i0 + 8], y_[i0:i0 + 8], 1)[0])


def g_curve(net, mode):
    out = np.empty(len(net))
    for s_ in range(4):
        m = SEAS == s_
        x_, y_ = GA[s_]
        if mode == "A":
            out[m] = np.interp(net[m], x_, y_, left=FLOOR, right=y_[-1])
        else:
            xa, ya, sl = EXT[s_]
            v_ = np.interp(net[m], x_, y_, right=y_[-1])
            lo = net[m] < xa
            v_[lo] = ya + sl * (net[m][lo] - xa)
            out[m] = v_
    return out


def price33(net, variant):
    if variant == "仕様A":
        return np.maximum(np.maximum(g_curve(net, "A"), FLOOR) + MU, FLOOR)
    if variant == "外挿・下限あり":
        return np.maximum(np.maximum(g_curve(net, "ext"), FLOOR) + MU, FLOOR)
    if variant == "外挿・下限なし":
        return g_curve(net, "ext") + MU
    if variant == "仕様B":
        return simulate_B(e33.assign(net=net))
    raise ValueError(variant)


assert np.allclose(price33(NET0, "仕様A"), ns13["predict_A"](e33))


def day_stats(pr):
    P = pr.reshape(N_DAYS, 24)
    srt = np.sort(P, axis=1)
    top, bot = srt[:, -4:].mean(1), srt[:, :4].mean(1)
    x = 3.4 * top - 4 * bot
    return {"top": top, "bot": bot, "x": x, "pf": np.maximum(0.0, x), "floor": (P <= FLOOR + 0.001).sum(1)}


def per_fy(v_):
    return pd.Series(v_).groupby(FY_D).sum().mean()


bsr = pd.read_csv(os.path.join(PROC, "baseload_shift_response.csv"))
rows_b = []
MODELS = ["仕様A", "外挿・下限あり", "外挿・下限なし", "仕様B"]
for v in VARS:
    cfw = attach(e33, v)["cf_wind"].to_numpy()
    for var in MODELS:
        for tl, tom, mults in (("なし", 0.0, [1.25, 2.0, 3.0]), ("泊3号", TOMARI, [2.0, 2.5, 3.0])):
            st0 = day_stats(price33(NET0 - tom, var))
            for m in mults:
                st1 = day_stats(price33(NET0 - (m - 1.0) * K_NOW[v] * 1e4 * cfw / 1000 - tom, var))
                both = (st0["x"] > 0) & (st1["x"] > 0)
                spread = np.where(both, 3.4 * ((st1["top"] - st1["bot"]) - (st0["top"] - st0["bot"])), 0.0)
                level = np.where(both, -0.6 * (st1["bot"] - st0["bot"]), 0.0)
                dpf = st1["pf"] - st0["pf"]
                r = {"補正": v, "補正名": VLAB[v], "モデル": var, "泊": tl, "風力倍率": m,
                     "完全予見粗利": per_fy(st1["pf"]), "Δ完全予見粗利": per_fy(dpf),
                     "うちスプレッドの変化(3.4ΔTB4h)": per_fy(spread), "うち往復損失の水準効果(−0.6Δ下位)": per_fy(level),
                     "うち休止の切替": per_fy(dpf - spread - level),
                     "上位4h平均": st1["top"].mean(), "下位4h平均": st1["bot"].mean(),
                     "Δ上位4h": st1["top"].mean() - st0["top"].mean(), "Δ下位4h": st1["bot"].mean() - st0["bot"].mean(),
                     "下限張り付き時間(h/年)": per_fy(st1["floor"].astype(float))}
                rows_b.append(r)
                if v == "btable":
                    o = bsr[(bsr["系列"] == "風力倍率") & (bsr["モデル"] == var) & (bsr["泊"] == tl)
                            & np.isclose(bsr["風力倍率"], m) & (bsr["季節"] == "年間")].iloc[0]
                    assert abs(o["完全予見粗利"] - r["完全予見粗利"]) < 0.01, (var, tl, m)
                    assert abs(o["Δ完全予見粗利"] - r["Δ完全予見粗利"]) < 0.01, (var, tl, m)
res_b = pd.DataFrame(rows_b)
num = res_b.select_dtypes("number").columns
res_b[num] = res_b[num].round(3)
res_b.to_csv(os.path.join(PROC, "cf_correction_decomp.csv"), index=False)
print("\n=== (b) 分解（円/kW-年）: Δ完全予見粗利（うちスプレッドの変化） ===")
tmp_b = res_b.assign(cell=lambda d: d["Δ完全予見粗利"].round(0).astype(int).astype(str) + "（"
                     + d["うちスプレッドの変化(3.4ΔTB4h)"].round(0).astype(int).astype(str) + "）")
print(tmp_b.pivot_table(index=["泊", "モデル", "風力倍率"], columns="補正", values="cell", aggfunc="first")[VARS].to_string())
print(res_b[(res_b["モデル"] == "仕様A") & (res_b["泊"] == "なし") & (res_b["風力倍率"] == 1.25)][
    ["補正名", "Δ上位4h", "Δ下位4h", "Δ完全予見粗利", "うち往復損失の水準効果(−0.6Δ下位)"]].round(3).to_string(index=False))
print(res_b[(res_b["モデル"] == "仕様A") & (res_b["泊"] == "泊3号")][["補正名", "風力倍率", "完全予見粗利"]]
      .pivot_table(index="風力倍率", columns="補正名", values="完全予見粗利").round(0).to_string())

# ====================================================================
# 4(c). π(K; K_wind)（26 の仕様A・θ=1）。戦略 c の実現粗利を直接計算（D1〜D3）
# ====================================================================
ns26 = load_module("26_price_process_v2.py", "pp_v2")
samp, est26, predict_A26 = ns26["samp"], ns26["est"], ns26["predict_A"]
K_NOW26 = {v: attach(est26, v)["wind_kw"].mean() / 1e4 for v in VARS}
assert all(abs(K_NOW26[v] - K_NOW[v]) < 1e-9 for v in VARS)   # 13 と 26 の推定標本は同じ時間
s = samp[samp["fy"].isin([2022, 2023, 2024, 2025])].sort_values("ts").copy()
s["date"] = s["ts"].dt.normalize()
pn = s.pivot_table(index="date", columns="hour", values="net")
pa = s.pivot_table(index="date", columns="hour", values="p_hokkaido")
ok = pn.notna().all(axis=1) & pa.notna().all(axis=1) & (s.groupby("date").size().reindex(pn.index) == 24)
days = pn.index[ok.to_numpy()]
tmp = s[s["date"].isin(days)].sort_values("ts").reset_index(drop=True)
n = len(days)
assert len(tmp) == n * 24
FYd = np.asarray(days.year - (days.month < 4).astype(int))
WK = np.asarray(days.dayofweek >= 5)
EV = np.where(FYd >= 2023)[0]
HIST = [[j for j in range(max(0, i - 29), i) if WK[j] == WK[i]] for i in EV]
assert min(len(h) for h in HIST) >= 5
FY_EV = FYd[EV]
PA = pa.loc[days].to_numpy()
ROWSEL = np.arange(n)[:, None]
print(f"\n(c) パス: FY2022〜25 の {n} 日（評価は FY2023〜25 の {len(EV)} 日、最初の履歴は FY2022 の {int((FYd == 2022).sum())} 日）")


def model(net2d):
    return predict_A26(tmp.assign(net=net2d.reshape(-1)), net_col="net", theta=1.0).reshape(n, 24)


def tw_mat(S, k=4):
    """信号の下位 k 時間の重み（境界の同値は均等配分。36 の tie_weights を行ごとに適用）"""
    thr = np.sort(S, axis=1)[:, k - 1:k]
    w = (S < thr).astype(float)
    tied = S == thr
    rem = k - w.sum(axis=1, keepdims=True)
    return np.where(tied, rem / tied.sum(axis=1, keepdims=True), w)


def eval_cpf(P):
    Pe = P[EV]
    CL = np.stack([P[h].mean(axis=0) for h in HIST])
    c = ETA * (tw_mat(-CL) * Pe).sum(1) - (tw_mat(CL) * Pe).sum(1)
    srt = np.sort(Pe, axis=1)
    pf = np.maximum(0.0, ETA * srt[:, -4:].sum(1) - srt[:, :4].sum(1))
    return pd.Series(c).groupby(FY_EV).sum().mean(), pd.Series(pf).groupby(FY_EV).sum().mean()


C_ACT, PF_ACT = eval_cpf(PA)
NET_BASE = tmp["net"].to_numpy().reshape(n, 24)
C0, PF0 = eval_cpf(model(NET_BASE))
CAL = C_ACT / C0
print(f"実績価格: 戦略c {C_ACT:,.1f}・完全予見粗利 {PF_ACT:,.1f}（capture {C_ACT / PF_ACT:.4f}）")
print(f"モデル価格（現状・K=0）: 戦略c {C0:,.1f}・完全予見粗利 {PF0:,.1f}（capture {C0 / PF0:.4f}）、校正係数 {CAL:.4f}")
assert abs(C_ACT - 8427) < 5 and abs(PF_ACT - 10317) < 5 and abs(PF0 - 8266) < 2


def step_fleet(adj, sl):
    P = model(adj)
    order = np.argsort(P, axis=1)                                 # 28 と同じ（既定のソート）
    chg, dis = order[:, :4], order[:, -4:]
    mg = np.take_along_axis(P, dis, 1).sum(1) * ETA - np.take_along_axis(P, chg, 1).sum(1)
    act = mg > 0
    adj[ROWSEL[act], chg[act]] += sl * 10.0
    adj[ROWSEL[act], dis[act]] -= sl * 10.0 * ETA


def pis(c, pf):
    return {"π_旧(0.81PF)": CAPTURE * pf - CHARGE_COST, "π_c_モデル直値": c - CHARGE_COST,
            "π_c_実績整合": CAL * c - CHARGE_COST}


PIV = ["π_旧(0.81PF)", "π_c_モデル直値", "π_c_実績整合"]


def run_pik(net0, grid=K_GRID, sl=SLICE):
    """刻み sl（万kW）の増分貪欲で grid の各 K を評価し、π=0 となる K を grid 上の線形補間で求める"""
    adj = net0.copy()
    done, rows = 0, []
    for K in grid:
        while done < K:
            step_fleet(adj, sl)
            done += sl
        c, pf = eval_cpf(model(adj))
        rows.append({"K(万kW)": K, "π_PF": pf, "c": c, **pis(c, pf)})
    df = pd.DataFrame(rows)
    zero = {}
    ks = np.asarray(grid, float)
    for pv_ in PIV:
        y = df[pv_].to_numpy()
        neg = np.where(y <= 0)[0]
        if len(neg) == 0:
            zero[pv_] = np.nan
            continue
        j = neg[0]
        zero[pv_] = ks[0] if j == 0 else ks[j - 1] + y[j - 1] / (y[j - 1] - y[j]) * (ks[j] - ks[j - 1])
    return df, zero


# 28 の再現の確認（刻み10、K=0・10・30。28 の「25」の行は30で計算されている）
eqs = pd.read_csv(os.path.join(PROC, "equilibrium_surface.csv"))
_chk, _ = run_pik(NET_BASE, grid=[0, 10, 30], sl=10)
_o = eqs[(eqs["泊"] == "なし") & (eqs["K_wind倍率"] == 1.0)].set_index("K(万kW)")["π_PF(円/kW-年)"]
print("28 の再現（現状・泊なし、刻み10）: K=0/10/30 →", _chk["π_PF"].round(0).tolist(),
      "／28 の K=0/10/「25」:", [_o[0], _o[10], _o[25]])
assert abs(_chk["π_PF"].iloc[0] - _o[0]) <= 0.51 and abs(_chk["π_PF"].iloc[1] - _o[10]) <= 0.51
assert abs(_chk["π_PF"].iloc[2] - _o[25]) <= 3

CFW26 = {v: attach(tmp, v)["cf_wind"].to_numpy().reshape(n, 24) for v in VARS}
MULTS26 = [0.5, 1.0, 1.25, 1.5, 2.0, 3.0]
rows_c, rows_cs = [], []
for tl, tom in (("なし", 0.0), ("あり", TOMARI)):
    for v in VARS:
        for m in MULTS26:
            for mode in ("同じ倍率", "同じ絶対量"):
                if m == 1.0 and (v != "btable" or mode != "同じ倍率"):
                    continue
                if mode == "同じ絶対量" and (v == "btable" or m not in (2.0, 3.0)):
                    continue
                knw = K_NOW26[v] if mode == "同じ倍率" else K_NOW26["btable"]
                net0 = NET_BASE - (m - 1.0) * knw * 1e4 * CFW26[v] / 1000 - tom
                df, zero = run_pik(net0)
                vv = "全補正共通" if m == 1.0 else v
                lab = dict(補正=vv, 補正名=VLAB.get(vv, "全補正共通（風力1倍は補正の影響なし）"), 泊=tl, 風力の加え方=mode,
                           K_wind倍率=m, **{"K_now(万kW)": round(K_NOW26[v], 2),
                                            "K_wind(万kW)": round(K_NOW26[v] + (m - 1) * knw, 1)})
                for _, r in df.iterrows():
                    rows_c.append({**lab, **r.to_dict(), "capture_c(c/PF)": r["c"] / r["π_PF"]})
                summ = {**lab}
                for K in (0, 10, 25, 50, 100, 150):
                    rr = df[df["K(万kW)"] == K].iloc[0]
                    summ[f"π_PF K{K}"] = rr["π_PF"]
                    for pv_ in PIV:
                        summ[f"{pv_} K{K}"] = rr[pv_]
                for pv_ in PIV:
                    summ[f"{pv_} がゼロのK(万kW)"] = zero[pv_]
                rows_cs.append(summ)
                print(f"  泊{tl} {VLAB.get(vv, vv)} ×{m} {mode}: π_PF(0)={df['π_PF'].iloc[0]:,.0f} "
                      f"π_c実績整合(0)={df['π_c_実績整合'].iloc[0]:,.0f} ゼロ K={zero['π_c_実績整合']:.1f}"
                      f"（旧 {zero['π_旧(0.81PF)']:.1f}）")
res_c = pd.DataFrame(rows_c)
res_cs = pd.DataFrame(rows_cs)
# 補正前との差（同じ泊・同じ倍率の補正前（btable、同じ倍率）の行に対する。風力1倍は補正の影響がないので差0）
_base = res_cs[res_cs["補正"].isin(["btable", "全補正共通"]) & (res_cs["風力の加え方"] == "同じ倍率")]
_base = _base.set_index(["泊", "K_wind倍率"])
for pv_ in ["π_PF K0", "π_c_実績整合 K0", "π_c_実績整合 K25", "π_c_実績整合 K50", "π_c_実績整合 K100",
            "π_旧(0.81PF) K0", "π_c_実績整合 がゼロのK(万kW)"]:
    refv = np.array([_base.loc[(t_, m_), pv_] for t_, m_ in zip(res_cs["泊"], res_cs["K_wind倍率"])])
    res_cs[f"Δ{pv_}（補正前比）"] = res_cs[pv_].to_numpy() - refv
    if pv_.startswith("π_PF") or pv_.endswith("K0"):
        res_cs[f"Δ{pv_}（補正前比,%）"] = (res_cs[pv_].to_numpy() / refv - 1) * 100
# K≤100万kW の全格子点（1万kW ごと）での補正前との差の最大絶対値
_bc = res_c[res_c["補正"].isin(["btable", "全補正共通"]) & (res_c["風力の加え方"] == "同じ倍率")]
_bc = _bc.set_index(["泊", "K_wind倍率", "K(万kW)"])
for pv_ in ["π_c_実績整合", "π_旧(0.81PF)", "π_PF"]:
    mx = []
    for _, r in res_cs.iterrows():
        cur = res_c[(res_c["補正"] == r["補正"]) & (res_c["泊"] == r["泊"]) & (res_c["風力の加え方"] == r["風力の加え方"])
                    & np.isclose(res_c["K_wind倍率"], r["K_wind倍率"]) & (res_c["K(万kW)"] <= 100)]
        refv = _bc.loc[[(r["泊"], r["K_wind倍率"], k) for k in cur["K(万kW)"]], pv_].to_numpy()
        mx.append(np.abs(cur[pv_].to_numpy() - refv).max())
    res_cs[f"max|Δ{pv_}| K≤100（補正前比）"] = mx
# 41（T1、pi_k_curve_v3.csv）との照合（同じ定義・刻み1万kW。補正前のシナリオは一致するはず。他トラックの出力なので表示のみ）
_t1p = os.path.join(PROC, "pi_k_curve_v3.csv")
if os.path.exists(_t1p):
    t1 = pd.read_csv(_t1p, encoding="utf-8-sig")
    t1 = t1[t1["価格モデル"].str.startswith("仕様A（26") & (t1["θ"] == 1.0) & t1["フリート配分"].str.startswith("完全予見")
            & t1["刻み(万kW)"].astype(str).isin(["1.0", "1"])]
    _d = []
    for (tl, m), g_ in _bc.reset_index().groupby(["泊", "K_wind倍率"]):
        t_ = t1[(t1["泊3号"] == tl) & np.isclose(t1["風力倍率"], m)].drop_duplicates("K(万kW)").set_index("K(万kW)")
        kk = [k for k in g_["K(万kW)"] if k in t_.index]
        if kk:
            _d.append(np.abs(g_.set_index("K(万kW)").loc[kk, "π_c_実績整合"].to_numpy()
                             - t_.loc[kk, "π_実績整合"].to_numpy()).max())
    print(f"41 の pi_k_curve_v3 との照合（補正前の {len(_d)} シナリオ、共通の K）: π_c 実績整合の差の最大 {max(_d):.4f}円")
for d_ in (res_c, res_cs):
    num = d_.select_dtypes("number").columns
    d_[num] = d_[num].round(3)
res_c.to_csv(os.path.join(PROC, "cf_correction_pik.csv"), index=False)
res_cs.to_csv(os.path.join(PROC, "cf_correction_pik_summary.csv"), index=False)
eq_chk = res_cs[(res_cs["風力の加え方"] == "同じ倍率") & (res_cs["補正"].isin(["btable", "全補正共通"]))]
for _, r in eq_chk.iterrows():          # K=0 は刻みによらないので 28 の π_PF と一致するはず
    if r["K_wind倍率"] in (0.5, 1.0, 1.5, 2.0, 3.0):
        o = eqs[(eqs["泊"] == r["泊"]) & np.isclose(eqs["K_wind倍率"], r["K_wind倍率"]) & (eqs["K(万kW)"] == 0)].iloc[0]
        assert abs(o["π_PF(円/kW-年)"] - r["π_PF K0"]) <= 0.51, (r["泊"], r["K_wind倍率"])
print("\n=== (c) π_c 実績整合（円/kW-年）。K=0・25・50・100 とゼロになる K（万kW） ===")
cols = ["泊", "補正名", "風力の加え方", "K_wind倍率", "K_wind(万kW)", "π_PF K0", "π_旧(0.81PF) K0", "π_c_モデル直値 K0",
        "π_c_実績整合 K0", "π_c_実績整合 K25", "π_c_実績整合 K50", "π_c_実績整合 K100", "π_c_実績整合 がゼロのK(万kW)",
        "π_旧(0.81PF) がゼロのK(万kW)", "Δπ_PF K0（補正前比）", "Δπ_c_実績整合 K0（補正前比）"]
print(res_cs[cols].round(1).to_string(index=False))

# ====================================================================
# 4(d). λ 実験（29）
# ====================================================================
metrics26 = ns26["metrics"]
e29 = est26.sort_values("ts").reset_index(drop=True).copy()
assert (e29.groupby("day").size() == 24).all()
ts_full = pd.date_range(e29["ts"].min(), e29["ts"].max(), freq="h")
x29 = e29.set_index("ts")["wind_pre"].reindex(ts_full).interpolate(limit_direction="both")
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬", 3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋",
              10: "春秋", 11: "春秋"}
LAMBDAS = [1.0, 1.5, 2.0, 3.0, 4.0]


def bands(x):
    ma6 = x.rolling(6, center=True, min_periods=3).mean()
    ma24 = x.rolling(24, center=True, min_periods=12).mean()
    ma168 = x.rolling(168, center=True, min_periods=84).mean()
    return {"<6h": x - ma6, "6-24h": ma6 - ma24, "1-7d": ma24 - ma168, ">7d": ma168 - x.mean()}


def shares(x):
    b = bands(x)
    v_ = x.var()
    return {k: float(s_.var() / v_ * 100) for k, s_ in b.items()}


INTRA0 = bands(x29)["<6h"] + bands(x29)["6-24h"]


def synth(lam, cap_mw):
    y = (x29 + (lam - 1.0) * INTRA0).clip(lower=0.0, upper=cap_mw)
    day = y.index.normalize()
    scale = x29.groupby(day).sum() / y.groupby(day).sum().replace(0, np.nan)
    return (y * scale.reindex(day).to_numpy()).clip(lower=0.0, upper=cap_mw)


def daily_reg(df, pcol, wcol):
    P = df.pivot(index="day", columns="hour", values=pcol)
    P = P[P.count(axis=1) == 24]
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["tb4"] = srt[:, -4:].mean(1) - srt[:, :4].mean(1)
    d["wind"] = df.groupby("day")[wcol].sum() / 1000
    d["solar"] = df.groupby("day")["solar_pre"].sum() / 1000
    d["demand"] = df.groupby("day")["demand"].sum() / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    d = d.dropna()
    X = pd.DataFrame(index=d.index)
    for s_ in ["夏", "冬", "春秋"]:
        m = (d["season"] == s_).astype(float)
        X[f"wind_{s_}"] = d["wind"] * m
        X[f"solar_{s_}"] = d["solar"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                   pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    res = sm.OLS(d["tb4"], sm.add_constant(X)).fit(cov_type="HC3")
    return {s_: float(res.params[f"wind_{s_}"]) for s_ in ["夏", "冬", "春秋"]}


sd_old = pd.read_csv(os.path.join(PROC, "spatial_dispersion.csv"))
rows_d = []
for v in VARS:
    cap_mw = attach(e29, v).set_index("ts")["wind_kw"].reindex(ts_full).ffill().bfill() / 1000
    for lam in LAMBDAS:
        raw_ = x29 + (lam - 1.0) * INTRA0
        y = synth(lam, cap_mw)
        sh = shares(y)
        df = e29.copy()
        df["wind_syn"] = y.reindex(df["ts"]).to_numpy()
        df["net_syn"] = df["demand"] - df["solar_pre"] - df["wind_syn"] - df["nuclear"].fillna(0)
        df["p_syn"] = predict_A26(df, net_col="net_syn", theta=1.0)
        mt = metrics26(df, "p_syn")
        fm = fast_metrics(df, "p_syn")
        reg = daily_reg(df, "p_syn", "wind_syn")
        r = {"補正": v, "補正名": VLAB[v], "λ": lam,
             "上限で打ち切る時間の割合(%)": float((raw_ > cap_mw).mean() * 100),
             "日内シェア(<24h,%)": sh["<6h"] + sh["6-24h"],
             "下限張り付き時間(h/年)": float(mt["床(≤0.01円)時間"].mean()),   # 右辺の列名は 26 の metrics のもの
             "TB4h中央値": float(fm["tb_med"].mean()),
             "p95": float(fm["p95"].mean()), "完全予見粗利(円/kW-年)": float(fm["pf"].mean()),
             **{f"β_wind→TB4h {s_}": b_ for s_, b_ in reg.items()}}
        rows_d.append(r)
        if v == "btable":
            o = sd_old[np.isclose(sd_old["λ"], lam)].iloc[0]
            assert abs(o["PF価値(円/kW-年)"] - r["完全予見粗利(円/kW-年)"]) <= 0.51, lam
            assert abs(o["β_wind→TB4h 春秋"] - r["β_wind→TB4h 春秋"]) <= 0.0005, lam
            assert abs(o["床時間(h/年)"] - r["下限張り付き時間(h/年)"]) <= 0.51, lam      # 29 の出力の列名
res_d = pd.DataFrame(rows_d)
num = res_d.select_dtypes("number").columns
res_d[num] = res_d[num].round(4)
res_d.to_csv(os.path.join(PROC, "cf_correction_lambda.csv"), index=False)
print("\n=== (d) λ 実験（29） ===")
print(res_d.drop(columns=["補正"]).to_string(index=False))

# ====================================================================
# 4(e). 表10.1 の泊＋風力2倍の行（32 の段差モデル、θ=1、K=0）
# ====================================================================
base_price26, G26, ADJ26 = ns26["base_price"], ns26["G"], ns26["ADJ"]
e32 = est26.sort_values("ts").reset_index(drop=True).copy()
CREQ_68 = (4 * 6.8 * (0.06 * 1.06 ** 20 / (1.06 ** 20 - 1)) + 0.53 + 0.69) * 1e4    # 32 の c_req(6.8, WACC 6%)


def price32(df, c=None):
    """32 の predict（θ=1）。下限価格に張り付く時間だけ −c 円"""
    base = base_price26(df, G26, ADJ26, "net")
    p = np.maximum(base, FLOOR)
    return p if c is None else np.where(base <= FLOOR + 1e-9, -c, p)


rows_e = []
for v in VARS:
    e = attach(e32, v)
    e["net"] = e["net"] - (2.0 - 1.0) * K_NOW26[v] * 1e4 * e["cf_wind"] / 1000 - TOMARI
    for c, lab in ((None, "現行（下限0.01円）"), (0.0, "下限 0円"), (5.0, "下限 −5円"), (10.0, "下限 −10円")):
        e["p32"] = price32(e, c)
        fm = fast_metrics(e, "p32")
        pf = float(fm["pf"].mean())
        rows_e.append({"補正": v, "補正名": VLAB[v], "下限": lab,
                       "下限張り付き・負価格の時間(h/年)": float(fm["floor"].mean()) if c is None
                       else float((e["p32"] <= FLOOR + 1e-9).sum() / 3),
                       "π_PF(0)": pf, "π(0)_旧(0.81PF)": CAPTURE * pf - CHARGE_COST,
                       "θ*（資本費6.8万・容量1.25万・WACC6%）": (CREQ_68 - 12_500 + CHARGE_COST) / (CAPTURE * pf)})
res_e = pd.DataFrame(rows_e)
# 同じ行を D1 の基準（戦略 c の実現粗利を直接計算、(c) と同じパス・校正係数 CAL）でも出す。K=0 のみ
_ce = {}
for v in VARS:
    net0 = NET_BASE - (2.0 - 1.0) * K_NOW26[v] * 1e4 * CFW26[v] / 1000 - TOMARI
    base2d = np.asarray(base_price26(tmp.assign(net=net0.reshape(-1)), G26, ADJ26, "net")).reshape(n, 24)
    for c, lab in ((None, "現行（下限0.01円）"), (0.0, "下限 0円"), (5.0, "下限 −5円"), (10.0, "下限 −10円")):
        P2 = np.maximum(base2d, FLOOR) if c is None else np.where(base2d <= FLOOR + 1e-9, -c, np.maximum(base2d, FLOOR))
        _ce[(v, lab)] = eval_cpf(P2)
res_e["c(0)"] = [_ce[(v, l)][0] for v, l in zip(res_e["補正"], res_e["下限"])]
_pf_chk = np.array([_ce[(v, l)][1] for v, l in zip(res_e["補正"], res_e["下限"])])
assert np.allclose(_pf_chk, res_e["π_PF(0)"].to_numpy(), atol=0.5)       # (c) のパスの FY2023〜25 と est が同じ日
res_e["π_c_モデル直値(0)"] = res_e["c(0)"] - CHARGE_COST
res_e["π_c_実績整合(0)"] = CAL * res_e["c(0)"] - CHARGE_COST
res_e["θ*_c実績整合（同じ前提）"] = (CREQ_68 - 12_500 + CHARGE_COST) / (CAL * res_e["c(0)"])
_b = res_e[res_e["補正"] == "btable"].set_index("下限")
res_e["Δπ(0)_旧（補正前比）"] = res_e["π(0)_旧(0.81PF)"].to_numpy() - _b.loc[res_e["下限"], "π(0)_旧(0.81PF)"].to_numpy()
res_e["Δπ(0)_旧（補正前比,%）"] = res_e["Δπ(0)_旧（補正前比）"] / _b.loc[res_e["下限"], "π(0)_旧(0.81PF)"].to_numpy() * 100
res_e["Δπ_c_実績整合(0)（補正前比）"] = (res_e["π_c_実績整合(0)"].to_numpy()
                                     - _b.loc[res_e["下限"], "π_c_実績整合(0)"].to_numpy())
res_e["Δπ_c_実績整合(0)（補正前比,%）"] = (res_e["Δπ_c_実績整合(0)（補正前比）"]
                                       / _b.loc[res_e["下限"], "π_c_実績整合(0)"].to_numpy() * 100)
neg_old = pd.read_csv(os.path.join(PROC, "negative_price_scenarios.csv"))
for _, r in res_e[res_e["補正"] == "btable"].iterrows():      # 32 の K=0 の行を再現
    o = neg_old[(neg_old["水準"] == "θ=1・泊＋風力2倍") & (neg_old["下限"] == r["下限"]) & (neg_old["K(万kW)"] == 0)].iloc[0]
    assert abs(o["π_実現可能(円/kW-年)"] - r["π(0)_旧(0.81PF)"]) <= 0.51, r["下限"]
num = res_e.select_dtypes("number").columns
res_e[num] = res_e[num].round(3)
res_e.to_csv(os.path.join(PROC, "cf_correction_negprice.csv"), index=False)
print("\n=== (e) 表10.1 泊＋風力2倍（θ=1、K=0、0.81×π_PF−1,752） ===")
print(res_e.drop(columns=["補正"]).round(2).to_string(index=False))

# ====================================================================
# 5. 図
# ====================================================================
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、2つのパネルを縦に並べ、文字は8.5pt 以上にする。凡例は各パネルの下に置く
fig = plt.figure(figsize=(6.1, 7.0), layout="constrained")
sf1, sf2 = fig.subfigures(2, 1, height_ratios=[1.0, 1.0], hspace=0.03)
ax1, ax2 = sf1.subplots(), sf2.subplots()
mm = mon.loc["2021-04":"2026-06"].copy()
xd = pd.to_datetime(mm.index + "-15")
ax1.fill_between(xd, mm["ref_min"], mm["ref_max"], color="#DDDDDD", lw=0, label="同じ月の他の年の範囲（2023/3〜2024/3 を除く）")
ax1.plot(xd, mm["ref_median"], color="#9A9A9A", lw=1.2, label="同じ月の他の年の中央値")
ax1.plot(xd, mm["cf_btable"], color=C_ORIG, lw=1.5, label="補正前（表Bの容量）")
ax1.plot(xd, mm["cf_step"], color=C_MAIN, lw=1.5, label="主（前倒し）")
ax1.plot(xd, mm["cf_eff"], color=C_MAIN, lw=1.1, ls="--", label="代替1（実効容量）")
ax1.set_ylabel("月平均の設備利用率", color=GRAY, fontsize=9)
ax1.set_title("(a) 風力の月平均 cf", fontsize=9.5, color=INK, loc="left")
sf1.legend(*ax1.get_legend_handles_labels(), fontsize=8.5, frameon=False, loc="outside lower center", ncol=2, columnspacing=1.2)
ax1.set_ylim(0.0, 0.62)
mb = mon.loc["2022-04":"2024-12"]
xb = pd.to_datetime(mb.index + "-15")
ax2.plot(xb, mb["cap_btable_kw"] / 1e4, color=C_ORIG, lw=1.5, label="表B（四半期末値の月次補間）")
ax2.plot(xb, mb["cap_step_kw"] / 1e4, color=C_MAIN, lw=1.5, label="主（前倒し）")
ax2.plot(xb, mb["cap_eff_kw"] / 1e4, color=C_MAIN, lw=1.1, ls="--", label="代替1（実効容量）")
ax2.plot(xb, mb["cap_peak_kw"] / 1e4, color=C_MAIN, lw=1.1, ls=":", label=f"代替2（最大出力÷{PEAK_Q:.2f}）")
ax2.scatter(xb, mb["peak_mw"] / 10, s=12, color=INK, zorder=3, label="月内の最大時間出力（制御前）")
ax2.set_ylabel("万kW", color=GRAY, fontsize=9)
ax2.set_title("(b) 風力の容量と月内の最大出力", fontsize=9.5, color=INK, loc="left")
sf2.legend(*ax2.get_legend_handles_labels(), fontsize=8.5, frameon=False, loc="outside lower center", ncol=2, columnspacing=1.2)
ax1.xaxis.set_major_locator(mdates.YearLocator(month=1))
ax2.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
for ax in (ax1, ax2):
    ax.grid(axis="y", color="#E5E5E5", lw=0.6)
    for sp_ in ("top", "right"):
        ax.spines[sp_].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=8.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m"))
    ax.axvspan(pd.Timestamp("2023-03-01"), pd.Timestamp("2024-03-31"), color="#F3E2D6", alpha=0.45, lw=0)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "cf_correction.png"), dpi=300)
print("\nsaved: hokkaido_cf_series_corrected.csv, cf_correction_{monthly,fy,btable_quarters,kwind_specB,decomp,pik,"
      "pik_summary,lambda,negprice}.csv, figures/hokkaido/cf_correction.png")
