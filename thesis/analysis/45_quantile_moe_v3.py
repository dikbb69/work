#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分位点回帰による風力のメリットオーダー効果（MOE）の期間比較の頑健化（6.3、表6.3a。監査 A6-3-1）

目的:
  6.3 の「τ=0.9 の風力 MOE が −11.2（FY2016〜19）から −4〜−7（FY2023〜25）へ減衰した」は、
  (i) 統制なし（風力・太陽光・需要＋定数）の点推定で、期間差の不確実性を示していない、
  (ii) 年度・季節・時刻を統制していない（期間プールの推定が年度間の価格水準の違いを拾う）、
  という二点で検証されていない。本スクリプトは、時間値の分位点回帰に統制を加え、日単位の移動ブロック・
  ブートストラップで係数と期間差の95%区間を求める。

データ: data/processed/hokkaido_hourly_panel.csv（北海道エリアプライス・需給実績、60分値、FY2016〜25）。
  価格・風力・太陽光・需要のいずれかが欠測の時間を除く（胆振東部地震後の 2018-09-07〜26 の480時間など）。

手法:
  被説明変数 y: (a) 北海道エリアプライス（円/kWh）、(b) 相対価格（その年度の時間平均価格で割った値。年度平均は
    全標本で固定し、ブートストラップでは再推定しない）。
  仕様 fe（主）: 制御前の風力・太陽光（発電実績＋出力制御量）と需要（GW）、季節（夏7〜9月・冬12〜2月・不需要期）×時刻の
    固定効果（各季節の0時を基準とする69本）、月固定効果、年度固定効果、曜日・祝日（37_robust_inference.py の祝日規則、
    年末年始・お盆を含む）。季節の主効果は月固定効果に含まれる。
  仕様 orig（参考、原稿 6.3 の再現）: 発電実績（制御後）の風力・太陽光・需要（GW）＋定数（10_hokkaido_quick_xlsx.py の h7）。
  τ=0.1〜0.9（0.1刻み）。期間: FY2016〜18・FY2019〜22・FY2023〜25（北本連系線の増強 2019年3月の前後）と、
    参考として FY2016〜19（Sakaguchi and Fujii 2021 の期間）。
  推定: 分位点回帰の線形計画を Frisch–Newton 内点法（Portnoy and Koenker 1997。Koenker の lp_fnm の移植）で解く。
    statsmodels の QuantReg（反復重み付き最小二乗）と目的関数値が一致することを全標本で確かめる。
  推論: 日単位の移動ブロック・ブートストラップ（Künsch 1989、ブロック14日、B=499、乱数種固定）。各期間の標本の日を
    並べ、長さ14日のブロックの始点を一様に引いて日を復元抽出し、その日の全時間を使う。同じ複製の中では全分位・両方の y で
    同じ抽出を使う。期間差は期間ごとに独立に抽出した複製の差（重ならない期間の組だけを比べる）。
    区間はパーセンタイル法の95%区間。SE は複製の標準偏差、z は差÷SE。
  判定（監査の仕様）: 円と相対価格の両方で、τ=0.9 の期間差（後の期間−前の期間）の95%区間が0を含まず正であれば「減衰」。
  感応度: (1) 年度別の点推定（orig、fe から年度FE を除いたもの）、(2) 下限張り付き時間（≤0.011円）を除いた点推定
    （被説明変数による標本選択なので、低分位がどれだけ下限に依存するかの目安にとどめる）。
    (3) 部分期間（`--subperiods` で実行。主の実行のあとに走らせる）: fe・両方の y・全分位を、FY2016〜17（胆振東部地震と
    ブラックアウトの FY2018 を除いた増強前）と FY2019〜20（増強後・燃料危機期の前）で推定し、同じ方式のブロック・ブートストラップ
    （B=499、乱数種は主の実行と別）で区間を求める。FY2023〜25 との差は、保存済みの FY2023〜25 の複製（quantile_moe_v3_boot_draws.npz）
    との差で求める（期間ごとに独立な抽出）。主の比較（FY2016〜18 との差）が FY2018 に、FY2019〜22 の値が燃料危機期
    （FY2021〜22）にどれだけ依存するかを確かめるためのもの（検証段階で追加）。

出力:
  data/processed/quantile_moe_v3_coef.csv（期間×分位×仕様×y の係数・ブートストラップ SE・95%区間）
  data/processed/quantile_moe_v3_diff.csv（期間差の点推定・SE・z・95%区間と「減衰」の判定）
  data/processed/quantile_moe_v3_yearly.csv（年度別の点推定）
  data/processed/quantile_moe_v3_floor_excl.csv（下限張り付き時間を除いた点推定）
  data/processed/quantile_moe_v3_subperiod.csv（`--subperiods`: FY2016〜17・FY2019〜20 の係数と FY2023〜25 との差）
  figures/hokkaido/quantile_moe_v3.png（統制付きの係数の分位プロファイルと95%区間、円・相対価格）

限界:
  分位点回帰の係数は条件付き分位への効果で、因果の解釈には制御前出力の外生性を仮定する。気温は統制していない。
  0.01円の下限による左側打ち切りは低分位の係数を0の方向に寄せうる（5.2.4。打ち切り分位点回帰は用いない）。
  ブロック長14日は日次残差の自己相関（ρ1≈0.4〜0.85）に対して短めの可能性があり、区間はやや狭めに出うる。
  相対価格の分母（年度平均）は推定値だが固定して扱う。
"""
import os

os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")    # ワーカーごとに BLAS を1スレッドに（並列は multiprocessing で）
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import logging
import sys
import time
import warnings
from multiprocessing import get_context

import numpy as np
import pandas as pd
import scipy.linalg
import scipy.sparse

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
SEED = 20261021
B = int(os.environ.get("B_QBOOT", "499"))
L_BLOCK = 14
TAUS = [round(0.1 * k, 1) for k in range(1, 10)]
PERIODS = {"FY2016-18": (2016, 2018), "FY2019-22": (2019, 2022), "FY2023-25": (2023, 2025), "FY2016-19": (2016, 2019)}
CONTRASTS = [("FY2019-22", "FY2016-18"), ("FY2023-25", "FY2019-22"), ("FY2023-25", "FY2016-18"), ("FY2023-25", "FY2016-19")]
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "不需要期", 4: "不需要期", 5: "不需要期", 6: "不需要期", 10: "不需要期", 11: "不需要期"}
YS = ["yen", "rel"]
YLAB = {"yen": "価格（円/kWh）", "rel": "相対価格（年度平均＝1）"}
NWORK = int(os.environ.get("N_WORKERS", str(max(1, (os.cpu_count() or 2) - 1))))


# ---------------------------------------------------------------- 分位点回帰（Frisch–Newton 内点法）
def rq_fn(X, y, tau, beta=0.99995, eps=1e-9, max_it=100):
    """min Σ ρ_τ(y − Xb) を双対の線形計画（max y'a s.t. X'a=(1−τ)X'1, 0≤a≤1）で解く。Koenker & Morillo の lp_fnm の移植。
    収束は双対ギャップ ≤ eps×(|主問題の目的|+1)。X はダミー変数が多く疎なので、正規方程式 X'QX は疎行列の積で作る
    （密な X と同じ解）。終盤に正規方程式が悪条件になったら最小二乗で解き直す。"""
    Xd = np.asarray(X, float)
    Xs = scipy.sparse.csr_matrix(Xd)
    Xt = Xs.T.tocsr()
    n, p = Xd.shape
    a = np.full(n, 1.0 - tau)
    bvec = Xt @ a
    c = -y
    x = a.copy()
    u = np.ones(n)
    s = u - x
    yd = scipy.linalg.solve((Xt @ Xs).toarray(), Xt @ c, assume_a="pos")
    r = c - Xs @ yd
    r = r + 0.001 * (r == 0)
    z = np.where(r > 0, r, 0.0)
    w = z - r
    gap = c @ x - yd @ bvec + w @ u
    scale = abs(c @ x) + 1.0
    it = 0

    def bound(v, dv):
        m = dv < 0
        return (-v[m] / dv[m]).min() if m.any() else 1e20

    def solve(q, rhs):
        M = (Xt @ Xs.multiply(q[:, None]).tocsr()).toarray()
        v = Xt @ rhs
        try:
            return scipy.linalg.cho_solve(scipy.linalg.cho_factor(M, check_finite=False), v, check_finite=False)
        except Exception:
            sq = np.sqrt(q)
            return np.linalg.lstsq(Xd * sq[:, None], rhs / sq, rcond=None)[0]

    while gap > eps * scale and it < max_it:
        it += 1
        q = 1.0 / (z / x + w / s)
        r = z - w
        dy = solve(q, q * r)
        dx = q * (Xs @ dy - r)
        ds = -dx
        dz = -z * (dx / x) - z
        dw = -w * (ds / s) - w
        fp = min(beta * min(bound(x, dx), bound(s, ds)), 1.0)
        fd = min(beta * min(bound(w, dw), bound(z, dz)), 1.0)
        if min(fp, fd) < 1:
            mu = z @ x + w @ s
            g = (z + fd * dz) @ (x + fp * dx) + (w + fd * dw) @ (s + fp * ds)
            mu = mu * (g / mu) ** 3 / (2 * n)
            dxdz, dsdw = dx * dz, ds * dw
            xinv, sinv = 1.0 / x, 1.0 / s
            xi = mu * (xinv - sinv)
            dy = solve(q, q * (r + dxdz - dsdw - xi))
            dx = q * (Xs @ dy + xi - r - dxdz + dsdw)
            ds = -dx
            dz = mu * xinv - z - xinv * z * dx - dxdz
            dw = mu * sinv - w - sinv * w * ds - dsdw
            fp = min(beta * min(bound(x, dx), bound(s, ds)), 1.0)
            fd = min(beta * min(bound(w, dw), bound(z, dz)), 1.0)
        x = x + fp * dx
        s = s + fp * ds
        yd = yd + fd * dy
        w = w + fd * dw
        z = z + fd * dz
        gap = c @ x - yd @ bvec + w @ u
    return -yd


def check_obj(X, y, b, tau):
    e = y - X @ b
    return float(np.sum(e * (tau - (e < 0))))


# ---------------------------------------------------------------- データ
def load_calendar():
    """37_robust_inference.py の祝日・曜日ダミー（実行部の前まで）を読み込む"""
    src = open(os.path.join(HERE, "37_robust_inference.py"), encoding="utf-8").read()
    head = src.split("# ================================================================ 実行")[0]
    ns = {"__file__": os.path.join(HERE, "37_robust_inference.py"), "__name__": "lib37"}
    exec(head, ns)
    return ns["calendar_dummies"]


def build_panel():
    hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
    hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)
    reg = hp[(hp["fy"] >= 2016) & (hp["fy"] <= 2025)].dropna(subset=["p_hokkaido", "wind", "solar", "demand"]).copy()
    reg["wind_gw"] = reg["wind"] / 1000
    reg["solar_gw"] = reg["solar"] / 1000
    reg["demand_gw"] = reg["demand"] / 1000
    reg["wind_pre_gw"] = (reg["wind"] + reg["wind_curt"].fillna(0)) / 1000
    reg["solar_pre_gw"] = (reg["solar"] + reg["solar_curt"].fillna(0)) / 1000
    reg["day"] = reg["ts"].dt.normalize()
    reg["hour"] = reg["ts"].dt.hour
    reg["month"] = reg["ts"].dt.month
    reg["season"] = reg["month"].map(SEASON_MAP)
    reg["rel"] = reg["p_hokkaido"] / reg.groupby("fy")["p_hokkaido"].transform("mean")
    reg["yen"] = reg["p_hokkaido"]
    reg["floor"] = reg["p_hokkaido"] <= 0.011
    cal = load_calendar()
    days = pd.DatetimeIndex(sorted(reg["day"].unique()))
    cd = cal(days)
    reg = reg.merge(cd, left_on="day", right_index=True, how="left")
    reg = reg.sort_values("ts").reset_index(drop=True)
    return reg, list(cd.columns)


def design(s, spec, cal_cols, fy_fe=True):
    if spec == "orig":
        X = s[["wind_gw", "solar_gw", "demand_gw"]].set_axis(["wind", "solar", "demand"], axis=1)
    else:
        X = s[["wind_pre_gw", "solar_pre_gw", "demand_gw"]].set_axis(["wind", "solar", "demand"], axis=1)
        hs = (s["season"] + "_" + s["hour"].astype(str)).where(s["hour"] != 0, "base")
        parts = [X, pd.get_dummies(hs, prefix="hs").astype(float).drop(columns="hs_base"),
                 pd.get_dummies(s["month"], prefix="m", drop_first=True).astype(float), s[cal_cols].astype(float)]
        if fy_fe:
            parts.append(pd.get_dummies(s["fy"], prefix="fy", drop_first=True).astype(float))
        X = pd.concat(parts, axis=1)
        X = X.loc[:, X.std() > 0]
    X.insert(0, "const", 1.0)
    return X


# ---------------------------------------------------------------- ブートストラップのワーカー
_G = {}


def _init(data):
    _G.update(data)


def _work(args):
    key, reps = args
    D = _G[key]
    Xn, Y, starts, counts, picks = D["X"], D["Y"], D["starts"], D["counts"], D["picks"]
    out = np.full((len(reps), len(YS), len(TAUS)), np.nan)
    for i, r in enumerate(reps):
        dsel = picks[r]
        ix = np.concatenate([np.arange(starts[k], starts[k] + counts[k]) for k in dsel])
        Xb = Xn[ix]
        keep = Xb.std(axis=0) > 0
        keep[0] = True
        Xb = Xb[:, keep]
        jw = int(np.sum(keep[:2]) - 1)                 # 風力は元の1列目（定数の次）
        for a, yname in enumerate(YS):
            yb = Y[yname][ix]
            for t_, tau in enumerate(TAUS):
                try:
                    out[i, a, t_] = rq_fn(Xb, yb, tau)[jw]
                except Exception:
                    pass
    return key, reps, out


def main():
    t0 = time.time()
    reg, cal_cols = build_panel()
    print(f"時間値の標本: {len(reg):,} 時間（FY2016〜25、{reg['day'].nunique():,} 日）。下限張り付き（≤0.011円）の比率: "
          + ", ".join(f"FY{fy} {100 * g.mean():.2f}%" for fy, g in reg.groupby("fy")["floor"]))
    print(f"ワーカー {NWORK}、B={B}、ブロック {L_BLOCK} 日")

    # ---- 点推定と statsmodels との照合
    data, point = {}, []
    rng_master = np.random.default_rng(SEED)
    for spec in ("fe", "orig"):
        for per, (f0, f1) in PERIODS.items():
            s = reg[(reg["fy"] >= f0) & (reg["fy"] <= f1)].reset_index(drop=True)
            X = design(s, spec, cal_cols)
            assert X.columns[1] == "wind"
            Xn = X.to_numpy(float)
            Y = {y: s[y].to_numpy(float) for y in YS}
            for y in YS:
                for tau in TAUS:
                    b = rq_fn(Xn, Y[y], tau)
                    point.append({"仕様": spec, "y": y, "期間": per, "tau": tau, "係数": b[1], "時間数": len(s),
                                  "日数": s["day"].nunique(), "説明変数の列数": Xn.shape[1]})
            # 日ごとの行の位置（標本は時刻順に並んでいる）
            dcode = pd.factorize(s["day"])[0]
            starts = np.r_[0, np.flatnonzero(np.diff(dcode)) + 1]
            counts = np.diff(np.r_[starts, len(s)])
            nd = len(starts)
            nb = int(np.ceil(nd / L_BLOCK))
            rng = np.random.default_rng([SEED, list(PERIODS).index(per), 0 if spec == "fe" else 1])
            picks = []
            for _ in range(B):
                st = rng.integers(0, nd - L_BLOCK + 1, nb)
                picks.append((st[:, None] + np.arange(L_BLOCK)[None, :]).ravel()[:nd])
            data[(spec, per)] = {"X": Xn, "Y": Y, "starts": starts, "counts": counts, "picks": picks}
            print(f"  {spec} {per}: {len(s):,} 時間・{nd} 日・列 {Xn.shape[1]}  ({time.time() - t0:.0f}s)", flush=True)
    pt = pd.DataFrame(point)

    # statsmodels との照合（目的関数値）
    from statsmodels.regression.quantile_regression import QuantReg
    for spec, per, y, tau in [("fe", "FY2016-18", "yen", 0.9), ("fe", "FY2023-25", "yen", 0.1), ("orig", "FY2016-19", "yen", 0.9)]:
        D = data[(spec, per)]
        bf = rq_fn(D["X"], D["Y"][y], tau)
        bs = QuantReg(D["Y"][y], D["X"]).fit(q=tau, max_iter=5000).params
        print(f"照合 {spec} {per} τ={tau}: 風力 FN {bf[1]:+.4f} / QuantReg {bs[1]:+.4f}、目的関数 FN {check_obj(D['X'], D['Y'][y], bf, tau):.4f}"
              f" / QuantReg {check_obj(D['X'], D['Y'][y], bs, tau):.4f}")

    # ---- ブートストラップ（並列）
    jobs = []
    chunk = 10
    for key in data:
        for r0 in range(0, B, chunk):
            jobs.append((key, list(range(r0, min(B, r0 + chunk)))))
    boot = {key: np.full((B, len(YS), len(TAUS)), np.nan) for key in data}
    ctx = get_context("spawn")
    with ctx.Pool(NWORK, initializer=_init, initargs=(data,)) as pool:
        done = 0
        for key, reps, out in pool.imap_unordered(_work, jobs):
            boot[key][reps] = out
            done += 1
            if done % 40 == 0:
                print(f"  ブートストラップ {done}/{len(jobs)} ジョブ ({time.time() - t0:.0f}s)", flush=True)
    np.savez_compressed(os.path.join(PROC, "quantile_moe_v3_boot_draws.npz"),
                        **{f"{k[0]}__{k[1]}": v for k, v in boot.items()})

    # ---- 係数の区間
    rows = []
    for _, r in pt.iterrows():
        bb = boot[(r["仕様"], r["期間"])][:, YS.index(r["y"]), TAUS.index(r["tau"])]
        bb = bb[np.isfinite(bb)]
        rows.append({**r.to_dict(), "SE_ブロックBS": bb.std(ddof=1), "95%下限": np.percentile(bb, 2.5),
                     "95%上限": np.percentile(bb, 97.5), "有効複製数": len(bb)})
    coef = pd.DataFrame(rows)
    coef["y_説明"] = coef["y"].map(YLAB)
    coef.to_csv(os.path.join(PROC, "quantile_moe_v3_coef.csv"), index=False, encoding="utf-8-sig")

    # ---- 期間差
    drows = []
    for spec in ("fe", "orig"):
        for y in YS:
            for later, earlier in CONTRASTS:
                for tau in TAUS:
                    gl = pt[(pt["仕様"] == spec) & (pt["y"] == y) & (pt["期間"] == later) & (pt["tau"] == tau)]["係数"].iloc[0]
                    ge = pt[(pt["仕様"] == spec) & (pt["y"] == y) & (pt["期間"] == earlier) & (pt["tau"] == tau)]["係数"].iloc[0]
                    dd = (boot[(spec, later)][:, YS.index(y), TAUS.index(tau)]
                          - boot[(spec, earlier)][:, YS.index(y), TAUS.index(tau)])
                    dd = dd[np.isfinite(dd)]
                    diff = gl - ge
                    se = dd.std(ddof=1)
                    lo, hi = np.percentile(dd, [2.5, 97.5])
                    drows.append({"仕様": spec, "y": y, "y_説明": YLAB[y], "比較": f"{later}−{earlier}", "tau": tau,
                                  "後の期間の係数": gl, "前の期間の係数": ge, "差（後−前）": diff, "SE_ブロックBS": se,
                                  "z": diff / se, "95%下限": lo, "95%上限": hi,
                                  "判定": "減衰（差>0、区間が0を含まない）" if lo > 0 else
                                          ("強まる（差<0、区間が0を含まない）" if hi < 0 else "区間が0を含む"),
                                  "有効複製数": len(dd)})
    diff = pd.DataFrame(drows)
    diff.to_csv(os.path.join(PROC, "quantile_moe_v3_diff.csv"), index=False, encoding="utf-8-sig")

    # ---- 年度別の点推定（orig、fe の年度FE なし）
    yrows = []
    for fy in range(2016, 2026):
        s = reg[reg["fy"] == fy].reset_index(drop=True)
        for spec in ("orig", "fe"):
            X = design(s, spec, cal_cols, fy_fe=False).to_numpy(float)
            for y in YS:
                for tau in (0.1, 0.5, 0.9):
                    yrows.append({"年度": f"FY{fy}", "仕様": spec, "y": y, "tau": tau, "係数": rq_fn(X, s[y].to_numpy(float), tau)[1],
                                  "時間数": len(s), "年度平均価格": s["p_hokkaido"].mean(), "風力平均GW（制御前）": s["wind_pre_gw"].mean(),
                                  "下限張り付き比率": s["floor"].mean()})
    yearly = pd.DataFrame(yrows)
    yearly.to_csv(os.path.join(PROC, "quantile_moe_v3_yearly.csv"), index=False, encoding="utf-8-sig")

    # ---- 下限張り付き時間を除いた点推定（fe）
    frows = []
    for per, (f0, f1) in PERIODS.items():
        s = reg[(reg["fy"] >= f0) & (reg["fy"] <= f1) & ~reg["floor"]].reset_index(drop=True)
        X = design(s, "fe", cal_cols).to_numpy(float)
        for y in YS:
            for tau in TAUS:
                base = pt[(pt["仕様"] == "fe") & (pt["y"] == y) & (pt["期間"] == per) & (pt["tau"] == tau)]["係数"].iloc[0]
                frows.append({"期間": per, "y": y, "tau": tau, "係数（下限張り付きを除く）": rq_fn(X, s[y].to_numpy(float), tau)[1],
                              "係数（全時間）": base, "除いた時間数": int(((reg["fy"] >= f0) & (reg["fy"] <= f1) & reg["floor"]).sum()),
                              "時間数": len(s)})
    floor_ex = pd.DataFrame(frows)
    floor_ex.to_csv(os.path.join(PROC, "quantile_moe_v3_floor_excl.csv"), index=False, encoding="utf-8-sig")

    # ---- 表示
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    for spec in ("orig", "fe"):
        for y in YS:
            g = coef[(coef["仕様"] == spec) & (coef["y"] == y)]
            tt = g.assign(v=[f"{b:+.3f} [{lo:+.2f},{hi:+.2f}]" if y == "rel" else f"{b:+.2f} [{lo:+.2f},{hi:+.2f}]"
                             for b, lo, hi in zip(g["係数"], g["95%下限"], g["95%上限"])]) \
                .pivot(index="tau", columns="期間", values="v")[list(PERIODS)]
            print(f"\n=== 係数と95%区間: 仕様 {spec}・{YLAB[y]} ===")
            print(tt.to_string())
            gd = diff[(diff["仕様"] == spec) & (diff["y"] == y)]
            td = gd.assign(v=[f"{d:+.3f} (z={z:+.2f}) [{lo:+.2f},{hi:+.2f}]" for d, z, lo, hi in
                              zip(gd["差（後−前）"], gd["z"], gd["95%下限"], gd["95%上限"])]) \
                .pivot(index="tau", columns="比較", values="v")
            print(f"--- 期間差（後−前）: 仕様 {spec}・{YLAB[y]} ---")
            print(td.to_string())
    print("\n=== 年度別 τ=0.9（円） ===")
    print(yearly[(yearly["y"] == "yen") & (yearly["tau"] == 0.9)].pivot(index="年度", columns="仕様", values="係数").round(2).to_string())
    print("\n=== 下限張り付き時間を除く（fe・円、τ=0.1〜0.3） ===")
    print(floor_ex[(floor_ex["y"] == "yen") & (floor_ex["tau"] <= 0.3)].round(3).to_string(index=False))
    j = diff[(diff["仕様"] == "fe") & (diff["tau"] == 0.9)]
    att = {c: all(j[(j["比較"] == c)]["95%下限"] > 0) for c in j["比較"].unique()}
    print("\n判定（fe・τ=0.9、円と相対価格の両方で区間が0を含まず正か）:", att)

    # ---- 図
    make_figure(coef)
    print(f"\nsaved quantile_moe_v3_coef.csv / _diff.csv / _yearly.csv / _floor_excl.csv / _boot_draws.npz、"
          f"figures/hokkaido/quantile_moe_v3.png（{time.time() - t0:.0f}s）")


def make_figure(coef):
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
        try:
            font_manager.fontManager.addfont(f)
        except Exception:
            pass
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
    INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
    COL = {"FY2016-18": "#2a78d6", "FY2019-22": "#eb6834", "FY2023-25": "#1baf7a"}
    MK = {"FY2016-18": "o", "FY2019-22": "s", "FY2023-25": "^"}   # 白黒でも区別できるマーカー
    LAB = {"FY2016-18": "FY2016〜18（増強前）", "FY2019-22": "FY2019〜22", "FY2023-25": "FY2023〜25"}
    # 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、文字は8.5pt 以上にする。凡例は2つのパネルの下に置く
    fig, axes = plt.subplots(1, 2, figsize=(6.1, 3.5), layout="constrained")
    for ax, y in zip(axes, YS):
        g = coef[(coef["仕様"] == "fe") & (coef["y"] == y)]
        for k, per in enumerate(COL):
            h = g[g["期間"] == per].sort_values("tau")
            xx = h["tau"].to_numpy() + (k - 1) * 0.012
            ax.fill_between(h["tau"], h["95%下限"], h["95%上限"], color=COL[per], alpha=0.13, lw=0)
            ax.plot(xx, h["係数"], color=COL[per], lw=1.4, marker=MK[per], ms=4, markeredgecolor="white", markeredgewidth=0.8,
                    label=LAB[per])
        ax.axhline(0, color=MUTED, lw=1)
        ax.set_xticks([0.1, 0.3, 0.5, 0.7, 0.9])
        ax.set_xlabel("分位 τ", fontsize=9, color=INK)
        ax.set_ylabel("風力の係数（円/kWh per GW）" if y == "yen" else "風力の係数（年度平均価格比 per GW）", fontsize=9, color=INK)
        ax.set_title(f"({'a' if y == 'yen' else 'b'}) {YLAB[y]}", fontsize=9.5, loc="left", color=INK)
        ax.grid(axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=8.5)
    fig.legend(*axes[0].get_legend_handles_labels(), fontsize=8.5, frameon=False, loc="outside lower center", ncol=3)
    # 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
    fig.savefig(os.path.join(FIGDIR, "quantile_moe_v3.png"), dpi=300)
    plt.close(fig)


def subperiods():
    """感応度 (3): FY2016〜17・FY2019〜20 の fe の係数と、FY2023〜25 との差（quantile_moe_v3_subperiod.csv）"""
    t0 = time.time()
    reg, cal_cols = build_panel()
    SUB = {"FY2016-17": (2016, 2017), "FY2019-20": (2019, 2020)}
    draws = np.load(os.path.join(PROC, "quantile_moe_v3_boot_draws.npz"))["fe__FY2023-25"]     # B×y×τ（主の実行の複製）
    coef_main = pd.read_csv(os.path.join(PROC, "quantile_moe_v3_coef.csv"))
    ref = coef_main[(coef_main["仕様"] == "fe") & (coef_main["期間"] == "FY2023-25")].set_index(["y", "tau"])["係数"]
    data, point = {}, {}
    for i, (per, (f0, f1)) in enumerate(SUB.items()):
        s = reg[(reg["fy"] >= f0) & (reg["fy"] <= f1)].reset_index(drop=True)
        X = design(s, "fe", cal_cols)
        assert X.columns[1] == "wind"
        Xn = X.to_numpy(float)
        Y = {y: s[y].to_numpy(float) for y in YS}
        for y in YS:
            for tau in TAUS:
                point[(per, y, tau)] = rq_fn(Xn, Y[y], tau)[1]
        dcode = pd.factorize(s["day"])[0]
        starts = np.r_[0, np.flatnonzero(np.diff(dcode)) + 1]
        counts = np.diff(np.r_[starts, len(s)])
        nd = len(starts)
        nb = int(np.ceil(nd / L_BLOCK))
        rng = np.random.default_rng([SEED, 100 + i, 0])
        picks = [(st[:, None] + np.arange(L_BLOCK)[None, :]).ravel()[:nd] for st in
                 (rng.integers(0, nd - L_BLOCK + 1, nb) for _ in range(B))]
        data[("fe", per)] = {"X": Xn, "Y": Y, "starts": starts, "counts": counts, "picks": picks}
        print(f"  {per}: {len(s):,} 時間・{nd} 日・列 {Xn.shape[1]}", flush=True)
    jobs = [(key, list(range(r0, min(B, r0 + 10)))) for key in data for r0 in range(0, B, 10)]
    boot = {key: np.full((B, len(YS), len(TAUS)), np.nan) for key in data}
    with get_context("spawn").Pool(NWORK, initializer=_init, initargs=(data,)) as pool:
        for key, reps, out in pool.imap_unordered(_work, jobs):
            boot[key][reps] = out
    rows = []
    for per in SUB:
        for a, y in enumerate(YS):
            for t_, tau in enumerate(TAUS):
                bb = boot[("fe", per)][:, a, t_]
                ok = np.isfinite(bb)
                dd = draws[:B, a, t_][ok] - bb[ok]
                b0, r0 = point[(per, y, tau)], float(ref.loc[(y, tau)])
                lo, hi = np.percentile(dd, [2.5, 97.5])
                se = dd.std(ddof=1)
                rows.append({"仕様": "fe", "y": y, "y_説明": YLAB[y], "期間": per, "tau": tau, "係数": b0,
                             "SE_ブロックBS": bb[ok].std(ddof=1), "95%下限": np.percentile(bb[ok], 2.5),
                             "95%上限": np.percentile(bb[ok], 97.5), "有効複製数": int(ok.sum()),
                             "FY2023-25 の係数": r0, "差（FY2023-25−期間）": r0 - b0, "差のSE": se, "差のz": (r0 - b0) / se,
                             "差の95%下限": lo, "差の95%上限": hi,
                             "判定": "減衰（差>0、区間が0を含まない）" if lo > 0 else
                                     ("強まる（差<0、区間が0を含まない）" if hi < 0 else "区間が0を含む")})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(PROC, "quantile_moe_v3_subperiod.csv"), index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250)
    print(out[["y", "期間", "tau", "係数", "95%下限", "95%上限", "差（FY2023-25−期間）", "差のz", "差の95%下限", "差の95%上限", "判定",
               "有効複製数"]].round(3).to_string(index=False))
    print(f"saved quantile_moe_v3_subperiod.csv（{time.time() - t0:.0f}s）")


if __name__ == "__main__":
    if "--subperiods" in sys.argv:
        subperiods()
    else:
        main()
