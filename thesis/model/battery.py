# -*- coding: utf-8 -*-
"""蓄電池の運用と価値、火力の最低限の容量

各年・各場合について、蓄電池の量 K を1万kW ずつ増やす。増やすたびに需給と価格を解き直す。
運用と価値（op）: 先に入っている蓄電池と追加の1kW を同じ規則で扱う（結果のレビュー 2026-10-25）
  - "share"（主）: 各日の最安4時間に充電・最高4時間に放電（完全予見）で価格を作り、価値は完全予見の粗利×実行できる比 s
                   （s＝0.833 は実績の価格で戦略c が完全予見から取る比）
  - "c"（変種）: すべての蓄電池が戦略c（過去28日の平均価格）で充放電の時間を決め、価値も戦略c で測る
  - "mixed"（旧の置き方、比較用）: 完全予見で価格を作り、追加の1kW だけ戦略c で測る
火力: 現状と同じ供給力の余裕を保つ最小の組み合わせ（蓄電池も κ×容量で数える。LTDA の火力は残す。マストランは、mustrun_exit なら
      ほかの火力と同じく燃料費の高い号機から退出し、そうでなければ残す。残っている間はマストランとして動く）
"""
import numpy as np
import pandas as pd

from . import params as PR
from . import balance as B
from . import price as PZ
from . import calibrate as CB
from . import merit as MO

K_GRID = np.array(list(range(0, 101)) + list(range(105, 401, 5)), float)


def keep_minimum(I, units, need, K, mustrun_exit=None, order=None):
    mustrun_exit = PR.MUSTRUN_EXIT if mustrun_exit is None else mustrun_exit
    fixed = [u for u in units if (u[6] and not mustrun_exit) or u[0] in PR.LTDA_UNITS]
    order = PR.EXIT_ORDER if order is None else order          # vc: 燃料費の高い号機から退出（主）、age: 古い号機から退出
    rest = sorted([u for u in units if u not in fixed], key=(lambda u: -u[7]) if order == "age" else (lambda u: u[4]))
    keep = list(fixed)
    net = B.residual(I)
    for u in [None] + rest:
        if u is not None:
            keep.append(u)
        if keep and CB.margin(I, keep, net, K) >= need:                # 火力が1基もない組み合わせは数えない
            return keep, 0.0
    return keep, need - CB.margin(I, keep, net, K)


def required_margin(I, cal):
    """必要な余裕。泊3号が最大機になる年は、苫東厚真4号（700MW）との差を上乗せする"""
    extra = max(PR.NUC["泊3号"] - PR.COMMIT_RESERVE["largest"], 0.0) if I["N"].max() >= PR.NUC["泊3号"] - 1e-6 else 0.0
    return cal["margin0"] + extra


def target_weights(units, year, exclude_mustrun=False):
    """要件の対象の重み。LTDA の火力は0、苫東厚真4号はアンモニア混焼の落札分を除いた比、マストランを除く変種ではマストランも0"""
    w = []
    for u in units:
        if u[0] in PR.LTDA_UNITS or (exclude_mustrun and u[6]):
            w.append(0.0)
        elif u[0] == "苫東厚真4":
            w.append(max(u[2] - PR.ltda_ammonia(year), 0.0) / u[2])
        else:
            w.append(1.0)
    return np.array(w)


def target_cap(units, year, exclude_mustrun=False):
    """要件の対象の火力（MW、送電端）"""
    return float(sum(u[2] * w for u, w in zip(units, target_weights(units, year, exclude_mustrun))))


def evaluate(I, units, chg, dis, cal, mode, cap_after2030, alpha_fixed=None, shape="all", exclude_mustrun=False, receipt_hist=None,
             k=None, losses="outside", recovery="uplift", req_scale=1.0, **_):
    """需給と価格を解く（メリットオーダー＋連系線）。mode: 'spot'（固定費をスポットで回収）または 'capacity'（固定費は契約で回収）。
    shape: 'all'＝燃料費の指標を超える部分に全時間で上乗せ（主）、'hk'＝北海道の電源が価格を決める時間だけ（変種）。
    losses: 'outside'＝運転の赤字は市場の外で補填（主）、'spot'＝運転の赤字もスポットで回収（足元の慣行）。
    recovery: 'uplift'＝全国の火力が同じ比率で上乗せ（東北の価格も上がる。主）、'bid'＝北海道の火力だけが入札に上乗せ（東北の価格が天井）"""
    R = MO.dispatch(I, units, chg, dis, I["link"])
    v = I["v"]
    p0 = R["p0"]
    f = MO.tight(p0, v)
    if shape == "hk":
        f = np.where(R["hk_sets"], f, 0.0)
    w = target_weights(units, I["year"], exclude_mustrun)
    req = CB.spot_requirement_per_kw(cal, I["year"], cap_after2030, receipt_hist, k, req_scale) * target_cap(units, I["year"], exclude_mustrun) * 1_000
    a_sol, gm1, miss, capped, mw1, mw_a = MO.solve_alpha_mw(p0, f, R, w, req)
    contract, info = 0.0, {}
    if losses == "outside":
        if mode == "capacity":
            a, capped, p = 1.0, False, p0
            contract = miss
        elif recovery == "bid":
            p, info = MO.solve_bid(R, w, req, losses_outside=True)
            a, capped = 1.0, False
        else:
            a, capped = (alpha_fixed, False) if alpha_fixed is not None else (a_sol, capped)
            p = MO.price(p0, f, a)
        mw = mw1 if np.array_equal(p, p0) else MO.make_whole(R, p, w)
        target = req
    else:                                                       # 運転の赤字は補填しない。固定費を契約で払う場合も、赤字の分はスポットで回収する
        contract = miss if mode == "capacity" else 0.0
        target = req - contract
        mw = 0.0
        if recovery == "bid":
            p, info = MO.solve_bid(R, w, target, losses_outside=False)
            a, capped = 1.0, False
        else:
            a, capped = (alpha_fixed, False) if alpha_fixed is not None else MO.solve_alpha_gm(p0, f, R, w, target)
            p = MO.price(p0, f, a)
    R["mw1"], R["mw"], R["contract"] = mw1, mw, contract
    R["unrecovered"] = max(req - MO.gm(R, p, w) - mw - contract, 0.0)        # 要件のうち、スポット・補填・契約のどれでも払われない額
    R["bid"] = info
    R["infeasible"] = bool(capped) or R["unrecovered"] > max(1e7, 0.005 * abs(req))  # α が上限、または入札が東北の価格に張り付いても要件に届かない（0.1億円か要件の0.5%を超える分）
    R["req"], R["gm1"], R["missing"], R["alpha_capped"] = req, gm1, miss, capped
    return R, p, a, w


def value(p, days, fy, cal, op):
    """1kW の価値（円/kW-年）。op は運用と価値の置き方"""
    if op == "share":
        return max(cal["capture"] * PZ.annual(PZ.daily_value(p), fy) - PR.W_LOSS, 0.0)
    return max(PZ.annual(PZ.strategy_c(p, days), fy) - PR.W_LOSS, 0.0)


def summarize(I, R, p, a, w, cal, K, op="share"):
    hr = np.arange(24)
    yrs = p.shape[0] / 365.25
    e = lambda x: float(np.asarray(x).sum() / yrs / 1e6)
    fuel = np.array([u[1] for u in R["units"]])
    D = I["D"]
    gm_real = PZ.gm(R, p, w)
    coupled = (np.abs(R["p0"] - R["pT"]) < 0.01) & (R["p0"] > PR.FLOOR + 0.001)   # 北海道が東北と同じ価格（分断していない）
    o = np.argsort(p, 1)
    top, bot = o[:, -4:], o[:, :4]
    pt = np.take_along_axis(p, top, 1)
    ct = np.take_along_axis(coupled, top, 1)
    return {"K(万kW)": K, "α": a, "π(円/kW-年)": value(p, I["days"], I["fy"], cal, op),
            "放電4時間のうち東北と同じ価格の割合": float(ct.mean()),
            "放電の収入のうち分断している時間の割合": float(1.0 - (pt * ct).sum() / max(pt.sum(), 1e-9)),
            "充電4時間のうち0.01円の割合": float((np.take_along_axis(p, bot, 1) <= PR.FLOOR + 0.001).mean()),
            "完全予見の粗利(円/kW-年)": PZ.annual(PZ.daily_value(p), I["fy"]),
            "戦略c の粗利(円/kW-年)": PZ.annual(PZ.strategy_c(p, I["days"]), I["fy"]),
            "平均価格（需要加重）": float((p * D).sum() / D.sum()), "時間平均の価格": float(p.mean()),
            "昼10〜15時": float(p[:, (hr >= 10) & (hr < 15)].mean()), "夕17〜21時": float(p[:, (hr >= 17) & (hr < 21)].mean()),
            "夜0〜6時": float(p[:, hr < 6].mean()), "0.01円の時間(h/年)": float((p <= PR.FLOOR + 0.001).sum() / yrs),
            "抑制の時間(h/年)": float((R["curt"] > 1e-6).sum() / yrs), "北海道が余る時間(h/年)": float(R["surplus"].sum() / yrs), "抑制(TWh)": e(R["curt"]),
            "北海道が価格を決める時間(h/年)": float(R["hk_sets"].sum() / yrs), "東北と同じ価格の時間(h/年)": float((np.abs(R["p0"] - R["pT"]) < 0.01).sum() / yrs),
            "北本 送電(TWh)": e(np.maximum(R["X"], 0.0)), "北本 受電(TWh)": e(np.maximum(-R["X"], 0.0)),
            "抑制率": float(R["curt"].sum() / max((I["S"] + I["W"]).sum(), 1e-9)),
            "需要(TWh)": e(D), "原子力": e(I["N"]), "太陽光（抑制前）": e(I["S"]), "風力（抑制前）": e(I["W"]), "水力": e(I["Hy"]),
            "地熱": e(I["G"]), "バイオマス": e(I["Bm"]), "火力 石炭": e(R["g"][:, :, fuel == "石炭"].sum(2)),
            "火力 LNG": e(R["g"][:, :, fuel == "LNG"].sum(2)), "火力 石油": e(R["g"][:, :, fuel == "石油"].sum(2)),
            "対象外の火力": e(R["other_out"]), "揚水（正味）": e(I["pump"]),
            "北本 送電−受電": e(R["X"]), "北本 増強分": e(R["X_incr"]), "供給力不足(MWh/年)": float(R["short"].sum() / yrs),
            "粗利の要件(億円/年)": R["req"] / 1e8, "α＝1 の粗利(億円/年)": R["gm1"] / 1e8, "不足額 M(億円/年)": R["missing"] / 1e8,
            "運転の赤字の補填 α＝1(億円/年)": R["mw1"] / 1e8, "運転の赤字の補填(億円/年)": R["mw"] / 1e8,
            "うち0.01円の時間の損失(億円/年)": -min(PZ.gm(R, p, w, floor_only=True), 0.0) / 1e8,
            "α が上限": bool(R["alpha_capped"]), "価格が上限の時間(h/年)": float((p >= PR.PRICE_CAP - 1e-6).sum() / yrs),
            "火力の粗利（対象）(億円/年)": gm_real / 1e8, "要件に届かない額(億円/年)": max(R["req"] - gm_real - R["mw"], 0.0) / 1e8,
            "契約で払う額(億円/年)": R.get("contract", 0.0) / 1e8, "回収しきれない額(億円/年)": R.get("unrecovered", 0.0) / 1e8,
            "入札の上乗せ 平均(円/kWh)": R.get("bid", {}).get("markup_avg", np.nan), "入札の上乗せ 年の一律分(円/kWh)": R.get("bid", {}).get("mu", np.nan),
            "入札で上げられる上限(億円/年)": R.get("bid", {}).get("headroom", np.nan) / 1e8 if R.get("bid") else np.nan,
            "入札が東北の価格に張り付き": R.get("bid", {}).get("at_ceiling", np.nan), "要件に届かない（α が上限か入札が天井）": R.get("infeasible", False),
            "収支のずれ(MWh/年)": float(np.abs(R["residual_check"]).sum() / yrs),
            "約定総額(億円/年)": float((p * D).sum() * 1_000 / yrs / 1e8),
            "対象の火力(MW)": target_cap(R["units"], I["year"]), "残す火力": "・".join(u[0] for u in R["units"])}


def _schedule(p, days, op):
    """充放電の4時間。op が 'c' なら戦略c の予測で、それ以外は実際の価格（完全予見）で決める"""
    f = PZ.forecast_c(p, days) if op == "c" else p
    oo = np.argsort(f, 1)
    c4, d4 = oo[:, :4], oo[:, -4:]
    ok = PR.ETA * np.take_along_axis(f, d4, 1).sum(1) - np.take_along_axis(f, c4, 1).sum(1) > 0
    return c4, d4, ok


def run_year(I, cal, mode, cap_price, Ks=K_GRID, adequacy=False, fix_alpha=False, keep_prices=(), op="share", step=1.0, mustrun_keep=None,
             mustrun_exit=None, exit_order=None, **kw):
    """格子の各 K で π(K) と要約を返す。K は step（万kW）ずつ増やし、格子の点で記録する。keep_prices の K では時間別の価格も返す。
    mustrun_keep: マストランとして残すユニットの名前（頑健性。それ以外のマストランは通常の火力として扱い、退出もできる）
    mustrun_exit: マストランも退出できるか（None なら PR.MUSTRUN_EXIT。号機ごと。残っている間はマストランとして動く）
    exit_order: 退出の順番（None なら PR.EXIT_ORDER。vc＝燃料費の高い号機から、age＝古い号機から）"""
    all_units = B.fleet(I["year"])
    if mustrun_keep is not None:
        all_units = [tuple(list(u[:6]) + [bool(u[6]) and u[0] in mustrun_keep] + list(u[7:])) for u in all_units]
    need = required_margin(I, cal)
    nd = I["D"].shape[0]
    chg, dis = np.zeros((nd, 24)), np.zeros((nd, 24))
    rows, prices, a0 = [], {}, None
    rr = np.arange(nd)[:, None]
    grid = sorted(float(k) for k in Ks)
    gi, done = 0, 0.0
    while gi < len(grid):
        units, short = keep_minimum(I, all_units, need, done, mustrun_exit, exit_order) if adequacy else (all_units, 0.0)
        R, p, a, w = evaluate(I, units, chg, dis, cal, mode, cap_price, a0 if fix_alpha else None, **kw)
        if a0 is None:
            a0 = a
        if abs(done - grid[gi]) < 1e-9:
            rows.append({**summarize(I, R, p, a, w, cal, done, op), "足りない供給力(MW)": short})
            if done in keep_prices:
                prices[done] = p.copy()
            gi += 1
            if gi == len(grid):
                break
        st = min(step, grid[gi] - done)
        c4, d4, ok = _schedule(p, I["days"], op)
        chg[rr[ok], c4[ok]] += st * 10.0
        dis[rr[ok], d4[ok]] += st * 10.0 * PR.ETA
        done += st
    return pd.DataFrame(rows), prices
