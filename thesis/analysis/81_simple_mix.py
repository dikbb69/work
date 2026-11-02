#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデル（model/simple.py）の結果の確かめ: 発電種別ごとの容量と発電量、時間帯ごとの構成、蓄電池の動き

1. FY2024・FY2025 の実績と、同じ年度のモデル（実績の入力で需給を解く）
2. 2026〜2040年: 均衡の経路（上乗せあり、容量価格14,972円）の蓄電池の量で需給を解く
3. 時間帯ごとの構成（季節ごと、MW と比率）
4. 蓄電池の量を増やしたときの1kW あたりの充放電と値幅（2035・2040年）
5. 確かめ: 動かない火力も残す場合、蓄電池に追加の収入がある場合の参入、北電NW の2035年の公式シミュレーションとの照合
出力: data/processed/simple_mix_annual.csv・simple_mix_hourly.csv・simple_battery_operation.csv・simple_checks.csv・simple_path_prices.npz（時間別の価格・需要・抑制・充放電）、
      figures/hokkaido/simple_capacity.png・simple_generation.png・simple_hourly_mw.png・simple_hourly_share.png・simple_battery_operation.png
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, data as DT, balance as B, merit as MO, entry as EN, calibrate as CB, simple as SM

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
BASE_P = 14_972.0
SC = PR.SCENARIOS["主"]
# 積み上げの順（下から）と色。色は検証済みの8色から、積み上げで隣り合う組がすべて見分けられる順に当てた（灰色は分類でない項目）
STACK = [("原子力", "#e87ba4"), ("地熱・バイオマス", "#008300"), ("水力（揚水の正味を含む）", "#2a78d6"), ("石油", "#e34948"),
         ("石炭", "#6250d6"), ("LNG", "#eb6834"), ("その他の火力（自家発など）", "#898781"), ("風力", "#1baf7a"), ("太陽光", "#eda100"),
         ("北本の受電", "#c3c2b7"), ("蓄電池の放電", "#52514e")]
NEG = [("北本の送電", "#c3c2b7"), ("蓄電池の充電", "#52514e")]
SEASONS = {"冬（12〜2月）": (12, 1, 2), "春（3〜5月）": (3, 4, 5), "夏（6〜9月）": (6, 7, 8, 9), "秋（10〜11月）": (10, 11)}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
plt.rcParams["font.size"] = 10


def fuel_sum(g, units, fuel):
    idx = [j for j, u in enumerate(units) if u[1] == fuel]
    return g[:, :, idx].sum(2) if idx else np.zeros(g.shape[:2])


def mix_actual(fy):
    """実績（時間別、MW）。火力はユニット別の実績を燃料で足し、エリアの火力との差をその他の火力とする。蓄電池は実績の内訳にない"""
    C = DT.calib()
    r = C["fy"] == fy
    G = C["G"][r]
    m = {"原子力": C["N"][r], "地熱・バイオマス": C["Geo"][r] + C["Bm"][r], "水力（揚水の正味を含む）": C["Hy"][r] + C["pump"][r],
         "石油": fuel_sum(G, C["units"], "石油"), "石炭": fuel_sum(G, C["units"], "石炭"), "LNG": fuel_sum(G, C["units"], "LNG"),
         "その他の火力（自家発など）": C["other"][r], "風力": C["W"][r], "太陽光": C["S"][r],
         "北本の受電": np.maximum(-C["X"][r], 0.0), "蓄電池の放電": np.zeros_like(C["D"][r]),
         "北本の送電": np.maximum(C["X"][r], 0.0), "蓄電池の充電": np.zeros_like(C["D"][r]),
         "需要": C["D"][r], "抑制": C["curt"][r], "下げ代不足": np.zeros_like(C["D"][r]), "供給力不足": np.zeros_like(C["D"][r])}
    return m, C["month"][r]


def mix_model(I, R, chg, dis):
    """モデル（時間別、MW）。抑制は、抑制できる太陽光と風力に出力の比で割り振る"""
    fS = np.maximum(I["S"] - I["U"], 0.0)
    share = np.where(fS + I["W"] > 0, fS / np.maximum(fS + I["W"], 1e-9), 0.0)
    cS = R["curt"] * share
    g, u = R["g"], R["units"]
    m = {"原子力": I["N"], "地熱・バイオマス": I["G"] + I["Bm"], "水力（揚水の正味を含む）": I["Hy"] + I["pump"],
         "石油": fuel_sum(g, u, "石油"), "石炭": fuel_sum(g, u, "石炭"), "LNG": fuel_sum(g, u, "LNG"),
         "その他の火力（自家発など）": R["other_out"], "風力": I["W"] - (R["curt"] - cS), "太陽光": I["S"] - cS,
         "北本の受電": np.maximum(-R["X"], 0.0), "蓄電池の放電": dis, "北本の送電": np.maximum(R["X"], 0.0), "蓄電池の充電": chg,
         "需要": I["D"], "抑制": R["curt"], "下げ代不足": R["unabs"], "供給力不足": R["short"]}
    return m, I["month"]


def annual(m):
    yrs = m["需要"].shape[0] / 365.25
    return {k: float(v.sum() / yrs / 1e6) for k, v in m.items()}


def hourly(m, month, label):
    rows = []
    for s, ms in SEASONS.items():
        sel = np.isin(month[:, 0], ms)
        for k, v in m.items():
            for h, x in enumerate(v[sel].mean(0)):
                rows.append({"区分": label, "季節": s, "時": h, "項目": k, "MW": float(x)})
    return rows


def biomass_base():
    """バイオマスの設備の推定: 気象年 FY2023〜25 の時間別の出力の99.9%点"""
    return float(np.quantile(DT.weather()["Bm"], 0.999))


def capacity(y, units_alive, K, sc_y=None, actual=False):
    """発電種別ごとの設備（MW）。水力・揚水は一定（資源エネルギー庁 2026-08-06、notes/37）、バイオマスは推定に新設を足す"""
    fuels = {f: float(sum(u[2] for u in units_alive if u[1] == f)) for f in ("石炭", "LNG", "石油")}
    if actual:
        cap = DT._capacity_daily(pd.DatetimeIndex([pd.Timestamp(y + 1, 3, 31)]))
        solar, wind, nuc = float(cap["solar_kw"].iloc[0]), float(cap["wind_kw"].iloc[0]), 0.0
        geo, bio = PR.GEO_MW[2025], biomass_base()
    else:
        solar, wind = sc_y["solar_mw"], sc_y["wind_mw"]
        nuc = float(sum(PR.NUC[n] for n, _ in sc_y["nuclear"]))
        geo = PR.interp_year(PR.GEO_MW, y)
        bio = biomass_base() + sum(mw for yy, mw in PR.BIOMASS_ADD.values() if y >= yy)
    return {"原子力": nuc, "地熱・バイオマス": geo + bio, "水力（揚水の正味を含む）": sum(PR.HYDRO_CAP.values()) + PR.PUMP_CAP,
            "石油": fuels["石油"], "石炭": fuels["石炭"], "LNG": fuels["LNG"], "風力": wind, "太陽光": solar,
            "蓄電池": K * 10.0, "LTDA の火力（内数）": float(sum(u[2] for u in units_alive if u[0] in PR.LTDA_UNITS))}


def main():
    import warnings
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    cal = SM.calibration("commit")
    E = pd.read_csv(os.path.join(PROC, "simple_entry.csv"))
    path = E[(E["場合"] == "上乗せ") & (E["容量価格(円/kW)"] == BASE_P)].iloc[0]
    before, when = SM.exit_years(cal, SC, PR.YEARS, "commit")
    ann, caps, hrs = [], [], []
    PP = {}                                                     # 時間別の価格など（価格の分布・日の形の図に使う）
    # 1. 実績と、同じ年度のモデル
    for fy in PR.CALIB_FY:
        Ia = MO.inputs_actual(fy)
        PP[f"p_FY{fy}"], PP[f"month_FY{fy}"] = Ia["p_act"].astype(np.float32), Ia["month"].astype(np.int8)
        PP[f"D_FY{fy}"] = Ia["D"].astype(np.float32)
        m, mo = mix_actual(fy)
        ann.append({"区分": "実績", "年": fy, **annual(m)})
        caps.append({"区分": "実績", "年": fy, **capacity(fy, B.fleet(fy), 0.0, actual=True)})
        hrs += hourly(m, mo, f"FY{fy} 実績")
        I = MO.inputs_actual(fy)
        R = SM.dispatch(I, B.fleet(fy))
        z = np.zeros_like(I["D"])
        m, mo = mix_model(I, R, z, z)
        ann.append({"区分": "モデル（実績の入力）", "年": fy, **annual(m)})
        hrs += hourly(m, mo, f"FY{fy} モデル")
    # 2. 将来（均衡の経路）
    for y in PR.YEARS:
        K = float(path[f"量 {y}"])
        sc_y = PR.scenario_year(y, SC)
        I = MO.inputs_future(sc_y, SC)
        T, _, st = SM.run_year(I, cal, Ks=[K], P_list=(BASE_P,), drop=before[y], return_state=True)
        R = st["R"]
        m, mo = mix_model(I, R, st["chg"], st["dis"])
        PP.update({f"p_{y}": st["p"].astype(np.float32), f"D_{y}": I["D"].astype(np.float32), f"month_{y}": I["month"].astype(np.int8),
                   f"vre_{y}": (I["S"] + I["W"]).astype(np.float32), f"curt_{y}": R["curt"].astype(np.float32),
                   f"chg_{y}": st["chg"].astype(np.float32), f"dis_{y}": st["dis"].astype(np.float32)})
        alive = [u for u, a in zip(R["units"], st["alive"]) if a]
        ann.append({"区分": "モデル（均衡の経路）", "年": y, "蓄電池(万kW)": K, "α": st["info"]["α"], "上乗せ μ(円/kWh)": st["info"].get("μ", np.nan), **annual(m),
                    "平均価格（需要加重）": float((st["p"] * I["D"]).sum() / I["D"].sum()), "退出した号機（累計）": "・".join(list(before[y]) + [u[0] for u, a in zip(R["units"], st["alive"]) if not a])})
        caps.append({"区分": "モデル（均衡の経路）", "年": y, **capacity(y, alive, K, sc_y)})
        if y in (2030, 2035, 2040):
            hrs += hourly(m, mo, f"{y} モデル")
        print(y, "蓄電池", K, "退出", ann[-1]["退出した号機（累計）"], flush=True)
    np.savez_compressed(os.path.join(PROC, "simple_path_prices.npz"), **PP)
    A, Cp, H = pd.DataFrame(ann), pd.DataFrame(caps), pd.DataFrame(hrs)
    A.to_csv(os.path.join(PROC, "simple_mix_annual.csv"), index=False, encoding="utf-8-sig")
    Cp.to_csv(os.path.join(PROC, "simple_capacity_annual.csv"), index=False, encoding="utf-8-sig")
    H.to_csv(os.path.join(PROC, "simple_mix_hourly.csv"), index=False, encoding="utf-8-sig")
    print(Cp.round(0).to_string())
    print(A.round(2).to_string())
    # 4. 蓄電池の量を増やしたときの動き
    ops = []
    for y in (2035, 2040):
        I = MO.inputs_future(PR.scenario_year(y, SC), SC)
        T, _ = SM.run_year(I, cal, Ks=[0, 10, 25, 50, 75, 99, 150, 200, 250, 300, 350, 400], P_list=(BASE_P,), drop=before[y])
        T.insert(0, "年", y)
        ops.append(T)
    O = pd.concat(ops, ignore_index=True)
    O.to_csv(os.path.join(PROC, "simple_battery_operation.csv"), index=False, encoding="utf-8-sig")
    # 5. 確かめ
    checks = check_runs(cal, before)
    figures(A, Cp, H, O)
    return A, Cp, H, O, checks


def check_runs(cal, before):
    """(a) 動かない火力も退出させず③の対象に残す場合、(b) 蓄電池に追加の収入がある場合、(c) 北電NW の2035年の公式シミュレーション"""
    Z = dict(np.load(os.path.join(PROC, "simple_pik.npz")))
    Ks = Z.pop("K")
    pi = {y: Z[f"上乗せ|{BASE_P:.0f}|{y}"] for y in PR.YEARS}
    kby = {y: CB.kappa_eff(MO.inputs_future(PR.scenario_year(y, SC), SC), Ks) for y in PR.YEARS}
    rows = []
    base = lambda cur, kb=None: EN.path(cur, Ks, BASE_P, kappa_by_year=kb)
    for lab, kb in (("κ 0.861 一定", None), ("κ 量に応じた実効値", kby)):
        Kt = base(pi, kb)
        rows.append({"確かめ": "主", "κ": lab, **{f"量 {t}": Kt[t] for t in (2030, 2035, 2040, 2045)}})
        for d in (500.0, 1_000.0, 2_000.0, 3_000.0, 5_000.0):
            Kt = base({y: v + d for y, v in pi.items()}, kb)
            rows.append({"確かめ": f"追加の収入 +{d:,.0f}円/kW-年", "κ": lab, **{f"量 {t}": Kt[t] for t in (2030, 2035, 2040, 2045)}})
    # (a) 動かない火力も残す（④を外す）
    pa = {}
    for y in PR.YEARS:
        I = MO.inputs_future(PR.scenario_year(y, SC), SC)
        T, _ = SM.run_year(I, cal, Ks=Ks, P_list=(BASE_P,), exit_idle=False)
        pa[y] = T["π(円/kW-年)"].to_numpy()
        if y in (2035, 2040):
            r = T[T["K(万kW)"] == 100.0].iloc[0]
            rows.append({"確かめ": f"動かない火力も残す（{y}年、100万kW）", "κ": "—", "α": r["α"], "π(円/kW-年)": r["π(円/kW-年)"]})
    for lab, kb in (("κ 0.861 一定", None), ("κ 量に応じた実効値", kby)):
        Kt = base(pa, kb)
        rows.append({"確かめ": "動かない火力も残す", "κ": lab, **{f"量 {t}": Kt[t] for t in (2030, 2035, 2040, 2045)}})
    # (c) 公式の2035年（ケース①: 出力制御率30.0%・3,972時間、原子力168万kW で一定、出力制御の時間の北本は平均769MW の送電、水力5,428GWh）
    sc_y = PR.scenario_year(2035, SC)
    I0 = MO.inputs_future(sc_y, SC)
    units = B.fleet(2035, drop=before[2035])
    yrs = I0["D"].shape[0] / 365.25

    def official(lab, I, mode="commit", mustrun=None):
        R = MO.dispatch(I, units) if mode == "old" else SM.dispatch(I, units, mode=mode, mustrun=mustrun)
        ch = R["curt"] > 1e-6
        rows.append({"確かめ": f"公式の2035年: {lab}", "κ": "—", "出力制御率": float(R["curt"].sum() / (I["S"] + I["W"]).sum()),
                     "出力制御の時間(h/年)": float(ch.sum() / yrs)})
    I1 = dict(I0, N=np.full_like(I0["N"], 1680.0), largest=np.full_like(I0["N"], PR.NUC["泊3号"]))
    I2 = dict(I1, link=(770.0, I1["link"][1]))
    I3 = dict(I2, Hy=I2["Hy"] * 5_428.0 / (I2["Hy"].sum() / yrs / 1e3))
    official("主の前提（蓄電池なし、マストラン3台）", I0)
    official("公式の原子力・送電・水力、マストラン3台（主）", I3)
    official("公式の原子力・送電・水力、マストランなし", I3, mustrun=())
    official("公式の原子力・送電・水力、前のモデルの需給", I3, mode="old")
    rows.append({"確かめ": "公式の2035年: 北電NW 公式シミュレーション（ケース①）", "κ": "—", "出力制御率": 0.300, "出力制御の時間(h/年)": 3972.0})
    Q = pd.DataFrame(rows)
    Q.to_csv(os.path.join(PROC, "simple_checks.csv"), index=False, encoding="utf-8-sig")
    print(Q.round(3).to_string())
    return Q


def _spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7")
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def figures(A, Cp, H, O):
    yrs_lab = lambda d: [f"FY{int(y) % 100}\n実績" if k == "実績" else str(int(y)) for k, y in zip(d["区分"], d["年"])]
    # 設備
    d = Cp.reset_index(drop=True)
    cats = [c for c, _ in STACK if c in d.columns] + ["蓄電池"]
    colors = dict(STACK, 蓄電池="#52514e")
    fig, ax = plt.subplots(figsize=(12, 5.2))
    x = np.arange(len(d))
    bottom = np.zeros(len(d))
    for c in cats:
        v = d[c].to_numpy() / 10.0
        ax.bar(x, v, bottom=bottom, color=colors[c], width=0.72, edgecolor="white", linewidth=0.8, label=c)
        bottom += v
    ax.set_xticks(x, yrs_lab(d), fontsize=8.5)
    ax.set_ylabel("設備（万kW、送電端）", color=INK)
    ax.set_title("発電種別ごとの設備（FY2024・2025 は実績、2026年以降は均衡の経路）", loc="left", color=INK, fontsize=12)
    _spines(ax)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.01, -0.02, "水力は一般水力126万kW＋揚水80万kW で一定。地熱・バイオマスのバイオマスは出力の99.9%点からの推定に新設を足した値。"
             "その他の火力（自家発など）は設備のデータがないので入れていない。FY2024・2025 の蓄電池は実績の内訳がないので入れていない",
             fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "simple_capacity.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    # 発電量
    d = A[A["区分"] != "モデル（実績の入力）"].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(12, 5.6))
    x = np.arange(len(d))
    bottom = np.zeros(len(d))
    for c, col in STACK:
        v = d[c].to_numpy()
        ax.bar(x, v, bottom=bottom, color=col, width=0.72, edgecolor="white", linewidth=0.8, label=c)
        bottom += v
    nb = np.zeros(len(d))
    for c, col in NEG:
        v = -d[c].to_numpy()
        ax.bar(x, v, bottom=nb, color=col, width=0.72, edgecolor="white", linewidth=0.8, hatch="////", label=c + "（下向き）")
        nb += v
    ax.plot(x, d["需要"], color=INK, lw=1.8, marker="o", ms=4, label="需要")
    ax.plot(x, d["抑制"], color="#e34948", lw=1.4, ls="--", marker="s", ms=3.5, label="太陽光・風力の抑制")
    ax.axhline(0, color="#c3c2b7", lw=0.8)
    ax.set_xticks(x, yrs_lab(d), fontsize=8.5)
    ax.set_ylabel("TWh/年", color=INK)
    ax.set_title("発電種別ごとの発電量（上向きが供給、下向きが北本の送電と蓄電池の充電）", loc="left", color=INK, fontsize=12)
    _spines(ax)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.text(0.01, -0.02, "FY2024・2025 は北電NW のエリアの需給実績と OCCTO のユニット別実績。2026年以降は均衡の経路の蓄電池の量でモデルの需給を解いた値（3つの気象年の平均）",
             fontsize=8, color=MUTED)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "simple_generation.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    # 時間帯ごと（MW と比率）
    cols = ["FY2024 実績", "FY2024 モデル", "2030 モデル", "2035 モデル", "2040 モデル"]
    seas = ["冬（12〜2月）", "春（3〜5月）"]
    for kind in ("mw", "share"):
        fig, axes = plt.subplots(len(seas), len(cols), figsize=(17, 7.2), sharex=True, sharey=True)
        for i, s in enumerate(seas):
            for j, c in enumerate(cols):
                ax = axes[i, j]
                g = H[(H["区分"] == c) & (H["季節"] == s)].pivot_table(index="時", columns="項目", values="MW")
                hr = g.index.to_numpy()
                pos = np.array([g[k].to_numpy() for k, _ in STACK])
                if kind == "share":
                    tot = pos.sum(0)
                    ax.stackplot(hr, pos / tot * 100, colors=[col for _, col in STACK], linewidth=0)
                    ax.set_ylim(0, 100)
                else:
                    ax.stackplot(hr, pos / 1e3, colors=[col for _, col in STACK], linewidth=0)
                    neg = np.array([g[k].to_numpy() for k, _ in NEG])
                    ax.stackplot(hr, -neg / 1e3, colors=[col for _, col in NEG], linewidth=0, hatch="////")
                    ax.plot(hr, g["需要"] / 1e3, color=INK, lw=1.5)
                    ax.axhline(0, color="#c3c2b7", lw=0.8)
                if i == 0:
                    ax.set_title(c.replace("FY2024", "FY2024"), color=INK, fontsize=10.5)
                if j == 0:
                    ax.set_ylabel(f"{s}\n" + ("供給の比率（%）" if kind == "share" else "GW（線は需要）"), color=INK)
                ax.set_xticks([0, 6, 12, 18, 23])
                _spines(ax)
        for ax in axes[-1]:
            ax.set_xlabel("時", color=MUTED)
        handles = [plt.Rectangle((0, 0), 1, 1, color=col) for _, col in STACK]
        labels = [k for k, _ in STACK]
        if kind == "mw":
            handles += [plt.Rectangle((0, 0), 1, 1, facecolor=col, hatch="////", edgecolor="white") for _, col in NEG] + [plt.Line2D([], [], color=INK, lw=1.5)]
            labels += [k + "（下向き）" for k, _ in NEG] + ["需要"]
        fig.legend(handles, labels, frameon=False, fontsize=8.5, loc="lower center", ncol=7, bbox_to_anchor=(0.5, -0.06))
        ttl = "時間帯ごとの供給の比率（北本の受電と蓄電池の放電を含む）" if kind == "share" else "時間帯ごとの需給（季節の平均の日、GW）"
        fig.suptitle(ttl + "。FY2024 は実績と、同じ年度をモデルで解いた値。2030年以降は均衡の経路", x=0.01, ha="left", color=INK, fontsize=12)
        fig.tight_layout(rect=(0, 0.02, 1, 0.96))
        fig.savefig(os.path.join(FIG, f"simple_hourly_{kind}.png"), dpi=200, bbox_inches="tight")
        plt.close(fig)
    # 蓄電池の動き
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    c2 = {2035: "#2a78d6", 2040: "#eb6834"}
    for y, g in O.groupby("年"):
        g = g.sort_values("K(万kW)")
        k = g["K(万kW)"]
        axes[0].plot(k, g["1kW あたりの放電(kWh/kW-年)"], color=c2[y], lw=2, marker="o", ms=3.5, label=f"{y}年")
        axes[1].plot(k, g["高い4時間の平均(円/kWh)"], color=c2[y], lw=2, label=f"{y}年 高い4時間")
        axes[1].plot(k, g["安い4時間の平均(円/kWh)"], color=c2[y], lw=2, ls="--", label=f"{y}年 安い4時間")
        axes[2].plot(k, g["π(円/kW-年)"], color=c2[y], lw=2, marker="o", ms=3.5, label=f"{y}年")
    axes[0].axhline(4 * PR.ETA * 365, color=MUTED, lw=1, ls=":")
    axes[0].text(400, 4 * PR.ETA * 365 + 15, "毎日1回の上限 1,314", color=MUTED, fontsize=8.5, ha="right", va="bottom")
    axes[0].set_ylim(0, 1450)
    axes[0].set_title("1kW あたりの放電（kWh/kW-年）", loc="left", color=INK, fontsize=11)
    axes[1].set_title("各日の高い4時間・安い4時間の価格（円/kWh）", loc="left", color=INK, fontsize=11)
    axes[2].set_title("1kW の価値 π（円/kW-年）", loc="left", color=INK, fontsize=11)
    for ax in axes:
        ax.set_xlabel("蓄電池の量（万kW）", color=MUTED)
        _spines(ax)
        ax.legend(frameon=False, fontsize=8.5)
    axes[2].set_ylim(0, None)
    fig.text(0.01, -0.08, "主の前提（容量価格14,972円、上乗せあり）。量ごとに蓄電池全体の充放電を一度に解く（安い時間から充電・高い時間から放電し、値差が往復の損失を"
             "上回るあいだ続ける。1日4時間分まで。同じ時間に充電と放電はしない。区切りでは蓄電池の入札が値を決める）。\n"
             "π は、その価格で1kW が各日の安い4時間に充電・高い4時間に放電したときの粗利×実行できる比−充電の従量費。往復効率0.9", fontsize=8.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "simple_battery_operation.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote figures")


if __name__ == "__main__":
    main()
