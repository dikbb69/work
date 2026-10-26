#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""【作業中（2026-10-23）: 再現の検証の途中。揚水の上池の日をまたぐ水位、水量の年変動、北本の送出の同時性を改良中（notes/36 §8.7・§8.8）】
北海道エリアの出力抑制時の電源構成を演繹的に導く構造モデル（時間別の需給と火力の運転台数の規則）

目的（著者の方針、notes/36 §8.7・§8.8）:
  出力抑制時の電源構成を、過去の運転実績から帰納するのではなく、設備容量・定検・需要カーブ・運用規則から演繹的に導く。
  時間ごとに「火力が限界の時間」「事業用の再エネを抑制する時間（価格≈0）」「下げ代不足の時間（再エネを全部止めても余る）」
  を判定し、FY2024〜FY2026 の実績の出力制御で再現性を確かめたうえで、FY2030・2035・2040 のシナリオに当てる。

時間 h（MW、送電端相当）の需給:
  必ず出る供給  M(h) = 原子力 N(h) ＋ 火力の床 T(d) ＋ 水力の必須分 Hy(h) ＋ バイオマスの最低 Bm ＋ 地熱 G ＋ 制御できない再エネ U(h)
  制御できる再エネ V(h) = 太陽光 S(h) ＋ 風力 W(h) − U(h)
  吸収できる量  A(h) = 需要 D(h) ＋ 北本の送電 X(h) ＋ 揚水 P(h) ＋ 既存蓄電池 Bt
  余剰 s(h) = M(h) ＋ V(h) ＋ 誤差 ε − A(h)。s≤0: 火力が限界。0<s≤V: 再エネの抑制 s（価格≈0）。s>V: 下げ代不足 s−V。
規則（一次資料。出典は notes/37-structural-model-inputs.md）:
  - 火力の床: マストラン3台（石炭・石油・LNG 各1台、北海道電力ネットワーク 2023-12・OCCTO 2026-07-29「石油・石炭・LNG のマストラン
    3台のみ運転」）の最低出力。2026/5 の出力制御日の前日計画の値（苫東厚真 9.3・知内 4.7・石狩湾新港 24.1〜24.3万kW、計38.2万kW）
    ＋非調整火力（同計画で6.2〜6.5万kW）。夕方・夜の火力の必要量がマストラン3台の最大出力（＋揚水の発電）を超える日は、
    石炭（起動停止に8時間・1日1回で日中に止められない）・石油を段階表の順に追加し、その最低出力が昼の床に加わる。
    LNG コンバインド（石狩湾新港2・3号）は日々の起動停止ができるので、昼の床に加えない。
  - 水力: 昼の必須分は北海道電力の月別昼間想定（2015、晴天日11〜12時、「昼間は可能な限り抑制」）。月の水量（気象年の月平均）の
    残りは、火力が床より上にある時間に回し、回しきれない分は他の時間の必須分になる（夜間の余剰の機構）。
  - バイオマス: 優先給電で再エネより先に抑制される。専焼は50%まで、地域資源は対象外（現状 専焼29×0.5＋地域資源11×0.81＝23.4万kW）。
  - 制御できない再エネ U: 10kW 未満の逆潮分（31.6万kW×0.65）と、被代理（実制御しない）旧ルール・オフライン10〜500kW（22.4万kW）。
  - 北本の送電 X: 活用率×（東北向の運用容量−マージン）。FY2025 の運用容量は4・5月70、6〜11月90、12〜3月70万kW、FY2028 以降100。
    マージン30万kW、活用率55%（2026年度見通し）。感応度として前日計画の約定済み送電（約50万kW）。
  - 揚水: 動力は京極2台の45.5万kW（2026/5 の前日計画）、2035年の公式前提は68万kW。日中の揚水量は、同じ日のうち火力が床より上に
    ある時間に発電で返せる量（発電60万kW、効率0.7）を上限とする（夜間も火力が最低出力なら揚水できないという北海道電力の説明）。
  - 誤差 ε: 前日計画の誤差（35.9万kW）。主は0、感応度で35.9。
検証: 気象年でなく実績の年（FY2024・FY2025・FY2026 4〜6月）の需要・制御前の太陽光・風力を入れ、予測した抑制の時間・日数・量を実績
      （hokkaido_hourly_panel の solar_curt＋wind_curt）と比べる。
出力: data/processed/structural_balance_validation.csv、structural_balance_hourly_{tag}.csv（シナリオ別の時間別の判定と電源構成）
"""
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------- 入力（一次資料の値）
HY_MID = {4: 449, 5: 797, 6: 701, 7: 445, 8: 450, 9: 356, 10: 355, 11: 343, 12: 295, 1: 262, 2: 252, 3: 250}   # MW、北海道電力 2015
HY_CAP = 1_260.0                                          # 一般水力（流込21＋調整池77＋貯水池28万kW、長期見通し）
OPCAP_EAST = {"FY2025": {4: 700, 5: 700, 6: 900, 7: 900, 8: 900, 9: 900, 10: 900, 11: 900, 12: 700, 1: 700, 2: 700, 3: 700},
              "FY2026": {m: 700 for m in range(1, 13)}, "FY2028+": {m: 1_000 for m in range(1, 13)}}
MARGIN, UTIL = 300.0, 0.55
PUMP_GEN, PUMP_EFF = 600.0, 0.7
U_FIXED = 316.0 * 0.65 + 224.0                            # MW（太陽光の設備ベース。×太陽光の CF）


def units_fleet(year):
    """火力のユニット（送電端の概数、最低出力、日中に止められるか）。year は年度"""
    u = [  # 名前, 最大, 最低, DSS 可, 種別, 順位
        ("苫東厚真4（マストラン）", 665, 93, False, "石炭", 0), ("知内2（マストラン）", 333, 47, False, "石油", 0),
        ("石狩湾新港1（マストラン）", 541, 242, False, "LNG", 0),
        ("苫東厚真2", 570, 171, False, "石炭", 1), ("苫東厚真1", 333, 100, False, "石炭", 2)]
    if year <= 2026:
        u += [("砂川3", 119, 52, False, "石炭", 3), ("砂川4", 119, 43, False, "石炭", 4)]
    if year >= 2030:
        u += [("石狩湾新港2", 551, 110, True, "LNG", 5)]
    if year >= 2033:
        u += [("石狩湾新港3", 551, 110, True, "LNG", 6)]
    u += [("知内1", 333, 86, False, "石油", 7)]
    if year <= 2029:
        u += [("苫小牧1", 238, 48, False, "石油", 8)]
    return sorted(u, key=lambda r: r[5])


# ---------------------------------------------------------------- データ
P = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
P = P[P["ts"] >= "2022-04-01"].copy().reset_index(drop=True)
P["S_pre"] = P["solar"] + P["solar_curt"].fillna(0)
P["W_pre"] = P["wind"] + P["wind_curt"].fillna(0)
P["curt"] = P["solar_curt"].fillna(0) + P["wind_curt"].fillna(0)
P["date"], P["hour"], P["month"] = P["ts"].dt.normalize(), P["ts"].dt.hour, P["ts"].dt.month
P["fy"] = P["ts"].dt.year - (P["month"] < 4)
CAP = pd.read_csv(os.path.join(PROC, "area_capacity_series.csv"), parse_dates=["date"])
CAP = CAP[CAP["area"] == "hokkaido"].set_index("date").sort_index()
for col, src in (("cap_S", "solar_kw"), ("cap_W", "wind_kw")):
    s = CAP[src].reindex(CAP.index.union(P["date"].unique())).interpolate("time").ffill()
    P[col] = P["date"].map(s) / 1000.0
P["cf_S"] = (P["S_pre"] / P["cap_S"]).clip(0, 1)
P["cf_W"] = (P["W_pre"] / P["cap_W"]).clip(0, 1)
HYD_MON = P[(P["fy"] >= 2023) & (P["fy"] <= 2025)].groupby("month")["hydro"].mean()     # 気象年の月平均の水量（MW）


def simulate(df, cfg):
    """df: 時間別（24の倍数の行、日ごと、列 ts・month・D・S・W・N・cf_S・cf_W・p_tohoku）。cfg: シナリオの設定。
    各時間の判定と電源構成を返す。揚水の上池の水位は日をまたいで追う（くみ上げは余剰の時間、発電は火力が床より上の時間）"""
    d = df.reset_index(drop=True)
    nd = len(d) // 24
    H = lambda col: d[col].to_numpy(float).reshape(nd, 24)
    mon = H("month").astype(int)
    D, S, W, N = H("D"), H("S"), H("W"), H("N")
    U = np.minimum(cfg["U_cap"] * H("cf_S"), S) + cfg.get("U_wind_cap", 0.0) * H("cf_W")
    V = S + W - U
    Bm, G, Bt, eps = cfg["bio_min"], cfg["geo"], cfg["batt"], cfg["eps"]
    X = cfg["util"] * (np.vectorize(cfg["opcap"].get)(mon) - MARGIN)
    if cfg.get("X_fixed") is not None:
        X = np.full(D.shape, float(cfg["X_fixed"]))
    if cfg.get("X_tohoku_rule"):
        X = np.where(H("p_tohoku") <= 0.011, 0.0, X)
    hy_mid = np.vectorize(cfg["hy_mid"].get)(mon).astype(float)
    hy_day = np.vectorize(cfg["hyd_mon"].get)(mon).astype(float)
    # 火力の運転台数（日ごと）
    fleet = units_fleet(cfg["year"])
    must = [u for u in fleet if u[5] == 0]
    extra = [u for u in fleet if u[5] > 0]
    req_max = (D - N - hy_day - Bm - G - S - W).max(1) - PUMP_GEN
    floor = np.full(nd, sum(u[2] for u in must) + cfg["nonadj"], float)
    if cfg.get("floor_override") is not None:
        floor[:] = cfg["floor_override"]
    capon = np.full(nd, sum(u[1] for u in must), float)
    nunits = np.full(nd, len(must))
    for i in range(nd if cfg.get("floor_override") is None else 0):   # 床を外から与える場合は、追加のユニットを足さない
        for u in extra:
            if capon[i] >= req_max[i] * 1.02:
                break
            capon[i] += u[1]
            nunits[i] += 1
            if not u[3]:
                floor[i] += u[2]
    T = np.repeat(floor[:, None], 24, 1)
    # 水力: 昼の必須分＋月の水量の残りを、火力が床より上の時間に回す。回しきれない分は全時間の必須分になる
    base = N + T + Bm + G + U + V + eps
    room = np.maximum(0.0, (D + X + Bt) - (base + hy_mid))
    flex = np.maximum(0.0, (hy_day - hy_mid) * 24)[:, 0]
    Hy = hy_mid.copy()
    for i in range(nd):
        f = flex[i]
        for j in np.argsort(-room[i]):
            if f <= 1e-9:
                break
            add = min(f, room[i, j], HY_CAP - Hy[i, j])
            if add > 0:
                Hy[i, j] += add
                f -= add
        if f > 1e-9:
            k = np.maximum(0.0, HY_CAP - Hy[i])
            Hy[i] += np.minimum(k, f * k / max(k.sum(), 1e-9))
    # 揚水: 上池の水位（発電換算 MWh）を時間順に追う
    s0 = (base + Hy - (D + X + Bt)).ravel()
    room_f = np.maximum(0.0, -s0)
    cap = cfg["pump_res_mwh"]
    lev = cfg.get("res_init", 0.4) * cap
    Pm, Pg, LV = np.zeros_like(s0), np.zeros_like(s0), np.zeros_like(s0)
    for t in range(len(s0)):
        if s0[t] > 0:
            q = min(cfg["pump_mw"], s0[t], (cap - lev) / PUMP_EFF)
            Pm[t] = max(q, 0.0)
            lev += PUMP_EFF * Pm[t]
        elif room_f[t] > 0 and lev > 0:
            g_ = min(PUMP_GEN, room_f[t], lev)
            Pg[t] = g_
            lev -= g_
        LV[t] = lev
    s = s0 - Pm
    Vr = V.ravel()
    curt = np.clip(s, 0, Vr)
    deficit = np.maximum(0.0, s - Vr)
    out = pd.DataFrame({"ts": d["ts"].to_numpy(), "D": D.ravel(), "N": N.ravel(), "T": T.ravel(), "Hy": Hy.ravel(), "Bm": Bm, "G": G,
                        "S": S.ravel(), "W": W.ravel(), "U": U.ravel(), "X": X.ravel(), "P": Pm, "Pgen": Pg, "res": LV, "s": s,
                        "curt": curt, "deficit": deficit, "units": np.repeat(nunits, 24)})
    out["regime"] = np.where(out["deficit"] > 0, "下げ代不足", np.where(out["curt"] > 0, "再エネ抑制", "火力が限界"))
    return out


def summarize(out, label, actual=None):
    on = out["curt"] > 0
    r = {"ケース": label, "抑制の時間(h)": int(on.sum()), "抑制の日数": out.loc[on, "ts"].dt.normalize().nunique(),
         "抑制量(MWh)": out["curt"].sum(), "抑制率(%)": out["curt"].sum() / (out["S"].sum() + out["W"].sum()) * 100,
         "下げ代不足の時間(h)": int((out["deficit"] > 0).sum()), "下げ代不足の最大(MW)": out["deficit"].max(),
         "下げ代不足のうち昼（9〜15時）": ((out["deficit"] > 0) & out["ts"].dt.hour.between(9, 15)).sum() / max((out["deficit"] > 0).sum(), 1),
         "揚水の平均（余剰の時間, MW）": out.loc[out["s"] + out["P"] > 0, "P"].mean() if (out["s"] + out["P"] > 0).any() else 0.0}
    if actual is not None:
        a = actual.to_numpy() > 0
        md, ad = set(out.loc[on, "ts"].dt.normalize()), set(out.loc[a, "ts"].dt.normalize())
        r.update({"実績 抑制の時間(h)": int(a.sum()), "実績 抑制の日数": len(ad), "実績 抑制量(MWh)": actual.sum(),
                  "実績 抑制率(%)": actual.sum() / (out["S"].sum() + out["W"].sum()) * 100,
                  "日の一致": len(md & ad), "実績の日のうち当たり": len(md & ad) / max(len(ad), 1), "モデルの日のうち当たり": len(md & ad) / max(len(md), 1)})
    return r


def hy_mid_for(hyd_mon):
    """昼の水力の必須分（北海道電力 2015 の月別昼間想定）を、その年の月の水量 ÷ FY2023〜25 の月平均で伸縮する"""
    return {m: v * hyd_mon.get(m, HYD_MON[m]) / HYD_MON[m] for m, v in HY_MID.items()}


def prep_actual(fy):
    df = P[P["fy"] == fy].copy()
    df = df.iloc[: len(df) // 24 * 24].reset_index(drop=True)
    df["D"], df["S"], df["W"], df["N"] = df["demand"], df["S_pre"], df["W_pre"], df["nuclear"].fillna(0)
    return df


# ---------------------------------------------------------------- (1) 検証: FY2024・FY2025・FY2026 4〜6月（実績の需要・制御前の VRE）
CUR_CFG = dict(U_cap=U_FIXED, bio_min=234.0, geo=11.0, batt=60.0, eps=0.0, util=UTIL, nonadj=65.0,
               pump_mw=810.0, pump_res_mwh=3_940.0, res_init=0.4)
VARIANTS = [("主（公式の活用率55%）", {}), ("北本: 東北が下限価格なら送出0", {"X_tohoku_rule": True}),
            ("誤差 ε=35.9万kW", {"eps": 359.0}), ("北本の同時性＋ε", {"X_tohoku_rule": True, "eps": 359.0}),
            ("揚水45.5万kW（前日計画）", {"pump_mw": 455.0})]
VAL = []
for fy, opk in ((2024, "FY2025"), (2025, "FY2025"), (2026, "FY2026")):
    df = prep_actual(fy)
    hyd = df.groupby("month")["hydro"].mean().to_dict()
    for lab, over in VARIANTS:
        cfg = {**CUR_CFG, "year": fy, "opcap": OPCAP_EAST[opk], "hyd_mon": hyd, "hy_mid": hy_mid_for(hyd), **over}
        out = simulate(df, cfg)
        VAL.append({"年度": fy, **summarize(out, lab, df["curt"])})
VALD = pd.DataFrame(VAL)
VALD.round(3).to_csv(os.path.join(PROC, "structural_balance_validation.csv"), index=False, encoding="utf-8-sig")
print("[1] 再現の検証（FY2026 は4〜6月）")
print(VALD[["年度", "ケース", "抑制の時間(h)", "抑制の日数", "抑制量(MWh)", "抑制率(%)", "実績 抑制の時間(h)", "実績 抑制の日数", "実績 抑制量(MWh)",
            "実績 抑制率(%)", "実績の日のうち当たり", "モデルの日のうち当たり", "揚水の平均（余剰の時間, MW）"]].round(2).to_string(index=False))

# 較正: 運用のマージン δ（予測誤差・ランプ・日々の抑制の枠など、モデルにない運用の摩擦の合計）を FY2025 の抑制量に合わせる
MAIN_CFG = {**CUR_CFG, "pump_mw": 455.0, "X_tohoku_rule": True}


def _fy_cfg(fy, df, eps):
    hyd = df.groupby("month")["hydro"].mean().to_dict()
    return {**MAIN_CFG, "year": fy, "opcap": OPCAP_EAST["FY2026" if fy >= 2026 else "FY2025"], "hyd_mon": hyd, "hy_mid": hy_mid_for(hyd), "eps": eps}


_df25 = prep_actual(2025)
_grid = np.arange(0, 401, 5)
_mwh = np.array([simulate(_df25, _fy_cfg(2025, _df25, e))["curt"].sum() for e in _grid])
DELTA = float(np.interp(_df25["curt"].sum(), _mwh, _grid))
CAL = []
for fy in (2024, 2025, 2026):
    df = prep_actual(fy)
    for lab, e in (("δ=0", 0.0), (f"δ={DELTA:.0f}（FY2025 で較正）", DELTA)):
        CAL.append({"年度": fy, **summarize(simulate(df, _fy_cfg(fy, df, e)), lab, df["curt"])})
CALD = pd.DataFrame(CAL)
OFFICIAL_OUTLOOK = {2024: "0.2%（第52回系統WG）", 2025: "0.3%（第6回次世代WG）", 2026: "当初1.23%・更新1.44%（4〜7月実績2.79%）"}
CALD["公式の短期見通し"] = CALD["年度"].map(OFFICIAL_OUTLOOK)
CALD.round(3).to_csv(os.path.join(PROC, "structural_balance_calibration.csv"), index=False, encoding="utf-8-sig")
print(f"\n[2] 運用のマージン δ={DELTA:.1f}MW（FY2025 の抑制量 {_df25['curt'].sum():,.0f}MWh に一致）。主: 北本の同時性・揚水45.5万kW")
print(CALD[["年度", "ケース", "抑制の時間(h)", "抑制の日数", "抑制量(MWh)", "抑制率(%)", "実績 抑制の時間(h)", "実績 抑制の日数", "実績 抑制量(MWh)",
            "実績 抑制率(%)", "公式の短期見通し"]].round(2).to_string(index=False))

# ---------------------------------------------------------------- (3) 将来の年: 気象年 FY2023〜25 に設備・需要を当てる
DC_FLAT = {2025: 0.0, 2030: 2_500.0, 2035: 3_600.0}          # DC・半導体（GWh/年、北海道。2035 は PwC の推計 DC15＋半導体21億kWh）
NUC_UNITS = {"泊3号": 872.0, "泊1号": 554.0, "泊2号": 554.0}  # MW（送電端の概数: 発電端×198/207）


def build_future(fy_w, sc):
    """気象年 fy_w の時間別の形に、シナリオ sc の設備・需要を当てる"""
    df = prep_actual(fy_w).copy()
    e_hist = df["demand"].sum() / 1e3                          # GWh
    e_dc = sc.get("dc_gwh", 0.0)
    k = (sc["demand_gwh"] - e_dc) / e_hist
    df["D"] = df["demand"] * k + e_dc * 1e3 / 8760.0
    # 追加の自家消費（屋根置き）: 発電は全量が需要の減少として現れる（逆潮流する分も出力制御の対象外なので、同じく制御できない）。
    # 屋根置きの出力の形は事業用より低い（過積載率・方位）ので、エリアの CF に0.85を掛ける
    df["D"] = df["D"] - sc.get("selfcons_mw", 0.0) * df["cf_S"] * 0.85
    df["S"] = sc["solar_mw"] * df["cf_S"]
    df["W"] = sc["wind_mw"] * df["cf_W"]
    n = sc["nuclear_mw"]
    if sc.get("nuc_mode") == "85%一定":
        df["N"] = n * 0.85
    elif sc.get("nuc_mode") == "春に1基定検":
        big = max(sc.get("nuc_units", [n]))
        df["N"] = n - np.where(df["month"].isin([4, 5, 6]), big, 0.0)
    else:
        df["N"] = n
    return df


def run_future(sc, label):
    outs = []
    for fy_w in (2023, 2024, 2025):
        df = build_future(fy_w, sc)
        hyd = df.groupby("month")["hydro"].mean().to_dict()
        cfg = {**MAIN_CFG, "year": sc["year"], "opcap": OPCAP_EAST["FY2028+"], "hyd_mon": hyd, "hy_mid": hy_mid_for(hyd), "eps": sc.get("eps", DELTA),
               "U_cap": U_FIXED, "bio_min": sc.get("bio_min", 344.0), "geo": sc.get("geo", 50.0),
               "nonadj": sc.get("nonadj", 65.0), "batt": sc.get("batt", 20.0), "pump_mw": sc.get("pump_mw", 680.0),
               "X_tohoku_rule": sc.get("X_tohoku_rule", True)}
        for k2 in ("floor_override", "X_fixed", "util"):
            if k2 in sc:
                cfg[k2] = sc[k2]
        if sc.get("hvdc_mw"):
            cfg["opcap"] = {m: v + sc["hvdc_mw"] for m, v in cfg["opcap"].items()}
        o = simulate(df, cfg)
        o["気象年"] = fy_w
        outs.append(o)
    o = pd.concat(outs, ignore_index=True)
    r = summarize(o, label)
    r["抑制の時間(h)"] /= 3
    r["下げ代不足の時間(h)"] /= 3
    r["抑制の日数"] /= 3
    r["抑制量(MWh)"] /= 3
    cur = o[o["curt"] > 0]
    dfc = o[o["deficit"] > 0]
    for nm, sub in (("抑制時", cur), ("下げ代不足時", dfc)):
        for col in ("D", "N", "T", "Hy", "U", "S", "W", "X", "P", "curt", "deficit"):
            r[f"{nm} {col}"] = sub[col].mean() if len(sub) else np.nan
    r["太陽光の抑制率(%)"] = np.nan
    return r, o


# 北電NW の2035年シミュレーション（ケース①）の再現: 公式の前提をそのまま入れる
BENCH = dict(year=2035, demand_gwh=33_050.0, dc_gwh=0.0, solar_mw=3_560.0, wind_mw=2_750.0, nuclear_mw=1_680.0, nuc_mode="定格",
             floor_override=610.0, bio_min=410.0, geo=50.0, pump_mw=680.0, X_tohoku_rule=False)
FUT = []
for lab, sc in (("北電NW 2035 ケース①の前提（δ=0、連系線 活用率55%）", {**BENCH, "eps": 0.0}),
                ("同（連系線 57万kW 固定）", {**BENCH, "eps": 0.0, "X_fixed": 570.0}),
                ("同（連系線 87万kW 固定＝公式の8,760時間の中央値）", {**BENCH, "eps": 0.0, "X_fixed": 870.0}),
                ("同（δ 較正値）", {**BENCH})):
    r, _ = run_future(sc, lab)
    FUT.append(r)
FUTD = pd.DataFrame(FUT)
print("\n[3] 北電NW の2035年シミュレーション（ケース①: 制御率30.0%、制御時間3,972h、VRE を全部止めても余る時間415h・最大42万kW）の再現")
print(FUTD[["ケース", "抑制率(%)", "抑制の時間(h)", "下げ代不足の時間(h)", "下げ代不足の最大(MW)", "下げ代不足のうち昼（9〜15時）"]].round(2).to_string(index=False))
FUTD.round(3).to_csv(os.path.join(PROC, "structural_balance_benchmark2035.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------- (4) シナリオ: 公式の2035年の前提（ケース①）を基準に、泊・自家消費・需要・直流連系を動かす
#   基準: 2035年、需要は OCCTO 需要想定（2026年度）の33,106GWh（うち DC・半導体 3,600GWh を一定の負荷）、太陽光356・風力275万kW、
#   火力の床61万kW、バイオマス41万kW、地熱5万kW、揚水68万kW（上池394万kWh）、北本57万kW（公式 p.8）、δ=0。
BASE35 = dict(year=2035, demand_gwh=33_106.0, dc_gwh=3_600.0, solar_mw=3_560.0, wind_mw=2_750.0, floor_override=610.0, bio_min=410.0,
              geo=50.0, pump_mw=680.0, X_fixed=570.0, X_tohoku_rule=False, eps=0.0, nuc_mode="定格")
NUC_SC = {"原子力なし": ([], 0.0), "泊3号": (["泊3号"], 872.0), "泊1・3号": (["泊3号", "泊1号"], 1_426.0), "泊全基": (["泊3号", "泊1号", "泊2号"], 1_980.0)}
SC_ROWS = []
OUTS = {}


def add(label, **kw):
    sc = {**BASE35, **kw}
    units = sc.pop("nuc_key", None)
    if units:
        names, mw = NUC_SC[units]
        sc["nuclear_mw"], sc["nuc_units"] = mw, [NUC_UNITS[n] for n in names] or [0.0]
    r, o = run_future(sc, label)
    r.update({k: v for k, v in kw.items() if k != "nuc_key"})
    r["原子力"] = units
    SC_ROWS.append(r)
    OUTS[label] = o


for nk in NUC_SC:
    for ds in (0, 300, 600, 1_000):
        add(f"2035 {nk} 自家消費+{ds // 10}万kW", nuc_key=nk, selfcons_mw=float(ds))
for nk in ("泊3号", "泊1・3号", "泊全基"):
    add(f"2035 {nk} 85%一定", nuc_key=nk, nuc_mode="85%一定")
    add(f"2035 {nk} 春に1基定検", nuc_key=nk, nuc_mode="春に1基定検")
for nk in ("泊1・3号", "泊全基"):
    add(f"2035 {nk} 直流連系+200万kW", nuc_key=nk, X_fixed=570.0 + 0.55 * 2_000.0)
    add(f"2035 {nk} 需要 高位（ほくでん想定）", nuc_key=nk, demand_gwh=40_300.0, dc_gwh=10_800.0)
    add(f"2035 {nk} 火力の床44.7万kW（現状の前日計画）", nuc_key=nk, floor_override=447.0)
    add(f"2035 {nk} バイオマス50%抑制（34.4万kW）", nuc_key=nk, bio_min=344.0)
# 2040（OCCTO 将来シナリオのエリア配賦、9,000億kWh／11,000億kWh ケース。需要地併設型の太陽光は自家消費の側に入れる）
for lab, kw in (("2040 低位（9,000億kWh）", dict(year=2040, demand_gwh=35_000.0, dc_gwh=4_000.0, solar_mw=2_400.0, wind_mw=3_500.0, selfcons_mw=300.0)),
                ("2040 高位（11,000億kWh）", dict(year=2040, demand_gwh=47_000.0, dc_gwh=8_000.0, solar_mw=2_900.0, wind_mw=7_200.0, selfcons_mw=1_000.0))):
    for nk in ("泊1・3号", "泊全基"):
        add(f"{lab} {nk}", nuc_key=nk, **kw)
        add(f"{lab} {nk} 直流連系+200万kW", nuc_key=nk, X_fixed=570.0 + 0.55 * 2_000.0, **kw)
SCD = pd.DataFrame(SC_ROWS)
SCD.round(3).to_csv(os.path.join(PROC, "structural_balance_scenarios.csv"), index=False, encoding="utf-8-sig")
print("\n[4] シナリオ（3気象年の平均。抑制率は VRE の制御前の発電量に対する比）")
cols = ["ケース", "抑制率(%)", "抑制の時間(h)", "下げ代不足の時間(h)", "下げ代不足の最大(MW)", "下げ代不足のうち昼（9〜15時）",
        "抑制時 N", "抑制時 T", "抑制時 Hy", "抑制時 D", "抑制時 P"]
print(SCD[cols].round(1).to_string(index=False))
