#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需要家の負担の分解: スポット回収の場合と容量回収の場合で、スポットの約定総額の差が誰に渡るか

2つの場合を同じ年・同じ蓄電池の量（先に入っている量）で解き、時間別の価格の差 Δp と電源別の発電量から、差を次に分ける。
  - 火力（要件の対象）: 上乗せで回収する固定費。容量回収の場合は不足額 M を別の契約で払う
  - 火力（LTDA・アンモニア混焼の落札分・対象外の火力）
  - 原子力・水力（大型）: 発電事業者への移転
  - FIT/FIP の電源（太陽光・風力（抑制後）・バイオマス・地熱）: 回避可能費用・参照価格がスポットに連動するので、賦課金・プレミアムの減少で需要家に戻る（全量が FIT/FIP の対象と仮定した上限）
  - 蓄電池・揚水・北本: 残り
需要家の正味の負担の差 ≈ 約定総額の差 − FIT/FIP で戻る分 − 容量回収の場合に別に払う不足額 M
2つの場合は同じ年・同じ需要どうしの比較なので、差はすべて1kWh あたりの価格の差である（1kWh あたりの値も出す）
出力: data/processed/eqm_burden_split.csv
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, balance as B, price as PZ, calibrate as CB, battery as BT, entry as EN, merit as MO

PROC = os.path.join(ROOT, "data", "processed")


def solve_at(I, cal, mode, K, P=14_972.0, adequacy=False, **kw):
    """蓄電池 K 万kW まで1万kW ずつ入れた状態の需給・価格。kw は払い方の変種（運転の赤字の扱い、回収の仕方）。
    adequacy: 今の供給力の余裕を保つのに要らない火力は退出する（蓄電池は κ×容量で数える。マストランと LTDA の火力は残す）"""
    all_units = B.fleet(I["year"])
    need = BT.required_margin(I, cal)
    units = all_units
    nd = I["D"].shape[0]
    chg, dis = np.zeros((nd, 24)), np.zeros((nd, 24))
    rr = np.arange(nd)[:, None]
    done = 0.0
    while True:
        if adequacy:
            units, _ = BT.keep_minimum(I, all_units, need, done)
        R, p, a, w = BT.evaluate(I, units, chg, dis, cal, mode, P, **kw)
        if done >= K - 1e-9:
            return R, p, a, w, chg, dis
        st = min(1.0, K - done)
        c4, d4, ok = BT._schedule(p, I["days"], "share")
        chg[rr[ok], c4[ok]] += st * 10.0
        dis[rr[ok], d4[ok]] += st * 10.0 * PR.ETA
        done += st


def main():
    import warnings
    warnings.filterwarnings("ignore")
    cal = CB.calibration(0.0)
    rows = []
    for sname in ("主", "原子力なし"):
        for y in (2030, 2035, 2040):
            I = MO.inputs_future(PR.scenario_year(y, PR.SCENARIOS[sname]), PR.SCENARIOS[sname])
            K = EN.preset_stock(y)
            yrs = I["D"].shape[0] / 365.25
            res = {}
            for mode in ("spot", "capacity"):
                R, p, a, w, chg, dis = solve_at(I, cal, mode, K)
                res[mode] = (R, p, a, w, chg, dis)
            (Rs, ps, a_s, w, cs, ds), (Rc, pc, _, _, cc, dc) = res["spot"], res["capacity"]
            dp = ps - pc
            oku = lambda x: float(np.asarray(x).sum() * 1_000 / yrs / 1e8)
            g = Rs["g"]
            tgt = (g * w).sum(2)
            th_all = g.sum(2) + Rs["other_out"]
            fit = I["S"] + I["W"] - Rs["curt"] + I["Bm"] + I["G"]
            r = {"シナリオ": sname, "年": y, "蓄電池（万kW）": K, "α（スポット回収）": a_s,
                 "約定総額 スポット回収(億円/年)": oku(ps * I["D"]), "約定総額 容量回収(億円/年)": oku(pc * I["D"]),
                 "約定総額の差(億円/年)": oku(dp * I["D"]),
                 "うち火力（要件の対象）": oku(dp * tgt), "うち火力（対象外・LTDA など）": oku(dp * (th_all - tgt)),
                 "うち原子力": oku(dp * I["N"]), "うち水力": oku(dp * I["Hy"]), "うち FIT/FIP の電源（戻る分の上限）": oku(dp * fit),
                 "うち揚水・蓄電池・北本ほか": oku(dp * (I["D"] - tgt - (th_all - tgt) - I["N"] - I["Hy"] - fit)),
                 "容量回収の場合の不足額 M(億円/年)": Rc["missing"] / 1e8,
                 "運転の赤字の補填 容量回収(億円/年)": Rc["mw"] / 1e8, "運転の赤字の補填 スポット回収(億円/年)": Rs["mw"] / 1e8}
            r["需要家の正味の負担の差(億円/年)"] = (r["約定総額の差(億円/年)"] - r["うち FIT/FIP の電源（戻る分の上限）"] - r["容量回収の場合の不足額 M(億円/年)"]
                                         - r["運転の赤字の補填 容量回収(億円/年)"] + r["運転の赤字の補填 スポット回収(億円/年)"])
            dem = float(I["D"].sum() / yrs / 1e6)                 # TWh（2つの場合で同じ需要）
            r["需要(TWh)"] = dem
            r["平均価格 スポット回収(円/kWh)"] = r["約定総額 スポット回収(億円/年)"] / (dem * 10)
            r["平均価格 容量回収(円/kWh)"] = r["約定総額 容量回収(億円/年)"] / (dem * 10)
            r["容量回収の M（円/kWh）"] = r["容量回収の場合の不足額 M(億円/年)"] / (dem * 10)
            r["約定総額の差（円/kWh）"] = r["約定総額の差(億円/年)"] / (dem * 10)
            r["正味の負担の差（円/kWh）"] = r["需要家の正味の負担の差(億円/年)"] / (dem * 10)
            r["約定総額の差÷M"] = r["約定総額の差(億円/年)"] / max(r["容量回収の場合の不足額 M(億円/年)"], 1e-9)
            r["FIT/FIP を引いた差÷M"] = (r["約定総額の差(億円/年)"] - r["うち FIT/FIP の電源（戻る分の上限）"]) / max(r["容量回収の場合の不足額 M(億円/年)"], 1e-9)
            rows.append(r)
            print(sname, y, flush=True)
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(PROC, "eqm_burden_split.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(T.round(1).T.to_string())
    cells(cal)
    cells(cal, adequacy=True, out_name="eqm_burden_cells_exit.csv")


CELLS = [  # (運転の赤字, 固定費, 回収の仕方, mode, kw)
    ("市場の外で補填", "スポット", "全国の火力が同じ比率で上乗せ", "spot", {}),
    ("市場の外で補填", "スポット", "北海道の火力だけが入札（東北の価格が天井）", "spot", dict(recovery="bid")),
    ("市場の外で補填", "契約", "—", "capacity", {}),
    ("スポット", "スポット", "全国の火力が同じ比率で上乗せ", "spot", dict(losses="spot")),
    ("スポット", "スポット", "北海道の火力だけが入札（東北の価格が天井）", "spot", dict(losses="spot", recovery="bid")),
    ("スポット", "契約", "全国の火力が同じ比率で上乗せ", "capacity", dict(losses="spot")),
    ("スポット", "契約", "北海道の火力だけが入札（東北の価格が天井）", "capacity", dict(losses="spot", recovery="bid")),
]


def cells(cal, adequacy=False, out_name="eqm_burden_cells.csv"):
    """2×2（運転の赤字をどこで払うか × 固定費をどこで払うか）の各マスの、火力の収入の内訳と需要家の支払い。
    比べる基準は「運転の赤字は市場の外で補填・固定費は契約」（主の容量回収）。同じ年・同じ蓄電池の量（先に入っている量）・同じ需要。
    adequacy: 要らない火力は退出する前提（2026-10-26 から主）"""
    rows = []
    for y in (2030, 2035, 2040):
        sc = PR.SCENARIOS["主"]
        I = MO.inputs_future(PR.scenario_year(y, sc), sc)
        K = EN.preset_stock(y)
        yrs = I["D"].shape[0] / 365.25
        oku = lambda x: float(np.asarray(x).sum() * 1_000 / yrs / 1e8)
        dem = float(I["D"].sum() / yrs / 1e6)
        base = None
        res = []
        for loss, fix, how, mode, kw in CELLS:
            R, p, a, w, chg, dis = solve_at(I, cal, mode, K, adequacy=adequacy, **kw)
            res.append((loss, fix, how, mode, kw, R, p, a, w))
            if mode == "capacity" and not kw:
                base = (R, p)
        Rb, pb = base
        for loss, fix, how, mode, kw, R, p, a, w in res:
            dp = p - pb
            fit = I["S"] + I["W"] - R["curt"] + I["Bm"] + I["G"]
            r = {"年": y, "蓄電池（万kW）": K, "運転の赤字": loss, "固定費": fix, "回収の仕方": how,
                 "α": a, "入札の上乗せ 平均(円/kWh)": R["bid"].get("markup_avg", np.nan) if R["bid"] else np.nan,
                 "平均価格(円/kWh)": oku(p * I["D"]) / (dem * 10), "夕17〜21時(円/kWh)": float(p[:, 17:21].mean()),
                 "約定総額(億円/年)": oku(p * I["D"]),
                 "火力のスポットの正味の粗利(億円/年)": MO.gm(R, p, w) / 1e8, "運転の赤字の補填(億円/年)": R["mw"] / 1e8,
                 "契約で払う額(億円/年)": R["contract"] / 1e8, "回収しきれない額(億円/年)": R["unrecovered"] / 1e8,
                 "火力の要件(億円/年)": R["req"] / 1e8}
            r["需要家の支払い（約定総額＋補填＋契約）(億円/年)"] = r["約定総額(億円/年)"] + r["運転の赤字の補填(億円/年)"] + r["契約で払う額(億円/年)"]
            r["基準との差 約定総額(億円/年)"] = oku(dp * I["D"])
            r["基準との差 うち FIT/FIP で戻る分(億円/年)"] = oku(dp * fit)
            r["基準との差 需要家の正味の負担(億円/年)"] = (r["基準との差 約定総額(億円/年)"] - r["基準との差 うち FIT/FIP で戻る分(億円/年)"]
                                            + r["運転の赤字の補填(億円/年)"] - Rb["mw"] / 1e8 + r["契約で払う額(億円/年)"] - Rb["contract"] / 1e8)
            r["基準との差 需要家の正味の負担（円/kWh）"] = r["基準との差 需要家の正味の負担(億円/年)"] / (dem * 10)
            th_rev = MO.gm(R, p, w) + R["mw"] + R["contract"]
            r["火力の収入（粗利＋補填＋契約）−要件(億円/年)"] = (th_rev - R["req"]) / 1e8
            # 回収しきれない額があるマスは、火力が要件を受け取っていないぶん安く見える。同じ収入でくらべるため、その額を市場の外で払った場合も出す
            r["基準との差 需要家の正味の負担（回収しきれない額も払う場合）(億円/年)"] = (r["基準との差 需要家の正味の負担(億円/年)"]
                                                               + (R["unrecovered"] - Rb["unrecovered"]) / 1e8)
            r["基準との差 需要家の正味の負担（回収しきれない額も払う場合）（円/kWh）"] = r["基準との差 需要家の正味の負担（回収しきれない額も払う場合）(億円/年)"] / (dem * 10)
            rows.append(r)
        print("cells", y, flush=True)
    C = pd.DataFrame(rows)
    C.to_csv(os.path.join(PROC, out_name), index=False, encoding="utf-8-sig")
    print(C.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
