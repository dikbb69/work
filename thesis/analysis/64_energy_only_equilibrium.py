#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""【試作 2026-10-25】容量市場のないエネルギーのみの市場の長期均衡で、蓄電池はどこまで増えるか（著者の提案）

著者の問い（2026-10-25）: どの時間帯でも需要を100% 満たすことは必須条件。容量市場と補助がなければ、太陽光・風力・原子力で
  稼働時間が減った火力は、少ない時間で固定費を回収できるよう入札価格を上げ、朝夕の価格は固定費を回収できる水準まで上がる。
  蓄電池は余剰の時間に安く充電して高い時間に売るので、値幅が一定以上のあいだは参入し、カニバリゼーションでどこかで止まる。その均衡点を求める。
方法: 競争的なエネルギーのみの市場（価格の上限なし、参入・退出は自由、市場支配力なし）の長期均衡は、費用（固定費＋運転費）を最小にする
  電源構成と一致し、各時間の価格は需給の制約の双対変数になる（Boiteux 1949; Steiner 1957; Schmalensee 2022; Junge, Mallapragada &
  Schmalensee 2022; Korpås & Botterud 2020）。均衡では、残る設備はどれも固定費をちょうど回収する（利潤0）。
  需要を100% 満たす制約は等式（供給不足を許さない）で置く。供給力が詰まる時間の価格（希少性のレント）は、限界の設備の固定費を回収する水準になる。
設備:
  - 既設の火力（58 のユニット。年の運転中のもの）: 容量は0〜既設（維持の固定費を回収できなければ退出）。最大出力は補修率で減らす（58 の AVAIL）。
    燃料費は 60（発電コスト検証WG の効率・燃料諸経費、月別の輸入価格）。非調整火力（72万kW、自家発等）は市場の判断の外に置き、固定費は数えない。
  - 新設の LNG コンバインド: 建設費26.8万円/kW（発電コスト検証WG 2025/2/6 p.14）、40年・6%、運転維持費は WG の諸元、燃料費は LNG。
  - 新設の蓄電池（4時間）: 資本費は params_v4.capex_path（WG と同じ方法）、運転維持5,000円＋廃止費＋託送等の固定費、往復効率0.90、充電の従量費。
  - 揚水（京極）: 動力68万kW・発電60万kW・上池394万kWh・効率0.7（55 と同じ）。
  - 再エネ: 太陽光（制御できない屋根置き・旧ルールの分 U を除く）・風力・水力は0円で抑制・放流できる。原子力・地熱・バイオマスの最低は必ず出る。
  - 系統の安定のための火力の床（マストラン3台の最低出力＋非調整火力の最低、計426MW）を主とし、感応度で外す。
  - 北本: 主は孤立系（希少性の上限側）。感応度で、東北の実績価格で受電・送電できる連系（上限は 61 と同じ）。
既設の火力の維持の固定費（円/kW-年、発電コスト検証WG のモデルプラントの運転維持費＋発電側課金の kW 分1,500円）:
  石炭: 人件費5.8億円/70万kW＋修繕費2.0%＋諸費2.3%（建設費26.5万円）＋一般管理費12.5% ≒ 13,750＋1,500
  LNG: 4.6億円/60万kW＋2.4%＋1.1%（26.8万円）＋14.0% ≒ 11,570＋1,500
  石油: 1.9億円/40万kW＋1.8%＋0.9%（29.3万円）＋9.3% ≒ 9,170＋1,500
  （既設の古いユニットに新設のモデルプラントの修繕費の比率を当てるのは近似。感応度で上下させる）
出力: data/processed/energy_only_*.csv
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params_v4 as P4

ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
ns = {"__file__": os.path.join(HERE, "61_signal_market.py"), "__name__": "m61"}
exec(open(os.path.join(HERE, "61_signal_market.py"), encoding="utf-8").read().split("# ---------------------------------------------------------------- 計算")[0], ns)
m55, m58, m59 = ns["m55"], ns["m58"], ns["m59"]
sc_year, EI = ns["sc_year"], ns["EI"]
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------- 費用
CRF40 = 0.06 * 1.06 ** 40 / (1.06 ** 40 - 1)
FC_EXIST = {"石炭": 13_750.0 + 1_500.0, "LNG": 11_570.0 + 1_500.0, "石油": 9_170.0 + 1_500.0}
CCGT_CAPEX = 268_000.0
FC_CCGT = CCGT_CAPEX * CRF40 + 11_570.0 + 1_500.0 + 0.05 * CCGT_CAPEX / 1.06 ** 40 * CRF40
W_CHG = P4.LOSS * (1.02 + 4.18) / 1.1                            # 充電の従量費（円/kWh 充電、損失分のみ）
FLOOR_MW = 426.0
U_CAP = m55["U_FIXED"]


def hourly_inputs(sc, fy_w):
    """気象年 fy_w の時間別の入力（MW）。sc は 61 の sc_year の戻り値"""
    df = m55["build_future"](fy_w, sc).reset_index(drop=True)
    n = len(df) // 24 * 24
    df = df.iloc[:n]
    S, W = df["S"].to_numpy(float), df["W"].to_numpy(float)
    U = np.minimum(U_CAP * df["cf_S"].to_numpy(float), S)
    must = df["N"].to_numpy(float) + U + sc.get("bio_min", 410.0) + sc.get("geo", 50.0)
    curtailable = S + W - U + df["hydro"].to_numpy(float)
    return dict(D=df["D"].to_numpy(float), must=must, cur=curtailable, pth=df["p_tohoku"].to_numpy(float),
                month=df["month"].to_numpy(int), dates=pd.DatetimeIndex(df["ts"]).normalize(), n=n)


def fleet_tech(year, dates, month):
    """既設の火力（ユニットごと）と新設の LNG。戻り値: list of dict(name, fuel, cap_max, fc, vc(h), avail(h), must)"""
    techs = []
    for u in m58["fleet"](year):
        ft = m59["FUELTYPE"](u)
        vc_day = m59["vc_matrix"](u, dates.unique())[:, 0]
        vc = pd.Series(vc_day, index=dates.unique()).reindex(dates).to_numpy()
        av = np.array(m58["AVAIL"][ft])[month - 1] / 100.0
        techs.append(dict(name=u[0], fuel=ft, cap_max=float(u[1]), fc=0.0 if u[0] == "非調整火力" else FC_EXIST[ft], vc=vc, avail=av,
                          fixed=u[0] == "非調整火力"))
    lng = [t for t in techs if t["fuel"] == "LNG"][0]
    vc_new = lng["vc"] * 13.0 / [u for u in m58["fleet"](year) if u[0] == lng["name"]][0][3] * 1.0
    techs.append(dict(name="新設 LNG CC", fuel="LNG", cap_max=None, fc=FC_CCGT, vc=vc_new, avail=lng["avail"], fixed=False))
    return techs


def solve_eo(sc, fys=(2024,), batt_fc=None, link=False, floor=True, fc_scale=1.0, carbon=0.0, verbose=True,
             p_cap=0.0, kappa_th=1.0, kappa_b=0.861, reserve=True, res_frac=0.02, res_unit=663.0):
    """p_cap: 一定と置く容量価格（円/kW）。火力は κ_th×p_cap、蓄電池は κ_b×p_cap の容量収入を受け、固定費から差し引く。
    reserve: 毎時間、上げの予備力（需要×res_frac＋最大単機 res_unit）を、火力の余力・揚水・蓄電池（充電量の裏づけ1時間分）で確保する"""
    """エネルギーのみの市場の長期均衡（費用最小）。戻り値: 容量、時間別の価格、収入の内訳"""
    year = sc["year"]
    INP = [hourly_inputs(sc, fy) for fy in fys]
    Y = len(fys)
    H = sum(x["n"] for x in INP)
    D = np.concatenate([x["D"] for x in INP])
    must = np.concatenate([x["must"] for x in INP])
    cur = np.concatenate([x["cur"] for x in INP])
    pth = np.concatenate([x["pth"] for x in INP])
    month = np.concatenate([x["month"] for x in INP])
    dates = pd.DatetimeIndex(np.concatenate([x["dates"].values for x in INP]))
    techs = fleet_tech(year, dates, month)
    for t in techs:
        t["vc"] = t["vc"] + carbon * EI[t["fuel"]] / 1_000.0
    nT = len(techs)
    if batt_fc is None:
        cx = P4.capex_path(year)
        batt_fc = cx * 4 * P4.CRF20 + P4.OM_BASE + P4.decom(cx) + P4.NET_FIX
    # 変数の並び: [cap_t (nT)] [P_batt] [g_t,h (nT×H)] [curt_h] [c_h] [d_h] [s_h] [pp_h] [pg_h] [r_h] [imp_h] [exp_h] [rb_h] [rp_h]
    off = {}
    k = 0
    for nm, size in (("cap", nT), ("P", 1), ("g", nT * H), ("curt", H), ("c", H), ("d", H), ("s", H), ("pp", H), ("pg", H), ("r", H),
                     ("imp", H if link else 0), ("exp", H if link else 0), ("rb", H if reserve else 0), ("rp", H if reserve else 0)):
        off[nm] = k
        k += size
    NV = k
    cost = np.zeros(NV)
    lb, ub = np.zeros(NV), np.full(NV, np.inf)
    for i, t in enumerate(techs):
        cost[off["cap"] + i] = (t["fc"] * fc_scale - kappa_th * p_cap) * 1_000 if not t["fixed"] else 0.0   # 円/kW-年 → 円/MW-年（容量収入を差し引く）
        if t["cap_max"] is not None:
            ub[off["cap"] + i] = t["cap_max"]
        if t["fixed"]:
            lb[off["cap"] + i] = t["cap_max"]
        cost[off["g"] + i * H: off["g"] + (i + 1) * H] = t["vc"] / Y * 1_000      # 円/MWh（MW×h）。年あたりに直すため /Y
    cost[off["P"]] = (batt_fc - kappa_b * p_cap) * 1_000                                 # 円/MW-年（容量収入を差し引く）
    cost[off["c"]: off["c"] + H] = W_CHG * 1_000 / Y
    ub[off["curt"]: off["curt"] + H] = cur
    ub[off["pp"]: off["pp"] + H] = 680.0
    ub[off["pg"]: off["pg"] + H] = 600.0
    ub[off["r"]: off["r"] + H] = 3_940.0
    if link:
        mexp = sc.get("X_fixed", 570.0)
        mimp = sc.get("mimp_mw", 900.0)
        ub[off["imp"]: off["imp"] + H] = mimp
        ub[off["exp"]: off["exp"] + H] = mexp
        cost[off["imp"]: off["imp"] + H] = pth * 1_000 / Y
        cost[off["exp"]: off["exp"] + H] = -pth * 1_000 / Y
    rows, cols, vals, b_eq = [], [], [], []
    rows_ub, cols_ub, vals_ub, b_ub = [], [], [], []
    hidx = np.arange(H)
    # (1) 需給: Σ g + d + pg + (cur − curt) + must + imp − exp − c − pp = D   → Σg + d + pg − curt + imp − exp − c − pp = D − must − cur
    r0 = 0
    for i in range(nT):
        rows.append(r0 + hidx); cols.append(off["g"] + i * H + hidx); vals.append(np.ones(H))
    for nm, sgn in (("d", 1), ("pg", 1), ("curt", -1), ("c", -1), ("pp", -1)) + ((("imp", 1), ("exp", -1)) if link else ()):
        rows.append(r0 + hidx); cols.append(off[nm] + hidx); vals.append(np.full(H, float(sgn)))
    b_eq.append(D - must - cur)
    r0 += H
    # (2) 蓄電池の充電量: s_h − s_{h−1} − 0.9 c_h + d_h = 0（各気象年の中で循環）
    starts = np.cumsum([0] + [x["n"] for x in INP])[:-1]
    prev = hidx - 1
    for st, x in zip(starts, INP):
        prev[st] = st + x["n"] - 1
    for nm, v_ in (("s", 1.0), ("c", -P4.ETA), ("d", 1.0)):
        rows.append(r0 + hidx); cols.append(off[nm] + hidx); vals.append(np.full(H, v_))
    rows.append(r0 + hidx); cols.append(off["s"] + prev); vals.append(np.full(H, -1.0))
    b_eq.append(np.zeros(H))
    r0 += H
    # (3) 揚水の上池: r_h − r_{h−1} − 0.7 pp_h + pg_h = 0
    for nm, v_ in (("r", 1.0), ("pp", -0.7), ("pg", 1.0)):
        rows.append(r0 + hidx); cols.append(off[nm] + hidx); vals.append(np.full(H, v_))
    rows.append(r0 + hidx); cols.append(off["r"] + prev); vals.append(np.full(H, -1.0))
    b_eq.append(np.zeros(H))
    r0 += H
    A_eq = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(r0, NV))
    b_eq = np.concatenate(b_eq)
    # 不等式: g_t,h − avail_h·cap_t ≤ 0、c_h − P ≤ 0、d_h − P ≤ 0、s_h − 4P ≤ 0、−Σ(マストランの火力 g) ≤ −床
    q0 = 0
    for i, t in enumerate(techs):
        rows_ub.append(q0 + hidx); cols_ub.append(off["g"] + i * H + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(np.full(H, off["cap"] + i)); vals_ub.append(-t["avail"])
        b_ub.append(np.zeros(H))
        q0 += H
    for nm, mult in (("c", 1.0), ("d", 1.0), ("s", 4.0)):
        rows_ub.append(q0 + hidx); cols_ub.append(off[nm] + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(np.full(H, off["P"])); vals_ub.append(np.full(H, -mult))
        b_ub.append(np.zeros(H))
        q0 += H
    if reserve:
        # 上げの予備力: Σ avail·cap − Σ g + rb + rp ≥ R_h  →  −Σ avail·cap + Σ g − rb − rp ≤ −R_h
        q_res = q0
        for i, t in enumerate(techs):
            rows_ub.append(q0 + hidx); cols_ub.append(np.full(H, off["cap"] + i)); vals_ub.append(-t["avail"])
            rows_ub.append(q0 + hidx); cols_ub.append(off["g"] + i * H + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(off["rb"] + hidx); vals_ub.append(-np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(off["rp"] + hidx); vals_ub.append(-np.ones(H))
        b_ub.append(-(res_frac * D + res_unit))
        q0 += H
        # 蓄電池: rb ≤ P − d + c、rb ≤ s（1時間分の充電量）。揚水: rp ≤ 600 − pg + pp、rp ≤ r
        for nm, coef in (("P", -1.0),):
            rows_ub.append(q0 + hidx); cols_ub.append(off["rb"] + hidx); vals_ub.append(np.ones(H))
            rows_ub.append(q0 + hidx); cols_ub.append(np.full(H, off["P"])); vals_ub.append(np.full(H, coef))
            rows_ub.append(q0 + hidx); cols_ub.append(off["d"] + hidx); vals_ub.append(np.ones(H))
            rows_ub.append(q0 + hidx); cols_ub.append(off["c"] + hidx); vals_ub.append(-np.ones(H))
            b_ub.append(np.zeros(H))
            q0 += H
        rows_ub.append(q0 + hidx); cols_ub.append(off["rb"] + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(off["s"] + hidx); vals_ub.append(-np.ones(H))
        b_ub.append(np.zeros(H))
        q0 += H
        rows_ub.append(q0 + hidx); cols_ub.append(off["rp"] + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(off["pg"] + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(off["pp"] + hidx); vals_ub.append(-np.ones(H))
        b_ub.append(np.full(H, 600.0))
        q0 += H
        rows_ub.append(q0 + hidx); cols_ub.append(off["rp"] + hidx); vals_ub.append(np.ones(H))
        rows_ub.append(q0 + hidx); cols_ub.append(off["r"] + hidx); vals_ub.append(-np.ones(H))
        b_ub.append(np.zeros(H))
        q0 += H
    if floor:
        mr = [i for i, t in enumerate(techs) if t["name"] in ("石狩湾新港1", "苫東厚真4", "知内2", "非調整火力")]
        for i in mr:
            rows_ub.append(q0 + hidx); cols_ub.append(off["g"] + i * H + hidx); vals_ub.append(-np.ones(H))
        b_ub.append(np.full(H, -FLOOR_MW))
        q0 += H
    A_ub = sp.csr_matrix((np.concatenate(vals_ub), (np.concatenate(rows_ub), np.concatenate(cols_ub))), shape=(q0, NV))
    b_ub = np.concatenate(b_ub)
    t0 = time.time()
    res = linprog(cost, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=np.column_stack([lb, ub]), method="highs")
    if verbose:
        print(f"  LP: 変数{NV:,}・制約{r0 + q0:,}・{time.time() - t0:.0f}秒・{res.message}")
    assert res.status == 0, res.message
    x = res.x
    price = res.eqlin.marginals[:H] * Y / 1_000                                  # 円/kWh（電力量の価格 λ）
    mu = -res.ineqlin.marginals[q_res: q_res + H] * Y / 1_000 if reserve else np.zeros(H)   # 予備力の価格 μ（円/kW・h）
    cap = {t["name"]: x[off["cap"] + i] for i, t in enumerate(techs)}
    Pb = x[off["P"]]
    c, d = x[off["c"]: off["c"] + H], x[off["d"]: off["d"] + H]
    out = dict(cap=cap, P_batt=Pb, price=price, mu=mu, techs=techs, H=H, Y=Y, D=D, must=must, cur=cur, month=month, p_cap=p_cap,
               hour=np.tile(np.arange(24), H // 24), batt_fc=batt_fc,
               batt_rev=float((price * (d - c)).sum() / Y - (W_CHG * c).sum() / Y) / max(Pb, 1e-9) if Pb > 1e-6 else np.nan,   # 円/kW-年
               g={t["name"]: x[off["g"] + i * H: off["g"] + (i + 1) * H] for i, t in enumerate(techs)}, c=c, d=d)
    rb = x[off["rb"]: off["rb"] + H] if reserve else np.zeros(H)
    out["batt_res_rev"] = float((mu * rb).sum() / Y) / max(Pb, 1e-9) if Pb > 1e-6 else np.nan
    rent = {}
    for i, t in enumerate(techs):
        g = out["g"][t["name"]]
        head = t["avail"] * cap[t["name"]] - g
        rent[t["name"]] = (float(((price - t["vc"]) * g).sum() / Y + (mu * head).sum() / Y) / max(cap[t["name"]], 1e-9)
                           if cap[t["name"]] > 1e-6 else np.nan)   # 円/kW-年（電力量の粗利＋予備力の収入）
    out["rent"] = rent
    return out


def summarize(o, label):
    p = o["price"]
    ev = (o["hour"] >= 16) & (o["hour"] <= 21)
    srt = np.sort(p)[::-1]
    pm = p + o["mu"]
    r = {"ケース": label, "容量価格(円/kW)": o["p_cap"], "蓄電池（万kW）": o["P_batt"] / 10, "蓄電池の固定費(円/kW-年)": o["batt_fc"],
         "蓄電池の容量収入(円/kW-年)": 0.861 * o["p_cap"], "蓄電池の電力量の粗利(円/kW-年)": o["batt_rev"],
         "蓄電池の予備力の収入(円/kW-年)": o.get("batt_res_rev", np.nan), "新設 LNG CC（万kW）": o["cap"].get("新設 LNG CC", 0) / 10,
         "予備力の価格が正の時間(h/年)": (o["mu"] > 1e-6).sum() / o["Y"], "予備力込みの価格の夕方の平均": pm[ev].mean(),
         "予備力込みの価格の最高": pm.max(),
         "価格の平均": p.mean(), "夕方16〜21時の平均": p[ev].mean(), "最高": p.max(),
         "上位10時間の平均": srt[:10 * o["Y"]].mean(), "50円超の時間(h/年)": (p > 50).sum() / o["Y"], "100円超(h/年)": (p > 100).sum() / o["Y"],
         "0円以下の時間(h/年)": (p <= 0.011).sum() / o["Y"]}
    for t in o["techs"]:
        if not t["fixed"]:
            r[f"{t['name']} 残る容量(MW)"] = o["cap"][t["name"]]
    return r


if __name__ == "__main__":
    MAIN = {"y2040": "OCCTO 11,000億kWh", "nuc": "主"}
    CASES = [("2030 主（泊3号）", 2030, MAIN), ("2035 主（泊1・3号）", 2035, MAIN),
             ("2035 原子力なし", 2035, {"y2040": "OCCTO 11,000億kWh", "nuc": "原子力なし"}),
             ("2040 主（11,000億kWh）", 2040, MAIN), ("2040 エネ基×3.0", 2040, {"y2040": "エネ基の倍率×3.0（需要は11,000億kWh）", "nuc": "主"}),
             ("2040 9,000億kWh", 2040, {"y2040": "OCCTO 9,000億kWh", "nuc": "主"})]
    PCAP = {"2029年度向けの実績14,972円": 14_972.0, "6回の平均11,867円": 11_867.0, "容量収入なし": 0.0}
    rows, prof = [], []
    for lab, y, pth in CASES:
        sc = sc_year(y, pth)
        for pn, pc in PCAP.items():
            t0 = time.time()
            o = solve_eo(sc, fys=(2023, 2024, 2025), p_cap=pc, reserve=True, verbose=False)
            r = summarize(o, lab)
            r["容量価格の置き方"] = pn
            r["秒"] = time.time() - t0
            rows.append(r)
            pm = o["price"] + o["mu"]
            for season, ms in (("冬（12〜2月）", (12, 1, 2)), ("春（4〜5月）", (4, 5)), ("夏（7〜8月）", (7, 8))):
                sel = np.isin(o["month"], ms)
                for h in range(24):
                    m_ = sel & (o["hour"] == h)
                    prof.append({"ケース": lab, "容量価格の置き方": pn, "季節": season, "時": h, "電力量の価格の中央値": float(np.median(o["price"][m_])),
                                 "電力量の価格の平均": float(o["price"][m_].mean()), "予備力込みの平均": float(pm[m_].mean())})
            print(f"{lab} / {pn}: 蓄電池 {r['蓄電池（万kW）']:.1f}万kW、新設LNG {r['新設 LNG CC（万kW）']:.1f}、夕方の平均 {r['夕方16〜21時の平均']:.1f}円、"
                  f"予備力の価格が正 {r['予備力の価格が正の時間(h/年)']:.1f}h/年、最高 {r['予備力込みの価格の最高']:,.0f}円、{r['秒']:.0f}秒", flush=True)
    R = pd.DataFrame(rows)
    R.round(2).to_csv(os.path.join(PROC, "energy_only_equilibrium.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(prof).round(3).to_csv(os.path.join(PROC, "energy_only_price_profile.csv"), index=False, encoding="utf-8-sig")
    print(R.round(1).T.to_string())
