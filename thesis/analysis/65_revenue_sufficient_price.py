#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""【試作 2026-10-25】火力の収入の十分性から価格カーブを逆算し、その上で蓄電池の均衡を求める（著者の提案）

著者の方法（2026-10-25）:
  - 発電事業者に必要な収益は、過去に実際に得ていた火力の粗利（売電収入−燃料費）とみなす（維持費・利益・リスクの上乗せを含む）。
    市場参加者は限界費用入札の原則に従う理想的な主体とし、容量価格は現状の水準で一定、不足はスポットで回収されると置く。
    基準は FY2024〜25 の2年の平均（OCCTO のユニット別の発電実績）。FY2016 まで遡った近似は頑健性の確認に使う（著者確認 2026-10-25）。
  - 太陽光・風力・原子力が増えると、火力が稼げる時間が減る。必要な粗利は変わらないので、残った時間（主に夕方）の単価が上がり、
    昼は下がる。日内の値幅が広がって蓄電池が入り、昼に買い夕方に売ることで値幅を縮める。その均衡を求める。
  - 北海道の需要を満たすための最低限の火力の kW は維持する。構造モデル（Kanamura & Ohashi 2007 と同じく、需給の構造から価格を作る）を
    使う。東北は加えない（著者の方針）。
価格の式（構造型）:
  p_h ＝ v_m ＋ min(m_h, 0) ＋ α・max(m_h, 0)、m_h ＝ γ_{s,h} ＋ c1・τ_h（余剰の時間は0.01円。下限0.01円）
    v_m: 燃料費の指標（石炭と LNG の送電端の燃料費の平均、60。月別。価格の水準は燃料費と共和分で、傾き約1）
    τ_h: 北海道の需給の逼迫度＝残余需要（需要−太陽光−風力−原子力−水力−地熱−バイオマス）÷火力の運転できる容量（補修率を引いた
         最大出力＋ユニット別の公開の対象外の火力の平均343MW）
    γ_{s,h}: 季節×時刻の固定の形。北海道の価格は分断がなければ東北と同じなので、本州側の需給の形（夕方の山・夜の谷）が入る。
         北海道だけの τ では日内の値幅の約4割しか説明できない（夕方と夜の τ がほぼ同じ）。東北はモデルに加えず、その形を過去の
         平均として固定する。本州側でも太陽光が増えて昼の谷・夕方の山が深くなるので、固定は値幅を小さめに見る（保守的）
    c1・γ: FY2024〜25 の実績で、p−v を τ と季節×時刻のダミーに回帰した係数（α＝1 が過去の形）
    α: 将来の年に、火力の粗利が必要な粗利（現状のモデルの1kW あたりの粗利 × その年の必要な火力の容量）に等しくなる値
  α は上乗せが正の時間（夕方・冬の逼迫した時間）だけに掛ける。著者の見立て「太陽光が増えるほど火力が稼げる時間が減り、残った時間の
  単価が上がる」に対応する。昼・夜の安い時間の下落は需給の構造（τ の低下）が決め、α では増幅しない（負の側まで α 倍すると、限界費用
  入札の原則に反して運転中の火力の燃料費を大きく下回る価格が多数の時間に出る。試算で確認）。α＝1 で過去の形に戻る。
将来の年: 構造モデル（55・58・61 の build61）の時間別の需給。需要は気象年 FY2023〜25 の時間の形を OCCTO 需要想定に合わせて伸縮し、
  DC・半導体を一定の負荷で加え、屋根置きの自家消費を差し引く。太陽光・風力は設備×気象年の出力の比率。泊は公表の時期で、定検は
  春（4〜6月）に最大の1基。火力は供給計画のユニット（58 の fleet）のうち、必要な容量だけを残す: 現状（FY2024〜25）と同じ供給力の
  余裕（年の上位3日の残余需要のピークでの、火力の運転できる容量−残余需要）を保てる最小の組み合わせ。マストランの3機と長期脱炭素電源
  オークション（LTDA）の石狩湾新港2・3号は残し、残りは燃料費の安い順に残す。最大の単機の脱落が泊3号（87.2万kW）になる年は、
  余裕を苫東厚真4号（70万kW）との差だけ上乗せする。LTDA の2基は固定費をそこで回収するので、必要な粗利の対象から外す。
  余剰（再エネの抑制・下げ代不足）は 55 の判定（北本の送電の上限57万kW を吸収に使う）。北本の受電は明示しない（過去の価格の関係に
  平均として入っている）。
蓄電池: 59・61 と同じ増分の貪欲法（1万kW 刻み、各日の最安4時間に充電・最高4時間に放電）。刻みごとに α を解き直す（蓄電池が夕方の
  火力の出力を減らすと、必要な粗利を残りの時間で回収するので α が上がる）。π は λ65（実績の戦略c ÷ 現状のモデルの戦略c）で較正。
主の経路（2026-10-25 夕）: 2040年 OCCTO 9,000億kWh（著者の決定）、泊は公式の時期、北本の増強分（東北向の運用容量 70→100万kW の差 300MW）を
  FY2028 から北海道が余っている時間の需要に加える（著者の方針: 北本は最低限の扱い）。LTDA の北海道の蓄電池67.4万kW を先に入れる。
均衡: 62 のコホートの自由参入（Lucas & Prescott 1971 の等価な凹計画）。容量収入は κ×P（κ＝0.861、P は2029年度向けの北海道14,972円で一定）。
出力: data/processed/revsuff_fit.csv、revsuff_years.csv、revsuff_price_profile.csv、revsuff_pik.npz、revsuff_entry.csv
"""
import glob
import os
import sys
import time

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")
CACHE = os.path.join(os.environ.get("SCR", "/private/tmp/claude-501/-Users-matsuba-work-thesis/d0c864fb-2c7b-407c-809f-7a4dc1efcfaf/scratchpad"),
                     "refocus", "unit_hourly.pkl")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

FV = pd.read_csv(os.path.join(PROC, "fuel_vc_monthly.csv"), parse_dates=["month"]).set_index("month")
FV["idx"] = (FV["vc_coal"] + FV["vc_lng"]) / 2
AVAIL = {"coal": [96.1, 96.0, 88.3, 74.4, 72.4, 79.9, 93.0, 96.3, 91.6, 83.3, 84.8, 91.0],
         "lng": [97.7, 98.6, 94.3, 85.5, 82.3, 87.5, 95.2, 98.0, 94.0, 86.1, 88.3, 94.0],
         "oil": [96.5, 96.7, 91.2, 84.6, 81.9, 81.1, 92.0, 92.4, 87.7, 79.5, 85.0, 92.6]}
NONADJ = 343.0          # ユニット別の公開の対象外の火力（非調整火力・自家発等）の平均（FY2024〜25、エリアの火力−ユニット計）
SEASON = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 0])   # 月→季節（0 冬12〜2月、1 春3〜5月、2 夏6〜9月、3 秋10〜11月）。添字は月（0 は未使用）
SEASON_NAME = ["冬", "春", "夏", "秋"]
KAP, P_CAP = 0.861, 14_972.0

# ---------------------------------------------------------------- (1) 過去（FY2024〜25）: ユニット別の実績で粗利と価格の形を推定
UNITS_HIST = {  # OCCTO の名前: (燃料, 燃料費の比（OCCTO の想定の燃種別）, 容量 MW、発電端の概数)
    "苫東厚真発電所 ４号機": ("coal", 1.0, 700), "苫東厚真発電所 ２号機": ("coal", 11.2 / 10.4, 600), "苫東厚真発電所 １号機": ("coal", 11.5 / 10.4, 350),
    "砂川発電所 ３号機": ("coal", 11.5 / 10.4, 125), "砂川発電所 ４号機": ("coal", 11.5 / 10.4, 125), "石狩湾新港発電所 １号機": ("lng", 1.0, 569),
    "知内発電所 ２号機": ("oil", 1.0, 350), "知内発電所 １号機": ("oil", 1.0, 350), "苫小牧発電所 単独": ("oil", 1.0, 250),
    "苫小牧共同火力発電所3G 単独": ("oil", 1.0, 250)}


def unit_hourly():
    """OCCTO のユニット別の発電実績（30分値、data/raw/occto_unit）を、北海道の火力について時間別（MW）に直す"""
    if os.path.exists(CACHE):
        return pd.read_pickle(CACHE)
    d = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in sorted(glob.glob(os.path.join(RAW, "occto_unit", "*.csv")))], ignore_index=True)
    h = d[(d["エリア"] == "北海道") & d["発電方式・燃種"].str.startswith("火力")].copy()
    slots = [c for c in h.columns if c.endswith("[kWh]") and ":" in c]
    h["unit"] = h["発電所名"].str.replace("北海道ﾊﾟﾜｰｴﾝｼﾞﾆｱﾘﾝｸﾞ株式会社　", "", regex=False) + " " + h["ユニット名"]
    lg = h.melt(id_vars=["unit", "対象日"], value_vars=slots, var_name="slot", value_name="kWh")
    hm = lg["slot"].str.slice(0, 5)
    lg["hour"] = (pd.to_datetime(lg["対象日"]) + pd.to_timedelta(hm.str.slice(0, 2).astype(int), unit="h")
                  + pd.to_timedelta(hm.str.slice(3, 5).astype(int), unit="m") - pd.Timedelta(minutes=30)).dt.floor("h")
    g = lg.groupby(["unit", "hour"])["kWh"].sum().unstack(0) / 1000
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    g.to_pickle(CACHE)
    return g


def load_hist():
    g = unit_hourly()
    P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"]).set_index("ts")
    idx = g.index.intersection(P.index)
    idx = idx[(idx >= "2024-04-01") & (idx < "2026-04-01")]
    m = idx.to_period("M").to_timestamp()
    mon = idx.month.to_numpy()
    VC = np.column_stack([FV[f"vc_{f}"].reindex(m).to_numpy() * r for f, r, c in UNITS_HIST.values()])
    G = np.column_stack([g.loc[idx, u].fillna(0).clip(lower=0).to_numpy() for u in UNITS_HIST])
    CAPA = np.column_stack([c * np.array(AVAIL[f])[mon - 1] / 100 for f, r, c in UNITS_HIST.values()])
    Q = P.loc[idx]
    net = (Q["demand"] - Q["solar"].fillna(0) - Q["wind"].fillna(0) - Q["nuclear"].fillna(0) - Q["hydro"].fillna(0)
           - Q["geothermal"].fillna(0) - Q["biomass"].fillna(0)).to_numpy()
    return dict(idx=idx, VC=VC, G=G, CAPA=CAPA, p=Q["p_hokkaido"].to_numpy(), v=FV["idx"].reindex(m).to_numpy(),
                net=net, tau=net / (CAPA.sum(1) + NONADJ), fy=(idx.year - (idx.month < 4)).to_numpy(),
                hs=SEASON[mon] * 24 + idx.hour.to_numpy())


H = load_hist()
GM_HIST = {y: float(((H["p"] - H["VC"].T).T * H["G"])[H["fy"] == y].sum() * 1_000) for y in (2024, 2025)}   # 円/年
ACTIVE_CAP = sum(c for u, (f, r, c) in UNITS_HIST.items())                                                    # 稼働中の容量（休止の奈井江・伊達を除く）
GM_PER_KW = np.mean(list(GM_HIST.values())) / (ACTIVE_CAP * 1_000)                                            # 円/kW-年
notfloor = H["p"] > 0.011
_D = np.eye(96)[H["hs"]]
REG = sm.OLS((H["p"] - H["v"])[notfloor], np.column_stack([H["tau"], _D])[notfloor]).fit(cov_type="HAC", cov_kwds={"maxlags": 24})
C1, GAMMA = REG.params[0], REG.params[1:]
REG_LIN = sm.OLS((H["p"] - H["v"])[notfloor], sm.add_constant(H["tau"][notfloor])).fit(cov_type="HAC", cov_kwds={"maxlags": 24})


def price_hist(alpha=1.0):
    m = GAMMA[H["hs"]] + C1 * H["tau"]
    return np.where(~notfloor, 0.01, np.maximum(H["v"] + np.minimum(m, 0.0) + alpha * np.maximum(m, 0.0), 0.01))


# ---------------------------------------------------------------- (1b) 頑健性: FY2016 まで遡った火力の粗利の近似（著者確認 2026-10-25）
# ユニット別の実績は FY2024〜 しかないので、エリアの火力の出力（−対象外の343MW）を、その年度の火力の構成に燃料費の順（マストランの最低出力を先に）
# で配って粗利を近似する。構成は notes/37: 奈井江1・2は2019/3末に休止、石狩湾新港1は2019/2/27に運転開始、伊達1は2023/11末・2は2024/3末に休止。
# この近似は FY2024〜25 で実績を約3割上回る（経済的な配分を仮定するため）ので、FY2024〜25 の同じ近似との比で使う。
# FY2016〜23 は容量市場がなく、固定費をすべて卸で回収していたので、FY2024〜25 に火力が受け取った容量価格の平均（北海道 14,137・5,242円/kW）を
# 差し引いた値も示す（主の比較）。FY2018 は胆振東部地震の停電で価格が欠けるので除く。
_R = 11.5 / 10.4
FLEET_HIST = {  # 名前: (燃料, 燃料費の比, MW, 運転の開始, 終了（休止）, マストランの最低出力)
    "苫東厚真4": ("coal", 1.0, 700, "2000-01-01", "2099-01-01", 103), "苫東厚真2": ("coal", 11.2 / 10.4, 600, "2000-01-01", "2099-01-01", 0),
    "苫東厚真1": ("coal", _R, 350, "2000-01-01", "2099-01-01", 0), "砂川3": ("coal", _R, 125, "2000-01-01", "2099-01-01", 0),
    "砂川4": ("coal", _R, 125, "2000-01-01", "2099-01-01", 0), "奈井江1": ("coal", _R, 175, "2000-01-01", "2019-04-01", 0),
    "奈井江2": ("coal", _R, 175, "2000-01-01", "2019-04-01", 0), "石狩湾新港1": ("lng", 1.0, 569, "2019-02-27", "2099-01-01", 212),
    "知内2": ("oil", 1.0, 350, "2000-01-01", "2099-01-01", 46), "知内1": ("oil", 1.0, 350, "2000-01-01", "2099-01-01", 0),
    "伊達1": ("oil", 1.0, 350, "2000-01-01", "2023-12-01", 0), "伊達2": ("oil", 1.0, 350, "2000-01-01", "2024-04-01", 0),
    "苫小牧1": ("oil", 1.0, 250, "2000-01-01", "2099-01-01", 0), "苫小牧共同3": ("oil", 1.0, 250, "2000-01-01", "2099-01-01", 0)}
CAP_PRICE_BASE = (14_137.0 + 5_242.0) / 2


def backcast_gm():
    P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"]).set_index("ts")
    P = P[P.index < "2026-04-01"]
    idx = P.index
    m, mon = idx.to_period("M").to_timestamp(), idx.month.to_numpy()
    U = list(FLEET_HIST.values())
    VC = np.column_stack([FV[f"vc_{f}"].reindex(m).to_numpy() * r for f, r, c, s, e, mn in U])
    alive = np.column_stack([(idx >= s) & (idx < e) for f, r, c, s, e, mn in U])
    CA = np.column_stack([c * np.array(AVAIL[f])[mon - 1] / 100 for f, r, c, s, e, mn in U]) * alive
    g = np.minimum(np.array([u[5] for u in U])[None, :] * alive, CA)
    rem = np.maximum((P["thermal"] - NONADJ).clip(lower=0).to_numpy() - g.sum(1), 0.0)
    order = np.argsort(np.where(alive, VC, np.inf), 1)
    for k in range(len(U)):
        ix = order[:, k:k + 1]
        cur = np.take_along_axis(g, ix, 1)[:, 0]
        add = np.minimum(np.take_along_axis(CA, ix, 1)[:, 0] - cur, rem)
        np.put_along_axis(g, ix, (cur + add)[:, None], 1)
        rem -= add
    gm = np.where(alive, (P["p_hokkaido"].to_numpy()[:, None] - VC) * g, 0.0).sum(1)
    cap = (np.array([u[2] for u in U])[None, :] * alive).sum(1)
    fy = idx.year - (idx.month < 4)
    out = pd.DataFrame({"gm": gm, "cap": cap, "fy": fy, "p": P["p_hokkaido"].to_numpy()}).groupby("fy").agg(
        gm=("gm", "sum"), cap=("cap", "mean"), p=("p", "mean"), nan=("gm", lambda s: s.isna().sum()))
    out["粗利の近似(億円)"] = out["gm"] * 1_000 / 1e8
    out["粗利の近似(円/kW-年)"] = out["gm"] * 1_000 / (out["cap"] * 1_000)
    out["容量収入を差し引いた値(円/kW-年)"] = np.where(out.index < 2024, out["粗利の近似(円/kW-年)"] - CAP_PRICE_BASE, out["粗利の近似(円/kW-年)"])
    out.loc[out["nan"] > 0, ["粗利の近似(億円)", "粗利の近似(円/kW-年)", "容量収入を差し引いた値(円/kW-年)"]] = np.nan
    base = out.loc[[2024, 2025], "粗利の近似(円/kW-年)"].mean()
    ratio = {"FY2016〜25 の平均・容量収入を差し引く（主の比較）": out["容量収入を差し引いた値(円/kW-年)"].mean() / base,
             "FY2016〜25 の平均・差し引かない（上限）": out["粗利の近似(円/kW-年)"].mean() / base}
    return out.rename(columns={"cap": "火力の容量(MW)", "p": "価格の平均(円/kWh)"}).drop(columns=["gm", "nan"]), ratio


# ---------------------------------------------------------------- (2) 将来: 構造モデルの残余需要と火力の構成
ns61 = {"__file__": os.path.join(HERE, "61_signal_market.py"), "__name__": "m61"}
exec(open(os.path.join(HERE, "61_signal_market.py"), encoding="utf-8").read().split("# ---------------------------------------------------------------- 計算")[0], ns61)
m59 = ns61["m59"]
build61, sc_year = ns61["build61"], ns61["sc_year"]
SH, RB, ETA, DATES_B, MONTH = m59["SH"], m59["RB"], m59["ETA"], m59["DATES_B"], m59["MONTH"]
FYB = np.asarray(m59["FYB"])
K_EVAL = np.array(list(range(0, 101)) + list(range(105, 401, 5)), float)     # 59・61 の格子（〜200万kW）を400万kW まで延ばす（上限に張り付くため）
GROSS = {"石狩湾新港1": 569, "苫東厚真4": 700, "知内2": 350, "苫東厚真2": 600, "苫東厚真1": 350, "砂川3": 125, "砂川4": 125, "知内1": 350,
         "苫小牧1": 250, "苫小牧共同3": 250, "音別GT": 148, "石狩湾新港2": 600, "石狩湾新港3": 600}      # 発電端の概数（OCCTO のユニット別と同じ基準）
LTDA_UNITS = {"石狩湾新港2", "石狩湾新港3"}
MR_MIN = {"石狩湾新港1": 212, "苫東厚真4": 103, "知内2": 46}  # マストランの最低出力（58）
V_IDX = np.repeat(FV["idx"].reindex(pd.DatetimeIndex(DATES_B).to_period("M").to_timestamp()).ffill().bfill().to_numpy()[:, None], 24, 1)
HS_B = SEASON[MONTH] * 24 + np.arange(24)[None, :]          # MONTH は日×24
EV_DAYS = np.isin(FYB, [2023, 2024, 2025])
BASE_DAYS = np.isin(FYB, [2024, 2025])
CONTINGENCY = 700.0     # 現状の最大の単機（苫東厚真4号）


def finish(A):
    A["capsum"] = A["av"].sum(2) + NONADJ
    A["target_units"] = np.array([n not in LTDA_UNITS for n in A["names"]])
    A["target_cap"] = sum(GROSS[n] for n in A["names"] if n not in LTDA_UNITS)
    return A


def scenario_arrays(sc, nuc_mode="春に1基定検"):
    """構造モデル（build61）から日×24 の配列を作る。sc=None は現状（FY2022〜25 の実績の需給）"""
    if sc is not None:
        # 61 の年シナリオはバイオマス・地熱を2035年の値（55 の BASE35）で一定にしている。65 では FY2024〜25 の実績から2035年へ直線で補間する
        w = min(max((sc["year"] - 2025) / 10.0, 0.0), 1.0)
        sc = {**sc, "nuc_mode": nuc_mode, "bio_min": 234.0 + w * (410.0 - 234.0), "geo": 11.0 + w * (50.0 - 11.0)}
    S = build61(sc)
    I = S["I"]
    units = [u for u in S["units"] if u[0] != "非調整火力"]
    av = np.stack([np.array(m59["AVAIL"][m59["FUELTYPE"](u)])[MONTH - 1] / 100.0 * GROSS[u[0]] for u in units], 2)
    vc = np.stack([m59["vc_matrix"](u, DATES_B) for u in units], 2)
    net = I["D"] - I["U"] - I["V"] - I["N"] - I["Hy"] - I["G"] - I["Bm"]
    return finish(dict(names=[u[0] for u in units], fuel=[m59["FUELTYPE"](u) for u in units], av=av, vc=vc, net=net, pump=I["P"] - I["Pgen"],
                       I={k: I[k] for k in ("D", "S", "W", "N", "Hy", "G", "Bm", "P", "Pgen", "curt", "X")},
                       surplus0=I["curt"] + I["deficit"], nuc=0.0 if sc is None else sc["nuclear_mw"],
                       year=None if sc is None else sc["year"]))


def margin(A, days):
    """供給力の余裕: 各年度の上位3日の残余需要のピークでの（火力の運転できる容量−残余需要）の平均（MW）"""
    out = []
    for fy in np.unique(FYB[days]):
        r = np.where(days & (FYB == fy))[0]
        top = r[np.argsort(A["net"][r].max(1))[-3:]]
        hh = A["net"][top].argmax(1)
        out.append((A["capsum"][top, hh] - A["net"][top, hh]).mean())
    return float(np.mean(out))


def keep_minimum(A, need):
    """余裕 need を保てる最小の火力の組み合わせ。マストランと LTDA は残し、残りは燃料費の安い順に足す。戻り値: (配列, 足りない MW)"""
    fixed = [i for i, n in enumerate(A["names"]) if n in MR_MIN or n in LTDA_UNITS]
    rest = sorted([i for i in range(len(A["names"])) if i not in fixed], key=lambda i: A["vc"][EV_DAYS, :, i].mean())
    keep = list(fixed)
    for i in [None] + rest:
        if i is not None:
            keep.append(i)
        B = finish(dict(A, names=[A["names"][j] for j in keep], fuel=[A["fuel"][j] for j in keep], av=A["av"][:, :, keep], vc=A["vc"][:, :, keep]))
        if margin(B, EV_DAYS) >= need:
            return B, 0.0
    return B, need - margin(B, EV_DAYS)


def dispatch(A, T):
    """火力の出力 T（日×24、MW、対象外の火力を除く）を、マストランの最低出力→燃料費の順に配る。戻り値: 日×24×ユニット"""
    mins = np.array([MR_MIN.get(n, 0.0) for n in A["names"]])
    g = np.minimum(np.broadcast_to(mins, A["av"].shape), A["av"]).copy()
    rem = np.maximum(T - g.sum(2), 0.0)
    order = np.argsort(A["vc"], 2)
    for k in range(len(A["names"])):
        ix = order[:, :, k][:, :, None]
        cur = np.take_along_axis(g, ix, 2)[:, :, 0]
        add = np.minimum(np.take_along_axis(A["av"], ix, 2)[:, :, 0] - cur, rem)
        np.put_along_axis(g, ix, (cur + add)[:, :, None], 2)
        rem = rem - add
    return g


TAU_X = float(np.quantile(H["tau"], 0.9))   # 北海道が余っている時間＝τ が過去（FY2024〜25）の上位1割に入らない時間
HOKUHON_ADD = 300.0                          # 北本の増強で増える送電の上限（東北向の運用容量 70→100万kW、FY2028〜。OCCTO 2026-06-09 資料1 p.20）


def export_add(A, tau0):
    """北本の送電のうち、過去の価格の関係に入っていない増強分。北海道が余っている時間の需要に加える（著者の方針: 北本は最低限の扱い）"""
    if not A.get("hokuhon", True) or A.get("year") is None or A["year"] < 2028:
        return 0.0
    return np.where(tau0 < TAU_X, HOKUHON_ADD, 0.0)


def state(A, chg, dis):
    """蓄電池の充放電を入れた後の、余剰の時間・逼迫度・火力の配分。北本の増強分は北海道の火力が出す（北海道の価格で売れる）"""
    sur = A["surplus0"] - chg > 1e-9
    net = A["net"] + np.maximum(chg - A["surplus0"], 0.0) - dis
    X = np.where(sur, 0.0, export_add(A, net / A["capsum"]))
    T = np.where(sur, 0.0, np.maximum(net + X + A["pump"] - NONADJ, 0.0))
    return sur, (net + X) / A["capsum"], dispatch(A, T)


# ---------------------------------------------------------------- (3) 価格と α
def price_alpha(sur, tau, alpha):
    m = GAMMA[HS_B] + C1 * tau
    return np.where(sur, 0.01, np.maximum(V_IDX + np.minimum(m, 0.0) + alpha * np.maximum(m, 0.0), 0.01))


def gm_parts(A, g, days):
    """粗利の計算に要る時間別の量（対象のユニット）: 出力の合計、燃料費の合計、年数"""
    gt = g[:, :, A["target_units"]]
    return gt.sum(2)[days], (gt * A["vc"][:, :, A["target_units"]]).sum(2)[days], days.sum() / 365.25


def gm_year(sur, tau, alpha, parts, days):
    gs, vcg, yrs = parts
    return (price_alpha(sur, tau, alpha)[days] * gs - vcg).sum() * 1_000 / yrs     # 円/年


ALPHA_MAX = 40.0


def solve_alpha(sur, tau, parts, target, days):
    """必要な粗利（円/年）に合う α（二分法。粗利は α について区分線形）"""
    f = lambda a: gm_year(sur, tau, a, parts, days) - target
    lo, hi = 0.0, ALPHA_MAX
    if f(hi) < 0:
        return hi                                  # 上乗せが正の時間が少なすぎて、スポットだけでは必要な粗利を回収できない
    if f(lo) >= 0:
        return 0.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return hi


def season_hour(pp, days):
    """季節×時刻の平均の価格（4×24）"""
    s = SEASON[MONTH[:, 0]][days]
    return np.stack([pp[days][s == k].mean(0) for k in range(4)])


A0 = scenario_arrays(None)
_z = np.zeros(SH)
_sur0, _tau0, _g0 = state(A0, _z, _z)
P0 = price_alpha(_sur0, _tau0, 1.0)
GM_MODEL_BASE = gm_year(_sur0, _tau0, 1.0, gm_parts(A0, _g0, BASE_DAYS), BASE_DAYS)
GM_PER_KW_MODEL = GM_MODEL_BASE / (A0["target_cap"] * 1_000)
MARGIN0 = margin(A0, BASE_DAYS)
C_ACT = m59["C_ACT"]
C_MODEL0 = m59["annual"](m59["daily_eval"](P0, m59["W_B"])["c"], m59["FYB"], m59["EVB"])
LAM65 = C_ACT / C_MODEL0
HR = np.arange(24)


def run_battery(A, Ks=K_EVAL, gm_per_kw=None, lam=None, keep_prof=(), fix_alpha=False):
    """fix_alpha=True: α を蓄電池がない時の値に固定する（蓄電池は火力の粗利の回収に便乗しない。カニバリゼーションの下限側）"""
    gm_per_kw = GM_PER_KW_MODEL if gm_per_kw is None else gm_per_kw
    lam = LAM65 if lam is None else lam
    target = gm_per_kw * A["target_cap"] * 1_000
    chg, dis = np.zeros(SH), np.zeros(SH)
    rows, done, prof, a0 = [], 0.0, {}, []

    def priced():
        sur, tau, g = state(A, chg, dis)
        if fix_alpha and a0:
            a = a0[0]
        else:
            a = solve_alpha(sur, tau, gm_parts(A, g, EV_DAYS), target, EV_DAYS)
            a0.append(a)
        return a, price_alpha(sur, tau, a), sur

    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            pp = priced()[1]
            oo = np.argsort(pp, 1)
            c4, d4 = oo[:, :4], oo[:, -4:]
            ok = np.take_along_axis(pp, d4, 1).sum(1) * ETA - np.take_along_axis(pp, c4, 1).sum(1) > 0
            chg[RB[ok], c4[ok]] += st * 10.0
            dis[RB[ok], d4[ok]] += st * 10.0 * ETA
            done += st
        a, pp, sur = priced()
        c = m59["annual"](m59["daily_eval"](pp, m59["W_B"])["c"], m59["FYB"], m59["EVB"])
        e = pp[EV_DAYS]
        rows.append({"K(万kW)": K, "α": a, "回収できない": a >= ALPHA_MAX, "c": c, "π": max(lam * c - P4.W_LOSS, 0.0), "価格の平均": e.mean(),
                     "昼10〜15時": e[:, (HR >= 10) & (HR < 15)].mean(), "夕17〜21時": e[:, (HR >= 17) & (HR < 21)].mean(),
                     "夜0〜6時": e[:, HR < 6].mean(), "0.01円の時間(h/年)": float((e <= 0.011).sum() / EV_DAYS.sum() * 365.25),
                     "余剰の時間(h/年)": float(sur[EV_DAYS].sum() / EV_DAYS.sum() * 365.25)})
        if K in keep_prof:
            prof[K] = season_hour(pp, EV_DAYS)
    return pd.DataFrame(rows), prof


def snapshot(A, K, gm_per_kw=None):
    """蓄電池 K 万kW を入れた後の価格・火力の配分・充放電（run_battery と同じ貪欲法、α は解き直す）"""
    target = (GM_PER_KW_MODEL if gm_per_kw is None else gm_per_kw) * A["target_cap"] * 1_000
    chg, dis = np.zeros(SH), np.zeros(SH)

    def priced():
        sur, tau, g = state(A, chg, dis)
        a = solve_alpha(sur, tau, gm_parts(A, g, EV_DAYS), target, EV_DAYS)
        return a, price_alpha(sur, tau, a), sur, g

    for _ in range(int(round(K))):
        pp = priced()[1]
        oo = np.argsort(pp, 1)
        c4, d4 = oo[:, :4], oo[:, -4:]
        ok = np.take_along_axis(pp, d4, 1).sum(1) * ETA - np.take_along_axis(pp, c4, 1).sum(1) > 0
        chg[RB[ok], c4[ok]] += 10.0
        dis[RB[ok], d4[ok]] += 10.0 * ETA
    a, pp, sur, g = priced()
    return dict(a=a, pp=pp, sur=sur, g=g, chg=chg, dis=dis)


def balance(A, snap, label):
    """年の需給（TWh/年）と価格の要約。気象年 FY2023〜25 の平均。北本の受電は明示しない（過去の価格の関係に入っている）"""
    I, pp, g, d = A["I"], snap["pp"], snap["g"], EV_DAYS
    yrs = d.sum() / 365.25
    e = lambda x: float(np.asarray(x)[d].sum() / yrs / 1e6) if np.ndim(x) else float(x) * 8_766 / 1e6
    fuel = np.array(A["fuel"])
    X = np.where(snap["sur"], 0.0, export_add(A, A["net"] / A["capsum"])) if A.get("year") else np.zeros(SH)
    th = {f: g[:, :, fuel == f].sum(2) for f in ("石炭", "LNG", "石油")}
    D = I["D"]
    return {"系列": label, "α": snap["a"], "需要(TWh)": e(D), "原子力": e(I["N"]), "太陽光（抑制前）": e(I["S"]), "風力（抑制前）": e(I["W"]),
            "抑制": e(I["curt"]), "水力": e(I["Hy"]), "地熱": e(I["G"]), "バイオマス": e(I["Bm"]),
            "火力 石炭": e(th["石炭"]), "火力 LNG": e(th["LNG"]), "火力 石油": e(th["石油"]), "対象外の火力": e(NONADJ),
            "うち LTDA の LNG": e(g[:, :, [n in LTDA_UNITS for n in A["names"]]].sum(2)),
            "揚水の動力−発電": e(I["P"] - I["Pgen"]), "北本の送電（余剰の時間・55）": e(np.where(snap["sur"], I["X"], 0.0)),
            "北本の送電（増強分）": e(X), "蓄電池の充電": e(snap["chg"]), "蓄電池の放電": e(snap["dis"]),
            "収支の差（供給−需要等）": e(I["N"] + I["S"] + I["W"] - I["curt"] + I["Hy"] + I["G"] + I["Bm"] + g.sum(2) + NONADJ + snap["dis"]
                                      - D - (I["P"] - I["Pgen"]) - np.where(snap["sur"], I["X"], 0.0) - X - snap["chg"]),
            "時間平均の価格": pp[d].mean(), "需要加重の平均価格": float((pp * D)[d].sum() / D[d].sum()),
            "昼10〜15時": pp[d][:, (HR >= 10) & (HR < 15)].mean(), "夕17〜21時": pp[d][:, (HR >= 17) & (HR < 21)].mean(),
            "夜0〜6時": pp[d][:, HR < 6].mean(), "0.01円の時間(h/年)": float((pp[d] <= 0.011).sum() / yrs),
            "約定総額(億円/年)": float((pp * D)[d].sum() / yrs * 1_000 / 1e8)}


def year_arrays(y, path, nuc_mode="春に1基定検", minimum=True):
    A = scenario_arrays(sc_year(y, path), nuc_mode)
    short = 0.0
    if minimum:
        need = MARGIN0 + max((872.0 if A["nuc"] >= 872.0 else 0.0) - CONTINGENCY, 0.0)
        A, short = keep_minimum(A, need)
    A["hokuhon"] = path.get("hokuhon", True)
    return A, short


PATHS65 = {  # 主は2040年 OCCTO 9,000億kWh（著者の決定 2026-10-25: 2035年までの需要想定と滑らかにつながる）
    "主（2040 は OCCTO 9,000億kWh、泊の公式の時期、北本の増強を反映）": dict(y2040="OCCTO 9,000億kWh", nuc="主"),
    "北本の増強を反映しない": dict(y2040="OCCTO 9,000億kWh", nuc="主", hokuhon=False),
    "2040 は OCCTO 11,000億kWh": dict(y2040="OCCTO 11,000億kWh", nuc="主"),
    "2040 の太陽光はエネ基の倍率×3.0（需要は11,000億kWh）": dict(y2040="エネ基の倍率×3.0（需要は11,000億kWh）", nuc="主"),
    "原子力なし": dict(y2040="OCCTO 9,000億kWh", nuc="原子力なし"),
}
LTDA_K0 = lambda t: (32.5 if 2029 <= t < 2049 else 0.0) + (20.9 if 2030 <= t < 2050 else 0.0) + (14.0 if 2031 <= t < 2051 else 0.0)
# LTDA の北海道の蓄電池（万kW）: 第1回32.5（2028年度末までに運開→2029年から）、第2回20.9（推定を含む）、第3回14.0（推定）。notes/33
YEARS = list(range(2026, 2041))
PROF_YEARS = (2026, 2030, 2035, 2040)
PROF_K = (0.0, 20.0, 50.0, 80.0, 100.0)


if __name__ == "__main__":
    t0 = time.time()
    QUICK = os.environ.get("QUICK") == "1"
    # ---- 当てはまり
    fit = []
    lin = np.where(~notfloor, 0.01, np.maximum(H["v"] + REG_LIN.params[0] + REG_LIN.params[1] * H["tau"], 0.01))
    for nm, pr in (("実績", H["p"]), ("北海道の τ だけ（線形）", lin), ("τ＋季節×時刻（主）", price_hist())):
        d = pd.DataFrame({"day": H["idx"].normalize(), "p": pr})
        spread = d.groupby("day")["p"].agg(lambda s: np.sort(s.values)[-4:].mean() - np.sort(s.values)[:4].mean()).mean()
        fit.append({"系列": nm, "R²（価格の水準、全時間）": 1 - ((H["p"] - pr) ** 2).sum() / ((H["p"] - H["p"].mean()) ** 2).sum(),
                    "MAE(円)": np.abs(H["p"] - pr).mean(), "日の上位4時間−下位4時間の平均(円)": spread,
                    **{f"{h}時": pr[H["idx"].hour == h].mean() for h in range(0, 24, 3)}})
    FIT = pd.DataFrame(fit)
    FIT.round(3).to_csv(os.path.join(PROC, "revsuff_fit.csv"), index=False, encoding="utf-8-sig")
    print(f"[1] 実績の火力の粗利（ユニット別、FY2024〜25）: {GM_HIST[2024] / 1e8:.0f}・{GM_HIST[2025] / 1e8:.0f}億円/年、稼働中 {ACTIVE_CAP}MW、{GM_PER_KW:,.0f}円/kW-年")
    print(f"    価格の形: c1＝{C1:.2f}（t {REG.tvalues[0]:.1f}、HAC）、季節×時刻96個。線形だけ: {REG_LIN.params[0]:.2f}＋{REG_LIN.params[1]:.2f}τ")
    print(FIT.round(2).to_string(index=False))
    hr = np.tile(HR, (SH[0], 1))
    act = m59["PACTM"][m59["BLK"]]
    mb = BASE_DAYS[:, None] & np.ones((1, 24), bool)
    print(f"[2] 現状のモデル（FY2024〜25、対象 {A0['target_cap']}MW）: 粗利 {GM_MODEL_BASE / 1e8:.0f}億円/年、{GM_PER_KW_MODEL:,.0f}円/kW-年。"
          f"余裕 {MARGIN0:,.0f}MW。戦略c 実績 {C_ACT:,.0f}／モデル {C_MODEL0:,.0f} → λ65＝{LAM65:.3f}")
    print("    時刻別（実績／モデル）:", " ".join(f"{h}:{act[mb & (hr == h)].mean():.1f}/{P0[mb & (hr == h)].mean():.1f}" for h in range(0, 24, 3)))
    if QUICK:
        for y in (2026, 2030, 2035, 2040):
            A, short = year_arrays(y, next(iter(PATHS65.values())))
            df, _ = run_battery(A, Ks=np.array([0.0, 20.0, 50.0]))
            print(y, A["target_cap"], "・".join(A["names"]), f"不足 {short:.0f}", df.round(2).to_dict("records"), f"{time.time() - t0:.0f}s", flush=True)
        sys.exit()

    # ---- 将来の年
    YR, PROF, SAVE = [], [], {}
    for pname, pth in PATHS65.items():
        for y in YEARS:
            A, short = year_arrays(y, pth)
            df, prof = run_battery(A, keep_prof=PROF_K if y in PROF_YEARS else ())
            SAVE[f"{pname}|{y}"] = df["π"].to_numpy(float)
            dff = run_battery(A, fix_alpha=True)[0]
            SAVE[f"{pname}|α固定|{y}"] = dff["π"].to_numpy(float)
            r0 = df.iloc[0]
            at = lambda K, c: float(df.loc[df["K(万kW)"] == K, c].iloc[0])
            YR.append({"経路": pname, "年": y, "火力（対象）MW": A["target_cap"], "残した火力": "・".join(A["names"]),
                       "足りない供給力(MW)": short, "残余需要の最大(MW)": float(A["net"][EV_DAYS].max()),
                       **{f"{k} K=0": r0[k] for k in ("α", "価格の平均", "昼10〜15時", "夕17〜21時", "夜0〜6時", "0.01円の時間(h/年)", "余剰の時間(h/年)", "π")},
                       "α K=50": at(50, "α"), "π K=20": at(20, "π"), "π K=50": at(50, "π"), "π K=100": at(100, "π"), "π K=200": at(200, "π"),
                       "昼10〜15時 K=50": at(50, "昼10〜15時"), "夕17〜21時 K=50": at(50, "夕17〜21時"),
                       "回収できない最小の K": float(df.loc[df["回収できない"], "K(万kW)"].min()) if df["回収できない"].any() else np.nan,
                       "α固定 π K=50": float(dff.loc[dff["K(万kW)"] == 50, "π"].iloc[0]), "α固定 π K=100": float(dff.loc[dff["K(万kW)"] == 100, "π"].iloc[0])})
            for K, pr in prof.items():
                for s in range(4):
                    PROF.append({"経路": pname, "年": y, "K(万kW)": K, "季節": SEASON_NAME[s], **{f"{h}時": pr[s, h] for h in range(24)}})
            print(f"  {pname[:12]} {y}: 火力 {A['target_cap']}MW 不足 {short:.0f} α0 {r0['α']:.2f} 昼 {r0['昼10〜15時']:.1f} 夕 {r0['夕17〜21時']:.1f} "
                  f"π0 {r0['π']:,.0f} π50 {YR[-1]['π K=50']:,.0f} ({time.time() - t0:.0f}s)", flush=True)
    YRD = pd.DataFrame(YR)
    YRD.round(3).to_csv(os.path.join(PROC, "revsuff_years.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(PROF).round(3).to_csv(os.path.join(PROC, "revsuff_price_profile.csv"), index=False, encoding="utf-8-sig")
    # ---- 頑健性: 必要な粗利の水準を FY2016 まで遡った近似で置き換える（主の経路）
    BC, RATIO = backcast_gm()
    BC.round(3).to_csv(os.path.join(PROC, "revsuff_gm_backcast.csv"), encoding="utf-8-sig")
    print("\n火力の粗利の遡及近似（FY2016〜25）"); print(BC.round(1).to_string()); print({k: round(v, 3) for k, v in RATIO.items()})
    ROB = []
    for i, (rk, rv) in enumerate(RATIO.items()):
        for y in YEARS:
            A, short = year_arrays(y, PATHS65[next(iter(PATHS65))])
            df = run_battery(A, gm_per_kw=GM_PER_KW_MODEL * rv)[0]
            SAVE[f"{next(iter(PATHS65))}|粗利{i}|{y}"] = df["π"].to_numpy(float)
            ROB.append({"必要な粗利": rk, "比": rv, "年": y, "α K=0": df["α"].iloc[0], "π K=0": df["π"].iloc[0],
                        "π K=50": float(df.loc[df["K(万kW)"] == 50, "π"].iloc[0])})
    pd.DataFrame(ROB).round(3).to_csv(os.path.join(PROC, "revsuff_robust.csv"), index=False, encoding="utf-8-sig")
    np.savez_compressed(os.path.join(PROC, "revsuff_pik.npz"), K=K_EVAL, **SAVE)

    # ---- コホートの自由参入（62 の線形計画）
    ns62 = {"__file__": os.path.join(HERE, "62_entry_path.py"), "__name__": "m62"}
    exec(open(os.path.join(HERE, "62_entry_path.py"), encoding="utf-8").read().split('if __name__ == "__main__":')[0], ns62)
    ns62["K"] = K_EVAL                                                      # 62 の線形計画の格子を 65 の格子に差し替える
    entry_lp, HORIZON, LAG = ns62["entry_lp"], ns62["HORIZON"], ns62["LAG"]

    def solve65(pname, P=P_CAP, cap="主", start=48_000.0, var="", ltda=True):
        """戻り値: (市場参入の最初の年, 合計 {年: 万kW}（LTDA を含む）)。LTDA は先に入れる（62 の K0）"""
        V = {t: SAVE[f"{pname}|{var}{min(t, YEARS[-1])}"] + KAP * P - P4.OM_BASE - P4.NET_FIX for t in range(YEARS[0], HORIZON + 1)}
        I_tau = {tau: 4 * P4.capex_path(tau, cap, start) * (1 + 0.05 / 1.06 ** 20) for tau in range(YEARS[0] - LAG, HORIZON + 1)}
        K0 = {t: LTDA_K0(t) for t in V} if ltda else None
        k, Kt = entry_lp(V, I_tau, K0)
        first = next((t for t in sorted(Kt) if Kt[t] - (K0 or {}).get(t, 0.0) > 0.5), None)
        return first, Kt

    def required65(pname, target=80.0, year=2040, **kw):
        """year 年の合計（LTDA を含む）が target 万kW に届く最小の容量価格 P（円/kW）。P＝0 ですでに届けば 0"""
        lo, hi = 0.0, 60_000.0
        if solve65(pname, P=lo, **kw)[1][year] >= target:
            return 0.0
        if solve65(pname, P=hi, **kw)[1][year] < target:
            return np.nan
        for _ in range(22):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if solve65(pname, P=mid, **kw)[1][year] >= target else (mid, hi)
        return hi

    ENT = []
    MAIN65 = next(iter(PATHS65))
    for pname in PATHS65:
        for var in ("", "α固定|", "粗利0|", "粗利1|"):
            if var.startswith("粗利") and pname != MAIN65:
                continue
            for cap, start in (("主", 48_000.0), ("低位", 48_000.0), ("高位", 48_000.0), ("主", 67_000.0)):
                if (pname != MAIN65 or var) and (cap, start) != ("主", 48_000.0):
                    continue
                for P in (0.0, 11_867.0, P_CAP, 20_911.0):
                    for ltda in ((True, False) if (pname == MAIN65 and not var and cap == "主" and start == 48_000.0) else (True,)):
                        first, Kt = solve65(pname, P, cap, start, var, ltda)
                        lab = {"": "主", "α固定|": "α を蓄電池なしの値に固定", "粗利0|": "必要な粗利 " + list(RATIO)[0], "粗利1|": "必要な粗利 " + list(RATIO)[1]}[var]
                        ENT.append({"経路": pname, "変種": lab, "資本費の経路": cap, "足下の単価(万円/kWh)": start / 1e4, "容量価格 P(円/kW)": P,
                                    "LTDA を先に入れる": ltda, "市場参入の最初の年": first,
                                    **{f"合計 {t}": Kt[t] for t in (2030, 2035, 2040, 2045)},
                                    **{f"うち市場参入 {t}": Kt[t] - (LTDA_K0(t) if ltda else 0.0) for t in (2030, 2035, 2040)}})
                ENT[-1]["2040年の合計が80万kW に要る P(円/kW)"] = required65(pname, cap=cap, start=start, var=var)
                ENT[-1]["2040年の合計が100万kW に要る P(円/kW)"] = required65(pname, target=100.0, cap=cap, start=start, var=var)
    ENTD = pd.DataFrame(ENT)
    ENTD.round(2).to_csv(os.path.join(PROC, "revsuff_entry.csv"), index=False, encoding="utf-8-sig")

    # ---- 全体像: 年ごとの需給（電源構成）と価格。主の経路、蓄電池なしと均衡の量（容量価格14,972円、LTDA を含む合計）
    Kt_main = solve65(MAIN65, P_CAP)[1]
    BAL = []
    Pq = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"]).set_index("ts")
    q = Pq[(Pq.index >= "2024-04-01") & (Pq.index < "2026-04-01")]
    tw = lambda c: float(q[c].fillna(0).sum() / 2 / 1e6)
    hq = q.index.hour
    BAL.append({"年": "実績 FY2024〜25", "系列": "実績", "需要(TWh)": tw("demand"), "原子力": tw("nuclear"), "太陽光（抑制前）": tw("solar") + tw("solar_curt"),
                "風力（抑制前）": tw("wind") + tw("wind_curt"), "抑制": tw("solar_curt") + tw("wind_curt"), "水力": tw("hydro"), "地熱": tw("geothermal"),
                "バイオマス": tw("biomass"), "火力（合計）": tw("thermal"), "揚水の動力−発電": -tw("pumped"), "北本の送電−受電": -tw("interconn"),
                "時間平均の価格": q["p_hokkaido"].mean(), "需要加重の平均価格": float((q["p_hokkaido"] * q["demand"]).sum() / q["demand"].sum()),
                "昼10〜15時": q["p_hokkaido"][(hq >= 10) & (hq < 15)].mean(), "夕17〜21時": q["p_hokkaido"][(hq >= 17) & (hq < 21)].mean(),
                "夜0〜6時": q["p_hokkaido"][hq < 6].mean(), "0.01円の時間(h/年)": float((q["p_hokkaido"] <= 0.011).sum() / 2),
                "約定総額(億円/年)": float((q["p_hokkaido"] * q["demand"]).sum() / 2 * 1_000 / 1e8)})
    for y in YEARS:
        A, short = year_arrays(y, PATHS65[MAIN65])
        BAL.append({"年": y, **balance(A, snapshot(A, 0), "蓄電池なし"), "火力（対象）MW": A["target_cap"], "足りない供給力(MW)": short})
        if y in (2030, 2035, 2040):
            K = float(K_EVAL[np.argmin(np.abs(K_EVAL - Kt_main[y]))])
            BAL.append({"年": y, **balance(A, snapshot(A, K), f"均衡の蓄電池 {K:.0f}万kW（P＝14,972円、LTDA 込み）"), "火力（対象）MW": A["target_cap"]})
    BALD = pd.DataFrame(BAL)
    BALD.round(3).to_csv(os.path.join(PROC, "revsuff_balance.csv"), index=False, encoding="utf-8-sig")
    print("\n年ごとの需給と価格（主の経路）"); print(BALD.round(2).to_string(index=False))
    print("\n年ごとの α と価格（K＝0）")
    print(YRD[["経路", "年", "火力（対象）MW", "足りない供給力(MW)", "α K=0", "価格の平均 K=0", "昼10〜15時 K=0", "夕17〜21時 K=0", "夜0〜6時 K=0",
               "0.01円の時間(h/年) K=0", "π K=0", "α K=50", "π K=20", "π K=50", "π K=100"]].round(2).to_string(index=False))
    print("\n均衡の経路（合計は LTDA の北海道分を含む、万kW）")
    print(ENTD.round(1).to_string(index=False))
    print(f"計 {time.time() - t0:.0f}s")

    # ---- 図: (a) 年ごとの α と昼・夕の価格（K＝0）、(b) 時刻別の価格の形（主の経路、年平均）
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Hiragino Sans", "Yu Gothic", "IPAexGothic", "sans-serif"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    Y = YRD[YRD["経路"] == MAIN65]
    ax[0].plot(Y["年"], Y["夕17〜21時 K=0"], "-o", color="k", ms=3, label="夕17〜21時の平均")
    ax[0].plot(Y["年"], Y["価格の平均 K=0"], "--", color="0.4", label="全時間の平均")
    ax[0].plot(Y["年"], Y["昼10〜15時 K=0"], ":o", color="0.4", ms=3, label="昼10〜15時の平均")
    ax[0].set_ylabel("価格（円/kWh、蓄電池なし）")
    a2 = ax[0].twinx()
    a2.bar(Y["年"], Y["α K=0"], color="0.88", width=0.6, zorder=0, label="α（右軸）")
    a2.set_ylabel("α（過去の上乗せに対する倍率）")
    ax[0].set_zorder(a2.get_zorder() + 1)
    ax[0].patch.set_visible(False)
    ax[0].legend(fontsize=8, loc="upper left")
    ax[0].set_title("(a) 火力の粗利を保つ価格（主の経路）", fontsize=10)
    PR = pd.DataFrame(PROF)
    hcols = [f"{h}時" for h in range(24)]
    for y, st in zip(PROF_YEARS, ("-", "--", "-.", ":")):
        q = PR[(PR["経路"] == MAIN65) & (PR["年"] == y) & (PR["K(万kW)"] == 0.0)][hcols].mean()
        ax[1].plot(range(24), q.to_numpy(), st, color="k", label=f"{y}年（K＝0）")
    q = PR[(PR["経路"] == MAIN65) & (PR["年"] == 2035) & (PR["K(万kW)"] == 50.0)][hcols].mean()
    ax[1].plot(range(24), q.to_numpy(), "-", color="0.6", label="2035年（K＝50万kW）")
    act_h = [act[mb & (hr == h)].mean() for h in range(24)]
    ax[1].plot(range(24), act_h, "o", color="0.3", ms=3, label="実績 FY2024〜25")
    ax[1].set_xlabel("時刻")
    ax[1].set_ylabel("価格（円/kWh、季節の平均）")
    ax[1].set_xticks(range(0, 24, 3))
    ax[1].legend(fontsize=8)
    ax[1].set_title("(b) 時刻別の価格の形", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "figures", "hokkaido", "revsuff_price_shape.png"), dpi=200)
    print("図を保存: figures/hokkaido/revsuff_price_shape.png")
