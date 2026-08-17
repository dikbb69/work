#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道の追加図2点（進捗報告用）

  1. 年間裁定粗利の時系列（FY2016-25）: 完全予見PF / a.前日価格 / b.前日予測 / c.平均価格（気候値）
     — 九州版「オプション価値算出（スポット裁定）」の北海道版＋cを追加
  2. 風力変動の帯域分解の年度別時系列（<6h / 6-24h / 1-7日 / >7日 の分散シェア）

出力: figures/hokkaido/annual_backtest_series.png, wind_bands_timeseries.png
      進捗報告_20260817_図表データ.xlsx に「年間裁定粗利」「帯域分解時系列」シート追加
"""
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = "Noto Sans CJK JP"

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
XLSX = os.path.join(ROOT, "slides", "進捗報告_20260817_図表データ.xlsx")

GRAY = "#595959"
ETA = 0.85
FY_FULL = list(range(2016, 2026))

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)

# ============================================================
# 1. 年間裁定粗利の時系列（PF / a / b / c）
# ============================================================
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
D = hp.pivot(index="day", columns="hour", values="demand")
S = hp.pivot(index="day", columns="hour", values="solar")
days = P.index
all_days = D.index
wk = pd.Series(all_days.dayofweek >= 5, index=all_days)
wkP = pd.Series(P.index.dayofweek >= 5, index=P.index)


def margin(p, dis, chg):
    return (p[list(dis)].sum() * ETA - p[list(chg)].sum()) * 1000


def win(series):
    o = series.sort_values()
    return o.index[-4:], o.index[:4]


rows = []
for i, d in enumerate(days):
    p = P.loc[d]
    rec = {"day": d, "pf": max(0.0, margin(p, *win(p)))}
    if i >= 1:
        rec["a"] = margin(p, *win(P.loc[days[i - 1]]))
    hist_p = [dd for dd in days[max(0, i - 29):i] if wkP[dd] == wkP[d]]
    if len(hist_p) >= 5:
        rec["c"] = margin(p, *win(P.loc[hist_p].mean()))
    jj = all_days.get_loc(d)
    if jj >= 30:
        hist = all_days[max(0, jj - 29):jj - 1]
        same = [h for h in hist if wk[h] == wk[d]]
        if len(same) >= 5:
            dem_f = D.loc[same].mean()
            sol_f = S.loc[all_days[jj - 8:jj - 1]].mean()
            rec["b"] = margin(p, *win(dem_f - sol_f))
    rows.append(rec)
bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
ann = bt[bt["fy"].isin(FY_FULL)].groupby("fy")[["pf", "a", "b", "c"]].sum() / 1000
print("=== 年間裁定粗利（円/kW-年） ===")
print(ann.round(0).to_string())

C_PF, C_A, C_B, C_C = "#A6BE0B", "#0079C2", "#5DB6E7", "#D95B20"
fig, ax = plt.subplots(figsize=(9.8, 5.2))
ax.plot(ann.index, ann["pf"], color=C_PF, lw=2.4, marker="o", ms=4.5, label="完全予見PF")
ax.plot(ann.index, ann["a"], color=C_A, lw=2.0, marker="o", ms=4, label="a. 前日価格ナイーブ")
ax.plot(ann.index, ann["b"], color=C_B, lw=2.0, marker="o", ms=4, label="b. 前日予測ベース（残余需要）")
ax.plot(ann.index, ann["c"], color=C_C, lw=2.0, marker="o", ms=4, label="c. 平均価格（気候値・28日）")
ax.set_title("北海道: 年間裁定粗利（円/kW-年、4h・往復効率0.85）", fontsize=13, fontweight="bold", pad=10)
ax.set_xticks(ann.index)
ax.set_xticklabels([f"FY{y}" for y in ann.index], fontsize=9.5)
ax.set_ylabel("円/kW-年", fontsize=10, color=GRAY)
ax.grid(axis="y", color="#DDDDDD", lw=0.6)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(colors=GRAY)
ax.legend(fontsize=9.5, frameon=False, loc="upper left")
fig.text(0.99, 0.005,
         "FY2018は胆振東部地震の欠測480時間を含む。b・cは冒頭30日のウォームアップ後から。データ: JEPX北海道エリアプライス",
         ha="right", fontsize=8, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "annual_backtest_series.png"), dpi=160, bbox_inches="tight")
print("saved annual_backtest_series.png")

# ============================================================
# 2. 帯域分解の年度別時系列
# ============================================================
def band_shares(x):
    x = x.interpolate()
    ma6 = x.rolling(6, center=True, min_periods=3).mean()
    ma24 = x.rolling(24, center=True, min_periods=12).mean()
    ma168 = x.rolling(168, center=True, min_periods=84).mean()
    comps = {"<6時間": x - ma6, "6-24時間": ma6 - ma24,
             "1-7日": ma24 - ma168, ">7日": ma168 - x.mean()}
    tot = x.var()
    return {k: float(v.var() / tot * 100) for k, v in comps.items()}


band_rows = []
for fy in FY_FULL:
    g = hp[hp["fy"] == fy].set_index("ts")["wind"]
    if g.notna().sum() < 5000:
        continue
    sh = band_shares(g)
    sh["fy"] = fy
    band_rows.append(sh)
bands = pd.DataFrame(band_rows).set_index("fy")
print("\n=== 帯域分解の年度別時系列（分散シェア%） ===")
print(bands.round(1).to_string())

C_BANDS = {"<6時間": "#5DB6E7", "6-24時間": "#0079C2", "1-7日": "#176871", ">7日": "#D95B20"}
fig, ax = plt.subplots(figsize=(9.8, 5.2))
for col, color in C_BANDS.items():
    ax.plot(bands.index, bands[col], color=color, lw=2.2, marker="o", ms=4.5, label=col)
ax.set_title("北海道: 風力変動の帯域分解の推移（分散シェア%、年度別）", fontsize=13, fontweight="bold", pad=10)
ax.set_xticks(bands.index)
ax.set_xticklabels([f"FY{y}" for y in bands.index], fontsize=9.5)
ax.set_ylabel("分散シェア（%）", fontsize=10, color=GRAY)
ax.set_ylim(0, None)
ax.grid(axis="y", color="#DDDDDD", lw=0.6)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(colors=GRAY)
ax.legend(fontsize=9.5, frameon=False, ncol=4, loc="upper center")
fig.text(0.99, 0.005,
         "移動平均カスケードによる非直交分解（各年度内で計算、交差項ありシェア合計≠100%）。風力＝フリート集約・制御後出力",
         ha="right", fontsize=8, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "wind_bands_timeseries.png"), dpi=160, bbox_inches="tight")
print("saved wind_bands_timeseries.png")

# ============================================================
# Excel追記
# ============================================================
wb = load_workbook(XLSX)
HDR = PatternFill("solid", fgColor="0079C2")


def put_table(ws, df, r0, c0, index_name):
    heads = [index_name] + list(df.columns)
    for k, h in enumerate(heads):
        cell = ws.cell(row=r0, column=c0 + k, value=h)
        cell.fill = HDR
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center")
    for i, (idx, row) in enumerate(df.iterrows(), start=1):
        ws.cell(row=r0 + i, column=c0, value=f"FY{idx}")
        for k, v in enumerate(row, start=1):
            ws.cell(row=r0 + i, column=c0 + k, value=round(float(v), 1))
    return r0, r0 + len(df)


for sheet in ["年間裁定粗利", "帯域分解時系列"]:
    if sheet in wb.sheetnames:
        del wb[sheet]

ws = wb.create_sheet("年間裁定粗利")
ws["A1"] = "北海道: 年間裁定粗利の時系列（円/kW-年、4h・往復効率0.85・60分粒度）"
ws["A1"].font = Font(bold=True, size=13, color="176871")
ann2 = ann.rename(columns={"pf": "完全予見PF", "a": "a. 前日価格ナイーブ", "b": "b. 前日予測ベース", "c": "c. 平均価格（気候値）"})
r0, r1 = put_table(ws, ann2, 3, 1, "年度")
for col, w in zip("ABCDE", [10, 16, 20, 20, 20]):
    ws.column_dimensions[col].width = w
ch = LineChart()
ch.title = "年間裁定粗利（円/kW-年）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, max_col=5, min_row=r0, max_row=r1)
cats = Reference(ws, min_col=1, min_row=r0 + 1, max_row=r1)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
for ln, color in zip(ch.series, ["A6BE0B", "0079C2", "5DB6E7", "D95B20"]):
    ln.graphicalProperties.line.solidFill = color
    ln.graphicalProperties.line.width = 22000
    ln.smooth = False
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "G3")
ws["A15"] = "注: FY2018は胆振東部地震の欠測480時間を含む。cは過去28日・同曜日区分の平均価格ランク（分解実験: analysis/16・19）"
ws["A15"].font = Font(size=9, color="595959")

ws = wb.create_sheet("帯域分解時系列")
ws["A1"] = "北海道: 風力変動の帯域分解の推移（分散シェア%、年度別・移動平均カスケード）"
ws["A1"].font = Font(bold=True, size=13, color="176871")
r0, r1 = put_table(ws, bands, 3, 1, "年度")
for col, w in zip("ABCDE", [10, 12, 12, 12, 12]):
    ws.column_dimensions[col].width = w
ch = LineChart()
ch.title = "帯域別の分散シェア（%）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, max_col=5, min_row=r0, max_row=r1)
cats = Reference(ws, min_col=1, min_row=r0 + 1, max_row=r1)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
for ln, color in zip(ch.series, ["5DB6E7", "0079C2", "176871", "D95B20"]):
    ln.graphicalProperties.line.solidFill = color
    ln.graphicalProperties.line.width = 22000
    ln.smooth = False
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "G3")
ws["A15"] = "注: 非直交分解（交差項あり、シェア合計≠100%）。各年度内で計算。風力＝フリート集約・制御後出力"
ws["A15"].font = Font(size=9, color="595959")

toc = wb["目次"]
for sheet, desc in [("年間裁定粗利", "追加: PF/a/b/cの年間裁定粗利 時系列（FY2016-25）"),
                    ("帯域分解時系列", "追加: 風力帯域分解の年度別推移")]:
    row = toc.max_row + 1
    toc.cell(row=row, column=1, value=sheet)
    toc.cell(row=row, column=2, value=desc)
wb.save(XLSX)
print("saved xlsx sheets")
