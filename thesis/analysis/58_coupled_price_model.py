#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道の価格を、道内の供給曲線（ユニット別のメリットオーダー）と北本連系線による本州（東北）との連系から演繹的に決める

背景（2026-10-23）: FY2023〜25 の北海道エリアの価格は、76% の時間で東北と同じだった（北海道が高い12%、低い12%）。北海道の
電源構成の変化が価格に現れるのは、北本が詰まって市場が分かれる時間に限られる。
価格の決め方（時間 h）:
  道内の供給曲線: 価格によらず出る供給 Q0（原子力・水力・バイオマス・地熱・制御できない再エネ・揚水の発電・運転中の火力の最低出力）、
    事業用の再エネ V（≈0円で抑制できる）、火力の増分（燃料費）、毎日起動停止できるユニット（LNG コンバインド・GT）の札
    （燃料費＋起動費÷（運転時間H×出力Q）。監視等委員会の整理のブロック入札の価格、第36回制度設計専門会合 資料5 p.13）。
  連系: 東北の価格 p_TH（気象年の実績）で、北本の受電・送電の上限まで電気が動く。受電の上限 M_imp＝北海道向の運用容量−マージン、
    送電の上限 M_exp＝東北向の運用容量−マージン。東北が下限価格（≤0.011円）の時間は東北も余っているので送電0。
  市場の結果: 道内の供給（p_TH での）−需要が送電・受電の上限の内側なら、価格＝p_TH。送電の上限を超えるなら、北海道の価格は下がり、
    再エネの抑制（0.01円）か、下げ代不足（現行0.01円、負の価格のシナリオでは −c 円）になる。受電の上限を超えるなら、道内の限界の札まで上がる。
日ごとの運転台数（現行の規律、notes/36 §8.8）:
  マストラン3台（石狩湾新港1号 LNG・苫東厚真4号 石炭・知内2号 石油）は常時運転。その他の石炭・石油は、起動停止に8時間・1日1回の
  制約で日中に止められないので、運転するなら終日最低出力以上。
  - 昼に余剰が出ない日: 石炭は燃料費が安いので全台運転する（石油は供給力が足りない日だけ）。
  - 昼に余剰が出る日（道内の残余需要の最小がマストランの最低出力を下回る）: 優先給電ルールどおり、マストラン以外の石炭・石油を止める。
    ただし、夕方のピークに対して「運転中の容量＋毎日起動停止できるユニット＋北本の受電」が「残余需要×1.02＋最大機（苫東厚真4号）」に
    届かない場合は、石炭を燃料費の安い順に運転する。
シナリオ（後者、著者の提案 2026-10-23）: 物理的な制約で昼も最低出力で運転した損失（燃料費−価格）を、夕方（17〜22時）の札に上乗せして
  回収できる制度になった場合。上乗せは、ユニットごとにその日の損失÷夕方の定格出力×時間。価格に効くのは、北海道が受電の上限に達して
  道内の札が価格を決める時間だけ。
出力: data/processed/coupled_price_validation.csv、coupled_price_battery.csv、coupled_price_units.csv、figures/hokkaido/coupled_price_profile.png
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
daily_eval, annual = m41["daily_eval"], m41["annual"]
BLK, RB, W_B, FYB, EVB, DAYS, PACTM = (m41[k] for k in ("BLK", "RB", "W_B", "FYB", "EVB", "DAYS", "PACTM"))
DATES_B = DAYS[BLK]
FLOOR = 0.01
SCARCITY = 50.0
MARGIN_TIE = 300.0

# ---------------------------------------------------------------- ユニット（送電端の概数。最低出力は OCCTO ユニット別実績の運転時5%点、
# 燃料費は OCCTO 第103回広域系統整備委員会 資料3 p.53〜54 の現行シナリオ（燃料費＋CO2）、起動費は同 p.54 の式）
UNITS = [
    # 名前, 容量MW, 最低MW, 燃料費 円/kWh, 起動費 円, 毎日起動停止, マストラン, 運開年度, 廃止年度（この年度まで運転）
    ("石狩湾新港1", 548, 212, 13.0, 548 * 1_000 + 1_000_000, False, True, 2018, 2100),
    ("苫東厚真4", 663, 103, 10.4, 700 * 13_000, False, True, 2002, 2100),
    ("知内2", 333, 46, 27.8, 350 * 20_000 + 3_000_000, False, True, 1998, 2100),
    ("苫東厚真2", 562, 139, 11.2, 600 * 13_000, False, False, 1985, 2100),
    ("苫東厚真1", 327, 89, 11.5, 350 * 13_000, False, False, 1980, 2100),
    ("砂川3", 115, 34, 11.5, 125 * 13_000, False, False, 1977, 2026),
    ("砂川4", 113, 38, 11.5, 125 * 13_000, False, False, 1982, 2026),
    ("知内1", 329, 34, 27.8, 350 * 20_000 + 3_000_000, False, False, 1983, 2100),
    ("苫小牧1", 232, 70, 27.8, 250 * 20_000 + 3_000_000, False, False, 1973, 2029),
    ("苫小牧共同3", 246, 48, 27.8, 250 * 20_000 + 3_000_000, False, False, 1974, 2029),
    ("音別GT", 148, 30, 35.0, 148 * 20_000 + 3_000_000, True, False, 1978, 2029),
    ("石狩湾新港2", 580, 116, 13.0, 580 * 1_000 + 1_000_000, True, False, 2030, 2100),
    ("石狩湾新港3", 580, 116, 13.0, 580 * 1_000 + 1_000_000, True, False, 2033, 2100),
    # 非調整火力（自家発・IPP など、ユニット別の公開の対象外）: 設備72万kW（長期見通しの前提 p.12）、最低出力は前日計画の6.5万kW、
    # 燃料費は石炭並みと置く。常時運転（価格に応じて最低出力から定格まで）
    ("非調整火力", 720, 65, 11.5, 0.0, False, True, 1900, 2100),
]
# 月別の最大稼働率（100%−過去5か年平均の補修率、全国。OCCTO 広域系統長期方針 別冊 2023/3 p.47）。容量に掛ける
AVAIL = {"石炭": [96.1, 96.0, 88.3, 74.4, 72.4, 79.9, 93.0, 96.3, 91.6, 83.3, 84.8, 91.0],
         "LNG": [97.7, 98.6, 94.3, 85.5, 82.3, 87.5, 95.2, 98.0, 94.0, 86.1, 88.3, 94.0],
         "石油": [96.5, 96.7, 91.2, 84.6, 81.9, 81.1, 92.0, 92.4, 87.7, 79.5, 85.0, 92.6]}   # 1〜12月の順
FUELTYPE = lambda u: "LNG" if u[3] == 13.0 else ("石油" if u[3] >= 20 else "石炭")
DSS_H, DSS_QSHARE = 6.0, 0.85                                  # 毎日起動停止のユニットのブロック（6時間、定格の85%）
LARGEST = 663.0


def fleet(year):
    return [u for u in UNITS if u[7] <= year <= u[8]]


# ---------------------------------------------------------------- 時間別の入力（BLK の日）
def inputs(sc, current=False, floor_arr=None, eps_current=0.0):
    """55 の需給（電池なし）から、価格モデルの入力を BLK の日×24時間で作る。floor_arr は日ごとの火力の最低出力の合計（MW）"""
    frames = []
    for fy in (2022, 2023, 2024, 2025):
        if current:
            df = m55["prep_actual"](fy)
            hyd = df.groupby("month")["hydro"].mean().to_dict()
            cfg = {**m55["MAIN_CFG"], "year": fy, "opcap": m55["OPCAP_EAST"]["FY2025"], "hyd_mon": hyd, "hy_mid": m55["hy_mid_for"](hyd),
                   "eps": eps_current}
        else:
            df = m55["build_future"](fy, sc)
            hyd = df.groupby("month")["hydro"].mean().to_dict()
            # 55 の run_future と同じ前提（公式の2035年: 北本の送電57万kW 固定・東北の規則なし、直流連系は送電に0.55×容量を加える）
            cfg = {**m55["MAIN_CFG"], "year": sc["year"], "opcap": {m: v + sc.get("hvdc_mw", 0.0) for m, v in m55["OPCAP_EAST"]["FY2028+"].items()},
                   "hyd_mon": hyd, "hy_mid": m55["hy_mid_for"](hyd), "eps": sc.get("eps", 0.0), "U_cap": m55["U_FIXED"],
                   "bio_min": sc.get("bio_min", 410.0), "geo": sc.get("geo", 50.0), "nonadj": 65.0, "batt": 20.0,
                   "pump_mw": sc.get("pump_mw", 680.0), "X_tohoku_rule": sc.get("X_tohoku_rule", False)}
            if sc.get("X_fixed") is not None:
                cfg["X_fixed"] = sc["X_fixed"]
            if floor_arr is None and sc.get("floor_override") is not None:
                cfg["floor_override"] = sc["floor_override"]
        if floor_arr is not None:
            fa = floor_arr.reindex(pd.DatetimeIndex(df["ts"]).normalize().unique()).ffill().bfill().to_numpy()
            cfg["floor_override"] = fa
        o = m55["simulate"](df, cfg)
        o["p_TH"] = df["p_tohoku"].to_numpy()
        frames.append(o)
    o = pd.concat(frames, ignore_index=True)
    o["date"] = o["ts"].dt.normalize()
    o = o.set_index(["date", o["ts"].dt.hour]).sort_index().reindex(pd.MultiIndex.from_product([DATES_B, range(24)]))
    assert not o["D"].isna().any()
    sh = (len(DATES_B), 24)
    g = lambda k: o[k].to_numpy(float).reshape(sh)
    Bm = o["Bm"].to_numpy(float).reshape(sh)
    G = o["G"].to_numpy(float).reshape(sh)
    return dict(D=g("D"), N=g("N"), Hy=g("Hy"), Bm=Bm, G=G, U=g("U"), V=g("S") + g("W") - g("U"), P=g("P"), Pgen=g("Pgen"),
                curt=g("curt"), deficit=g("deficit"), X=g("X"), T55=g("T"), S=g("S"), W=g("W"),   # S・W は 65 の電源構成の集計用
                p_TH=g("p_TH"), month=np.repeat(DATES_B.month.to_numpy()[:, None], 24, 1))


TIE_ADD = {"exp": 0.0, "imp": 0.0}                            # 実効的な送電・受電の上限への加算（MW、FY2023〜25 で較正）


def tie_caps(sc, month, current):
    if current:
        east = np.vectorize(m55["OPCAP_EAST"]["FY2025"].get)(month).astype(float)
        west = np.full(month.shape, 900.0)
    else:
        east = np.full(month.shape, 1_000.0)
        west = np.full(month.shape, 1_200.0)
    hv = 0.0 if current else sc.get("hvdc_mw", 0.0)
    return np.maximum(east - MARGIN_TIE + TIE_ADD["exp"], 0) + hv, np.maximum(west - MARGIN_TIE + TIE_ADD["imp"], 0) + hv


def commit(I, year, chg=None, dis=None, nonadj=0.0):
    """日ごとの運転（マストラン以外の石炭・石油）。戻り値: 運転の行列（日×ユニット）、日ごとの最低出力の合計"""
    units = fleet(year)
    nd = I["D"].shape[0]
    net_b = (0 if chg is None else chg) - (0 if dis is None else dis)
    R = I["D"] + I["P"] + net_b - (I["N"] + I["Hy"] + I["Bm"] + I["G"] + I["U"] + I["V"] + I["Pgen"])
    must = [u for u in units if u[6]]
    f_must = sum(u[2] for u in must) + nonadj
    cap_must = sum(u[1] for u in must)
    dss_cap = sum(u[1] for u in units if u[5])
    extra = sorted([u for u in units if not u[6] and not u[5]], key=lambda u: u[3])
    on = np.zeros((nd, len(units)), bool)
    idx = {u[0]: i for i, u in enumerate(units)}
    for u in must:
        on[:, idx[u[0]]] = True
    Xexp = I.get("X", 0.0)                                     # 余剰の時間に送れる量（55 と同じ）
    surplus_day = (R + Xexp).min(1) < f_must                   # 送電を含めても、マストランの最低出力を下回る時間がある日
    need = R.max(1) * 1.02 + LARGEST - (cap_must + dss_cap + I["_Mimp_day"])
    for i in range(nd):
        if not surplus_day[i]:
            for u in extra:                                    # 余剰のない日: 石炭は全台、石油は足りないときだけ
                if u[3] < 20 or need[i] > 0:
                    on[i, idx[u[0]]] = True
                    need[i] -= u[1]
        else:
            for u in extra:                                    # 余剰の日: 足りない分だけ燃料費の安い順
                if need[i] <= 0:
                    break
                on[i, idx[u[0]]] = True
                need[i] -= u[1]
    floor = nonadj + (on * np.array([u[2] if not u[5] else 0.0 for u in units])[None, :]).sum(1)
    return units, on, floor


def clear(I, units, on, floor, Mexp, Mimp, chg=None, dis=None, def_price=FLOOR, markup=None):
    """各時間の価格・抑制・下げ代不足・ユニット別の出力。markup: (日×ユニット) の夕方の上乗せ（円/kWh）"""
    nd = I["D"].shape[0]
    Dd = I["D"] + I["P"] + (0 if chg is None else chg) - (0 if dis is None else dis)
    Q0 = I["N"] + I["Hy"] + I["Bm"] + I["G"] + I["U"] + I["Pgen"] + floor[:, None]
    V = I["V"]
    pTH = I["p_TH"]
    Mexp_eff = np.where(pTH <= 0.011, 0.0, Mexp)
    # 増分の札（日×時間×ユニット）
    K = len(units)
    caps = np.zeros((nd, 24, K))
    bids = np.full((nd, 24, K), np.inf)
    ev = np.zeros(24, bool)
    ev[17:23] = True
    av_m = lambda u: np.array(AVAIL[FUELTYPE(u)])[I["month"] - 1] / 100.0
    for k, u in enumerate(units):
        capm = u[1] * av_m(u)                                  # 補修を差し引いた容量（月別）
        if u[5]:                                               # 毎日起動停止: 定格の全量を札（燃料費＋起動費の上乗せ）
            caps[:, :, k] = capm
            bids[:, :, k] = u[3] + u[4] / (DSS_H * DSS_QSHARE * u[1] * 1_000)
        else:
            caps[:, :, k] = np.where(on[:, k][:, None], np.maximum(capm - u[2], 0.0), 0.0)
            b = np.full((nd, 24), u[3])
            if markup is not None:
                b = b + np.where(ev[None, :], markup[:, k][:, None], 0.0)
            bids[:, :, k] = np.where(on[:, k][:, None], b, np.inf)
    o = np.argsort(bids, 2)
    bs = np.take_along_axis(bids, o, 2)
    cs = np.take_along_axis(caps, o, 2)
    cum = np.cumsum(cs, 2)
    s_at = Q0 + V + (cs * (bs <= pTH[:, :, None])).sum(2)
    E = s_at - Dd
    p = pTH.copy()
    curt = np.zeros_like(p)
    deficit = np.zeros_like(p)
    # 送電の上限を超える（北海道の価格が下がる）
    hi = E > Mexp_eff
    tgt = Dd + Mexp_eff
    d0 = hi & (Q0 >= tgt)
    deficit[d0] = (Q0 - tgt)[d0]
    curt[d0] = V[d0]
    p[d0] = def_price
    c0 = hi & ~d0 & (Q0 + V >= tgt)
    curt[c0] = (Q0 + V - tgt)[c0]
    p[c0] = FLOOR
    t0 = hi & ~d0 & ~c0
    need = (tgt - Q0 - V)[:, :, None]
    first = np.argmax(cum >= need - 1e-9, 2)
    pb = np.take_along_axis(bs, first[:, :, None], 2)[:, :, 0]
    p[t0] = pb[t0]
    # 受電の上限を超える（北海道の価格が上がる）
    lo = E < -Mimp
    need2 = (Dd - Mimp - Q0 - V)[:, :, None]
    ok = cum[:, :, -1:] >= need2
    first2 = np.argmax(cum >= need2 - 1e-9, 2)
    pb2 = np.take_along_axis(bs, first2[:, :, None], 2)[:, :, 0]
    pb2 = np.where(ok[:, :, 0] & np.isfinite(pb2), pb2, SCARCITY)
    p[lo] = pb2[lo]
    p = np.where(np.isfinite(p), p, SCARCITY)
    return dict(p=p, curt=curt, deficit=deficit, split_hi=lo, split_lo=hi, Q0=Q0, Dd=Dd, bids=bids, caps=caps, on=on, floor=floor)


def unit_output(res, units, I):
    """ユニット別の出力（MW）: 最低出力＋札が価格以下の増分（限界のユニットは按分しない近似）"""
    p = res["p"]
    out = {}
    for k, u in enumerate(units):
        base = np.where(res["on"][:, k][:, None], u[2], 0.0) if not u[5] else 0.0
        inc = np.where(res["bids"][:, :, k] <= p + 1e-9, res["caps"][:, :, k], 0.0)
        out[u[0]] = base + inc
    return out


def _coal_share(r, units_):
    idx = [i for i, u in enumerate(units_) if not u[6] and not u[5] and u[3] < 20]
    return float(r["on"][EVB][:, idx].mean()) if idx else np.nan


def run_case(sc, current=False, def_price=FLOOR, Ks=(0,), opp_cost=False, return_res=False):
    year = 2025 if current else sc["year"]
    I0 = inputs(sc, current)
    Mexp, Mimp = tie_caps(sc or {}, I0["month"], current)
    I0["_Mimp_day"] = Mimp.min(1)
    units, on, floor = commit(I0, year)
    fl = pd.Series(floor, index=DATES_B)
    I = inputs(sc, current, floor_arr=fl)                       # 運転台数に合わせて水力・揚水を計算し直す
    I["_Mimp_day"] = Mimp.min(1)
    chg = np.zeros_like(I["D"])
    dis = np.zeros_like(I["D"])

    def price(chg, dis):
        units_, on_, floor_ = commit(I, year, chg, dis)
        mk = None
        if opp_cost:
            r0 = clear(I, units_, on_, floor_, Mexp, Mimp, chg, dis, def_price)
            mk = np.zeros((I["D"].shape[0], len(units_)))
            for k, u in enumerate(units_):
                if u[5]:
                    continue
                loss = (np.maximum(u[3] - r0["p"], 0.0) * u[2]).sum(1) * 1_000      # 円/日（最低出力での損失）
                mk[:, k] = np.where(on_[:, k], loss / (u[1] * 1_000 * 6.0), 0.0)
        return clear(I, units_, on_, floor_, Mexp, Mimp, chg, dis, def_price, mk), units_

    rows, done, res = [], 0.0, None
    for K in Ks:
        while done < K - 1e-9:
            st = min(1.0, K - done)
            r, _ = price(chg, dis)
            pp = r["p"]
            o = np.argsort(pp, 1)
            c4, d4 = o[:, :4], o[:, -4:]
            mg = np.take_along_axis(pp, d4, 1).sum(1) * ETA - np.take_along_axis(pp, c4, 1).sum(1)
            a = mg > 0
            chg[RB[a], c4[a]] += st * 10.0
            dis[RB[a], d4[a]] += st * 10.0 * ETA
            done += st
        r, units_ = price(chg, dis)
        d = daily_eval(r["p"], W_B)
        rows.append({"K(万kW)": K, "c": annual(d["c"], FYB, EVB), "π_PF": annual(d["pf"], FYB, EVB),
                     "分断（北海道が高い）の割合": r["split_hi"][EVB].mean(), "分断（北海道が低い）の割合": r["split_lo"][EVB].mean(),
                     "負の時間(h/年)": float((r["p"][EVB] < 0).sum() / EVB.sum() * 365),
                     "下限の時間(h/年)": float((np.abs(r["p"][EVB] - FLOOR) < 1e-9).sum() / EVB.sum() * 365),
                     "抑制(MWh/年)": float(r["curt"][EVB].sum() / EVB.sum() * 365), "下げ代不足(h/年)": float((r["deficit"][EVB] > 0).sum() / EVB.sum() * 365),
                     "マストラン以外の石炭の運転日の割合": _coal_share(r, units_)})
        if return_res and K == Ks[0]:
            res = (r, units_, I)
    return pd.DataFrame(rows), res


# ---------------------------------------------------------------- (1) 再現の検証（FY2023〜25、実績の需給、原子力なし）
EV_DAYS = np.asarray(EVB)
ACT = PACTM[BLK]


def fit_stats(p_model, p_th, mask=EV_DAYS):
    pm, pa, pt = p_model[mask], ACT[mask], p_th[mask]
    sa, sm = np.sort(pa, 1), np.sort(pm, 1)
    return {"平均 実績": pa.mean(), "平均 モデル": pm.mean(), "上位4h 実績": sa[:, -4:].mean(), "上位4h モデル": sm[:, -4:].mean(),
            "下位4h 実績": sa[:, :4].mean(), "下位4h モデル": sm[:, :4].mean(),
            "高い時間 実績": (pa > pt + 0.01).mean(), "高い時間 モデル": (pm > pt + 0.01).mean(),
            "低い時間 実績": (pa < pt - 0.01).mean(), "低い時間 モデル": (pm < pt - 0.01).mean(),
            "相関": np.corrcoef(pa.ravel(), pm.ravel())[0, 1], "MAE": np.abs(pa - pm).mean(),
            "R2": 1 - ((pa - pm) ** 2).sum() / ((pa - pa.mean()) ** 2).sum(),
            "値幅の相関": np.corrcoef(sa[:, -4:].mean(1) - sa[:, :4].mean(1), sm[:, -4:].mean(1) - sm[:, :4].mean(1))[0, 1],
            "東北そのままの相関": np.corrcoef(pa.ravel(), pt.ravel())[0, 1]}


if __name__ == "__main__" and os.environ.get("RUN58", "1") == "1":
    VALI, (r0, units0, I0) = run_case(None, current=True, return_res=True)
    st = fit_stats(r0["p"], I0["p_TH"])
    print("[1] 再現の検証（FY2023〜25）")
    print(pd.Series(st).round(3).to_string())
