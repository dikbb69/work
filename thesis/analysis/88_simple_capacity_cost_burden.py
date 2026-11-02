# -*- coding: utf-8 -*-
"""火力の固定費を kW の支払いで補う場合の需要家の負担: 見方ごとの負担・図・要約（2026-11-01 の検証を受けた版）
使い方: python analysis/88_simple_capacity_cost_burden.py data/processed/simple_capcost/main 主 capcost_main.png
      SOLAR_UP="600,186" python analysis/88_simple_capacity_cost_burden.py data/processed/simple_capcost/solar600 "太陽光 上振れ" capcost_solar_up.png

主（全国の需要家）:
  Σp×需要 − Σp×（FIT/FIP の支援がその年に続いている電源の出力）− 0.9×LTDA の電源のスポットの粗利（泊3号を含む）
  ＋ k×（容量価格×（調達量−LTDA の容量）＋火力への kW の支払い＋一般水力の要件に届かない分） → ÷k
  - FIT/FIP の支援が続く分（年 y）: 既設の太陽光・風力は、年度ごとの導入量（北電NW 2026-10-06 p.7 の系列）から、運開から20年の間だけ。
    2027年度以降の系統の太陽光の増分は支援なし（地上設置の新規認定は対象外）。新しい風力は、陸上（+63万kW）は支援あり、
    洋上（+520万kW）は半分（ゼロプレミアムの案件があるため、主は0.5、幅は0〜1）。地熱・バイオマス（LTDA 以外）は支援あり。
  - LTDA の容量: メインオークションは LTDA の落札分を差し引いて調達する（notes/28）。泊3号87.2、石狩湾新港2・3 各55.8、アンモニア混焼13.2〜26.4、
    蓄電池の落札67.4（期待容量）、バイオマス19.9万kW。
北海道の需要家の請求だけ: Σp×需要 ＋ k×（容量価格×（調達量−LTDA）＋火力への kW の支払い） → ÷k
感応度: FIT/FIP をすべて相殺／新しい分は相殺なし（洋上0）／相殺なし、泊3号の還付なし（調達量に泊3号を戻す）、調達量全体に払う、÷k をしない
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTDIR, SCEN, FIGNAME = sys.argv[1], sys.argv[2], sys.argv[3]
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "hokkaido")
BASE_P = 14_972.0
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
CA, CB = "#2a78d6", "#eb6834"
plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
plt.rcParams["font.size"] = 10
SOLAR_HIST = {2010: 0, 2011: 6, 2012: 10, 2013: 35, 2014: 61, 2015: 97, 2016: 115, 2017: 133, 2018: 154, 2019: 188, 2020: 199,
              2021: 214, 2022: 221, 2023: 227, 2024: 236, 2025: 243}     # 北電NW 2026-10-06 次世代電力系統WG 第13回 参考資料3-1 p.7（年度末、万kW）
WIND_HIST = {2010: 25, 2011: 29, 2012: 29, 2013: 32, 2014: 32, 2015: 32, 2016: 35, 2017: 39, 2018: 44, 2019: 48, 2020: 53,
             2021: 58, 2022: 79, 2023: 123, 2024: 136, 2025: 137}
NEW_ONSHORE, NEW_OFFSHORE = 63.0, 520.0                                # 旧の主: 2040年の風力720 のうち FY2025 からの増分583（陸上+63・洋上+520）
ONSHORE_2035 = 275.0                                                  # 新しい主（2026-11-02）: FY2035 までの供給計画の増分（137→275）は陸上、それより上は洋上

R = pd.read_csv(os.path.join(OUTDIR, "capcost_eval.csv"), encoding="utf-8-sig")
R = R[R["シナリオ"] == SCEN].copy()
Pth = pd.read_csv(os.path.join(OUTDIR, "capcost_paths.csv"), encoding="utf-8-sig")
Pth = Pth[Pth["シナリオ"] == SCEN].copy()
k = R["k"].iloc[0]


def hist(h, t):
    return h[max(min(t, max(h)), min(h))] if t >= min(h) else 0.0


def phi_solar(y, cap_mw):
    cap = cap_mw / 10.0
    c26 = hist(SOLAR_HIST, 2025) + max(cap - hist(SOLAR_HIST, 2025), 0) * 0 + (cap_2026[SCEN] - hist(SOLAR_HIST, 2025))
    sup = min(c26, cap) - hist(SOLAR_HIST, y - 20)
    return float(np.clip(sup / cap, 0, 1))


def phi_wind(y, cap_mw, off):
    cap = cap_mw / 10.0
    sup = hist(WIND_HIST, 2025) - hist(WIND_HIST, y - 20)
    if PLAN2035:                                                      # その年の設備のうち275万kW までの増分は陸上（支援あり）、それより上は洋上（off の比）
        sup += max(min(cap, ONSHORE_2035) - hist(WIND_HIST, 2025), 0.0) + off * max(cap - ONSHORE_2035, 0.0)
    else:
        new = max(cap - hist(WIND_HIST, 2025), 0.0)
        sup += new * (NEW_ONSHORE + off * NEW_OFFSHORE) / (NEW_ONSHORE + NEW_OFFSHORE)
    return float(np.clip(sup / cap, 0, 1))


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from model import params as PR  # noqa: E402
sc = {n: v for n, v in PR.SCENARIOS.items()}
if SCEN not in sc:
    s_, o_ = [float(x) * 10 for x in os.environ.get("SOLAR_UP", "600,186").split(",")]
    PR.Y2040["solar_up"] = {**PR.Y2040["11000"], "solar": s_, "onsite": o_}
    PR.SELFCONS_SHARE["solar_up"] = o_ / s_
    sc[SCEN] = dict(y2040="solar_up", nuclear="3号だけ", path="linear")   # 旧の主の頑健性なので旧の経路に固定
cap_2026 = {SCEN: PR.scenario_year(2026, sc[SCEN])["solar_mw"] / 10.0}
PLAN2035 = sc[SCEN].get("path", PR.PATH) == "plan2035"

R["φ 太陽光"] = [phi_solar(y, c) for y, c in zip(R["年"], R["太陽光（系統）の設備(MW)"])]
for off, lab in ((0.5, ""), (0.0, " 洋上0"), (1.0, " 洋上1")):
    R["φ 風力" + lab] = [phi_wind(y, c, off) for y, c in zip(R["年"], R["風力の設備(MW)"])]
spot = R["スポットの支払い Σp×需要(億円/年)"]
pS, pW, pG, pB = R["太陽光の分 Σp×出力(億円/年)"], R["風力の分 Σp×出力(億円/年)"], R["地熱の分(億円/年)"], R["バイオマスの分（LTDA 以外）(億円/年)"]
ret_other = 0.9 * (R["LTDA 火力の粗利(億円/年)"] + R["アンモニア混焼分の粗利(億円/年)"] + 0.825 * R["LTDA 蓄電池の値差の収入(億円/年)"])
ret_nuc = 0.9 * R["原子力の粗利(億円/年)"]
hy_short = np.maximum(R["一般水力の要件(億円/年)"] - R["一般水力の収入(億円/年)"], 0.0)
Pcap = R["容量価格(円/kW)"]
cap_main = Pcap * np.maximum(R["容量市場の調達量(万kW)"] - R["LTDA の容量(万kW)"], 0) * 1e4 / 1e8
cap_nonuc = Pcap * np.maximum(R["容量市場の調達量(万kW)"] - R["LTDA の容量(万kW)"] + R["泊の設備(MW)"] / 10.0, 0) * 1e4 / 1e8
cap_all = Pcap * R["容量市場の調達量(万kW)"] * 1e4 / 1e8
xpay = R["火力への kW の支払い(億円/年)"]
nuc_req = R["原子力の要件(億円/年)"]
nuc_rev_noret = R["原子力の粗利(億円/年)"] + Pcap * R["泊の設備(MW)"] * 1_000 / 1e8
nuc_short = np.maximum(nuc_req - nuc_rev_noret, 0.0)
F_main = R["φ 太陽光"] * pS + R["φ 風力"] * pW + pG + pB
F_full = pS + pW + pG + pB
F_new0 = R["φ 太陽光"] * pS + R["φ 風力 洋上0"] * pW + pG + pB
V = {"主（全国の需要家）": (spot - F_main - ret_other - ret_nuc + k * (cap_main + xpay + hy_short)) / k,
     "北海道の需要家の請求だけ": (spot + k * (cap_main + xpay)) / k,
     "感応度: FIT/FIP をすべて相殺": (spot - F_full - ret_other - ret_nuc + k * (cap_main + xpay + hy_short)) / k,
     "感応度: 新しい洋上風力も相殺なし": (spot - F_new0 - ret_other - ret_nuc + k * (cap_main + xpay + hy_short)) / k,
     "感応度: FIT/FIP の相殺なし": (spot - ret_other - ret_nuc + k * (cap_main + xpay + hy_short)) / k,
     "感応度: 泊3号の還付なし": (spot - F_main - ret_other + k * (cap_nonuc + xpay + hy_short + nuc_short)) / k,
     "感応度: 調達量全体に容量価格": (spot - F_main - ret_other - ret_nuc + k * (cap_all + xpay + hy_short)) / k,
     "感応度: ÷k をしない": (spot - F_main - ret_other - ret_nuc) + (cap_main + xpay + hy_short)}
for name, s in V.items():
    R[name] = s
base = R[(R["補い方"] == "A") & (R["値(円/kW)"] == BASE_P)].set_index("年")
for name in V:
    R[name + " 主との差"] = R[name] - R["年"].map(base[name])
R["kW の増分(円/kW-年)"] = np.where(R["補い方"] == "A", R["値(円/kW)"] - BASE_P, R["値(円/kW)"])
Pth["kW の増分(円/kW-年)"] = np.where(Pth["補い方"] == "A", Pth["値(円/kW)"] - BASE_P, Pth["値(円/kW)"])
R["需要1kWh あたり 主（円/kWh）"] = R["主（全国の需要家） 主との差"] / (R["需要(TWh)"] * 10)
R["需要1kWh あたり 北海道（円/kWh）"] = R["北海道の需要家の請求だけ 主との差"] / (R["需要(TWh)"] * 10)
R.to_csv(os.path.join(OUTDIR, f"capcost_variants_{SCEN}.csv"), index=False, encoding="utf-8-sig")

# B: 上乗せがちょうど0 になる額 X*（年ごと、格子の点の間を直線で補間）とそのときの負担
rows = []
for y, g in R[R["補い方"] == "B"].groupby("年"):
    g = g.sort_values("値(円/kW)")
    pos = g[g["上乗せ μ(円/kWh)"] > 1e-6]
    zero = g[g["上乗せ μ(円/kWh)"] <= 1e-6]
    if len(pos) < 2 or zero.empty:
        continue
    a0, a1, b = pos.iloc[-2], pos.iloc[-1], zero.iloc[0]
    dx = a1["値(円/kW)"] - a0["値(円/kW)"]
    slope = (a0["上乗せ μ(円/kWh)"] - a1["上乗せ μ(円/kWh)"]) / dx            # μ>0 の側の傾き（X について直線）で0 まで延ばす
    xs = min(a1["値(円/kW)"] + a1["上乗せ μ(円/kWh)"] / slope, b["値(円/kW)"]) if slope > 0 else b["値(円/kW)"]
    t = (xs - a1["値(円/kW)"]) / dx
    r = {"年": y, "X*(円/kW-年)": xs, "火力への kW の支払い(億円/年)": a1["火力への kW の支払い(億円/年)"] + t * (a1["火力への kW の支払い(億円/年)"] - a0["火力への kW の支払い(億円/年)"]),
         "蓄電池(万kW)": b["蓄電池(万kW)"], "需要(TWh)": b["需要(TWh)"]}
    for name in V:
        c = name + " 主との差"
        r[name] = a1[c] + t * (a1[c] - a0[c])
    rows.append(r)
XS = pd.DataFrame(rows)
XS.to_csv(os.path.join(OUTDIR, f"capcost_xstar_{SCEN}.csv"), index=False, encoding="utf-8-sig")

# 1円の kW の支払いあたりの、スポットに関わる支払いの減少（漏れの倍率）: 2040年、主の点と X* の比較
y40 = XS[XS["年"] == 2040].iloc[0] if (XS["年"] == 2040).any() else None
mult = {}
if y40 is not None:
    kwp = y40["火力への kW の支払い(億円/年)"]
    for name in ("主（全国の需要家）", "北海道の需要家の請求だけ"):
        mult[name] = (kwp - y40[name]) / kwp

LAB = {"A": "容量価格を上げる（すべての電源に払う）", "B": "火力だけに kW で払う（容量価格は14,972円のまま）"}


def spines(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)


fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.4))
ax = axes.ravel()
full = R.groupby(["補い方", "値(円/kW)"])["年"].count()
ny = R["年"].nunique()
for lever, col in (("A", CA), ("B", CB)):
    vals = [v for v in sorted(R[R["補い方"] == lever]["値(円/kW)"].unique()) if full.get((lever, v), 0) == ny]
    g = R[(R["補い方"] == lever) & R["値(円/kW)"].isin(vals)].groupby("kW の増分(円/kW-年)")
    for i, name in enumerate(("主（全国の需要家）", "北海道の需要家の請求だけ")):
        m = g[name + " 主との差"].mean()
        ax[i].plot(m.index, m.values, color=col, marker="o", ms=4, lw=2, label=LAB[lever])
        if name == "主（全国の需要家）":
            lo = g[["感応度: FIT/FIP をすべて相殺 主との差", "感応度: 新しい洋上風力も相殺なし 主との差", "感応度: FIT/FIP の相殺なし 主との差",
                    "感応度: 泊3号の還付なし 主との差"]].mean()
            ax[i].fill_between(lo.index, lo.min(axis=1), lo.max(axis=1), color=col, alpha=0.12, lw=0)
    d = R[(R["補い方"] == lever) & (R["年"] == 2040)].sort_values("kW の増分(円/kW-年)")
    ax[2].plot(d["kW の増分(円/kW-年)"], d["上乗せ μ(円/kWh)"], color=col, marker="o", ms=4, lw=2, label=LAB[lever])
    q = Pth[Pth["補い方"] == lever].sort_values("kW の増分(円/kW-年)")
    ok = q["量 2040"] < q["量 2040"].max() - 1e-6 if q["量 2040"].max() >= 399 else q["量 2040"] < 1e9
    ax[3].plot(q.loc[ok, "kW の増分(円/kW-年)"], q.loc[ok, "量 2040"], color=col, marker="o", ms=4, lw=2, label=LAB[lever])
ax[0].set_title("需要家の負担の主との差（全国の需要家、2030〜40年の平均）", loc="left", fontsize=10.5, color=INK)
ax[1].set_title("需要家の負担の主との差（北海道の需要家の請求だけ、2030〜40年の平均）", loc="left", fontsize=10.5, color=INK)
ax[2].set_title("上乗せ μ（2040年）", loc="left", fontsize=10.5, color=INK)
ax[3].set_title("蓄電池の量（2040年）", loc="left", fontsize=10.5, color=INK)
for a, u in zip(ax, ("億円/年", "億円/年", "円/kWh", "万kW")):
    a.set_ylabel(u, color=INK)
for a in ax[:2]:
    a.axhline(0, color=MUTED, lw=1)
ax[3].axhline(98.8, color=MUTED, lw=1, ls="--")
ax[3].text(ax[3].get_xlim()[0], 100, " 既設＋LTDA 98.8万kW", color=MUTED, fontsize=8.5, va="bottom")
for a in ax:
    a.axvline(0, color=MUTED, lw=1, ls=":")
    a.set_xlabel("火力が kW で受け取る額の主からの増分（円/kW-年、2030年度以降）", color=INK, fontsize=9)
    spines(a)
ax[0].legend(frameon=False, fontsize=8.5, loc="best")
fig.text(0.01, -0.01, f"{SCEN}。薄い帯は全国の需要家の見方の感応度（FIT/FIP をすべて相殺・新しい洋上風力も相殺なし・相殺なし・泊3号の還付なし）の幅。"
         "蓄電池の量は、量が決まる点（格子の上限に達しない点）だけ描く", fontsize=8.5, color=MUTED)
fig.tight_layout()
fig.savefig(os.path.join(FIG, FIGNAME), dpi=200, bbox_inches="tight")
print("wrote", FIGNAME)

pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 40)
A11 = R.groupby(["補い方", "値(円/kW)"]).agg(**{"年の数": ("年", "count"), **{n: (n + " 主との差", "mean") for n in V}, "μ 平均": ("上乗せ μ(円/kWh)", "mean")}).reset_index()
print(A11.round(1).to_string(index=False))
A11.to_csv(os.path.join(OUTDIR, f"capcost_avg_{SCEN}.csv"), index=False, encoding="utf-8-sig")
print("== X*（上乗せがちょうど0 になる火力への kW の支払い）")
print(XS.round(1).to_string(index=False))
print("2030〜40年の平均:", {n: round(XS[n].mean(), 1) for n in V})
print("2040年 漏れの倍率（スポットに関わる支払いの減少÷kW の支払い）:", {n: round(v, 2) for n, v in mult.items()})
cols = ["補い方", "値(円/kW)", "年", "蓄電池(万kW)", "上乗せ μ(円/kWh)", "平均価格（需要加重）", "φ 太陽光", "φ 風力"] + [n + " 主との差" for n in V] + ["需要1kWh あたり 主（円/kWh）", "需要1kWh あたり 北海道（円/kWh）"]
S = R[R["年"].isin([2030, 2035, 2040])][cols].sort_values(["補い方", "値(円/kW)", "年"])
S.to_csv(os.path.join(OUTDIR, f"capcost_summary_{SCEN}.csv"), index=False, encoding="utf-8-sig")
print(Pth[["補い方", "値(円/kW)"] + [f"量 {y}" for y in (2030, 2035, 2040, 2045)]].round(1).to_string(index=False))
