#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需給調整市場のレントの上限（単位の訂正版）: ΔkW 価格を 円/ΔkW・30分 として年額に換算する

28_equilibrium_surface.py の上限バンド（eprx_rent_cap.csv）は ΔkW 価格を 円/ΔkW·h とみなして 8,760 時間を掛けていた。
需給調整市場の約定価格・上限価格は 円/ΔkW・30分 で公表される（一次調整力の上限 15.00円/ΔkW・30分 など）ので、
1時間あたりは2倍になる。本スクリプトは同じ格子を、1kW あたりの物理上限（供出できる ΔkW は設備 1kW まで）で抑えて計算し直す。
  上限 = min(Q/K, 1) × 2 × p30 × 8,760   （円/kW-年。p30 は 円/ΔkW・30分）
Q（北海道の調達量）は未取得のため 10・30・50万kW の仮定、p30 は 5円（火力並み）と15円（一次調整力の上限）。
出力: data/processed/eprx_rent_cap_v2.csv
限界: 一年中すべての時間で全量が落札し、その価格が続くとした上限であり、レントの実測ではない。
"""
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
rows = []
for Q, p30 in [(10, 5.0), (10, 15.0), (30, 5.0), (30, 15.0), (50, 5.0), (50, 15.0)]:
    r = {"調達量Q(万kW)": Q, "ΔkW価格(円/ΔkW・30分)": p30, "1時間あたり(円/ΔkW·h)": 2 * p30}
    for K in (25, 50, 100, 200):
        r[f"K={K}万kW"] = round(min(Q / K, 1.0) * 2 * p30 * 8760)
    rows.append(r)
out = pd.DataFrame(rows)
out.to_csv(os.path.join(ROOT, "data", "processed", "eprx_rent_cap_v2.csv"), index=False, encoding="utf-8-sig")
print(out.to_string(index=False))
