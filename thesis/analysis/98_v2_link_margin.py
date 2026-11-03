#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの北本の上限の検討（2026-11-03、著者が取得した OCCTO の運用容量の PDF と、年間マージンの公表値から）
スポットで北海道へ受けられる量は「運用容量−マージン（東北⇒北海道）」（JEPX 取引規程 第18条第4項、OCCTO の空容量の式）で、
年間計画の通常時のマージンは480〜610MW ある。基準は北海道向を運用容量900MW のまま置いている。3つの決め方を比べる:
- opcap（基準）: 東北へ送れる量＝運用容量（東北向）×0.65、北海道へ受けられる量＝運用容量
- margin_import: 北海道へ受けられる量だけ 運用容量−マージン（月×平日・休日×昼間帯・夜間帯）
- margin_both: 両方向とも 運用容量（年間計画）−マージン（東北向は FY2023・FY2024 も年間計画どおり900MW）
作業の日（年間マージン p.5）は入れていない。将来は FY2026 の年間マージンの形を当てる（PR.LINK_MARGIN の注）。
1. 当てはまり（FY2024・FY2025、上乗せ前）と推定に使わない期間（FY2023、FY2026 4〜6月）: 表5.1 の指標、方向別の分断、k
2. 2040年の普及均衡点（基準シナリオ、3つの払い方、容量価格14,972円）。k はそれぞれの決め方で較正し直し、退出の年もそれぞれで解く
出力: data/processed/v2_link_margin_fit.csv、v2_link_margin_2040.csv
"""
import importlib.util
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, data as DT, balance as B, merit as MO, price as PZ, simple as SM, calibrate as CB

PROC = os.path.join(ROOT, "data", "processed")
RULES = ("opcap", "margin_import", "margin_both")
P = 14_972.0
Y = 2040
KS = [0.0, 25.0, 50.0, 75.0, 95.0, 100.0, 125.0, 150.0, 175.0, 200.0, 250.0, 300.0, 400.0, 500.0]
CASES = {"上乗せ": (False, "spot"), "上乗せ_赤字は外": (False, "outside"), "燃料費": (True, "spot")}


def _load(name):
    spec = importlib.util.spec_from_file_location(name.split("_")[0] + "_mod", os.path.join(HERE, name))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _set(rule):
    warnings.filterwarnings("ignore")
    PR.LINK_RULE = rule
    SM.calibration.cache_clear()                                # 較正は決め方ごと（プロセスを使い回しても混ざらないように）


def inputs(fy, months=None):
    I = MO.inputs_actual(fy)
    if months is not None:
        keep = np.isin(I["days"].month, months)
        E, M = I["link"]
        for k, v in list(I.items()):
            if isinstance(v, np.ndarray) and v.ndim >= 1 and v.shape[0] == len(keep):
                I[k] = v[keep]
        I["days"] = I["days"][keep]
        I["link"] = (E[keep] if np.ndim(E) else E, M[keep] if np.ndim(M) else M)
    return I


def fit_job(a):
    rule, fy, months, name = a
    _set(rule)
    F = _load("89_v2_fit_direction.py")
    I = inputs(fy, months)
    I["X_act"] = I["X"]
    R = SM.dispatch(I, B.fleet(fy), mode="commit")
    c, d, ca, cm = F.confusion(I, R, {"決め方": rule, "期間": name})
    hist = [u[0] for u in DT.calib()["units"]]
    E, M = I["link"]
    row = {"決め方": rule, "期間": name, **F.fit_row(I, R),
           "受電の上限 中央値(MW)": float(np.median(M)), "送電の上限 中央値(MW)": float(np.median(E)),
           "モデルの分断 安い(時間)": int((cm == 1).sum()), "モデルの分断 高い(時間)": int((cm == 2).sum()),
           "実績の分断 安い(時間)": int((ca == 1).sum()), "実績の分断 高い(時間)": int((ca == 2).sum()),
           "高い分断の一致(時間)": int(((ca == 2) & (cm == 2)).sum()), "安い分断の一致(時間)": int(((ca == 1) & (cm == 1)).sum()),
           "区分が一致(%)": float((ca == cm).mean() * 100), "供給力不足(時間)": int((R.get("short", np.zeros(1)) > 1e-6).sum()) if "short" in R else np.nan,
           "200円の時間": int((R["p0"] >= PR.PRICE_CAP - 1e-6).sum()),
           **{f"{r['実績の区分']} R²": r["R²"] for r in d}, **{f"{r['実績の区分']} MAE": r["MAE"] for r in d},
           "火力の粗利 モデル(円)": PZ.gm(R, R["p0"], np.array([u[0] in hist for u in R["units"]]))}
    return row


def k_job(rule):
    _set(rule)
    cal = SM.calibration("commit", None)
    return rule, float(cal["k"])


def y2040_job(a):
    rule, case = a
    _set(rule)
    standard, losses = CASES[case]
    S = _load("91_v2_sensitivity_2040.py")
    sc = PR.SCENARIOS["主"]
    cal = SM.calibration("commit", None)
    before, when = SM.exit_years(cal, sc, PR.YEARS, "commit", losses=losses if not standard else "spot")
    I = MO.inputs_future(PR.scenario_year(Y, sc), sc)
    T, _ = SM.run_year(I, cal, Ks=KS, P_list=(P,), standard=standard, p_sched=P, drop=before[Y], losses=losses)
    pi = T["π(円/kW-年)"].to_numpy()
    r100 = T[T["K(万kW)"] == 100.0].iloc[0]
    E, M = I["link"]
    return {"決め方": rule, "場合": case, "k": float(cal["k"]), "退出": "・".join(f"{n}({y})" for n, y in when.items()),
            "受電の上限 中央値(MW)": float(np.median(M)), "送電の上限 中央値(MW)": float(np.median(E)),
            "普及均衡点(万kW)": S.k_star(pi, S.threshold(), KS), "しきい値": S.threshold(),
            "π 0万kW": pi[0], "π 100万kW": r100["π(円/kW-年)"], "μ 100万kW": r100["上乗せ μ(円/kWh)"],
            "上乗せが上限 100万kW": bool(r100["上乗せが上限"]), "平均価格 100万kW": r100["平均価格（需要加重）"],
            "日の値幅 100万kW": r100["日の値幅 高い4時間−安い4時間(円/kWh)"], "0.01円の時間 100万kW": r100["0.01円の時間(h/年)"],
            "抑制 100万kW(TWh)": r100["抑制(TWh)"], "北本 送電 100万kW(TWh)": r100["北本 送電(TWh)"], "北本 受電 100万kW(TWh)": r100["北本 受電(TWh)"],
            "粗利 100万kW(億円/年)": r100["粗利(億円/年)"], "要件 100万kW(億円/年)": r100["要件(億円/年)"],
            **{f"π {k:g}万kW": v for k, v in zip(KS, pi)}}


def main():
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 40)
    W = int(os.environ.get("WORKERS", "10"))
    periods = [(2024, None, "FY2024"), (2025, None, "FY2025"), (2023, None, "FY2023（推定に使わない）"), (2026, (4, 5, 6), "FY2026 4〜6月（推定に使わない）")]
    with ProcessPoolExecutor(max_workers=W, max_tasks_per_child=1) as ex:
        fit = list(ex.map(fit_job, [(r, fy, m, n) for r in RULES for fy, m, n in periods], chunksize=1))
        ks = dict(ex.map(k_job, RULES))
        if os.environ.get("FIT_ONLY") != "1":
            y40 = list(ex.map(y2040_job, [(r, c) for r in RULES for c in CASES], chunksize=1))
        else:
            y40 = []
    F = pd.DataFrame(fit)
    F["k（その決め方で較正）"] = F["決め方"].map(ks)
    F.to_csv(os.path.join(PROC, "v2_link_margin_fit.csv"), index=False, encoding="utf-8-sig")
    cols = ["決め方", "期間", "受電の上限 中央値(MW)", "送電の上限 中央値(MW)", "R² 全時間", "R² 全時間 素朴な予測", "R² 分断した時間", "R² 分断した時間 素朴な予測", "MAE",
            "モデルの分断 安い(時間)", "モデルの分断 高い(時間)", "実績の分断 安い(時間)", "実績の分断 高い(時間)", "高い分断の一致(時間)", "安い分断の一致(時間)",
            "区分が一致(%)", "200円の時間", "日の値幅 実績", "日の値幅 モデル", "k（その決め方で較正）"]
    print(F[cols].round(3).to_string(index=False), flush=True)
    if y40:
        T = pd.DataFrame(y40)
        T.to_csv(os.path.join(PROC, "v2_link_margin_2040.csv"), index=False, encoding="utf-8-sig")
        print(T[["決め方", "場合", "k", "退出", "受電の上限 中央値(MW)", "送電の上限 中央値(MW)", "普及均衡点(万kW)", "π 100万kW", "μ 100万kW",
                 "平均価格 100万kW", "日の値幅 100万kW", "0.01円の時間 100万kW", "抑制 100万kW(TWh)", "北本 受電 100万kW(TWh)"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
