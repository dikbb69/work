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

# 需給実績パネル（11_build_area_panels.py の出力。2026-07-27に取得・検証済み）
hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["hour"] = hp["ts"].dt.hour
hp["day"] = hp["ts"].dt.normalize()
hp["curt_total"] = hp["solar_curt"].fillna(0) + hp["wind_curt"].fillna(0)
kp = pd.read_csv(os.path.join(PROC, "kyushu_hourly_panel.csv"), parse_dates=["ts"])
BLACKOUT_NOTE = "2018年9月7〜26日は胆振東部地震後の取引停止により北海道エリアプライスが欠損（480時間）"

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
curt_days = hp[hp["fy"].isin(FY_FULL)].groupby("fy").apply(lambda g: int((g.groupby("day")["curt_total"].sum() > 0).sum()))
curt_gwh = hp[hp["fy"].isin(FY_FULL)].groupby("fy")["curt_total"].sum() / 1000
h1 = pd.DataFrame({"年度": [f"FY{y}" for y in FY_FULL],
                   "北海道 0.01円コマ数": floor_h.to_numpy(),
                   "出力制御実施日数": curt_days.to_numpy(),
                   "出力制御量（GWh）": curt_gwh.round(1).to_numpy(),
                   "（参考）九州 0.01円コマ数": floor_k.to_numpy()})
ws = new_sheet("h1_床コマ数", "h1 下限価格0.01円への張り付きと出力制御：北海道は「これから」の初期段階",
               "北海道はFY2020に床コマ初出現・出力制御はFY2022（2022年5月8日）開始。FY2025の床コマ473は九州の約半分。出力制御は需給実績（太陽光・風力抑制量>0の日数）より。再現: analysis/10・11")
h0, h1r = write_df(ws, h1)
ch = BarChart()
ch.type = "col"
ch.title = "0.01円/kWh 約定コマ数（年度計）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
data = Reference(ws, min_col=5, min_row=h0, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
ch.series[0].graphicalProperties.solidFill = BLUE
ch.series[1].graphicalProperties.solidFill = "CDE2FB"
ch.x_axis.title = "年度"
ch.y_axis.title = "コマ数"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "G4")
ch2 = BarChart()
ch2.type = "col"
ch2.title = "出力制御実施日数（北海道）"
ch2.height, ch2.width = 11, 12
data = Reference(ws, min_col=3, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch2.add_data(data, titles_from_data=True)
ch2.set_categories(cats)
ch2.series[0].graphicalProperties.solidFill = CORAL
ch2.legend = None
ch2.x_axis.title = "年度"
ch2.y_axis.title = "日数"
ch2.x_axis.delete = False
ch2.y_axis.delete = False
ws.add_chart(ch2, "G26")

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
# h3: バックテスト（完全予見・a前日価格・b前日予測・b'風力込み予測）
# ============================================================
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
D = hp.pivot(index="day", columns="hour", values="demand")
S = hp.pivot(index="day", columns="hour", values="solar")
W = hp.pivot(index="day", columns="hour", values="wind")
days = P.index
all_days = D.index
wk = pd.Series(all_days.dayofweek >= 5, index=all_days)


def margin(p, dis, chg):
    return (p[list(dis)].sum() * ETA - p[list(chg)].sum()) * 1000


rows = []
for i, d in enumerate(days):
    p = P.loc[d]
    o = p.sort_values()
    pf = max(0.0, margin(p, o.index[-4:], o.index[:4]))
    a = b = b2 = np.nan
    if i >= 1:
        oo = P.loc[days[i - 1]].sort_values()
        a = margin(p, oo.index[-4:], oo.index[:4])
    jj = all_days.get_loc(d)
    if jj >= 30:
        hist = all_days[max(0, jj - 29):jj - 1]
        same = [h for h in hist if wk[h] == wk[d]]
        if len(same) >= 5:
            dem_f = D.loc[same].mean()
            win7 = all_days[jj - 8:jj - 1]
            sol_f = S.loc[win7].mean()
            net = (dem_f - sol_f).sort_values()
            b = margin(p, net.index[-4:], net.index[:4])
            net2 = (dem_f - sol_f - W.loc[win7].mean()).sort_values()
            b2 = margin(p, net2.index[-4:], net2.index[:4])
    rows.append({"day": d, "pf": pf, "naive": a, "fcst": b, "fcst_w": b2})
bt = pd.DataFrame(rows)
bt["fy"] = bt["day"].dt.year - (bt["day"].dt.month < 4).astype(int)
ann = bt[bt["fy"].isin(FY_FULL)].groupby("fy")[["pf", "naive", "fcst", "fcst_w"]].sum() / 1000
bt_k = pd.read_csv(os.path.join(PROC, "kyushu_battery_backtest_daily.csv"), parse_dates=["day"])
bt_k["fy"] = bt_k["day"].dt.year - (bt_k["day"].dt.month < 4).astype(int)
ann_k = bt_k[bt_k["fy"].isin(FY_FULL)].groupby("fy")["pf"].sum() / 1000
h3 = pd.DataFrame({
    "年度": [f"FY{y}" for y in ann.index],
    "北海道 完全予見（円/kW-年）": ann["pf"],
    "a. 前日価格（円/kW-年）": ann["naive"],
    "b. 前日予測 需要−太陽光（円/kW-年）": ann["fcst"],
    "b'. 前日予測 −風力持続込み（円/kW-年）": ann["fcst_w"],
    "（参考）九州 完全予見": ann_k.reindex(ann.index).to_numpy(),
})
ws = new_sheet("h3_バックテスト", "h3 4時間蓄電池のスポット裁定価値（北海道・実績バックテスト）",
               "仕様は九州と同一（1MW/4MWh・効率85%・日次1サイクル・60分粒度・下限推定）。b=需要（平日/休日別28日平均）−太陽光（7日平均）の予測残余需要ランク、b'=さらに風力の7日持続予測を控除。捕捉率は数式列。" + BLACKOUT_NOTE + "。再現: analysis/10・11")
h0, h1r = write_df(ws, h3, fmts={c: "#,##0" for c in h3.columns if c != "年度"})
for ci, lab, src_col in [(7, "a捕捉率", "C"), (8, "b捕捉率", "D"), (9, "b'捕捉率", "E")]:
    cell = ws.cell(row=h0, column=ci, value=lab)
    cell.font = F_HDR
    cell.fill = FILL_HDR
    for i in range(h0 + 1, h1r + 1):
        ws.cell(row=i, column=ci, value=f"={src_col}{i}/B{i}").number_format = "0%"
        ws.cell(row=i, column=ci).font = F_BODY
ch = LineChart()
ch.title = "年間裁定粗利（円/kW-年）"
ch.height, ch.width = 11, 18
data = Reference(ws, min_col=2, max_col=6, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
style_line(ch, [NAVY, LBLUE, CORAL, "F0B45A", "8496AD"])
ch.series[4].graphicalProperties.line.dashStyle = "dash"
ch.x_axis.title = "年度"
ch.y_axis.title = "円/kW-年"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "H4")
print("h3 北海道 b捕捉率:", (ann["fcst"] / ann["pf"] * 100).round(0).to_dict())
print("h3 北海道 b'捕捉率:", (ann["fcst_w"] / ann["pf"] * 100).round(0).to_dict())

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
# h6: 風力の帯域分解（北海道 vs 九州）＋エネルギーシェア実測
# ============================================================
def band_shares(x):
    x = x.interpolate()
    ma6 = x.rolling(6, center=True, min_periods=3).mean()
    ma24 = x.rolling(24, center=True, min_periods=12).mean()
    ma168 = x.rolling(168, center=True, min_periods=84).mean()
    comps = {"<6時間": x - ma6, "6–24時間": ma6 - ma24,
             "1–7日": ma24 - ma168, ">7日": ma168 - x.mean()}
    tot = x.var()
    return {k: float(v.var() / tot * 100) for k, v in comps.items()}


hw = hp[(hp["ts"] >= "2022-04-01") & (hp["ts"] < "2026-04-01")].set_index("ts")
kw = kp[(kp["ts"] >= "2022-04-01") & (kp["ts"] < "2026-04-01")].set_index("ts")
sh_hw, sh_hs = band_shares(hw["wind"]), band_shares(hw["solar"])
sh_kw = band_shares(kw["wind"])
h6 = pd.DataFrame({
    "帯域": list(sh_hw.keys()),
    "北海道 風力（%）": list(sh_hw.values()),
    "九州 風力（%）": [sh_kw[k] for k in sh_hw],
    "北海道 太陽光（%）": [sh_hs[k] for k in sh_hw],
})
# 低出力イベント（フリート出力が期間平均の20%未満の連続時間）
x = hw["wind"].interpolate()
low = (x < x.mean() * 0.2)
runs = (low != low.shift()).cumsum()
durs = low.groupby(runs).sum()
durs = durs[durs > 0]
# エネルギーシェア実測
shares = hp[hp["fy"].isin(FY_FULL)].groupby("fy").apply(
    lambda g: pd.Series({"風力シェア%": g["wind"].sum() / g["demand"].sum() * 100,
                         "太陽光シェア%": g["solar"].sum() / g["demand"].sum() * 100}))
h6b = pd.DataFrame({"年度": [f"FY{y}" for y in shares.index],
                    "風力シェア（%）": shares["風力シェア%"].round(1).to_numpy(),
                    "太陽光シェア（%）": shares["太陽光シェア%"].round(1).to_numpy()})
ws = new_sheet("h6_風力帯域分解", "h6 北海道の風力変動も「数日帯域」が支配的 — 九州の実測が北海道でも再現",
               "移動平均カスケードによる非直交帯域分解（FY2022-25、交差項ありシェア合計≠100%）。低出力イベント（平均の20%未満）: "
               + f"中央値{durs.median():.0f}h・p90 {durs.quantile(.9):.0f}h・最長{durs.max():.0f}h。右表は風力・太陽光の対エリア需要エネルギーシェア実測。再現: analysis/10・11")
h0, h1r = write_df(ws, h6, fmts={c: "0.0" for c in h6.columns if c != "帯域"})
b0, b1 = write_df(ws, h6b, start_col=7)
ch = BarChart()
ch.type = "col"
ch.title = "変動エネルギーの時間スケール配分（分散シェア%）"
ch.height, ch.width = 11, 16
data = Reference(ws, min_col=2, max_col=4, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
for s, col in zip(ch.series, [NAVY, LBLUE, CORAL]):
    s.graphicalProperties.solidFill = col
ch.x_axis.title = "帯域"
ch.y_axis.title = "分散シェア（%）"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "B12")
ch2 = LineChart()
ch2.title = "風力・太陽光のエネルギーシェア実測（対エリア需要、%）"
ch2.height, ch2.width = 11, 14
data = Reference(ws, min_col=8, max_col=9, min_row=b0, max_row=b1)
cats = Reference(ws, min_col=7, min_row=b0 + 1, max_row=b1)
ch2.add_data(data, titles_from_data=True)
ch2.set_categories(cats)
style_line(ch2, [BLUE, CORAL])
ch2.x_axis.title = "年度"
ch2.y_axis.title = "%"
ch2.x_axis.delete = False
ch2.y_axis.delete = False
ws.add_chart(ch2, "J12")
print("h6 北海道風力帯域:", {k: round(v, 1) for k, v in sh_hw.items()})
print("h6 低出力イベント: 中央値", durs.median(), "p90", durs.quantile(.9), "最長", durs.max())

# ============================================================
# h7: 風力×エリアプライスの分位点回帰（Sakaguchi & Fujii 再現・更新）
# ============================================================
import statsmodels.api as sm

reg = hp.dropna(subset=["p_hokkaido", "wind", "solar", "demand"]).copy()
for c in ["wind", "solar", "demand"]:
    reg[c + "_gw"] = reg[c] / 1000
QS = [round(q, 1) for q in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
res = {"分位点": QS}
for label, fys in [("FY2016-19", range(2016, 2020)), ("FY2023-25", range(2023, 2026))]:
    sub = reg[reg["fy"].isin(fys)]
    X = sm.add_constant(sub[["wind_gw", "solar_gw", "demand_gw"]])
    coefs = []
    for q in QS:
        m = sm.QuantReg(sub["p_hokkaido"], X).fit(q=q, max_iter=2000)
        coefs.append(m.params["wind_gw"])
    res[f"風力係数 {label}（円/kWh per GW）"] = [round(c, 2) for c in coefs]
h7 = pd.DataFrame(res)
ws = new_sheet("h7_分位点回帰", "h7 風力1GWあたりの価格押し下げ効果（分位点回帰）— Sakaguchi & Fujii (2021) の再現と更新",
               "被説明変数=北海道エリアプライス（60分）、説明変数=風力・太陽光・需要（GW）＋定数。係数は風力のメリットオーダー効果（負=押し下げ）。"
               "FY2016-19はSakaguchi & Fujii (2021)の対象期間の再現、FY2023-25は風力倍増後の更新。燃料価格水準の違いによるスケール差に注意（本番はHAR-X等で精緻化）。再現: analysis/10・11")
h0, h1r = write_df(ws, h7, fmts={c: "0.00" for c in h7.columns if c != "分位点"})
ch = LineChart()
ch.title = "風力係数の分位点プロファイル（円/kWh per GW）"
ch.height, ch.width = 11, 16
data = Reference(ws, min_col=2, max_col=3, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
style_line(ch, [LBLUE, NAVY])
ch.x_axis.title = "価格分位点"
ch.y_axis.title = "円/kWh per GW"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "E4")
print("h7 風力係数:", {k: v for k, v in res.items() if k != "分位点"})

# ============================================================
# h8: 需給内訳（昼間10-14時、北海道）
# ============================================================
nz = hp[hp["fy"].isin(FY_FULL) & (hp["hour"] >= 10) & (hp["hour"] < 14)].fillna(0).copy()
sup = pd.DataFrame({
    "原子力": nz["nuclear"], "火力": nz["thermal"], "一般水力": nz["hydro"],
    "地熱・バイオマス": nz["geothermal"] + nz["biomass"],
    "太陽光（制御前）": nz["solar"] + nz["solar_curt"],
    "風力（制御前）": nz["wind"] + nz["wind_curt"],
    "揚水・蓄電池 発電": nz["pumped"].clip(lower=0) + nz["battery"].clip(lower=0),
    "域外受電": nz["interconn"].clip(lower=0), "fy": nz["fy"],
}).groupby("fy").mean() / 1000
dem = pd.DataFrame({
    "エリア需要": nz["demand"],
    "揚水・蓄電池 充電": -(nz["pumped"].clip(upper=0) + nz["battery"].clip(upper=0)),
    "域外送電": -nz["interconn"].clip(upper=0),
    "出力制御": nz["solar_curt"] + nz["wind_curt"], "fy": nz["fy"],
}).groupby("fy").mean() / 1000
bal = pd.DataFrame({"年度": [f"FY{y}" for y in sup.index]})
for c in sup.columns:
    bal[c] = sup[c].to_numpy()
bal["供給計"] = sup.sum(axis=1).to_numpy()
for c in dem.columns:
    bal[c] = dem[c].to_numpy()
bal["需要側計"] = dem.sum(axis=1).to_numpy()
ws = new_sheet("h8_需給内訳_昼間", "h8 昼間（10-14時）の需要と供給の内訳（北海道、年度平均GW）",
               "九州版（需給内訳_昼間）と同一の定義。太陽光・風力は制御前、出力制御は需要側に計上。泊は全期間停止（原子力=0）。再現: analysis/10・11")
h0, h1r = write_df(ws, bal, fmts={c: "0.00" for c in bal.columns if c != "年度"}, width={"年度": 9})
ch = BarChart()
ch.type = "col"
ch.grouping = "stacked"
ch.overlap = 100
ch.title = "供給側の内訳（昼間平均、GW・制御前）"
ch.height, ch.width = 11, 16
data = Reference(ws, min_col=2, max_col=9, min_row=h0, max_row=h1r)
cats = Reference(ws, min_col=1, min_row=h0 + 1, max_row=h1r)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
for s, col in zip(ch.series, ["1F3864", "8496AD", "2A78D6", "A6B481", "F0B45A", "6DA7EC", "3987E5", "CDE2FB"]):
    s.graphicalProperties.solidFill = col
    s.graphicalProperties.line.noFill = True
ch.x_axis.title = "年度"
ch.y_axis.title = "GW"
ch.x_axis.delete = False
ch.y_axis.delete = False
ws.add_chart(ch, "B14")
ch2 = BarChart()
ch2.type = "col"
ch2.grouping = "stacked"
ch2.overlap = 100
ch2.title = "需要側の内訳（昼間平均、GW）"
ch2.height, ch2.width = 11, 16
data = Reference(ws, min_col=11, max_col=14, min_row=h0, max_row=h1r)
ch2.add_data(data, titles_from_data=True)
ch2.set_categories(cats)
for s, col in zip(ch2.series, ["B7D3F6", "184F95", "6DA7EC", "EC835A"]):
    s.graphicalProperties.solidFill = col
    s.graphicalProperties.line.noFill = True
ch2.x_axis.title = "年度"
ch2.y_axis.title = "GW"
ch2.x_axis.delete = False
ch2.y_axis.delete = False
ws.add_chart(ch2, "K14")

# ============================================================
# 目次
# ============================================================
toc = wb.create_sheet("目次", 0)
toc["A1"] = "北海道 簡易分析（JEPXエリアプライスのみで実施可能な範囲）"
toc["A1"].font = Font(name=FONT, size=14, bold=True, color="1F3864")
toc["A2"] = "目的:「北海道でも面白い結果が得られるのか」への回答材料。九州と同一仕様のパイプラインをエリアプライス列の切替のみで適用。"
toc["A2"].font = F_NOTE
toc["A3"] = "生成: thesis/analysis/10_hokkaido_quick_xlsx.py。需給実績（2026-07-27取得・11_build_area_panels.pyで検証）を反映した完全版。" 
toc["A3"].font = F_NOTE
rows = [
    ("シート", "内容", "キーメッセージ"),
    ("h1_床コマ数", "0.01円コマ数（北海道 vs 九州）", "FY2020初出現→FY2022以降常態化。九州の約半分＝「これから」の初期段階"),
    ("h2_ダックカーブ", "時間帯別平均価格カーブ（北海道）", "昼の谷が浅く朝夕ピークが残る（九州と形状が異なる）。昼の沈みはFY2023以降に出現"),
    ("h3_バックテスト", "裁定価値（完全予見・前日価格）", "直近0.96〜1.15万円/kW-年で九州と同水準。ただしa捕捉率66〜69%は九州（77〜80%）より低い＝形状の予測可能性が低い"),
    ("h4_TB4hスプレッド", "スプレッドの年度推移", "FY2016から高水準（冬季逼迫型）→FY2020底→再拡大。九州型の太陽光単調拡大と経路が異なる"),
    ("h5_分断の方向転換", "市場分断の方向と値差", "高値分断87〜92%→約60%、安値分断1〜5%→30%前後。余剰閉じ込め型への転換が既に進行"),
    ("h6_風力帯域分解", "風力変動の帯域分解＋エネルギーシェア実測", "北海道でも数日帯域が支配的（九州の実測が再現）。風力シェア実測はFY2024-25で10%超＝欧米の検出水準を既に超過"),
    ("h7_分位点回帰", "風力×価格の分位点回帰（S&F再現・更新）", "風力のメリットオーダー効果をFY2016-19（先行研究期間）とFY2023-25（倍増後）で比較"),
    ("h8_需給内訳_昼間", "昼間の需要・供給の積み上げ内訳", "九州版と同一定義の北海道版（泊=0・風力と火力の構成変化）"),
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
