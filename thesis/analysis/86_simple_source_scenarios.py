#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデル: 電源別のシナリオ（著者の依頼 2026-10-31、2026-11-03 に新しい主を起点に作り直し）。
主（2026-11-02 の決定: 第7次エネ基の2040年度見通しの中央×北海道の今のシェアで太陽光698.5・風力615.1万kW、FY2035 までは供給計画、泊3号だけ）から、
太陽光・風力・原子力のどれか1つだけを動かし、蓄電池の価値 π と市場だけで入る量がどう変わるかを見る（容量価格14,972円）。
スポットで回収（主）、赤字だけ市場外、すべて市場外（燃料費で入札）の3つで解く。主の上乗せでは、
どの電源が増えても火力の発電量が減って μ が上がるので、一般的な方法と並べて、電源の価格の形への効きと、固定費をスポットで回収することの効きを分け、
赤字を外で精算する場合と並べて、後者のうちマストランの赤字の分を分ける。
動かす量（2040年の値。経路は主と同じ: FY2035 まで供給計画、FY2035→2040 は直線。2040年の値が2035年より小さい場合も直線で下げる）:
- 太陽光（自家消費を含む）: 243万kW（FY2025 年度末のまま）、356万kW（2035年度の公的な値のまま）、
  588万kW（エネ基の下限×今のシェア）、698.5万kW（主）、809万kW（エネ基の上限×今のシェア）。自家消費は2035年からの増分の31%（主と同じ規則）
- 風力: 137万kW（FY2025 年度末のまま）、275万kW（2035年度の公的な値のまま）、418万kW（エネ基の下限）、615万kW（主）、
  813万kW（エネ基の上限）、1,230万kW（陸上は主の275＋洋上955。2026-11-03 の著者の回答で1,155万kW（陸上200＋洋上955）から変更。洋上は洋上風力産業ビジョン（第1次、2020-12）p.7 の北海道の2040年の下限、案件形成ベースで予測ではない）
- 原子力: なし、3号だけ（主）、3号＋1号（1号 FY2032）、3基（2号 FY2033、時期は仮定）
退出: シナリオごとに、先に入っている蓄電池の量の経路で年を順に解く（主と同じ SM.exit_years。一般的な方法も上乗せありの退出の経路を使う、主と同じ）。
前提はこのスクリプトの中だけで足す（params の値は変えない）。
出力: data/processed/simple_source_scenarios.csv、simple_source_exit_years.csv、figures/hokkaido/simple_source_scenarios.png
（FIG_ONLY=1 なら CSV から図だけ描き直す）
"""
import os
import sys
import warnings
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
from model import params as PR, merit as MO, simple as SM, entry as EN

PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
WORKERS = int(os.environ.get("WORKERS", "9"))
KS = [0.0, 10.0, 25.0, 50.0, 75.0, 95.0, 100.0, 125.0, 150.0, 175.0, 200.0, 250.0, 300.0, 400.0, 500.0]
P = 14_972.0
YEARS = (2035, 2040)
# 場合: (名前, standard, losses)。losses は SM.run_year の引数（'spot'＝主、'outside'＝マストランの赤字はスポットの外で精算）
CASES = [("スポットで回収（主）", False, "spot"),
         ("赤字だけ市場外", False, "outside"),
         ("すべて市場外", True, "spot")]
SHARE = PR.SELFCONS_SHARE[PR.MAIN_SC["y2040"]]                  # 自家消費の比（基準は0＝分けない。頑健性「自家消費を分ける」は増分の31%）
MAIN = {**PR.Y2040[PR.MAIN_SC["y2040"]]}
MAIN["onsite"] = MAIN["solar"] * SHARE                          # 下で行ごとに比を onsite÷solar で作るので、基準の比とそろえる
sol = lambda mw: {"solar": mw, "onsite": mw * SHARE}              # onsite は比を渡すためだけに使う（自家消費の量は経路の規則で決まる）

# シナリオ: (名前, 動かす電源, 2040年の値, 泊の号機)。2040年の値は PR.Y2040 の形（需要と DC は主のまま）
SCN = [("主", "主", MAIN, "3号だけ"),
       ("太陽光 243万kW（FY2025 のまま）", "太陽光", {**MAIN, "solar": 2_430.0, "onsite": 0.0}, "3号だけ"),
       ("太陽光 356万kW（2035年度の公的な値のまま）", "太陽光", {**MAIN, **sol(3_560.0)}, "3号だけ"),
       ("太陽光 588万kW（エネ基の下限）", "太陽光", {**MAIN, **sol(PR.Y2040["エネ基下限"]["solar"])}, "3号だけ"),
       ("太陽光 809万kW（エネ基の上限）", "太陽光", {**MAIN, **sol(PR.Y2040["エネ基上限"]["solar"])}, "3号だけ"),
       ("風力 137万kW（FY2025 のまま）", "風力", {**MAIN, "wind": 1_370.0}, "3号だけ"),
       ("風力 275万kW（2035年度の公的な値のまま）", "風力", {**MAIN, "wind": 2_750.0}, "3号だけ"),
       ("風力 418万kW（エネ基の下限）", "風力", {**MAIN, "wind": PR.Y2040["エネ基下限"]["wind"]}, "3号だけ"),
       ("風力 813万kW（エネ基の上限）", "風力", {**MAIN, "wind": PR.Y2040["エネ基上限"]["wind"]}, "3号だけ"),
       ("風力 1,230万kW（陸上275＋洋上風力産業ビジョンの下限955）", "風力", {**MAIN, "wind": 12_300.0}, "3号だけ"),
       ("原子力 なし", "原子力", MAIN, "なし"),
       ("原子力 3号＋1号", "原子力", MAIN, "3号＋1号"),
       ("原子力 3基", "原子力", MAIN, "3基")]
for i, (_, _, a, _) in enumerate(SCN):                          # 各プロセスで読み込み時に登録する
    PR.Y2040[f"src{i}"] = a
    PR.SELFCONS_SHARE[f"src{i}"] = a["onsite"] / a["solar"] if a["solar"] > 0 else 0.0
PR.NUC_CASES["なし"] = ()
PR.NUC_CASES["3号＋1号"] = ("泊3号", "泊1号")


def sc_of(i):
    return {**PR.MAIN_SC, "y2040": f"src{i}", "nuclear": SCN[i][3]}


def exits(i):
    import warnings; warnings.filterwarnings("ignore")
    before, when = SM.exit_years(SM.calibration("commit", None), sc_of(i), PR.YEARS, "commit")
    return i, before, when


def job(args):
    import warnings; warnings.filterwarnings("ignore")
    i, y, c, drop = args
    case, standard, losses = CASES[c]
    name, group, a, nuc = SCN[i]
    sc = sc_of(i)
    sy = PR.scenario_year(y, sc)
    I = MO.inputs_future(sy, sc)
    T, _ = SM.run_year(I, SM.calibration("commit", None), Ks=KS, P_list=(P,), standard=standard, p_sched=P, drop=drop, losses=losses)
    pi = T["π(円/kW-年)"].to_numpy()
    th = EN.annual_cost(y) + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * P
    v = np.minimum.accumulate(pi)
    if v[0] < th:
        k = 0.0
    elif v[-1] >= th:
        k = float(KS[-1])
    else:
        j = int(np.argmax(v < th)); k = KS[j - 1] + (KS[j] - KS[j - 1]) * (v[j - 1] - th) / (v[j - 1] - v[j])
    r0, r100 = T[T["K(万kW)"] == 0.0].iloc[0], T[T["K(万kW)"] == 100.0].iloc[0]
    pi988 = float(np.interp(98.8, KS, pi))
    W = I["S"].shape[0] / 365.25                              # 気象年の数（1年あたりに直す）
    from model import data as DT
    cfS = DT.weather()["cf_S"]
    return {"シナリオ": name, "動かす電源": group, "場合": case, "年": y,
            "太陽光(万kW)": sy["solar_mw"] / 10 + sy["selfcons_mw"] / 10, "風力(万kW)": sy["wind_mw"] / 10, "泊": nuc,
            "太陽光の発電量(TWh、自家消費を含む)": float((I["S"].sum() + sy["selfcons_mw"] * cfS.sum() * 0.85) / W / 1e6),
            "風力の発電量(TWh)": float(I["W"].sum() / W / 1e6), "原子力の発電量(TWh)": float(I["N"].sum() / W / 1e6),
            "前の年までに退出": "・".join(drop),
            "π 0万kW": pi[0], "π 98.8万kW": pi988, "しきい値": th, "市場だけで入る量(万kW)": k,
            "98.8万kW で参入": "あり" if pi988 > th else "なし",
            "値幅 0万kW": r0["日の値幅 高い4時間−安い4時間(円/kWh)"], "高い4時間 0万kW": r0["高い4時間の平均(円/kWh)"],
            "安い4時間 0万kW": r0["安い4時間の平均(円/kWh)"],
            "値幅 100万kW": r100["日の値幅 高い4時間−安い4時間(円/kWh)"], "高い4時間 100万kW": r100["高い4時間の平均(円/kWh)"],
            "安い4時間 100万kW": r100["安い4時間の平均(円/kWh)"],
            "μ 0万kW": r0["上乗せ μ(円/kWh)"], "μ 100万kW": r100["上乗せ μ(円/kWh)"], "平均価格 100万kW": r100["平均価格（需要加重）"],
            "マストランの赤字 0万kW(億円/年)": r0["マストランの運転の赤字 α＝1(億円/年)"], "市場の外の補填 0万kW(億円/年)": r0["市場の外の補填(億円/年)"],
            "0.01円の時間 0万kW(h)": r0["0.01円の時間(h/年)"], "0.01円の時間 100万kW(h)": r100["0.01円の時間(h/年)"],
            "抑制 0万kW(TWh)": r0["抑制(TWh)"], "抑制 100万kW(TWh)": r100["抑制(TWh)"],
            "火力の発電量 100万kW(TWh)": r100["火力の発電量(TWh)"], "残る火力 100万kW(MW)": r100["残る火力(MW)"],
            "退出する号機 100万kW": r100["退出する号機"]}


def figure(R):
    """2040年の市場だけで入る量を、動かす電源の発電量に対して3つの場合で描く（主の点は3つの電源で共通）"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
    C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"                 # 概観の図と同じ並び（主＝C1、一般的な方法＝C2）
    plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
    plt.rcParams["font.size"] = 10
    D = R[R["年"] == 2040]
    xcol = {"太陽光": "太陽光の発電量(TWh、自家消費を含む)", "風力": "風力の発電量(TWh)", "原子力": "原子力の発電量(TWh)"}
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), sharey=True)
    for ax, (g, xc) in zip(axes, xcol.items()):
        for (case, _, _), col in zip(CASES, (C1, C3, C2)):
            d = D[(D["場合"] == case) & D["動かす電源"].isin([g, "主"])].sort_values(xc)
            ax.plot(d[xc], d["市場だけで入る量(万kW)"], color=col, marker="o", ms=4, lw=2, label=case)
        m = D[(D["場合"] == CASES[0][0]) & (D["動かす電源"] == "主")].iloc[0]
        ax.annotate("主", (m[xc], m["市場だけで入る量(万kW)"]), xytext=(4, 6), textcoords="offset points", color=C1, fontsize=9)
        ax.axhline(98.8, color=MUTED, lw=1, ls="--")
        ax.set_xlabel(f"{g}の発電量（TWh/年、2040年）", color=INK)
        ax.set_title(g, loc="left", color=INK, fontsize=11)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color("#c3c2b7")
        ax.tick_params(colors=MUTED)
        ax.grid(axis="y", color=GRID, lw=0.7)
        ax.set_axisbelow(True)
    axes[0].text(axes[0].get_xlim()[0], 101, " 既設＋LTDA 98.8万kW", color=MUTED, fontsize=8.5, va="bottom")
    axes[0].set_ylabel("LTDA などの契約なしで採算が合う量（万kW、2040年）", color=INK)
    axes[0].legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.suptitle("電源を1つだけ動かしたときの、スポットと容量市場の収入で採算が合う蓄電池の量（容量価格14,972円、ほかは主のまま）", x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "simple_source_scenarios.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote simple_source_scenarios.png")


def main():
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    if os.environ.get("FIG_ONLY"):
        figure(pd.read_csv(os.path.join(PROC, "simple_source_scenarios.csv"))); return
    only = os.environ.get("ONLY")                              # 確かめ用: シナリオの番号（カンマ区切り）
    idx = [int(x) for x in only.split(",")] if only else list(range(len(SCN)))
    years = tuple(int(x) for x in os.environ["YEARS"].split(",")) if os.environ.get("YEARS") else YEARS
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        E = list(ex.map(exits, idx))
    ex_rows = [{"シナリオ": SCN[i][0], "号機": n, "退出の年": yy} for i, _, when in E for n, yy in when.items()]
    before = {i: b for i, b, _ in E}
    jobs = [(i, y, st, before[i][y]) for i in idx for y in years for st in range(len(CASES))]
    print(f"計算の数 {len(jobs)}", flush=True)
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    suffix = os.environ.get("SUFFIX", "")
    pd.DataFrame(ex_rows, columns=["シナリオ", "号機", "退出の年"]).to_csv(
        os.path.join(PROC, f"simple_source_exit_years{suffix}.csv"), index=False, encoding="utf-8-sig")
    R.to_csv(os.path.join(PROC, f"simple_source_scenarios{suffix}.csv"), index=False, encoding="utf-8-sig")
    print(pd.DataFrame(ex_rows).to_string())
    print(R.round(2).to_string(index=False))
    if not only:
        figure(R)


if __name__ == "__main__":
    main()
