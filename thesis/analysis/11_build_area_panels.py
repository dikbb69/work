#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道・東北の需給実績パネル構築（01_build_panel.py のエリア一般化）

入力: thesis/data/raw/hokkaido/  sup_dem_results_YYYY_Nq.csv|.xls（60分値MWh、2016/4-2024/3）
                                 eria_jukyu_YYYYMM_01.csv（30分値MW平均、2024/4-）
      thesis/data/raw/tohoku/    juyo_YYYY_tohoku_NQ.csv（60分値MWh、2016/4-2024/3）
                                 eria_jukyu_YYYYMM_02.csv（30分値MW平均、2024/2-）
出力: thesis/data/processed/{hokkaido,tohoku}_hourly_panel.csv

形式差の要点（九州との違い、検証コードで確認）:
  - 新形式のTIMEはコマ「開始」ラベル（九州は終端ラベル）→ そのままtsに使う
  - 連系線の符号は新旧とも「正=受電・負=域外送電」で恒等式が成立 → 九州で行った符号反転は適用しない
  - 東北は旧形式が2024/1-3も存在し新形式（2024/2-）と重複 → 旧は2024/1まで採用・新を正とする
"""
import glob
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")

PANEL_COLS = ["demand", "nuclear", "thermal", "hydro", "geothermal", "biomass",
              "solar", "solar_curt", "wind", "wind_curt", "pumped", "interconn", "battery"]

NEW_NAME_MAP = {
    "DATE": "date", "TIME": "time", "エリア需要": "demand", "原子力": "nuclear",
    "火力(LNG)": "th_lng", "火力(石炭)": "th_coal", "火力(石油)": "th_oil", "火力(その他)": "th_other",
    "火力（ＬＮＧ）": "th_lng", "火力（石炭）": "th_coal", "火力（石油）": "th_oil", "火力（その他）": "th_other",
    "水力": "hydro", "地熱": "geothermal", "バイオマス": "biomass",
    "太陽光発電実績": "solar", "太陽光出力制御量": "solar_curt",
    "風力発電実績": "wind", "風力出力制御量": "wind_curt", "揚水": "pumped",
    "蓄電池": "battery", "連系線": "interconn", "その他": "other", "合計": "total",
}
IGNORE_NEW = ("火力出力制御量", "バイオマス出力制御量")


def fiscal_year(ts):
    return ts.dt.year - (ts.dt.month < 4).astype(int)


def load_new(area_dir, code):
    """新形式（30分MW平均）→ 60分平均。TIMEは開始ラベルであることを検証の上使用"""
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, area_dir, f"eria_jukyu_*_{code}.csv"))):
        df = pd.read_csv(f, encoding="cp932", skiprows=1, dtype={"DATE": str})
        df.columns = [str(c).strip() for c in df.columns]
        unknown = [c for c in df.columns if c not in NEW_NAME_MAP and c not in IGNORE_NEW]
        if unknown:
            raise ValueError(f"{f}: 未知の列 {unknown}")
        df = df[[c for c in df.columns if c in NEW_NAME_MAP]].rename(columns=NEW_NAME_MAP)
        frames.append(df)
    df = pd.concat(frames, ignore_index=True).dropna(subset=["date"])
    ds = df["date"].astype(str).str.strip()
    slash = ds.str.contains("/")
    dates = pd.Series(pd.NaT, index=df.index)
    if slash.any():
        dates[slash] = pd.to_datetime(ds[slash], format="%Y/%m/%d")
    if (~slash).any():
        dates[~slash] = pd.to_datetime(ds[~slash], format="%Y%m%d")
    tt = df["time"].astype(str).str.strip()
    minutes = tt.str.split(":").str[0].astype(int) * 60 + tt.str.split(":").str[1].astype(int)
    assert minutes.min() == 0 and minutes.max() == 23 * 60 + 30, \
        f"{area_dir}: TIMEが開始ラベル(0:00-23:30)でない → 要確認"
    df["ts"] = dates + pd.to_timedelta(minutes, unit="m")
    for c in df.columns:
        if c not in ("date", "time", "ts"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["thermal"] = df[["th_lng", "th_coal", "th_oil", "th_other"]].sum(axis=1)
    # 恒等式検証（正=受電のまま成立するか）
    comp = (df[["nuclear", "thermal", "hydro", "geothermal", "biomass", "solar",
                "wind", "pumped", "battery", "interconn", "other"]].fillna(0).sum(axis=1))
    resid = (comp - df["demand"]).abs()
    print(f"  新形式 恒等式残差: 中央値{resid.median():.1f}MW / p99 {resid.quantile(.99):.1f}MW / 最大{resid.max():.0f}MW")
    g = df.set_index("ts")[[c for c in PANEL_COLS if c in df.columns]].resample("1h").mean()
    return g.reset_index()


def load_hokkaido_old():
    """旧形式: 4行前置き＋月日は日の先頭行のみ。1ファイルだけ.xls"""
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, "hokkaido", "sup_dem_results_*"))):
        if f.endswith(".xls"):
            raw = pd.read_excel(f, header=None, dtype=str)
        else:
            raw = pd.read_csv(f, encoding="cp932", header=None, dtype=str)
        # データ開始行 = 2列目が「0時」の最初の行
        start = raw.index[raw[1].astype(str).str.strip() == "0時"][0]
        df = raw.iloc[start:, :15].copy()
        df.columns = ["date_raw", "time_raw", "demand", "nuclear", "thermal", "hydro",
                      "geothermal", "biomass", "solar", "solar_curt", "wind", "wind_curt",
                      "pumped", "interconn", "total"]
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["date_raw"] = df["date_raw"].ffill()
    df = df[df["time_raw"].astype(str).str.contains("時", na=False)]
    hours = df["time_raw"].astype(str).str.replace("時", "", regex=False).astype(int)
    df["ts"] = pd.to_datetime(df["date_raw"], format="mixed") + pd.to_timedelta(hours, unit="h")
    for c in df.columns:
        if c not in ("date_raw", "time_raw", "ts"):
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ""), errors="coerce")
    comp = df[["nuclear", "thermal", "hydro", "geothermal", "biomass", "solar",
               "wind", "pumped", "interconn"]].fillna(0).sum(axis=1)
    resid = (comp - df["demand"]).abs()
    print(f"  旧形式 恒等式残差: 中央値{resid.median():.1f} / p99 {resid.quantile(.99):.1f} / 最大{resid.max():.0f}")
    df["battery"] = pd.NA
    df = df[df["ts"] < "2024-04-01"]
    return df[["ts"] + PANEL_COLS].sort_values("ts").reset_index(drop=True)


def load_tohoku_old():
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, "tohoku", "juyo_*_tohoku_*.csv"))):
        df = pd.read_csv(f, encoding="cp932")
        df.columns = [str(c).replace("〔MWh〕", "").strip() for c in df.columns]
        df = df.rename(columns={
            "DATE_TIME": "ts", "エリア需要": "demand", "水力": "hydro", "火力": "thermal",
            "原子力": "nuclear", "太陽光実績": "solar", "太陽光抑制量": "solar_curt",
            "風力実績": "wind", "風力抑制量": "wind_curt", "地熱": "geothermal",
            "バイオマス": "biomass", "揚水": "pumped", "連系線": "interconn"})
        frames.append(df)
    df = pd.concat(frames, ignore_index=True).dropna(subset=["ts"])
    df["ts"] = pd.to_datetime(df["ts"])
    for c in df.columns:
        if c != "ts":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    comp = df[["nuclear", "thermal", "hydro", "geothermal", "biomass", "solar",
               "wind", "pumped", "interconn"]].fillna(0).sum(axis=1)
    resid = (comp - df["demand"]).abs()
    print(f"  旧形式 恒等式残差: 中央値{resid.median():.1f} / p99 {resid.quantile(.99):.1f} / 最大{resid.max():.0f}")
    df["battery"] = pd.NA
    # 新形式が2024/2から存在するため旧は2024/1まで採用
    df = df[df["ts"] < "2024-02-01"]
    return df[["ts"] + PANEL_COLS].sort_values("ts").reset_index(drop=True)


def build(area, old_loader, area_dir, code, price_col):
    print(f"=== {area} ===")
    old = old_loader()
    new = load_new(area_dir, code)
    supply = pd.concat([old, new], ignore_index=True).sort_values("ts")
    supply = supply.drop_duplicates(subset="ts", keep="last").reset_index(drop=True)

    jepx = pd.read_csv(os.path.join(OUT, "jepx_kyushu_30min.csv"), parse_dates=["ts"])
    jh = jepx.set_index("ts")[["p_system", "p_hokkaido", "p_tohoku"]].resample("1h").mean().reset_index()
    panel = supply.merge(jh, on="ts", how="left")
    panel["fy"] = fiscal_year(panel["ts"])
    out = os.path.join(OUT, f"{area}_hourly_panel.csv")
    panel.to_csv(out, index=False)

    # ---- 検証サマリー ----
    print(f"  行数 {len(panel):,} / 期間 {panel['ts'].min()} .. {panel['ts'].max()}")
    full = pd.date_range(panel["ts"].min(), panel["ts"].max(), freq="1h")
    print(f"  欠落時刻: {len(full) - panel['ts'].nunique()} / 価格欠損: {panel[price_col].isna().sum()}")
    for name, col in [("太陽光", "solar_curt"), ("風力", "wind_curt")]:
        pos = panel[panel[col].fillna(0) > 0]
        print(f"  {name}出力制御 初回: {pos['ts'].min() if len(pos) else 'なし'} / 発生時間数 {len(pos):,}")
    print(f"  原子力>0の時間数: {(panel['nuclear'].fillna(0) > 0).sum():,}")
    # 形式境界の連続性（夜間連系線の月平均）
    b = panel[(panel["ts"].dt.hour < 5)].set_index("ts")["interconn"].resample("MS").mean()
    around = b[(b.index >= "2023-11-01") & (b.index <= "2024-06-01")]
    print("  夜間連系線 月平均（形式境界前後）:", {str(k.date()): round(v) for k, v in around.items()})
    return panel


if __name__ == "__main__":
    build("hokkaido", load_hokkaido_old, "hokkaido", "01", "p_hokkaido")
    build("tohoku", load_tohoku_old, "tohoku", "02", "p_tohoku")
