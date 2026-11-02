#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""簡素版のモデル: 蓄電池が増えると価格がどう変わるか（主、容量価格14,972円、2035・2040年）

蓄電池の量 K ごとに、
1. 時刻別の平均価格（上乗せ込み）
2. 日の安い4時間・高い4時間の平均と、東北の価格（同じ上乗せを足したもの）の安い4時間・高い4時間
3. 充電・放電した電気量を、その時間の価格の決まり方で分ける
   - 0.01円（北海道が余り、太陽光・風力を抑制）
   - 蓄電池が値を決める（充放電の後の量が価格の階段の区切りに止まり、蓄電池の入札で値が決まる）
   - 東北の価格（北本が混んでいない。北海道の価格＝東北の価格）
   - 北海道の火力（北海道へ受けられる量がいっぱい）
   - 北海道が安い（東北へ送れる量がいっぱい、または最低出力の帯）
4. 蓄電池0 と比べた、充電の電気の出どころ（抑制の減少、東北へ送る量の減少、東北から受ける量の増加、北海道の火力の増加）
5. 1kW の価値 π と、参入のしきい値（その年に建てる蓄電池の年あたりの建設費＋運転維持費＋託送等−κ×容量価格）
6. 確かめ: 同じ時間の充電と放電（蓄電池全体の運用を量ごとに決め直すので0のはず）
7. 残る抑制がどんな日に出るか（1日中ほぼ0.01円の日＝蓄電池の入札で決まる約0.011円を含む）
出力: data/processed/simple_price_response.csv、simple_price_response_hourly.csv、simple_price_response_sources.csv、figures/hokkaido/simple_price_response.png
FIG_ONLY=1 なら保存した結果から図だけ描き直す
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
from model import params as PR, simple as SM, merit as MO, entry as EN

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROC = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures", "hokkaido")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams["font.family"] = ["Hiragino Sans", "sans-serif"]
plt.rcParams["font.size"] = 10
BASE_P = 14_972.0
SC = PR.SCENARIOS["主"]
KS = (0.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 600.0, 800.0)
YEARS_SHOW = (2035, 2040)
REGIMES = ("0.01円（抑制）", "蓄電池が値を決める", "東北の価格", "北海道の火力（受電がいっぱい）", "北海道が安い（送電がいっぱい）")


def drop_before(y, case="上乗せ"):
    X = pd.read_csv(os.path.join(PROC, "simple_exit_years.csv"))
    return tuple(X[(X["場合"] == case) & (X["退出の年"] < y)]["号機"])


def _job(args):
    import warnings
    warnings.filterwarnings("ignore")
    y, K = args
    cal = SM.calibration("commit")
    I = MO.inputs_future(PR.scenario_year(y, SC), SC)
    T, _, st = SM.run_year(I, cal, Ks=[K], P_list=(BASE_P,), drop=drop_before(y), return_state=True)
    R, p, chg, dis = st["R"], st["p"], st["chg"], st["dis"]
    mu = float(st["info"]["μ"])
    p0, pT = R["p0"], R["pT"]
    fl = PR.FLOOR + 0.001
    bat = st["fixed"][0] if st.get("fixed") is not None else np.zeros_like(p0, bool)
    floor = (p <= fl) & ~bat
    toh = ~floor & ~bat & (np.abs(p0 - pT) < 1e-6)
    hi = ~floor & ~bat & (p0 > pT + 1e-6)
    lo = ~floor & ~bat & (p0 < pT - 1e-6)
    pT_mu = np.where(pT > fl, pT + mu, pT)                     # 東北の価格にも同じ上乗せが乗る
    low4 = lambda x: np.sort(x, 1)[:, :4].mean(1)
    high4 = lambda x: np.sort(x, 1)[:, -4:].mean(1)
    yrs = I["D"].shape[0] / 365.25
    g = R["g"].sum(2)
    exp, imp = np.maximum(R["X"], 0.0), np.maximum(-R["X"], 0.0)
    row = {"年": y, "K(万kW)": K, "μ(円/kWh)": mu, "π(円/kW-年)": float(T.iloc[0]["π(円/kW-年)"]),
           "参入のしきい値(円/kW-年)": EN.annual_cost(y) + PR.OM + PR.NET_FIX - PR.KAPPA_BATT * BASE_P,
           "安い4時間(円/kWh)": float(low4(p).mean()), "高い4時間(円/kWh)": float(high4(p).mean()),
           "東北 安い4時間(円/kWh)": float(low4(pT_mu).mean()), "東北 高い4時間(円/kWh)": float(high4(pT_mu).mean()),
           "充電(TWh)": float(chg.sum() / yrs / 1e6), "放電(TWh)": float(dis.sum() / yrs / 1e6),
           "抑制(TWh)": float(R["curt"].sum() / yrs / 1e6), "送電(TWh)": float(exp.sum() / yrs / 1e6), "受電(TWh)": float(imp.sum() / yrs / 1e6),
           "火力(TWh)": float(g.sum() / yrs / 1e6), "供給力不足(MWh/年)": float(R["short"].sum() / yrs),
           "打ち消し合う充電(TWh)": float(np.minimum(chg, dis / PR.ETA).sum() / yrs / 1e6),
           "正味の充電(TWh)": float(np.maximum(chg - dis / PR.ETA, 0.0).sum() / yrs / 1e6),
           "0.01円の時間への放電の比": float((dis * floor).sum() / dis.sum()) if dis.sum() > 0 else np.nan,
           "抑制のある日(日/年)": float((R["curt"].sum(1) > 1e-6).sum() / yrs),
           "抑制のうち1日中ほぼ0.01円の日の比": float(R["curt"][(p <= 0.0125).all(1)].sum() / R["curt"].sum()) if R["curt"].sum() > 0 else np.nan,
           "1日中ほぼ0.01円の日(日/年)": float((p <= 0.0125).all(1).sum() / yrs)}
    for lab, m in zip(REGIMES, (floor, bat, toh, hi, lo)):
        row[f"時間の比 {lab}"] = float(m.mean())
        row[f"充電の比 {lab}"] = float((chg * m).sum() / chg.sum()) if chg.sum() > 0 else np.nan
        row[f"放電の比 {lab}"] = float((dis * m).sum() / dis.sum()) if dis.sum() > 0 else np.nan
    hourly = pd.DataFrame({"年": y, "K(万kW)": K, "時刻": np.arange(24), "価格(円/kWh)": p.mean(0), "東北の価格＋上乗せ(円/kWh)": pT_mu.mean(0),
                           "充電(MW)": chg.mean(0), "放電(MW)": dis.mean(0)})
    hourly_state = dict(curt=R["curt"], exp=exp, imp=imp, g=g, chg=chg, dis=dis)
    return row, hourly, (y, K, hourly_state)


def sources(states):
    """蓄電池0 と比べた充電の電気の出どころ（充電が放電より多い時間、TWh/年）"""
    rows = []
    for y in YEARS_SHOW:
        z = states[(y, 0.0)]
        for K in KS[1:]:
            s = states[(y, K)]
            net = s["chg"] - s["dis"]
            m = net > 1e-9
            yrs = net.shape[0] / 365.25
            d = lambda k, sign=1.0: float((sign * (s[k] - z[k]) * m).sum() / yrs / 1e6)
            rows.append({"年": y, "K(万kW)": K, "充電が多い時間の正味の充電(TWh)": float((net * m).sum() / yrs / 1e6),
                         "抑制の減少": d("curt", -1.0), "東北へ送る量の減少": d("exp", -1.0), "東北から受ける量の増加": d("imp"),
                         "北海道の火力の増加": d("g")})
    return pd.DataFrame(rows)


def spines(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.7)
    ax.set_axisbelow(True)


def figure(S, H, Src, y=2035):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    a, b, c = axes
    h = H[H["年"] == y]
    cols = {0.0: "#9b9a94", 50.0: C1, 100.0: C3, 200.0: C4, 400.0: C2}
    for K, col in cols.items():
        g = h[h["K(万kW)"] == K]
        a.plot(g["時刻"], g["価格(円/kWh)"], color=col, lw=2, label=f"蓄電池 {K:.0f}万kW")
    a.set_xticks(range(0, 24, 3))
    a.set_xlabel("時刻", color=MUTED)
    a.set_ylabel("平均価格（円/kWh）", color=INK)
    a.set_title(f"{y}年 時刻別の平均価格", loc="left", color=INK, fontsize=11)
    a.legend(frameon=False, fontsize=8.5)
    spines(a)
    s = S[S["年"] == y]
    b.plot(s["K(万kW)"], s["高い4時間(円/kWh)"], color=C2, lw=2, marker="o", ms=4, label="高い4時間")
    b.plot(s["K(万kW)"], s["安い4時間(円/kWh)"], color=C1, lw=2, marker="o", ms=4, label="安い4時間")
    b.set_xlabel("蓄電池の量（万kW）", color=MUTED)
    b.set_ylabel("日の平均（円/kWh）", color=INK)
    b.set_title("安い時間は上がり、高い時間は下がる", loc="left", color=INK, fontsize=11)
    b.set_ylim(0, 16)
    b.legend(frameon=False, fontsize=8.5, loc="lower right")
    spines(b)
    c.plot(s["K(万kW)"], s["π(円/kW-年)"], color=C1, lw=2, marker="o", ms=4, label="1kW の価値 π（スポットの値差）")
    th = float(s["参入のしきい値(円/kW-年)"].iloc[0])
    c.axhline(th, color=C2, lw=1.5, ls="--")
    c.text(s["K(万kW)"].max(), th + 250, f"参入のしきい値 {th:,.0f}円\n（建設費＋運転維持費＋託送等−容量収入）", color=C2, fontsize=8.5, ha="right", va="bottom")
    k = s["K(万kW)"].to_numpy()
    v = s["π(円/kW-年)"].to_numpy()
    if v[0] > th > v.min():
        j = int(np.argmax(v < th))
        kx = k[j - 1] + (k[j] - k[j - 1]) * (v[j - 1] - th) / (v[j - 1] - v[j])
        c.plot([kx], [th], "o", color=C2, ms=6)
        c.annotate(f"π がしきい値まで下がる量 約{round(kx / 5) * 5:.0f}万kW", (kx, th), xytext=(kx + 75, th + 1600), color=C2, fontsize=8.5,
                   arrowprops=dict(arrowstyle="-", color=C2, lw=0.8))
    ks = EN.preset_stock(y)
    c.axvline(ks, color=MUTED, lw=1, ls=":")
    c.annotate(f"既設＋LTDA {ks:.1f}万kW\n（この量で π はしきい値より低く、\n新しい参入はない）", (ks, th * 0.5), xytext=(ks + 130, th * 0.5), color=MUTED, fontsize=8.5, va="center",
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    c.set_xlabel("蓄電池の量（万kW）", color=MUTED)
    c.set_ylabel("円/kW-年", color=INK)
    c.set_title("値差が縮み、1kW の価値が下がる", loc="left", color=INK, fontsize=11)
    c.set_ylim(0, None)
    c.legend(frameon=False, fontsize=8.5, loc="upper right")
    spines(c)
    fig.text(0.01, -0.06, f"主の前提（{y}年、容量価格14,972円、一律の上乗せ）。同じスペックの蓄電池は同じ価格を見て一緒に動く（量ごとに蓄電池全体の充放電を決め直す。同じ時間に充電と放電はしない。区切りでは蓄電池の入札が値を決める）。"
             "π はその年の価値だけで、建設費の低下は待たない。しきい値は容量価格14,972円・κ＝0.861", fontsize=8.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "simple_price_response.png"), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote simple_price_response.png")


def main():
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    if os.environ.get("FIG_ONLY") == "1":                      # 保存した結果から図だけ描き直す
        rd = lambda f: pd.read_csv(os.path.join(PROC, f), encoding="utf-8-sig")
        return figure(rd("simple_price_response.csv"), rd("simple_price_response_hourly.csv"), rd("simple_price_response_sources.csv"))
    jobs = [(y, K) for y in YEARS_SHOW for K in KS]
    with ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", "8"))) as ex:
        out = list(ex.map(_job, jobs, chunksize=1))
    S = pd.DataFrame([o[0] for o in out])
    H = pd.concat([o[1] for o in out], ignore_index=True)
    Src = sources({(y, K): st for _, _, (y, K, st) in out})
    S.to_csv(os.path.join(PROC, "simple_price_response.csv"), index=False, encoding="utf-8-sig")
    H.to_csv(os.path.join(PROC, "simple_price_response_hourly.csv"), index=False, encoding="utf-8-sig")
    Src.to_csv(os.path.join(PROC, "simple_price_response_sources.csv"), index=False, encoding="utf-8-sig")
    print(S.round(3).to_string())
    print(Src.round(3).to_string())
    figure(S, H, Src)


if __name__ == "__main__":
    main()
