# -*- coding: utf-8 -*-
"""表6.1: 主の経路の平均価格の変化（2026年のモデル → 年 y のモデル）を、8つの要因に分ける（Shapley 値: 2^8 の組み合わせを全部解く）。
要因を「切る」＝その要因だけ2026年の値に戻す。燃料費・東北の価格の土台・気象年は全部の年で同じ。
（2026-11-01 に scratchpad で作った計算を、2026-11-03 の新しい主の再計算のためにリポジトリに移した。中身は同じ）
使い方: WORKERS=9 python analysis/92_v2_price_decomposition.py [年...]  （既定 2030 2035 2040）。
出力: data/processed/v2_decomp_<年>.csv（256通りの結果）、v2_decomp_shapley.csv（要因ごとの Shapley 値）
"""
import itertools
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from model import params as PR, merit as MO, simple as SM, balance as BAL  # noqa: E402

OUT = os.path.join(ROOT, "data", "processed")
BASE_Y = 2026
P = 14_972.0
FACTORS = ["需要", "原子力", "太陽光・風力", "地熱・バイオマス", "火力の入れ替え", "北本", "蓄電池", "火力の容量収入"]
E = pd.read_csv(os.path.join(ROOT, "data/processed/simple_entry.csv"), encoding="utf-8-sig")
PATH = E[(E["場合"] == "上乗せ") & (E["容量価格(円/kW)"] == P)].iloc[0]
K_PATH = {y: float(PATH[f"量 {y}"]) for y in range(2026, 2041)}
_CAL = None


def cal():
    global _CAL
    if _CAL is None:
        _CAL = SM.calibration("commit", None)
    return _CAL


def job(arg):
    y, on = arg                                                 # on: 要因 → True なら年 y の値、False なら2026年の値
    sc = PR.SCENARIOS["主"]
    sy, s0 = PR.scenario_year(y, sc), PR.scenario_year(BASE_Y, sc)
    keys = {"需要": ("demand_gwh", "dc_gwh"), "原子力": ("nuclear",), "太陽光・風力": ("solar_mw", "selfcons_mw", "wind_mw"),
            "地熱・バイオマス": ("biomass_add_mw", "geo_add_mw"), "北本": ("export_opcap", "export_increment_mw")}
    for f, ks in keys.items():
        if not on[f]:
            for k in ks:
                sy[k] = s0[k]
    I = MO.inputs_future(sy, sc)
    if not on["北本"]:
        I["link"] = MO.link_caps(BASE_Y, sc.get("link_share"))
    orig, orig_tcr, orig_amm = BAL.fleet, PR.thermal_cap_receipt, PR.ltda_ammonia
    if not on["火力の入れ替え"]:                                  # 号機の入れ替え（新設・廃止）と、苫東厚真4号のアンモニア混焼の LTDA 分（要件から外す分）
        BAL.fleet = lambda year, drop=(): orig(BASE_Y, drop)
        PR.ltda_ammonia = lambda year: orig_amm(BASE_Y)
    if not on["火力の容量収入"]:                                  # 火力が受け取る容量収入（③の要件から引く分）を2026年の値に戻す
        PR.thermal_cap_receipt = lambda year, after2030=14_972.0: orig_tcr(BASE_Y, after2030)
    try:
        K = K_PATH[y] if on["蓄電池"] else K_PATH[BASE_Y]
        t0 = time.time()
        T, _ = SM.run_year(I, cal(), Ks=[K], P_list=(P,), standard=False, mode="commit", p_sched=P, drop=(), mustrun=None,
                           losses="spot", shape="flat")
    finally:
        BAL.fleet, PR.thermal_cap_receipt, PR.ltda_ammonia = orig, orig_tcr, orig_amm
    r = T.iloc[0]
    return {"年": y, **{f: int(on[f]) for f in FACTORS}, "K": K, "平均価格": r["平均価格（需要加重）"], "0.01円の時間": r["0.01円の時間(h/年)"],
            "上乗せ μ": r["上乗せ μ(円/kWh)"], "高い4時間": r["高い4時間の平均(円/kWh)"], "安い4時間": r["安い4時間の平均(円/kWh)"],
            "夕17〜21時": r["夕17〜21時"], "昼10〜15時": r["昼10〜15時"], "夜0〜6時": r["夜0〜6時"], "火力の発電量": r["火力の発電量(TWh)"],
            "抑制": r["抑制(TWh)"], "北本 送電": r["北本 送電(TWh)"], "秒": time.time() - t0}


def shapley(df, col):
    n = len(FACTORS)
    val = {tuple(int(r[f]) for f in FACTORS): r[col] for _, r in df.iterrows()}
    from math import factorial
    out = {}
    for i, f in enumerate(FACTORS):
        s = 0.0
        for S in itertools.product((0, 1), repeat=n):
            if S[i]:
                continue
            k = sum(S)
            w = factorial(k) * factorial(n - k - 1) / factorial(n)
            S1 = list(S); S1[i] = 1
            s += w * (val[tuple(S1)] - val[S])
        out[f] = s
    return out


if __name__ == "__main__":
    years = [int(a) for a in sys.argv[1:]] or [2030, 2035, 2040]
    if os.environ.get("ONE"):                                    # 時間を測る: 全部の要因が年 y の値（主の再現）
        print(job((years[0], {f: True for f in FACTORS})))
        sys.exit()
    jobs = [(y, dict(zip(FACTORS, map(bool, S)))) for y in years for S in itertools.product((0, 1), repeat=len(FACTORS))]
    print("計算の数", len(jobs), flush=True)
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "8"))) as ex:
        rows = list(ex.map(job, jobs, chunksize=1))
    D = pd.DataFrame(rows)
    SH = []
    for y in years:
        d = D[D["年"] == y]
        d.to_csv(os.path.join(OUT, f"v2_decomp_{y}.csv"), index=False, encoding="utf-8-sig")
        full = d[(d[FACTORS] == 1).all(1)].iloc[0]
        base = d[(d[FACTORS] == 0).all(1)].iloc[0]
        print(f"\n{y}: 2026年の値に全部戻す {base['平均価格']:.3f} → 主 {full['平均価格']:.3f}（差 {full['平均価格'] - base['平均価格']:+.3f}）")
        for col in ("平均価格", "0.01円の時間", "上乗せ μ", "高い4時間", "安い4時間"):
            sh = shapley(d, col)
            SH.append({"年": y, "指標": col, **sh, "合計": sum(sh.values()), "主の値": full[col], "2026年の値": base[col]})
            print(f"  {col}: " + "  ".join(f"{f} {v:+.2f}" for f, v in sh.items()) + f"  合計 {sum(sh.values()):+.2f}")
    pd.DataFrame(SH).to_csv(os.path.join(OUT, "v2_decomp_shapley.csv"), index=False, encoding="utf-8-sig")
