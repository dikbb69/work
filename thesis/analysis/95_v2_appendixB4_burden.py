# -*- coding: utf-8 -*-
"""付録B.4 の後半: 需要家の負担（4.12節、式4.12〜4.14）の2点の検算（2040年、基準シナリオ）

保存した集計（capcost_eval.csv・capcost_variants_主.csv）は比べる相手としてだけ読み、計算には使わない。
各点で、2040年をその点の経路の量で解き直し、時間別の需給・価格・充放電から負担の各項と2つの見方の負担を足し直す。
足し方はこのファイルの中で一から書く（負担を書き出す側の関数は呼ばない）。使うのはモデルの需給と価格の解（SM.run_year）と、
需給の前提（PR.scenario_year・MO.inputs_future）だけ。

点（2040年）:
  A 容量価格14,972円（X＝0）で、量は capcost_paths.csv の A・14,972円の「量 2040」
  B 容量価格14,972円のまま、上乗せの対象の火力にだけ年11,000円/kW を払う。量は B・11,000円の「量 2040」
退出した号機は simple_exit_years.csv の基準（主・上乗せ）の行から読む（基準では退出なし）。CHECK_EXIT=1 なら退出の年も解き直す。

使い方: python analysis/95_v2_appendixB4_burden.py（2点を順に1つのプロセスで解く。並列にしない）
出力: data/processed/v2_appendixB4_burden.csv（項目ごとに 解き直した値・保存した値・差）
"""
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from model import params as PR, merit as MO, simple as SM  # noqa: E402

SCEN = "主"                                    # コードの中の基準シナリオの名前（論文では「基準」）
Y = 2040
BASE_P = 14_972.0                              # 2030年度以降の容量価格（OCCTO メインオークション 2029年度向けの北海道）
SAVED = os.path.join(ROOT, "data", "processed", "simple_capcost", "main")
OUTCSV = os.path.join(ROOT, "data", "processed", "v2_appendixB4_burden.csv")
TOL = 1e-8                                     # 億円/年

# ---- 負担の足し方の前提（4.12節・表A.1。値と出典をここに書き直す）
SOLAR_CUM = {2020: 199.0, 2025: 243.0}         # 太陽光の年度末の累計（万kW）。北電NW 2026-10-06 次世代電力系統WG 第13回 参考資料3-1 p.7
WIND_CUM = {2020: 53.0, 2025: 137.0}           # 風力の年度末の累計（万kW）。同上
SUPPORT_YEARS = 20                             # FIT/FIP の調達期間（10kW 以上）。資源エネルギー庁「買取価格・期間等」
WIND_ONSHORE_2035 = 275.0                      # FY2035 の風力（万kW、OCCTO 2026年度供給計画の取りまとめ p.20）。FY2025 からの増分は陸上（支援あり）
OFFSHORE_SUPPORT = 0.5                         # FY2035 より上の風力（洋上）のうち支援が続く比（表A.1、幅は0〜1）
LTDA_BIO_MW = 199.0 * 0.70                     # LTDA のバイオマス（FIT/FIP ではない、2034年度から、設備利用率0.70）
RETURN = 0.9                                   # LTDA の他市場収益の還付の比（一律、仮定）
FEASIBLE = 0.825                               # 蓄電池の値差の粗利の実行できる比（4.6節）
LTDA_BATT_MW = 37.5 + 24.2 + 16.1              # LTDA の蓄電池（設備、万kW）。2029〜31年度から20年
AMMONIA_MW, TOMATO4_MW = 264.4, 662.0          # 苫東厚真4号のアンモニア混焼（LTDA 落札分、2032年度以降）と号機の容量（MW）
NUC_VC = 1.9                                   # 原子力の燃料費（円/kWh、発電コスト検証WG 2025-02-06 p.131〜132）
Q_CAP_2029 = 529.0                             # 2029年度向けの北海道の H3 需要（万kW、OCCTO 需要曲線 2025-07-31 印字 p.3）
# LTDA の容量（万kW、期待容量の概数）: 泊3号87.2、石狩湾新港2・3 各55.8、アンモニア混焼26.44、蓄電池の落札容量32.5・20.9・14.0、バイオマス19.9
LTDA_KW = {"泊3号": 87.2, "石狩湾新港2": 55.8, "石狩湾新港3": 55.8, "アンモニア混焼": AMMONIA_MW / 10.0,
           "蓄電池（第1回）": 32.5, "蓄電池（第2回）": 20.9, "蓄電池（第3回）": 14.0, "バイオマス": 19.9}
HYDRO = {"流れ込み式": (210.0, 0.4592), "調整池式": (770.0, 1.0), "貯水池式": (280.0, 1.0)}   # 一般水力（MW、容量市場の調整係数）
HYDRO_REQ_KW = 3.5 * 0.547 * 8760              # 一般水力の要件（円/kW-年）。発電コスト検証WG p.31 の中水力
NUC_REQ_KW = 5.3 * 0.70 * 8760                 # 泊の運転を続ける費用（円/kW-年）。同 p.131〜132
NUC_MW = 872.0                                 # 泊3号（送電端の概数）
LTDA_THERMAL = ("石狩湾新港2", "石狩湾新港3")


def oku(x, yrs):
    """MW×円/kWh の時間の和 → 億円/年（気象年の平均）"""
    return float(np.sum(x)) * 1_000.0 / yrs / 1e8


def h3_mw(I):
    """各年度（気象年）の上位3日の日の最大需要の平均を、気象年で平均（MW）"""
    vals = []
    for fy in sorted(set(np.asarray(I["fy"]).tolist())):
        dmax = np.asarray(I["D"])[np.asarray(I["fy"]) == fy].max(axis=1)
        vals.append(np.sort(dmax)[-3:].mean())
    return float(np.mean(vals))


def phi_solar(cap40, cap26):
    """2040年の系統の太陽光のうち支援が続く比: FY2021〜26 に運開した分（FY2027 以降の系統の太陽光の増分は支援なし）"""
    return float(np.clip((min(cap26, cap40) - SOLAR_CUM[Y - SUPPORT_YEARS]) / cap40, 0.0, 1.0))


def phi_wind(cap40, off):
    """2040年の風力のうち支援が続く比: FY2021〜25 の既設、FY2026〜35 の陸上の増分、FY2035 より上（洋上）の off の比"""
    sup = (WIND_CUM[2025] - WIND_CUM[Y - SUPPORT_YEARS]) + max(min(cap40, WIND_ONSHORE_2035) - WIND_CUM[2025], 0.0) \
        + off * max(cap40 - WIND_ONSHORE_2035, 0.0)
    return float(np.clip(sup / cap40, 0.0, 1.0))


def solve_point(lever, X_or_P, K, cal, drop):
    sc = PR.SCENARIOS[SCEN]
    sy = PR.scenario_year(Y, sc)
    I = MO.inputs_future(sy, sc)
    X = X_or_P if lever == "B" else 0.0
    Pcap = X_or_P if lever == "A" else BASE_P               # 容量価格（全電源に払う）
    Preq = Pcap + X                                         # 火力が kW で受け取る額（要件の式4.12）
    t0 = time.time()
    T, _, st = SM.run_year(I, cal, Ks=[K], P_list=(Preq,), p_sched=Preq, drop=drop, return_state=True)
    sec = time.time() - t0
    R, p, chg, dis, info = st["R"], st["p"], st["chg"], st["dis"], st["info"]
    yrs = p.shape[0] / 365.25
    k = cal["k"]
    units = R["units"]
    names = [u[0] for u in units]
    capu = {u[0]: float(u[2]) for u in units}
    g, vc = R["g"], R["vc"]
    gm = lambda n: oku((p - vc[:, :, names.index(n)]) * g[:, :, names.index(n)], yrs) if n in names else 0.0

    # 上乗せの対象の火力（MW）: LTDA を除き、苫東厚真4号はアンモニア混焼の落札分を除く。1年に一度も動かない号機は対象外（退出）
    gen = g.sum((0, 1))
    alive = {n: (gen[j] > 1e-6) or (n in LTDA_THERMAL) for j, n in enumerate(names)}
    w = {n: 0.0 if n in LTDA_THERMAL else ((capu[n] - AMMONIA_MW) / capu[n] if n == "苫東厚真4" else 1.0) for n in names}
    tgt = sum(capu[n] * w[n] for n in names if alive[n])
    # 要件（式4.12、億円/年、モデルの単位）と、最終の価格での対象の火力の粗利（上乗せが要件にちょうど届くか）
    r_bar = cal["gm_act_kw"] + PR.CAP_RECEIPT_HIST         # 足元（FY2024〜25）の火力の総収入（円/kW-年）
    req = k * (r_bar - Preq) * tgt * 1_000 / 1e8
    gm_tgt = sum(w[n] * gm(n) for n in names if alive[n])

    # スポットの支払い（モデルの単位）
    spot = oku(p * I["D"], yrs)
    # FIT/FIP の電源の分。抑制は制御できる太陽光と風力に出力の比で分ける
    s_ctl = np.maximum(I["S"] - I["U"], 0.0)
    den = s_ctl + I["W"]
    cS = np.where(den > 1e-9, R["curt"] * s_ctl / np.where(den > 1e-9, den, 1.0), 0.0)
    pS = oku(p * (I["S"] - cS), yrs)
    pW = oku(p * (I["W"] - (R["curt"] - cS)), yrs)
    pG = oku(p * I["G"], yrs)
    pB = oku(p * np.maximum(I["Bm"] - LTDA_BIO_MW, 0.0), yrs)
    cap40_s, cap40_w = sy["solar_mw"] / 10.0, sy["wind_mw"] / 10.0
    cap26_s = PR.scenario_year(2026, sc)["solar_mw"] / 10.0
    phiS = phi_solar(cap40_s, cap26_s)
    phiW = {off: phi_wind(cap40_w, off) for off in (OFFSHORE_SUPPORT, 0.0, 1.0)}
    Z = phiS * pS + phiW[OFFSHORE_SUPPORT] * pW + pG + pB
    Z_full = pS + pW + pG + pB
    Z_off0 = phiS * pS + phiW[0.0] * pW + pG + pB
    # LTDA の電源のスポットの粗利（還付の対象）
    ltda_th = gm("石狩湾新港2") + gm("石狩湾新港3")
    amm = AMMONIA_MW / TOMATO4_MW * gm("苫東厚真4")
    arb = oku(p * (dis - chg), yrs)                         # 蓄電池全体の値差の収入（完全予見）
    ltda_b = LTDA_BATT_MW / K * arb                         # LTDA の分（全体と同じ動き）
    nuc_m = oku((p - NUC_VC) * I["N"], yrs)
    ret_other = RETURN * (ltda_th + amm + FEASIBLE * ltda_b)
    ret_nuc = RETURN * nuc_m
    # 容量市場: 調達量は H3 需要に比例。払う量＝調達量−LTDA の容量
    I29 = MO.inputs_future(PR.scenario_year(2029, sc), sc)
    q = Q_CAP_2029 * h3_mw(I) / h3_mw(I29)
    ltda_kw = sum(LTDA_KW.values())
    cap_pay = Pcap * max(q - ltda_kw, 0.0) * 1e4 / 1e8
    cap_nonuc = Pcap * max(q - ltda_kw + NUC_MW / 10.0, 0.0) * 1e4 / 1e8
    cap_all = Pcap * q * 1e4 / 1e8
    xpay = X * tgt * 1_000 / 1e8
    # 一般水力と泊3号の要件に届かない分（実際の円）
    hy_m = oku(p * I["Hy"], yrs)
    hy_rev = hy_m + Pcap * sum(mw * kap for mw, kap in HYDRO.values()) * 1_000 / 1e8
    hy_req = HYDRO_REQ_KW * sum(mw for mw, _ in HYDRO.values()) * 1_000 / 1e8
    hy_short = max(hy_req - hy_rev, 0.0)
    nuc_req = NUC_REQ_KW * NUC_MW * 1_000 / 1e8
    nuc_short = max(nuc_req - (nuc_m + Pcap * NUC_MW * 1_000 / 1e8), 0.0)
    # 2つの見方（式4.13・4.14）と6つの感応度
    nat = (spot - Z - ret_other - ret_nuc) / k + cap_pay + xpay + hy_short
    hk = spot / k + cap_pay + xpay
    views = {"主（全国の需要家）": nat, "北海道の需要家の請求だけ": hk,
             "感応度: FIT/FIP をすべて相殺": (spot - Z_full - ret_other - ret_nuc) / k + cap_pay + xpay + hy_short,
             "感応度: 新しい洋上風力も相殺なし": (spot - Z_off0 - ret_other - ret_nuc) / k + cap_pay + xpay + hy_short,
             "感応度: FIT/FIP の相殺なし": (spot - ret_other - ret_nuc) / k + cap_pay + xpay + hy_short,
             "感応度: 泊3号の還付なし": (spot - Z - ret_other) / k + cap_nonuc + xpay + hy_short + nuc_short,
             "感応度: 調達量全体に容量価格": (spot - Z - ret_other - ret_nuc) / k + cap_all + xpay + hy_short,
             "感応度: ÷k をしない": (spot - Z - ret_other - ret_nuc) + cap_pay + xpay + hy_short}
    t = T.iloc[0]
    items = {"上乗せ μ(円/kWh)": float(info["μ"]), "π(円/kW-年)": float(t["π(円/kW-年)"]),
             "平均価格（需要加重）": float((p * I["D"]).sum() / I["D"].sum()),
             "要件(億円/年)": req, "粗利(億円/年)": gm_tgt, "対象の火力(MW)": tgt,
             "需要(TWh)": float(I["D"].sum() / yrs / 1e6),
             "スポットの支払い Σp×需要(億円/年)": spot, "FIT/FIP の電源の分 すべて(億円/年)": Z_full,
             "太陽光の分 Σp×出力(億円/年)": pS, "風力の分 Σp×出力(億円/年)": pW, "地熱の分(億円/年)": pG, "バイオマスの分（LTDA 以外）(億円/年)": pB,
             "φ 太陽光": phiS, "φ 風力": phiW[OFFSHORE_SUPPORT], "φ 風力 洋上0": phiW[0.0], "φ 風力 洋上1": phiW[1.0],
             "LTDA 火力の粗利(億円/年)": ltda_th, "アンモニア混焼分の粗利(億円/年)": amm, "蓄電池全体の値差の収入(億円/年)": arb,
             "LTDA 蓄電池の値差の収入(億円/年)": ltda_b, "原子力の粗利(億円/年)": nuc_m, "一般水力の粗利(億円/年)": hy_m,
             "容量市場の調達量(万kW)": q, "LTDA の容量(万kW)": ltda_kw, "容量市場の支払い 調達量全体(億円/年)": cap_all,
             "容量市場の支払い LTDA を除く(億円/年)": cap_pay, "火力への kW の支払い(億円/年)": xpay,
             "原子力の要件(億円/年)": nuc_req, "一般水力の要件(億円/年)": hy_req, "一般水力の収入(億円/年)": hy_rev,
             "k": k, **views}
    extra = {"秒": sec, "運用の繰り返し(回)": int(t["運用の繰り返し(回)"]), "退出する号機": str(t["退出する号機"]),
             "一般水力の届かない分(億円/年)": hy_short, "泊3号の届かない分(億円/年)": nuc_short,
             "上乗せが上限": bool(info["capped"]), "モデルの要件(億円/年)": float(info["req"] / 1e8), "モデルの対象(MW)": float(info["cap"])}
    return items, extra


def exit_drop():
    X = pd.read_csv(os.path.join(ROOT, "data", "processed", "simple_exit_years.csv"), encoding="utf-8-sig")
    X = X[(X["シナリオ"] == SCEN) & (X["場合"] == "上乗せ") & (X["退出の年"] < Y)]
    return tuple(X["号機"])


def main():
    cal = SM.calibration("commit", None)
    drop = exit_drop()
    if os.environ.get("CHECK_EXIT") == "1":                 # 退出の年を解き直す（15年分、時間がかかる）
        before, when = SM.exit_years(cal, PR.SCENARIOS[SCEN], PR.YEARS, "commit")
        assert tuple(before[Y]) == drop, (before[Y], drop)
        print("退出の年を解き直した:", when or "退出なし", flush=True)
    print("退出した号機（2040年より前）:", drop or "なし", flush=True)
    paths = pd.read_csv(os.path.join(SAVED, "capcost_paths.csv"), encoding="utf-8-sig")
    ev = pd.read_csv(os.path.join(SAVED, "capcost_eval.csv"), encoding="utf-8-sig")
    va = pd.read_csv(os.path.join(SAVED, f"capcost_variants_{SCEN}.csv"), encoding="utf-8-sig")
    pts = [("A", 14_972.0, "A 容量価格14,972円"), ("B", 11_000.0, "B 火力だけに X＝11,000円")]
    rows, res = [], {}
    for lever, v, label in pts:
        K = float(paths[(paths["シナリオ"] == SCEN) & (paths["補い方"] == lever) & (paths["値(円/kW)"] == v)][f"量 {Y}"].iloc[0])
        print(f"{label}: 量 {K:.4f}万kW を解く", flush=True)
        items, extra = solve_point(lever, v, K, cal, drop)
        res[lever] = (items, extra, K)
        sel = lambda D: D[(D["シナリオ"] == SCEN) & (D["補い方"] == lever) & (D["値(円/kW)"] == v) & (D["年"] == Y)].iloc[0]
        e, s = sel(ev), sel(va)
        assert abs(float(e["蓄電池(万kW)"]) - K) < 1e-9
        for name, val in items.items():
            saved = float(e[name]) if name in e.index else (float(s[name]) if name in s.index else np.nan)
            rows.append({"点": label, "補い方": lever, "値(円/kW)": v, "量(万kW)": K, "項目": name, "解き直した値": val, "保存した値": saved,
                         "差": val - saved})
        print({kk: vv for kk, vv in extra.items()}, flush=True)
    # 2つの見方の B−A（表6.5 の2040年の行の元になる差）
    for name in ("主（全国の需要家）", "北海道の需要家の請求だけ"):
        d = res["B"][0][name] - res["A"][0][name]
        sv = float(va[(va["シナリオ"] == SCEN) & (va["補い方"] == "B") & (va["値(円/kW)"] == 11_000.0) & (va["年"] == Y)][name + " 主との差"].iloc[0])
        rows.append({"点": "B−A", "補い方": "B−A", "値(円/kW)": 11_000.0, "量(万kW)": res["B"][2] - res["A"][2], "項目": name + " 主との差",
                     "解き直した値": d, "保存した値": sv, "差": d - sv})
    D = pd.DataFrame(rows)
    D.to_csv(OUTCSV, index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.float_format", lambda x: f"{x:.10g}")
    print(D[["点", "項目", "解き直した値", "保存した値", "差"]].to_string(index=False))
    oku_rows = D[D["項目"].str.contains("億円/年") | D["項目"].str.startswith(("主（", "北海道", "感応度"))]
    for lab, g in oku_rows.groupby("点"):
        print(f"{lab}: 億円/年の項目の差の最大 {g['差'].abs().max():.3e}")
    print("すべての項目の差の最大:", f"{D['差'].abs().max():.3e}", "判定:", "一致" if D["差"].abs().max() < TOL else "不一致")
    print("wrote", OUTCSV)


if __name__ == "__main__":
    main()
