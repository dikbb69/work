#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""価格モデルの供給曲線と感応度: ベースロード一律シフトの分解、下限価格の機構の検証、九州の原子力係数（ゼミ指摘2・3）

手法:
  (a) 仕様A（13: p = max{0.01, g(net;季節)+μ(季節,時刻)}、net＝需要−太陽光−風力−原子力（制御前））の
      供給曲線 g と代表時刻（3時・12時・18時）の g+μ を季節別に描き、FY2023〜25 パスの純需要の分布
      （現状／泊3号 −821MW＝912MW×0.9／泊2基相当＝泊3号×2 −1,642MW／風力2倍）を重ねる。参考に泊1〜3号の全基
      （(579+579+912)MW×0.9＝1,863MW）も計算する。
      実績の純需要20分位ビン（通年）と季節別10分位ビンの価格中央値と傾き（円/kWh per 100MW）を表にする。
      仕様A は各季節の最下位ビンの中心（g の推定範囲の下端）より下を 0.01円 とするので、その外側の時間の割合と、
      実績の最小値（FY2023〜25、季節別）をも下回る時間の割合を出す。
  (b) ベースロードを一律に 0〜−2,000MW（100MW刻み＋821・1,642・1,863MW）動かし、仕様Aで季節別（夏7-9月・冬12-2月・
      不需要期3-6・10-11月）と年間の 完全予見粗利・上位4h平均・下位4h平均・TB4h・効率調整後スプレッド
      （0.85·上位−下位）・下限張り付き時間 を計算。日次の恒等式（稼働日）
        完全予見粗利/日 = 4·(0.85·上位 − 下位) = 3.4·上位 − 4·下位 = 3.4·TB4h − 0.6·下位
      から、Δ完全予見粗利 を「スプレッドの変化（3.4·ΔTB4h）」「往復損失の水準効果（−0.6·Δ下位）」
      「休止の切替（稼働・休止が入れ替わる日の差）」に分解する。失われる0.6kWhは充電時に下位4hの価格で買うので
      下位4hで評価するのが自然だが、頑健性に上位4hで評価する別分解（4·ΔTB4h と −0.6·Δ上位）も併記する。
      風力倍率 0.5〜3（泊なし／あり）も同じ枠組みで計算し、18_kwind_sweep.py（仕様B）の結果と照合するため
      仕様B（共通乱数）でも再計算する。
      上位4h・下位4h の時間での供給曲線の局所の傾き（100MW の有限差分）も季節別に出す。
  (c) 下限価格の機構: FY2023〜25 の実績価格を一様に δ 円（0〜10）下げ、0.01円で打ち切る場合と打ち切らない場合の
      完全予見粗利を比べる。さらに仕様Aの g の下端を、0.01円への段差の代わりに最下位の打ち切られていない8ビン
      （各季節の時間の約1割）の傾きで線形外挿した反実仮想を作り、「下限あり」「下限なし」でベースロードシフトと
      風力倍率への応答を比べる（段差の効果＝仕様A−外挿・下限あり、下限価格の効果＝外挿・下限あり−外挿・下限なし）。
  (d) 外部検証: 九州（FY2016〜25）の日次の 日平均価格・上位4h・下位4h・TB4h・効率調整後スプレッド・完全予見粗利/日・
      下限張り付き時間 を、季節×太陽光・風力・原子力 GWh/日、需要、FY・季節 FE に回帰（HC3 と Newey-West 14日）。
      頑健性に年月FE版（NW14）を併記。需要・原子力が欠測の日（九州 2019-03-12〜31 の20日）は除く
      （欠測を0として日合計すると需要0・原子力0の外れ値になるため。24_vol_verification.py は九州でこの20日を
      需要0のまま含んでいる）。北海道は泊が2012年5月以降停止しており、FY2016〜25 の原子力発電量が全日0のため
      同じ回帰では識別できない。
出力:
  figures/hokkaido/supply_curve_net_dist.png、figures/hokkaido/baseload_shift_response.png
  data/processed/supply_curve_bin_slopes.csv、data/processed/baseload_shift_response.csv、
  data/processed/floor_mechanism_check.csv、data/processed/kyushu_nuclear_coef.csv
限界:
  部分均衡・決定論（仕様A）。g と μ は FY2023〜25 の歴史的応答のまま固定（揚水・連系線・入札行動は内生化しない）。
  g の推定範囲より下の純需要での価格は識別できず、仕様Aの 0.01円 への段差と線形外挿は両端の仮定にすぎない
  （冬の最下位ビンの下半分の実績14時間の価格中央値は1.08円で、段差に近い急な低下を示すが、時間数が少ない）。
  ベースロードの一律シフトは泊の出力を一定とみなす近似（定期検査・負荷追従は無視）。
  九州の原子力の変動は主に定期検査による計画停止で、季節FE・需要で統制しても停止時期の選択が残りうる。
  九州の需要は北海道の約2.8倍（FY2016〜25 平均 9,786MW 対 3,457MW）なので、1GWh/日あたりの係数の大きさは北海道に
  移せない（向きの比較に使う）。線形外挿・下限なしは負の価格が際限なく深くなる仮定で、下限価格の効果の上限側の値。
"""
import contextlib
import io
import logging
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib import font_manager
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
          "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)   # 見つからないフォントの警告を抑止

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
PROC = os.path.join(ROOT, "data", "processed")
GRAY = "#595959"
INK = "#1a1a1a"

# ---------- 13 をモデル部品として読み込む（13 が hokkaido_cf_series.csv を上書きしないよう to_csv を無効化） ----------
ns = {"__file__": os.path.join(HERE, "13_price_process_v1.py"), "__name__": "pp_v1"}
_to_csv = pd.DataFrame.to_csv
pd.DataFrame.to_csv = lambda *a, **k: None
try:
    with contextlib.redirect_stdout(io.StringIO()):
        exec(open(os.path.join(HERE, "13_price_process_v1.py"), encoding="utf-8").read(), ns)
finally:
    pd.DataFrame.to_csv = _to_csv

GA, ADJ_A = ns["GA"], ns["ADJ_A"]
predict_A, simulate_B = ns["predict_A"], ns["simulate_B"]
K_WIND_NOW = ns["K_WIND_NOW"]            # 万kW
ETA = 0.85
FLOOR = 0.01
TOMARI = 912_000 * 0.9 / 1000            # 820.8 MW（泊3号 91.2万kW×稼働率90%）
TOMARI2 = 2 * TOMARI                     # 1,641.6 MW（2基相当＝泊3号×2。10/5 ゼミの想定）
TOMARI_ALL = (579_000 * 2 + 912_000) * 0.9 / 1000   # 1,863 MW（泊1〜3号の全基、稼働率90%）
MULTS = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
SHIFTS = sorted(set(range(0, 2001, 100)) | {TOMARI, TOMARI2, TOMARI_ALL})
CAPTURE, CHARGE_COST = 0.81, 4 * 365 * 1.2   # 1,752 円/kW-年
C_REQ, KP_CAP = 34_500, 12_500               # 8.4 の標準ケース（θ* 3.55 の起点）
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "不需要期", 4: "不需要期", 5: "不需要期", 6: "不需要期", 10: "不需要期", 11: "不需要期"}
RS = ["夏", "冬", "不需要期"]
MODEL_SEASON = {0: "冬（12〜2月）", 1: "春（3〜5月）", 2: "夏（6〜8月）", 3: "秋（9〜11月）"}

# ---------- FY2023〜25 パス（24時間そろった日） ----------
e = ns["est"].sort_values("ts").reset_index(drop=True).copy()
e["hour"] = e["ts"].dt.hour
cnt = e.groupby("day")["hour"].transform("count")
e = e[cnt == 24].reset_index(drop=True)
N_DAYS = e["day"].nunique()
assert len(e) == N_DAYS * 24
SEAS = e["season"].to_numpy()
MU = ADJ_A.reindex(pd.MultiIndex.from_arrays([SEAS, e["hour"].to_numpy()])).fillna(0).to_numpy()
DAYS = pd.DatetimeIndex(e["day"].to_numpy().reshape(N_DAYS, 24)[:, 0])
FY_D = np.asarray(DAYS.year - (DAYS.month < 4).astype(int))
RS_D = np.asarray(pd.Series(DAYS.month).map(SEASON_MAP))
N_FY = len(np.unique(FY_D))
NET0 = e["net"].to_numpy()
CFW = e["cf_wind"].to_numpy()
print(f"FY2023〜25 パス: {N_DAYS}日（{N_FY}年度）、現行風力 {K_WIND_NOW:.0f}万kW")

# ---------- 供給曲線の下端の扱い（仕様A／線形外挿） ----------
X0 = {s: GA[s][0][0] for s in range(4)}     # g の推定範囲の下端（最下位ビンの中心）。仕様A はこれより下を 0.01円
XMIN = {s: NET0[SEAS == s].min() for s in range(4)}   # 実績の純需要の最小値（季節別）
EXT = {}
for s in range(4):
    x, y = GA[s]
    i0 = int(np.argmax(y > FLOOR + 0.001))      # 最初の打ち切られていないビン
    slope = np.polyfit(x[i0:i0 + 8], y[i0:i0 + 8], 1)[0]
    EXT[s] = (x[i0], y[i0], slope)


def g_curve(net, season, mode):
    """mode='A': 13 と同じ（左端 0.01円・右端は最上位ビンの値）。mode='ext': 下端を線形外挿（打ち切りなし）"""
    out = np.empty(len(net))
    for s in range(4):
        m = season == s
        x, y = GA[s]
        if mode == "A":
            out[m] = np.interp(net[m], x, y, left=FLOOR, right=y[-1])
        else:
            xa, ya, sl = EXT[s]
            v = np.interp(net[m], x, y, right=y[-1])
            lo = net[m] < xa
            v[lo] = ya + sl * (net[m][lo] - xa)
            out[m] = v
    return out


def price(net, variant):
    if variant == "仕様A":
        return np.maximum(np.maximum(g_curve(net, SEAS, "A"), FLOOR) + MU, FLOOR)
    if variant == "外挿・下限あり":
        return np.maximum(np.maximum(g_curve(net, SEAS, "ext"), FLOOR) + MU, FLOOR)
    if variant == "外挿・下限なし":
        return g_curve(net, SEAS, "ext") + MU
    if variant == "仕様B":
        return simulate_B(e.assign(net=net))
    raise ValueError(variant)


# 自前の仕様A が 13 の predict_A と一致することを確認
assert np.allclose(price(NET0, "仕様A"), predict_A(e)), "仕様A の再実装が 13 と一致しない"
assert np.allclose(price(NET0 - TOMARI, "仕様A"), predict_A(e.assign(net=NET0 - TOMARI)))


def day_stats(p, net):
    P = p.reshape(N_DAYS, 24)
    order = np.argsort(P, axis=1)
    srt = np.take_along_axis(P, order, 1)
    top, bot = srt[:, -4:].mean(1), srt[:, :4].mean(1)
    x = 3.4 * top - 4 * bot
    nm = net.reshape(N_DAYS, 24)
    return {"top": top, "bot": bot, "x": x, "pf": np.maximum(0.0, x),
            "floor": (P <= FLOOR + 0.001).sum(1), "order": order, "net": nm}


def local_slope(net, variant, st):
    """上位4h・下位4h の時間の局所の傾き（円/kWh per 100MW、純需要を 100MW 下げたときの価格低下）"""
    if variant == "仕様B":
        return np.nan, np.nan
    dp = (price(net, variant) - price(net - 100.0, variant)).reshape(N_DAYS, 24)
    s_top = np.take_along_axis(dp, st["order"][:, -4:], 1).mean(1)
    s_bot = np.take_along_axis(dp, st["order"][:, :4], 1).mean(1)
    return s_top, s_bot


def out_of_support(net):
    return np.concatenate([net[SEAS == s] < X0[s] for s in range(4)]).mean() * 100, \
        {s: (net[SEAS == s] < X0[s]) for s in range(4)}


def regime_share_B(net, st):
    """仕様B の上位4h・下位4h の時間のうち連系レジーム（価格＝観測システムプライス、北海道の純需要に反応しない）の割合"""
    pr = ns["regime_probs"](net, SEAS)
    u = np.random.default_rng(20260728).random(len(net))          # simulate_B と同じ共通乱数
    reg = np.select([u < pr[:, 0], u < pr[:, 0] + pr[:, 1]], [0, 1], default=2).reshape(N_DAYS, 24)
    return {"連系レジームの割合_上位4h(仕様B)": (np.take_along_axis(reg, st["order"][:, -4:], 1) == 1).mean(1),
            "連系レジームの割合_下位4h(仕様B)": (np.take_along_axis(reg, st["order"][:, :4], 1) == 1).mean(1),
            "安値分断レジームの割合_全時間(仕様B)": (reg == 0).mean(1),
            "連系レジームの割合_全時間(仕様B)": (reg == 1).mean(1)}


def summarize(st0, st1, net1, variant, slopes, extra=None):
    """季節別・年間の集計と Δ完全予見粗利 の分解（st0 が基準）"""
    both = (st0["x"] > 0) & (st1["x"] > 0)
    spread = np.where(both, 3.4 * ((st1["top"] - st1["bot"]) - (st0["top"] - st0["bot"])), 0.0)
    level = np.where(both, -0.6 * (st1["bot"] - st0["bot"]), 0.0)
    # 別分解（失われる0.6kWhを上位4hで評価）: 3.4·上位−4·下位 = 4·TB4h − 0.6·上位
    spread_t = np.where(both, 4.0 * ((st1["top"] - st1["bot"]) - (st0["top"] - st0["bot"])), 0.0)
    level_t = np.where(both, -0.6 * (st1["top"] - st0["top"]), 0.0)
    dpf = st1["pf"] - st0["pf"]
    switch = dpf - spread - level
    oos_h = np.zeros(N_DAYS * 24, dtype=bool)
    below_min_h = np.zeros(N_DAYS * 24, dtype=bool)
    for s in range(4):
        m = SEAS == s
        oos_h[m] = net1[m] < X0[s]
        below_min_h[m] = net1[m] < XMIN[s]
    oos_d = oos_h.reshape(N_DAYS, 24).mean(1)
    bmin_d = below_min_h.reshape(N_DAYS, 24).mean(1)
    s_top, s_bot = slopes
    rows = []
    for sea in ["年間"] + RS:
        m = np.ones(N_DAYS, bool) if sea == "年間" else (RS_D == sea)
        per_fy = lambda v: pd.Series(v[m]).groupby(FY_D[m]).sum().mean()   # 円/kW-年（季節は年間への寄与）
        rows.append({
            "季節": sea, "日数/年": m.sum() / N_FY,
            "完全予見粗利": per_fy(st1["pf"]),
            "Δ完全予見粗利": per_fy(dpf),
            "うちスプレッドの変化(3.4ΔTB4h)": per_fy(spread),
            "うち往復損失の水準効果(−0.6Δ下位)": per_fy(level),
            "うち休止の切替": per_fy(switch),
            "別分解_スプレッドの変化(4ΔTB4h)": per_fy(spread_t),
            "別分解_往復損失の水準効果(−0.6Δ上位)": per_fy(level_t),
            "上位4h平均": st1["top"][m].mean(), "下位4h平均": st1["bot"][m].mean(),
            "TB4h平均": (st1["top"] - st1["bot"])[m].mean(),
            "TB4h中央値": np.median((st1["top"] - st1["bot"])[m]),
            "効率調整後スプレッド(0.85上位−下位)": (ETA * st1["top"] - st1["bot"])[m].mean(),
            "下限張り付き時間(h/年)": per_fy(st1["floor"].astype(float)),
            "稼働日の割合": (st1["x"] > 0)[m].mean(),
            "推定範囲外の時間の割合(%)": oos_d[m].mean() * 100,
            "実績の最小値より下の時間の割合(%)": bmin_d[m].mean() * 100,
            "傾き_上位4h(円/kWh per 100MW)": np.nanmean(s_top[m]) if np.ndim(s_top) else np.nan,
            "傾き_下位4h(円/kWh per 100MW)": np.nanmean(s_bot[m]) if np.ndim(s_bot) else np.nan,
            **{k: v[m].mean() for k, v in (extra or {}).items()},
        })
    return rows


# ====================================================================
# (b) ベースロード一律シフトと風力倍率
# ====================================================================
VARIANTS = ["仕様A", "外挿・下限あり", "外挿・下限なし", "仕様B"]
records = []
for var in VARIANTS:
    st_base = day_stats(price(NET0, var), NET0)
    # ベースロード
    for sh in SHIFTS:
        net1 = NET0 - sh
        st1 = day_stats(price(net1, var), net1)
        sl = local_slope(net1, var, st1)
        ex = regime_share_B(net1, st1) if var == "仕様B" else None
        for r in summarize(st_base, st1, net1, var, sl, ex):
            records.append({"系列": "ベースロード", "モデル": var, "ベースロード減(MW)": round(sh, 1),
                            "風力倍率": 1.0, "泊": "—", "基準": "現状（シフト0）", **r})
    # 風力倍率（泊なし／泊3号あり）
    for tom_lab, tom in (("なし", 0.0), ("泊3号", TOMARI)):
        net_ref = NET0 - tom
        st_ref = day_stats(price(net_ref, var), net_ref)
        for m_ in MULTS:
            net1 = NET0 - (m_ - 1.0) * K_WIND_NOW * 1e4 * CFW / 1000 - tom
            st1 = day_stats(price(net1, var), net1)
            sl = local_slope(net1, var, st1)
            for r in summarize(st_ref, st1, net1, var, sl):
                records.append({"系列": "風力倍率", "モデル": var, "ベースロード減(MW)": round(tom, 1),
                                "風力倍率": m_, "泊": tom_lab,
                                "基準": f"風力1.0倍・泊{tom_lab}", **r})
res = pd.DataFrame(records)
ann = res["季節"] == "年間"
res["π実現可能(0)"] = np.where(ann, CAPTURE * res["完全予見粗利"] - CHARGE_COST, np.nan)
res["θ*(c_req3.45万・容量1.25万)"] = np.where(
    ann, (C_REQ - KP_CAP + CHARGE_COST) / (CAPTURE * res["完全予見粗利"]), np.nan)
res["K=0の参入余地(円/kW-年)"] = np.where(ann, res["π実現可能(0)"] + KP_CAP - C_REQ, np.nan)
num = res.select_dtypes("number").columns
out = res.copy()
out[num] = out[num].round(3)
out.to_csv(os.path.join(PROC, "baseload_shift_response.csv"), index=False)


def pick(var, series="ベースロード", sh=None, mult=1.0, tom="—", sea="年間"):
    q = (res["モデル"] == var) & (res["系列"] == series) & (res["季節"] == sea)
    if series == "ベースロード":
        q &= np.isclose(res["ベースロード減(MW)"], round(sh, 1))
    else:
        q &= np.isclose(res["風力倍率"], mult) & (res["泊"] == tom)
    return res[q].iloc[0]


print("\n=== (b) ベースロード一律シフト（仕様A、FY2023〜25 平均、円/kW-年・円/kWh） ===")
cols = ["季節", "完全予見粗利", "Δ完全予見粗利", "うちスプレッドの変化(3.4ΔTB4h)", "うち往復損失の水準効果(−0.6Δ下位)",
        "うち休止の切替", "上位4h平均", "下位4h平均", "TB4h平均", "効率調整後スプレッド(0.85上位−下位)",
        "下限張り付き時間(h/年)", "推定範囲外の時間の割合(%)", "実績の最小値より下の時間の割合(%)",
        "傾き_上位4h(円/kWh per 100MW)", "傾き_下位4h(円/kWh per 100MW)"]
for lab, sh in [("現状", 0), ("泊3号（−821MW）", TOMARI), ("泊2基相当（泊3号×2、−1,642MW）", TOMARI2),
                ("泊1〜3号の全基（−1,863MW）", TOMARI_ALL)]:
    q = (res["モデル"] == "仕様A") & (res["系列"] == "ベースロード") & np.isclose(res["ベースロード減(MW)"], round(sh, 1))
    print(f"--- {lab} ---")
    print(res.loc[q, cols].round(2).to_string(index=False))
print("\n年間の完全予見粗利（ベースロード減 0〜2,000MW、モデル別）:")
piv = res[(res["系列"] == "ベースロード") & ann].pivot(index="ベースロード減(MW)", columns="モデル", values="完全予見粗利")
print(piv[VARIANTS].round(0).to_string())
pk = piv["仕様A"].idxmax()
print(f"仕様A の山の頂点: ベースロード減 {pk:.0f}MW で {piv['仕様A'].max():,.0f} 円/kW-年")
print("仕様B の分解とレジーム構成（年間）:")
for lab, sh in [("現状", 0), ("泊3号", TOMARI), ("泊2基相当", TOMARI2), ("−2,000MW", 2000)]:
    r = pick("仕様B", sh=sh)
    print(f"  {lab}: 完全予見粗利 {r['完全予見粗利']:,.0f}（Δ{r['Δ完全予見粗利']:+,.0f}、スプレッド {r['うちスプレッドの変化(3.4ΔTB4h)']:+,.0f}・"
          f"水準 {r['うち往復損失の水準効果(−0.6Δ下位)']:+,.0f}）、上位4hのうち連系 {r['連系レジームの割合_上位4h(仕様B)'] * 100:.0f}%・"
          f"全時間のうち安値分断 {r['安値分断レジームの割合_全時間(仕様B)'] * 100:.0f}%・連系 {r['連系レジームの割合_全時間(仕様B)'] * 100:.0f}%")
for lab, sh in [("泊3号", TOMARI), ("泊2基相当", TOMARI2), ("泊全基", TOMARI_ALL)]:
    r = pick("仕様A", sh=sh)
    print(f"{lab}: Δ={r['Δ完全予見粗利']:+.0f}（スプレッド {r['うちスプレッドの変化(3.4ΔTB4h)']:+.0f}・"
          f"水準 {r['うち往復損失の水準効果(−0.6Δ下位)']:+.0f}・切替 {r['うち休止の切替']:+.0f}）、"
          f"水準効果の比率 {r['うち往復損失の水準効果(−0.6Δ下位)'] / r['Δ完全予見粗利'] * 100:.0f}%、"
          f"別分解（上位で評価）スプレッド {r['別分解_スプレッドの変化(4ΔTB4h)']:+.0f}・水準 {r['別分解_往復損失の水準効果(−0.6Δ上位)']:+.0f}、"
          f"π実現可能(0)={r['π実現可能(0)']:,.0f}、θ*={r['θ*(c_req3.45万・容量1.25万)']:.2f}、"
          f"参入余地={r['K=0の参入余地(円/kW-年)']:,.0f}")
print("季節別の分解（泊3号、下端の扱い別、円/kW-年。Δ／スプレッド／水準、TB4h 現状→泊3号）:")
for v in ["仕様A", "外挿・下限あり", "外挿・下限なし", "仕様B"]:
    parts = []
    for sea in ["年間"] + RS:
        r, r0_ = pick(v, sh=TOMARI, sea=sea), pick(v, sh=0, sea=sea)
        parts.append(f"{sea} {r['Δ完全予見粗利']:+.0f}／{r['うちスプレッドの変化(3.4ΔTB4h)']:+.0f}／"
                     f"{r['うち往復損失の水準効果(−0.6Δ下位)']:+.0f}（TB4h {r0_['TB4h平均']:.2f}→{r['TB4h平均']:.2f}）")
    print(f"  {v}: " + "、".join(parts))
for v in ["仕様A", "外挿・下限あり", "外挿・下限なし", "仕様B"]:
    print(f"  {v} 冬 2基相当: Δ {pick(v, sh=TOMARI2, sea='冬')['Δ完全予見粗利']:+.0f}")
print("π実現可能(0) と θ*（泊3号・2基相当・全基、下端の扱い別）:")
for lab, sh in [("泊3号", TOMARI), ("泊2基相当", TOMARI2), ("泊全基", TOMARI_ALL)]:
    print(f"  {lab}: " + "、".join(f"{v} {pick(v, sh=sh)['π実現可能(0)']:,.0f}（θ* {pick(v, sh=sh)['θ*(c_req3.45万・容量1.25万)']:.2f}）"
                                  for v in VARIANTS))
r0 = pick("仕様A", sh=0)
print(f"現状: π実現可能(0)={r0['π実現可能(0)']:,.0f}、θ*={r0['θ*(c_req3.45万・容量1.25万)']:.2f}")

print("\n=== (b) 風力倍率（年間、円/kW-年）と 18_kwind_sweep.py（仕様B）の照合 ===")
kw = pd.read_csv(os.path.join(PROC, "kwind_sweep.csv"))
rows_kw = []
for tom_lab, kw_lab in (("なし", "なし"), ("泊3号", "あり")):
    for m_ in MULTS:
        rA, rB = pick("仕様A", "風力倍率", mult=m_, tom=tom_lab), pick("仕様B", "風力倍率", mult=m_, tom=tom_lab)
        k18 = kw[(kw["泊"] == kw_lab) & np.isclose(kw["K_wind倍率"], m_)]["PF価値(円/kW-年)"].iloc[0]
        rows_kw.append({"泊": tom_lab, "風力倍率": m_, "仕様A": rA["完全予見粗利"], "仕様A_Δ": rA["Δ完全予見粗利"],
                        "仕様A_スプレッド": rA["うちスプレッドの変化(3.4ΔTB4h)"],
                        "仕様A_水準": rA["うち往復損失の水準効果(−0.6Δ下位)"],
                        "仕様B": rB["完全予見粗利"], "18の仕様B": k18, "仕様B_スプレッド": rB["うちスプレッドの変化(3.4ΔTB4h)"],
                        "仕様B_水準": rB["うち往復損失の水準効果(−0.6Δ下位)"]})
kwc = pd.DataFrame(rows_kw)
_c = [c for c in kwc.columns if c not in ("泊", "風力倍率")]
print(kwc.assign(**{c: kwc[c].round(0) for c in _c}).to_string(index=False))
print("仕様B の再計算と 18 の最大差:", float((kwc["仕様B"].round(0) - kwc["18の仕様B"]).abs().max()), "円/kW-年")

# ====================================================================
# (c) 下限価格の機構
# ====================================================================
P_act = e["p_hokkaido"].to_numpy().reshape(N_DAYS, 24)


def pf_of(P):
    s = np.sort(P, 1)
    top, bot = s[:, -4:].mean(1), s[:, :4].mean(1)
    x = 3.4 * top - 4 * bot
    return x, top, bot


def per_fy(v):
    return pd.Series(v).groupby(FY_D).sum().mean()


x0, t0, b0 = pf_of(P_act)
fm = []
for d in np.arange(0, 10.01, 0.5):
    for clip in (True, False):
        Pd = np.maximum(P_act - d, FLOOR) if clip else P_act - d
        x1, t1, b1 = pf_of(Pd)
        both = (x0 > 0) & (x1 > 0)
        fm.append({"ブロック": "実績価格の一様シフト", "シナリオ": f"δ={d:.1f}円", "δ(円/kWh)": d,
                   "下限": "0.01円で打ち切り" if clip else "打ち切りなし",
                   "完全予見粗利": per_fy(np.maximum(0, x1)),
                   "Δ完全予見粗利": per_fy(np.maximum(0, x1) - np.maximum(0, x0)),
                   "うちスプレッドの変化(3.4ΔTB4h)": per_fy(np.where(both, 3.4 * ((t1 - b1) - (t0 - b0)), 0)),
                   "うち往復損失の水準効果(−0.6Δ下位)": per_fy(np.where(both, -0.6 * (b1 - b0), 0)),
                   "平行シフトの理論値(0.6·δ·日数)": per_fy(np.maximum(0, x0)) + 0.6 * d * N_DAYS / N_FY,
                   "下限張り付き時間(h/年)": per_fy((Pd <= FLOOR + 0.001).sum(1).astype(float))})
for k in (1.2, 0.8, 0.6):
    x1, _, _ = pf_of(np.maximum(P_act * k, FLOOR))
    fm.append({"ブロック": "実績価格の比例縮小（参考）", "シナリオ": f"p×{k}", "δ(円/kWh)": np.nan, "下限": "0.01円で打ち切り",
               "完全予見粗利": per_fy(np.maximum(0, x1)), "Δ完全予見粗利": per_fy(np.maximum(0, x1) - np.maximum(0, x0))})
fmd = pd.DataFrame(fm)
act = fmd[fmd["ブロック"] == "実績価格の一様シフト"]
pv = act.pivot(index="δ(円/kWh)", columns="下限", values="完全予見粗利")
pv["下限価格が削る価値（打ち切りなし−打ち切り）"] = pv["打ち切りなし"] - pv["0.01円で打ち切り"]
print("\n=== (c) 実績価格（FY2023〜25）を一様に δ 円下げたときの完全予見粗利（円/kW-年） ===")
print(pv.loc[[0, 1, 2, 3, 5, 8, 10]].round(0).to_string())
slope_nc = np.polyfit(pv.index, pv["打ち切りなし"], 1)[0]
print(f"打ち切りなしの傾き {slope_nc:.1f} 円/kW-年 per 円（理論値 0.6×{N_DAYS / N_FY:.2f}日 = {0.6 * N_DAYS / N_FY:.1f}）")
print("参考（日平均×365 の換算）: δ=0 で", round(np.maximum(0, x0).mean() * 365))

# モデル上の下端の扱いの比較
SCN = [("泊3号（−821MW）", "ベースロード", TOMARI, 1.0, "—"),
       ("泊2基相当（−1,642MW）", "ベースロード", TOMARI2, 1.0, "—"),
       ("泊1〜3号の全基（−1,863MW）", "ベースロード", TOMARI_ALL, 1.0, "—"),
       ("ベースロード −2,000MW", "ベースロード", 2000, 1.0, "—"),
       ("風力2倍", "風力倍率", None, 2.0, "なし"),
       ("風力3倍", "風力倍率", None, 3.0, "なし")]
print("\n=== (c) 供給曲線の下端の扱いと Δ完全予見粗利（年間、円/kW-年） ===")
for lab, ser, sh, m_, tom in SCN:
    rr = {v: pick(v, ser, sh=sh, mult=m_, tom=tom) for v in ["仕様A", "外挿・下限あり", "外挿・下限なし"]}
    for v, r in rr.items():
        fm.append({"ブロック": "モデルの下端の扱い", "シナリオ": lab, "δ(円/kWh)": np.nan, "下限": v,
                   "完全予見粗利": r["完全予見粗利"], "Δ完全予見粗利": r["Δ完全予見粗利"],
                   "うちスプレッドの変化(3.4ΔTB4h)": r["うちスプレッドの変化(3.4ΔTB4h)"],
                   "うち往復損失の水準効果(−0.6Δ下位)": r["うち往復損失の水準効果(−0.6Δ下位)"],
                   "下限張り付き時間(h/年)": r["下限張り付き時間(h/年)"]})
    cliff = rr["仕様A"]["Δ完全予見粗利"] - rr["外挿・下限あり"]["Δ完全予見粗利"]
    floor_eff = rr["外挿・下限あり"]["Δ完全予見粗利"] - rr["外挿・下限なし"]["Δ完全予見粗利"]
    fm.append({"ブロック": "モデルの下端の扱い（差）", "シナリオ": lab, "下限": "段差の効果（仕様A−外挿・下限あり）",
               "Δ完全予見粗利": cliff})
    fm.append({"ブロック": "モデルの下端の扱い（差）", "シナリオ": lab, "下限": "下限価格の効果（外挿・下限あり−外挿・下限なし）",
               "Δ完全予見粗利": floor_eff})
    print(f"{lab}: 仕様A {rr['仕様A']['Δ完全予見粗利']:+.0f}（スプレッド {rr['仕様A']['うちスプレッドの変化(3.4ΔTB4h)']:+.0f}）"
          f" ／ 外挿・下限あり {rr['外挿・下限あり']['Δ完全予見粗利']:+.0f}（{rr['外挿・下限あり']['うちスプレッドの変化(3.4ΔTB4h)']:+.0f}）"
          f" ／ 外挿・下限なし {rr['外挿・下限なし']['Δ完全予見粗利']:+.0f}（{rr['外挿・下限なし']['うちスプレッドの変化(3.4ΔTB4h)']:+.0f}）"
          f" → 段差 {cliff:+.0f}、下限価格 {floor_eff:+.0f}")
fmd = pd.DataFrame(fm)
num = fmd.select_dtypes("number").columns
fmd[num] = fmd[num].round(3)
fmd.to_csv(os.path.join(PROC, "floor_mechanism_check.csv"), index=False)

# ====================================================================
# (a) 供給曲線・分位ビンの傾き
# ====================================================================
h = e[["net", "p_hokkaido", "season", "ts"]].copy()
h["報告季節"] = h["ts"].dt.month.map(SEASON_MAP)
bins = []
h["bin"] = pd.qcut(h["net"], 20, labels=False)
gb = h.groupby("bin").agg(純需要中央値=("net", "median"), 価格中央値=("p_hokkaido", "median"),
                          下限張り付きの割合=("p_hokkaido", lambda x: (x <= FLOOR + 0.001).mean()))
gb["傾き(円/kWh per 100MW)"] = gb["価格中央値"].diff() / gb["純需要中央値"].diff() * 100
gb.insert(0, "区分", "実績・通年20分位")
bins.append(gb.reset_index())
for sea in RS:
    hh = h[h["報告季節"] == sea].copy()
    hh["bin"] = pd.qcut(hh["net"], 10, labels=False)
    g2 = hh.groupby("bin").agg(純需要中央値=("net", "median"), 価格中央値=("p_hokkaido", "median"),
                               下限張り付きの割合=("p_hokkaido", lambda x: (x <= FLOOR + 0.001).mean()))
    g2["傾き(円/kWh per 100MW)"] = g2["価格中央値"].diff() / g2["純需要中央値"].diff() * 100
    g2.insert(0, "区分", f"実績・{sea}10分位")
    bins.append(g2.reset_index())
# モデル g の下端（推定範囲の下端・外挿の傾き）
for s in range(4):
    xa, ya, sl = EXT[s]
    x, y = GA[s]
    mid = (x > np.quantile(x, 0.4)) & (x < np.quantile(x, 0.6))
    top = x >= np.quantile(x, 0.9)
    bins.append(pd.DataFrame([{
        "区分": f"仕様A g・{MODEL_SEASON[s]}", "bin": np.nan,
        "推定範囲の下端(MW)": x[0], "下端の価格(円/kWh)": y[0],
        "外挿の起点(MW)": xa, "起点の価格(円/kWh)": ya, "下端の傾き(円/kWh per 100MW)": sl * 100,
        "中位の傾き(円/kWh per 100MW)": np.polyfit(x[mid], y[mid], 1)[0] * 100,
        "上端の傾き(円/kWh per 100MW)": np.polyfit(x[top], y[top], 1)[0] * 100}]))
bdf = pd.concat(bins, ignore_index=True)
num = bdf.select_dtypes("number").columns
bdf[num] = bdf[num].round(3)
bdf.to_csv(os.path.join(PROC, "supply_curve_bin_slopes.csv"), index=False)
print("\n=== (a) 実績の純需要20分位ビン（FY2023〜25 通年）===")
print(gb.round(3).to_string())
print("\n仕様A の g の下端・中位・上端（季節別）:")
print(bdf[bdf["区分"].str.startswith("仕様A")].dropna(axis=1, how="all").round(2).to_string(index=False))
for sea in RS:
    t = bdf[bdf["区分"] == f"実績・{sea}10分位"]
    print(f"実績・{sea}: 傾き（下端→上端）", t["傾き(円/kWh per 100MW)"].round(2).tolist()[1:])
print("推定範囲外（最下位ビンの中心より下、仕様A で 0.01円）の時間の割合(%):")
print("（括弧内は実績の純需要の最小値をも下回る時間の割合(%)）")
for lab, net in [("現状", NET0), ("泊3号", NET0 - TOMARI), ("泊2基相当", NET0 - TOMARI2), ("泊全基", NET0 - TOMARI_ALL),
                 ("風力2倍", NET0 - K_WIND_NOW * 1e4 * CFW / 1000)]:
    print(f"  {lab}: 全時間 {np.mean([v for s in range(4) for v in (net[SEAS == s] < X0[s])]) * 100:.1f}"
          f"（{np.mean([v for s in range(4) for v in (net[SEAS == s] < XMIN[s])]) * 100:.1f}）、"
          + "、".join(f"{MODEL_SEASON[s][:1]} {(net[SEAS == s] < X0[s]).mean() * 100:.1f}"
                     f"（{(net[SEAS == s] < XMIN[s]).mean() * 100:.1f}）" for s in range(4)))
print("最下位ビンの中心より下にある実績の時間（現状）の価格（仕様Aは0.01円＋μ）:")
for s in range(4):
    m = (SEAS == s) & (NET0 < X0[s])
    print(f"  {MODEL_SEASON[s]}: 中心 {X0[s]:,.0f}MW・実績の最小値 {XMIN[s]:,.0f}MW、該当 {m.sum()} 時間、実績価格の中央値 "
          f"{np.median(e['p_hokkaido'].to_numpy()[m]):.2f}円（最下位ビンの中心の g {GA[s][1][0]:.2f}円）")

# ====================================================================
# (d) 九州の原子力係数（外部検証）
# ====================================================================
def build_daily(area, pcol):
    p = pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=[pcol]).copy()
    p["day"] = p["ts"].dt.normalize()
    p["hour"] = p["ts"].dt.hour
    c = p.groupby("day")["hour"].count()
    p = p[p["day"].isin(c[c == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    P = p.pivot(index="day", columns="hour", values=pcol)
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["日平均価格"] = P.mean(axis=1)
    d["上位4h"] = srt[:, -4:].mean(axis=1)
    d["下位4h"] = srt[:, :4].mean(axis=1)
    d["TB4h"] = d["上位4h"] - d["下位4h"]
    d["効率調整後スプレッド"] = ETA * d["上位4h"] - d["下位4h"]
    d["完全予見粗利/日"] = np.maximum(0, 3.4 * d["上位4h"] - 4 * d["下位4h"])
    d["下限張り付き時間"] = (P <= FLOOR + 0.001).sum(axis=1)
    g = p.groupby("day")
    d["solar"] = g["solar_pre"].sum() / 1000
    d["wind"] = g["wind_pre"].sum() / 1000
    d["nuclear"] = g["nuclear"].sum(min_count=24) / 1000   # 欠測を含む日は NaN にして除く（0 として合計しない）
    d["demand"] = g["demand"].sum(min_count=24) / 1000
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    return d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()


hk = build_daily("hokkaido", "p_hokkaido")
print(f"\n北海道 FY2016〜25 の原子力発電量: 最大 {hk['nuclear'].max():.1f} GWh/日（{len(hk)} 日、全日0: {bool((hk['nuclear'] == 0).all())}）"
      "→ 原子力の係数は識別できない")
ky = build_daily("kyushu", "p_kyushu")
print(f"九州: 需要・原子力が欠測で除いた日 {len(pd.date_range('2016-04-01', '2026-03-31')) - len(ky)} 日（FY2016〜25 の暦日のうち）")
n_gap = (ky.index.to_series().diff().dt.days > 1).sum()
print(f"九州: {len(ky)}日（欠落の区間 {n_gap} 箇所）、原子力 平均 {ky['nuclear'].mean():.1f}・年度内SD "
      f"{ky.groupby('fy')['nuclear'].std().mean():.1f} GWh/日")


def design(d, fe="fy_season"):
    X = pd.DataFrame(index=d.index)
    for s in RS:
        m = (d["season"] == s).astype(float)
        for src in ("solar", "wind", "nuclear"):
            X[f"{src}_{s}"] = d[src] * m
    X["demand"] = d["demand"]
    if fe == "fy_season":
        X = pd.concat([X, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                       pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    else:
        ym = d.index.year * 100 + d.index.month
        X = pd.concat([X, pd.get_dummies(ym, prefix="ym", drop_first=True).astype(float).set_index(d.index)], axis=1)
    return sm.add_constant(X)


YS = ["日平均価格", "上位4h", "下位4h", "TB4h", "効率調整後スプレッド", "完全予見粗利/日", "下限張り付き時間"]
SPECS = [("主仕様・HC3", "fy_season", "HC3", {}), ("主仕様・NW14", "fy_season", "HAC", {"maxlags": 14}),
         ("年月FE・NW14", "ym", "HAC", {"maxlags": 14})]
kc = []
for spec, fe, cov, kwds in SPECS:
    X = design(ky, fe)
    for y in YS:
        r = sm.OLS(ky[y], X).fit(cov_type=cov, cov_kwds=kwds) if kwds else sm.OLS(ky[y], X).fit(cov_type=cov)
        for s in RS:
            for src in ("solar", "wind", "nuclear"):
                k = f"{src}_{s}"
                kc.append({"エリア": "九州", "仕様": spec, "被説明変数": y, "季節": s,
                           "説明変数": {"solar": "太陽光", "wind": "風力", "nuclear": "原子力"}[src],
                           "係数(per GWh/日)": r.params[k], "SE": r.bse[k], "t": r.tvalues[k], "p値": r.pvalues[k],
                           "参考_係数×19.7GWh/日(泊3号相当、市場規模の違いは無視)": r.params[k] * TOMARI * 24 / 1000,
                           "n": int(r.nobs), "R2": r.rsquared})
kcd = pd.DataFrame(kc)
num = kcd.select_dtypes("number").columns
kcd[num] = kcd[num].round(4)
kcd.to_csv(os.path.join(PROC, "kyushu_nuclear_coef.csv"), index=False)


def star(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


print("\n=== (d) 九州 FY2016〜25: 原子力 1GWh/日あたりの係数（円/kWh、完全予見粗利/日は円/kW、下限張り付きは時間/日） ===")
nuc = kcd[kcd["説明変数"] == "原子力"].copy()
nuc["表示"] = nuc.apply(lambda r: f"{r['係数(per GWh/日)']:+.3f}{star(r['p値'])}", axis=1)
print(nuc.pivot_table(index=["被説明変数"], columns=["仕様", "季節"], values="表示", aggfunc="first")
      .reindex(YS).to_string())
print("（主仕様の SE: HC3 と NW14）")
for y in ["上位4h", "下位4h", "TB4h"]:
    a = nuc[(nuc["被説明変数"] == y)]
    print(" ", y, "、".join(f"{s} HC3 {a[(a['仕様'] == '主仕様・HC3') & (a['季節'] == s)]['SE'].iloc[0]:.3f}"
                           f"／NW {a[(a['仕様'] == '主仕様・NW14') & (a['季節'] == s)]['SE'].iloc[0]:.3f}" for s in RS))
print("北海道モデル（仕様A）の泊3号の効果を 1GWh/日あたりに換算（19.7GWh/日で割る）:")
for s in RS:
    r = pick("仕様A", sh=TOMARI, sea=s)
    r0s = pick("仕様A", sh=0, sea=s)
    gwh = TOMARI * 24 / 1000
    print(f"  {s}: 上位 {(r['上位4h平均'] - r0s['上位4h平均']) / gwh:+.3f}・下位 {(r['下位4h平均'] - r0s['下位4h平均']) / gwh:+.3f}"
          f"・TB4h {(r['TB4h平均'] - r0s['TB4h平均']) / gwh:+.3f}・完全予見粗利/日 {r['Δ完全予見粗利'] / r['日数/年'] / gwh:+.3f}")

# ====================================================================
# 図1: 供給曲線と純需要の分布
# ====================================================================
# 図の体裁: Word では本文幅15.5cm（6.1インチ）で載せるので、その大きさで描き、図中の文字は8.5〜9.5pt にする
FIG_W = 6.1
FS_TICK, FS_LAB, FS_TTL, FS_LEG, FS_ANN = 8.5, 9.0, 9.5, 8.5, 8.5
FIG_DPI = 300
SC_COL = {"現状": "#0079C2", "泊3号（−821MW）": "#D95B20", "泊2基相当（−1,642MW）": "#7A3E9D", "風力2倍": "#2E8B57"}
SC_LS = {"現状": "-", "泊3号（−821MW）": "--", "泊2基相当（−1,642MW）": ":", "風力2倍": "-."}
SC_NET = {"現状": NET0, "泊3号（−821MW）": NET0 - TOMARI, "泊2基相当（−1,642MW）": NET0 - TOMARI2,
          "風力2倍": NET0 - K_WIND_NOW * 1e4 * CFW / 1000}
HOURS = [(3, "3時", "--"), (12, "12時", ":"), (18, "18時", "-.")]
# 上段（上の2行）に季節別の供給曲線、下段（下の2行）に純需要の分布。各段の季節の並びは 冬・春／夏・秋
fig, axes = plt.subplots(4, 2, figsize=(FIG_W, 6.5), sharex=True, layout="constrained",
                         gridspec_kw={"height_ratios": [1.65, 1.65, 0.82, 0.82]})
fig.get_layout_engine().set(h_pad=0.03, w_pad=0.03, hspace=0.03, wspace=0.02)
POS = {0: (0, 0), 1: (0, 1), 2: (1, 0), 3: (1, 1)}
xgrid = np.linspace(-1500, 5200, 1341)
bins_h = np.arange(-1600, 5300, 100)
for s in range(4):
    r_, c_ = POS[s]
    ax, axd = axes[r_, c_], axes[2 + r_, c_]
    m = SEAS == s
    ax.scatter(NET0[m], e["p_hokkaido"].to_numpy()[m], s=0.8, color="#BDBDBD", alpha=0.35, lw=0, rasterized=True)
    ax.axvspan(xgrid[0], X0[s], color="#EEEEEE", zorder=0)
    sv = np.full(len(xgrid), s)
    gA = np.maximum(g_curve(xgrid, sv, "A"), FLOOR)
    ax.plot(xgrid, gA, color=INK, lw=1.6, zorder=5)
    gE = g_curve(xgrid, sv, "ext")
    lo = xgrid < EXT[s][0] + 1
    ax.plot(xgrid[lo], gE[lo], color="#8C8C8C", lw=1.1, ls=(0, (4, 1.6)), zorder=4)
    labs = [(gA[-1], "g", INK)]
    for hr, hl, ls in HOURS:
        muh = ADJ_A.get((s, hr), 0.0)
        ax.plot(xgrid, np.maximum(gA + muh, FLOOR), color="#4D4D4D", lw=0.9, ls=ls, zorder=4)
        labs.append((max(gA[-1] + muh, FLOOR), hl, GRAY))
    labs.sort(key=lambda t: t[0])
    ypos = [labs[0][0]]
    for yv, _, _ in labs[1:]:
        ypos.append(max(yv, ypos[-1] + 2.7))      # ラベルの重なりを避ける
    for (yv, tx, c), yp in zip(labs, ypos):
        ax.text(xgrid[-1] + 80, yp, "$g$" if tx == "g" else tx, fontsize=FS_ANN, color=c, va="center")
    ax.axhline(FLOOR, color="#999999", lw=0.6)
    ax.set_ylim(-6, 26)
    ax.set_title(MODEL_SEASON[s], fontsize=FS_TTL, pad=3)
    ax.text(X0[s] - 80, 25, "推定範囲外", fontsize=FS_ANN, color=GRAY, ha="right", va="top")
    for lab, net in SC_NET.items():
        hist, _ = np.histogram(net[m], bins=bins_h)
        axd.step(bins_h[:-1], hist / m.sum() * 100, where="post", color=SC_COL[lab], lw=1.1, ls=SC_LS[lab])
    axd.axvline(X0[s], color="#999999", lw=0.6)
    axd.text(0.015, 0.95, MODEL_SEASON[s][:1], transform=axd.transAxes, fontsize=FS_LAB, color="#333333", va="top")
    axd.set_ylim(0, 10.5)
    axd.set_yticks([0, 5, 10])
for a_ in axes.flat:
    a_.set_xlim(xgrid[0], xgrid[-1] + 820)
    a_.set_xticks([0, 2000, 4000])
    a_.grid(axis="y", color="#E3E3E3", lw=0.5)
    for sp in ["top", "right"]:
        a_.spines[sp].set_visible(False)
    a_.tick_params(colors=GRAY, labelsize=FS_TICK, length=2.5, pad=2)
for r_ in range(4):
    axes[r_, 1].tick_params(labelleft=False)
axes[1, 0].tick_params(labelbottom=True)
axes[1, 1].tick_params(labelbottom=True)
for c_ in range(2):
    axes[3, c_].set_xlabel("純需要（MW、制御前）", fontsize=FS_LAB, color=GRAY)
axes[0, 0].set_ylabel("価格（円/kWh）", fontsize=FS_LAB, color=GRAY)
axes[1, 0].set_ylabel("価格（円/kWh）", fontsize=FS_LAB, color=GRAY)
axes[2, 0].set_ylabel(" ", fontsize=FS_LAB)     # 下段の2行に共通の縦軸ラベルの場所（下で一つだけ置く）
axes[3, 0].set_ylabel(" ", fontsize=FS_LAB)
h1 = [Line2D([], [], color=INK, lw=1.6, label="$g$（供給曲線、仕様A）"),
      Line2D([], [], color="#4D4D4D", lw=0.9, ls="--", label="$g+\\mu$（線の右端に時刻）"),
      Line2D([], [], color="#8C8C8C", lw=1.1, ls=(0, (4, 1.6)), label="下端の線形外挿（下限なし）"),
      Line2D([], [], color="#A6A6A6", marker="o", ls="", ms=3, label="実績（FY2023〜25）")]
h2 = [Line2D([], [], color=SC_COL[k], lw=1.1, ls=SC_LS[k], label=f"純需要の分布：{k}") for k in SC_NET]
fig.legend(handles=h1, loc="outside upper center", ncol=2, fontsize=FS_LEG, frameon=False,
           handlelength=2.4, columnspacing=1.2, borderaxespad=0.2)
fig.legend(handles=h2, loc="outside lower center", ncol=2, fontsize=FS_LEG, frameon=False,
           handlelength=2.4, columnspacing=1.2, borderaxespad=0.2)
fig.canvas.draw()
_r = fig.canvas.get_renderer()
_bl = axes[1, 0].yaxis.label.get_window_extent(_r)
_p2, _p3 = axes[2, 0].get_position(), axes[3, 0].get_position()
fig.text((_bl.x0 + _bl.x1) / 2 / fig.bbox.width, (_p2.y0 + _p3.y1) / 2, "時間の割合（%／100MW）", rotation=90,
         ha="center", va="center", fontsize=FS_LAB, color=GRAY)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "supply_curve_net_dist.png"), dpi=FIG_DPI, bbox_inches="tight", pad_inches=0.03)
plt.close(fig)
print("\nsaved supply_curve_net_dist.png")

# ====================================================================
# 図2: ベースロード一律シフトへの応答
# ====================================================================
bl = res[res["系列"] == "ベースロード"].copy()
grid = sorted(set(range(0, 2001, 100)))
A_ = bl[bl["モデル"] == "仕様A"]
SE_COL = {"夏": "#D95B20", "冬": "#0079C2", "不需要期": "#2E8B57"}
SE_LS = {"夏": "-", "冬": "--", "不需要期": "-."}
SE_MK = {"夏": "o", "冬": "s", "不需要期": "^"}
# A〜F の6パネルを 3行×2列に並べる（A・B／C・D／E・F）
fig, axs = plt.subplots(3, 2, figsize=(FIG_W, 6.9), sharex=True, layout="constrained")
FS_TTL = 9.0
fig.get_layout_engine().set(h_pad=0.04, w_pad=0.04, hspace=0.05, wspace=0.04)
axA, axB, axC, axD, axE, axF = axs.flat
MK = dict(ms=2.8, lw=1.1)


def series(df, var, sea, col):
    d = df[(df["モデル"] == var) & (df["季節"] == sea)].sort_values("ベースロード減(MW)")
    d = d[d["ベースロード減(MW)"].isin(grid)]
    return d["ベースロード減(MW)"].to_numpy(), d[col].to_numpy()


def marks(ax, ytxt=None):
    for xv, lab, dx, ha in [(TOMARI, "泊3号", 20, "left"), (TOMARI2, "泊2基相当", -20, "right")]:
        ax.axvline(xv, color="#B0B0B0", lw=0.7, ls=":")
        if ytxt is not None:
            ax.text(xv + dx, ytxt, lab, fontsize=FS_ANN, color=GRAY, va="bottom", ha=ha)


# A: 年間の完全予見粗利（下端の扱い別）
ax = axA
VSTY = {"仕様A": (INK, "-", 1.6, "仕様A"), "外挿・下限あり": ("#595959", "--", 1.2, "線形外挿・下限あり"),
        "外挿・下限なし": ("#8C8C8C", ":", 1.4, "線形外挿・下限なし")}
for v, (c, ls, lw, lab) in VSTY.items():
    xs, ys = series(bl, v, "年間", "完全予見粗利")
    ax.plot(xs, ys, color=c, ls=ls, lw=lw, label=lab)
xs, yF = series(bl, "外挿・下限あり", "年間", "完全予見粗利")
_, yN = series(bl, "外挿・下限なし", "年間", "完全予見粗利")
ax.fill_between(xs, yF, yN, color="#E6E6E6", zorder=0)
ax.text(1350, 10500, "下限価格が\n削る価値", fontsize=FS_ANN, color=GRAY, ha="center", va="center")
marks(ax, 5050)
ax.set_ylim(5000, 15800)
ax.legend(fontsize=FS_LEG, frameon=False, loc="upper left", handlelength=2.2, borderaxespad=0.2)
ax.set_title("A. 年間の完全予見粗利", fontsize=FS_TTL, loc="left", pad=3)
ax.set_ylabel("円/kW-年", fontsize=FS_LAB, color=GRAY)

# B: 仕様A の Δ完全予見粗利の分解（年間）
ax = axB
d = A_[(A_["季節"] == "年間") & A_["ベースロード減(MW)"].isin(grid)].sort_values("ベースロード減(MW)")
xb = d["ベースロード減(MW)"].to_numpy()
lev, spr, tot = (d["うち往復損失の水準効果(−0.6Δ下位)"].to_numpy(), d["うちスプレッドの変化(3.4ΔTB4h)"].to_numpy(),
                 d["Δ完全予見粗利"].to_numpy())
ax.bar(xb, lev, width=70, color="#B8860B", label="往復損失の水準効果（$-0.6\\,\\Delta B$）")
ax.bar(xb, spr, width=70, color="#7A3E9D", hatch="////", edgecolor="white", lw=0, label="スプレッドの変化（$3.4\\,\\Delta(T-B)$）")
ax.plot(xb, tot, color=INK, marker="o", label="完全予見粗利の変化（合計）", **MK)
ax.axhline(0, color="#999999", lw=0.6)
marks(ax)
ax.set_ylim(-5300, 1950)
ax.set_yticks(range(-5000, 2000, 1000))
ax.legend(fontsize=FS_LEG, frameon=False, loc="lower left", handlelength=2.0, borderaxespad=0.2)
ax.set_title("B. 完全予見粗利の変化の分解（仕様A）", fontsize=FS_TTL, loc="left", pad=3)
ax.set_ylabel("円/kW-年", fontsize=FS_LAB, color=GRAY)

# C: 季節別の Δ完全予見粗利（仕様A）
ax = axC
for s in RS:
    xs, ys = series(bl, "仕様A", s, "Δ完全予見粗利")
    ax.plot(xs, ys, color=SE_COL[s], ls=SE_LS[s], marker=SE_MK[s], label=s, **MK)
xs, ys = series(bl, "仕様A", "年間", "Δ完全予見粗利")
ax.plot(xs, ys, color=INK, lw=1.5, label="年間")
xs, ys = series(bl, "外挿・下限あり", "冬", "Δ完全予見粗利")
ax.plot(xs, ys, color=SE_COL["冬"], ls=(0, (1, 1.5)), lw=1.0, label="冬（線形外挿・下限あり）")
ax.axhline(0, color="#999999", lw=0.6)
marks(ax)
ax.set_ylim(-2350, 1300)
ax.legend(fontsize=FS_LEG, frameon=False, loc="lower left", handlelength=2.2, borderaxespad=0.2)
ax.set_title("C. 季節別の完全予見粗利の変化（仕様A）", fontsize=FS_TTL, loc="left", pad=3)
ax.set_ylabel("円/kW-年", fontsize=FS_LAB, color=GRAY)

# D: 年間の上位4h・下位4h・TB4h・効率調整後スプレッド
ax = axD
for col, c, ls, lab in [("上位4h平均", INK, "-", "上位4時間 $T$"), ("下位4h平均", INK, "--", "下位4時間 $B$"),
                        ("TB4h平均", "#7A3E9D", "-", "TB4h（$T-B$）"),
                        ("効率調整後スプレッド(0.85上位−下位)", "#7A3E9D", "--", "$0.85\\,T-B$（効率調整後）")]:
    xs, ys = series(bl, "仕様A", "年間", col)
    ax.plot(xs, ys, color=c, ls=ls, lw=1.3, label=lab)
marks(ax)
ax.set_ylim(0, 22.5)
ax.legend(fontsize=FS_LEG, frameon=False, loc="upper right", handlelength=2.0, borderaxespad=0.2)
ax.set_title("D. 年間の価格指標（仕様A）", fontsize=FS_TTL, loc="left", pad=3)
ax.set_ylabel("円/kWh", fontsize=FS_LAB, color=GRAY)

# E: 季節別 TB4h
ax = axE
for s in RS:
    xs, ys = series(bl, "仕様A", s, "TB4h平均")
    ax.plot(xs, ys, color=SE_COL[s], ls=SE_LS[s], marker=SE_MK[s], label=s, **MK)
marks(ax)
ax.set_ylim(2.8, 9.8)
ax.legend(fontsize=FS_LEG, frameon=False, loc="lower left", handlelength=2.2, borderaxespad=0.2)
ax.set_title("E. 季節別の TB4h（仕様A）", fontsize=FS_TTL, loc="left", pad=3)
ax.set_ylabel("円/kWh", fontsize=FS_LAB, color=GRAY)

# F: 季節別 下限張り付き時間
ax = axF
for s in RS:
    xs, ys = series(bl, "仕様A", s, "下限張り付き時間(h/年)")
    ax.plot(xs, ys, color=SE_COL[s], ls=SE_LS[s], marker=SE_MK[s], label=s, **MK)
marks(ax)
ax.legend(fontsize=FS_LEG, frameon=False, loc="upper left", handlelength=2.2, borderaxespad=0.2)
ax.set_title("F. 季節別の下限張り付き時間（仕様A）", fontsize=FS_TTL, loc="left", pad=3)
ax.set_ylabel("時間/年", fontsize=FS_LAB, color=GRAY)

for ax in axs.flat:
    ax.set_xlim(-60, 2060)
    ax.set_xticks([0, 500, 1000, 1500, 2000])
    ax.tick_params(labelbottom=True)
    ax.grid(axis="y", color="#E3E3E3", lw=0.5)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(colors=GRAY, labelsize=FS_TICK, length=2.5, pad=2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}".replace("-", "−")))
axD.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
axE.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
for ax in axs[-1, :]:
    ax.set_xlabel("ベースロードの一律減（MW）", fontsize=FS_LAB, color=GRAY)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "baseload_shift_response.png"), dpi=FIG_DPI, bbox_inches="tight", pad_inches=0.03)
plt.close(fig)
print("saved baseload_shift_response.png")
print("saved baseload_shift_response.csv / floor_mechanism_check.csv / supply_curve_bin_slopes.csv / kyushu_nuclear_coef.csv")
