#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道の簡易分析（JEPXエリアプライスのみで可能な範囲）

九州パイロットの主要図（床コマ・ダックカーブ・バックテスト）の北海道版＋
転換提案のカウンター材料（TB4h推移・市場分断の方向転換）をExcel化する。
需給実績が必要な分析（出力制御日数・戦略b・帯域分解）はデータ取得後に追加。

出力: thesis/slides/ゼミ発表_北海道簡易分析.xlsx
"""
import os

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "slides", "ゼミ発表_北海道簡易分析.xlsx")

FONT = "Yu Gothic"
NAVY, BLUE, LBLUE, CORAL, GRAY = "184F95", "2A78D6", "6DA7EC", "EC835A", "68758A"
FY_FULL = list(range(2016, 2026))
ETA = 0.85

j = pd.read_csv(os.path.join(PROC, "jepx_kyushu_30min.csv"), parse_dates=["ts"])
j["fy"] = j["ts"].dt.year - (j["ts"].dt.month < 4).astype(int)
j = j[j["fy"].isin(FY_FULL)].copy()
j["day"] = j["ts"].dt.normalize()
j["hourf"] = j["ts"].dt.hour + j["ts"].dt.minute / 60
j["hour"] = j["ts"].dt.hour

wb = Workbook()
wb.remove(wb.active)
F_TITLE = Font(name=FONT, size=13, bold=True, color="1F3864")
F_NOTE = Font(name=FONT, size=9, color=GRAY)
F_HDR = Font(name=FONT, size=10, bold=True, color="FFFFFF")
F_BODY = Font(name=FONT, size=10)
FILL_HDR = PatternFill("solid", fgColor=NAVY)


def new_sheet(name, title, note):
    ws = wb.create_sheet(name)
    ws["A1"] = title
    ws["A1"].font = F_TITLE
    ws["A2"] = note
    ws["A2"].font = F_NOTE
    return ws


def write_df(ws, df, start_row=4, start_col=1, fmts=None, width=None):
    r0 = start_row
    for ci, col in enumerate(df.columns):
        c = ws.cell(row=r0, column=start_col + ci, value=str(col))
        c.font = F_HDR
        c.fill = FILL_HDR
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(start_col + ci)].width = (width or {}).get(col, max(10, min(18, len(str(col)) * 2 + 4)))
    for ri, (_, row) in enumerate(df.iterrows()):
        for ci, col in enumerate(df.columns):
            v = row[col]
            if isinstance(v, (np.floating, np.integer)):
                v = v.item()
            c = ws.cell(row=r0 + 1 + ri, column=start_col + ci, value=v)
            c.font = F_BODY
            if fmts and col in fmts:
                c.number_format = fmts[col]
    return r0, r0 + len(df)


def style_line(chart, colors, marker=True):
    from openpyxl.chart.marker import Marker
    for s, col in zip(chart.series, colors):
        s.smooth = False
        s.graphicalProperties.line.solidFill = col
        s.graphicalProperties.line.width = 22000
        if marker:
            s.marker = Marker(symbol="circle", size=5)
            s.marker.graphicalProperties.solidFill = col
            s.marker.graphicalProperties.line.solidFill = col
        else:
            s.marker = Marker(symbol="none")


# ============================================================
# h1: 0.01円コマ数（北海道 vs 九州）
# ============================================================
floor_h = j.groupby("fy")["p_hokkaido"].apply(lambda x: int((x <= 0.011).sum()))
floor_k = j.groupby("fy")["p_kyushu"].apply(lambda x: int((x <= 0.011).sum()))
h1 = pd.DataFrame({"年度": [f"FY{y}" for y in FY_FULL],
                   "北海道 0.01円コマ数": floor_h.to_numpy(),
                   "（参考）九州": floor_k.to_numpy()})
ws = new_sheet("h1_床コマ数", "h1 下限価格0.01円への張り付きコマ数（30分コマ・年度計）：北海道は「これから」の初期段階",
               "北海道はFY2020に初出現しFY2022以降に常態化（ピーク861、FY2025は473＝九州の約半分）。北海道の出力制御初回は2022年5月8日。出力制御実施日数の併記は北海道需給実績の取得後に追加。再現: analysis/10")
h0, h1r = write_df(ws, h1)
ch = BarChart()
ch.type = "col"
ch.title = "0.01円/kWh 約定コマ数（年度計）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, max_col=3, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
ch.series[0].graphicalProperties.solidFill = BLUE
ch.series[1].graphicalProperties.solidFill = "CDE2FB"
ch.x_axis.title = "年度"
ch.y_axis.title = "コマ数"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "E4")

# ============================================================
# h2: 時間帯別平均価格カーブ（北海道）
# ============================================================
sel = [2016, 2019, 2023, 2025]
h2 = pd.DataFrame({"時刻": sorted(j["hourf"].unique())})
for fy in sel:
    g = j[j["fy"] == fy].groupby("hourf")["p_hokkaido"].mean()
    h2[f"FY{fy}"] = h2["時刻"].map(g)
ws = new_sheet("h2_ダックカーブ", "h2 時間帯別平均価格カーブ（北海道エリアプライス、円/kWh）",
               "九州（太陽光の深い昼間陥没）と異なり、北海道は昼の谷が浅く夕方・朝のピークが残る形状。FY2023以降に昼の沈み込みが出始めた段階。FY2022（燃料危機）は表示対象外。再現: analysis/10")
h0, h1r = write_df(ws, h2, fmts={c: "0.00" for c in h2.columns})
ch = LineChart()
ch.title = "時間帯別平均価格カーブ（北海道、円/kWh）"
ch.height, ch.width = 11, 20
data = Reference(ws, min_col=2, max_col=1 + len(sel), min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
style_line(ch, ["B7D3F6", "6DA7EC", "2A78D6", "184F95"], marker=False)
ch.x_axis.title = "時刻"
ch.y_axis.title = "円/kWh"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "G4")

# ============================================================
# h3: バックテスト（完全予見・前日価格。戦略bは需給実績待ち）
# ============================================================
P = j.groupby(["day", "hour"])["p_hokkaido"].mean().reset_index().pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
days = P.index
rows = []
for i, d in enumerate(days):
    p = P.loc[d].to_numpy()
    o = np.argsort(p)
    pf = max(0.0, (p[o[-4:]].sum() * ETA - p[o[:4]].sum()) * 1000)
    a = np.nan
    if i >= 1:
        pp = P.loc[days[i - 1]].to_numpy()
        oo = np.argsort(pp)
        a = (p[oo[-4:]].sum() * ETA - p[oo[:4]].sum()) * 1000
    rows.append({"day": d, "pf": pf, "naive": a})
bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
ann = bt[bt["fy"].isin(FY_FULL)].groupby("fy")[["pf", "naive"]].sum() / 1000
# 九州PF（参考）
bt_k = pd.read_csv(os.path.join(PROC, "kyushu_battery_backtest_daily.csv"), parse_dates=["day"])
ann_k = bt_k[bt_k["fy"].isin(FY_FULL)].groupby("fy")["pf"].sum() / 1000
h3 = pd.DataFrame({
    "年度": [f"FY{y}" for y in ann.index],
    "北海道 完全予見（円/kW-年）": ann["pf"],
    "北海道 a.前日価格（円/kW-年）": ann["naive"],
    "（参考）九州 完全予見": ann_k.reindex(ann.index).to_numpy(),
})
ws = new_sheet("h3_バックテスト", "h3 4時間蓄電池のスポット裁定価値（北海道・実績バックテスト）",
               "仕様は九州と同一（1MW/4MWh・効率85%・日次1サイクル・60分粒度・下限推定）。b.前日予測ベースは北海道需給実績（需要・太陽光）の取得後に追加。a捕捉率は数式列（=C÷B）。再現: analysis/10")
h0, h1r = write_df(ws, h3, fmts={c: "#,##0" for c in h3.columns if c != "年度"})
ws.cell(row=h0, column=5, value="a捕捉率").font = F_HDR
ws.cell(row=h0, column=5).fill = FILL_HDR
for i in range(h0 + 1, h1r + 1):
    ws.cell(row=i, column=5, value=f"=C{i}/B{i}").number_format = "0%"
    ws.cell(row=i, column=5).font = F_BODY
ch = LineChart()
ch.title = "年間裁定粗利（円/kW-年）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, max_col=4, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
style_line(ch, [NAVY, LBLUE, CORAL])
ch.series[2].graphicalProperties.line.dashStyle = "dash"
ch.x_axis.title = "年度"
ch.y_axis.title = "円/kW-年"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "G4")

# ============================================================
# h4: TB4hスプレッドの推移（北海道 vs 九州）
# ============================================================
def tb4h(col):
    t = j.groupby(["fy", "day"])[col].apply(lambda x: x.sort_values().iloc[-8:].mean() - x.sort_values().iloc[:8].mean())
    g = t.groupby(level="fy")
    return g.median(), g.apply(lambda x: x.quantile(.25)), g.apply(lambda x: x.quantile(.75))

mh, q1h, q3h = tb4h("p_hokkaido")
mk, _, _ = tb4h("p_kyushu")
h4 = pd.DataFrame({
    "年度": [f"FY{y}" for y in FY_FULL],
    "北海道 25%分位": q1h.to_numpy(), "北海道 中央値": mh.to_numpy(), "北海道 75%分位": q3h.to_numpy(),
    "（参考）九州 中央値": mk.to_numpy(),
})
ws = new_sheet("h4_TB4hスプレッド", "h4 日次TB4hスプレッドの年度推移（円/kWh）：北海道は九州型の単調拡大とは異なる履歴",
               "各日の48コマのうち上位8コマ平均−下位8コマ平均。北海道はFY2016から高スプレッド（冬季逼迫型）→FY2020に底→再拡大という経路で、太陽光起因の九州とドライバーが異なる。再現: analysis/10")
h0, h1r = write_df(ws, h4, fmts={c: "0.00" for c in h4.columns if c != "年度"})
ch = LineChart()
ch.title = "TB4hスプレッド（中央値と四分位、円/kWh）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, max_col=5, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
style_line(ch, ["B7D3F6", "184F95", "B7D3F6", "EC835A"])
ch.series[3].graphicalProperties.line.dashStyle = "dash"
ch.x_axis.title = "年度"
ch.y_axis.title = "円/kWh"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "G4")

# ============================================================
# h5: 市場分断の方向転換（高値分断→安値分断）
# ============================================================
h5 = pd.DataFrame({
    "年度": [f"FY{y}" for y in FY_FULL],
    "高値分断率%（北海道>システム）": j.assign(s=j["p_hokkaido"] > j["p_system"] + 0.01).groupby("fy")["s"].mean().mul(100).to_numpy(),
    "安値分断率%（北海道<システム）": j.assign(s=j["p_hokkaido"] < j["p_system"] - 0.01).groupby("fy")["s"].mean().mul(100).to_numpy(),
    "北海道−東北 平均値差（円/kWh）": (j["p_hokkaido"] - j["p_tohoku"]).groupby(j["fy"]).mean().to_numpy(),
})
ws = new_sheet("h5_分断の方向転換", "h5 市場分断の方向転換：「逼迫の高値エリア」から「余剰閉じ込めの安値方向」へ",
               "高値分断率はFY2016-19の87〜92%から約60%へ低下、安値分断率は1〜5%から30%前後へ増加。北海道−東北の平均値差も+2.6〜4.6円→ほぼ0円へ（双方向に割れる構造に変化）。間接送電権の北海道→東北方向の商品化（2026年度）と整合。再現: analysis/10")
h0, h1r = write_df(ws, h5, fmts={c: "0.0" for c in h5.columns if c != "年度"})
ch = LineChart()
ch.title = "分断率の推移（%）"
ch.height, ch.width = 10, 15
data = Reference(ws, min_col=2, max_col=3, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
style_line(ch, [CORAL, BLUE])
ch.x_axis.title = "年度"
ch.y_axis.title = "コマ比率（%）"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "F4")
ch2 = BarChart()
ch2.type = "col"
ch2.title = "北海道−東北の平均値差（円/kWh）"
ch2.height, ch2.width = 10, 15
data = Reference(ws, min_col=4, min_row=h0, max_row=h1r)
ch2.add_data(data, titles_from_data=True)
ch2.set_categories(cats)
ch2.series[0].graphicalProperties.solidFill = NAVY
ch2.legend = None
ch2.x_axis.title = "年度"
ch2.y_axis.title = "円/kWh"
ch2.x_axis.delete = False
ch2.y_axis.delete = False
ws.add_chart(ch2, "F25")

# ============================================================
# 目次
# ============================================================
toc = wb.create_sheet("目次", 0)
toc["A1"] = "北海道 簡易分析（JEPXエリアプライスのみで実施可能な範囲）"
toc["A1"].font = Font(name=FONT, size=14, bold=True, color="1F3864")
toc["A2"] = "目的:「北海道でも面白い結果が得られるのか」への回答材料。九州と同一仕様のパイプラインをエリアプライス列の切替のみで適用。"
toc["A2"].font = F_NOTE
toc["A3"] = "生成: thesis/analysis/10_hokkaido_quick_xlsx.py（2026年7月27日）。需給実績が必要な分析（出力制御日数・戦略b・風力帯域分解・需給内訳）は北海道需給実績CSV取得後に追加。"
toc["A3"].font = F_NOTE
rows = [
    ("シート", "内容", "キーメッセージ"),
    ("h1_床コマ数", "0.01円コマ数（北海道 vs 九州）", "FY2020初出現→FY2022以降常態化。九州の約半分＝「これから」の初期段階"),
    ("h2_ダックカーブ", "時間帯別平均価格カーブ（北海道）", "昼の谷が浅く朝夕ピークが残る（九州と形状が異なる）。昼の沈みはFY2023以降に出現"),
    ("h3_バックテスト", "裁定価値（完全予見・前日価格）", "直近0.96〜1.15万円/kW-年で九州と同水準。ただしa捕捉率66〜69%は九州（77〜80%）より低い＝形状の予測可能性が低い"),
    ("h4_TB4hスプレッド", "スプレッドの年度推移", "FY2016から高水準（冬季逼迫型）→FY2020底→再拡大。九州型の太陽光単調拡大と経路が異なる"),
    ("h5_分断の方向転換", "市場分断の方向と値差", "高値分断87〜92%→約60%、安値分断1〜5%→30%前後。余剰閉じ込め型への転換が既に進行"),
]
for ri, row in enumerate(rows):
    for ci, v in enumerate(row):
        c = toc.cell(row=5 + ri, column=1 + ci, value=v)
        if ri == 0:
            c.font = F_HDR
            c.fill = FILL_HDR
        else:
            c.font = F_BODY
for col, w in [("A", 20), ("B", 36), ("C", 80)]:
    toc.column_dimensions[col].width = w

wb.save(OUT)
print("saved", OUT)
