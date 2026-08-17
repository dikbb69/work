#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""風力は水準を下げるがスプレッドを広げない — 発電量×価格の関係（季節別、太陽光と対比）

各季節で日次発電量（制御前）の五分位に日をグループ化し、
  ・日平均価格（水準＝MOE）
  ・日内TB4hスプレッド（形状・ボラティリティの代理）
を横軸=日次発電量（GWh/日）でプロット。風力: 水準↓・スプレッド→ ／ 太陽光: スプレッド↑ を対比。

出力: figures/hokkaido/gen_vs_price_shape.png ＋ 図表データ.xlsx「量と価格の関係」シート
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
C_LEVEL, C_SPREAD = "#0079C2", "#D95B20"

p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
p = p[(p["ts"] >= "2023-04-01") & (p["ts"] < "2026-04-01")].dropna(subset=["p_hokkaido"]).copy()
p["day"] = p["ts"].dt.normalize()
p["hour"] = p["ts"].dt.hour
p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
cnt = p.groupby("day")["hour"].count()
p = p[p["day"].isin(cnt[cnt == 24].index)]

P = p.pivot(index="day", columns="hour", values="p_hokkaido")
srt = np.sort(P.to_numpy(), axis=1)
daily = pd.DataFrame(index=P.index)
daily["mean_p"] = P.mean(axis=1)
daily["tb4"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
daily["sd"] = P.std(axis=1)
daily["wind_gwh"] = p.groupby("day")["wind_pre"].sum() / 1000
daily["solar_gwh"] = p.groupby("day")["solar_pre"].sum() / 1000
daily["month"] = daily.index.month

SEASONS = [
    ("需要期・夏（7-8月）", [7, 8]),
    ("需要期・冬（12-2月）", [12, 1, 2]),
    ("不需要期（4-5・10-11月）", [4, 5, 10, 11]),
]


def quintile_curve(d, xcol):
    q = pd.qcut(d[xcol], 5, labels=False, duplicates="drop")
    g = d.groupby(q).agg(x=(xcol, "mean"), mean_p=("mean_p", "mean"),
                         tb4=("tb4", "mean"), sd=("sd", "mean"))
    return g

fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.0), sharey=True)
results = {}
for r, (res, xcol, rowlab) in enumerate([("風力", "wind_gwh", "風力の日次発電量（GWh/日）"),
                                         ("太陽光", "solar_gwh", "太陽光の日次発電量（GWh/日）")]):
    for c0, (name, months) in enumerate(SEASONS):
        d = daily[daily["month"].isin(months)]
        g = quintile_curve(d, xcol)
        results[(res, name)] = g
        ax = axes[r, c0]
        ax.plot(g["x"], g["mean_p"], color=C_LEVEL, lw=2.3, marker="o", ms=5, label="日平均価格（水準）")
        ax.plot(g["x"], g["tb4"], color=C_SPREAD, lw=2.3, marker="s", ms=5, label="日内TB4hスプレッド（形状）")
        if r == 0:
            ax.set_title(name, fontsize=12, pad=8)
        ax.set_xlabel(rowlab if r == 1 else "", fontsize=9.5, color=GRAY)
        if r == 0:
            ax.set_xlabel(rowlab, fontsize=9.5, color=GRAY)
        ax.grid(axis="y", color="#DDDDDD", lw=0.6)
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
        ax.tick_params(colors=GRAY, labelsize=9)
        # 傾き注記（Q1→Q5の変化）
        dlv = g["mean_p"].iloc[-1] - g["mean_p"].iloc[0]
        dsp = g["tb4"].iloc[-1] - g["tb4"].iloc[0]
        ax.text(0.03, 0.04, f"Q1→Q5: 水準{dlv:+.1f}円 / スプレッド{dsp:+.1f}円",
                transform=ax.transAxes, fontsize=9, color=GRAY)
axes[0, 0].set_ylabel("風力\n（円/kWh）", fontsize=10.5, color=GRAY)
axes[1, 0].set_ylabel("太陽光\n（円/kWh）", fontsize=10.5, color=GRAY)
axes[0, 0].legend(fontsize=9.5, frameon=False, loc="upper right")
fig.suptitle("風力は「水準」だけを下げ、スプレッド（形状）を変えない — 太陽光は不需要期にスプレッドを拡大する（FY2023-25）",
             fontsize=13.5, fontweight="bold", y=1.0)
fig.text(0.995, -0.015,
         "各季節で日次発電量（制御前）の五分位に日をグループ化し、群平均をプロット。TB4h＝上位4h平均−下位4h平均。データ: JEPX・北海道電力NW需給実績",
         ha="right", fontsize=8, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "gen_vs_price_shape.png"), dpi=160, bbox_inches="tight")
print("saved gen_vs_price_shape.png")

for k, g in results.items():
    print(k, "| 水準Q1→Q5:", round(g["mean_p"].iloc[-1] - g["mean_p"].iloc[0], 2),
          "| TB4h Q1→Q5:", round(g["tb4"].iloc[-1] - g["tb4"].iloc[0], 2))

# ---------- Excel ----------
wb = load_workbook(XLSX)
if "量と価格の関係" in wb.sheetnames:
    del wb["量と価格の関係"]
ws = wb.create_sheet("量と価格の関係")
ws["A1"] = "日次発電量（五分位）× 日平均価格・日内TB4hスプレッド（FY2023-25、季節別）"
ws["A1"].font = Font(bold=True, size=13, color="176871")
HDR = PatternFill("solid", fgColor="0079C2")

r0 = 3
for res in ("風力", "太陽光"):
    ws.cell(row=r0, column=1, value=f"■ {res}").font = Font(bold=True, size=11)
    r0 += 1
    heads = ["五分位"]
    for name, _ in SEASONS:
        s_ = name.split("（")[0]
        heads += [f"{s_} 発電量GWh", f"{s_} 平均価格", f"{s_} TB4h", f"{s_} 日内SD"]
    for k, h in enumerate(heads, start=1):
        cell = ws.cell(row=r0, column=k, value=h)
        cell.fill = HDR
        cell.font = Font(bold=True, color="FFFFFF", size=9)
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    for qi in range(5):
        row = [f"Q{qi + 1}"]
        for name, _ in SEASONS:
            g = results[(res, name)]
            if qi < len(g):
                row += [round(g["x"].iloc[qi], 1), round(g["mean_p"].iloc[qi], 2),
                        round(g["tb4"].iloc[qi], 2), round(g["sd"].iloc[qi], 2)]
            else:
                row += [None] * 4
        for k, v in enumerate(row, start=1):
            ws.cell(row=r0 + 1 + qi, column=k, value=v)
    r0 += 8

ws.column_dimensions["A"].width = 8
for col in "BCDEFGHIJKLM":
    ws.column_dimensions[col].width = 13

# チャート: 風力・太陽光それぞれ TB4hスプレッド（3季節）
anchors = {"風力": "A21", "太陽光": "H21"}
for res, base_row in [("風力", 4), ("太陽光", 12)]:
    ch = LineChart()
    ch.title = f"{res}: 日内TB4hスプレッド（円/kWh）× 発電量五分位"
    ch.height, ch.width = 9, 12
    for si in range(3):
        col_tb = 2 + si * 4 + 2  # TB4h列
        data = Reference(ws, min_col=col_tb, min_row=base_row, max_row=base_row + 5)
        ch.add_data(data, titles_from_data=True)
    cats = Reference(ws, min_col=1, min_row=base_row + 1, max_row=base_row + 5)
    ch.set_categories(cats)
    for ln, color in zip(ch.series, ["D95B20", "176871", "0079C2"]):
        ln.graphicalProperties.line.solidFill = color
        ln.graphicalProperties.line.width = 22000
        ln.smooth = False
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ws.add_chart(ch, anchors[res])
ws.cell(row=36, column=1, value="注: 五分位＝各季節内の日次発電量（制御前）による5等分。TB4h＝上位4h平均−下位4h平均。風力のTB4hはほぼ平坦（形状不変）、太陽光は不需要期に急拡大").font = Font(size=9, color="595959")

toc = wb["目次"]
row = toc.max_row + 1
toc.cell(row=row, column=1, value="量と価格の関係")
toc.cell(row=row, column=2, value="追加: 発電量五分位×価格水準・TB4hスプレッド（風力vs太陽光・季節別）")
wb.save(XLSX)
print("saved xlsx 量と価格の関係")
