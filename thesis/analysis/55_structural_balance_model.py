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
    """df: 時間別（24の倍数の行、日ごと）。cfg: シナリオの設定。各時間の判定と電源構成を返す"""
    d = df.copy()
    nd = len(d) // 24
    H = lambda col: d[col].to_numpy(float).reshape(nd, 24)
    mon = H("month").astype(int)
    D = H("D")
    S, W = H("S"), H("W")
    U = np.minimum(cfg["U_mw_per_cf"] * H("cf_S"), S) + cfg.get("U_wind", 0.0) * H("cf_W")
    V = S + W - U
    N = H("N")
    Bm, G, Bt, eps = cfg["bio_min"], cfg["geo"], cfg["batt"], cfg["eps"]
    X = cfg["util"] * (np.vectorize(cfg["opcap"].get)(mon) - MARGIN) if cfg.get("X_fixed") is None else np.full(D.shape, cfg["X_fixed"])
    hy_mid = np.vectorize(HY_MID.get)(mon).astype(float) * cfg.get("hy_scale", 1.0)
    hy_day = np.vectorize(cfg["hyd_mon"].get)(mon).astype(float)            # その月の平均の水量
    # 火力の運転台数（日ごと）: 水力の平均の水量と揚水の発電を使っても足りない火力の必要量で決める
    fleet = units_fleet(cfg["year"])
    must = [u for u in fleet if u[5] == 0]
    extra = [u for u in fleet if u[5] > 0]
    req = D - N - hy_day - Bm - G - S - W - cfg.get("import_evening", 0.0)
    req_max = req.max(1) - PUMP_GEN
    floor = np.full(nd, sum(u[2] for u in must) + cfg["nonadj"])
    capon = np.full(nd, sum(u[1] for u in must), float)
    nunits = np.full(nd, len(must))
    for i in range(nd):
        for u in extra:
            if capon[i] >= req_max[i] * (1 + 0.02) + 0:
                break
            capon[i] += u[1]
            nunits[i] += 1
            if not u[3]:                                    # 日中に止められない（石炭・石油）
                floor[i] += u[2]
    T = np.repeat(floor[:, None], 24, 1)
    # 水力: 昼の必須分＋月の水量の残りを火力が床より上の時間に回す
    base = N + T + Bm + G + U + V + eps
    room = np.maximum(0.0, (D + X + Bt) - (base + hy_mid))                 # 火力が床より上にある量（水力の必須分のあと）
    flex = np.maximum(0.0, hy_day * 24 - hy_mid * 24)[:, 0]                 # 日の追加の水量（MWh）
    Hy = hy_mid.copy()
    for i in range(nd):
        f = flex[i]
        if f <= 0:
            continue
        order = np.argsort(-room[i])
        for j in order:
            add = min(f, room[i, j], HY_CAP - Hy[i, j])
            if add <= 0:
                continue
            Hy[i, j] += add
            f -= add
            if f <= 1e-9:
                break
        if f > 1e-9:                                         # 回しきれない水量は全時間に均して必須分になる（放流しない）
            k = np.maximum(0.0, HY_CAP - Hy[i])
            Hy[i] += np.minimum(k, f * k / max(k.sum(), 1e-9))
    # 揚水: 余剰の時間にくみ上げ、同じ日の火力が床より上の時間に発電で返せる量まで
    s0 = base + Hy - (D + X + Bt)                                           # 揚水の前の余剰（>0 は再エネ抑制か下げ代不足）
    room2 = np.maximum(0.0, -s0)
    Pm = np.zeros_like(D)
    for i in range(nd):
        can = min(PUMP_GEN * 24, room2[i].clip(max=PUMP_GEN).sum()) / PUMP_EFF   # 返せる量に見合うくみ上げ量（MWh）
        can = min(can, cfg["pump_res_mwh"])
        pos = np.where(s0[i] > 0)[0]
        for j in pos[np.argsort(-s0[i, pos])]:
            q = min(cfg["pump_mw"], s0[i, j], can)
            Pm[i, j] = q
            can -= q
            if can <= 1e-9:
                break
    s = s0 - Pm
    curt = np.clip(s, 0, V)
    deficit = np.maximum(0.0, s - V)
    out = pd.DataFrame({"ts": d["ts"].to_numpy(), "D": D.ravel(), "N": N.ravel(), "T": T.ravel(), "Hy": Hy.ravel(), "Bm": Bm, "G": G,
                        "S": S.ravel(), "W": W.ravel(), "U": U.ravel(), "X": X.ravel(), "P": Pm.ravel(), "s": s.ravel(),
                        "curt": curt.ravel(), "deficit": deficit.ravel(), "units": np.repeat(nunits, 24)})
    out["regime"] = np.where(out["deficit"] > 0, "下げ代不足", np.where(out["curt"] > 0, "再エネ抑制", "火力が限界"))
    return out


def summarize(out, label, actual=None):
    hrs = (out["curt"] > 0).sum()
    days = out.loc[out["curt"] > 0, "ts"].dt.normalize().nunique()
    r = {"ケース": label, "抑制の時間(h)": hrs, "抑制の日数": days, "抑制量(MWh)": out["curt"].sum(),
         "抑制率(%)": out["curt"].sum() / (out["S"].sum() + out["W"].sum()) * 100,
         "下げ代不足の時間(h)": (out["deficit"] > 0).sum(), "下げ代不足の最大(MW)": out["deficit"].max(),
         "うち昼（9〜15時）の割合": ((out["deficit"] > 0) & out["ts"].dt.hour.between(9, 15)).sum() / max((out["deficit"] > 0).sum(), 1)}
    if actual is not None:
        r.update({"実績 抑制の時間(h)": (actual > 0).sum(), "実績 抑制の日数": out.loc[actual.to_numpy() > 0, "ts"].dt.normalize().nunique(),
                  "実績 抑制量(MWh)": actual.sum(),
                  "時間の一致（両方>0）": int(((out["curt"].to_numpy() > 0) & (actual.to_numpy() > 0)).sum())})
    return r


# ---------------------------------------------------------------- (1) 検証: FY2024・FY2025・FY2026 4〜6月（実績の需要・制御前の VRE）
VAL = []
CUR_CFG = dict(year=2025, U_mw_per_cf=U_FIXED, bio_min=234.0, geo=11.0, batt=60.0, eps=0.0, util=UTIL,
               opcap=OPCAP_EAST["FY2025"], nonadj=65.0, pump_mw=455.0, pump_res_mwh=3_940 / PUMP_EFF * 1.0, hyd_mon=None)
for fy, opk in ((2024, "FY2025"), (2025, "FY2025"), (2026, "FY2026")):
    df = P[P["fy"] == fy].copy()
    df = df.iloc[: len(df) // 24 * 24]
    df["D"], df["S"], df["W"], df["N"] = df["demand"], df["S_pre"], df["W_pre"], df["nuclear"].fillna(0)
    hyd = df.groupby("month")["hydro"].mean().to_dict()
    for lab, over in (("主（活用率55%・ε=0）", {}), ("送電=前日計画の約定（50万kW）", {"X_fixed": 500.0}),
                      ("誤差 ε=35.9万kW", {"eps": 359.0}), ("送電50万kW＋ε", {"X_fixed": 500.0, "eps": 359.0})):
        cfg = {**CUR_CFG, "year": fy, "opcap": OPCAP_EAST[opk], "hyd_mon": hyd, **over}
        out = simulate(df, cfg)
        VAL.append({"年度": fy, **summarize(out, lab, df["curt"].reset_index(drop=True))})
VALD = pd.DataFrame(VAL)
VALD.round(2).to_csv(os.path.join(PROC, "structural_balance_validation.csv"), index=False, encoding="utf-8-sig")
print(VALD.round(1).to_string(index=False))
