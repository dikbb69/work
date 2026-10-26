#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ユニット別の発電実績で、出力制御時の火力の運転台数と出力を確かめる（55 の構造モデルの「火力の床」の検証）

データ: OCCTO「ユニット別発電実績公開システム」の北海道・東北の30分値（著者が利用規約に同意して取得、2024/4/1〜2026/10/21、
       data/raw/occto_unit/）。北海道電力ネットワークのエリア需給実績（30分値、eria_jukyu、2024/4〜2026/6）の再エネ出力制御のコマと結合する。
確かめる点:
  (1) 出力制御のコマに運転していた火力ユニットと、その出力（中央値・5%点）。北海道電力ネットワーク・OCCTO の運用の説明
      「石油・石炭・LNG のマストラン3台のみ運転」（55 の規則）がどの程度成り立つか。
  (2) ユニット別の最低出力の実績値（運転時の5%点）と、55 で使う最低出力（2026/5 の前日計画）との比較。
  (3) エリアの火力計とユニット計の差（ユニット別の公開の対象外の火力。非調整火力・自家発など）。
出力: data/processed/unit_commitment_curtailment.csv、unit_commitment_combos.csv
"""
import glob
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")

d = pd.concat([pd.read_csv(f, encoding="utf-8-sig") for f in sorted(glob.glob(os.path.join(RAW, "occto_unit", "*.csv")))], ignore_index=True)
h = d[(d["エリア"] == "北海道") & (d["発電方式・燃種"].str.startswith("火力") | d["発電方式・燃種"].eq("水力"))].copy()
SLOTS = [c for c in h.columns if c.endswith("[kWh]") and ":" in c]
h["unit"] = h["発電所名"].str.replace("北海道ﾊﾟﾜｰｴﾝｼﾞﾆｱﾘﾝｸﾞ株式会社　", "", regex=False) + " " + h["ユニット名"]
FUEL = h.drop_duplicates("unit").set_index("unit")["発電方式・燃種"]
long = h.melt(id_vars=["unit", "対象日"], value_vars=SLOTS, var_name="slot", value_name="kWh")
hm = long["slot"].str.slice(0, 5)
long["ts"] = (pd.to_datetime(long["対象日"]) + pd.to_timedelta(hm.str.slice(0, 2).astype(int), unit="h")
              + pd.to_timedelta(hm.str.slice(3, 5).astype(int), unit="m") - pd.Timedelta(minutes=30))      # コマの開始時刻
long["MW"] = long["kWh"] * 2 / 1000
W = long.pivot_table(index="ts", columns="unit", values="MW")

fs = sorted(glob.glob(os.path.join(RAW, "hokkaido", "eria_jukyu_2*_01.csv")))
J = pd.concat([pd.read_csv(f, encoding="shift_jis", skiprows=1) for f in fs], ignore_index=True)
J.columns = [c.strip() for c in J.columns]
J = J.dropna(subset=["DATE"])
J["ts"] = pd.to_datetime(J["DATE"] + " " + J["TIME"])
J = J.set_index("ts")
for c in J.columns:
    if c not in ("DATE", "TIME"):
        J[c] = pd.to_numeric(J[c], errors="coerce")
J["火力計"] = J[["火力(LNG)", "火力(石炭)", "火力(石油)", "火力(その他)"]].sum(axis=1)
J["再エネ出力制御"] = J["太陽光出力制御量"].fillna(0) + J["風力出力制御量"].fillna(0)
X = W.join(J[["火力計", "再エネ出力制御"]], how="inner")
TH = [u for u in W.columns if FUEL[u].startswith("火力")]
X["火力ユニット計"] = X[TH].sum(axis=1)
X["ユニット外の火力"] = X["火力計"] - X["火力ユニット計"]
CUR = X[X["再エネ出力制御"] > 0]
MID = CUR[CUR.index.hour.isin([10, 11, 12, 13])]
print(f"結合: {len(X):,} コマ（{X.index.min():%Y-%m-%d}〜{X.index.max():%Y-%m-%d}）、出力制御のコマ {len(CUR):,}、うち10〜13時 {len(MID):,}")

PLAN_MIN = {"苫東厚真発電所 ４号機": 93.0, "知内発電所 ２号機": 47.0, "石狩湾新港発電所 １号機": 242.0}   # 55 の値（2026/5 の前日計画）
rows = []
for u in TH + [u for u in W.columns if u not in TH]:
    s, m = CUR[u], MID[u]
    on, onm = s[s > 1], m[m > 1]
    rows.append({"ユニット": u, "燃種": FUEL[u], "運転の割合（制御のコマ）": (s > 1).mean(), "運転の割合（10〜13時）": (m > 1).mean(),
                 "出力の中央値MW（10〜13時、運転時）": onm.median(), "出力の5%点MW（運転時）": on.quantile(0.05),
                 "全期間の運転時の1%点MW": X[u][X[u] > 1].quantile(0.01), "55 の最低出力MW": PLAN_MIN.get(u)})
R = pd.DataFrame(rows)
R.round(3).to_csv(os.path.join(PROC, "unit_commitment_curtailment.csv"), index=False, encoding="utf-8-sig")
print(R.round(2).to_string(index=False))

n_on = (MID[TH] > 1).sum(axis=1)
short = lambda u: u.replace("発電所", "").replace(" ", "")
combo = (MID[TH] > 1).apply(lambda r: "＋".join(sorted(short(u) for u, v in r.items() if v)), axis=1)
C = combo.value_counts().rename("コマ数").to_frame()
C["割合"] = C["コマ数"] / len(MID)
C.to_csv(os.path.join(PROC, "unit_commitment_combos.csv"), encoding="utf-8-sig")
print("\n10〜13時の出力制御のコマの運転台数:", n_on.value_counts().sort_index().to_dict())
print(C.head(8).round(3).to_string())
print("\n出力制御のコマの火力（MW）: 5%点 / 中央値")
for c in ("火力計", "火力ユニット計", "ユニット外の火力"):
    print(f"  {c}: {CUR[c].quantile(0.05):.0f} / {CUR[c].median():.0f}")
low = CUR[CUR["火力計"] <= CUR["火力計"].quantile(0.1)]
print("\n火力計が下位10%の出力制御のコマ（最も深く絞った時間）の内訳（MW、平均）")
print(low[TH + ["ユニット外の火力", "火力計"]].mean().round(0)[lambda s: s > 0.5].to_string())
