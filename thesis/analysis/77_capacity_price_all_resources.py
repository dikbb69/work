#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""容量価格と需要家の負担（原子力・水力の収入の要件も入れる版）

analysis/75 は火力の収入の要件だけを置いていた。ここでは原子力（泊）と一般水力にも「運転を続けるのに要る収入」を置き、
容量価格 P のもとで要件に届かない分を、払い方に応じて
  - 補填・契約（基準）: 市場の外の契約で、その電源にだけ払う
  - すべてスポット（全国の上乗せ）: 上乗せ α を、すべての電源の要件を満たすまで上げる（α は全電源に共通）
で払ったときの需要家の負担を出し、負担が最小の容量価格を探す。
  負担＝スポットの支払い（FIT/FIP の電源の分を除く）＋補填＋契約（火力・原子力・水力）＋容量市場の支払い（P×北海道の調達量）
電源ごとの収入＝スポットの粗利（価格−燃料費）×発電量＋P×調整係数×設備。要件と調整係数の根拠は model/params.py の NUC_REQ ほか。
感応度: 原子力の要件を全部の費用（建設費を含む）にする、揚水も要件に入れる、調達量600万kW。
蓄電池の量は、火力の要件だけで解いた参入の経路の K*(P)（analysis/75 と同じ）。原子力・水力のための上乗せで蓄電池の価値が上がる効果は入れていない。
出力: data/processed/eqm_capacity_price_all_resources.csv、figures/hokkaido/eqm_capacity_price_all_resources.png
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, calibrate as CB, entry as EN, merit as MO

PROC = os.path.join(ROOT, "data", "processed")
P_GRID = [0.0, 5_000.0, 10_000.0, 12_500.0, 14_972.0, 16_000.0, 17_000.0, 18_000.0, 19_000.0, 20_000.0, 20_911.0, 25_000.0]
YEARS_EVAL = (2035, 2040)
CELLS = [("補填・契約（基準）", "capacity_退出あり", "capacity", {}),
         ("すべてスポット（全国の上乗せ）", "all_spot_退出あり", "spot", dict(losses="spot"))]
VARIANTS = {"主（原子力は続ける費用）": dict(nuc="続ける費用（主）", pump=False),
            "原子力は全部の費用": dict(nuc="全部の費用", pump=False),
            "揚水も入れる": dict(nuc="続ける費用（主）", pump=True)}
ALPHA_MAX = 40.0
_CAL = None
_BS = None


def pi_curves(Z, key, P, years):
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


def nuc_cap(y):
    """運転している泊の出力（送電端、MW）。3号は2027年10月から、1号は FY2032 から"""
    return PR.NUC["泊3号"] * (y >= 2028) + PR.NUC["泊1号"] * (y >= 2032)


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
    name, key, mode, kw, P, y, K = job
    sc = PR.SCENARIOS["主"]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc)
    R, p, a, w, chg, dis = _BS.solve_at(I, _CAL, mode, K, P=P, adequacy=True, **kw)
    yrs = I["D"].shape[0] / 365.25
    oku = lambda x: float(np.asarray(x).sum() * 1_000 / yrs / 1e8)
    p0, v = R["p0"], I["v"]
    floor = p0 <= PR.FLOOR + 1e-6
    price = lambda al: np.where(floor, p0, p0 + (al - 1.0) * np.maximum(p0 - v, 0.0))
    fit = I["S"] + I["W"] - R["curt"] + I["Bm"] + I["G"]
    net_load = I["D"] - fit
    capnu = nuc_cap(y)
    q_hy = sum(PR.HYDRO_CAP[k] * PR.KAPPA_HYDRO[k] for k in PR.HYDRO_CAP)
    groups = {"原子力": dict(out=I["N"], vc=PR.NUC_VC, q=capnu * PR.KAPPA_NUC),
              "一般水力": dict(out=I["Hy"], vc=0.0, q=q_hy, req=PR.HYDRO_REQ * sum(PR.HYDRO_CAP.values()) * 1_000 / 1e8),
              "揚水": dict(out=I["pump"], vc=0.0, q=PR.PUMP_CAP * PR.KAPPA_PUMP, req=PR.HYDRO_REQ * PR.PUMP_CAP * 1_000 / 1e8)}
    margin = lambda g, al: oku((price(al) - groups[g]["vc"]) * groups[g]["out"])
    cap_pay = lambda g: P * groups[g]["q"] * 1_000 / 1e8
    base = {"払い方": name, "容量価格(円/kW)": P, "年": y, "蓄電池（万kW）": K, "α（火力の要件だけ）": a,
            "補填(億円/年)": R["mw"] / 1e8, "火力の契約(億円/年)": R["contract"] / 1e8,
            "原子力の粗利 α＝火力(億円/年)": margin("原子力", a), "一般水力の粗利 α＝火力(億円/年)": margin("一般水力", a),
            "揚水の粗利 α＝火力(億円/年)": margin("揚水", a)}
    rows = []
    for vlab, vv in VARIANTS.items():
        gs = ["原子力", "一般水力"] + (["揚水"] if vv["pump"] else [])
        req = {"原子力": PR.NUC_REQ[vv["nuc"]] * 0.70 * 8760 * capnu * 1_000 / 1e8,
               "一般水力": groups["一般水力"]["req"], "揚水": groups["揚水"]["req"]}
        if mode == "capacity":                                  # 届かない分は、その電源にだけ契約で払う
            al = a
            short = {g: max(req[g] - margin(g, al) - cap_pay(g), 0.0) for g in gs}
        else:                                                   # 上乗せを、すべての電源の要件を満たすまで上げる
            al = a
            for g in gs:
                if margin(g, al) + cap_pay(g) < req[g]:
                    lo, hi = al, ALPHA_MAX
                    if margin(g, hi) + cap_pay(g) < req[g]:
                        al = ALPHA_MAX
                        continue
                    for _ in range(40):
                        mid = (lo + hi) / 2
                        lo, hi = (lo, mid) if margin(g, mid) + cap_pay(g) >= req[g] else (mid, hi)
                    al = max(al, hi)
            short = {g: max(req[g] - margin(g, al) - cap_pay(g), 0.0) for g in gs}
        spot = oku(price(al) * net_load)
        r = {**base, "要件の置き方": vlab, "α（すべての電源の要件）": al, "スポットの支払い（FIT/FIP の分を除く）(億円/年)": spot}
        for g in ("原子力", "一般水力", "揚水"):
            r[f"{g}の要件(億円/年)"] = req[g] if g in gs else np.nan
            r[f"{g}の収入（粗利＋容量）(億円/年)"] = margin(g, al) + cap_pay(g)
            r[f"{g}の契約(億円/年)"] = short.get(g, 0.0)
        for qlab, q in (("主", PR.Q_CAPACITY), ("感応度", 600.0)):
            capm = P * q * 1e4 / 1e8
            r[f"容量市場の支払い（{qlab} {q:.0f}万kW）(億円/年)"] = capm
            r[f"需要家の負担（{qlab}）(億円/年)"] = spot + r["補填(億円/年)"] + r["火力の契約(億円/年)"] + sum(short.values()) + capm
        rows.append(r)
    return rows


def figure(T):
    """容量価格と需要家の負担。補填・契約（主）と、すべてスポットの3つの要件の置き方。揚水も入れる場合は低い容量価格で縦軸の外に出る"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
    plt.rcParams["font.size"] = 11
    ink, muted = "#1F2A3A", "#6B7480"
    lines = [("補填・契約（基準）", "主（原子力は続ける費用）", "#2a78d6", "-", "補填・契約"),          # 検証済みの色の順（1〜4番）
             ("すべてスポット（全国の上乗せ）", "主（原子力は続ける費用）", "#eb6834", "-", "すべてスポット"),
             ("すべてスポット（全国の上乗せ）", "原子力は全部の費用", "#1baf7a", "--", "すべてスポット（原子力は全部の費用）"),
             ("すべてスポット（全国の上乗せ）", "揚水も入れる", "#eda100", "-.", "すべてスポット（揚水も入れる）")]
    col = "需要家の負担（主）(億円/年)"
    fig, axes = plt.subplots(1, len(YEARS_EVAL), figsize=(12, 4.8), sharey=True)
    for ax, y in zip(axes, YEARS_EVAL):
        for name, vlab, color, ls, lab in lines:
            g = T[(T["年"] == y) & (T["払い方"] == name) & (T["要件の置き方"] == vlab)].sort_values("容量価格(円/kW)")
            ax.plot(g["容量価格(円/kW)"] / 1e4, g[col], color=color, lw=2, ls=ls, label=lab)
            b = g.loc[g[col].idxmin()]
            ax.plot(b["容量価格(円/kW)"] / 1e4, b[col], "o", ms=8, color=color, mec="white", mew=2)
        ax.set_ylim(1_600, 3_300)
        ax.axvline(1.4972, color=muted, lw=1, ls=":")
        ax.text(1.4972, 1_620, " 現行 14,972円", color=muted, fontsize=9, va="bottom")
        v0 = T[(T["年"] == y) & (T["払い方"] == "すべてスポット（全国の上乗せ）") & (T["要件の置き方"] == "揚水も入れる") & (T["容量価格(円/kW)"] == 0.0)][col]
        if len(v0):
            ax.text(0.02, 3_250, f"揚水も入れる: 容量価格0で{float(v0.iloc[0]):,.0f}億円", color=muted, fontsize=8.5, va="top")
        ax.set_title(f"{y}年", color=ink, fontsize=12, loc="left")
        ax.set_xlabel("2030年度以降の容量価格（万円/kW）", color=ink)
        ax.grid(axis="y", color="#E3E1DA", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axes[0].set_ylabel("需要家の負担（億円/年）", color=ink)
    axes[-1].legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.01, -0.02, "原子力（泊）・一般水力（感応度で揚水）にも運転を続ける収入の要件を置く。届かない分は、補填・契約ではその電源にだけ払い、すべてスポットでは全電源共通の上乗せで取り戻す。"
             "負担＝スポットの支払い（FIT/FIP の分を除く）＋補填＋契約＋容量価格×529万kW。丸は負担が最小の容量価格", fontsize=8.5, color=muted)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "hokkaido", "eqm_capacity_price_all_resources.png")
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print("wrote", out)


def main():
    import warnings
    warnings.filterwarnings("ignore")
    Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
    Ks = Z["K"]
    sc = PR.SCENARIOS["主"]
    kby = {y: CB.kappa_eff(MO.inputs_future(PR.scenario_year(y, sc), sc), Ks) for y in PR.YEARS} if PR.KAPPA_MODE == "energy" else None
    jobs = []
    for name, key, mode, kw in CELLS:
        for P in P_GRID:
            Kt = EN.path(pi_curves(Z, key, P, PR.YEARS), Ks, P, kappa_by_year=kby)
            for y in YEARS_EVAL:
                jobs.append((name, key, mode, kw, P, y, float(Kt[y])))
    print(f"計算の数 {len(jobs)}", flush=True)
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "4")), initializer=_init) as ex:
        rows = [r for rs in ex.map(_solve, jobs, chunksize=1) for r in rs]
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(PROC, "eqm_capacity_price_all_resources.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    col = "需要家の負担（主）(億円/年)"
    for vlab in VARIANTS:
        print("==", vlab)
        print(T[T["要件の置き方"] == vlab].pivot_table(index=["年", "容量価格(円/kW)"], columns="払い方", values=[col, "α（すべての電源の要件）"]).round(1).to_string())
    for (y, name, vlab), g in T.groupby(["年", "払い方", "要件の置き方"]):
        b = g.loc[g[col].idxmin()]
        print(f"{y} {name} {vlab}: 負担が最小の容量価格 {b['容量価格(円/kW)']:,.0f}円（{b[col]:,.0f}億円）")
    figure(T)


def replot():
    figure(pd.read_csv(os.path.join(PROC, "eqm_capacity_price_all_resources.csv")))


if __name__ == "__main__":
    replot() if os.environ.get("REPLOT") == "1" else main()
