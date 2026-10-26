# -*- coding: utf-8 -*-
"""較正（FY2024〜25）: 運用のマージン δ、値崩れのしきい値 θ、粗利の換算比 k、蓄電池の価値の比 λ、供給力の余裕、北海道が余る時間のしきい値"""
from functools import lru_cache

import numpy as np

from . import params as PR
from . import data as DT
from . import balance as B
from . import price as PZ
from . import merit as MO


def batt_credit(m, K):
    """蓄電池 K 万kW が、ある日の時間別の余裕 m（MW）の一番低いところを持ち上げられる幅（MW）。
    放電は出力 η×容量・1日 4×η×容量（MWh）までで、余裕の低い時間から順に埋める（水位を上げる形）。κ×容量を上限とする"""
    P = K * 10.0
    if P <= 0:
        return 0.0
    pd_, e = PR.ETA * P, 4.0 * PR.ETA * P
    s = np.sort(m)
    cum = np.cumsum(s)
    lev = s[-1] + e / len(s)
    for j in range(1, len(s) + 1):                            # 下から j 時間を同じ高さにそろえる水位
        L = (e + cum[j - 1]) / j
        if j == len(s) or L <= s[j]:
            lev = L
            break
    return float(min(PR.KAPPA_BATT * P, min(lev, s[0] + pd_) - s[0]))


def kappa_eff(I, Ks):
    """蓄電池 K 万kW の1kW あたりの供給力（κ の実効値）。各年度の上位3日に、4時間分のエネルギーで余裕を持ち上げられる幅÷容量（PR.KAPPA_BATT が上限）。
    余裕の形だけで決まり（火力の構成によらない）、全量に同じ値を当てる（容量市場の調整係数は同じ時間の電源に一律）"""
    net = B.residual(I)
    den = B.tau_den(I, B.fleet(I["year"]))
    tops = []
    for fy in np.unique(I["fy"]):
        r = np.where(I["fy"] == fy)[0]
        tops += list(r[np.argsort(net[r].max(1))[-3:]])
    out = []
    for K in Ks:
        if K <= 0:
            out.append(PR.KAPPA_BATT)
        else:
            out.append(float(np.mean([batt_credit(den[d] - net[d], K) for d in tops])) / (K * 10.0))
    return np.array(out)


def margin(I, units, net=None, K=0.0):
    """供給力の余裕（MW）: 各年度の上位3日の残余需要のピークでの（運転できる火力＋対象外の火力−残余需要）の平均＋蓄電池。
    蓄電池は PR.BATT_CREDIT が "kappa" なら κ×容量（旧）、"energy" なら上位3日それぞれで4時間分のエネルギーで余裕を持ち上げられる幅（κ×容量が上限）"""
    net = B.residual(I) if net is None else net
    den = B.tau_den(I, units)
    energy = getattr(PR, "BATT_CREDIT", "kappa") == "energy"
    out = []
    for fy in np.unique(I["fy"]):
        r = np.where(I["fy"] == fy)[0]
        top = r[np.argsort(net[r].max(1))[-3:]]
        hh = net[top].argmax(1)
        base = den[top, hh] - net[top, hh]
        if energy:
            base = base + np.array([batt_credit(den[d] - net[d], K) for d in top])
        out.append(base.mean())
    return float(np.mean(out)) + (0.0 if energy else PR.KAPPA_BATT * K * 10.0)


@lru_cache(None)
def calibration(delta=0.0):
    est = PZ.estimate()                                       # 旧の価格の式（参考）
    C = DT.calib()
    R = {}
    for fy in PR.CALIB_FY:
        I = MO.inputs_actual(fy)
        R[fy] = (I, MO.dispatch(I, B.fleet(fy)))
    MP = {fy: (r["p0"], I["v"], None) for fy, (I, r) in R.items()}   # 基準の価格（α＝1）
    act_floor = int((C["p"] <= PR.FLOOR + 0.001).sum())
    theta = -np.inf
    # 粗利の換算比 k（過去のユニットだけ、音別GT を除く）
    gm_act = {fy: float((((C["p"] - C["VC"].transpose(2, 0, 1)).transpose(1, 2, 0) * C["G"])[C["fy"] == fy]).sum() * 1_000)
              for fy in PR.CALIB_FY}
    hist_names = [u[0] for u in C["units"]]
    gm_mod = {}
    for fy, (I, r) in R.items():
        target = np.array([u[0] in hist_names for u in r["units"]])
        gm_mod[fy] = PZ.gm(r, MP[fy][0], target)
    k = np.mean(list(gm_mod.values())) / np.mean(list(gm_act.values()))
    cap_hist = sum(u[2] for u in C["units"])
    gm_act_kw = np.mean(list(gm_act.values())) / (cap_hist * 1_000)
    # 蓄電池の価値の比 λ
    v_act = PZ.annual(PZ.strategy_c(C["p"], C["days"]), C["fy"])
    v_mod = np.mean([PZ.strategy_c(MP[fy][0], R[fy][0]["days"]).sum() for fy in PR.CALIB_FY])
    pf_act = PZ.annual(PZ.daily_value(C["p"]), C["fy"])
    lam_est = v_act / v_mod
    lam = 1.0                                                 # 主は1（推定値は感応度。設計レビュー）
    sc_d, pf_d = PZ.strategy_c(C["p"], C["days"]), PZ.daily_value(C["p"])
    capture = float(sc_d[28:].sum() / pf_d[28:].sum())        # 実行できる戦略が完全予見の粗利から取る比（実績の価格、最初の28日を除く）
    # 供給力の余裕（実績の需給、実績の火力）と、北海道が余る時間のしきい値
    marg = np.mean([margin(I, B.fleet(fy)) for fy, (I, r) in R.items()])
    tau_x = float(np.quantile(est["tau"], 0.9))                # 参考（増強分の当て方には使わない）
    # 当てはまりの記録
    pm = np.concatenate([MP[fy][0] for fy in PR.CALIB_FY])
    pa = np.concatenate([C["p"][C["fy"] == fy] for fy in PR.CALIB_FY])
    hr = np.tile(np.arange(24), (pa.shape[0], 1))
    curt_m = {fy: (int((r["curt"] > 1e-6).sum()), float(r["curt"].sum())) for fy, (I, r) in R.items()}
    curt_a = {fy: (int((I["curt_act"] > 0).sum()), float(I["curt_act"].sum())) for fy, (I, r) in R.items()}
    return dict(est=est, delta=delta, theta=theta, k=k, k_year={fy: gm_mod[fy] / gm_act[fy] for fy in PR.CALIB_FY}, capture=capture,
                gm_act=gm_act, gm_mod=gm_mod, gm_act_kw=gm_act_kw, cap_hist=cap_hist,
                lam=lam, lam_est=lam_est, v_act=v_act, v_mod=v_mod, pf_act=pf_act, margin0=marg, tau_x=tau_x, runs=R, model_price=MP,
                fit=dict(r2=1 - ((pa - pm) ** 2).sum() / ((pa - pa.mean()) ** 2).sum(), mae=float(np.abs(pa - pm).mean()),
                         spread_act=float((np.sort(pa, 1)[:, -4:].mean(1) - np.sort(pa, 1)[:, :4].mean(1)).mean()),
                         spread_mod=float((np.sort(pm, 1)[:, -4:].mean(1) - np.sort(pm, 1)[:, :4].mean(1)).mean()),
                         hourly_act=[float(pa[hr == h].mean()) for h in range(24)], hourly_mod=[float(pm[hr == h].mean()) for h in range(24)],
                         floor_act=act_floor / 2, floor_mod=sum(int((p <= PR.FLOOR + 0.001).sum()) for p, v, m in MP.values()) / 2,
                         curt_model=curt_m, curt_actual=curt_a))


def spot_requirement_per_kw(cal, year, cap_after2030=14_972.0, receipt_hist=None, k=None, req_scale=1.0):
    """火力1kW（送電端）あたりのスポットの粗利の要件（モデルの単位、円/kW-年）。
    総収入の要件（FY2024〜25 の実績の粗利＋同期間に実際に受け取った容量収入）−その年に実際に受け取る容量収入。モデルの単位へは比 k で換算。
    容量収入が総収入の要件を超えるときは負（スポットの粗利は負でもよい）。
    req_scale: 総収入の要件に掛ける倍率（頑健性の確認: 足元の収益が、火力に要る最低限の収益より高すぎる・低すぎる場合）"""
    rh = PR.CAP_RECEIPT_HIST if receipt_hist is None else receipt_hist
    total = req_scale * (cal["gm_act_kw"] + rh)
    return (cal["k"] if k is None else k) * (total - PR.thermal_cap_receipt(year, cap_after2030))
