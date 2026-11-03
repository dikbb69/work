#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの頑健性（付録C 表C.2）の集計（2026-11-04）
需給・価格の前提を1つだけ動かして経路まで解いた項目（data/processed/robust/<名前>/）と、参入とファイナンスの前提を動かした項目
（v2_robustness_entry.csv）を、基準シナリオ（simple_entry.csv、容量価格14,972円）と並べる。
列: 3つの場合ごとの 2030・2035・2040年の量、98.8万kW を超える最初の年、退出した号機、2040年の基準との差、3つの場合の量の順が保たれるか。
"""
import glob
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
sys.path.insert(0, HERE)
P = 14_972.0
BASE_K = 98.8                                                   # 既設＋LTDA（万kW）
CASES = {"上乗せ": "スポット回収", "上乗せ_赤字は外": "運転損失だけ補填", "燃料費": "燃料費入札"}
ENTRY_CASES = {"スポットで回収（基準）": "スポット回収", "運転赤字だけ市場外": "運転損失だけ補填", "すべて市場外": "燃料費入札"}
LABEL = {                                                       # 項目の名前（論文の言葉）
    "selfcons_split": "太陽光の自家消費を分ける", "link_margin": "北本の上限から年間計画のマージンを引く（両方向）",
    "nuc3": "原子力 泊3基", "demand9000": "需要 OCCTO 9,000億kWh ケースの値", "demandplan": "需要の経路を計画の経路に",
    "th_plus3": "東北の価格 +3円/kWh", "th_minus3": "東北の価格 −3円/kWh", "fuel12": "燃料費 +20%", "fuel08": "燃料費 −20%",
    "req08": "足元の総収入×0.8", "req12": "足元の総収入×1.2", "mr2": "マストラン2台", "mr0": "マストランなし",
    "prop": "上乗せを燃料費に比例", "link60": "北本 両方向60万kW", "noupgrade": "北本の増強なし",
    "link333": "北本の東北への流れ 実績（333MW）", "link055": "北本の東北への流れ 運用容量の55%",
    "link100": "北本の東北への流れ 運用容量いっぱい", "retire45": "火力を運開45年で廃止",
    "th_comove": "東北の価格が北海道の再エネに連動",
}


def first_over(row):
    ys = [int(c.split()[1]) for c in row.index if c.startswith("量 ") and row[c] > BASE_K + 1e-6]
    return min(ys) if ys else None


def summarize(E, item, label, exits):
    rows = []
    for key, name in CASES.items():
        r = E[(E["場合"] == key) & (E["容量価格(円/kW)"] == P)]
        if r.empty:
            continue
        r = r.iloc[0]
        rows.append({"区分": "需給・価格（経路）", "項目": item, "名前": label, "場合": name,
                     "量 2030": r["量 2030"], "量 2035": r["量 2035"], "量 2040": r["量 2040"],
                     "98.8万kW を超える最初の年": first_over(r), "退出": exits.get(key, "")})
    return rows


def exits_of(d, suffix):
    f = os.path.join(d, f"simple_exit_years{suffix}.csv")
    if not os.path.exists(f):
        return {}
    X = pd.read_csv(f, encoding="utf-8-sig")
    if X.empty:
        return {}
    col = "場合" if "場合" in X else "運転の赤字の払い方"
    m = {"spot": "上乗せ", "outside": "上乗せ_赤字は外"}
    out = {}
    for c, g in X.groupby(col):
        out[m.get(c, c)] = "・".join(f"{n}（{int(y)}）" for n, y in zip(g["号機"], g["退出の年"]))
    out.setdefault("燃料費", out.get("上乗せ", ""))
    return out


def main():
    rows = summarize(pd.read_csv(os.path.join(PROC, "simple_entry.csv"), encoding="utf-8-sig"), "base", "基準シナリオ",
                     exits_of(PROC, ""))
    for r in rows:
        r["区分"] = "基準"
    for d in sorted(glob.glob(os.path.join(PROC, "robust", "*"))):
        item = os.path.basename(d)
        fs = glob.glob(os.path.join(d, "simple_entry*.csv"))
        if item not in LABEL or not fs:
            continue
        suffix = os.path.basename(fs[0])[len("simple_entry"):-len(".csv")]
        rows += summarize(pd.read_csv(fs[0], encoding="utf-8-sig"), item, LABEL[item], exits_of(d, suffix))
    R = pd.read_csv(os.path.join(PROC, "v2_robustness_entry.csv"), encoding="utf-8-sig")
    for _, r in R[R["頑健性"] != "基準"].iterrows():
        name = r["頑健性"].replace("実行できる比", "実現率")
        rows.append({"区分": "参入とファイナンス", "項目": r["頑健性"], "名前": name, "場合": ENTRY_CASES.get(r["場合"], r["場合"]),
                     "量 2030": r["量 2030"], "量 2035": r["量 2035"], "量 2040": r["量 2040"],
                     "98.8万kW を超える最初の年": r["98.8万kW を超える最初の年"], "退出": ""})
    T = pd.DataFrame(rows)
    base = T[T["区分"] == "基準"].set_index("場合")["量 2040"]
    T["2040年の基準との差"] = T["量 2040"] - T["場合"].map(base)
    order = list(CASES.values())
    piv = T.pivot_table(index="項目", columns="場合", values="量 2040", sort=False)[order]
    keep = ((piv[order[0]] >= piv[order[1]] - 0.05) & (piv[order[1]] >= piv[order[2]] - 0.05))
    T["3つの場合の量の順が保たれる"] = T["項目"].map(keep)
    T.to_csv(os.path.join(PROC, "v2_robustness_summary.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(T.round(1).to_string(index=False))
    print("\n2040年の量の範囲（基準以外）:")
    print(T[T["区分"] != "基準"].groupby("場合", sort=False)["量 2040"].agg(["min", "max"]).round(1).to_string())
    print("順が保たれない項目:", sorted(set(T.loc[~T["3つの場合の量の順が保たれる"].astype(bool), "名前"])))


if __name__ == "__main__":
    main()
