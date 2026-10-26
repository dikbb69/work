#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""容量価格を動かしたときの需要家の負担: 負担が最小になる容量価格を探す

払い方のマスごと・容量価格 P ごとに、
  1. 蓄電池の量の経路 K*(P)（eqm_pik.npz の π の曲線と、κ の実効値から参入の均衡を解く）
  2. その年の量 K*(P) で需給と価格を解き直す（要らない火力は退出、マストランも退出できる主の前提）
  3. 需要家の負担＝スポットの支払い（FIT/FIP の電源の分を除く）＋補填＋契約＋容量市場の支払い（P×北海道の調達量）
を出す。FIT/FIP の電源の分を除くのは、回避可能費用・参照価格がスポットに連動し、買取の総額は価格によらないため。
容量市場の支払いは、北海道の調達量を H3 需要（2029年度向け 529万kW）で置く（調達量は蓄電池の参入によらない）。600万kW を感応度にする。
回収しきれない額（北海道の入札のマス）は、同じ収入でくらべるため市場の外で払う場合も出す。
出力: data/processed/eqm_capacity_price_burden.csv
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, battery as BT, calibrate as CB, entry as EN, merit as MO

PROC = os.environ.get("EQM_PROC") or os.path.join(ROOT, "data", "processed")
Q_H = {"主": 529.0, "感応度": 600.0}                            # 北海道の容量市場の調達量（万kW）。OCCTO 2029年度向け需要曲線の H3 需要
P_GRID = [0.0, 5_000.0, 10_000.0, 12_500.0, 14_972.0, 16_000.0, 17_000.0, 18_000.0, 19_000.0, 20_000.0, 20_911.0, 25_000.0]
YEARS_EVAL = (2035, 2040)
CELLS = [  # (表示名, eqm_pik の変種キー, mode, 払い方の引数)
    ("補填・契約（基準）", "capacity_退出あり", "capacity", {}),
    ("補填・スポット", "spot_退出あり", "spot", {}),
    ("赤字はスポット・残りは契約", "capacity_赤字はスポット_退出あり", "capacity", dict(losses="spot")),
    ("すべてスポット（全国の上乗せ）", "all_spot_退出あり", "spot", dict(losses="spot")),
    ("すべてスポット（北海道の入札）", "all_spot_入札_退出あり", "spot", dict(losses="spot", recovery="bid")),
]
_CAL = None
_BS = None


def pi_curves(Z, key, P, years):
    """容量価格 P の π の曲線（格子の間は線形に補間。容量回収で補填のマスは P によらない）"""
    cur = {}
    for y in years:
        grid = sorted(float(k.split("|")[2]) for k in Z.files if k.startswith(f"主|{key}|") and k.endswith(f"|{y}"))
        if len(grid) == 1:
            cur[y] = Z[f"主|{key}|{grid[0]:.0f}|{y}"]
            continue
        lo = max(q for q in grid if q <= P)
        hi = min(q for q in grid if q >= P)
        a, b = Z[f"主|{key}|{lo:.0f}|{y}"], Z[f"主|{key}|{hi:.0f}|{y}"]
        cur[y] = a if hi == lo else a + (b - a) * (P - lo) / (hi - lo)
    return cur


def _init():
    global _CAL, _BS
    import warnings
    import importlib.util
    warnings.filterwarnings("ignore")
    _CAL = CB.calibration(0.0)
    spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "73_burden_split.py"))
    _BS = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_BS)


def _solve(job):
    """1つの（マス、容量価格、年、量）で需給を解き、負担の内訳を返す"""
    name, key, mode, kw, P, y, K = job
    sc = PR.SCENARIOS["主"]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    R, p, a, w, chg, dis = _BS.solve_at(I, _CAL, mode, K, P=P, adequacy=True, **kw)
    yrs = I["D"].shape[0] / 365.25
    oku = lambda x: float(np.asarray(x).sum() * 1_000 / yrs / 1e8)
    fit = I["S"] + I["W"] - R["curt"] + I["Bm"] + I["G"]
    dem = float(I["D"].sum() / yrs / 1e6)
    r = {"払い方": name, "変種キー": key, "容量価格(円/kW)": P, "年": y, "蓄電池（万kW）": K, "α": a,
         "平均価格(円/kWh)": oku(p * I["D"]) / (dem * 10), "夕17〜21時(円/kWh)": float(p[:, 17:21].mean()),
         "スポットの支払い（FIT/FIP の分を除く）(億円/年)": oku(p * (I["D"] - fit)),
         "補填(億円/年)": R["mw"] / 1e8, "契約(億円/年)": R["contract"] / 1e8, "回収しきれない額(億円/年)": R["unrecovered"] / 1e8,
         "残す火力": "・".join(u[0] for u in R["units"]) if "units" in R else "", "需要(TWh)": dem}
    for lab, q in Q_H.items():
        cap = P * q * 1e4 / 1e8
        r[f"容量市場の支払い（{lab} {q:.0f}万kW）(億円/年)"] = cap
        tot = r["スポットの支払い（FIT/FIP の分を除く）(億円/年)"] + r["補填(億円/年)"] + r["契約(億円/年)"] + cap
        r[f"需要家の負担（{lab}）(億円/年)"] = tot
        r[f"需要家の負担（{lab}、回収しきれない額も払う）(億円/年)"] = tot + r["回収しきれない額(億円/年)"]
    return r


def main():
    import warnings
    warnings.filterwarnings("ignore")
    Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
    Ks = Z["K"]
    years = PR.YEARS
    sc = PR.SCENARIOS["主"]
    kby = {y: CB.kappa_eff(MO.inputs_future(PR.scenario_year(y, sc), sc), Ks) for y in years} if PR.KAPPA_MODE == "energy" else None
    jobs, paths = [], []
    for name, key, mode, kw in CELLS:
        if not any(k.startswith(f"主|{key}|") for k in Z.files):
            print("π の曲線がない:", key)
            continue
        for P in P_GRID:
            Kt = EN.path(pi_curves(Z, key, P, years), Ks, P, kappa_by_year=kby)
            paths.append({"払い方": name, "容量価格(円/kW)": P, **{f"量 {t}": Kt[t] for t in (2030, 2035, 2040, 2045)}})
            for y in YEARS_EVAL:
                jobs.append((name, key, mode, kw, P, y, float(Kt[y])))
    print(f"計算の数 {len(jobs)}", flush=True)
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "6")), initializer=_init) as ex:
        rows = list(ex.map(_solve, jobs, chunksize=1))
    T = pd.DataFrame(rows).merge(pd.DataFrame(paths), on=["払い方", "容量価格(円/kW)"], how="left")
    T.to_csv(os.path.join(PROC, "eqm_capacity_price_burden.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    col = "需要家の負担（主、回収しきれない額も払う）(億円/年)"
    print(T.pivot_table(index=["年", "容量価格(円/kW)"], columns="払い方", values=col).round(0).to_string())
    print(T.pivot_table(index=["年", "容量価格(円/kW)"], columns="払い方", values="蓄電池（万kW）").round(1).to_string())
    for (y, name), g in T.groupby(["年", "払い方"]):
        b = g.loc[g[col].idxmin()]
        print(f"{y} {name}: 負担が最小の容量価格 {b['容量価格(円/kW)']:,.0f}円（負担 {b[col]:,.0f}億円、蓄電池 {b['蓄電池（万kW）']:.1f}万kW）")
    figure(T)


def figure(T, col="需要家の負担（主、回収しきれない額も払う）(億円/年)"):
    """容量価格と需要家の負担（2035年・2040年）。線は払い方、丸は負担が最小の容量価格"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
    plt.rcParams["font.size"] = 11
    ink, muted = "#1F2A3A", "#6B7480"
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]          # 検証済みの5色（固定の順）
    names = [c[0] for c in CELLS]
    fig, axes = plt.subplots(1, len(YEARS_EVAL), figsize=(12, 4.8))
    for ax, y in zip(axes, YEARS_EVAL):
        for i, name in enumerate(names):
            g = T[(T["年"] == y) & (T["払い方"] == name)].sort_values("容量価格(円/kW)")
            if g.empty:
                continue
            x = g["容量価格(円/kW)"] / 1e4
            ax.plot(x, g[col], color=colors[i], lw=2, ls="--" if "入札" in name else "-", label=name)
            b = g.loc[g[col].idxmin()]
            ax.plot(b["容量価格(円/kW)"] / 1e4, b[col], "o", ms=8, color=colors[i], mec="white", mew=2)
        ax.axvline(1.4972, color=muted, lw=1, ls=":")
        ax.text(1.4972, ax.get_ylim()[1], " 現行 14,972円", color=muted, fontsize=9, va="top")
        ax.set_title(f"{y}年", color=ink, fontsize=12, loc="left")
        ax.set_xlabel("2030年度以降の容量価格（万円/kW）", color=ink)
        ax.grid(axis="y", color="#E3E1DA", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("需要家の負担（億円/年）", color=ink)
    axes[-1].legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.01, -0.02, "負担＝スポットの支払い（FIT/FIP の電源の分を除く）＋補填＋契約＋容量市場の支払い（容量価格×529万kW）＋回収しきれない額。丸は負担が最小の容量価格。蓄電池の量はその容量価格での均衡",
             fontsize=8.5, color=muted)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "hokkaido", "eqm_capacity_price_burden.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print("wrote", out)


if __name__ == "__main__":
    main()
