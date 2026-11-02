#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2 のモデル（model/simple.py）の当てはまりの補強（notes/38 §2、2026-11-03 の進捗報告での指導教員の指摘への対応）

1. R² の式の確かめ: R² ＝ 1 − Σ(実績 − 予測)² ÷ Σ(実績 − 実績の平均)²（1時間値、年度ごと）。素朴な予測（北海道＝東北の実績価格）で計算し、
   相関係数の2乗とも並べる
2. 方向別の一致表（FY2024・FY2025）: 各時間を、実績とモデルのそれぞれで 非分断／北海道が安い分断／北海道が高い分断 に分ける。
   分断は |北海道の価格 − 東北の価格| > 0.005円/kWh（実績・モデルとも同じ定義。モデルの東北の価格は実績の入力）。
   モデルは「北本の流れが上限に当たった時間」の定義も並べる。方向別の R² と平均絶対誤差も出す
3. 受電側の上限の倍率 m（北海道向の運用容量900MW×m）を変えたときの、一致表・方向別の分断の時間数・R²・k（粗利の換算比）
4. 推定に使わない期間（FY2023、FY2026 4〜6月）での表5.1 と同じ指標（較正した値は固定）
モデルは上乗せ前（燃料費で入札）、需給は主（マストラン3台、日ごとの起動と通常時の最低出力）。
出力: data/processed/v2_fit_r2_check.csv・v2_fit_confusion.csv・v2_fit_direction.csv・v2_fit_import_cap.csv・v2_fit_oos.csv
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, data as DT, balance as B, merit as MO, price as PZ, simple as SM, calibrate as CB

PROC = os.path.join(ROOT, "data", "processed")
TOL = 0.005                                                    # 分断の判定（円/kWh、表3.2 の注）
CLS = {0: "非分断", 1: "北海道が安い分断", 2: "北海道が高い分断"}
M_GRID = (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)


def r2(a, b):
    return float(1 - ((a - b) ** 2).sum() / ((a - a.mean()) ** 2).sum()) if len(a) > 1 else np.nan


def corr2(a, b):
    return float(np.corrcoef(a, b)[0, 1] ** 2) if len(a) > 1 else np.nan


def split_class(ph, pt):
    d = ph - pt
    return np.where(d < -TOL, 1, np.where(d > TOL, 2, 0))


def inputs(fy, months=None):
    """実績の年度の入力（months: その年度のうち使う月。None なら通年）"""
    I = MO.inputs_actual(fy)
    if months is not None:
        keep = np.isin(I["days"].month, months)
        for k, v in list(I.items()):
            if isinstance(v, np.ndarray) and v.ndim >= 1 and v.shape[0] == len(keep):
                I[k] = v[keep]
        I["days"] = I["days"][keep]
        E, M = I["link"]
        I["link"] = (E[keep] if np.ndim(E) else E, M)
    return I


def run(I, fy, m=1.0):
    """需給を解いて、モデルの価格と北本の流れを返す（m: 受電の上限の倍率）"""
    E, M = I["link"]
    I = {**I, "link": (E, M * m)}
    R = SM.dispatch(I, B.fleet(fy), mode="commit")
    return I, R


def fit_row(I, R, gm_act=None):
    """表5.1 と同じ指標"""
    pa, p = I["p_act"], R["p0"]
    ok = ~np.isnan(pa)
    a, b = pa[ok], p[ok]
    spread = lambda x: float(np.nanmean(np.sort(x, 1)[:, -4:].mean(1) - np.sort(x, 1)[:, :4].mean(1)))
    pt = I["pT"][ok]
    sp = split_class(a, pt) > 0
    C = DT.calib()
    hist = [u[0] for u in C["units"]]
    yrs = 1.0 if I["D"].shape[0] >= 365 else I["D"].shape[0] / 365.25      # 通年は年度の合計（表5.1 と同じ）、一部の月は年あたりに直す
    out = {"時間": int(ok.sum()), "R² 全時間": r2(a, b), "R² 全時間 素朴な予測": r2(a, pt),
           "R² 分断した時間": r2(a[sp], b[sp]), "R² 分断した時間 素朴な予測": r2(a[sp], pt[sp]), "分断した時間(実績)": int(sp.sum()),
           "MAE": float(np.abs(a - b).mean()), "平均 実績": float(a.mean()), "平均 モデル": float(b.mean()),
           "0.01円の時間 実績": int((pa <= PR.FLOOR + 0.001).sum()), "0.01円の時間 モデル": int((p <= PR.FLOOR + 0.001).sum()),
           "日の値幅 実績": spread(pa), "日の値幅 モデル": spread(p),
           "完全予見の粗利 実績(円/kW-年)": float(PZ.daily_value(np.nan_to_num(pa, nan=float(np.nanmean(pa)))).sum() / yrs),
           "完全予見の粗利 モデル(円/kW-年)": float(PZ.daily_value(p).sum() / yrs),
           "抑制(GWh) 実績": float(I["curt_act"].sum() / 1e3), "抑制(GWh) モデル": float(R["curt"].sum() / 1e3),
           "火力の粗利(億円/年) モデル": PZ.gm(R, p, np.array([u[0] in hist for u in R["units"]])) / 1e8}
    if gm_act is not None:
        out["火力の粗利(億円/年) 実績"] = gm_act / 1e8
    return out


def confusion(I, R, label):
    """方向別の一致表（価格差の定義と、モデルは流れが上限に当たった定義も）と方向別の R²・MAE"""
    pa, p, pt = I["p_act"], R["p0"], I["pT"]
    ok = ~np.isnan(pa)
    ca = split_class(pa[ok], pt[ok])
    cm = split_class(p[ok], pt[ok])
    E, M = R["link"] if "link" in R else I["link"]
    E = np.broadcast_to(np.asarray(E, float).reshape(-1) if np.ndim(E) else E, pa.size).reshape(pa.shape)
    X = R["X"]
    cf = np.where((X >= E - 1.0) & (pt > PR.FLOOR + 0.001), 1, np.where(-X >= np.asarray(M) - 1.0, 2, 0))[ok]
    rows = []
    for name, cmod in (("価格差", cm), ("北本の流れが上限", cf)):
        for i in range(3):
            rows.append({**label, "モデルの定義": name, "実績": CLS[i], **{f"モデル {CLS[j]}": int(((ca == i) & (cmod == j)).sum()) for j in range(3)},
                         "実績の時間": int((ca == i).sum())})
    a, b = pa[ok], p[ok]
    Xa = I["X_act"][ok] if "X_act" in I else None
    drows = []
    for i in range(3):
        s = ca == i
        drows.append({**label, "実績の区分": CLS[i], "時間": int(s.sum()), "R²": r2(a[s], b[s]), "R² 素朴な予測": r2(a[s], pt[ok][s]),
                      "相関係数の2乗": corr2(a[s], b[s]), "MAE": float(np.abs(a[s] - b[s]).mean()) if s.any() else np.nan,
                      "MAE 素朴な予測": float(np.abs(a[s] - pt[ok][s]).mean()) if s.any() else np.nan,
                      "平均 実績": float(a[s].mean()) if s.any() else np.nan, "平均 モデル": float(b[s].mean()) if s.any() else np.nan,
                      "モデルが同じ区分(時間)": int((s & (cm == i)).sum()),
                      "北本の受電の中央値 実績(MW)": float(np.median(np.maximum(-Xa[s], 0))) if Xa is not None and s.any() else np.nan,
                      "北本の送電の中央値 実績(MW)": float(np.median(np.maximum(Xa[s], 0))) if Xa is not None and s.any() else np.nan,
                      "北本の受電の中央値 モデル(MW)": float(np.median(np.maximum(-X[ok][s], 0))) if s.any() else np.nan,
                      "北本の送電の中央値 モデル(MW)": float(np.median(np.maximum(X[ok][s], 0))) if s.any() else np.nan})
    s = ca > 0
    drows.append({**label, "実績の区分": "分断した時間（2方向の合計）", "時間": int(s.sum()), "R²": r2(a[s], b[s]), "R² 素朴な予測": r2(a[s], pt[ok][s]),
                  "相関係数の2乗": corr2(a[s], b[s]), "MAE": float(np.abs(a[s] - b[s]).mean()),
                  "MAE 素朴な予測": float(np.abs(a[s] - pt[ok][s]).mean()), "平均 実績": float(a[s].mean()), "平均 モデル": float(b[s].mean()),
                  "モデルが同じ区分(時間)": int((s & (cm == ca)).sum())})
    return rows, drows, ca, cm


def main():
    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    base = CB.calibration(0.0)
    P = DT.panel()

    # 1. R² の式の確かめ（素朴な予測）
    rows = []
    for fy in PR.CALIB_FY:
        Q = P[P["fy"] == fy][["p_hokkaido", "p_tohoku"]].dropna()
        a, b = Q["p_hokkaido"].to_numpy(), Q["p_tohoku"].to_numpy()
        sp = np.abs(a - b) > TOL
        rows.append({"年度": fy, "時間": len(a), "分断した時間": int(sp.sum()), "北海道が安い": int((a - b < -TOL).sum()), "北海道が高い": int((a - b > TOL).sum()),
                     "R² 全時間（1−SSE/SST）": r2(a, b), "R² 分断した時間（1−SSE/SST）": r2(a[sp], b[sp]),
                     "相関係数の2乗 全時間": corr2(a, b), "相関係数の2乗 分断した時間": corr2(a[sp], b[sp])})
    R2 = pd.DataFrame(rows)
    R2.to_csv(os.path.join(PROC, "v2_fit_r2_check.csv"), index=False, encoding="utf-8-sig")
    print(R2.round(3).to_string(index=False))

    # 2・3. 方向別の一致表と、受電の上限の倍率
    conf, dirs, caps = [], [], []
    hist = [u[0] for u in DT.calib()["units"]]
    for m in M_GRID:
        gm_mod = {}
        for fy in PR.CALIB_FY:
            I0 = inputs(fy)
            I0["X_act"] = I0["X"]
            I, R = run(I0, fy, m)
            label = {"受電の上限の倍率": m, "年度": fy}
            c, d, ca, cm = confusion(I, R, label)
            conf += c
            dirs += d
            f = fit_row(I, R, base["gm_act"][fy])
            gm_mod[fy] = PZ.gm(R, R["p0"], np.array([u[0] in hist for u in R["units"]]))
            caps.append({**label, **f, "モデルの分断 安い(時間)": int((cm == 1).sum()), "モデルの分断 高い(時間)": int((cm == 2).sum()),
                         "実績の分断 安い(時間)": int((ca == 1).sum()), "実績の分断 高い(時間)": int((ca == 2).sum()),
                         "区分が一致(%)": float((ca == cm).mean() * 100),
                         "高い分断の一致(時間)": int(((ca == 2) & (cm == 2)).sum()), "安い分断の一致(時間)": int(((ca == 1) & (cm == 1)).sum())})
        k = np.mean(list(gm_mod.values())) / np.mean(list(base["gm_act"].values()))
        for r in caps:
            if r["受電の上限の倍率"] == m:
                r["k"] = float(k)
        print(f"m={m} 済", flush=True)
    CF = pd.DataFrame(conf)
    DR = pd.DataFrame(dirs)
    CP = pd.DataFrame(caps)
    CF.to_csv(os.path.join(PROC, "v2_fit_confusion.csv"), index=False, encoding="utf-8-sig")
    DR.to_csv(os.path.join(PROC, "v2_fit_direction.csv"), index=False, encoding="utf-8-sig")
    CP.to_csv(os.path.join(PROC, "v2_fit_import_cap.csv"), index=False, encoding="utf-8-sig")
    print(CF[CF["受電の上限の倍率"] == 1.0].to_string(index=False))
    print(DR[DR["受電の上限の倍率"] == 1.0].round(3).to_string(index=False))
    print(CP[["受電の上限の倍率", "年度", "R² 全時間", "R² 分断した時間", "MAE", "モデルの分断 安い(時間)", "モデルの分断 高い(時間)",
              "実績の分断 安い(時間)", "実績の分断 高い(時間)", "高い分断の一致(時間)", "安い分断の一致(時間)", "区分が一致(%)", "日の値幅 モデル",
              "完全予見の粗利 モデル(円/kW-年)", "k"]].round(3).to_string(index=False))

    # 4. 推定に使わない期間
    rows = []
    for fy, months, name in ((2023, None, "FY2023"), (2026, (4, 5, 6), "FY2026 4〜6月")):
        I0 = inputs(fy, months)
        I0["X_act"] = I0["X"]
        for m in (1.0,) + tuple(x for x in M_GRID if x in (0.3, 0.5)):
            I, R = run(I0, fy, m)
            c, d, ca, cm = confusion(I, R, {"期間": name, "受電の上限の倍率": m})
            rows.append({"期間": name, "受電の上限の倍率": m, **fit_row(I, R),
                         "モデルの分断 安い(時間)": int((cm == 1).sum()), "モデルの分断 高い(時間)": int((cm == 2).sum()),
                         "実績の分断 安い(時間)": int((ca == 1).sum()), "実績の分断 高い(時間)": int((ca == 2).sum()),
                         "高い分断の一致(時間)": int(((ca == 2) & (cm == 2)).sum()), "安い分断の一致(時間)": int(((ca == 1) & (cm == 1)).sum()),
                         **{f"{r['実績の区分']} R²": r["R²"] for r in d}, **{f"{r['実績の区分']} MAE": r["MAE"] for r in d}})
    OS = pd.DataFrame(rows)
    OS.to_csv(os.path.join(PROC, "v2_fit_oos.csv"), index=False, encoding="utf-8-sig")
    print(OS.round(3).T.to_string())


if __name__ == "__main__":
    main()
