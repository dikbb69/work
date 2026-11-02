#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデルの再計算（notes/38 §1.3、2026-11-03）: 簡易見積（旧の表6.4 の合成、notes/36 §9 (g)）と本計算の差の分解（2040年、容量価格14,972円）
簡易見積: 旧の主から、太陽光は420→600万kW の傾きで698.5万kW まで外挿、風力は太陽光420万kW での400→720万kW の傾きで641万kW 相当まで下げ、足し算で合わせる。
本計算の新しい表6.4 の点（太陽光698.5・風力720、太陽光420・風力615）で、太陽光の効きと風力の効きに分けて比べる。
入力: data/processed/simple_source_scenarios_v2draft.csv（初稿の旧の主の表6.4 の写し）、data/processed/simple_source_scenarios.csv（新）
"""
import pandas as pd, numpy as np
col = "市場だけで入る量(万kW)"
O = pd.read_csv("data/processed/simple_source_scenarios_v2draft.csv"); O = O[O["年"] == 2040]
N = pd.read_csv("data/processed/simple_source_scenarios.csv"); N = N[N["年"] == 2040]
om = {"上乗せあり（主）": "スポットで回収（主）", "上乗せあり（マストランの赤字はスポットの外で精算）": "赤字だけ市場外", "一般的な方法（燃料費で入札）": "すべて市場外"}
O["場合"] = O["場合"].map(om)
g = lambda D, s, c: float(D[(D["シナリオ"] == s) & (D["場合"] == c)][col].iloc[0])
for c in om.values():
    old_main = g(O, "主", c); s600 = g(O, "太陽光 600万kW（上振れ）", c); w400 = g(O, "風力 400万kW（9,000億kWh ケース）", c)
    sl_s = (s600 - old_main) / 180.0; sl_w = (old_main - w400) / 320.0
    est_add = old_main + sl_s * (698.48 - 420) - sl_w * (720 - 641)
    new_main = g(N, "主", c); s698w720 = g(N, "風力 720万kW（旧の主）", c); s420w615 = g(N, "太陽光 420万kW（旧の主）", c)
    s588 = g(N, "太陽光 588万kW（エネ基の下限）", c); s809 = g(N, "太陽光 809万kW（エネ基の上限）", c); w418 = g(N, "風力 418万kW（エネ基の下限）", c)
    print(f"== {c}")
    print(f" 旧の主 {old_main:.1f}; 旧の表 太陽光600 {s600:.1f}（傾き {sl_s:.3f}/万kW）; 風力400 {w400:.1f}（傾き {sl_w:.3f}/万kW）; 足し算の見積 {est_add:.1f}")
    print(f" 新しい主 {new_main:.1f}; 太陽光698・風力720 {s698w720:.1f}; 太陽光420・風力615 {s420w615:.1f}")
    print(f"  太陽光 420→698（風力720）: {s698w720 - old_main:+.1f}（線形の外挿 {sl_s * (698.48 - 420):+.1f}、差 {s698w720 - old_main - sl_s * (698.48 - 420):+.1f}）")
    print(f"  風力 720→615（太陽光698）: {new_main - s698w720:+.1f}（簡易見積は641相当で {-sl_w * (720 - 641):+.1f}、差 {new_main - s698w720 + sl_w * (720 - 641):+.1f}）")
    print(f"  風力 720→615（太陽光420）: {s420w615 - old_main:+.1f}  ※太陽光420 の自家消費の規則は新（系統400.2）")
    print(f"  太陽光 588→698→809 の傾き（風力615）: {(new_main - s588) / (698.48 - 588.07):.3f}・{(s809 - new_main) / (808.88 - 698.48):.3f}/万kW;  420→588: {(s588 - s420w615) / (588.07 - 420):.3f}")
    print(f"  風力 418→615・615→720 の傾き（太陽光698）: {(new_main - w418) / (615.12 - 417.6):.3f}・{(s698w720 - new_main) / (720 - 615.12):.3f}/万kW")

# 下限・上限: 簡易見積の作り方（太陽光は旧の表の420→600 の傾きで外挿、風力は発電量をモデルの設備利用率で設備に直して旧の表の傾き）と、
# 新しい表6.4 の点から足し算した値（主＋太陽光だけ動かした差＋風力だけ動かした差）を、経路の値と比べる
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from model import params as PR
CF_MODEL = 0.2743                                               # モデルの風力の時間別の形の設備利用率（notes/39 §0.2）
for scen, case, srow, wrow in (("エネ基の下限", "下限", "太陽光 588万kW（エネ基の下限）", "風力 418万kW（エネ基の下限）"),
                               ("エネ基の上限", "上限", "太陽光 809万kW（エネ基の上限）", "風力 813万kW（エネ基の上限）")):
    a = PR.e7_y2040(f"{case}" if case in ("下限", "上限") else case)
    w_eq = (a["wind_on"] * PR.CF_WIND_ON + a["wind_off"] * PR.CF_WIND_OFF) / CF_MODEL / 10          # 万kW 相当
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "processed", f"simple_entry_{scen}.csv")
    E = pd.read_csv(f) if os.path.exists(f) else None
    print(f"== {scen}: 太陽光 {a['solar'] / 10:.1f}・風力 {a['wind'] / 10:.1f}万kW（モデルの設備利用率で発電量をそろえると {w_eq:.0f}万kW 相当）")
    for c, key in zip(om.values(), ("上乗せ", "上乗せ_赤字は外", "燃料費")):
        old_main = g(O, "主", c); s600 = g(O, "太陽光 600万kW（上振れ）", c); w400 = g(O, "風力 400万kW（9,000億kWh ケース）", c)
        sl_s = (s600 - old_main) / 180.0
        w1155 = g(O, "風力 1,155万kW（洋上風力産業ビジョンの下限）", c)
        sl_w = (old_main - w400) / 320.0 if w_eq < 720 else (w1155 - old_main) / 435.0   # 720万kW の上は720→1,155 の傾き
        est = old_main + sl_s * (a["solar"] / 10 - 420) + sl_w * (w_eq - 720)
        nm = g(N, "主", c); add_new = nm + (g(N, srow, c) - nm) + (g(N, wrow, c) - nm)
        act = float(E[(E["場合"] == key) & (E["容量価格(円/kW)"] == 14972.0)]["量 2040"].iloc[0]) if E is not None else float("nan")
        print(f"  {c}: 簡易見積の作り方 {est:.1f}、新しい表6.4 の足し算 {add_new:.1f}（太陽光だけ {g(N, srow, c):.1f}、風力だけ {g(N, wrow, c):.1f}）、経路 {act:.1f}")
