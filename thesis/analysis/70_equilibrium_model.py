#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北海道の蓄電池の均衡モデル（作り直し、2026-10-25。結果のレビューを反映）の実行。設計は notes/43-rebuild-design.md、部品は model/

1. 較正と当てはまり（FY2024〜25）
2. 検証: 需給の収支、出力制御（量を主な指標）、値崩れの時間の火力、ユニット別の発電量。運転台数は較正の目標として別に示す
3. 推定に使っていない年（FY2023、FY2026 4〜6月）。0.01円の時間は「東北も0.01円」と「北海道だけ0.01円」に分ける
4. 北電NW の2035年の公式シミュレーションとの照合（主の前提と、公式の前提）
5. 誘導形の推定との整合の確認: 過去データの回帰（同じ FY2024〜25 と FY2019〜25）と構造モデルの短期の反応（α＝1）。原子力と日内の値幅
6. 将来（2026〜2040）: シナリオ×価格の作り方で π(K) と年の需給・価格。主の経路では変種も計算。並列で計算する
7. 参入の均衡: 容量価格・資本費・LTDA・調整係数・需給調整市場の上乗せ。目標の量に要る容量価格
出力: data/processed/eqm_*.csv・eqm_pik.npz
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, data as DT, balance as B, price as PZ, calibrate as CB, battery as BT, entry as EN, merit as MO

PROC = os.environ.get("EQM_PROC") or os.path.join(ROOT, "data", "processed")   # EQM_PROC で出力先を変えられる（試し用）
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
QUICK = os.environ.get("QUICK") == "1"
WORKERS = int(os.environ.get("WORKERS", "9"))
# 2030年度以降の容量価格の格子（スポット回収では α と π も変わる）。固定費の不足が0になる容量価格（約16,500〜17,800円）で π が折れるので、
# その近くは1,000円おきにする（結果の確認で、粗い格子の直線の補間がスポット回収の要る容量価格を低く出していた）
P_SCEN = [0.0, 10_000.0, 12_500.0, 14_972.0, 16_000.0, 17_000.0, 18_000.0, 19_000.0, 20_000.0, 20_911.0, 25_000.0]
P_MAIN = sorted(P_SCEN + [5_000.0])
BASE_P = 14_972.0
MODES = {"spot": "スポット回収", "capacity": "容量回収"}
VARIANTS = {  # 主の経路だけで計算する変種。mode と run_year への引数
    "spot_fixα": ("spot", dict(fix_alpha=True)),
    "spot_北海道だけ上乗せ": ("spot", dict(shape="hk")),
    "spot_マストラン除く": ("spot", dict(exclude_mustrun=True)),
    "spot_容量収入9690": ("spot", dict(receipt_hist=PR.CAP_PRICE_HIST)),
    "spot_k2024": ("spot", dict(k_year=2024)),
    "spot_k2025": ("spot", dict(k_year=2025)),
    "spot_旧の運用": ("spot", dict(op="mixed")),
    "capacity_旧の運用": ("capacity", dict(op="mixed")),
    "spot_本州+3円": ("spot", dict(pT_shift=3.0)),
    "capacity_本州+3円": ("capacity", dict(pT_shift=3.0)),
    "spot_本州−3円": ("spot", dict(pT_shift=-3.0)),
    "capacity_本州−3円": ("capacity", dict(pT_shift=-3.0)),
    "spot_通常時の最低出力なし": ("spot", dict(no_normal_min=True)),
    "capacity_通常時の最低出力なし": ("capacity", dict(no_normal_min=True)),
    # 2×2（運転の赤字をどこで払うか × 固定費をどこで払うか）の残りのマス。スポットで回収するマスは、
    # 全国の火力が同じ比率で上乗せする場合（東北の価格も上がる。主）と、北海道の火力だけが入札に上乗せする場合（東北の価格が天井。頑健性）の2つで示す。
    # どちらが π や価格を高く出すかは、年・量・マスで入れ替わる（上限・下限の関係ではない）
    "spot_入札": ("spot", dict(recovery="bid")),
    "all_spot": ("spot", dict(losses="spot")),
    "all_spot_入札": ("spot", dict(losses="spot", recovery="bid")),
    "capacity_赤字はスポット": ("capacity", dict(losses="spot")),
    "capacity_赤字はスポット_入札": ("capacity", dict(losses="spot", recovery="bid")),
    # 頑健性: 火力の要件（足元の総収入）を上下にずらす（足元の収益が、火力に要る最低限の収益より高すぎる・低すぎる場合）
    "spot_要件0.8": ("spot", dict(req_scale=0.8)),
    "spot_要件1.2": ("spot", dict(req_scale=1.2)),
    "all_spot_要件0.8": ("spot", dict(losses="spot", req_scale=0.8)),
    "all_spot_要件1.2": ("spot", dict(losses="spot", req_scale=1.2)),
    "capacity_赤字はスポット_要件0.8": ("capacity", dict(losses="spot", req_scale=0.8)),
    "capacity_赤字はスポット_要件1.2": ("capacity", dict(losses="spot", req_scale=1.2)),
    # 頑健性: 火力の退出（今の供給力の余裕を保つのに要らない火力は退出する。蓄電池は κ×容量で数える。マストランと LTDA の火力は残す）
    "spot_退出あり": ("spot", dict(adequacy=True)),
    "capacity_退出あり": ("capacity", dict(adequacy=True)),
    "all_spot_退出あり": ("spot", dict(losses="spot", adequacy=True)),
    "capacity_赤字はスポット_退出あり": ("capacity", dict(losses="spot", adequacy=True)),
    "spot_入札_退出あり": ("spot", dict(recovery="bid", adequacy=True)),
    "all_spot_入札_退出あり": ("spot", dict(losses="spot", recovery="bid", adequacy=True)),
    "capacity_赤字はスポット_入札_退出あり": ("capacity", dict(losses="spot", recovery="bid", adequacy=True)),
    # 頑健性（主の前提＝退出あり）: 容量回収（基準）と、すべてスポット（全国の上乗せ）で各仮定をずらす
    "capacity_退出あり_本州+3円": ("capacity", dict(adequacy=True, pT_shift=3.0)),
    "capacity_退出あり_本州−3円": ("capacity", dict(adequacy=True, pT_shift=-3.0)),
    "all_spot_退出あり_本州+3円": ("spot", dict(losses="spot", adequacy=True, pT_shift=3.0)),
    "all_spot_退出あり_本州−3円": ("spot", dict(losses="spot", adequacy=True, pT_shift=-3.0)),
    "all_spot_退出あり_要件0.8": ("spot", dict(losses="spot", adequacy=True, req_scale=0.8)),
    "all_spot_退出あり_要件1.2": ("spot", dict(losses="spot", adequacy=True, req_scale=1.2)),
    "capacity_退出あり_最低出力なし": ("capacity", dict(adequacy=True, no_normal_min=True)),
    "all_spot_退出あり_最低出力なし": ("spot", dict(losses="spot", adequacy=True, no_normal_min=True)),
    "capacity_退出あり_マストラン2台": ("capacity", dict(adequacy=True, mustrun_keep=("石狩湾新港1", "苫東厚真4"))),
    "all_spot_退出あり_マストラン2台": ("spot", dict(losses="spot", adequacy=True, mustrun_keep=("石狩湾新港1", "苫東厚真4"))),
    "capacity_退出あり_燃料+20%": ("capacity", dict(adequacy=True, fuel_scale=1.2)),
    "capacity_退出あり_燃料−20%": ("capacity", dict(adequacy=True, fuel_scale=0.8)),
    "all_spot_退出あり_燃料+20%": ("spot", dict(losses="spot", adequacy=True, fuel_scale=1.2)),
    "all_spot_退出あり_燃料−20%": ("spot", dict(losses="spot", adequacy=True, fuel_scale=0.8)),
    # 頑健性（主の前提の中身、2026-10-26）: 主はマストランも燃料費の高い号機から退出。マストランは残す版と、古い号機から退出する版
    "capacity_退出あり_マストランは残す": ("capacity", dict(adequacy=True, mustrun_exit=False)),
    "all_spot_退出あり_マストランは残す": ("spot", dict(losses="spot", adequacy=True, mustrun_exit=False)),
    "capacity_赤字はスポット_退出あり_マストランは残す": ("capacity", dict(losses="spot", adequacy=True, mustrun_exit=False)),
    "capacity_退出あり_古い順": ("capacity", dict(adequacy=True, exit_order="age")),
    "all_spot_退出あり_古い順": ("spot", dict(losses="spot", adequacy=True, exit_order="age")),
    "capacity_赤字はスポット_退出あり_古い順": ("capacity", dict(losses="spot", adequacy=True, exit_order="age")),
}
ROBUST_V = [k for k in VARIANTS if "_退出あり_" in k and "マストラン2台" not in k]   # マストラン2台は、マストランも退出できる主の前提では意味がない
CELLS = ["spot", "spot_入札", "capacity", "all_spot", "all_spot_入札", "capacity_赤字はスポット", "capacity_赤字はスポット_入札",
         "spot_退出あり", "capacity_退出あり", "all_spot_退出あり", "capacity_赤字はスポット_退出あり",
         "spot_入札_退出あり", "all_spot_入札_退出あり", "capacity_赤字はスポット_入札_退出あり"]   # 2×2 のマス（退出ありは主の前提、2026-10-26 著者の決定）
VLAB = {"spot": "スポット回収", "capacity": "容量回収", "spot_fixα": "スポット回収（α を蓄電池なしの値に固定）",
        "spot_北海道だけ上乗せ": "スポット回収（北海道の電源が価格を決める時間だけ上乗せ）", "spot_マストラン除く": "スポット回収（マストランの固定費は契約で回収）",
        "spot_容量収入9690": "スポット回収（過去の容量収入を約定価格の平均9,690円）",
        "spot_k2024": "スポット回収（粗利の換算比 k を FY2024 の値）", "spot_k2025": "スポット回収（粗利の換算比 k を FY2025 の値）",
        "spot_旧の運用": "スポット回収（追加の1kW だけ戦略c で測る旧の置き方）", "capacity_旧の運用": "容量回収（追加の1kW だけ戦略c で測る旧の置き方）",
        "spot_本州+3円": "スポット回収（東北の価格 +3円）", "capacity_本州+3円": "容量回収（東北の価格 +3円）",
        "spot_本州−3円": "スポット回収（東北の価格 −3円）", "capacity_本州−3円": "容量回収（東北の価格 −3円）",
        "spot_通常時の最低出力なし": "スポット回収（通常時の最低出力なし）", "capacity_通常時の最低出力なし": "容量回収（通常時の最低出力なし）",
        "spot_入札": "スポット回収（北海道の火力だけが入札で回収、東北の価格が天井）",
        "all_spot": "すべてスポット（運転の赤字も上乗せで回収）",
        "all_spot_入札": "すべてスポット（運転の赤字も北海道の火力の入札で回収、東北の価格が天井）",
        "capacity_赤字はスポット": "容量回収（運転の赤字は上乗せで回収）",
        "capacity_赤字はスポット_入札": "容量回収（運転の赤字は北海道の火力の入札で回収、東北の価格が天井）",
        "spot_要件0.8": "スポット回収（火力の要件×0.8）", "spot_要件1.2": "スポット回収（火力の要件×1.2）",
        "all_spot_要件0.8": "すべてスポット（火力の要件×0.8）", "all_spot_要件1.2": "すべてスポット（火力の要件×1.2）",
        "capacity_赤字はスポット_要件0.8": "容量回収（運転の赤字は上乗せで回収、火力の要件×0.8）",
        "capacity_赤字はスポット_要件1.2": "容量回収（運転の赤字は上乗せで回収、火力の要件×1.2）",
        "spot_退出あり": "スポット回収（要らない火力は退出）", "capacity_退出あり": "容量回収（要らない火力は退出）",
        "all_spot_退出あり": "すべてスポット（要らない火力は退出）", "capacity_赤字はスポット_退出あり": "容量回収（運転の赤字は上乗せで回収、要らない火力は退出）",
        "spot_入札_退出あり": "スポット回収（北海道の火力だけが入札で回収、要らない火力は退出）",
        "all_spot_入札_退出あり": "すべてスポット（北海道の火力だけが入札で回収、要らない火力は退出）",
        "capacity_赤字はスポット_入札_退出あり": "容量回収（運転の赤字は北海道の火力の入札で回収、要らない火力は退出）"}


PR_CAPTURE = 0.825                                              # 主の実行できる比（較正の値。calibrate の capture と同じ）
ENTRY_OV = [dict(wacc=0.04), dict(wacc=0.08), dict(life=15), dict(existing=45.0), dict(sratio=0.70), dict(kappa_const=0.861)]   # 参入の計算だけで変えられる前提（頑健性）


def ov_label(ov):
    if not ov:
        return ""
    return "・".join({"wacc": lambda v: f"割引率{v:.0%}", "life": lambda v: f"寿命{v:.0f}年", "existing": lambda v: f"既設{v:.0f}万kW",
                     "sratio": lambda v: f"実行できる比{v:.2f}", "kappa_const": lambda v: f"κ一定{v:.3f}"}[k](v) for k, v in ov.items())


_RLAB = {"本州+3円": "東北の価格 +3円", "本州−3円": "東北の価格 −3円", "要件0.8": "火力の要件×0.8", "要件1.2": "火力の要件×1.2",
         "最低出力なし": "通常時の最低出力なし", "マストラン2台": "マストラン2台", "燃料+20%": "燃料費+20%", "燃料−20%": "燃料費−20%",
         "マストランは残す": "マストランは残す", "古い順": "古い号機から退出"}
for _k in [k for k in VARIANTS if "_退出あり_" in k]:
    _base, _sfx = _k.split("_退出あり_")
    VLAB[_k] = {"capacity": "容量回収", "all_spot": "すべてスポット", "capacity_赤字はスポット": "容量回収（運転の赤字は上乗せで回収）"}[_base] + f"（要らない火力は退出、{_RLAB[_sfx]}）"


def p_grid_needed(mode, kw):
    """容量価格で π が変わるか。固定費を契約で払い、運転の赤字も補填する場合（α＝1）だけは変わらない"""
    return not (mode == "capacity" and kw.get("losses", "outside") == "outside")


def out(df, name):
    df.to_csv(os.path.join(PROC, name), index=False, encoding="utf-8-sig")


def add_energy_cols(S):
    """蓄電池が避けた抑制の量と、減った火力の発電量（同じシナリオ・場合・容量価格・年の、蓄電池なしとの差。TWh/年）"""
    S = S.copy()
    th = S["火力 石炭"] + S["火力 LNG"] + S["火力 石油"] + S["対象外の火力"]
    S["火力の発電量 合計(TWh)"] = th
    key = ["シナリオ", "変種キー", "2030年度以降の容量価格", "年"]
    b = S[S["K(万kW)"] == 0.0].set_index(key)
    idx = pd.MultiIndex.from_frame(S[key])
    S["蓄電池が避けた抑制(TWh)"] = b["抑制(TWh)"].reindex(idx).to_numpy() - S["抑制(TWh)"].to_numpy()
    S["減った火力の発電量(TWh)"] = b["火力の発電量 合計(TWh)"].reindex(idx).to_numpy() - th.to_numpy()
    return S


def model_price_actual(cal, fy):
    I = MO.inputs_actual(fy)
    R = MO.dispatch(I, B.fleet(fy))
    return I, R, R["p0"]


def stats(pa, pm, I, R):
    ok = ~np.isnan(pa)
    a, b = pa[ok], pm[ok]
    sa = (np.sort(pa, 1)[:, -4:].mean(1) - np.sort(pa, 1)[:, :4].mean(1))
    sb = (np.sort(pm, 1)[:, -4:].mean(1) - np.sort(pm, 1)[:, :4].mean(1))
    fa, fb = pa <= PR.FLOOR + 0.001, pm <= PR.FLOOR + 0.001
    th = I["nat_floor"]
    hk_a, hk_m = fa & ~th, R["surplus"] & ~th                   # 北海道だけ0.01円（実績）、モデルが北海道の余剰と判定（東北は0.01円でない）
    return {"R²": 1 - ((a - b) ** 2).sum() / ((a - a.mean()) ** 2).sum(), "相関（水準のずれを除く）": float(np.corrcoef(a, b)[0, 1]),
            "MAE": float(np.abs(a - b).mean()), "偏り": float((b - a).mean()),
            "値幅 実績": float(np.nanmean(sa)), "値幅 モデル": float(np.nanmean(sb)), "値幅の相関": float(pd.Series(sa).corr(pd.Series(sb))),
            "0.01円の時間 実績": int(fa.sum()), "0.01円の時間 モデル": int(fb.sum()),
            "うち東北も0.01円 実績": int((fa & th).sum()), "うち北海道だけ0.01円 実績": int(hk_a.sum()),
            "北海道だけ 再現率": float((hk_a & hk_m).sum() / max(hk_a.sum(), 1)), "北海道だけ 適合率": float((hk_a & hk_m).sum() / max(hk_m.sum(), 1)),
            "まとめた当たり率（東北の実績価格を入力にした値）": float((fa & fb).sum() / max(fa.sum(), 1)),
            "まとめた空振り率": float((fb & ~fa).sum() / max(fb.sum(), 1)),
            "東北と同じ価格の時間 実績": float(np.mean(np.abs(a - I["pT"][ok]) < 0.01)), "東北と同じ価格の時間 モデル": float(np.mean(np.abs(b - I["pT"][ok]) < 0.01)),
            "北本の流れ 平均 実績": float(I["X"].mean()), "北本の流れ 平均 モデル": float(R["X"].mean()),
            "北本の流れ 昼 実績": float(I["X"][:, 10:15].mean()), "北本の流れ 昼 モデル": float(R["X"][:, 10:15].mean()),
            "北本の流れ 夕 実績": float(I["X"][:, 17:21].mean()), "北本の流れ 夕 モデル": float(R["X"][:, 17:21].mean()),
            "北本の流れの相関": float(np.corrcoef(I["X"].ravel(), R["X"].ravel())[0, 1]),
            **naive_bench(pa, pm, I)}


def naive_bench(pa, pm, I):
    """比較の基準: 「北海道の価格＝東北の価格（実績）」。全時間と、2つの価格が違う時間（切り離された時間）に分けて比べる"""
    ok = ~np.isnan(pa)
    a, b, n = pa[ok], pm[ok], I["pT"][ok]
    dec = np.abs(a - n) > 0.01
    r2 = lambda x, y: float(1 - ((x - y) ** 2).sum() / ((x - x.mean()) ** 2).sum())
    return {"基準（北海道＝東北）R²": r2(a, n), "基準 MAE": float(np.abs(a - n).mean()),
            "切り離された時間の割合": float(dec.mean()), "切り離された時間 R² モデル": r2(a[dec], b[dec]), "切り離された時間 R² 基準": r2(a[dec], n[dec]),
            "切り離された時間 MAE モデル": float(np.abs(a[dec] - b[dec]).mean()), "切り離された時間 MAE 基準": float(np.abs(a[dec] - n[dec]).mean())}


# ---------------------------------------------------------------- 1. 較正
def step_calibration():
    cal = CB.calibration(0.0)
    f = cal["fit"]
    nr = MO.normal_min_ratio()
    rows = [("価格の作り方", "メリットオーダー＋連系線", "北海道の火力を燃料費の順に並べ、連系線で東北の価格で売買（東北へ 運用容量×比、北海道へ 運用容量）"),
            ("東北へ送れる量の比", PR.LINK_EXPORT_SHARE, "運用容量（東北向）に対する比。FY2024〜25 の流れと東北と同じ価格の時間に合わせた"),
            ("通常時の最低出力の比", "・".join(f"{k} {v:.2f}" for k, v in nr.items() if k in [u[0] for u in DT.calib()["units"]]),
             "東北の価格が燃料費より安く出力制御もない時間の、出力÷運転できる容量の中央値（FY2024〜25）"),
            ("予備力の外部の分（MW）", PR.COMMIT_RESERVE["credit"], "値崩れの日の運転台数に合わせた較正値"),
            ("旧の価格の式（参考）", f"c1 {cal['est']['c1']:.2f}（t {cal['est']['t_c1']:.1f}）、c2 {cal['est']['c2']:.2f}（t {cal['est']['t_c2']:.1f}）", "τ と季節×時刻の形。比較のために残す"),
            ("粗利の換算比 k（モデル÷実績）", cal["k"], f"2年の平均。FY2024 {cal['k_year'][2024]:.3f}・FY2025 {cal['k_year'][2025]:.3f}（年ごとの値は変種）"),
            ("実績の火力の粗利（円/kW-年、送電端）", cal["gm_act_kw"], f"FY2024 {cal['gm_act'][2024] / 1e8:.0f}・FY2025 {cal['gm_act'][2025] / 1e8:.0f}億円、{cal['cap_hist']}MW"),
            ("火力の総収入の要件（円/kW-年、実績の単位）", cal["gm_act_kw"] + PR.CAP_RECEIPT_HIST, f"粗利＋同期間に実際に受け取った容量収入（{PR.CAP_RECEIPT_HIST:,.0f}円、経過措置の控除後）"),
            ("実行できる比 s（主）", cal["capture"], "実績の価格（FY2024〜25、最初の28日を除く）で戦略c が完全予見から取る比"),
            ("供給力の余裕（MW）", cal["margin0"], "年の上位3日のピーク（最低限の規則の変種で使う）"),
            ("R²（価格の水準）", f["r2"], "推定期間"), ("MAE（円/kWh）", f["mae"], ""),
            ("日内の値幅 実績（円/kWh）", f["spread_act"], "日の上位4時間−下位4時間"), ("日内の値幅 モデル（円/kWh）", f["spread_mod"], ""),
            ("0.01円の時間 実績（h/年）", f["floor_act"], ""), ("0.01円の時間 モデル（h/年）", f["floor_mod"], "")]
    for fy in PR.CALIB_FY:
        rows += [(f"出力制御 FY{fy} 実績（h・MWh）", f"{f['curt_actual'][fy][0]}・{f['curt_actual'][fy][1]:,.0f}", ""),
                 (f"出力制御 FY{fy} モデル（h・MWh）", f"{f['curt_model'][fy][0]}・{f['curt_model'][fy][1]:,.0f}", "")]
    out(pd.DataFrame(rows, columns=["項目", "値", "注"]), "eqm_calibration.csv")
    out(pd.DataFrame({"時刻": range(24), "実績": f["hourly_act"], "モデル": f["hourly_mod"]}), "eqm_fit_hourly.csv")
    out(PR.table(), "eqm_params.csv")
    print(pd.DataFrame(rows, columns=["項目", "値", "注"]).to_string(index=False))
    return cal


# ---------------------------------------------------------------- 2. 検証（推定期間）・3. 推定に使っていない年
def step_validation(cal):
    C = DT.calib()
    rows = []
    for fy, (I, R) in cal["runs"].items():
        fl = C["p"][C["fy"] == fy] <= PR.FLOOR + 0.001
        g_act = C["G"][C["fy"] == fy]
        names = [u[0] for u in C["units"]]
        idx = [i for i, u in enumerate(R["units"]) if u[0] in names]
        fl_day = fl.any(1)
        n_on_act = (g_act.max(1) > 1.0).sum(1)
        th_act = g_act.sum(2) + C["other"][C["fy"] == fy]
        th_mod = R["g"][:, :, idx].sum(2) + R["other_out"]
        ca = I["curt_act"] > 0
        within = sum(abs(R["g"][:, :, j].sum() / max(g_act[:, :, i].sum(), 1e-9) - 1) <= 0.10
                     for i, u in enumerate(C["units"]) for j, uu in enumerate(R["units"]) if uu[0] == u[0])
        rows.append({"年度": fy, "収支のずれの最大(MW)": float(np.abs(R["residual_check"]).max()),
                     "出力制御 実績(GWh)": float(I["curt_act"].sum() / 1e3), "出力制御 モデル(GWh)": float(R["curt"].sum() / 1e3),
                     "出力制御の量の比（モデル÷実績）": float(R["curt"].sum() / max(I["curt_act"].sum(), 1e-9)),
                     "出力制御 実績(h、参考)": int(ca.sum()), "出力制御 モデル(h、参考)": int((R["curt"] > 1e-6).sum()),
                     "北海道が余る時間 モデル(h)": int(R["surplus"].sum()),
                     "出力制御の時間の火力 実績(MW)": float(th_act[ca].mean()) if ca.any() else np.nan,
                     "余剰と判定した時間の火力 モデル(MW)": float(th_mod[R["surplus"]].mean()) if R["surplus"].any() else np.nan,
                     "値崩れの時間の火力 実績(MW)": float(th_act[fl].mean()), "値崩れの時間の火力 モデル(MW)": float(th_mod[fl].mean()),
                     "火力の発電量 実績(TWh)": float(g_act.sum() / 1e6), "火力の発電量 モデル(TWh)": float(R["g"][:, :, idx].sum() / 1e6),
                     "ユニット別の発電量 ±10%に入る基数": int(within), "ユニットの数": len(names),
                     "値崩れの日の運転台数 実績（較正の目標）": float(n_on_act[fl_day].mean()),
                     "値崩れの日の運転台数 モデル（較正の目標）": float(R["on"][fl_day][:, idx].sum(1).mean()),
                     **{f"{u[0]} 実績(GWh)": float(g_act[:, :, i].sum() / 1e3) for i, u in enumerate(C["units"])},
                     **{f"{u[0]} モデル(GWh)": float(R["g"][:, :, j].sum() / 1e3) for j, u in enumerate(R["units"]) if u[0] in names}})
    V = pd.DataFrame(rows)
    # 運転の赤字の補填: 実績（ユニット別の出力・実績の価格）とモデル（α＝1）
    for i, fy in enumerate(PR.CALIB_FY):
        I, R = cal["runs"][fy]
        r = C["fy"] == fy
        G = C["G"][r]
        x = ((C["VC"][r] - C["p"][r][:, :, None]) * G).sum(1)
        V.loc[i, "運転の赤字の補填 実績(億円/年)"] = float(np.maximum(x, 0.0).sum() * 1_000 / (G.shape[0] / 365.25) / 1e8)
        names = [u[0] for u in C["units"]]
        w = np.array([1.0 if u[0] in names else 0.0 for u in R["units"]])
        V.loc[i, "運転の赤字の補填 モデル(億円/年)"] = MO.make_whole(R, R["p0"], w) / 1e8
    out(V, "eqm_validation.csv")
    print(V.iloc[:, :18].round(2).to_string(index=False))
    O = []
    for fy, lab in ((2024, "推定期間 FY2024"), (2025, "推定期間 FY2025"), (2023, "推定に使っていない FY2023"), (2026, "推定に使っていない FY2026 4〜6月")):
        I, R, pm = model_price_actual(cal, fy)
        v_a = PZ.strategy_c(np.nan_to_num(I["p_act"], nan=float(np.nanmean(I["p_act"]))), I["days"]).sum()
        v_m = PZ.strategy_c(pm, I["days"]).sum()
        O.append({"年": lab, **stats(I["p_act"], pm, I, R),
                  "出力制御 実績(GWh)": float(I["curt_act"].sum() / 1e3), "出力制御 モデル(GWh)": float(R["curt"].sum() / 1e3),
                  "出力制御 実績(h、参考)": int((I["curt_act"] > 0).sum()), "出力制御 モデル(h、参考)": int((R["curt"] > 1e-6).sum()),
                  "蓄電池の価値の比（実績÷モデル、戦略c）": float(v_a / max(v_m, 1e-9))})
    OO = pd.DataFrame(O)
    out(OO, "eqm_validation_oos.csv")
    print(OO.round(3).to_string(index=False))
    return V, OO


# ---------------------------------------------------------------- 3b. 連系線で売買できる量の較正（最終のモデルで）
def step_link(cal):
    rows = []
    for share in (333.0, 0.55, 0.65, 0.80, 1.00):
        for M in (600.0, 900.0):
            rec = {"東北へ送れる量": f"{share:.0f}MW" if share > 2 else f"運用容量×{share:.2f}", "北海道へ受けられる量(MW)": M}
            for lab, fys in (("推定期間", PR.CALIB_FY), ("FY2023", (2023,)), ("FY2026 4〜6月", (2026,))):
                A, Bm, Xa, Xm, T = [], [], [], [], []
                for fy in fys:
                    I = MO.inputs_actual(fy, share)
                    I["link"] = (I["link"][0], M)
                    R = MO.dispatch(I, B.fleet(fy))
                    A.append(I["p_act"]); Bm.append(R["p0"]); Xa.append(I["X"]); Xm.append(R["X"]); T.append(I["pT"])
                a, b, xa, xm, t = [np.concatenate(z) for z in (A, Bm, Xa, Xm, T)]
                ok = ~np.isnan(a)
                rec[f"R² {lab}"] = float(1 - ((a[ok] - b[ok]) ** 2).sum() / ((a[ok] - a[ok].mean()) ** 2).sum())
                if lab == "推定期間":
                    rec.update({"流れの平均 モデル": float(xm.mean()), "流れの平均 実績": float(xa.mean()),
                                "昼の流れ モデル": float(xm[:, 10:15].mean()), "昼の流れ 実績": float(xa[:, 10:15].mean()),
                                "夕の流れ モデル": float(xm[:, 17:21].mean()), "夕の流れ 実績": float(xa[:, 17:21].mean()),
                                "東北と同じ価格 モデル": float(np.mean(np.abs(b - t) < 0.01)), "東北と同じ価格 実績": float(np.mean(np.abs(a[ok] - t[ok]) < 0.01)),
                                "0.01円の時間 モデル(h/年)": float((b <= 0.011).sum() / len(fys) / 1), "0.01円の時間 実績(h/年)": float((a <= 0.011).sum() / len(fys))})
            rows.append(rec)
    L = pd.DataFrame(rows)
    out(L, "eqm_link_calibration.csv")
    print(L.round(2).to_string(index=False))
    return L


# ---------------------------------------------------------------- 4. 北電NW の2035年の公式シミュレーションとの照合
def step_official(cal):
    """公式（ケース①）: 出力制御率30.0%・3,972時間。前提は原子力168万kW で一定、出力制御の時間の連系線は平均769MW の送電、水力5,428GWh"""
    sc = PR.scenario_year(2035, PR.SCENARIOS["主"])
    units = B.fleet(2035)
    I0 = MO.inputs_future(sc, PR.SCENARIOS["主"])
    yrs = I0["D"].shape[0] / 365.25
    rows = []

    def add(lab, I):
        R = MO.dispatch(I, units, link=I["link"])
        mo = I["month"]
        ch = R["curt"] > 1e-6
        rows.append({"前提": lab, "原子力 平均(MW)": float(I["N"].mean()), "出力制御率": float(R["curt"].sum() / (I["S"] + I["W"]).sum()),
                     "出力制御の時間(h/年)": float(ch.sum() / yrs),
                     "うち12〜2月(h/年)": float(ch[np.isin(mo, [12, 1, 2])].sum() / yrs),
                     "出力制御の時間の北本 平均(MW)": float(R["X"][ch].mean()) if ch.any() else np.nan})
    add("主の前提（2035年、蓄電池なし）", I0)
    I1 = dict(I0, N=np.full_like(I0["N"], 1680.0), largest=np.full_like(I0["N"], PR.NUC["泊3号"]))
    add("＋公式の原子力（168万kW で一定）", I1)
    I2 = dict(I1, link=(770.0, I1["link"][1]))
    add("＋余剰の時間の送電770MW", I2)
    I3 = dict(I2)
    I3["Hy"] = I2["Hy"] * 5_428.0 / (I2["Hy"].sum() / yrs / 1e3)
    add("＋公式の水力（5,428GWh）", I3)
    rows.append({"前提": "北電NW 公式シミュレーション（ケース①）", "原子力 平均(MW)": 1680.0, "出力制御率": 0.300, "出力制御の時間(h/年)": 3972.0,
                 "うち12〜2月(h/年)": 46.0, "出力制御の時間の北本 平均(MW)": 769.0})
    Ofc = pd.DataFrame(rows)
    out(Ofc, "eqm_official_2035.csv")
    print(Ofc.round(3).to_string(index=False))
    return Ofc


# ---------------------------------------------------------------- 5. 誘導形の推定との整合の確認
def step_external(cal):
    P = DT.panel()
    P = P[(P["fy"] >= 2019) & (P["fy"] <= 2025)].copy()
    P["S_pre"] = P["solar"].fillna(0) + P["solar_curt"].fillna(0)
    P["W_pre"] = P["wind"].fillna(0) + P["wind_curt"].fillna(0)
    P["date"] = P.index.normalize()
    h = P.index.hour
    d = P.groupby("date").agg(S=("S_pre", "sum"), W=("W_pre", "sum"), D=("demand", "sum"), p=("p_hokkaido", "mean"), fy=("fy", "first"))
    d["p_mid"] = P[(h >= 10) & (h < 15)].groupby("date")["p_hokkaido"].mean()
    d["p_eve"] = P[(h >= 17) & (h < 21)].groupby("date")["p_hokkaido"].mean()
    d = d.dropna()
    for c in ("S", "W", "D"):
        d[c] = d[c] / 1e3
    d["ym"] = d.index.to_period("M").astype(str)
    d["dow"] = d.index.weekday

    def regress(dd):
        X = pd.get_dummies(dd[["ym", "dow"]].astype(str), drop_first=True).astype(float)
        X = sm.add_constant(pd.concat([dd[["S", "W", "D"]], X], axis=1))   # 燃料費は年月の固定効果に吸収される
        res = {}
        for yv in ("p_mid", "p_eve", "p"):
            r = sm.OLS(dd[yv], X).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
            res[yv] = {k: (float(r.params[k]), float(r.bse[k])) for k in ("S", "W")}
        return res
    reg_all = regress(d)
    reg_cal = regress(d[d["fy"].isin(PR.CALIB_FY)])
    est = cal["est"]

    cf = MO.tohoku_comove_coefs()

    def model_prices(scale_s=1.0, scale_w=1.0, add_n=0.0, comove=False):
        res = []
        for fy in PR.CALIB_FY:
            I = dict(MO.inputs_actual(fy))
            S0, W0 = I["S"].copy(), I["W"].copy()
            if comove:                                          # 東北の価格が北海道の再エネと一緒に動く版（頑健性の確認 B）
                dS = (scale_s - 1.0) * S0.sum(1) / 1e3
                dW = (scale_w - 1.0) * W0.sum(1) / 1e3
                I["pT"] = np.where(I["pT"] <= PR.FLOOR + 0.001, I["pT"], np.maximum(I["pT"] + cf[None, :, 0] * dS[:, None] + cf[None, :, 1] * dW[:, None], PR.FLOOR))
            I["S"], I["W"] = I["S"] * scale_s, I["W"] * scale_w
            I["U"] = np.minimum(I["U"] * scale_s, I["S"])
            I["N"] = I["N"] + add_n
            if add_n > 0:
                I["largest"] = np.full_like(I["N"], PR.NUC["泊3号"])
            R = MO.dispatch(I, B.fleet(fy))
            res.append((R["p0"], S0, W0))
        return res
    base = model_prices()
    hr = np.arange(24)
    st = lambda p: dict(p_mid=p[:, (hr >= 10) & (hr < 15)].mean(), p_eve=p[:, (hr >= 17) & (hr < 21)].mean(), p=p.mean(),
                        tb4=(np.sort(p, 1)[:, -4:].mean(1) - np.sort(p, 1)[:, :4].mean(1)).mean(), fl=(p <= 0.011).sum() / 2)
    pb = np.concatenate([b[0] for b in base])
    s_gwh = np.mean(np.concatenate([b[1] for b in base]).sum(1)) / 1e3
    w_gwh = np.mean(np.concatenate([b[2] for b in base]).sum(1)) / 1e3
    rows = []
    for lab, kw, dgwh, key in (("太陽光 +10%", dict(scale_s=1.1), 0.1 * s_gwh, "S"), ("風力 +10%", dict(scale_w=1.1), 0.1 * w_gwh, "W")):
        pm = np.concatenate([x[0] for x in model_prices(**kw)])
        pc = np.concatenate([x[0] for x in model_prices(comove=True, **kw)])
        sb, sm_, sc_ = st(pb), st(pm), st(pc)
        for yv, nm in (("p_mid", "昼10〜15時"), ("p_eve", "夕17〜21時"), ("p", "日平均")):
            rows.append({"要因": lab, "価格": nm, "構造モデル（円/kWh per GWh/日）": (sm_[yv] - sb[yv]) / dgwh,
                         "構造モデル・東北の価格が連動する版": (sc_[yv] - sb[yv]) / dgwh,
                         "回帰 FY2024〜25（円/kWh per GWh/日）": reg_cal[yv][key][0], "回帰 FY2024〜25 の標準誤差": reg_cal[yv][key][1],
                         "回帰 FY2019〜25（円/kWh per GWh/日）": reg_all[yv][key][0], "回帰 FY2019〜25 の標準誤差": reg_all[yv][key][1]})
    pn = np.concatenate([x[0] for x in model_prices(add_n=PR.NUC["泊3号"])])
    rows.append({"要因": "原子力 +872MW（20.9GWh/日、最大機も872MW）", "価格": "日内の値幅（上位4h−下位4h）",
                 "構造モデル（円/kWh per GWh/日）": (st(pn)["tb4"] - st(pb)["tb4"]) / (PR.NUC["泊3号"] * 24 / 1e3),
                 "注": ("九州の実証（原子力1GWh/日あたり）: 主仕様は夏 −0.102・冬 −0.058（10%水準）・不需要期 −0.035（有意でない）。"
                       "年月の固定効果の仕様では +0.009・−0.006・+0.018 でいずれも有意でない。補助的な証拠にとどまる。"
                       f"モデルの0.01円の時間は {st(pb)['fl']:.0f}→{st(pn)['fl']:.0f} h/年、平均価格は {st(pn)['p'] - st(pb)['p']:+.2f}円")})
    E = pd.DataFrame(rows)
    out(E, "eqm_external_validation.csv")
    print(E.round(3).to_string(index=False))
    return E


# ---------------------------------------------------------------- 6. 将来（並列）
_CAL = None


def _init():
    global _CAL
    import warnings
    warnings.filterwarnings("ignore")
    _CAL = CB.calibration(0.0)


def _job(job):
    sname, y, key, P, mode, kw, keep = job
    kw = dict(kw)
    if "k_year" in kw:
        kw["k"] = _CAL["k_year"][kw.pop("k_year")]
    Ks = BT.K_GRID if not QUICK else np.array([0.0, 20.0, 50.0, 100.0, 150.0, 200.0])
    MO.NORMAL_MIN_ON = not kw.pop("no_normal_min", False)
    sc = PR.SCENARIOS[sname]
    I = MO.inputs_future(PR.scenario_year(y, sc), sc, kw.pop("pT_shift", 0.0), kw.pop("fuel_scale", 1.0))
    df, pr = BT.run_year(I, _CAL, mode, P, Ks=Ks, keep_prices=keep, **kw)
    MO.NORMAL_MIN_ON = True
    return job, df, pr


def jobs_list():
    years = PR.YEARS if not QUICK else [2026, 2029, 2030, 2035, 2040]
    keepK = (0.0, 50.0, 100.0)
    J = []
    only = os.environ.get("ONLY_SCEN")
    only_v = [v for v in os.environ.get("ONLY_VARIANTS", "").split(",") if v]   # 主の経路の変種だけ計算し直して、既存の出力に差し込む
    bad = [v for v in only_v if v not in VARIANTS]
    if bad:
        raise SystemExit(f"ONLY_VARIANTS に変種でない名前がある（spot・capacity は全体の計算か ONLY_SCEN=主 で）: {bad}")
    for sname in PR.SCENARIOS:
        if QUICK and sname not in ("主", "原子力なし"):
            continue
        if only and sname != only:
            continue
        if only_v and sname != "主" and os.environ.get("SCEN_ALL") != "1":
            continue
        for y in years:
            for key in (MODES if not only_v else []):
                plist = [BASE_P] if (key == "capacity" or y <= 2029) else (P_MAIN if sname == "主" else P_SCEN)
                for P in plist:
                    J.append((sname, y, key, P, key, {}, keepK if (sname == "主" and P == BASE_P) else ()))
            if sname == "主" or (only_v and os.environ.get("SCEN_ALL") == "1"):
                for vk, (mode, kw) in VARIANTS.items():
                    if only_v and vk not in only_v:
                        continue
                    if sname != "主" and not only_v:
                        continue
                    main_cell = sname == "主" and vk in CELLS
                    plist = [BASE_P] if (not p_grid_needed(mode, kw) or y <= 2029) else (P_MAIN if main_cell else P_SCEN)
                    for P in plist:
                        J.append((sname, y, vk, P, mode, kw, keepK if (main_cell and P == BASE_P) else ()))
    return J


def step_future(cal):
    pik, summ, prices = {}, [], {}
    t0 = time.time()
    J = jobs_list()
    print(f"  計算の数: {len(J)}（並列 {WORKERS}）", flush=True)
    keepK = (0.0, 50.0, 100.0)
    Ks = None
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_init) as ex:
        for n, (job, df, pr) in enumerate(ex.map(_job, J, chunksize=1), 1):
            sname, y, key, P, mode, kw, keep = job
            Ks = df["K(万kW)"].to_numpy(float)
            pik[f"{sname}|{key}|{P:.0f}|{y}"] = df["π(円/kW-年)"].to_numpy(float)
            for K in keepK:
                if K in df["K(万kW)"].values:
                    summ.append({"シナリオ": sname, "価格の作り方": VLAB[key], "変種キー": key, "2030年度以降の容量価格": P, "年": y,
                                 **df[df["K(万kW)"] == K].iloc[0].to_dict()})
            for K, p in pr.items():
                prices[f"{sname}|{key}|{y}|{K:.0f}"] = p
            if n % 50 == 0 or n == len(J):
                print(f"  {n}/{len(J)} ({time.time() - t0:.0f}s)", flush=True)
    S = pd.DataFrame(summ)
    only = os.environ.get("ONLY_SCEN")
    only_v = [v for v in os.environ.get("ONLY_VARIANTS", "").split(",") if v]
    if only_v:                                                  # 変種だけ計算し直して、既存の出力に差し込む
        Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
        redone = {(j[0], j[2]) for j in J}
        old = {k: Z[k] for k in Z.files if k != "K" and (k.split("|")[0], k.split("|")[1]) not in redone}
        pik = {**old, **pik}
        Y0 = pd.read_csv(os.path.join(PROC, "eqm_years.csv"), low_memory=False)
        if not J or Ks is None:
            raise RuntimeError("計算が1つも走っていないので、既存の出力を上書きしない")
        keep0 = ~pd.Series([(a, b) in redone for a, b in zip(Y0["シナリオ"], Y0["変種キー"])], index=Y0.index)
        S = pd.concat([Y0[keep0], S], ignore_index=True)
        for c in ("契約で払う額(億円/年)", "回収しきれない額(億円/年)"):                # 新しい列がない古い行（運転の赤字は補填・全国の上乗せ）を埋める
            if c not in S:
                S[c] = np.nan
        old_rows = S["契約で払う額(億円/年)"].isna()
        cap = old_rows & S["変種キー"].astype(str).str.startswith("capacity")
        spt = old_rows & ~S["変種キー"].astype(str).str.startswith("capacity")
        S.loc[cap, "契約で払う額(億円/年)"] = S.loc[cap, "不足額 M(億円/年)"]
        S.loc[cap, "回収しきれない額(億円/年)"] = (S.loc[cap, "要件に届かない額(億円/年)"] - S.loc[cap, "不足額 M(億円/年)"]).clip(lower=0.0)
        S.loc[spt, "契約で払う額(億円/年)"] = 0.0
        S.loc[spt, "回収しきれない額(億円/年)"] = S.loc[spt, "要件に届かない額(億円/年)"]
        np.savez_compressed(os.path.join(PROC, "eqm_pik.npz"), K=Ks, **pik)
        S = add_energy_cols(S)
        out(S, "eqm_years.csv")
        PP = pd.read_csv(os.path.join(PROC, "eqm_price_profile.csv"))
        labs = {(a, VLAB[b]) for a, b in redone}
        PP = PP[~pd.Series([(a, b) in labs for a, b in zip(PP["シナリオ"], PP["価格の作り方"])], index=PP.index)]
        W = DT.weather()
        prof = []
        for key, p in prices.items():
            sname, mode, y, K = key.split("|")
            for sea in range(4):
                sel = W["season"][:, 0] == sea
                prof.append({"シナリオ": sname, "価格の作り方": VLAB[mode], "年": int(y), "K(万kW)": float(K), "季節": "冬春夏秋"[sea],
                             **{f"{h}時": float(p[sel, h].mean()) for h in range(24)}})
        out(pd.concat([PP, pd.DataFrame(prof)], ignore_index=True), "eqm_price_profile.csv")
        return pik, S, Ks
    if only:                                                    # 1つのシナリオだけ計算し直して、既存の出力に差し込む
        Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
        old = {k: Z[k] for k in Z.files if k != "K" and not k.startswith(f"{only}|")}
        pik = {**old, **pik}
        Y0 = pd.read_csv(os.path.join(PROC, "eqm_years.csv"))
        S = pd.concat([Y0[Y0["シナリオ"] != only], S], ignore_index=True)
        np.savez_compressed(os.path.join(PROC, "eqm_pik.npz"), K=Ks, **pik)
        out(S, "eqm_years.csv")
        return pik, S, Ks
    np.savez_compressed(os.path.join(PROC, "eqm_pik.npz"), K=Ks, **pik)
    S = add_energy_cols(S)
    out(S, "eqm_years.csv")
    W = DT.weather()
    prof = []
    for key, p in prices.items():
        sname, mode, y, K = key.split("|")
        for s in range(4):
            sel = W["season"][:, 0] == s
            prof.append({"シナリオ": sname, "価格の作り方": VLAB[mode], "年": int(y), "K(万kW)": float(K), "季節": "冬春夏秋"[s],
                         **{f"{h}時": float(p[sel, h].mean()) for h in range(24)}})
    out(pd.DataFrame(prof), "eqm_price_profile.csv")
    return pik, S, Ks


# ---------------------------------------------------------------- 7. 参入の均衡
def pi_curves(pik, sname, key, P, years):
    """容量価格 P のときの π の年別の曲線。2030年度以降でスポット回収（α が P で変わる）は、計算した格子の間を線形に補間する"""
    cur = {}
    for y in years:
        grid = sorted(float(k.split("|")[2]) for k in pik if k.startswith(f"{sname}|{key}|") and k.endswith(f"|{y}"))
        if not grid:
            continue
        if len(grid) == 1:
            cur[y] = pik[f"{sname}|{key}|{grid[0]:.0f}|{y}"]
            continue
        if not grid[0] - 1e-6 <= P <= grid[-1] + 1e-6:
            raise ValueError(f"容量価格 {P} が格子 {grid[0]}〜{grid[-1]} の外（{sname} {key} {y}）")
        lo = max(q for q in grid if q <= P)
        hi = min(q for q in grid if q >= P)
        a, b = pik[f"{sname}|{key}|{lo:.0f}|{y}"], pik[f"{sname}|{key}|{hi:.0f}|{y}"]
        w = 0.0 if hi == lo else (P - lo) / (hi - lo)
        cur[y] = (1 - w) * a + w * b
    return cur


def balancing_premium(pik_cur, Ks):
    """需給調整市場の上乗せ（感応度）: 2026〜2031年に、1kW の価値に (r0−π)×max(1−K/Q, 0) を足す。
    r0 は FY2026（4〜8月）の北海道の電源への支払総額÷約定量、Q は約定量の合計（全商品）。蓄電池が増えると上乗せは線形に0まで下がる"""
    F = pd.read_csv(os.path.join(PROC, "balancing_hokkaido_fy.csv"))
    f = F[(F["年度"] == 2026) & (F["商品"] != "全商品（最良の商品・支払総額）")]
    Q = float(f["約定量 平均(MW)"].sum()) / 10.0               # 万kW
    r0 = float(f["支払総額 年換算(億円)"].sum()) * 1e8 / (Q * 1e4)
    add = {}
    for t, pi in pik_cur.items():
        if t <= 2031:
            add[t] = np.maximum(r0 - pi, 0.0) * np.maximum(1.0 - Ks / Q, 0.0)
    return add, Q, r0


def step_entry(pik, Ks, S):
    years = sorted({int(k.split("|")[3]) for k in pik})
    keys = sorted({(k.split("|")[0], k.split("|")[1]) for k in pik})
    capped = S[(S["K(万kW)"] == 0.0) & S["α が上限"].astype(bool)].groupby(["シナリオ", "変種キー", "2030年度以降の容量価格"])["年"].apply(list)
    unrec = S["回収しきれない額(億円/年)"].fillna(0.0) if "回収しきれない額(億円/年)" in S else pd.Series(0.0, index=S.index)
    short = S[(S["K(万kW)"] == 0.0) & (S["α が上限"].astype(bool) | (unrec > 0.1))].groupby(["シナリオ", "変種キー", "2030年度以降の容量価格"])["年"].apply(list)
    rows = []
    KC = {}

    def kcurve(sname):
        """容量収入の κ の実効値の曲線（年ごと、K の格子の上）。PR.KAPPA_MODE が energy のときだけ使う"""
        if sname not in KC:
            sc = PR.SCENARIOS[sname]
            KC[sname] = {y: CB.kappa_eff(MO.inputs_future(PR.scenario_year(y, sc), sc), Ks) for y in years}
        return KC[sname]

    def entry_path(cur, P, case="主", start=None, ltda=True, kappa=None, ov=None, sname="主"):
        """参入の経路。ov で参入の計算だけの前提を一時的に変える（割引率、寿命、既設の蓄電池、実行できる比、κ を一定に）。
        κ: 主は量に応じた実効値（PR.KAPPA_MODE＝energy）。kappa か ov の kappa_const を与えると、その値で一定"""
        ov = ov or {}
        if "kappa_const" in ov:
            kappa = ov["kappa_const"]
        kby = kcurve(sname) if (kappa is None and PR.KAPPA_MODE == "energy") else None
        if "sratio" in ov:                                     # 価値＝実行できる比×完全予見の粗利−充電の従量費 を、比だけ変えた値に直す
            r = ov["sratio"] / PR_CAPTURE
            cur = {t: np.maximum(r * (v + PR.W_LOSS) - PR.W_LOSS, 0.0) for t, v in cur.items()}
        save = (PR.KAPPA_BATT, PR.WACC, PR.LIFE, PR.BATT_EXISTING)
        if kappa is not None:
            PR.KAPPA_BATT = kappa
        PR.WACC = ov.get("wacc", PR.WACC)
        PR.LIFE = ov.get("life", PR.LIFE)
        PR.BATT_EXISTING = ov.get("existing", PR.BATT_EXISTING)
        try:
            return EN.path(cur, Ks, P, case, start, ltda, kappa_by_year=kby)
        finally:
            PR.KAPPA_BATT, PR.WACC, PR.LIFE, PR.BATT_EXISTING = save

    def run(sname, key, P, case="主", start=None, ltda=True, kappa=None, prem=False, ov=None):
        cur = pi_curves(pik, sname, key, P, years)
        if len(cur) < len(years):
            return None
        if prem:
            add, Q, r0 = balancing_premium(cur, Ks)
            cur = {t: v + add.get(t, 0.0) for t, v in cur.items()}
        Kt = entry_path(cur, P, case, start, ltda, kappa, ov, sname=sname)
        cy = capped.get((sname, key, P), [])
        sy = short.get((sname, key, P), [])
        return {"シナリオ": sname, "価格の作り方": VLAB[key], "2030年度以降の容量価格": P,
                "参入の前提の変更": ov_label(ov),
                "資本費": case if start is None else "足下6.7万円", "LTDA を先に入れる": ltda,
                "調整係数 κ": PR.KAPPA_BATT if kappa is None else kappa,
                "κ の置き方": "一定" if (kappa is not None or "kappa_const" in (ov or {}) or PR.KAPPA_MODE != "energy") else "量に応じた実効値（上限0.861）",
                "需給調整市場の上乗せ": prem,
                "α が上限の年（蓄電池なし）": "・".join(map(str, cy)) if cy else "",
                "要件に届かない年（蓄電池なし、α が上限か回収しきれない額が0.1億円超）": "・".join(map(str, sy)) if sy else "",
                "2045年までに格子の上限（400万kW）に達した": bool(max(v for t, v in Kt.items() if t <= 2045) >= Ks[-1] - 1e-6),
                **{f"合計 {t}": Kt[t] for t in (2028, 2030, 2035, 2040, 2045)},
                **{f"うち市場参入 {t}": Kt[t] - EN.preset_stock(t, ltda) for t in (2028, 2030, 2035, 2040)}}
    for sname, key in keys:
        r = run(sname, key, BASE_P)
        if r:
            rows.append(r)
        if sname == "主" and (key in MODES or key in CELLS):
            for P in (0.0, 10_000.0, 20_911.0):
                rows.append(run(sname, key, P))
            for case, start in (("低位", None), ("高位", None), ("主", 67_000.0)):
                rows.append(run(sname, key, BASE_P, case, start))
            rows.append(run(sname, key, BASE_P, ltda=False))
            rows.append(run(sname, key, BASE_P, kappa=0.70))
            rows.append(run(sname, key, BASE_P, prem=True))
            if key.endswith("_退出あり"):
                for ov in ENTRY_OV:
                    rows.append(run(sname, key, BASE_P, ov=ov))
    E = pd.DataFrame([r for r in rows if r])
    out(E, "eqm_entry.csv")
    req = []
    for sname, key in keys:
        for tgt in (100.0, 150.0, 200.0):
            fobj = lambda P: entry_path(pi_curves(pik, sname, key, P, years), P, sname=sname)[2040] - tgt
            lo, hi = 0.0, 25_000.0
            if fobj(lo) >= 0:
                val = 0.0
            elif fobj(hi) < 0:
                val = np.nan
            else:
                for _ in range(18):
                    mid = (lo + hi) / 2
                    lo, hi = (lo, mid) if fobj(mid) >= 0 else (mid, hi)
                val = hi
            req.append({"シナリオ": sname, "価格の作り方": VLAB[key], "2040年の合計（万kW）": tgt, "要る容量価格（2030年度以降、円/kW）": val,
                        "注": "25,000円でも届かない" if np.isnan(val) else ""})
    for sname, key in keys:
        if not (sname == "主" and key.endswith("_退出あり") and key in CELLS):
            continue
        for ov in ENTRY_OV:
            for tgt in (100.0, 150.0, 200.0):
                fobj = lambda P: entry_path(pi_curves(pik, sname, key, P, years), P, ov=ov, sname=sname)[2040] - tgt
                lo, hi = 0.0, 25_000.0
                if fobj(lo) >= 0:
                    val = 0.0
                elif fobj(hi) < 0:
                    val = np.nan
                else:
                    for _ in range(18):
                        mid = (lo + hi) / 2
                        lo, hi = (lo, mid) if fobj(mid) >= 0 else (mid, hi)
                    val = hi
                req.append({"シナリオ": sname, "価格の作り方": VLAB[key] + "【" + ov_label(ov) + "】", "2040年の合計（万kW）": tgt,
                            "要る容量価格（2030年度以降、円/kW）": val, "注": "25,000円でも届かない" if np.isnan(val) else ""})
    RQ = pd.DataFrame(req)
    out(RQ, "eqm_required_capacity_price.csv")
    show = E[(E["資本費"] == "主") & E["LTDA を先に入れる"] & (E["2030年度以降の容量価格"] == BASE_P) & (E["調整係数 κ"] == PR.KAPPA_BATT)
             & ~E["需給調整市場の上乗せ"]]
    print(show.round(1).to_string(index=False))
    print(E[(E["シナリオ"] == "主") & E["価格の作り方"].isin(MODES.values())].round(1).to_string(index=False))
    print(RQ.round(0).to_string(index=False))
    _, Q, r0 = balancing_premium({2026: np.zeros(len(Ks))}, Ks)
    print(f"需給調整市場の上乗せ: Q {Q:.1f}万kW、r0 {r0:,.0f}円/kW-年")
    return E, RQ


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    t0 = time.time()
    if os.environ.get("CHECKS_ONLY") == "1":                 # 較正・検証・公式との照合・誘導形との整合だけ
        cal = step_calibration()
        step_validation(cal)
        step_link(cal)
        step_official(cal)
        step_external(cal)
        sys.exit(0)
    if os.environ.get("ENTRY_ONLY") == "1":                  # 将来の計算の保存結果から、参入の均衡だけを解き直す
        Z = np.load(os.path.join(PROC, "eqm_pik.npz"))
        step_entry({k: Z[k] for k in Z.files if k != "K"}, Z["K"], pd.read_csv(os.path.join(PROC, "eqm_years.csv")))
        sys.exit(0)
    cal = step_calibration()
    step_validation(cal)
    step_link(cal)
    step_official(cal)
    step_external(cal)
    pik, S, Ks = step_future(cal)
    step_entry(pik, Ks, S)
    print(f"計 {time.time() - t0:.0f}s")
