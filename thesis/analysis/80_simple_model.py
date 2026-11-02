#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデル（model/simple.py、著者の決定 2026-10-27）の実行

① コマごとのメリットオーダーで価格（マストラン3台） ② 火力の入札に一律の上乗せ（マストランの赤字も含む） ③ 必要な収入は足元のスポット＋容量収入
④ 1年間動かない号機は退出
1. 較正と当てはまり（FY2024〜25）
2. 将来（2026〜2040）: 蓄電池の量 K ごとの π(K)、退出、α。スポットで回収（容量価格ごと）、赤字だけ市場外、すべて市場外（μ＝0）。
   呼び名（2026-11-02 の決定）: 場合のキー「上乗せ」＝スポットで回収（主）、「上乗せ_赤字は外」＝赤字だけ市場外、「燃料費」＝すべて市場外
   頑健性: 比例の上乗せ、マストランの赤字はスポットの外で精算、マストラン2台、マストランなし
3. 参入（容量価格ごと、κ＝0.861 一定。規則は PR.ENTRY_RULE）と、参入の経路での火力の退出
出力: data/processed/simple_*.csv・simple_pik.npz
ENTRY_ONLY=1 なら 1・2 を飛ばし、保存した simple_years.csv から 3 だけを計算し直す（参入の規則だけを変えたとき）
SCEN＝シナリオの名前（PR.SCENARIOS）、CASES＝場合の名前（カンマ区切り）、P_GRID＝容量価格の格子（カンマ区切り）で絞れる
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, battery as BT, entry as EN, merit as MO, simple as SM

PROC = os.environ.get("EQM_PROC") or os.path.join(ROOT, "data", "processed")
WORKERS = int(os.environ.get("WORKERS", "8"))
P_GRID = [0.0, 5_000.0, 10_000.0, 12_500.0, 14_972.0, 16_000.0, 17_000.0, 18_000.0, 19_000.0, 20_000.0, 20_911.0, 25_000.0, 30_000.0]
BASE_P = 14_972.0
MR2 = ("石狩湾新港1", "苫東厚真4")
CASES = {  # キー: (表示名, standard, 需給の mode, マストラン（None は主の3台）, 運転の赤字の払い方, 上乗せの形)
    "上乗せ": ("スポットで回収（主、一律の上乗せ）", False, "commit", None, "spot", "flat"),
    "燃料費": ("すべて市場外（μ＝0、燃料費で入札）", True, "commit", None, "spot", "flat"),
    "上乗せ_比例": ("スポットで回収（比例の上乗せ）", False, "commit", None, "spot", "prop"),
    "上乗せ_赤字は外": ("赤字だけ市場外（マストランの赤字は送配電が市場の外で精算）", False, "commit", None, "outside", "flat"),
    "上乗せ_マストラン2台": ("スポットで回収（マストラン2台、知内2 を外す）", False, "commit", MR2, "spot", "flat"),
    "上乗せ_マストランなし": ("スポットで回収（マストランなし）", False, "commit", (), "spot", "flat"),
}
if os.environ.get("CASES"):                                    # 頑健性のシナリオでは場合と容量価格の格子を絞る（計算の時間）
    CASES = {k: v for k, v in CASES.items() if k in os.environ["CASES"].split(",")}
if os.environ.get("P_GRID"):
    P_GRID = [float(x) for x in os.environ["P_GRID"].split(",")]
SCEN = os.environ.get("SCEN", "主")
ENTRY_ONLY = os.environ.get("ENTRY_ONLY") == "1"
YEARS = PR.YEARS
_CAL = {}


def _cal(mode, mustrun=None):
    key = (mode, mustrun)
    if key not in _CAL:
        _CAL[key] = SM.calibration(mode, mustrun)
    return _CAL[key]


def _job(job):
    import warnings
    warnings.filterwarnings("ignore")
    case, P, y, drop = job
    _, standard, mode, mr, losses, shape = CASES[case]
    sc = PR.SCENARIOS[SCEN]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    T, _ = SM.run_year(I, _cal(mode, mr), Ks=SM.K_GRID, P_list=(P,), standard=standard, mode=mode, p_sched=P, drop=drop,
                       mustrun=mr, losses=losses, shape=shape)
    T.insert(0, "前の年までに退出", "・".join(drop))
    T.insert(0, "年", y)
    T.insert(0, "場合", case)
    T.insert(0, "シナリオ", SCEN)
    return T


def entry_paths(Y, Ks):
    """場合・容量価格ごとの量の経路（κ＝0.861 一定）"""
    rows, curves = [], {}
    for case in CASES:
        for P in P_GRID:
            src = BASE_P if CASES[case][1] else P                # 一般的な方法の π は容量価格によらない
            g = Y[(Y["場合"] == case) & (Y["容量価格(円/kW)"] == src)]
            if g.empty:
                continue
            pi = {y: g[g["年"] == y].sort_values("K(万kW)")["π(円/kW-年)"].to_numpy() for y in YEARS}
            for y in YEARS:
                curves[f"{case}|{P:.0f}|{y}"] = pi[y]
            Kt = EN.path(pi, Ks, P)
            rows.append({"シナリオ": SCEN, "場合": case, "容量価格(円/kW)": P, **{f"量 {t}": Kt[t] for t in range(2026, 2046)}})
    return pd.DataFrame(rows), curves


def required_price(Z, Ks, targets=(100.0, 150.0, 200.0), year=2040, kappa_by_year=None):
    """year 年の合計が目標の量になるのに要る、2030年度以降の容量価格（π の曲線は容量価格の格子の間を直線で補間、二分法）"""
    def curves(case, P):
        grid = sorted({float(k.split("|")[1]) for k in Z if k.startswith(case + "|")})
        lo = max([q for q in grid if q <= P] or [grid[0]])
        hi = min([q for q in grid if q >= P] or [grid[-1]])
        a = lambda q, y: Z[f"{case}|{q:.0f}|{y}"]
        return {y: a(lo, y) if hi == lo else a(lo, y) + (a(hi, y) - a(lo, y)) * (P - lo) / (hi - lo) for y in YEARS}
    rows = []
    for case in CASES:
        if not any(k.startswith(case + "|") for k in Z):
            continue
        for tgt in targets:
            f = lambda P: EN.path(curves(case, P), Ks, P, kappa_by_year=kappa_by_year)[year] - tgt
            lo, hi = 0.0, P_GRID[-1]
            if f(lo) >= 0:
                val = 0.0
            elif f(hi) < 0:
                val = np.nan
            else:
                for _ in range(18):
                    mid = (lo + hi) / 2
                    lo, hi = (lo, mid) if f(mid) >= 0 else (mid, hi)
                val = hi
            rows.append({"シナリオ": SCEN, "場合": case, "κ": "0.861 一定" if kappa_by_year is None else "量に応じた実効値（上限0.861）",
                         f"{year}年の合計（万kW）": tgt, "要る容量価格（2030年度以降、円/kW）": val})
    return pd.DataFrame(rows)


def exit_on_path(Y, E, case="上乗せ", P=BASE_P):
    """均衡の経路での火力: 蓄電池0の場合と、均衡の量の場合（格子の近い点）"""
    src = BASE_P if CASES[case][1] else P
    g = Y[(Y["場合"] == case) & (Y["容量価格(円/kW)"] == src)]
    path = E[(E["場合"] == case) & (E["容量価格(円/kW)"] == P)].iloc[0]
    rows = []
    for y in YEARS:
        gy = g[g["年"] == y].set_index("K(万kW)")
        k = float(path[f"量 {y}"])
        kk = gy.index[np.argmin(np.abs(gy.index.to_numpy() - k))]
        a, b = gy.loc[0.0], gy.loc[kk]
        rows.append({"年": y, "均衡の量(万kW)": k, "格子の点": kk, "退出（蓄電池0）": a["退出する号機"], "退出（均衡の量）": b["退出する号機"],
                     "残る火力 蓄電池0(MW)": a["残る火力(MW)"], "残る火力 均衡(MW)": b["残る火力(MW)"],
                     "蓄電池による退出(MW)": a["残る火力(MW)"] - b["残る火力(MW)"], "α 蓄電池0": a["α"], "α 均衡": b["α"],
                     "π 均衡(円/kW-年)": b["π(円/kW-年)"], "平均価格 均衡": b["平均価格（需要加重）"], "抑制 均衡(TWh)": b["抑制(TWh)"]})
    return pd.DataFrame(rows)


def main():
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    suffix = "" if SCEN == "主" else f"_{SCEN}"
    sc = PR.SCENARIOS[SCEN]
    if ENTRY_ONLY:
        Y = pd.read_csv(os.path.join(PROC, f"simple_years{suffix}.csv"), encoding="utf-8-sig")
        return entry_part(Y, sc, suffix)
    # 1. 較正
    fit = []
    for case, mode, mr in (("主（マストラン3台、日ごとの起動と最低出力）", "commit", None), ("マストラン2台", "commit", MR2),
                           ("マストランなし", "commit", ()), ("運転の制約なし", "pure", None)):
        cal = _cal(mode, mr)
        for fy, f in cal["fit"].items():
            fit.append({"需給": case, "年度": fy, "k": cal["k"], **f})
    F = pd.DataFrame(fit)
    if SCEN == "主":
        F.to_csv(os.path.join(PROC, "simple_calibration.csv"), index=False, encoding="utf-8-sig")
    print(F.round(3).to_string())
    # 2. 将来
    # 退出の年（先に入っている蓄電池の量の経路。需給の作り方ごと）
    drops, rows = {}, []
    for case, (_, standard, mode, mr, losses, shape) in CASES.items():
        key = (mode, mr, losses, shape)
        if key in drops:
            continue
        before, when = SM.exit_years(_cal(mode, mr), sc, YEARS, mode, mustrun=mr, losses=losses, shape=shape)
        drops[key] = before
        rows += [{"シナリオ": SCEN, "場合": case, "号機": n, "退出の年": y} for n, y in when.items()]
    pd.DataFrame(rows, columns=["シナリオ", "場合", "号機", "退出の年"]).to_csv(os.path.join(PROC, f"simple_exit_years{suffix}.csv"), index=False, encoding="utf-8-sig")
    print(pd.DataFrame(rows).to_string())
    jobs = []
    for case, (_, standard, mode, mr, losses, shape) in CASES.items():
        for P in ([BASE_P] if standard else P_GRID):
            jobs += [(case, P, y, drops[(mode, mr, losses, shape)][y]) for y in YEARS]
    print(f"計算の数 {len(jobs)}", flush=True)
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        Y = pd.concat(list(ex.map(_job, jobs, chunksize=1)), ignore_index=True)
    Y.to_csv(os.path.join(PROC, f"simple_years{suffix}.csv"), index=False, encoding="utf-8-sig")
    entry_part(Y, sc, suffix)


def entry_part(Y, sc, suffix):
    # 3. 参入
    Ks = np.array(sorted(Y["K(万kW)"].unique()), float)
    E, curves = entry_paths(Y, Ks)
    E.to_csv(os.path.join(PROC, f"simple_entry{suffix}.csv"), index=False, encoding="utf-8-sig")
    np.savez(os.path.join(PROC, f"simple_pik{suffix}.npz"), K=Ks, **curves)
    print(E[["場合", "容量価格(円/kW)", "量 2030", "量 2035", "量 2040", "量 2045"]].round(1).to_string())
    from model import calibrate as CB
    kby = {y: CB.kappa_eff(MO.inputs_future(PR.scenario_year(y, sc), sc), Ks) for y in YEARS}   # 頑健性: κ を量に応じた実効値（前の主の置き方）
    RQ = pd.concat([required_price(curves, Ks), required_price(curves, Ks, kappa_by_year=kby)], ignore_index=True)
    RQ.to_csv(os.path.join(PROC, f"simple_required_capacity_price{suffix}.csv"), index=False, encoding="utf-8-sig")
    print(RQ.round(0).to_string())
    X = pd.concat([exit_on_path(Y, E, c).assign(場合=c) for c in ("上乗せ", "燃料費")], ignore_index=True)
    X.to_csv(os.path.join(PROC, f"simple_exit_path{suffix}.csv"), index=False, encoding="utf-8-sig")
    print(X.round(2).to_string())


if __name__ == "__main__":
    main()
