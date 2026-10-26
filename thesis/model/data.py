# -*- coding: utf-8 -*-
"""過去のデータ。日×24時間の配列で返す

- 時間別の需給・価格: data/processed/hokkaido_hourly_panel.csv（北電NW エリア需給実績＋JEPX、analysis/11 で作成）
- 太陽光・風力の容量: data/processed/area_capacity_series.csv（FIT/FIP B表、analysis/12 で作成）
- ユニット別の火力: data/raw/occto_unit/*.csv（OCCTO ユニット別発電実績。規約がはっきりするまでコミットしない）。
  キャッシュは data/interim/occto_unit_hourly_hokkaido.pkl（同じくコミットしない）
- 燃料費: data/processed/fuel_vc_monthly.csv（analysis/60 で作成）
- 火力の停止の記録: data/raw/hjks/outages_*.csv（HJKS 発電情報公開システム、著者が取得。規約がはっきりするまでコミットしない）
"""
import glob
import os
from functools import lru_cache

import numpy as np
import pandas as pd

from . import params as PR

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")
INTERIM = os.path.join(ROOT, "data", "interim")


@lru_cache(None)
def panel():
    P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"]).set_index("ts")
    P["fy"] = P.index.year - (P.index.month < 4)
    return P


@lru_cache(None)
def fuel():
    F = pd.read_csv(os.path.join(PROC, "fuel_vc_monthly.csv"), parse_dates=["month"]).set_index("month")
    F["idx"] = (F["vc_coal"] + F["vc_lng"]) / 2
    return F


def _capacity_daily(dates):
    C = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
    C = C[C["area"] == "hokkaido"].set_index("date")[["solar_kw", "wind_kw"]] / 1_000.0
    full = C.reindex(C.index.union(dates)).interpolate("time").ffill().bfill()
    return full.reindex(dates)


def _days(fys):
    P = panel()
    idx = P.index[np.isin(P["fy"], fys)]
    days = pd.DatetimeIndex(sorted(set(idx.normalize())))
    full = [d for d in days if ((idx >= d) & (idx < d + pd.Timedelta(days=1))).sum() == 24]
    return pd.DatetimeIndex(full)


def _grid(series, days):
    """時間の Series を日×24 に並べる"""
    ts = (days.values[:, None] + (np.arange(24) * np.timedelta64(1, "h"))[None, :]).ravel()
    return series.reindex(pd.DatetimeIndex(ts)).to_numpy(float).reshape(len(days), 24)


@lru_cache(None)
def weather():
    """気象年（FY2023〜25）の時間別の形。D・S_pre・W_pre（抑制前）・cf_S・cf_W・Hy・N・G・Bm・th・pump・X・p・month・fy"""
    P = panel()
    days = _days(PR.WEATHER_FY)
    g = lambda c: _grid(P[c].fillna(0.0), days)
    cap = _capacity_daily(days)
    W = dict(days=days, D=g("demand"), S_pre=g("solar") + g("solar_curt"), W_pre=g("wind") + g("wind_curt"),
             curt=g("solar_curt") + g("wind_curt"), Hy=g("hydro"), N=g("nuclear"), G=g("geothermal"), Bm=g("biomass"),
             th=g("thermal"), pump=g("pumped"), X=-g("interconn"), p=g("p_hokkaido"), p_th=g("p_tohoku"))
    W["cf_S"] = W["S_pre"] / cap["solar_kw"].to_numpy()[:, None]
    W["cf_W"] = W["W_pre"] / cap["wind_kw"].to_numpy()[:, None]
    W["month"] = np.repeat(days.month.to_numpy()[:, None], 24, 1)
    W["fy"] = (days.year - (days.month < 4)).to_numpy()
    W["hour"] = np.tile(np.arange(24), (len(days), 1))
    W["season"] = np.vectorize(PR.SEASON_OF_MONTH.get)(W["month"])
    return W


@lru_cache(None)
def units_hourly():
    """OCCTO ユニット別発電実績（30分の kWh）を、北海道の火力について時間別の MW にする"""
    cache = os.path.join(INTERIM, "occto_unit_hourly_hokkaido.pkl")
    files = sorted(glob.glob(os.path.join(RAW, "occto_unit", "*.csv")))
    newest = max(os.path.getmtime(f) for f in files)
    if os.path.exists(cache) and os.path.getmtime(cache) >= newest:
        return pd.read_pickle(cache)
    d = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in files], ignore_index=True)
    h = d[(d["エリア"] == "北海道") & d["発電方式・燃種"].str.startswith("火力")].copy()
    slots = [c for c in h.columns if c.endswith("[kWh]") and ":" in c]
    h["unit"] = h["発電所名"].str.replace("北海道ﾊﾟﾜｰｴﾝｼﾞﾆｱﾘﾝｸﾞ株式会社　", "", regex=False) + " " + h["ユニット名"]
    lg = h.melt(id_vars=["unit", "対象日"], value_vars=slots, var_name="slot", value_name="kWh")
    hm = lg["slot"].str.slice(0, 5)
    lg["hour"] = (pd.to_datetime(lg["対象日"]) + pd.to_timedelta(hm.str.slice(0, 2).astype(int), unit="h")
                  + pd.to_timedelta(hm.str.slice(3, 5).astype(int), unit="m") - pd.Timedelta(minutes=30)).dt.floor("h")
    out = lg.groupby(["unit", "hour"])["kWh"].sum().unstack(0) / 1_000.0
    os.makedirs(INTERIM, exist_ok=True)
    out.to_pickle(cache)
    return out


def unit_vc(unit_row, months):
    """ユニットの燃料費（円/kWh、送電端）。月別の燃料費の指標×ユニットの比"""
    name, fuel_, cap, mn, ratio = unit_row[:5]
    F = fuel().reindex(pd.DatetimeIndex(months).to_period("M").to_timestamp()).ffill().bfill()
    base = {"石炭": F["vc_coal"] / 10.4, "LNG": F["vc_lng"] / 13.0, "石油": F["vc_oil"] / 27.8}[fuel_]
    return base.to_numpy() * ratio


@lru_cache(None)
def calib():
    """較正の基準年（FY2024〜25）の時間別の配列。ユニット別の火力の出力・燃料費、対象外の火力、価格、燃料費の指標"""
    P = panel()
    days = _days(PR.CALIB_FY)
    U = units_hourly()
    hist_units = [u for u in PR.UNITS if u[9] is not None]
    ts = pd.DatetimeIndex((days.values[:, None] + (np.arange(24) * np.timedelta64(1, "h"))[None, :]).ravel())
    G = np.stack([U[u[9]].reindex(ts).fillna(0.0).clip(lower=0.0).to_numpy().reshape(len(days), 24) for u in hist_units], 2)
    months = np.repeat(days.values[:, None], 24, 1).ravel()
    VC = np.stack([unit_vc(u, months).reshape(len(days), 24) for u in hist_units], 2)
    g = lambda c: _grid(P[c].fillna(0.0), days)
    th = g("thermal")
    C = dict(days=days, units=hist_units, G=G, VC=VC, th=th, other=th - G.sum(2), p=g("p_hokkaido"),
             D=g("demand"), S=g("solar"), W=g("wind"), N=g("nuclear"), Hy=g("hydro"), Geo=g("geothermal"), Bm=g("biomass"),
             curt=g("solar_curt") + g("wind_curt"), X=-g("interconn"), pump=g("pumped"))
    C["month"] = np.repeat(days.month.to_numpy()[:, None], 24, 1)
    C["season"] = np.vectorize(PR.SEASON_OF_MONTH.get)(C["month"])
    C["hour"] = np.tile(np.arange(24), (len(days), 1))
    C["fy"] = (days.year - (days.month < 4)).to_numpy()
    F = fuel().reindex(pd.DatetimeIndex(months).to_period("M").to_timestamp())
    C["v"] = F["idx"].to_numpy().reshape(len(days), 24)
    return C


HJKS_UNIT = {("石狩湾新港発電所", "１号機"): "石狩湾新港1", ("苫東厚真発電所", "４号機"): "苫東厚真4", ("苫東厚真発電所", "２号機"): "苫東厚真2",
             ("苫東厚真発電所", "１号機"): "苫東厚真1", ("知内発電所", "２号機"): "知内2", ("知内発電所", "１号機"): "知内1",
             ("砂川発電所", "３号機"): "砂川3", ("砂川発電所", "４号機"): "砂川4", ("苫小牧発電所", "単独"): "苫小牧1"}


@lru_cache(None)
def hjks_records():
    """HJKS の停止の記録（北海道の火力）。停止は出力0、出力低下は低下量÷認可出力の比だけ下げる。
    復旧予定日（日付）はその日の終わりまで止まるとみなす"""
    fs = sorted(glob.glob(os.path.join(RAW, "hjks", "outages_*.csv")))
    d = pd.concat([pd.read_csv(f, encoding="cp932", index_col=False) for f in fs]).drop_duplicates()
    d = d[d["発電形式"].astype(str).str.contains("火力")].copy()
    d = d[~(d["種別"].astype(str).str.contains("燃料制約") | d["停止原因"].astype(str).str.contains("非効率"))]   # 期間の平均の低下で、時間の上限ではない
    name = []
    for _, r in d.iterrows():
        k = (str(r["発電所名"]).strip(), str(r["ユニット名"]).strip())
        name.append(HJKS_UNIT.get(k, "苫小牧共同3" if "苫小牧共同火力" in k[0] else None))
    d["unit"] = name
    d = d[d["unit"].notna()]
    d["start"] = pd.to_datetime(d["停止日時"], format="%Y/%m/%d %H:%M", errors="coerce")
    d["end"] = pd.to_datetime(d["復旧予定日"], format="%Y/%m/%d", errors="coerce") + pd.Timedelta(days=1)
    red = pd.to_numeric(d["低下量"], errors="coerce") / pd.to_numeric(d["認可出力"], errors="coerce")
    d["frac"] = np.where(d["停止区分"].astype(str).str.contains("低下"), red.clip(0, 1).fillna(0.0), 1.0)
    return d[["unit", "start", "end", "frac", "停止区分", "種別"]].dropna(subset=["start", "end"]).reset_index(drop=True)


def hjks_availability(days, names):
    """日×24 の運転できる比（1−停止・低下の比）。記録が重なる時間は大きい方の低下をとる。{ユニット名: 配列}"""
    ts = pd.DatetimeIndex((days.values[:, None] + (np.arange(24) * np.timedelta64(1, "h"))[None, :]).ravel())
    R = hjks_records()
    out = {}
    for u in names:
        red = np.zeros(len(ts))
        for _, r in R[R["unit"] == u].iterrows():
            m = (ts >= r["start"]) & (ts < r["end"])
            red[m] = np.maximum(red[m], r["frac"])
        out[u] = (1.0 - red).reshape(len(days), 24)
    return out


@lru_cache(None)
def unit_avail_profile():
    """将来の運転できる比（ユニット×月）: OCCTO の月別の形 × （そのユニットの気象年 FY2023〜25 の HJKS による平均 ÷ 同じ燃料の OCCTO の年平均）。
    実績のないユニット（石狩湾新港2・3号）は OCCTO の値のまま。推定（HJKS の実績の比）と将来の土台をそろえる"""
    days = _days(PR.WEATHER_FY)                               # 気象年 FY2023〜25 の平均
    names = [u[0] for u in PR.UNITS if u[9] is not None]
    A = hjks_availability(days, names)
    out = {}
    for u in PR.UNITS:
        base = np.array(PR.AVAIL[u[1]]) / 100.0
        if u[0] in A:
            out[u[0]] = np.minimum(base * float(A[u[0]].mean()) / base.mean(), 1.0)
        else:
            out[u[0]] = base
    return out
