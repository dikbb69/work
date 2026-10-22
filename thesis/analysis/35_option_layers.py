#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完全予見粗利を日次スプレッド（交換）オプションの3層に分解する（北海道、FY2016〜25）

手法:
  蓄電池（4時間・往復効率0.85を放電側に一括・1日1サイクル・日をまたがない・価格テイカー）の日次ペイオフを、
  放電窓 D と充電窓 C（各4時間）を選んで「充電時間の電力 1/η 単位を放電時間の電力 1 単位と交換する」
  スプレッド（交換）オプションとみなす。1/η≈1.18 はスパーク・スプレッドのヒートレートに当たる。
      X(D, C) = η·Σ_{h∈D} p_h − Σ_{h∈C} p_h   [円/kW-日]
  完全予見粗利 PF = max_{D,C} X(D, C)^+ は、当日の実現価格を見てから窓を選ぶ「ペナルティなしの情報緩和」
  （Brown, Smith & Sun 2010）による上界で、日ごとに（標本の経路ごとに）先読みのないどの方策の粗利も上回る。
  これを3層に分ける（すべて当日の実現価格で評価する。日次で (II)≥0、(III)≥0）:
    (I)   期待価格カーブに対する本源的（intrinsic）方策の価値 = Σ X(D_c, C_c)。窓は直近29日（24時間そろう日）のうち
          同じ曜日区分（平日/土日。祝日は平日扱い。5日以上）の平均価格カーブ（原稿の「過去28日」の気候値。北海道に
          時間別のフォワードはないので期待価格カーブの代理とする）の上位4h/下位4hで、前日に固定する。analysis/16・19 の
          戦略 c と同一で、(I)/PF が capture率になる。c は先読みのない方策の一つなので、その価値は先読みのない最適方策の
          価値の下界になる（期待値の意味。実現値は標本に依存する）。
    (II)  休止の価値 = Σ max(X_c, 0) − Σ X_c。固定窓の粗利が負になる日に行使しない価値。事後の符号で判定するので、
          前日入札だけで確実に取れる額ではなく、その上限である。
    (III) 窓の選び直しの価値 = PF − Σ max(X_c, 0)。当日の実現価格で窓を選び直す価値。
    (II)+(III) が固定窓に対する完全情報の価値で、前日約定後に時間前市場でスポットと同じ価格・十分な流動性で
          組み替えられるとした場合に取れる額（＝その上限）にあたる。ガス貯蔵評価の extrinsic（フォワードの動的取引で
          実際に得る価値）とは性質が違う。
  集計: 年度別（FY2016〜25）、年度×季節、FY2023〜25 の季節別と季節×風力三分位（三分位は analysis/17 と同じ定義）。
  季節別には、戦略 c の窓と完全予見の窓の一致時間、完全予見の放電窓・充電窓の時刻（朝6〜11時・夕16〜21時、
  昼9〜15時・夜0〜5時）、朝に2時間以上放電する日とそれ以外の日の (III) の比率も出す（(III) が冬に大きい理由の確認用）。
  頑健性1（充放電の順序）: ランク法は「充電してから放電する」順序を無視する。0時に空の状態から始め、各時刻までの
  放電時間が充電時間を超えない制約を課した厳密解（24時間×(充電回数,放電回数) の動的計画。ランク法と同じく充放電4時間ずつ
  か休止）で完全予見粗利を、期待価格カーブに対して同じ制約で選んだ窓で (I) を計算し直し、3層を出す。
  頑健性2（風力との関係）: FY2023〜25 の日次の PF・(I)・(II)・(III)（円/kW-日）を季節ごとに日次風力（GWh/日、出力制御前）
  に回帰する。仕様は (a) 年度固定効果、(b) 年月固定効果＋日次需要・太陽光（出力制御前、GWh/日）・土日ダミー。
  標準誤差は Newey-West（7ラグ。3年分の季節の日を時系列順につないだ系列に適用）。
  検算: 図7.1（analysis/19 §1）と同じ集計で戦略 a・b・c の capture率を年度別に出す（7.2 の訂正用）。戦略 c の窓を
  安定ソート（パイロット p2 の実装）で選んだ場合との差も出す。表7.3（analysis/17 §2）を現データで全セル再計算し、
  三分位の境界に乗る日の扱いの感応度と、夏を7〜8月に限った場合（7.3 本文の数値）も出す。
  正規近似（Bachelier 型）の価格公式は評価に使わない。年度×季節で、正規近似が時間価値を何倍に出すかを診断列として
  残すだけである。
出力:
  data/processed/option_layers_by_fy.csv          年度別の3層（円/kW-年）、順序制約つきの3層、図7.1と同じ集計の戦略別 capture率
  data/processed/option_layers_by_season.csv      年度×季節、FY2023〜25 の季節別・季節×風力三分位の3層（順序制約つきを併記）
  data/processed/option_layers_wind_regression.csv FY2023〜25 の日次の層を風力に回帰した係数（季節別、2仕様）
  data/processed/table73_refresh.csv              表7.3 の全セルの再計算値（原稿値を併記）
  figures/hokkaido/option_layers.png              年度別の積み上げ棒と FY2023〜25 の季節×風力三分位
限界:
  本体はランク法で、充放電の順序と SoC を無視する。順序を課すと完全予見の窓は FY2023〜25 の28%の日（冬は54%）、
  戦略 c の窓は12%の日（冬は36%）で実行不能になるが、順序制約つきの厳密解でも (I) の額はほぼ変わらず（±0.4%以内）、
  完全予見粗利が年度により0.3〜2.7%下がる（FY2023〜25 の capture率は0.817→0.835、冬の (III)/PF は0.315→0.279。
  頑健性1）。60分粒度。価格テイカー。先読みのない最適方策の価値は、期待値で見て (I) と PF の間にあるが、ペナルティ付きの
  双対上界は計算していない。c は試した戦略（a・a2・b・c）の中で最善だったものを事後に採ったので、(I) の実現値は
  その期待値をやや過大に表しうる（データ・スヌーピング。Reality Check／SPA 型の検定で扱う）。FY2018 は胆振東部地震の欠測日（24時間そろわない日）
  を含まない観測日の合計。FY2016 の3層は戦略 c のウォームアップ（冒頭の10日）を除く共通標本で、図7.1 の集計（PF は
  全日の合計）とは分母が違う（capture率 0.856 と 0.843）。戦略 a は前日価格の同順位（0.01円の時間など）の並べ方で
  capture率が動き（FY2023〜25 で最大0.6ポイント、FY2016 は67.1〜71.8%）、並べ方は numpy・pandas の版や CPU に
  依存しうる（戦略 c は安定ソートと19の並べ方で全日一致）。表7.3 の冬は 2026-02-26 の日次風力（7,800 MWh）が
  1/3 分位点に、2026-02-24（12,760 MWh）が 2/3 分位点にちょうど一致し、≤・≥ の判定が分位点計算の丸めに依存する
  （2026-02-26 を「小」に入れると 7.24円・18.98円/kW-日、「中」に入れると原稿の 7.30円・19.2円/kW-日）。
  回帰の Newey-West は年をまたぐ季節の継ぎ目も隣り合う日として扱う。
"""
import os

import numpy as np
import pandas as pd
from matplotlib import font_manager
import matplotlib.pyplot as plt
from scipy.stats import norm
import statsmodels.formula.api as smf

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
OUT_FY = os.path.join(PROC, "option_layers_by_fy.csv")
OUT_SEASON = os.path.join(PROC, "option_layers_by_season.csv")
OUT_T73 = os.path.join(PROC, "table73_refresh.csv")
OUT_REG = os.path.join(PROC, "option_layers_wind_regression.csv")
OUT_FIG = os.path.join(FIGDIR, "option_layers.png")

ETA, H = 0.85, 4
FY_FULL = list(range(2016, 2026))
FY_NOW = [2023, 2024, 2025]
SEASONS = [("夏", [7, 8, 9]), ("冬", [12, 1, 2]), ("不需要期", [3, 4, 5, 6, 10, 11])]
M2S = {m: s for s, ms in SEASONS for m in ms}
TER = ["小", "中", "大"]
GRAY = "#595959"
C_I, C_II, C_III = "#D95B20", "#5DB6E7", "#0079C2"   # (I) は図7.1の戦略cと同じ色

hp = pd.read_csv(os.path.join(PROC, "hokkaido_hourly_panel.csv"), parse_dates=["ts"])
hp["day"] = hp["ts"].dt.normalize()
hp["hour"] = hp["ts"].dt.hour
hp["fy"] = hp["ts"].dt.year - (hp["ts"].dt.month < 4).astype(int)
hp["wind_pre"] = hp["wind"].fillna(0) + hp["wind_curt"].fillna(0)

# ============================================================
# 1. 日次の計算（analysis/19 §1 と同じ標本・窓の選び方）
# ============================================================
P = hp.dropna(subset=["p_hokkaido"]).pivot(index="day", columns="hour", values="p_hokkaido")
P = P[P.count(axis=1) == 24]
D = hp.pivot(index="day", columns="hour", values="demand")
S = hp.pivot(index="day", columns="hour", values="solar")
days = P.index
all_days = D.index
wk = pd.Series(all_days.dayofweek >= 5, index=all_days)
wkP = pd.Series(days.dayofweek >= 5, index=days)


def margin(p, dis, chg):
    """固定窓の日次粗利（円/kW-日）。19 の margin（円/MW-日）を 1/1000 にしたもの。"""
    return p[list(dis)].sum() * ETA - p[list(chg)].sum()


def win(series):
    """19 と同じ窓の選び方（pandas の既定ソート）。上位4h=放電、下位4h=充電。"""
    o = series.sort_values()
    return o.index[-H:], o.index[:H]


def win_stable(v):
    """パイロット p2 の実装（安定ソート）。同順位の扱いだけが 19 と違いうる。"""
    o = np.argsort(v, kind="stable")
    return o[-H:], o[:H]


def order_ok(dis, chg):
    """0時に空の状態から始めて、各時刻までの放電時間が充電時間を超えないか（ランク法の窓が順序の上で実行可能か）。"""
    s = 0
    for h in range(24):
        s += (h in chg) - (h in dis)
        if s < 0:
            return False
    return True


def ordered_opt(v):
    """順序制約つきの厳密解（頑健性1）。状態=(充電回数, 放電回数)、放電回数≤充電回数≤4 の動的計画で、
    充電4時間・放電4時間をすべて使う窓のうち順序の上で実行可能な最良のものを返す（ランク法と同じく4時間ずつ。
    完全予見は呼び出し側で 0 と比べて休止を許す）。戻り値は (目的関数値, 放電時刻, 充電時刻)。"""
    V = {(0, 0): (0.0, (), ())}
    for h in range(24):
        NV = {}
        for (nc, nd), (val, ds, cs) in V.items():
            cand = [((nc, nd), val, ds, cs)]
            if nc < H:
                cand.append(((nc + 1, nd), val - v[h], ds, cs + (h,)))
            if nd < nc:
                cand.append(((nc, nd + 1), val + ETA * v[h], ds + (h,), cs))
            for st_, vv, dd_, cc_ in cand:
                if st_ not in NV or vv > NV[st_][0]:
                    NV[st_] = (vv, dd_, cc_)
        V = NV
    best = V[(H, H)]
    return best[0], list(best[1]), list(best[2])


rows = []
for i, d in enumerate(days):
    p = P.loc[d]
    dis, chg = win(p)
    x_pf = margin(p, dis, chg)
    hd, hc = set(dis), set(chg)
    pv = p.to_numpy()
    rec = {"day": d, "pf": max(0.0, x_pf), "pf_raw": x_pf,
           "pf_dis_am": len(hd & set(range(6, 12))), "pf_dis_pm": len(hd & set(range(16, 22))),
           "pf_chg_mid": len(hc & set(range(9, 16))), "pf_chg_night": len(hc & set(range(0, 6))),
           "pf_order_ok": order_ok(hd, hc), "pf_ord": max(0.0, ordered_opt(pv)[0])}
    if i >= 1:
        rec["a"] = margin(p, *win(P.loc[days[i - 1]]))
        pv, qv = p.to_numpy(), P.loc[days[i - 1]].to_numpy()
        da, ca = win_stable(qv)
        rec["a_stable"] = pv[da].sum() * ETA - pv[ca].sum()
        da, ca = win_stable(qv[::-1])
        rec["a_stable_rev"] = pv[23 - da].sum() * ETA - pv[23 - ca].sum()
    hist_p = [dd for dd in days[max(0, i - 29):i] if wkP[dd] == wkP[d]]
    if len(hist_p) >= 5:
        prof = P.loc[hist_p].mean()
        dc, cc = win(prof)
        rec["c"] = margin(p, dc, cc)
        ds, cs = win_stable(prof.to_numpy())
        rec["c_stable"] = pv[ds].sum() * ETA - pv[cs].sum()
        rec["dis_overlap"] = len(set(dis) & set(dc))
        rec["chg_overlap"] = len(set(chg) & set(cc))
        rec["c_order_ok"] = order_ok(set(dc), set(cc))
        _, do, co = ordered_opt(prof.to_numpy())
        rec["c_ord"] = pv[do].sum() * ETA - pv[co].sum()
    jj = all_days.get_loc(d)
    if jj >= 30:
        hist = all_days[max(0, jj - 29):jj - 1]
        same = [h for h in hist if wk[h] == wk[d]]
        if len(same) >= 5:
            dem_f = D.loc[same].mean()
            sol_f = S.loc[all_days[jj - 8:jj - 1]].mean()
            rec["b"] = margin(p, *win(dem_f - sol_f))
    rows.append(rec)
bt = pd.DataFrame(rows).set_index("day")
bt["fy"] = bt.index.year - (bt.index.month < 4).astype(int)
bt["season"] = bt.index.month.map(M2S)
bt["wind"] = hp.groupby("day")["wind_pre"].sum().reindex(bt.index) / 1000   # GWh/日（出力制御前）
bt["c_pos"] = bt["c"].clip(lower=0)
bt["c_ord_pos"] = bt["c_ord"].clip(lower=0)
cs_ = bt.dropna(subset=["c"])
assert (cs_["pf"] + 1e-9 >= cs_["c_pos"]).all(), "PF ≥ max(X_c,0) が崩れている"
assert (cs_["pf_ord"] + 1e-9 >= cs_["c_ord_pos"]).all(), "順序制約つきでも PF ≥ max(X_c,0) のはず"
assert (bt["pf"] + 1e-9 >= bt["pf_ord"]).all(), "順序制約つきの PF はランク法の PF を超えないはず"


def layers(df, pf="pf", c="c"):
    """3層の合計（円/kW-年 または 円/kW-日×日数）と比率。df は戦略 c がある日の共通標本。"""
    pf_, xc, xcp = df[pf].sum(), df[c].sum(), df[c].clip(lower=0).sum()
    return {"日数": len(df), "PF": pf_, "I": xc, "II": xcp - xc, "III": pf_ - xcp,
            "capture": xc / pf_, "II_share": (xcp - xc) / pf_, "III_share": (pf_ - xcp) / pf_,
            "loss_day": (df[c] < 0).mean(), "pf0_day": (df["pf_raw"] <= 0).mean()}


# ============================================================
# 2. 年度別（共通標本の3層＋図7.1と同じ集計の capture率）
# ============================================================
fy_rows = []
for fy in FY_FULL:
    allf = bt[bt["fy"] == fy]
    com = allf.dropna(subset=["c"])
    L = layers(com)
    LO = layers(com, "pf_ord", "c_ord")
    fig71_pf = allf["pf"].sum()
    fy_rows.append({
        "年度": f"FY{fy}", "日数_共通標本": L["日数"],
        "完全予見粗利PF(円/kW-年)": L["PF"], "(I)本源的方策(円/kW-年)": L["I"],
        "(II)休止(円/kW-年)": L["II"], "(III)窓の選び直し(円/kW-年)": L["III"],
        "(II)+(III)完全情報の価値(円/kW-年)": L["II"] + L["III"],
        "capture率=(I)/PF": L["capture"], "(II)/PF": L["II_share"], "(III)/PF": L["III_share"],
        "固定窓で損失の日の比率": L["loss_day"], "固定窓で損失の日数": int((com["c"] < 0).sum()),
        "固定窓の損失日の平均損失(円/kW-日)": com.loc[com["c"] < 0, "c"].mean(),
        "完全予見でも休止の日の比率": L["pf0_day"],
        "順序_完全予見の窓が実行不能な日の比率": 1 - com["pf_order_ok"].astype(float).mean(),
        "順序_戦略cの窓が実行不能な日の比率": 1 - com["c_order_ok"].astype(float).mean(),
        "順序制約_PF(円/kW-年)": LO["PF"], "順序制約_(I)(円/kW-年)": LO["I"], "順序制約_(II)(円/kW-年)": LO["II"],
        "順序制約_(III)(円/kW-年)": LO["III"], "順序制約_capture率": LO["capture"],
        "順序制約_(II)/PF": LO["II_share"], "順序制約_(III)/PF": LO["III_share"],
        "順序制約_PF/ランク法PF−1": LO["PF"] / L["PF"] - 1, "順序制約_(I)/ランク法(I)−1": LO["I"] / L["I"] - 1,
        "日数_図7.1": len(allf), "図7.1_PF(円/kW-年)": fig71_pf,
        "図7.1_a(円/kW-年)": allf["a"].sum(), "図7.1_b(円/kW-年)": allf["b"].sum(),
        "図7.1_c(円/kW-年)": allf["c"].sum(),
        "図7.1_capture_a": allf["a"].sum() / fig71_pf, "図7.1_capture_b": allf["b"].sum() / fig71_pf,
        "図7.1_capture_c": allf["c"].sum() / fig71_pf,
        "検算_安定ソート版c−19版c(円/kW-年)": (com["c_stable"] - com["c"]).sum(),
        "検算_窓が違う日数": int((np.abs(com["c_stable"] - com["c"]) > 1e-9).sum()),
        "検算_capture_a_安定ソート": allf["a_stable"].sum() / fig71_pf,
        "検算_capture_a_逆順の安定ソート": allf["a_stable_rev"].sum() / fig71_pf,
    })
fyt = pd.DataFrame(fy_rows)
num = [c for c in fyt.columns if c != "年度"]
for lab, fys in [("FY2023-25平均", FY_NOW), ("FY2016-25平均", FY_FULL)]:
    sub = fyt[fyt["年度"].isin([f"FY{y}" for y in fys])]
    r = {"年度": lab}
    for c in num:
        r[c] = sub[c].mean()
    pf, pf71 = r["完全予見粗利PF(円/kW-年)"], r["図7.1_PF(円/kW-年)"]
    r["capture率=(I)/PF"] = r["(I)本源的方策(円/kW-年)"] / pf
    r["(II)/PF"] = r["(II)休止(円/kW-年)"] / pf
    r["(III)/PF"] = r["(III)窓の選び直し(円/kW-年)"] / pf
    pfo = r["順序制約_PF(円/kW-年)"]
    r["順序制約_capture率"] = r["順序制約_(I)(円/kW-年)"] / pfo
    r["順序制約_(II)/PF"] = r["順序制約_(II)(円/kW-年)"] / pfo
    r["順序制約_(III)/PF"] = r["順序制約_(III)(円/kW-年)"] / pfo
    r["順序制約_PF/ランク法PF−1"] = pfo / pf - 1
    r["順序制約_(I)/ランク法(I)−1"] = r["順序制約_(I)(円/kW-年)"] / r["(I)本源的方策(円/kW-年)"] - 1
    yrs = bt[bt["fy"].isin(fys)].dropna(subset=["c"])
    r["固定窓の損失日の平均損失(円/kW-日)"] = yrs.loc[yrs["c"] < 0, "c"].mean()
    r["順序_完全予見の窓が実行不能な日の比率"] = 1 - yrs["pf_order_ok"].astype(float).mean()
    r["順序_戦略cの窓が実行不能な日の比率"] = 1 - yrs["c_order_ok"].astype(float).mean()
    for s in "abc":
        r[f"図7.1_capture_{s}"] = r[f"図7.1_{s}(円/kW-年)"] / pf71
    fyt = pd.concat([fyt, pd.DataFrame([r])], ignore_index=True)
fyt.to_csv(OUT_FY, index=False, encoding="utf-8-sig")

# ============================================================
# 3. 季節別（年度×季節、FY2023-25 の季節、季節×風力三分位）
# ============================================================
# 風力三分位: analysis/17 §2 と同じ定義（FY2023-25 の24時間そろう日、季節内3年プール、≤1/3分位=小、≥2/3分位=大）
p17 = hp[(hp["ts"] >= "2023-04-01") & (hp["ts"] < "2026-04-01")].dropna(subset=["p_hokkaido"]).copy()
cnt = p17.groupby("day")["hour"].count()
p17 = p17[p17["day"].isin(cnt[cnt == 24].index)]
wind17 = p17.groupby("day")["wind_pre"].sum()
ter17 = pd.Series(index=wind17.index, dtype=object)
cuts = {}
for s, ms in SEASONS:
    w = wind17[wind17.index.month.isin(ms)]
    q = w.quantile([1 / 3, 2 / 3])
    cuts[s] = q
    ter17.loc[w.index] = np.select([w <= q.iloc[0], w >= q.iloc[1]], ["小", "大"], "中")
bt["ter"] = ter17.reindex(bt.index)


def season_row(df, kind, period, season, ter, n_fy):
    L = layers(df)
    LO = layers(df, "pf_ord", "c_ord")
    n = L["日数"]
    mu, sd = df["c"].mean(), df["c"].std()
    z = mu / sd
    tv_norm = mu * norm.cdf(z) + sd * norm.pdf(z) - mu          # 正規近似の時間価値（診断のみ）
    tv_real = df["c_pos"].mean() - mu                           # 実現の (II)（円/kW-日）
    am = df["pf_dis_am"] >= 2                                   # 完全予見の放電窓に朝6〜11時が2h以上入る日
    iii = df["pf"] - df["c_pos"]
    return {"区分": kind, "期間": period, "季節": season, "風力三分位": ter, "日数": n,
            "風力GWh/日": df["wind"].mean(),
            "PF(円/kW-日)": L["PF"] / n, "(I)本源的方策(円/kW-日)": L["I"] / n,
            "(II)休止(円/kW-日)": L["II"] / n, "(III)窓の選び直し(円/kW-日)": L["III"] / n,
            "capture率=(I)/PF": L["capture"], "(II)/PF": L["II_share"], "(III)/PF": L["III_share"],
            "PF年寄与(円/kW-年)": L["PF"] / n_fy, "(I)年寄与(円/kW-年)": L["I"] / n_fy,
            "(II)年寄与(円/kW-年)": L["II"] / n_fy, "(III)年寄与(円/kW-年)": L["III"] / n_fy,
            "固定窓で損失の日の比率": L["loss_day"],
            "固定窓の損失日の平均損失(円/kW-日)": df.loc[df["c"] < 0, "c"].mean(),
            "放電窓の一致(h/4h)": df["dis_overlap"].mean(), "充電窓の一致(h/4h)": df["chg_overlap"].mean(),
            "完全予見の放電_朝6-11時(h)": df["pf_dis_am"].mean(), "完全予見の放電_夕16-21時(h)": df["pf_dis_pm"].mean(),
            "朝6-11時に2h以上放電する日の比率": am.mean(),
            "朝放電日_放電窓の一致(h/4h)": df.loc[am, "dis_overlap"].mean(),
            "その他の日_放電窓の一致(h/4h)": df.loc[~am, "dis_overlap"].mean(),
            "朝放電日_(III)/PF": iii[am].sum() / df.loc[am, "pf"].sum() if am.any() else np.nan,
            "その他の日_(III)/PF": iii[~am].sum() / df.loc[~am, "pf"].sum(),
            "(III)のうち朝放電日の比率": iii[am].sum() / iii.sum(),
            "完全予見の充電_昼9-15時(h)": df["pf_chg_mid"].mean(), "完全予見の充電_夜0-5時(h)": df["pf_chg_night"].mean(),
            "順序_完全予見の窓が実行不能な日の比率": 1 - df["pf_order_ok"].astype(float).mean(),
            "順序_戦略cの窓が実行不能な日の比率": 1 - df["c_order_ok"].astype(float).mean(),
            "順序制約_PF(円/kW-日)": LO["PF"] / n, "順序制約_(I)(円/kW-日)": LO["I"] / n,
            "順序制約_(II)(円/kW-日)": LO["II"] / n, "順序制約_(III)(円/kW-日)": LO["III"] / n,
            "順序制約_capture率": LO["capture"], "順序制約_(III)/PF": LO["III_share"],
            "X_c平均(円/kW-日)": mu, "X_c標準偏差(円/kW-日)": sd, "X_c歪度": df["c"].skew(),
            "診断_正規近似の損失日の比率": norm.cdf(-z),
            "診断_正規近似の時間価値/実現の休止価値": tv_norm / tv_real if tv_real > 0 else np.nan}


com = bt.dropna(subset=["c"])
srows = []
for fy in FY_FULL:
    for s, _ in SEASONS:
        g = com[(com["fy"] == fy) & (com["season"] == s)]
        srows.append(season_row(g, "年度×季節", f"FY{fy}", s, "全体", 1))
now = com[com["fy"].isin(FY_NOW)]
assert now["ter"].notna().all() and len(now) == len(wind17), "FY2023-25 の標本が analysis/17 と一致しない"
for s, _ in SEASONS:
    g = now[now["season"] == s]
    srows.append(season_row(g, "FY2023-25×季節", "FY2023-25", s, "全体", 3))
    for t in TER:
        srows.append(season_row(g[g["ter"] == t], "FY2023-25×季節×風力三分位", "FY2023-25", s, t, 3))
srows.append(season_row(now, "FY2023-25×季節", "FY2023-25", "通年", "全体", 3))
st = pd.DataFrame(srows)
st.to_csv(OUT_SEASON, index=False, encoding="utf-8-sig")

# 頑健性2: 日次の層を風力に回帰（FY2023-25、季節別）
dctl = hp.groupby("day").agg(dem=("demand", "sum"), sol=("solar", "sum"), solc=("solar_curt", "sum"))
reg = now.join(pd.DataFrame({"dem": dctl["dem"] / 1000,
                             "sol_pre": (dctl["sol"].fillna(0) + dctl["solc"].fillna(0)) / 1000}))
reg = reg.assign(II=reg["c_pos"] - reg["c"], III=reg["pf"] - reg["c_pos"], fyc=reg["fy"].astype(str),
                 ym=reg.index.strftime("%Y-%m"), wkend=(reg.index.dayofweek >= 5).astype(int))
SPECS = [("(a) 年度FE", "{y} ~ wind + C(fyc)"),
         ("(b) 年月FE＋需要・太陽光・土日", "{y} ~ wind + dem + sol_pre + wkend + C(ym)")]
YS = [("pf", "完全予見粗利"), ("c", "(I)本源的方策"), ("II", "(II)休止"), ("III", "(III)窓の選び直し")]
rrows = []
for s, _ in SEASONS:
    g = reg[reg["season"] == s].sort_index()
    for spec, f in SPECS:
        for y, yname in YS:
            r_ = smf.ols(f.format(y=y), data=g).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
            rrows.append({"季節": s, "仕様": spec, "被説明変数(円/kW-日)": yname, "日数": int(r_.nobs),
                          "被説明変数の平均": g[y].mean(), "風力係数(per GWh/日)": r_.params["wind"],
                          "NW標準誤差": r_.bse["wind"], "t値": r_.tvalues["wind"], "p値": r_.pvalues["wind"]})
rt = pd.DataFrame(rrows)
rt.to_csv(OUT_REG, index=False, encoding="utf-8-sig")

# ============================================================
# 4. 表7.3 の再計算（analysis/17 §2 と同じコード）
# ============================================================
P3 = p17.pivot(index="day", columns="hour", values="p_hokkaido")
srt = np.sort(P3.to_numpy(), axis=1)
d3 = pd.DataFrame(index=P3.index)
d3["TB4h"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
d3["PF"] = np.maximum(0.0, (srt[:, -4:].sum(axis=1) * ETA - srt[:, :4].sum(axis=1)) * 1000) / 1000
d3["下限張り付き"] = (P3 <= 0.011).sum(axis=1)
split = p17.assign(low_split=(p17["p_hokkaido"] < p17["p_system"] - 0.01))
d3["安値分断"] = split.groupby("day")["low_split"].sum()
d3["wind_day"] = wind17
d3["month"] = d3.index.month

MS73 = {("夏", "小"): (10.89, 31.6, 0.14, 7.2), ("夏", "大"): (11.30, 33.8, 0.35, 10.7),
        ("冬", "小"): (7.30, 19.2, 0.02, 3.1), ("冬", "大"): (5.92, 15.3, 0.04, 8.3),
        ("不需要期", "小"): (10.61, 32.1, 0.62, 4.8), ("不需要期", "大"): (10.19, 31.6, 1.19, 9.2)}
MET = ["TB4h", "PF", "下限張り付き", "安値分断"]
MET_NAME = {"TB4h": "TB4h(円/kWh)", "PF": "完全予見粗利(円/kW-日)", "下限張り付き": "下限張り付き時間(h/日)",
            "安値分断": "安値分断(h/日)"}


def tercile_table(d, kind, season, assign=None):
    q = d["wind_day"].quantile([1 / 3, 2 / 3])
    ter = pd.Series(np.select([d["wind_day"] <= q.iloc[0], d["wind_day"] >= q.iloc[1]], ["小", "大"], "中"),
                    index=d.index)
    if assign is not None:
        ter.loc[assign[0]] = assign[1]
    out = []
    for t in TER:
        g = d[ter == t]
        r = {"区分": kind, "季節": season, "風力三分位": t, "日数": len(g),
             "風力GWh/日": g["wind_day"].mean() / 1000}
        for m in MET:
            r[MET_NAME[m]] = g[m].mean()
        ms = MS73.get((season, t))
        for k, m in enumerate(MET):
            r["原稿_" + MET_NAME[m]] = ms[k] if (ms is not None and kind == "本表（現データ）") else np.nan
        out.append(r)
    return out, q


t73, notes73 = [], []
for s, ms in SEASONS:
    d = d3[d3["month"].isin(ms)]
    o, q = tercile_table(d, "本表（現データ）", s)
    t73 += o
    # 三分位の境界に乗る日: (n−1)×k/3 が整数なら、その順位の日の値が分位点に一致し、≤ / ≥ の判定が丸めに依存する
    n = len(d)
    w_sorted = d["wind_day"].sort_values()
    for k, (lab_in, lab_out) in zip([1, 2], [("小", "中"), ("大", "中")]):
        pos = (n - 1) * k / 3
        if abs(pos - round(pos)) < 1e-9:
            day_b = w_sorted.index[int(round(pos))]
            notes73.append(f"{s}: {k}/3分位の境界日 {day_b.date()}（風力 {w_sorted.iloc[int(round(pos))]:.1f} MWh/日、"
                           f"分位点 {q.iloc[k - 1]:.6f}）")
            o2, _ = tercile_table(d, f"感応度: 境界日{day_b.date()}を{lab_out}に入れた場合", s,
                                  assign=(day_b, lab_out))
            t73 += o2
d78 = d3[d3["month"].isin([7, 8])]
o, _ = tercile_table(d78, "参考: 夏を7〜8月に限る（三分位は7〜8月内）", "夏(7-8月)")
t73 += o
t73 = pd.DataFrame(t73)
t73.to_csv(OUT_T73, index=False, encoding="utf-8-sig")

# ============================================================
# 5. 図: 年度別の積み上げ棒（左）と FY2023-25 の季節×風力三分位（右）。棒の上の数字は (I) の比率（%、記号は省く）
#    Word では本文幅15.5cm（6.1インチ）で載せるので、その大きさで描き、図中の文字は8.5〜9.5pt にする
# ============================================================
FIG_W = 6.1
FS_TICK, FS_LAB, FS_TTL, FS_LEG, FS_ANN = 8.5, 9.0, 9.5, 8.5, 8.5
fyp = fyt[fyt["年度"].str.match(r"FY\d{4}$")].copy()
fig, axes = plt.subplots(1, 2, figsize=(FIG_W, 3.5), layout="constrained", gridspec_kw={"width_ratios": [1, 1.12]})
fig.get_layout_engine().set(w_pad=0.03, wspace=0.04)
ax = axes[0]
x = np.arange(len(fyp))
I_, II_, III_ = (fyp["(I)本源的方策(円/kW-年)"].to_numpy() / 1e4, fyp["(II)休止(円/kW-年)"].to_numpy() / 1e4,
                 fyp["(III)窓の選び直し(円/kW-年)"].to_numpy() / 1e4)
kw = dict(width=0.62, edgecolor="white", linewidth=0.8)
ax.bar(x, I_, color=C_I, label="(I) 本源的方策の価値（戦略 c が前日に固定した窓）", **kw)
ax.bar(x, II_, bottom=I_, color=C_II, label="(II) 休止の価値", **kw)
ax.bar(x, III_, bottom=I_ + II_, color=C_III, hatch="////", label="(III) 窓の選び直しの価値", **kw)
for xi, tot, cap in zip(x, I_ + II_ + III_, fyp["capture率=(I)/PF"]):
    ax.text(xi, tot + 0.03, f"{cap * 100:.0f}", ha="center", va="bottom", fontsize=FS_ANN, color="#222222")
ax.set_xticks(x)
ax.set_xticklabels(fyp["年度"], rotation=45, ha="right", rotation_mode="anchor")
ax.set_xlim(-0.55, len(x) - 0.45)
ax.set_ylabel("完全予見粗利（万円/kW-年）", fontsize=FS_LAB, color=GRAY)
ax.set_ylim(0, (I_ + II_ + III_).max() * 1.12)
ax.set_title("年度別", fontsize=FS_TTL, pad=4)

ax = axes[1]
sub = st[st["区分"] == "FY2023-25×季節×風力三分位"]
xs, labs, k = [], [], 0
for s, _ in SEASONS:
    for t in TER:
        xs.append(k)
        labs.append(f"{t}")
        k += 1
    k += 0.4
xs = np.array(xs)
I2 = sub["(I)本源的方策(円/kW-日)"].to_numpy()
II2 = sub["(II)休止(円/kW-日)"].to_numpy()
III2 = sub["(III)窓の選び直し(円/kW-日)"].to_numpy()
ax.bar(xs, I2, color=C_I, **kw)
ax.bar(xs, II2, bottom=I2, color=C_II, **kw)
ax.bar(xs, III2, bottom=I2 + II2, color=C_III, hatch="////", **kw)
for xi, tot, cap in zip(xs, I2 + II2 + III2, sub["capture率=(I)/PF"]):
    ax.text(xi, tot + 0.4, f"{cap * 100:.0f}", ha="center", va="bottom", fontsize=FS_ANN, color="#222222")
ax.set_xticks(xs)
ax.set_xticklabels(labs)
# 季節名は三分位の目盛の下に置く
sec = ax.secondary_xaxis("bottom")
sec.set_xticks([xs[3 * j + 1] for j in range(len(SEASONS))], labels=[s for s, _ in SEASONS])
sec.tick_params(length=0, pad=16, labelsize=FS_LAB, colors="#222222")
sec.spines["bottom"].set_visible(False)
ax.set_xlim(xs[0] - 0.55, xs[-1] + 0.55)
ax.set_ylabel("完全予見粗利（円/kW-日）", fontsize=FS_LAB, color=GRAY)
ax.set_ylim(0, (I2 + II2 + III2).max() * 1.14)
ax.set_title("FY2023〜25 の季節×風力の三分位", fontsize=FS_TTL, pad=4)
for a in axes:
    a.grid(axis="y", color="#DDDDDD", lw=0.5)
    a.set_axisbelow(True)
    for sp in ["top", "right"]:
        a.spines[sp].set_visible(False)
    a.tick_params(colors=GRAY, labelsize=FS_TICK, length=2.5, pad=2)
fig.legend(handles=axes[0].get_legend_handles_labels()[0], loc="outside upper center", ncol=2, fontsize=FS_LEG,
           frameon=False, handlelength=1.6, columnspacing=1.5, borderaxespad=0.1)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(OUT_FIG, dpi=300, bbox_inches="tight", pad_inches=0.03)

# ============================================================
# 6. 表示
# ============================================================
pd.set_option("display.width", 260)
pd.set_option("display.max_columns", 40)
print("=== 年度別の3層（円/kW-年、共通標本）===")
print(fyt[["年度", "日数_共通標本", "完全予見粗利PF(円/kW-年)", "(I)本源的方策(円/kW-年)", "(II)休止(円/kW-年)",
           "(III)窓の選び直し(円/kW-年)", "(II)+(III)完全情報の価値(円/kW-年)", "capture率=(I)/PF", "(II)/PF", "(III)/PF",
           "固定窓で損失の日の比率", "固定窓で損失の日数", "固定窓の損失日の平均損失(円/kW-日)"]]
      .round(3).to_string(index=False))
print("\n=== 頑健性1: 充放電の順序を課した厳密解（円/kW-年）===")
print(fyt[["年度", "順序_完全予見の窓が実行不能な日の比率", "順序_戦略cの窓が実行不能な日の比率", "順序制約_PF(円/kW-年)",
           "順序制約_(I)(円/kW-年)", "順序制約_capture率", "順序制約_(II)/PF", "順序制約_(III)/PF",
           "順序制約_PF/ランク法PF−1", "順序制約_(I)/ランク法(I)−1"]].round(4).to_string(index=False))
print("\n=== 図7.1 と同じ集計の capture率（分母は全日の PF）===")
print(fyt[["年度", "日数_図7.1", "図7.1_PF(円/kW-年)", "図7.1_capture_a", "図7.1_capture_b", "図7.1_capture_c",
           "検算_安定ソート版c−19版c(円/kW-年)", "検算_窓が違う日数",
           "検算_capture_a_安定ソート", "検算_capture_a_逆順の安定ソート"]].round(4).to_string(index=False))
fyonly = fyt[fyt["年度"].str.match(r"FY\d{4}$")]
print(f"  戦略c（図7.1集計）FY2016-25 の範囲: {fyonly['図7.1_capture_c'].min():.3f}〜{fyonly['図7.1_capture_c'].max():.3f}")
print("\n=== FY2023-25 の季節別・季節×風力三分位（円/kW-日、年寄与は円/kW-年）===")
cols = ["季節", "風力三分位", "日数", "風力GWh/日", "PF(円/kW-日)", "(I)本源的方策(円/kW-日)", "(II)休止(円/kW-日)",
        "(III)窓の選び直し(円/kW-日)", "capture率=(I)/PF", "(III)/PF", "PF年寄与(円/kW-年)", "(I)年寄与(円/kW-年)",
        "(II)年寄与(円/kW-年)", "(III)年寄与(円/kW-年)", "固定窓で損失の日の比率", "固定窓の損失日の平均損失(円/kW-日)"]
print(st[st["期間"] == "FY2023-25"][cols].round(3).to_string(index=False))
cols2 = ["季節", "風力三分位", "放電窓の一致(h/4h)", "充電窓の一致(h/4h)", "朝6-11時に2h以上放電する日の比率",
         "朝放電日_放電窓の一致(h/4h)", "その他の日_放電窓の一致(h/4h)", "朝放電日_(III)/PF", "その他の日_(III)/PF",
         "(III)のうち朝放電日の比率", "完全予見の充電_昼9-15時(h)", "完全予見の充電_夜0-5時(h)"]
print(st[st["期間"] == "FY2023-25"][cols2].round(3).to_string(index=False))
cols3 = ["季節", "風力三分位", "順序_完全予見の窓が実行不能な日の比率", "順序_戦略cの窓が実行不能な日の比率",
         "順序制約_PF(円/kW-日)", "順序制約_(I)(円/kW-日)", "順序制約_(III)(円/kW-日)", "順序制約_capture率", "順序制約_(III)/PF"]
print("（頑健性1: 順序制約つき）")
print(st[st["期間"] == "FY2023-25"][cols3].round(3).to_string(index=False))
sx = st[(st["区分"] == "FY2023-25×季節") & (st["風力三分位"] == "全体")].set_index("季節")
for s_ref in ["夏", "不需要期"]:
    cap_ref = sx.loc[s_ref, "capture率=(I)/PF"]
    cf = (sx.loc["通年", "(I)年寄与(円/kW-年)"] - sx.loc["冬", "(I)年寄与(円/kW-年)"]
          + cap_ref * sx.loc["冬", "PF年寄与(円/kW-年)"]) / sx.loc["通年", "PF年寄与(円/kW-年)"]
    print(f"  冬の capture率が{s_ref}並み（{cap_ref:.3f}）なら通年の capture率は {cf:.3f}"
          f"（実際 {sx.loc['通年', 'capture率=(I)/PF']:.3f}）")
print(f"  冬の PF 年寄与の比率 {sx.loc['冬', 'PF年寄与(円/kW-年)'] / sx.loc['通年', 'PF年寄与(円/kW-年)']:.3f}、"
      f"(II)+(III) の年寄与に占める冬の比率 "
      f"{(sx.loc['冬', '(II)年寄与(円/kW-年)'] + sx.loc['冬', '(III)年寄与(円/kW-年)']) / (sx.loc['通年', '(II)年寄与(円/kW-年)'] + sx.loc['通年', '(III)年寄与(円/kW-年)']):.3f}")
print("\n=== 頑健性2: 日次の層を風力に回帰（FY2023-25、円/kW-日 per GWh/日、Newey-West 7ラグ）===")
print(rt.round(3).to_string(index=False))
print("\n=== 年度×季節の capture率（(I)/PF）===")
print(st[st["区分"] == "年度×季節"].pivot(index="期間", columns="季節", values="capture率=(I)/PF")
      [["夏", "冬", "不需要期"]].round(3).to_string())
dg = st[st["区分"] == "年度×季節"]["診断_正規近似の時間価値/実現の休止価値"]
print(f"\n診断（評価には使わない）: 正規近似の時間価値／実現の休止価値（年度×季節 {dg.notna().sum()} セル）"
      f" 中央値 {dg.median():.2f}、四分位 {dg.quantile(0.25):.2f}〜{dg.quantile(0.75):.2f}、範囲 {dg.min():.2f}〜{dg.max():.2f}")
dgs = st[st["区分"] == "年度×季節"]
print(f"  X_c の歪度（年度×季節30セル）中央値 {dgs['X_c歪度'].median():.2f}、正のセル {int((dgs['X_c歪度'] > 0).sum())}；"
      f" 損失日の比率 実際の中央値 {dgs['固定窓で損失の日の比率'].median():.3f}、正規近似の中央値 {dgs['診断_正規近似の損失日の比率'].median():.3f}；"
      f" 正規近似が損失日を多く見積もるセル {int((dgs['診断_正規近似の損失日の比率'] > dgs['固定窓で損失の日の比率']).sum())}")
print("\n=== 表7.3 の再計算（analysis/17 §2 と同じ定義）===")
print(t73.round(3).to_string(index=False))
print("\n".join(notes73) if notes73 else "三分位の境界に乗る日はない")
main = t73[t73["区分"] == "本表（現データ）"].set_index(["季節", "風力三分位"])
for s, _ in SEASONS:
    lo, hi = main.loc[(s, "小")], main.loc[(s, "大")]
    print(f"  {s}: 完全予見粗利 大/小 {hi['完全予見粗利(円/kW-日)'] / lo['完全予見粗利(円/kW-日)'] - 1:+.1%}、"
          f"TB4h {lo['TB4h(円/kWh)']:.2f}→{hi['TB4h(円/kWh)']:.2f}、安値分断 大/小 {hi['安値分断(h/日)'] / lo['安値分断(h/日)']:.2f}倍")
m78 = t73[t73["季節"] == "夏(7-8月)"].set_index("風力三分位")
print(f"  夏7〜8月: TB4h {m78.loc['小', 'TB4h(円/kWh)']:.2f}→{m78.loc['大', 'TB4h(円/kWh)']:.2f}、完全予見粗利 "
      f"{m78.loc['大', '完全予見粗利(円/kW-日)'] / m78.loc['小', '完全予見粗利(円/kW-日)'] - 1:+.1%}")
print(f"\nsaved: {OUT_FY}\n       {OUT_SEASON}\n       {OUT_REG}\n       {OUT_T73}\n       {OUT_FIG}")
