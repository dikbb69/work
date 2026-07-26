#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""九州パイロット: 生データから分析用パネルを構築する

入力: thesis/data/raw/jepx/spot_summary_YYYY.csv (30分48コマ, cp932)
      thesis/data/raw/kyushu/area_jyukyu_jisseki_*.csv (60分値, 2016/4-2024/3, MWh)
      thesis/data/raw/kyushu/eria_jukyu_YYYYMM_09.csv (30分値, 2024/3-, MW平均)
出力: thesis/data/processed/jepx_kyushu_30min.csv   価格30分パネル(全期間)
      thesis/data/processed/kyushu_hourly_panel.csv 価格×需給の60分パネル(全期間)
      thesis/data/processed/kyushu_daily_metrics.csv 日次指標(価格構造・スプレッド・制御)

粒度・単位の断層への対処は thesis/data/README.md の方針に従う:
  - 長期比較は60分に統一(30分JEPX→単純平均, 新形式MW平均→×0.5でMWh→時間合算)
  - 2024年3月は新旧重複のため新形式を正とする
"""
import glob
import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "processed")
os.makedirs(OUT, exist_ok=True)


def fiscal_year(ts):
    return ts.dt.year - (ts.dt.month < 4).astype(int)


# ---------- JEPX 30分パネル ----------
def load_jepx():
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, "jepx", "spot_summary_*.csv"))):
        df = pd.read_csv(f, encoding="cp932")
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(
        columns={
            "受渡日": "date",
            "時刻コード": "koma",
            "売り入札量(kWh)": "sell_kwh",
            "買い入札量(kWh)": "buy_kwh",
            "約定総量(kWh)": "volume_kwh",
            "システムプライス(円/kWh)": "p_system",
            "エリアプライス北海道(円/kWh)": "p_hokkaido",
            "エリアプライス東北(円/kWh)": "p_tohoku",
            "エリアプライス九州(円/kWh)": "p_kyushu",
        }
    )
    keep = ["date", "koma", "sell_kwh", "buy_kwh", "volume_kwh",
            "p_system", "p_hokkaido", "p_tohoku", "p_kyushu"]
    df = df[keep].copy()
    df["date"] = pd.to_datetime(df["date"])
    # コマ1 = 0:00-0:30 開始時刻
    df["ts"] = df["date"] + pd.to_timedelta((df["koma"] - 1) * 30, unit="m")
    df["fy"] = fiscal_year(df["ts"])
    return df.sort_values("ts").reset_index(drop=True)


# ---------- 九州需給実績: 旧形式(60分値, MWh) ----------
OLD_COLS = ["ts", "demand", "nuclear", "thermal", "hydro", "geothermal", "biomass",
            "solar", "solar_curt", "wind", "wind_curt", "pumped", "interconn"]


def load_kyushu_old():
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, "kyushu", "area_jyukyu_jisseki_*.csv"))):
        df = pd.read_csv(f, encoding="cp932", skiprows=2, header=None)
        df = df.iloc[:, :13]
        df.columns = OLD_COLS
        frames.append(df)
    df = pd.concat(frames, ignore_index=True).dropna(subset=["ts"])
    df["ts"] = pd.to_datetime(df["ts"])
    # 2024年3月は新形式を正とするため除外
    df = df[df["ts"] < "2024-03-01"]
    for c in OLD_COLS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["battery"] = pd.NA  # 旧形式に蓄電池列はない(欠測扱い)
    return df.sort_values("ts").reset_index(drop=True)


# ---------- 九州需給実績: 新形式(30分値, MW平均) ----------
NEW_COLS = ["date", "time", "demand", "nuclear", "th_lng", "th_coal", "th_oil",
            "th_other", "hydro", "geothermal", "biomass", "solar", "solar_curt",
            "wind", "wind_curt", "pumped", "battery", "interconn", "other", "total"]


def load_kyushu_new():
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, "kyushu", "eria_jukyu_*.csv"))):
        df = pd.read_csv(f, encoding="cp932", skiprows=2, header=None, dtype={0: str})
        df = df.iloc[:, :20]
        df.columns = NEW_COLS
        frames.append(df)
    df = pd.concat(frames, ignore_index=True).dropna(subset=["date"])
    # 日付は '20240401' 形式と '2025/12/1' 形式が混在
    ds = df["date"].astype(str).str.strip()
    slash = ds.str.contains("/")
    dates = pd.Series(pd.NaT, index=df.index)
    dates[slash] = pd.to_datetime(ds[slash], format="%Y/%m/%d")
    dates[~slash] = pd.to_datetime(ds[~slash], format="%Y%m%d")
    # TIME はコマ終端ラベル(0:30 が 0:00-0:30)。開始時刻に変換する
    end = dates + pd.to_timedelta(
        df["time"].astype(str).str.split(":").str[0].astype(int) * 60
        + df["time"].astype(str).str.split(":").str[1].astype(int),
        unit="m",
    )
    df["ts"] = end - pd.Timedelta(minutes=30)
    num_cols = [c for c in NEW_COLS if c not in ("date", "time")]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["thermal"] = df[["th_lng", "th_coal", "th_oil", "th_other"]].sum(axis=1)
    return df.sort_values("ts").reset_index(drop=True)


def kyushu_new_to_hourly(new30):
    """MW平均30分値 → 時間電力量MWh(2コマ平均×1h)で旧形式と接続"""
    g = new30.set_index("ts")[
        ["demand", "nuclear", "thermal", "hydro", "geothermal", "biomass",
         "solar", "solar_curt", "wind", "wind_curt", "pumped", "battery", "interconn"]
    ].resample("1h").mean()
    return g.reset_index()


def main():
    jepx = load_jepx()
    jepx.to_csv(os.path.join(OUT, "jepx_kyushu_30min.csv"), index=False)
    print(f"jepx 30min: {len(jepx):,} rows {jepx['ts'].min()} .. {jepx['ts'].max()}")

    old = load_kyushu_old()
    new30 = load_kyushu_new()
    newh = kyushu_new_to_hourly(new30)
    supply = pd.concat(
        [old[["ts"] + OLD_COLS[1:] + ["battery"]], newh], ignore_index=True
    ).sort_values("ts").reset_index(drop=True)

    # JEPX 30分 → 60分平均で結合
    jh = jepx.set_index("ts")[["p_kyushu", "p_system", "p_hokkaido", "p_tohoku"]].resample("1h").mean().reset_index()
    panel = supply.merge(jh, on="ts", how="left")
    panel["fy"] = fiscal_year(panel["ts"])
    panel.to_csv(os.path.join(OUT, "kyushu_hourly_panel.csv"), index=False)
    print(f"hourly panel: {len(panel):,} rows {panel['ts'].min()} .. {panel['ts'].max()}")
    print("  price欠損(需給側期間内):", panel["p_kyushu"].isna().sum())

    # ---------- 日次指標(価格はJEPX30分値から計算) ----------
    j = jepx.copy()
    j["day"] = j["ts"].dt.normalize()

    def day_metrics(g):
        p = g["p_kyushu"].sort_values().to_numpy()
        top8 = p[-8:].mean()
        bot8 = p[:8].mean()
        return pd.Series({
            "p_mean": g["p_kyushu"].mean(),
            "p_min": p[0],
            "p_max": p[-1],
            "floor_koma": (g["p_kyushu"] <= 0.011).sum(),
            "spike50_koma": (g["p_kyushu"] >= 50).sum(),
            "spike100_koma": (g["p_kyushu"] >= 100).sum(),
            "spread_maxmin": p[-1] - p[0],
            "spread_tb4h": top8 - bot8,
            "p_sys_mean": g["p_system"].mean(),
        })
    daily = j.groupby("day").apply(day_metrics, include_groups=False).reset_index()

    # 需給側の日次集計(太陽光・制御)
    s = supply.copy()
    s["day"] = s["ts"].dt.normalize()
    sd = s.groupby("day").agg(
        demand_mwh=("demand", "sum"),
        solar_mwh=("solar", "sum"),
        solar_curt_mwh=("solar_curt", "sum"),
        wind_mwh=("wind", "sum"),
        wind_curt_mwh=("wind_curt", "sum"),
        solar_peak_mw=("solar", "max"),
    ).reset_index()
    daily = daily.merge(sd, on="day", how="left")
    daily["curtail_day"] = (daily["solar_curt_mwh"].fillna(0) + daily["wind_curt_mwh"].fillna(0)) > 0
    daily["fy"] = fiscal_year(daily["day"])
    daily.to_csv(os.path.join(OUT, "kyushu_daily_metrics.csv"), index=False)
    print(f"daily metrics: {len(daily):,} rows")

    # 年度別サマリー(検証を兼ねる)
    fy = daily.groupby("fy").agg(
        days=("day", "count"),
        p_mean=("p_mean", "mean"),
        floor_koma=("floor_koma", "sum"),
        spike100_koma=("spike100_koma", "sum"),
        spread_tb4h_med=("spread_tb4h", "median"),
        curtail_days=("curtail_day", "sum"),
        solar_peak_mw=("solar_peak_mw", "max"),
    )
    print(fy.to_string())


if __name__ == "__main__":
    main()
