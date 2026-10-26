#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""構造モデル（55）の時間の局面で価格を決め、蓄電池の収益 π(K) と市場だけで成立する容量 K* を求める

価格の決め方（時間 h）:
  - 下げ代不足（再エネを全部止めても余る）: 現行の制度では 0.01円。負の価格を許す制度では −c 円（c は制度上の最低価格。
    この時間に限界になるのは長期固定電源・制御できない再エネで、停止コストから深さを決められないので、5・10円の格子で示す）。
  - 再エネの抑制（事業用の再エネが限界、停止コスト≈0）: 0.01円（負の価格を許しても≈0 で、差は無視できる）。
  - 火力が限界: 41 の仕様A（26、θ=1）の g(net)+μ。net＝需要−太陽光−風力−原子力。g の推定範囲より下の net は、
    推定範囲の下端（下限価格より上の最初の点）で止める（構造上は火力が限界なので、価格を下限に落とさない。notes/36 §8.8）。
  蓄電池の充電は、まず下げ代不足、次に再エネの抑制を吸収し（価格は変わらない）、それを超えると net を押し上げる。
  放電は net を押し下げる。フリートは 41 と同じ増分貪欲（刻み1万kW、各日の最安4時間に充電・最高4時間に放電）。
前提: 往復効率0.90（OCCTO）、費用は params_v4（託送の蓄電池特措、揚水等損失率0.10、税抜）、容量価格は北海道ブロック（2030年度向け近似）。
  収益は実績整合: λ＝実績の戦略c（往復効率0.90）÷ 現状のモデル（このスクリプトの価格の決め方、原子力なし・FY2023〜25 の実績の需給）の c(K=0)。
シナリオ: 55 の2035年の基準（OCCTO 需要想定、太陽光356・風力275万kW、火力の床61万kW、北本57万kW など）に、泊・自家消費・
  直流連系を重ねる。気象年は FY2023〜25（フリートの戦略c の履歴のため 2023-02〜03 も計算）。
出力: data/processed/structural_battery_value.csv、figures/hokkaido/structural_battery_value.png
"""
import contextlib
import io
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)


def load_head(fn, cut):
    src = open(os.path.join(HERE, fn), encoding="utf-8").read().split(cut)[0]
    ns = {"__file__": os.path.join(HERE, fn), "__name__": "mod_" + fn[:2]}
    _t = pd.DataFrame.to_csv
    pd.DataFrame.to_csv = lambda *a, **k: None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(src, ns)
    finally:
        pd.DataFrame.to_csv = _t
    return ns


m41 = load_head("41_equilibrium_v3.py", "\ncurves = []\n")
C_ACT = P4.set_eta(m41)
ETA = m41["ETA"]
m55 = load_head("55_structural_balance_model.py", "\nSC_ROWS = []\n")
daily_eval, annual, g_curve = m41["daily_eval"], m41["annual"], m41["g_curve"]
G26, MU26B, SEASB, BLK, RB, W_B, FYB, EVB, DAYS = (m41[k] for k in ("G26", "MU26B", "SEASB", "BLK", "RB", "W_B", "FYB", "EVB", "DAYS"))
FLOOR = m41["FLOOR"]
print(f"往復効率 {ETA:.2f}、実績の戦略c {C_ACT:,.1f}円/kW-年（FY2023〜25）。55 の運用のマージン δ={m55['DELTA']:.1f}MW")

# g の推定範囲の下端（季節別、下限価格より上の最初の点）
X_LO = {}
for s in range(4):
    x, y = G26[s]
    X_LO[s] = x[int(np.argmax(y > FLOOR + 0.001))]
XLO_B = np.vectorize(X_LO.get)(SEASB)
DATES_B = DAYS[BLK]


def structural_rows(sc, current=False):
    """BLK の日（2023-02〜2026-03）の時間別に、55 の需給（電池なし）を作る。current=True は実績の需給（原子力なし）"""
    outs, frames = [], []
    for fy in (2022, 2023, 2024, 2025):
        if current:
            df = m55["prep_actual"](fy)
            hyd = df.groupby("month")["hydro"].mean().to_dict()
            cfg = {**m55["MAIN_CFG"], "year": fy, "opcap": m55["OPCAP_EAST"]["FY2025"], "hyd_mon": hyd, "hy_mid": m55["hy_mid_for"](hyd),
                   "eps": m55["DELTA"]}
        else:
            df = m55["build_future"](fy, sc)
            hyd = df.groupby("month")["hydro"].mean().to_dict()
            cfg = {**m55["MAIN_CFG"], "year": sc["year"], "opcap": m55["OPCAP_EAST"]["FY2028+"], "hyd_mon": hyd, "hy_mid": m55["hy_mid_for"](hyd),
                   "eps": sc.get("eps", 0.0), "U_cap": m55["U_FIXED"], "bio_min": sc.get("bio_min", 410.0), "geo": sc.get("geo", 50.0),
                   "nonadj": 65.0, "batt": 20.0, "pump_mw": sc.get("pump_mw", 680.0), "X_tohoku_rule": sc.get("X_tohoku_rule", False)}
            for k2 in ("floor_override", "X_fixed"):
                if k2 in sc:
                    cfg[k2] = sc[k2]
        o = m55["simulate"](df, cfg)
        o["net"] = (df["D"] - df["S"] - df["W"] - df["N"]).to_numpy()
        frames.append(o)
    o = pd.concat(frames, ignore_index=True)
    o["date"] = o["ts"].dt.normalize()
    o = o.set_index(["date", o["ts"].dt.hour]).sort_index()
    idx = pd.MultiIndex.from_product([DATES_B, range(24)])
    o = o.reindex(idx)
    assert not o["curt"].isna().any(), "BLK の日がそろわない"
    sh = (len(DATES_B), 24)
    return {k: o[k].to_numpy(float).reshape(sh) for k in ("curt", "deficit", "net", "S", "W")}


def make_price(st, def_price):
    curt0, def0, net0 = st["curt"], st["deficit"], st["net"]

    def price(chg, dis):
        rem_def = def0 - chg
        rem_curt = curt0 - np.maximum(chg - def0, 0.0)
        extra = np.maximum(chg - def0 - curt0, 0.0)
        net = np.maximum(net0 + extra - dis, XLO_B)
        p_th = np.maximum(g_curve(net, G26, SEASB) + MU26B, FLOOR)
        return np.where(rem_def > 1e-9, def_price, np.where(rem_curt > 1e-9, FLOOR, p_th))
    return price


K_EVAL = list(range(0, 101)) + list(range(105, 201, 5))


def run_fleet(price, Ks=K_EVAL):
    chg = np.zeros((len(DATES_B), 24))
    dis = np.zeros_like(chg)
    done, out = 0.0, []
    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            p = price(chg, dis)
            o = np.argsort(p, 1)
            c4, d4 = o[:, :4], o[:, -4:]
            mg = np.take_along_axis(p, d4, 1).sum(1) * ETA - np.take_along_axis(p, c4, 1).sum(1)
            a = mg > 0
            chg[RB[a], c4[a]] += st * 10.0
            dis[RB[a], d4[a]] += st * 10.0 * ETA
            done += st
        p = price(chg, dis)
        d = daily_eval(p, W_B)
        out.append({"K(万kW)": K, "c": annual(d["c"], FYB, EVB), "π_PF": annual(d["pf"], FYB, EVB),
                    "負の時間(h/年)": float((p[EVB] < 0).sum() / EVB.sum() * 365),
                    "下限の時間(h/年)": float((np.abs(p[EVB] - FLOOR) < 1e-9).sum() / EVB.sum() * 365)})
    return pd.DataFrame(out)


CAPP = pd.read_csv(os.path.join(PROC, "capacity_price_of_k_v3.csv"))
KP = lambda K: np.interp(K, CAPP["K(万kW)"].to_numpy(float), CAPP[P4.KP_COL].to_numpy(float))


def kstar(df, lam, capex):
    K = df["K(万kW)"].to_numpy(float)
    slack = (lam * df["c"] - P4.W_LOSS).clip(lower=0).to_numpy() + KP(K) - P4.c_req(capex)
    if slack[0] < 0:
        return 0.0
    neg = np.where(slack < 0)[0]
    if len(neg) == 0:
        return float(K[-1])
    i = neg[0]
    return float(K[i - 1] + (K[i] - K[i - 1]) * slack[i - 1] / (slack[i - 1] - slack[i]))


# ---------------------------------------------------------------- 現状（実績の需給、原子力なし）で λ を校正
ST_NOW = structural_rows(None, current=True)
NOW = run_fleet(make_price(ST_NOW, FLOOR), [0])
LAM = C_ACT / NOW["c"].iloc[0]
print(f"現状（このスクリプトの価格の決め方）: c(0)={NOW['c'].iloc[0]:,.0f}、π_PF(0)={NOW['π_PF'].iloc[0]:,.0f}、下限の時間 {NOW['下限の時間(h/年)'].iloc[0]:.0f}h/年 → λ={LAM:.4f}")

# ---------------------------------------------------------------- シナリオ
BASE = dict(m55["BASE35"])
NUC = m55["NUC_SC"]
NUC_UNITS = m55["NUC_UNITS"]


def sc_of(nuc, **kw):
    sc = {**BASE, **kw}
    names, mw = NUC[nuc]
    sc["nuclear_mw"], sc["nuc_units"] = mw, [NUC_UNITS[n] for n in names] or [0.0]
    return sc


SCEN = [("現状（FY2023〜25 の実績の需給）", None, {})]
for nuc in ("原子力なし", "泊3号", "泊1・3号", "泊全基"):
    for ds in (0, 600, 1_000):
        SCEN.append((f"2035 {nuc} 自家消費+{ds // 10}万kW", nuc, {"selfcons_mw": float(ds)}))
for nuc in ("泊1・3号", "泊全基"):
    SCEN.append((f"2035 {nuc} 自家消費+100万kW 直流連系+200万kW", nuc, {"selfcons_mw": 1_000.0, "X_fixed": 570.0 + 0.55 * 2_000.0}))
ROWS = []
for lab, nuc, kw in SCEN:
    st = ST_NOW if nuc is None else structural_rows(sc_of(nuc, **kw))
    for reg, dp in (("現行（0.01円）", FLOOR), ("負の価格 −5円", -5.0), ("負の価格 −10円", -10.0)):
        if nuc is None and reg != "現行（0.01円）":
            continue
        df = run_fleet(make_price(st, dp))
        pi = LAM * df["c"] - P4.W_LOSS
        r = {"シナリオ": lab, "下げ代不足の価格": reg, "π(0)": pi.iloc[0], "π(20)": pi.iloc[20], "π(50)": pi.iloc[50],
             "負の時間 K=0(h/年)": df["負の時間(h/年)"].iloc[0], "負の時間 K=50(h/年)": df["負の時間(h/年)"].iloc[50],
             "下限の時間 K=0(h/年)": df["下限の時間(h/年)"].iloc[0]}
        for ck, cv in P4.CAPEX.items():
            r[f"K*（{ck}）"] = kstar(df, LAM, cv)
        ROWS.append(r)
        print(f"  {lab} / {reg}: π(0)={r['π(0)']:,.0f} π(50)={r['π(50)']:,.0f} 負の時間 {r['負の時間 K=0(h/年)']:.0f}h 下限の時間 {r['下限の時間 K=0(h/年)']:.0f}h "
              f"K*: {r['K*（6.8万）']:.1f}/{r['K*（4.0万）']:.1f}/{r['K*（2.3万）']:.1f}")
R = pd.DataFrame(ROWS)
R.round(3).to_csv(os.path.join(PROC, "structural_battery_value.csv"), index=False, encoding="utf-8-sig")
