# -*- coding: utf-8 -*-
"""火力の固定費を kW の支払いで補う場合の需要家の負担（簡素版のモデル、2026-11-01）
使い方: python analysis/87_simple_capacity_cost.py（主）。太陽光の上振れは SOLAR_UP="600,186" ONLY_SCEN="太陽光 上振れ" KMAX=400
A_GRID="10000,14972,17000,19000,20911" B_GRID="0,2028,4028,5939,8000,10028,12000,15028" OUT=data/processed/simple_capcost/solar600。
見方ごとの負担・図は analysis/88_simple_capacity_cost_burden.py

主（スポットに集約）: 火力の総収入の要件のうち、容量収入（2030年度以降14,972円）で足りない分とマストランの運転の赤字を、一律の上乗せ μ で回収する。
補い方（2030年度以降に効く。2026〜29年度は主と同じ）:
  A 容量価格を上げる: 2030年度以降の容量価格 P を変える。火力・原子力・水力・蓄電池などすべての電源に P が払われ、
    需要家は P×調達量を払う。蓄電池の容量収入も κ×P に上がる。
  B 火力だけに kW で払う: 容量価格は14,972円のまま、上乗せの対象の火力（LTDA を除く）にだけ1kW あたり X 円を市場の外で払う
    （予備電源・LTDA の既設改修のような対象を絞った kW の支払いを想定）。蓄電池の容量収入は κ×14,972円のまま。
どちらも、要件のうちスポットで回収する額が k×（P または 14,972＋X）だけ減る（火力の必要な収入の式は主と同じ）。
各点で、π(K) の曲線から参入の経路を解き直し、その量で年ごとに需給と価格を解いて負担を測る。
負担の計算（見方ごとの足し方）は capcost_post.py。ここでは、その材料（スポットの支払い、FIT/FIP の電源ごとの分、LTDA の電源の粗利、
容量市場の調達量と LTDA の容量、火力への kW の支払い、原子力・一般水力の要件）を年ごとに書き出す。
"""
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from model import params as PR, merit as MO, simple as SM, entry as EN, balance as B  # noqa: E402

OUT = os.environ.get("OUT", os.path.join(ROOT, "data", "processed", "simple_capcost", "main"))
PROC = os.path.join(ROOT, "data", "processed")
WORKERS = int(os.environ.get("WORKERS", "9"))
BASE_P = 14_972.0
KS = SM.K_GRID[SM.K_GRID <= float(os.environ.get("KMAX", "800")) + 1e-9]   # 格子の上限（上振れのシナリオは計算の時間のため400）
EVAL_YEARS = list(range(2030, 2041))
A_GRID = [0.0, 5_000.0, 10_000.0, 12_500.0, 14_972.0, 16_000.0, 17_000.0, 18_000.0, 19_000.0, 20_000.0, 20_911.0, 25_000.0, 30_000.0]
B_GRID = [0.0, 1_028.0, 2_028.0, 3_028.0, 4_028.0, 5_028.0, 5_939.0, 8_000.0, 10_028.0, 11_000.0, 12_000.0, 13_000.0, 15_028.0]
if os.environ.get("A_GRID"):
    A_GRID = [float(x) for x in os.environ["A_GRID"].split(",")]
if os.environ.get("B_GRID"):
    B_GRID = [float(x) for x in os.environ["B_GRID"].split(",")]
RETURN_SHARE = float(os.environ.get("RETURN_SHARE", "0.9"))        # LTDA の他市場収益の還付の比
NUC_LTDA = os.environ.get("NUC_LTDA", "1") == "1"                    # 泊3号を LTDA の還付の対象に入れるか
Q_CAP = 529.0                                                         # 北海道の容量市場の調達量（万kW、FY2029 向け H3）
LTDA_BIO_MW = 199.0 * 0.70                                            # LTDA のバイオマス（FIT/FIP ではない、2034年から）

# シナリオ（PR.SCENARIOS の名前をカンマ区切りで SCENS に。太陽光の上振れ（旧の主の頑健性）は環境変数で 2040年の値を渡す: SOLAR_UP="総量,需要地併設型" 万kW）
_v = os.environ.get("SCENS", "主")                              # 名前にコンマを含むシナリオ（"2040年 9,000億kWh" など）は "|" で区切る
SCENS = {n: PR.SCENARIOS[n] for n in _v.split("|" if "|" in _v else ",")}
if os.environ.get("SOLAR_UP"):
    s, o = [float(x) * 10 for x in os.environ["SOLAR_UP"].split(",")]
    PR.Y2040["solar_up"] = {**PR.Y2040["11000"], "solar": s, "onsite": o}
    PR.SELFCONS_SHARE["solar_up"] = o / s
    SCENS["太陽光 上振れ"] = dict(y2040="solar_up", nuclear="3号だけ", path="linear")   # 旧の主の頑健性なので旧の経路に固定
_CAL = None


def cal():
    global _CAL
    if _CAL is None:
        _CAL = SM.calibration("commit", None)
    return _CAL


def p_req(lever, v):
    return v if lever == "A" else BASE_P + v


def p_batt(lever, v):
    return v if lever == "A" else BASE_P


def curve_job(a):
    scen, P, y, drop = a
    sc = SCENS[scen]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    T, _ = SM.run_year(I, cal(), Ks=KS, P_list=(P,), p_sched=P, drop=drop)
    return (scen, P, y), T.sort_values("K(万kW)")["π(円/kW-年)"].to_numpy()


def exit_job(scen):
    before, when = SM.exit_years(cal(), SCENS[scen], PR.YEARS, "commit")
    return scen, before, when


def h3(I):
    """各年度の上位3日の日の最大需要の平均（MW、気象年の平均）"""
    out = []
    for fy in np.unique(I["fy"]):
        r = np.where(I["fy"] == fy)[0]
        out.append(np.sort(I["D"][r].max(1))[-3:].mean())
    return float(np.mean(out))


def eval_job(a):
    scen, lever, v, y, K, drop = a
    sc = SCENS[scen]
    sy = PR.scenario_year(y, sc)
    I = MO.inputs_future(sy, sc)
    P = p_req(lever, v)
    c = cal()
    T, _, st = SM.run_year(I, c, Ks=[K], P_list=(P,), p_sched=P, drop=drop, return_state=True)
    t = T.iloc[0]
    R, p, chg, dis, info, alive = st["R"], st["p"], st["chg"], st["dis"], st["info"], st["alive"]
    nd = p.shape[0]
    yrs = nd / 365.25
    oku = lambda x: float(np.asarray(x).sum() * 1_000 / yrs / 1e8)
    k = c["k"]
    names = [u[0] for u in R["units"]]
    g, vc = R["g"], R["vc"]
    margin_u = {n: oku((p - vc[:, :, j]) * g[:, :, j]) for j, n in enumerate(names)}
    bio_ltda = LTDA_BIO_MW if y >= 2034 else 0.0
    F = I["S"] + I["W"] - R["curt"] + I["G"] + np.maximum(I["Bm"] - bio_ltda, 0.0)
    spot_D = oku(p * I["D"])
    spot_F = oku(p * F)
    # 抑制を太陽光（制御できる分）と風力に出力の比で分ける
    sc_ = np.maximum(I["S"] - I["U"], 0.0)
    den = sc_ + I["W"]
    cS = np.where(den > 1e-9, R["curt"] * sc_ / np.where(den > 1e-9, den, 1.0), 0.0)
    spot_S = oku(p * (I["S"] - cS))
    spot_W = oku(p * (I["W"] - (R["curt"] - cS)))
    spot_G = oku(p * I["G"])
    spot_Bm = oku(p * np.maximum(I["Bm"] - bio_ltda, 0.0))
    # LTDA の電源のスポットの粗利（還付の対象）
    ltda_th = sum(margin_u.get(n, 0.0) for n in PR.LTDA_UNITS)
    amm = PR.ltda_ammonia(y) / 662.0 * margin_u.get("苫東厚真4", 0.0)
    arb = oku(p * (dis - chg))                                       # 蓄電池全体の値差の収入（完全予見）
    ltda_b = EN.ltda_stock(y) / K * arb if K > 0 else 0.0      # LTDA の分（全体と同じ動き）
    nuc_cap = sum(PR.NUC[u] for u, m in sy["nuclear"])                # その年に動く泊（年度の途中からも1基と数える）
    nuc_m = oku((p - PR.NUC_VC) * I["N"])
    hy_m = oku(p * I["Hy"])
    # 容量市場: 調達量は H3 需要に比例（FY2029 向け529万kW を基準。モデルの2029年の H3 で割る）。
    # メインオークションは LTDA の落札分を差し引いて調達するので、容量価格で払う量＝調達量−LTDA の容量（万kW、期待容量の概数）
    Pcap = PR.cap_price(y, p_batt(lever, v))
    q = Q_CAP * h3(I) / H3_2029[scen]
    ltda_kw = (nuc_cap / 10.0 if NUC_LTDA else 0.0) + 55.8 * (y >= 2030) + 55.8 * (y >= 2033) + PR.ltda_ammonia(y) / 10.0 \
        + 32.5 * (y >= 2029) + 20.9 * (y >= 2030) + 14.0 * (y >= 2031) + 19.9 * (y >= 2034)
    tgt = info["cap"]                                                  # 上乗せの対象の火力（MW）
    x_pay = (v if lever == "B" else 0.0) * tgt * 1_000 / 1e8
    # 原子力・水力の要件（届かない分は契約で払う。実際の円）
    nuc_req = PR.NUC_REQ["続ける費用（主）"] * 0.70 * 8760 * nuc_cap * 1_000 / 1e8
    hy_cap = sum(PR.HYDRO_CAP.values())
    hy_req = PR.HYDRO_REQ * hy_cap * 1_000 / 1e8
    hy_rev = hy_m + Pcap * sum(PR.HYDRO_CAP[kk] * PR.KAPPA_HYDRO[kk] for kk in PR.HYDRO_CAP) * 1_000 / 1e8
    Dtwh = float(I["D"].sum() / yrs / 1e6)
    return {"シナリオ": scen, "補い方": lever, "値(円/kW)": v, "容量価格(円/kW)": Pcap, "年": y, "蓄電池(万kW)": K,
            "上乗せ μ(円/kWh)": t["上乗せ μ(円/kWh)"], "平均価格（需要加重）": t["平均価格（需要加重）"], "π(円/kW-年)": t["π(円/kW-年)"],
            "要件(億円/年)": t["要件(億円/年)"], "α＝1 の粗利(億円/年)": t["α＝1 の粗利(億円/年)"], "粗利(億円/年)": t["粗利(億円/年)"],
            "対象の火力(MW)": tgt, "退出する号機": t["退出する号機"], "需要(TWh)": Dtwh,
            "スポットの支払い Σp×需要(億円/年)": spot_D, "FIT/FIP の電源の分 すべて(億円/年)": spot_F,
            "LTDA 火力の粗利(億円/年)": ltda_th, "アンモニア混焼分の粗利(億円/年)": amm, "蓄電池全体の値差の収入(億円/年)": arb,
            "LTDA 蓄電池の値差の収入(億円/年)": ltda_b, "原子力の粗利(億円/年)": nuc_m, "一般水力の粗利(億円/年)": hy_m,
            "容量市場の調達量(万kW)": q, "LTDA の容量(万kW)": ltda_kw, "容量市場の支払い 調達量全体(億円/年)": Pcap * q * 1e4 / 1e8,
            "容量市場の支払い LTDA を除く(億円/年)": Pcap * max(q - ltda_kw, 0.0) * 1e4 / 1e8,
            "火力への kW の支払い(億円/年)": x_pay, "原子力の要件(億円/年)": nuc_req, "泊の設備(MW)": nuc_cap,
            "一般水力の要件(億円/年)": hy_req, "一般水力の収入(億円/年)": hy_rev,
            "太陽光の分 Σp×出力(億円/年)": spot_S, "風力の分 Σp×出力(億円/年)": spot_W, "地熱の分(億円/年)": spot_G, "バイオマスの分（LTDA 以外）(億円/年)": spot_Bm,
            "太陽光（系統）の設備(MW)": sy["solar_mw"], "風力の設備(MW)": sy["wind_mw"], "k": k,
            "抑制(TWh)": t["抑制(TWh)"], "0.01円の時間(h/年)": t["0.01円の時間(h/年)"]}


def _h3_2029(scen):
    sc = SCENS[scen]
    return scen, h3(MO.inputs_future(PR.scenario_year(2029, sc), sc))


H3_2029 = {}


def _init(h):
    H3_2029.update(h)


def main():
    os.makedirs(OUT, exist_ok=True)
    only = os.environ.get("ONLY_SCEN")
    scens = [s for s in SCENS if only is None or s in only.split("|" if "|" in only else ",")]
    h = dict(_h3_2029(s) for s in SCENS)
    H3_2029.update(h)
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_init, initargs=(h,)) as ex:
        # 退出の年（先に入っている蓄電池の量の経路）
        drops = {}
        for scen, before, when in ex.map(exit_job, scens):
            drops[scen] = before
            print(scen, "退出", when, flush=True)
        # π(K) の曲線: 主の格子の点は保存したものを使い、ほかは解く
        need, curves = [], {}
        preqs = sorted({p_req("A", v) for v in A_GRID} | {p_req("B", v) for v in B_GRID})
        for scen in scens:
            f = os.path.join(PROC, "simple_pik.npz" if scen == "主" else f"simple_pik_{scen}.npz")   # 80 で保存した曲線（同じ格子なら使い回す）
            Z = dict(np.load(f)) if os.path.exists(f) else {"K": np.array([])}
            use_saved = np.allclose(Z["K"], KS) if len(Z["K"]) == len(KS) else False
            for y in PR.YEARS:
                for P in (preqs if y >= 2030 else [BASE_P]):
                    key = f"上乗せ|{P:.0f}|{y}"
                    if use_saved and key in Z:
                        curves[(scen, P, y)] = Z[key]
                    else:
                        need.append((scen, P, y, drops[scen][y]))
        if os.environ.get("REUSE_CURVES") == "1":                 # 保存した曲線を使う（評価だけやり直す）
            C0 = pd.read_csv(os.path.join(OUT, "capcost_curves.csv"), encoding="utf-8-sig")
            for (sn, P, y), g in C0.groupby(["シナリオ", "要件の容量価格(円/kW)", "年"]):
                curves[(sn, float(P), int(y))] = g.sort_values("K(万kW)")["π(円/kW-年)"].to_numpy()
            need = [n for n in need if (n[0], n[1], n[2]) not in curves]
        print("曲線を解く数", len(need), flush=True)
        for key, pi in ex.map(curve_job, need, chunksize=1):
            curves[key] = pi
        rows = []
        for scen in scens:
            for (_, P, y), pi in curves.items():
                if _ == scen:
                    rows += [{"シナリオ": scen, "要件の容量価格(円/kW)": P, "年": y, "K(万kW)": kk, "π(円/kW-年)": vv} for kk, vv in zip(KS, pi)]
        pd.DataFrame(rows).to_csv(os.path.join(OUT, "capcost_curves.csv"), index=False, encoding="utf-8-sig")
        # 参入の経路と評価
        paths, jobs = [], []
        for scen in scens:
            for lever, grid in (("A", A_GRID), ("B", B_GRID)):
                for v in grid:
                    pi = {y: curves[(scen, p_req(lever, v) if y >= 2030 else BASE_P, y)] for y in PR.YEARS}
                    Kt = EN.path(pi, KS, p_batt(lever, v))
                    paths.append({"シナリオ": scen, "補い方": lever, "値(円/kW)": v, **{f"量 {t}": Kt[t] for t in range(2026, 2046)}})
                    for y in EVAL_YEARS:
                        if Kt[y] < KS[-1] - 1e-6:
                            jobs.append((scen, lever, v, y, float(Kt[y]), drops[scen][y]))
        pd.DataFrame(paths).to_csv(os.path.join(OUT, "capcost_paths.csv"), index=False, encoding="utf-8-sig")
        print("評価の数", len(jobs), flush=True)
        R = pd.DataFrame(list(ex.map(eval_job, jobs, chunksize=1)))
    R.to_csv(os.path.join(OUT, "capcost_eval.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(R.groupby(["シナリオ", "補い方", "値(円/kW)"])["上乗せ μ(円/kWh)"].mean().round(2).to_string())


if __name__ == "__main__":
    main()
