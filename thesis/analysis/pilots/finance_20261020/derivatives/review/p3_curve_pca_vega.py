#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""パイロット3: 24時間価格カーブの主成分（水準・形状）と、蓄電池スプレッドオプションの因子別ベガ（北海道）

金利の期間構造の主成分分析（Litterman–Scheinkman 1991: level/slope/curvature）や
電力フォワードカーブの主成分（Koekebakker–Ollmar 2005）と同じ作法を、日内24時間の価格ベクトルに適用する。
  D_{d,h} = p_{d,h} − M_{FY×季節, h}   （年度×季節×時刻の平均プロファイルを除いた偏差）
  D = Σ_k z_{d,k} v_k'                   （主成分: 負荷 v_k、スコア z_k）
因子別ベガ（ノンパラメトリック）: 第k主成分のスコアだけを s 倍した価格
  p^(s) = M + Σ_j (s if j==k else 1)·z_j v_j'
を作り（下限0.01円で打ち切る版／打ち切らない版）、完全予見粗利 PF と固定窓の粗利を再計算する。
  ∂PF/∂s の大きさ ＝ その因子の変動にオプションがどれだけ値を付けるか
風力成分のベガ: 時刻別偏差を風力・太陽光・需要の偏差に回帰して得た時刻別負荷 B_wind(h) で、
  p^(s) = p + (s−1)·B_wind(h)·(W_d − W̄) とし、風力が作る日間変動だけを s 倍する（太陽光も同様）。
出力: このフォルダの p3_*.csv
"""
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

OUT = os.path.dirname(os.path.abspath(__file__))
PANEL = "/Users/matsuba/work/thesis/data/processed/hokkaido_hourly_panel.csv"
ETA, H, FLOOR = 0.85, 4, 0.01
SEASON = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
          3: "不需要期", 4: "不需要期", 5: "不需要期", 6: "不需要期", 10: "不需要期", 11: "不需要期"}
FYS = [2023, 2024, 2025]

hp = pd.read_csv(PANEL, parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)
hp["solar_pre"] = hp["solar"].fillna(0) + hp["solar_curt"].fillna(0)
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
info = pd.DataFrame(index=P.index)
info["fy"] = info.index.year - (info.index.month < 4).astype(int)
info["season"] = info.index.month.map(SEASON)
g = hp.groupby("day")
info["wind"] = g["wind_pre"].sum().reindex(info.index) / 1000
info["solar"] = g["solar_pre"].sum().reindex(info.index) / 1000
info["demand"] = g["demand"].sum().reindex(info.index) / 1000
keep = info["fy"].isin(FYS)
P, info = P[keep], info[keep]


def pf_mean(A):
    s = np.sort(A, axis=1)
    return np.maximum(0, H * (ETA * s[:, -H:].mean(1) - s[:, :H].mean(1))).mean()


def fixed_mean(A, M):
    """各日の平均プロファイル M（年度×季節）の上位/下位4hに固定した窓の粗利（休止なし）"""
    o = np.argsort(M, axis=1)
    dis, chg = o[:, -H:], o[:, :H]
    pd_ = np.take_along_axis(A, dis, 1).mean(1)
    pc_ = np.take_along_axis(A, chg, 1).mean(1)
    return (H * (ETA * pd_ - pc_)).mean()


rows, load_rows, reg_rows, wv_rows = [], [], [], []
for s_name in ["夏", "冬", "不需要期"]:
    idx = info["season"] == s_name
    A = P[idx].to_numpy()
    inf = info[idx]
    grp = inf["fy"].to_numpy()
    M = np.zeros_like(A)
    for fy in FYS:
        M[grp == fy] = A[grp == fy].mean(0)
    D = A - M
    U, S, Vt = np.linalg.svd(D, full_matrices=False)
    Z = D @ Vt.T                     # スコア（日×24）
    ev = S**2 / (S**2).sum()
    for k in range(3):
        v = Vt[k]
        if v.sum() < 0:                # 符号を「全時間が上がる向き」に揃える
            Vt[k], Z[:, k] = -v, -Z[:, k]
            v = Vt[k]
        load_rows.append({"季節": s_name, "PC": k + 1, "寄与率": ev[k],
                          **{f"h{h:02d}": v[h] for h in range(24)}})
        # スコアを風力・太陽光・需要に回帰（年度FE、HC3）
        X = pd.DataFrame({"wind": inf["wind"].values, "solar": inf["solar"].values,
                          "demand": inf["demand"].values}, index=inf.index)
        X = pd.concat([X, pd.get_dummies(inf["fy"], prefix="fy", drop_first=True).astype(float)], axis=1)
        X = sm.add_constant(X)
        m = sm.OLS(Z[:, k], X).fit(cov_type="HC3")
        mfe = sm.OLS(Z[:, k], sm.add_constant(X[["demand"] + [c for c in X.columns if c.startswith("fy")]])).fit()
        reg_rows.append({"季節": s_name, "PC": k + 1,
                         "β_wind(1σ)": m.params["wind"] * inf["wind"].std(), "t_wind": m.tvalues["wind"],
                         "β_solar(1σ)": m.params["solar"] * inf["solar"].std(), "t_solar": m.tvalues["solar"],
                         "R2": m.rsquared, "風力・太陽光の追加R2": m.rsquared - mfe.rsquared,
                         "スコアのsd": Z[:, k].std()})
    base_pf, base_fx = pf_mean(np.maximum(A, FLOOR)), fixed_mean(A, M)
    for k in range(3):
        for sc in [0.0, 0.5, 1.0, 1.5, 2.0]:
            Zs = Z.copy()
            Zs[:, k] *= sc
            Araw = M + Zs @ Vt
            for clip in [True, False]:
                As = np.maximum(Araw, FLOOR) if clip else Araw
                rows.append({"季節": s_name, "PC": k + 1, "倍率s": sc, "下限で打ち切り": clip,
                             "PF": pf_mean(As), "固定窓": fixed_mean(As, M),
                             "PF/基準": pf_mean(As) / base_pf})
    # 純水準（日平均の偏差×平坦ベクトル）と形状（日内偏差）に分けたベガ
    Lv = np.repeat(D.mean(1, keepdims=True), 24, axis=1)
    Sh = D - Lv
    for comp_name, comp in [("純水準", Lv), ("形状", Sh)]:
        for sc in [0.0, 0.5, 1.0, 1.5, 2.0]:
            Araw = A + (sc - 1) * comp
            for clip in [True, False]:
                As = np.maximum(Araw, FLOOR) if clip else Araw
                rows.append({"季節": s_name, "PC": comp_name, "倍率s": sc, "下限で打ち切り": clip,
                             "PF": pf_mean(As), "固定窓": fixed_mean(As, M),
                             "PF/基準": pf_mean(As) / base_pf})
    # 風力・太陽光成分のベガ
    Wd =inf["wind"].to_numpy() - inf.groupby("fy")["wind"].transform("mean").to_numpy()
    Sd = inf["solar"].to_numpy() - inf.groupby("fy")["solar"].transform("mean").to_numpy()
    Dd = inf["demand"].to_numpy() - inf.groupby("fy")["demand"].transform("mean").to_numpy()
    Xh = np.column_stack([Wd, Sd, Dd])
    B, *_ = np.linalg.lstsq(Xh, D, rcond=None)     # 3×24 の時刻別負荷
    load_rows.append({"季節": s_name, "PC": "B_wind(1σ)", "寄与率": np.nan,
                      **{f"h{h:02d}": B[0, h] * Wd.std() for h in range(24)}})
    load_rows.append({"季節": s_name, "PC": "B_solar(1σ)", "寄与率": np.nan,
                      **{f"h{h:02d}": B[1, h] * Sd.std() for h in range(24)}})
    for j, fname in [(0, "風力"), (1, "太陽光")]:
        comp = np.outer(Xh[:, j], B[j])
        for sc in [0.0, 1.0, 2.0, 3.0]:
            As = np.maximum(A + (sc - 1) * comp, FLOOR)
            wv_rows.append({"季節": s_name, "成分": fname, "倍率s": sc, "PF": pf_mean(As),
                            "固定窓": fixed_mean(As, M), "PF/基準": pf_mean(As) / base_pf,
                            "日平均価格のsd": As.mean(1).std()})

vega = pd.DataFrame(rows)
loads = pd.DataFrame(load_rows)
regs = pd.DataFrame(reg_rows)
wv = pd.DataFrame(wv_rows)
vega.to_csv(os.path.join(OUT, "p3_pc_vega.csv"), index=False, encoding="utf-8-sig")
loads.to_csv(os.path.join(OUT, "p3_pc_loadings.csv"), index=False, encoding="utf-8-sig")
regs.to_csv(os.path.join(OUT, "p3_pc_score_regressions.csv"), index=False, encoding="utf-8-sig")
wv.to_csv(os.path.join(OUT, "p3_wind_solar_vega.csv"), index=False, encoding="utf-8-sig")

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print("=== 主成分の寄与率と負荷の形（FY2023-25、年度×季節×時刻の平均を除去）===")
lv = loads[loads["PC"].isin([1, 2, 3])].copy()
hcols = [f"h{h:02d}" for h in range(24)]
lv["負荷min"] = lv[hcols].min(1)
lv["負荷max"] = lv[hcols].max(1)
lv["夕方17-20平均"] = lv[["h17", "h18", "h19", "h20"]].mean(1)
lv["昼10-13平均"] = lv[["h10", "h11", "h12", "h13"]].mean(1)
lv["夜0-5平均"] = lv[["h00", "h01", "h02", "h03", "h04", "h05"]].mean(1)
print(lv[["季節", "PC", "寄与率", "負荷min", "負荷max", "夜0-5平均", "昼10-13平均", "夕方17-20平均"]].round(3).to_string(index=False))
print("\n=== 主成分スコアの回帰（1σ効果、年度FE・HC3）===")
print(regs.round(3).to_string(index=False))
print("\n=== 因子別ベガ: 第k主成分のスコアを s 倍したときの PF（円/kW-日）===")
vt = vega.pivot_table(index=["季節", "PC", "下限で打ち切り"], columns="倍率s", values="PF").round(2)
print(vt.to_string())
print("\n固定窓（事前に固定した窓）")
print(vega.pivot_table(index=["季節", "PC", "下限で打ち切り"], columns="倍率s", values="固定窓").round(2).to_string())
print("\n=== 風力・太陽光が作る日間変動を s 倍したときの PF・固定窓（下限で打ち切り）===")
print(wv.pivot_table(index=["季節", "成分"], columns="倍率s", values=["PF", "固定窓"]).round(2).to_string())
print("\n時刻別負荷（1σ、円/kWh）")
bl = loads[loads["PC"].isin(["B_wind(1σ)", "B_solar(1σ)"])].copy()
bl["夜0-5"] = bl[["h00", "h01", "h02", "h03", "h04", "h05"]].mean(1)
bl["昼10-13"] = bl[["h10", "h11", "h12", "h13"]].mean(1)
bl["夕17-20"] = bl[["h17", "h18", "h19", "h20"]].mean(1)
bl["min"], bl["max"] = bl[hcols].min(1), bl[hcols].max(1)
print(bl[["季節", "PC", "夜0-5", "昼10-13", "夕17-20", "min", "max"]].round(3).to_string(index=False))
