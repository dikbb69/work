#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""併設（BTM）蓄電池を研究対象に加える根拠のデータ整理（北海道・風力）

  1. 風力出力制御の実績: 抑制率（エネルギーベース）・抑制時間の推移
  2. 抑制発生時間のエリア価格内訳: 床 / 中間 / 5円超
     → 5円超の抑制 ＝ エリア価格に映らないローカル制約（BTM固有価値の証拠）
  3. 併設蓄電池の抑制回避価値の上限試算（抑制率シナリオ別）

出力: figures/hokkaido/btm_case.png ＋ 図表データ.xlsx「併設BTM検討」シート
"""
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference
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

p = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
p["fy"] = p["ts"].dt.year - (p["ts"].dt.month < 4).astype(int)

# ---------- 1. 抑制実績 ----------
def curt_stats(g):
    wc = g["wind_curt"].fillna(0)
    w = g["wind"].fillna(0)
    return pd.Series({
        "抑制率%": wc.sum() / max(1.0, w.sum() + wc.sum()) * 100,
        "抑制時間h": int((wc > 0).sum()),
    })

t1 = p[p["fy"] >= 2022].groupby("fy").apply(curt_stats)
t1["抑制率%"] = t1["抑制率%"].round(2)
print("=== 風力抑制の実績 ===")
print(t1.to_string())

# ---------- 2. 抑制時間の価格内訳 ----------
c = p[p["wind_curt"].fillna(0) > 0].dropna(subset=["p_hokkaido"])
rows2 = []
for fy in (2025, 2026):
    x = c[c["fy"] == fy]["p_hokkaido"]
    rows2.append({"年度": f"FY{fy}", "床(≤0.01円)%": round((x <= 0.011).mean() * 100, 1),
                  "0.01〜5円%": round(((x > 0.011) & (x <= 5)).mean() * 100, 1),
                  "5円超%": round((x > 5).mean() * 100, 1), "抑制時間h": len(x)})
t2 = pd.DataFrame(rows2)
print("\n=== 抑制発生時間のエリア価格内訳 ===")
print(t2.to_string(index=False))

# ---------- 3. 回避価値の上限試算 ----------
CF = 0.26          # 実測cf_wind（FY2024-25）
FIP = 14.0         # 陸上風力の基準価格めやす（円/kWh、2024年度水準）
scen = [("現状（FY2026上期実測）", 1.35), ("3%（数年内の到達想定）", 3.0),
        ("5%", 5.0), ("8%（九州太陽光FY2023実績並み）", 8.0)]
rows3 = []
for name, r in scen:
    val_kw_wind = 8760 * CF * r / 100 * FIP
    rows3.append({"抑制率シナリオ": name, "抑制電力量(kWh/kW風力-年)": round(8760 * CF * r / 100, 0),
                  "回避価値上限(円/kW風力-年)": round(val_kw_wind, 0),
                  "併設0.64kWh/kWあたり(円/kWh蓄電池-年)": round(val_kw_wind / 0.64, 0)})
t3 = pd.DataFrame(rows3)
print("\n=== 併設蓄電池の抑制回避価値（上限試算） ===")
print(t3.to_string(index=False))

# ---------- PNG（2パネル） ----------
C_BLUE, C_ORANGE, C_TEAL, C_LB = "#0079C2", "#D95B20", "#176871", "#5DB6E7"
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.6))

fys = [f"FY{y}" for y in t1.index]
b = ax1.bar(fys, t1["抑制率%"], color=[C_LB] * (len(fys) - 1) + [C_ORANGE], width=0.55)
for x, v in zip(fys, t1["抑制率%"]):
    ax1.text(x, v + 0.03, f"{v:.2f}%", ha="center", fontsize=10, color=C_TEAL, fontweight="bold")
ax1.set_title("風力の出力制御率（エネルギーベース）", fontsize=12.5)
ax1.set_ylabel("抑制率（%）", fontsize=10, color=GRAY)
ax1.text(len(fys) - 1, t1["抑制率%"].iloc[-1] / 2, "4-6月\nのみ", ha="center", fontsize=8.5, color="white")

labels = t2["年度"]
bot = np.zeros(len(t2))
for col, color, lab in [("床(≤0.01円)%", C_LB, "床（0.01円）"), ("0.01〜5円%", C_BLUE, "0.01〜5円"),
                        ("5円超%", C_ORANGE, "5円超")]:
    ax2.bar(labels, t2[col], bottom=bot, color=color, width=0.45, label=lab)
    for i, v in enumerate(t2[col]):
        if v > 5:
            ax2.text(i, bot[i] + v / 2, f"{v:.0f}%", ha="center", va="center", fontsize=9.5,
                     color="white", fontweight="bold")
    bot += t2[col].to_numpy()
ax2.set_title("抑制発生時間のエリア価格内訳", fontsize=12.5)
ax2.set_ylabel("構成比（%）", fontsize=10, color=GRAY)
ax2.legend(fontsize=9, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3)

for ax in (ax1, ax2):
    ax.grid(axis="y", color="#DDDDDD", lw=0.6)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=9.5)
fig.suptitle("風力の出力制御は「立ち上がり」段階 — しかも1割強はエリア価格が高いのに抑制されている（ローカル制約）",
             fontsize=13, fontweight="bold", y=1.02)
fig.text(0.995, -0.06,
         "抑制＝需給実績の風力抑制量>0の時間。5円超での抑制はエリア余剰でなくローカル系統制約・下げ代制約を示唆＝エリア価格に映らないBTM固有の価値",
         ha="right", fontsize=8, color=GRAY)
fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "btm_case.png"), dpi=160, bbox_inches="tight")
print("saved btm_case.png")

# ---------- Excel ----------
wb = load_workbook(XLSX)
if "併設BTM検討" in wb.sheetnames:
    del wb["併設BTM検討"]
ws = wb.create_sheet("併設BTM検討")
ws["A1"] = "併設（BTM）蓄電池を対象に加える根拠 — 風力抑制の実績・価格内訳・回避価値試算"
ws["A1"].font = Font(bold=True, size=13, color="176871")
HDR = PatternFill("solid", fgColor="0079C2")


def put(ws, df, r0, title):
    ws.cell(row=r0, column=1, value=title).font = Font(bold=True, size=11)
    r0 += 1
    for k, col in enumerate(df.columns, start=1):
        cell = ws.cell(row=r0, column=k, value=col)
        cell.fill = HDR
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center")
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        for k, v in enumerate(row, start=1):
            ws.cell(row=r0 + i, column=k, value=v)
    return r0 + len(df) + 2


t1x = t1.reset_index().rename(columns={"fy": "年度"})
t1x["年度"] = t1x["年度"].map(lambda y: f"FY{y}" + ("（4-6月のみ）" if y == 2026 else ""))
r = put(ws, t1x, 3, "① 風力の出力制御実績")
r = put(ws, t2, r, "② 抑制発生時間のエリア価格内訳（5円超＝ローカル制約の示唆）")
r = put(ws, t3, r, "③ 併設蓄電池の抑制回避価値の上限試算（cf26%・FIP14円/kWh・全量回収仮定）")
for col, w in zip("ABCDE", [30, 22, 24, 30, 14]):
    ws.column_dimensions[col].width = w
ch = BarChart()
ch.type = "col"
ch.title = "回避価値上限（円/kW風力-年）"
ch.height, ch.width = 8, 12
r3h = r - len(t3) - 1
data = Reference(ws, min_col=3, min_row=r3h, max_row=r3h + len(t3))
cats = Reference(ws, min_col=1, min_row=r3h + 1, max_row=r3h + len(t3))
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
ch.legend = None
ws.add_chart(ch, "G3")
ws.cell(row=r, column=1, value="注: 回避価値は「蓄電池が抑制分を全量吸収できる」場合の上限。実際は容量制約（系統WG併設前提: 風力1kWあたり0.64kWh）で長時間イベントを取り切れない。5円超の抑制はエリア価格に映らないローカル価値のため、エリア価格ベースのπ_spotはBTM価値を過小評価する").font = Font(size=9, color="595959")
toc = wb["目次"]
row = toc.max_row + 1
toc.cell(row=row, column=1, value="併設BTM検討")
toc.cell(row=row, column=2, value="追加: BTM対象化の根拠（抑制実績・価格内訳・回避価値試算）")
wb.save(XLSX)
print("saved xlsx 併設BTM検討")
