#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIT/FIP 情報公表用ウェブサイト B表（市町村別導入容量）から都道府県・エリア別の
太陽光・風力 導入容量の四半期系列を構築する

入力: thesis/data/raw/fit_b/B_city*.xls(x)（2014/6〜2025/12・四半期、ユーザー取得）
出力: thesis/data/processed/fit_capacity_pref_quarterly.csv（都道府県別）
      thesis/data/processed/area_capacity_series.csv（北海道・東北・九州エリア別、月次補間つき）

方法: 表B②－１（新規認定分）＋表B②－２（移行認定分）の導入容量(kW)を合算。
      列位置は年代・シートで異なるためヘッダー行のグループ名（太陽光/風力発電設備）から特定。
      太陽光=10kW未満+10kW以上、風力=20kW未満+20kW以上（「うち〜」列は除外）
限界: FIT/FIP認定設備のみ（非FIT設備は含まない）。2016/9・2019/6は欠落四半期（線形補間）。
"""
import glob
import os
import re

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw", "fit_b")
OUT = os.path.join(ROOT, "data", "processed")

PREFS = ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県",
         "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県",
         "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府",
         "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県",
         "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県",
         "鹿児島県", "沖縄県"]
PREF_RE = re.compile("^(" + "|".join(PREFS) + ")")

AREAS = {
    "hokkaido": ["北海道"],
    "tohoku": ["青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "新潟県"],
    "kyushu": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県"],
}


def find_block_cols(raw):
    """ヘッダー行から太陽光・風力の容量列インデックスを特定"""
    hdr_group = None
    for r in range(min(6, len(raw))):
        vals = raw.iloc[r].astype(str)
        if vals.str.contains("太陽光発電設備").any() and vals.str.contains("風力発電設備").any():
            hdr_group = r
            break
    assert hdr_group is not None, "グループヘッダー行が見つからない"
    groups = raw.iloc[hdr_group].fillna("").astype(str)
    sub = raw.iloc[hdr_group + 1].fillna("").astype(str)

    def gcol(name):
        idx = [i for i, v in enumerate(groups) if name in v]
        return idx[0]

    s0 = gcol("太陽光発電設備")
    w0 = gcol("風力発電設備")
    h0 = gcol("水力発電設備")
    solar_cols = [i for i in range(s0, w0) if ("10kW未満" in sub[i]) or ("10kW以上" in sub[i])]
    wind_cols = [i for i in range(w0, h0) if ("20kW未満" in sub[i]) or ("20kW以上" in sub[i])]
    assert len(solar_cols) == 2 and len(wind_cols) == 2, f"列特定失敗 solar={solar_cols} wind={wind_cols}"
    return hdr_group, solar_cols, wind_cols


def parse_sheet(f, sheet):
    raw = pd.read_excel(f, sheet_name=sheet, header=None)
    hdr, scols, wcols = find_block_cols(raw)
    df = raw.iloc[hdr + 2:].copy()
    name = df[0].astype(str).str.strip()
    m = name.str.extract(PREF_RE, expand=False)
    df = df[m.notna()].copy()
    df["pref"] = m[m.notna()]
    for c in scols + wcols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    g = df.groupby("pref").agg(solar_kw=(scols[0], "sum"), _s2=(scols[1], "sum"),
                               wind_kw=(wcols[0], "sum"), _w2=(wcols[1], "sum"))
    g["solar_kw"] += g.pop("_s2")
    g["wind_kw"] += g.pop("_w2")
    return g


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(RAW, "*B_city*.xls*"))):
        m = re.search(r"(20\d{4})", os.path.basename(f))
        date = pd.Timestamp(int(m.group(1)[:4]), int(m.group(1)[4:6]), 1) + pd.offsets.MonthEnd(0)
        tot = None
        for sheet in ["表B②－１", "表B②－２"]:
            g = parse_sheet(f, sheet)
            tot = g if tot is None else tot.add(g, fill_value=0)
        tot = tot.reset_index()
        tot["date"] = date
        rows.append(tot)
        print(f"{os.path.basename(f)}: 北海道 太陽光{tot.set_index('pref').loc['北海道','solar_kw']/1e4:.1f}万kW"
              f" 風力{tot.set_index('pref').loc['北海道','wind_kw']/1e4:.1f}万kW")
    df = pd.concat(rows, ignore_index=True)
    df = df.sort_values(["date", "pref"])[["date", "pref", "solar_kw", "wind_kw"]]
    df.to_csv(os.path.join(OUT, "fit_capacity_pref_quarterly.csv"), index=False)

    # エリア集計 → 月次線形補間
    out = []
    for area, prefs in AREAS.items():
        a = df[df["pref"].isin(prefs)].groupby("date")[["solar_kw", "wind_kw"]].sum()
        idx = pd.date_range(a.index.min(), a.index.max(), freq="ME")
        a = a.reindex(idx).interpolate(method="time")
        a["area"] = area
        out.append(a.reset_index(names="date"))
    pd.concat(out, ignore_index=True).to_csv(os.path.join(OUT, "area_capacity_series.csv"), index=False)
    print("saved area_capacity_series.csv")

    # 検証アンカー
    hk = df[df["pref"] == "北海道"].set_index("date")
    for d, lab, ref in [("2016-12-31", "北海道風力 2016年末", "JWPA 2010年代 約36万kW"),
                        ("2023-12-31", "北海道風力 2023年末", "JWPA 約83万kW"),
                        ("2024-12-31", "北海道風力 2024年末", "JWPA 約128万kW"),
                        ("2025-03-31", "北海道太陽光 2025年3月末", "接続量 約236万kW")]:
        if pd.Timestamp(d) in hk.index:
            col = "wind_kw" if "風力" in lab else "solar_kw"
            print(f"  検証: {lab} = {hk.loc[pd.Timestamp(d), col]/1e4:.1f}万kW（参照: {ref}）")


if __name__ == "__main__":
    main()
