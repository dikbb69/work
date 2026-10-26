#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""需給調整市場（EPRX）の北海道の取引結果: 市場の大きさと、蓄電池 1kW が得られる ΔkW 収入の上限

入力: data/需給調整市場データ/*.zip（EPRX 取引結果 CSV。著者が免責事項に同意して手動で取得。FY2024〜FY2026年8月）
  - 商品: 一次調整力・一次オフライン・二次調整力1・二次調整力2・三次調整力1・三次調整力2・複合商品
  - 価格の単位は 円/kW・30分（3時間ブロックの年も同じ）。ブロックの長さ ＝ 48÷ブロック数 コマ（1コマ30分）
  - 北海道の列を使う。調達量は「募集量（TSO別）」、約定は「合計（確報値）」の電源属地別（北海道にある電源が受け取った分）
出力:
  data/processed/balancing_hokkaido_monthly.csv  月×商品の募集量・約定量・平均価格・支払総額
  data/processed/balancing_hokkaido_fy.csv       年度×商品の同じ集計と、1kW の ΔkW 収入の上限
  data/processed/balancing_vs_spot_monthly.csv   月ごとの ΔkW 収入の上限とスポット裁定（4時間、実績価格）の比較
  figures/hokkaido/balancing_hokkaido.png
1kW の収入の上限（円/kW-年）:
  - 商品ごと: そのコマで北海道の電源が落札した平均価格を、全コマで受け取ったとした値（落札できない・SOC の制約は無視）
  - 最良の商品: コマごとに最も高い商品の平均価格を受け取ったとした値（1kW は1コマに1商品）
  - 市場の大きさで割った値: 北海道の電源への支払総額（全商品）÷ 蓄電池の容量 K。K が市場を全部取っても1kW あたりはこれ以下
限界: kWh の精算（発動の収入）は入れない。落札は応札の価格で決まる（複数価格）ので、平均価格は限界の価格ではない。
"""
import glob
import io
import os
import re
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "data", "需給調整市場データ")
PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Maru Gothic Pro", "sans-serif"]

PRODUCTS = ["一次調整力", "一次オフライン", "二次調整力1", "二次調整力2", "三次調整力1", "三次調整力2", "複合商品"]
ROWS = {"募集量（TSO別）[MW]": "募集量", "約定量合計（電源属地別）[MW]": "約定量", "平均約定価格（電源属地別）[円/kW・30分]": "平均価格",
        "最高約定価格（電源属地別）[円/kW・30分]": "最高価格", "応札量合計（電源属地別）[MW]": "応札量"}


def read_one(raw, name):
    txt = raw.decode("cp932").replace("\r", "")
    lines = txt.split("\n")
    meta = lines[1].split(",")
    product, nblock = meta[3], int(meta[4])
    df = pd.read_csv(io.StringIO("\n".join(lines[2:])), dtype=str)
    df = df[df["TT"].astype(str).str.match(r"^\d{8}B\d+$") & (df["調達区分"] == "合計（確報値）")]
    m = re.search(r"_(\d{4})-(\d{4})_", os.path.basename(name))
    if m:   # 月の途中で制度が変わった月は、ファイルごとに対象の日を絞る（ほかの日は空の行）
        md = df["TT"].str[4:8]
        df = df[(md >= m.group(1)) & (md <= m.group(2))]
    df = df[df["取引情報"].isin(ROWS)]
    out = df[["TT", "取引情報", "北海道"]].copy()
    out["北海道"] = pd.to_numeric(out["北海道"].replace("-", np.nan), errors="coerce")
    w = out.pivot_table(index="TT", columns="取引情報", values="北海道", aggfunc="first").rename(columns=ROWS)
    w["商品"] = product
    w["コマ"] = 48 // nblock
    return w


def load():
    parts = []
    for z in sorted(glob.glob(os.path.join(SRC, "*_result.zip"))):
        if "tieline" in z:
            continue
        with zipfile.ZipFile(z) as zf:
            for n in zf.namelist():
                if n.endswith(".csv"):
                    parts.append(read_one(zf.read(n), n))
    A = pd.concat(parts)
    A = A.reset_index().drop_duplicates(["TT", "商品"], keep="last")
    A["日"] = pd.to_datetime(A["TT"].str[:8])
    A["ブロック"] = A["TT"].str[9:].astype(int)
    A["fy"] = A["日"].dt.year - (A["日"].dt.month < 4)
    A["月"] = A["日"].dt.to_period("M").dt.to_timestamp()
    for c in ROWS.values():
        A[c] = A[c].fillna(0.0)
    A["支払(円)"] = A["平均価格"] * A["約定量"] * 1000 * A["コマ"]
    return A


def per_slot(A):
    """30分のコマに展開した北海道の平均価格（商品×コマ）"""
    rows = []
    for (prod, k), g in A.groupby(["商品", "コマ"]):
        rep = g.loc[g.index.repeat(k)].copy()
        rep["コマ番号"] = (rep["ブロック"] - 1) * k + np.tile(np.arange(k), len(g))
        rows.append(rep[["日", "コマ番号", "商品", "平均価格", "約定量"]])
    S = pd.concat(rows)
    S["ts"] = S["日"] + pd.to_timedelta(S["コマ番号"] * 30, "min")
    return S


def spot_arbitrage_monthly():
    """4時間の蓄電池の裁定（実績の北海道価格、完全予見、往復効率0.90）の月の値（円/kW）"""
    P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"]).set_index("ts")["p_hokkaido"]
    j = pd.read_csv(os.path.join(ROOT, "data", "raw", "jepx", "spot_summary_2026.csv"), encoding="cp932")
    j["ts"] = pd.to_datetime(j["受渡日"]) + pd.to_timedelta((j["時刻コード"] - 1) * 30, "min")
    h = j.set_index("ts")["エリアプライス北海道(円/kWh)"].resample("h").mean()
    P = pd.concat([P[P.index < h.index[0]], h]).sort_index()
    P = P[P.index >= "2024-04-01"].dropna()
    d = P.groupby(P.index.normalize())
    out = {}
    for day, x in d:
        if len(x) != 24:
            continue
        s = np.sort(x.to_numpy())
        out[day] = max(s[-4:].sum() * 0.90 ** 0.5 - s[:4].sum() / 0.90 ** 0.5, 0.0)
    v = pd.Series(out)
    return v.groupby(v.index.to_period("M").to_timestamp()).agg(["sum", "count"])


def main():
    A = load()
    print(f"読み込み: {len(A):,} 行（商品×ブロック）、{A['日'].min():%Y-%m-%d}〜{A['日'].max():%Y-%m-%d}")
    M = A.groupby(["月", "商品"]).apply(lambda g: pd.Series({
        "募集量 平均(MW)": np.average(g["募集量"], weights=g["コマ"]),
        "約定量 平均(MW)": np.average(g["約定量"], weights=g["コマ"]),
        "応札量 平均(MW)": np.average(g["応札量"], weights=g["コマ"]),
        "平均価格(円/kW・30分)": (g["平均価格"] * g["約定量"] * g["コマ"]).sum() / max((g["約定量"] * g["コマ"]).sum(), 1e-9),
        "支払総額(億円)": g["支払(円)"].sum() / 1e8,
        "1kW 全コマ(円/kW)": (g["平均価格"] * g["コマ"]).sum(),
    }), include_groups=False).reset_index()
    M.to_csv(os.path.join(PROC, "balancing_hokkaido_monthly.csv"), index=False, encoding="utf-8-sig")

    S = per_slot(A)
    best = S.groupby("ts")["平均価格"].max()
    best_m = best.groupby(best.index.to_period("M").to_timestamp()).sum()
    pay_m = M.groupby("月")["支払総額(億円)"].sum()
    req_m = M.groupby("月")["募集量 平均(MW)"].sum()
    sp = spot_arbitrage_monthly()
    C = pd.DataFrame({"ΔkW 最良の商品(円/kW)": best_m, "北海道の支払総額(億円)": pay_m, "募集量の合計 平均(MW)": req_m,
                      "スポット裁定 完全予見(円/kW)": sp["sum"], "スポット裁定の日数": sp["count"]})
    for K in (21, 50, 100):
        C[f"支払総額÷{K}万kW(円/kW)"] = C["北海道の支払総額(億円)"] * 1e8 / (K * 1e4)
    C.index.name = "月"
    C.to_csv(os.path.join(PROC, "balancing_vs_spot_monthly.csv"), encoding="utf-8-sig")

    # 年度の集計（FY2026 は4〜8月。年額は日数で換算した参考値）
    rows = []
    for fy, g in A.groupby("fy"):
        nd = g["日"].nunique()
        scale = 365.0 / nd
        for prod in PRODUCTS:
            q = g[g["商品"] == prod]
            if q.empty:
                continue
            rows.append({"年度": fy, "日数": nd, "商品": prod,
                         "募集量 平均(MW)": np.average(q["募集量"], weights=q["コマ"]),
                         "約定量 平均(MW)": np.average(q["約定量"], weights=q["コマ"]),
                         "応札量 平均(MW)": np.average(q["応札量"], weights=q["コマ"]),
                         "平均価格(円/kW・30分)": (q["平均価格"] * q["約定量"] * q["コマ"]).sum() / max((q["約定量"] * q["コマ"]).sum(), 1e-9),
                         "支払総額 年換算(億円)": q["支払(円)"].sum() / 1e8 * scale,
                         "1kW 全コマ 年換算(円/kW-年)": (q["平均価格"] * q["コマ"]).sum() * scale})
        sfy = S[S["日"].dt.year - (S["日"].dt.month < 4) == fy]
        b = sfy.groupby("ts")["平均価格"].max().sum() * scale
        pay = g["支払(円)"].sum() * scale
        rows.append({"年度": fy, "日数": nd, "商品": "全商品（最良の商品・支払総額）", "募集量 平均(MW)": np.nan,
                     "支払総額 年換算(億円)": pay / 1e8, "1kW 全コマ 年換算(円/kW-年)": b,
                     **{f"支払総額÷{K}万kW(円/kW-年)": pay / (K * 1e4) for K in (21, 50, 100)}})
    Y = pd.DataFrame(rows)
    Y.to_csv(os.path.join(PROC, "balancing_hokkaido_fy.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(Y.round(1).to_string(index=False))
    print(C.round(0).to_string())

    # 図: 月ごとの ΔkW の上限・市場の大きさ÷K とスポット裁定
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    x = C.index
    ax[0].plot(x, C["ΔkW 最良の商品(円/kW)"], marker="o", label="ΔkW 収入の上限（コマごとに最良の商品）")
    ax[0].plot(x, C["支払総額÷100万kW(円/kW)"], marker="s", label="北海道の支払総額 ÷ 100万kW")
    ax[0].plot(x, C["スポット裁定 完全予見(円/kW)"], marker="^", label="スポット裁定（4時間・完全予見）")
    ax[0].axvline(pd.Timestamp("2026-03-14"), color="gray", ls=":", lw=1)
    ax[0].text(pd.Timestamp("2026-03-20"), ax[0].get_ylim()[1] * 0.6, "前日化・\n上限15円", fontsize=8, ha="left", va="top")
    ax[0].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%y/%m"))
    ax[0].set_ylabel("円/kW（月）")
    ax[0].set_title("蓄電池 1kW の月の収入の上限（北海道）")
    ax[0].legend(fontsize=8)
    piv = M.pivot(index="月", columns="商品", values="募集量 平均(MW)").reindex(columns=PRODUCTS).fillna(0)
    piv.plot.area(ax=ax[1], lw=0, alpha=0.8)
    ax[1].set_ylabel("MW（月平均）")
    ax[1].set_title("北海道の募集量（TSO別、商品別）")
    ax[1].legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "balancing_hokkaido.png"), dpi=150)
    print("図:", os.path.join(FIG, "balancing_hokkaido.png"))


if __name__ == "__main__":
    main()
