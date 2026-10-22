#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""6.4 空間分散シミュレーション v3: 校正の再現・実現分散比で合わせた集中立地の反実仮想・日周位相の検定・価格過程の検証

29_spatial_dispersion.py（表6.4 の旧版）の作り直し。旧版の問題は (i) 名目の λ と実際の増幅が一致しない
（0 での打ち切りと日ごとの再スケールのため、名目 λ=4 で実現する日内帯域の分散比は 7.5 にとどまり、校正の上限 17.1 に届かない）、
(ii) 校正（N≈A/(2ξ)²）が原稿・作業ノートから再現できない、(iii) 帯域別の校正を一様な λ で代用している、
(iv)「系統的な日内位相が符号を決める」を λ の設計では検定していない、(v) 価格過程の日内感応度が検証されていない、の5点。

手法:
  (A) 校正の再現（St. Martin, Lundquist and Handschy 2015, ERL 10, 044004）。
      相関距離 ξ_τ は「窓幅 τ の移動平均を引いたハイパス系列（τ より速い成分すべて）」の地点間相関を距離で積分した値で、
      帯域通過の値ではない。論文は 6h・24h の ξ_τ を数値で報告していないので、次の2通りで求める。
        (a) 論文の式(2) の経験的包絡  [1+τ0/τ]^−2 < ξ_τ/ξmax < [1+(τ0/τ)²]^−1/2、τ0=38h を τ=6h・24h で評価
            （下限・上限・幾何平均・算術平均）。ξmax は CAN 273km（10m 風速、45年）・AUS 368km（発電量、1年）。BPA 89km は参考。
        (b) 論文 Fig.6 の地域別の点を読み取り τ=6h・24h に対数内挿した値（文献ノート
            planning/thesis-jepx/literature/notes/st-martin2015.md §4.3–4.4。図からの読み取りで誤差 ±3〜5%）:
            AUS 0.086／0.353、CAN 0.059／0.245、BPA 0.046／0.316。AUS・BPA は βℓ 基準（447・130km）も併記。
      帯域 b の分散の減衰 N_b（単一サイトの分散 ÷ フリート集約の分散）を次の2通りで求める。
        (1) 面積式 N_b = A/(2ξ_b)²（論文 §4 の「最大で（up to）」の上限式。領域を発電所で埋め尽くした場合）。
            A は 北海道全域 83,424km²（国土地理院、北方領土を含む）・78,421km²（北方領土を除く）・
            風力の所在市町村の凸包（日本海側の主要地点のみ／容量1%以上の全地点）。N<1 は 1 とする（減衰なし）。
            実際の発電所数が少なければその数で決まる（論文 §4）ので、発電所数 70（NEDO 2018年3月末の63設備
            ＋ユーラス道北6か所＋石狩湾新港洋上）で上から抑えた値も併記する。
        (2) フリートの容量加重: 指数相関 ρ_ij=exp(−d_ij/ξ_b) の下で集約出力の分散比 N_eff=1/(wᵀCw)。
            w は市町村別の容量シェア（NEDO「日本における風力発電設備・導入実績」北海道、2018年3月末の25市町村 359.5MW に、
            ユーラスエナジー道北6か所 434.5MW（稚内市・豊富町・幌延町に3等分。北海道新聞 2025年7月3日）と石狩湾新港洋上 112MW を加え、
            FY2023〜25 の平均設備容量 1.21GW（B表系列）との残差を2018年の分布に比例配分）。座標は市町村役場の概略位置（±5km）。
            同じ市町村の発電所を完全相関（1点）とみなすので N_eff を小さめに出す（下限側）。
      ξ_6h を「6時間未満」帯に、ξ_24h（累積値）を「6〜24時間」帯に当てる。帯域通過の ξ_b は ξ_24h 以上なので、
      N_2 は上限側の値になる。日内分散比 R=(s6·N1+s24·N2)/(s6+s24)（s6・s24 は実フリートの帯域分散シェア）、
      実効的な振幅倍率 √R、単一サイト相当の日内シェア s1=(s6·N1+s24·N2)/(s6·N1+s24·N2+s_slow)（1日超の帯域は減衰しないと置く）。
      校正の下限・中央・上限は (2)×AUS型・(1) 北海道全域×AUS型・(1) 北海道全域×CAN型 とする（中央の交差の組 CAN型×容量加重も併記）。
      Malvaldi et al. (2017) の国別と10か国集約の分散比（2.1〜6.5）は全帯域の値で、日内帯域の R には対応させない。
  (B) 打ち切りに強い増幅（ロジット版）。設備利用率 u=x/cap を [0.003, 0.997] に収めてロジット z に変換し、
      z を 08・29 と同じ移動平均カスケードで帯域分解する（<6h=z−MA6h、6–24h=MA6h−MA24h）。
        y = cap·logistic(z + (m1−1)·b̃_<6h + (m2−1)·b̃_6–24h + c_d)
      c_d は各日の二分法（60回）で、日次エネルギーを実績に一致させる（容量の上下限も守る）。
      一様版（m1=m2=m）は、y の帯域分散から測った実現の日内分散比 R（帯域分散の和の比）が目標値に一致するよう m を Brent 法で求める。
      帯域別版は、<6h 比と 6–24h 比を目標 (N1, N2) に合わせるよう m1・m2 を交互に根探し（4周）し、帯域間の漏れを打ち消す。
      判定: 実現の帯域別分散比が目標の ±5% 以内。旧版（加法＋打ち切り＋日次再スケール、29 と同一）の名目 λ=1.5〜4 も
      実現の分散比・√比・s1・日次エネルギーの誤差とともに再計算する。
  (B') 確率成分だけの増幅（主。2026-10-21 の検証で追加）。St. Martin et al. の ξ は、最初の4次の日周高調波を差し引いた
      確率的な変動の相関距離で、日周成分は空間的に同調して残る（論文 §2.2.1・§2.2.4。文献ノート st-martin2015.md §6 の注意
      「日周成分には λ を適用しない」）。(B) は日内帯域全体を増幅するので、フリート自身の系統的な日周（季節×時刻の平均。
      FY2023 以降は 0時・14時・18〜19時に山、7時・21〜22時に谷があり、<6h 帯の分散の12.6% を占める）も N 倍に増幅してしまう
      （上限で日周振幅 0.17→0.84、帯域別の上限では 1.32）。この日周の増幅は完全予見粗利を下げる（(C) のフリート自身の日周×k）。
      そこで、ロジット z の各帯域から季節×時刻の平均 D_b を除いた確率成分だけを増幅する:
        y = cap·logistic(z + (m1−1)·(b̃_<6h − D_<6h) + (m2−1)·(b̃_6–24h − D_6–24h) + c_d)
      校正の目標も確率成分の分散シェア（<6h 1.68%、6–24h 8.74%）で R_ns=(s6n·N1+s24n·N2)/(s6n+s24n) とし、
      y の各帯域から季節×時刻の平均を除いた分散の比（実現の R_ns）が目標に一致するよう m を求める
      （下限 2.81・中央 4.40・交差 3.87・上限 16.88）。帯域別版も同様（6–24h 帯は m2 の下限 0 に達し ±5% に入らない場合がある）。
      (B) の全成分の版は、各サイトの日周の位相がばらばらでフリートの日周も集約で減衰していると置いた場合の感応度として残す。
  (C) 日周位相の付与（29 に無い検定）: y = x·(1+a·cos(2π(h−h0)/24)) を [0, 容量] で打ち切り日次エネルギーに再スケール（3回）。
      h0 ∈ {3（夜）, 13（昼）, 18（夕方）}、a ∈ {0.1, 0.2, 0.3}、a=0.2 で h0 を 0〜21時の3時間刻みに動かす掃引、
      およびフリート自身の季節×時刻の日周成分を k 倍にした版（日次エネルギー保存、ロジット空間）。各系列の実現分散比を測り、
      同じ実現分散比（全成分の R）の一様増幅（(B) 全成分と (B') 確率成分の格子を線形補間）と比べて、分散1単位あたりの効き（ΔPF/(R−1)）を示す。
  (D) 価格過程の検証（実績 vs 仕様A θ=1、FY2023〜25）:
      (i) 下限張り付き時間・TB4h 中央値・p05・p95・完全予見粗利、風力日量→TB4h の季節別係数（5.2.3 の右辺を FY2023〜25 に当てた仕様）と
          差（実績TB4h−モデルTB4h を同じ右辺に回帰）の EWC 検定。
      (ii) 風力の日内帯域の日次標準偏差（GW）→TB4h の感応度（季節別）を、実績・モデル・差について EWC で推定。
          FY・季節FE 版、追加統制版（需要・太陽光の日内SD、前日からの風力日量の変化の絶対値、風力日量の2乗。
          参考にシステムプライスの TB4h を加えた版）、年月FE で夏を 7〜8月と9月に分けた版。
      (iii) モデルの季節別 ΔPF に、実績/モデルの感応度比（実績係数の EWC 95%区間、モデル係数は固定）を掛けた補正幅（参考値）。
          全季節を補正する版と、差が5%で有意な季節（夏）だけ補正する版。線形外挿（感応度×日内SD の増分）は使わない。
          2026-10-21 の敵対的検証で、モデル係数の推定誤差も含めた比の Fieller 95%区間を追加した（実績とモデルの係数の
          同時の EWC 共分散。同じ右辺・同じ日の影響関数を積み重ねて第II種離散余弦に射影）。モデル係数の t が小さい
          （夏 2.35）ため区間は上側に長く、二次式の先頭係数が負（分母が5%で有意でない）なら有界にならず NaN とする。
  EWC: 影響関数 ψ_t=(X'X)^{-1}x_t e_t を暦日の格子に置き、第II種離散余弦 √2·cos(πj(t−1/2)/T)（j=1..ν、ν=⌊0.4T^{2/3}⌋）に
       射影した2乗の平均を分散とし、t_ν で検定する（37_robust_inference.py と同じ。FY2023〜25 は欠測日なし、T=1,096、ν=42）。
  価格指標は 26（仕様A、θ=1）の metrics と同じ定義（FY2023〜25 の年度平均）。完全予見粗利は 1日1サイクル・4時間・
  往復効率0.85（放電側）、粗利が負の日は休止。
出力:
  data/processed/spatial_dispersion_v3_calibration.csv（(A) 校正の全組合せ）
  data/processed/spatial_dispersion_v3_table64.csv（(B)(B') 表6.4 の新版: 旧版の名目λ・ロジット一様（全成分）・帯域別（全成分）・
    確率成分の一様（主）・確率成分の帯域別の価格指標。列「実現の日内分散比R」は全成分、「確率成分の日内分散比R_ns」は確率成分の比）
  data/processed/spatial_dispersion_v3_phase.csv（(C) 日周位相の付与と、同じ実現分散比の一様増幅との比較）
  data/processed/spatial_dispersion_v3_validation.csv（(D)(i)(ii) 実績とモデルの比較・感応度の回帰）
  data/processed/spatial_dispersion_v3_correction.csv（(D)(iii) 感応度比による補正幅）
  figures/hokkaido/spatial_dispersion_v3.png
限界:
  - 反実仮想は風力系列だけを置き換え、価格ゾーンの構成（連系制約・地点別価格）は動かさない。「集中立地（分散効果の除去）」の
    価値であって、単一価格ゾーンの寄与は識別しない。
  - 価格過程（仕様A・θ=1）は FY2023〜25 の供給曲線と時刻プレミアムで固定。日内SD への感応度は夏で実績より小さく
    （(D)(ii)）、不需要期の水準の係数は実績より大きい。表の値は「この価格過程の上での」比較。
  - 増幅は日内帯域の位相を保つ（新しい位相を作らない）。系統的な日周で説明される日内分散は実フリートで2.8%（<6h 帯では12.6%）。
    (B) の全成分の版はこの日周も増幅する（上限で日周振幅が約5倍）ので、主は (B') の確率成分の版とする。
    季節×時刻の平均は論文の「90日移動窓の4次の日周高調波」の近似。
  - 校正は相関距離の文献値・面積式・市町村単位の概略配置に依存し、北海道の単一サイト出力で R を直接測ったものではない。
    市町村の容量配分・座標は概略で、2018年以降の撤去・リプレースは反映しない。帯域通過の ξ_b は推定していない。
  - ドイツ陸上風力の平均日周形状を当てた版は、数値で引ける出典をリポジトリに持たないため作っていない。
"""
import logging
import os

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import brentq
from scipy.spatial import ConvexHull
import matplotlib

matplotlib.use("Agg")
from matplotlib import font_manager  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = ["Noto Sans CJK JP", "Hiragino Sans", "Yu Gothic", "Meiryo"]

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
FIGDIR = os.path.join(ROOT, "figures", "hokkaido")
GRAY = "#595959"
SEED = 20261021
np.random.seed(SEED)  # 乱数は使わないが作法として固定
ETA = 0.85
SEASONS = ["夏", "冬", "春秋"]
SLAB = {"夏": "夏", "冬": "冬", "春秋": "不需要期"}
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬", 3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)

# ---------- 0. 価格過程 v2（26 を exec。26 の price_level_theta.csv の書き出しは一時的に無効化） ----------
_to_csv = pd.DataFrame.to_csv
pd.DataFrame.to_csv = lambda self, *a, **k: None
try:
    ns = {"__file__": os.path.join(HERE, "26_price_process_v2.py"), "__name__": "pp_v2"}
    exec(open(os.path.join(HERE, "26_price_process_v2.py"), encoding="utf-8").read(), ns)
finally:
    pd.DataFrame.to_csv = _to_csv
est = ns["est"].sort_values("ts").reset_index(drop=True).copy()
predict_A, metrics26 = ns["predict_A"], ns["metrics"]
est["sea3"] = est["ts"].dt.month.map(SEASON_MAP)

ts_full = pd.date_range(est["ts"].min(), est["ts"].max(), freq="h")
assert len(ts_full) == len(est), "FY2023-25 の時間格子に欠測がある"
x = est.set_index("ts")["wind_pre"].reindex(ts_full).interpolate(limit_direction="both")
cap = est.set_index("ts")["wind_kw"].reindex(ts_full).ffill().bfill() / 1000
day = x.index.normalize()
hour = x.index.hour.to_numpy()
sea_h = pd.Series(x.index.month.map(SEASON_MAP), index=x.index)
print(f"FY2023-25: {len(est):,} 時間、{day.nunique():,} 日。風力（制御前）平均 {x.mean():.0f}MW、設備容量平均 {cap.mean():.0f}MW、"
      f"x>容量の時間 {(x > cap).mean() * 100:.2f}%")


def bands(s):
    ma6 = s.rolling(6, center=True, min_periods=3).mean()
    ma24 = s.rolling(24, center=True, min_periods=12).mean()
    ma168 = s.rolling(168, center=True, min_periods=84).mean()
    return {"<6h": s - ma6, "6-24h": ma6 - ma24, "1-7d": ma24 - ma168, ">7d": ma168 - s.mean()}


BX = bands(x)
VX = {k: float(v.var()) for k, v in BX.items()}
VXT = float(x.var())
SH = {k: VX[k] / VXT * 100 for k in VX}
S6, S24, SSLOW = SH["<6h"], SH["6-24h"], SH["1-7d"] + SH[">7d"]
INTRA_X = BX["<6h"] + BX["6-24h"]
print("実フリートの帯域分散シェア(%):", {k: round(v, 2) for k, v in SH.items()},
      f" 日内（合成系列 x−MA24 の分散）{INTRA_X.var() / VXT * 100:.2f}%")
SEA_A = sea_h.to_numpy()


def sysmean(s):
    """季節×時刻の平均（系統的な日周。St. Martin et al. の日周高調波の除去の近似）"""
    return s.groupby([SEA_A, hour]).transform("mean")


# 確率成分（各帯域から季節×時刻の平均を除いた部分）の分散
VXN = {k: float((BX[k] - sysmean(BX[k])).var()) for k in ("<6h", "6-24h")}
S6N, S24N = VXN["<6h"] / VXT * 100, VXN["6-24h"] / VXT * 100
print(f"確率成分の分散シェア(%): <6h {S6N:.2f}（帯域内の系統的日周 {(1 - VXN['<6h'] / VX['<6h']) * 100:.1f}%）、"
      f"6-24h {S24N:.2f}（同 {(1 - VXN['6-24h'] / VX['6-24h']) * 100:.1f}%）")


def diurnal_share(intra):
    """日内帯域の分散のうち、季節×時刻の平均（系統的な日周）で説明される割合"""
    dm = intra.groupby([sea_h.to_numpy(), hour]).transform("mean")
    return float(dm.var() / intra.var())


def stats_series(y):
    """実現の分散比・s1・日次エネルギー誤差・日周の指標"""
    by = bands(y)
    vy = {k: float(v.var()) for k, v in by.items()}
    intra = by["<6h"] + by["6-24h"]
    R = (vy["<6h"] + vy["6-24h"]) / (VX["<6h"] + VX["6-24h"])
    prof = y.groupby([sea_h.to_numpy(), hour]).mean().unstack()
    de = (y.groupby(day).sum() / x.groupby(day).sum() - 1).abs()
    vn = {k: float((by[k] - sysmean(by[k])).var()) for k in ("<6h", "6-24h")}
    return {"実現の日内分散比R": R, "実効振幅倍率√R": np.sqrt(R),
            "確率成分の日内分散比R_ns": (vn["<6h"] + vn["6-24h"]) / (VXN["<6h"] + VXN["6-24h"]),
            "<6h確率成分の分散比": vn["<6h"] / VXN["<6h"], "6-24h確率成分の分散比": vn["6-24h"] / VXN["6-24h"],
            "合成日内帯域の分散比": float(intra.var() / INTRA_X.var()),
            "<6h分散比": vy["<6h"] / VX["<6h"], "6-24h分散比": vy["6-24h"] / VX["6-24h"],
            "1日超の分散比": (vy["1-7d"] + vy[">7d"]) / (VX["1-7d"] + VX[">7d"]),
            "s1(%)": (vy["<6h"] + vy["6-24h"]) / sum(vy.values()) * 100,
            "総分散に対する日内シェア(%)": float(intra.var() / y.var() * 100),
            "系統的日周の比率(%)": diurnal_share(intra) * 100,
            "日周振幅(max−min)/平均": float(((prof.max(axis=1) - prof.min(axis=1)) / prof.mean(axis=1)).mean()),
            "日次エネルギー誤差 平均(%)": float(de.mean() * 100), "日次エネルギー誤差 最大(%)": float(de.max() * 100)}


# ---------- EWC ----------
_COS = {}


def ewc_fit(y, X, keys):
    """OLS と EWC（暦日の格子、ν=⌊0.4T^{2/3}⌋、t_ν）。keys の係数・SE・p と ν を返す"""
    Xn = X.to_numpy(float)
    yn = np.asarray(y, float)
    XtXi = np.linalg.pinv(Xn.T @ Xn)
    b = XtXi @ Xn.T @ yn
    e = yn - Xn @ b
    cols = list(X.columns)
    idx = [cols.index(k) for k in keys]
    psi = (Xn @ XtXi[idx].T) * e[:, None]
    pos = (X.index - X.index[0]).days.to_numpy()
    T = int(pos.max()) + 1
    g = np.zeros((T, len(idx)))
    g[pos] = psi
    nu = int(np.floor(0.4 * T ** (2 / 3)))
    if (T, nu) not in _COS:
        t = np.arange(1, T + 1) - 0.5
        _COS[(T, nu)] = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, nu + 1), t) / T)
    v = ((_COS[(T, nu)] @ g) ** 2).mean(axis=0)
    out = {}
    for i, k in enumerate(keys):
        se = float(np.sqrt(v[i]))
        tt = b[idx[i]] / se
        out[k] = {"b": float(b[idx[i]]), "se": se, "p": float(2 * stats.t.sf(abs(tt), nu)), "nu": nu}
    return out


# ---------- 日次の指標と回帰の右辺 ----------
DEM_H = est.set_index("ts")["demand"].reindex(ts_full).interpolate()
SOL_H = est.set_index("ts")["solar_pre"].reindex(ts_full).interpolate()


def daily_sd_intra(s):
    bb = bands(s)
    i = bb["<6h"] + bb["6-24h"]
    return i.groupby(i.index.normalize()).std() / 1000


def tb4_daily(df, pcol):
    P = df.pivot(index="day", columns="hour", values=pcol)
    P = P[P.count(axis=1) == 24]
    srt = np.sort(P.to_numpy(), axis=1)
    return pd.Series(srt[:, -4:].mean(1) - srt[:, :4].mean(1), index=P.index)


D0 = pd.DataFrame(index=pd.DatetimeIndex(sorted(est["day"].unique())))
D0["wind"] = x.groupby(day).sum().reindex(D0.index) / 1000
D0["solar"] = est.groupby("day")["solar_pre"].sum() / 1000
D0["demand"] = est.groupby("day")["demand"].sum() / 1000
D0["fy"] = D0.index.year - (D0.index.month < 4).astype(int)
D0["season"] = D0.index.month.map(SEASON_MAP)
D0["isd"] = daily_sd_intra(x).reindex(D0.index)


def design(isd=False, extra=None, ymfe=False, split_sep=False, wind=None):
    """5.2.3 の右辺（FY2023〜25）: 季節×風力・太陽光 GWh/日、需要、FY FE、季節 FE。isd=True で季節×風力の日内SD を加える。
    wind を与えると風力日量をその系列に置き換える（合成系列の日量。ロジット版は実績と厳密に一致、旧版の加法は最大21%ずれる）"""
    d = D0 if wind is None else D0.assign(wind=wind.reindex(D0.index))
    X = pd.DataFrame(index=d.index)
    X["const"] = 1.0
    for s in SEASONS:
        m = (d["season"] == s).astype(float)
        X[f"wind_{s}"] = d["wind"] * m
        X[f"solar_{s}"] = d["solar"] * m
        if isd:
            if s == "夏" and split_sep:
                X["isd_夏7-8"] = d["isd"] * m * (d.index.month != 9)
                X["isd_9月"] = d["isd"] * m * (d.index.month == 9)
            else:
                X[f"isd_{s}"] = d["isd"] * m
    X["demand"] = d["demand"]
    if extra is not None:
        X = pd.concat([X, extra.reindex(d.index)], axis=1)
    if ymfe:
        ym = pd.get_dummies(d.index.to_period("M").astype(str), prefix="ym", drop_first=True).astype(float)
        ym.index = d.index
        X = pd.concat([X, ym], axis=1)
    else:
        X = pd.concat([X, pd.get_dummies(d["fy"], prefix="fy", drop_first=True).astype(float),
                       pd.get_dummies(d["season"], prefix="ssn", drop_first=True).astype(float)], axis=1)
    return X


X_MAIN = design()
WKEYS = [f"wind_{s}" for s in SEASONS]


def wind_coef(tb4, wind=None):
    X = X_MAIN if wind is None else design(wind=wind)
    return ewc_fit(tb4.reindex(X.index), X, WKEYS)


# ---------- 価格過程に通す ----------
def run_price(y):
    df = est.copy()
    df["wind_syn"] = y.reindex(df["ts"]).to_numpy()
    df["net_syn"] = df["demand"] - df["solar_pre"] - df["wind_syn"] - df["nuclear"].fillna(0)
    df["p_syn"] = predict_A(df, net_col="net_syn", theta=1.0)
    m = metrics26(df, "p_syn").mean()
    tb = tb4_daily(df, "p_syn")
    reg = wind_coef(tb, wind=y.groupby(y.index.normalize()).sum() / 1000)
    piv = df.pivot(index="day", columns="hour", values="p_syn")
    srt = np.sort(piv.to_numpy(), axis=1)
    mg = pd.Series(np.maximum(0.0, srt[:, -4:].sum(1) * ETA - srt[:, :4].sum(1)), index=piv.index)
    pf_s = mg.groupby(mg.index.month.map(SEASON_MAP)).sum() / 3.0
    r = {"下限張り付き(h/年)": float(m["床(≤0.01円)時間"]), "TB4h中央値": float(m["TB4h中央値"]), "p05": float(m["p05"]),
         "p95": float(m["p95"]), "完全予見粗利(円/kW-年)": float(m["PF価値(円/kW-年)"])}
    for s in SEASONS:
        r[f"完全予見粗利_{SLAB[s]}"] = float(pf_s[s])
    for s in SEASONS:
        r[f"β風力→TB4h_{SLAB[s]}"] = reg[f"wind_{s}"]["b"]
        r[f"p_EWC_{SLAB[s]}"] = reg[f"wind_{s}"]["p"]
    return r, tb


# ======================================================================
# (A) 校正
# ======================================================================
TAU0 = 38.0


def env_lo(t):
    return (1 + TAU0 / t) ** -2


def env_hi(t):
    return (1 + (TAU0 / t) ** 2) ** -0.5


A_HOK, A_HOK_EX = 83424.0, 78421.0
N_PLANT = 70
# 市町村: 緯度・経度（役場の概略位置）、2018年3月末の総出力 MW（NEDO）
MUNI = [("稚内市", 45.4156, 141.6731, 76.355), ("利尻町", 45.18, 141.13, 0.25), ("幌延町", 45.0186, 141.8492, 21.48),
        ("天塩町", 44.8853, 141.7469, 2.4), ("遠別町", 44.7225, 141.7964, 2.97), ("羽幌町", 44.3631, 141.7011, 0.8),
        ("苫前町", 44.3083, 141.6553, 52.8), ("小平町", 44.0156, 141.6617, 2.96), ("留萌市", 43.9406, 141.6369, 5.36),
        ("石狩市", 43.1714, 141.3156, 9.78), ("小樽市", 43.1906, 140.9944, 6.6), ("寿都町", 42.7906, 140.2289, 16.58),
        ("島牧村", 42.6997, 140.06, 4.5), ("せたな町", 42.42, 139.87, 13.2), ("江差町", 41.8692, 140.1275, 41.3),
        ("上ノ国町", 41.8017, 140.1086, 28.0), ("松前町", 41.4306, 140.1103, 0.8), ("函館市", 41.7686, 140.7289, 2.9),
        ("室蘭市", 42.3153, 140.9736, 4.45), ("伊達市", 42.4717, 140.8647, 44.0), ("えりも町", 42.0158, 143.1483, 0.8),
        ("浜中町", 43.0778, 145.1283, 1.97), ("根室市", 43.33, 145.5828, 13.13), ("浜頓別町", 45.1239, 142.3597, 4.96),
        ("猿払村", 45.3283, 142.1067, 1.2), ("豊富町", 45.1033, 141.7783, 0.0)]
mu = pd.DataFrame(MUNI, columns=["市町村", "lat", "lon", "MW_2018"]).set_index("市町村")
ADD = {"稚内市": 434.5 / 3, "豊富町": 434.5 / 3, "幌延町": 434.5 / 3, "石狩市": 112.0}
mu["MW_既知"] = mu["MW_2018"] + pd.Series(ADD).reindex(mu.index).fillna(0.0)
CAP_MEAN = float(cap.mean())
RESID = CAP_MEAN - mu["MW_既知"].sum()
mu["MW_FY23-25"] = mu["MW_既知"] + RESID * mu["MW_2018"] / mu["MW_2018"].sum()
print(f"\n(A) 容量配分: NEDO 2018年3月末 {mu['MW_2018'].sum():.1f}MW＋道北 434.5＋石狩洋上 112 ＝ {mu['MW_既知'].sum():.1f}MW、"
      f"FY2023-25 平均 {CAP_MEAN:.0f}MW との残差 {RESID:.0f}MW を2018年の分布に比例配分")
lat0 = np.deg2rad(43.5)
XY = np.c_[(mu["lon"] - 141.0) * 111.32 * np.cos(lat0), (mu["lat"] - 43.5) * 110.95]
la, lo = np.deg2rad(mu["lat"].to_numpy()), np.deg2rad(mu["lon"].to_numpy())
hv = (np.sin((la[:, None] - la[None, :]) / 2) ** 2 + np.cos(la[:, None]) * np.cos(la[None, :]) * np.sin((lo[:, None] - lo[None, :]) / 2) ** 2)
DIST = 2 * 6371.0 * np.arcsin(np.sqrt(hv))
JS = ["稚内市", "豊富町", "幌延町", "天塩町", "苫前町", "留萌市", "石狩市", "小樽市", "寿都町", "島牧村", "せたな町", "江差町", "上ノ国町", "松前町"]
w_cur = (mu["MW_FY23-25"] / mu["MW_FY23-25"].sum()).to_numpy()
big = w_cur > 0.01
A_HULL_JS = float(ConvexHull(XY[mu.index.isin(JS)]).volume)
A_HULL_BIG = float(ConvexHull(XY[big]).volume)
print(f"  凸包の面積: 日本海側の主要14市町村 {A_HULL_JS:,.0f}km²、容量1%以上の{big.sum()}市町村 {A_HULL_BIG:,.0f}km²（海域を含む）")


def n_eff(wcol, xi):
    w = (mu[wcol] / mu[wcol].sum()).to_numpy()
    return float(1.0 / (w @ np.exp(-DIST / xi) @ w))


XI_SRC = []  # (出典, ξmax の基準, ξmax km, 比 6h, 比 24h)
for lab, f6, f24 in (("式(2)包絡・下限", env_lo(6), env_lo(24)), ("式(2)包絡・上限", env_hi(6), env_hi(24)),
                     ("式(2)包絡・幾何平均", np.sqrt(env_lo(6) * env_hi(6)), np.sqrt(env_lo(24) * env_hi(24))),
                     ("式(2)包絡・算術平均", (env_lo(6) + env_hi(6)) / 2, (env_lo(24) + env_hi(24)) / 2)):
    for basis, xm in (("CAN 273", 273.0), ("AUS 368", 368.0), ("BPA 89（参考）", 89.0)):
        XI_SRC.append((lab, basis, xm, f6, f24))
for lab, basis, xm, f6, f24 in (("Fig.6 AUS型（発電量）", "ξmax 368", 368.0, 0.086, 0.353), ("Fig.6 AUS型（発電量）", "βℓ 447", 447.0, 0.086, 0.353),
                                ("Fig.6 CAN型（風速）", "ξmax 273", 273.0, 0.059, 0.245),
                                ("Fig.6 BPA型（風速、参考）", "ξmax 89", 89.0, 0.046, 0.316), ("Fig.6 BPA型（風速、参考）", "βℓ 130", 130.0, 0.046, 0.316)):
    XI_SRC.append((lab, basis, xm, f6, f24))

EXTENTS = [("北海道全域（北方領土を含む）", "面積式", A_HOK), ("北海道（北方領土を除く）", "面積式", A_HOK_EX),
           ("日本海側主要14市町村の凸包", "面積式", A_HULL_JS), ("容量1%以上の市町村の凸包", "面積式", A_HULL_BIG),
           ("フリート容量加重（FY23-25推計）", "容量加重", np.nan), ("フリート容量加重（既知分のみ）", "容量加重", np.nan)]


def R_of(n1, n2):
    return (S6 * n1 + S24 * n2) / (S6 + S24)


def s1_of(n1, n2):
    return (S6 * n1 + S24 * n2) / (S6 * n1 + S24 * n2 + SSLOW) * 100


def R_ns_of(n1, n2):
    """確率成分の分散シェアで重みづけた日内分散比（(B') の校正の目標。日周成分は減衰しないと置く）"""
    return (S6N * n1 + S24N * n2) / (S6N + S24N)


cal_rows = []
for lab, basis, xm, f6, f24 in XI_SRC:
    xi6, xi24 = f6 * xm, f24 * xm
    for ext, kind, A in EXTENTS:
        if kind == "面積式":
            n1r, n2r = A / (2 * xi6) ** 2, A / (2 * xi24) ** 2
            n1, n2 = max(n1r, 1.0), max(n2r, 1.0)
            n1c, n2c = min(n1, N_PLANT), min(n2, N_PLANT)
        else:
            wcol = "MW_FY23-25" if "推計" in ext else "MW_既知"
            n1r, n2r = n_eff(wcol, xi6), n_eff(wcol, xi24)
            n1, n2 = n1r, n2r
            n1c, n2c = n1, n2
        cal_rows.append({"ξの出典": lab, "ξmaxの基準": basis, "ξmax(km)": xm, "ξ6h/ξmax": f6, "ξ24h/ξmax": f24,
                         "ξ6h(km)": xi6, "ξ24h(km)": xi24, "空間の広がり": ext, "方式": kind, "A(km²)": A,
                         "N1(<6h)": n1, "N2(6-24h)": n2, "日内分散比R": R_of(n1, n2), "実効振幅倍率√R": np.sqrt(R_of(n1, n2)),
                         "s1(%)": s1_of(n1, n2), "N1_発電所数で抑制": n1c, "N2_発電所数で抑制": n2c, "R_発電所数で抑制": R_of(n1c, n2c),
                         "日内分散比R_ns（確率成分）": R_ns_of(n1, n2), "R_ns_発電所数で抑制": R_ns_of(n1c, n2c)})
cal = pd.DataFrame(cal_rows)
cal["校正での役割"] = ""


def pick(src, basis, ext):
    m = (cal["ξの出典"] == src) & (cal["ξmaxの基準"] == basis) & (cal["空間の広がり"] == ext)
    assert m.sum() == 1
    return cal.index[m][0]


ROLE = {"下限": pick("Fig.6 AUS型（発電量）", "ξmax 368", "フリート容量加重（FY23-25推計）"),
        "中央": pick("Fig.6 AUS型（発電量）", "ξmax 368", "北海道全域（北方領土を含む）"),
        "中央（交差の組）": pick("Fig.6 CAN型（風速）", "ξmax 273", "フリート容量加重（FY23-25推計）"),
        "上限": pick("Fig.6 CAN型（風速）", "ξmax 273", "北海道全域（北方領土を含む）")}
for k, i in ROLE.items():
    cal.loc[i, "校正での役割"] = k
cal.round(4).to_csv(os.path.join(PROC, "spatial_dispersion_v3_calibration.csv"), index=False)
print(f"  実フリートの帯域シェア s6={S6:.2f}%、s24={S24:.2f}%、1日超={SSLOW:.2f}%（帯域分散の和に対する実フリートの s1={(S6 + S24) / (S6 + S24 + SSLOW) * 100:.1f}%）")
print("  式(2) 包絡: 6h", round(env_lo(6), 4), "〜", round(env_hi(6), 4), " 24h", round(env_lo(24), 4), "〜", round(env_hi(24), 4))
show = ["ξの出典", "ξmaxの基準", "空間の広がり", "ξ6h(km)", "ξ24h(km)", "N1(<6h)", "N2(6-24h)", "日内分散比R", "実効振幅倍率√R", "s1(%)", "R_発電所数で抑制", "校正での役割"]
print(cal.loc[cal["ξの出典"].str.startswith("Fig.6"), show].round(2).to_string(index=False))
print(cal.loc[cal["空間の広がり"].isin(["北海道全域（北方領土を含む）", "フリート容量加重（FY23-25推計）"]) & cal["ξの出典"].str.startswith("式(2)"), show].round(2).to_string(index=False))
TARGET = {k: (float(cal.loc[i, "N1(<6h)"]), float(cal.loc[i, "N2(6-24h)"]), float(cal.loc[i, "日内分散比R"])) for k, i in ROLE.items()}
# 上限の感応度（一様増幅のみ）: 北方領土を除く面積、発電所数 70 で N を抑えた値
i_ex = pick("Fig.6 CAN型（風速）", "ξmax 273", "北海道（北方領土を除く）")
cal.loc[i_ex, "校正での役割"] = "上限の感応度（北方領土を除く面積）"
UNI_EXTRA = {"上限の感応度（北方領土を除く面積）": float(cal.loc[i_ex, "日内分散比R"]),
             "上限の感応度（発電所数70で抑制）": float(cal.loc[ROLE["上限"], "R_発電所数で抑制"])}
TARGET_NS = {k: (t[0], t[1], R_ns_of(t[0], t[1])) for k, t in TARGET.items()}
UNI_EXTRA_NS = {"上限の感応度（北方領土を除く面積）": float(cal.loc[i_ex, "日内分散比R_ns（確率成分）"]),
                "上限の感応度（発電所数70で抑制）": float(cal.loc[ROLE["上限"], "R_ns_発電所数で抑制"])}
print("  確率成分の校正の目標 R_ns:", {k: round(t[2], 2) for k, t in TARGET_NS.items()}, {k: round(v, 2) for k, v in UNI_EXTRA_NS.items()})
cal.round(4).to_csv(os.path.join(PROC, "spatial_dispersion_v3_calibration.csv"), index=False)
print("  上限の感応度 R:", {k: round(v, 2) for k, v in UNI_EXTRA.items()})
print("  校正の目標 (N1, N2, R):", {k: tuple(round(v, 2) for v in t) for k, t in TARGET.items()})

# ======================================================================
# (B) ロジット版の増幅と旧版の再計算
# ======================================================================
EPS = 0.003
u = (x / cap).clip(EPS, 1 - EPS)
z = np.log(u / (1 - u))
BZ = bands(z)
dcodes, dlev = pd.factorize(day)
E_DAY = x.groupby(day).sum().reindex(dlev).to_numpy()
CAPN = cap.to_numpy()
ZN, BZ6, BZ24 = z.to_numpy(), BZ["<6h"].to_numpy(), BZ["6-24h"].to_numpy()


def logit_daily(zz):
    """各日のロジット平行移動 c_d を二分法で求め、日次エネルギーを厳密に一致させる"""
    lo_, hi_ = np.full(len(dlev), -30.0), np.full(len(dlev), 30.0)
    for _ in range(60):
        c = (lo_ + hi_) / 2
        s = np.bincount(dcodes, CAPN / (1 + np.exp(-(zz + c[dcodes]))), minlength=len(dlev))
        over = s > E_DAY
        hi_ = np.where(over, c, hi_)
        lo_ = np.where(over, lo_, c)
    c = (lo_ + hi_) / 2
    return pd.Series(CAPN / (1 + np.exp(-(zz + c[dcodes]))), index=x.index)


def make_logit(m1, m2):
    return logit_daily(ZN + (m1 - 1) * BZ6 + (m2 - 1) * BZ24)


def ratios_fast(y):
    by = bands(y)
    v6, v24 = float(by["<6h"].var()), float(by["6-24h"].var())
    return (v6 + v24) / (VX["<6h"] + VX["6-24h"]), v6 / VX["<6h"], v24 / VX["6-24h"]


def synth_add(lam):
    """旧版（29 と同一）: 加法の増幅 → 0〜容量で打ち切り → 日次エネルギーに再スケール → 再び打ち切り"""
    intra0 = BX["<6h"] + BX["6-24h"]
    y = (x + (lam - 1.0) * intra0)
    raw = y.copy()
    y = y.clip(lower=0.0, upper=cap)
    scale = x.groupby(day).sum() / y.groupby(day).sum().replace(0, np.nan)
    y = (y * scale.reindex(day).to_numpy()).clip(lower=0.0, upper=cap)
    return y, float((raw <= 0).mean() * 100)


y1 = make_logit(1.0, 1.0)
print(f"\n(B) ロジット変換の往復（m=1）: 日内分散比 {ratios_fast(y1)[0]:.4f}、時間値の差 最大 {float((y1 - x).abs().max()):.1f}MW・平均 {float((y1 - x).abs().mean()):.3f}MW")

rows = []
base_r, base_tb = run_price(x)
rows.append({"区分": "実フリート", "仕様": "λ=1（実フリート）", "目標R": 1.0, "m1": 1.0, "m2": 1.0, **stats_series(x), **base_r})
BASE_PF = base_r["完全予見粗利(円/kW-年)"]
print("  実フリート:", {k: round(v, 3) for k, v in base_r.items()})

for lam in (1.5, 2.0, 3.0, 4.0):
    y, neg = synth_add(lam)
    r, _ = run_price(y)
    rows.append({"区分": "旧版（加法・打ち切り）", "仕様": f"名目λ={lam:g}", "目標R": np.nan, "m1": lam, "m2": lam,
                 "打ち切り前に0以下(%)": neg, **stats_series(y), **r})
    print(f"  旧版 名目λ={lam}: 実現R {rows[-1]['実現の日内分散比R']:.2f}  PF {r['完全予見粗利(円/kW-年)']:.0f}")

UNI_GRID = sorted({1.5, 2.0, 3.0, 4.0, 5.0, 7.51, 10.0, 13.0, 22.0} | {round(t[2], 3) for t in TARGET.values()}
                  | {round(v, 3) for v in UNI_EXTRA.values()})
uni_m = {}
for tgt in UNI_GRID:
    m = brentq(lambda mm: ratios_fast(make_logit(mm, mm))[0] - tgt, 1.0, 20.0, xtol=1e-4)
    y = make_logit(m, m)
    r, _ = run_price(y)
    role = [k for k, t in TARGET.items() if abs(round(t[2], 3) - tgt) < 1e-9] + \
           [k.replace("上限の感応度", "上限の感応度") for k, v in UNI_EXTRA.items() if abs(round(v, 3) - tgt) < 1e-9]
    rows.append({"区分": "ロジット一様", "仕様": f"一様 R={tgt:g}" + (f"（校正の{'・'.join(role)}）" if role else ""), "目標R": tgt,
                 "m1": m, "m2": m, **stats_series(y), **r})
    uni_m[tgt] = m
    print(f"  ロジット一様 目標R={tgt:g}: m={m:.3f} 実現R {rows[-1]['実現の日内分散比R']:.3f}  PF {r['完全予見粗利(円/kW-年)']:.0f}"
          f"  β {r['β風力→TB4h_夏']:+.3f}/{r['β風力→TB4h_冬']:+.3f}/{r['β風力→TB4h_不需要期']:+.3f}")


def root_clip(f, a, b):
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        return a if abs(fa) < abs(fb) else b
    return brentq(f, a, b, xtol=1e-4)


for role, (n1, n2, R) in TARGET.items():
    m1, m2 = np.sqrt(n1), np.sqrt(n2)
    for _ in range(4):
        m1 = root_clip(lambda a: ratios_fast(make_logit(a, m2))[1] - n1, 0.0, 40.0)
        m2 = root_clip(lambda a: ratios_fast(make_logit(m1, a))[2] - n2, 0.0, 20.0)
    y = make_logit(m1, m2)
    st = stats_series(y)
    r, _ = run_price(y)
    ok = abs(st["<6h分散比"] / n1 - 1) <= 0.05 and abs(st["6-24h分散比"] / n2 - 1) <= 0.05
    rows.append({"区分": "ロジット帯域別", "仕様": f"帯域別 (N1,N2)=({n1:.1f},{n2:.2f})（校正の{role}）", "目標R": R, "目標N1": n1, "目標N2": n2,
                 "m1": m1, "m2": m2, "帯域別の目標±5%": ok, **st, **r})
    print(f"  帯域別（{role}）({n1:.1f},{n2:.2f}): m1={m1:.2f} m2={m2:.2f}  実現 <6h {st['<6h分散比']:.2f} 6-24h {st['6-24h分散比']:.2f} R {st['実現の日内分散比R']:.2f}"
          f" ±5%:{ok}  PF {r['完全予見粗利(円/kW-年)']:.0f}")

# ---------- (B') 確率成分だけの増幅（主） ----------
DZ6 = BZ["<6h"].groupby([SEA_A, hour]).transform("mean").to_numpy()
DZ24 = BZ["6-24h"].groupby([SEA_A, hour]).transform("mean").to_numpy()
NZ6, NZ24 = BZ6 - DZ6, BZ24 - DZ24


def make_logit_ns(m1, m2):
    """ロジットの各帯域から季節×時刻の平均（系統的な日周）を除いた確率成分だけを増幅し、日周はフリートの水準に保つ"""
    return logit_daily(ZN + (m1 - 1) * NZ6 + (m2 - 1) * NZ24)


def ratios_ns(y):
    by = bands(y)
    v6 = float((by["<6h"] - sysmean(by["<6h"])).var())
    v24 = float((by["6-24h"] - sysmean(by["6-24h"])).var())
    return (v6 + v24) / (VXN["<6h"] + VXN["6-24h"]), v6 / VXN["<6h"], v24 / VXN["6-24h"]


print("\n(B') 確率成分だけの増幅（主）")
UNI_GRID_NS = sorted({1.5, 2.0, 3.0, 5.0, 7.51, 10.0, 13.0, 22.0} | {round(t[2], 3) for t in TARGET_NS.values()}
                     | {round(v, 3) for v in UNI_EXTRA_NS.values()})
for tgt in UNI_GRID_NS:
    m = brentq(lambda mm: ratios_ns(make_logit_ns(mm, mm))[0] - tgt, 1.0, 30.0, xtol=1e-4)
    y = make_logit_ns(m, m)
    r, _ = run_price(y)
    role = [k for k, t in TARGET_NS.items() if abs(round(t[2], 3) - tgt) < 1e-9] + \
           [k for k, v in UNI_EXTRA_NS.items() if abs(round(v, 3) - tgt) < 1e-9]
    rows.append({"区分": "ロジット一様・確率成分（主）", "仕様": f"確率成分 一様 R_ns={tgt:g}" + (f"（校正の{'・'.join(role)}）" if role else ""),
                 "目標R": tgt, "m1": m, "m2": m, **stats_series(y), **r})
    print(f"  確率成分 一様 目標R_ns={tgt:g}: m={m:.3f} 実現R_ns {rows[-1]['確率成分の日内分散比R_ns']:.3f}（全成分R {rows[-1]['実現の日内分散比R']:.2f}）"
          f"  PF {r['完全予見粗利(円/kW-年)']:.0f}  β {r['β風力→TB4h_夏']:+.3f}/{r['β風力→TB4h_冬']:+.3f}/{r['β風力→TB4h_不需要期']:+.3f}")

for role, (n1, n2, R) in TARGET_NS.items():
    m1, m2 = np.sqrt(n1), np.sqrt(n2)
    for _ in range(4):
        m1 = root_clip(lambda a: ratios_ns(make_logit_ns(a, m2))[1] - n1, 0.0, 40.0)
        m2 = root_clip(lambda a: ratios_ns(make_logit_ns(m1, a))[2] - n2, 0.0, 20.0)
    y = make_logit_ns(m1, m2)
    st = stats_series(y)
    r, _ = run_price(y)
    ok = abs(st["<6h確率成分の分散比"] / n1 - 1) <= 0.05 and abs(st["6-24h確率成分の分散比"] / n2 - 1) <= 0.05
    rows.append({"区分": "ロジット帯域別・確率成分", "仕様": f"確率成分 帯域別 (N1,N2)=({n1:.1f},{n2:.2f})（校正の{role}）", "目標R": R,
                 "目標N1": n1, "目標N2": n2, "m1": m1, "m2": m2, "帯域別の目標±5%": ok, **st, **r})
    print(f"  確率成分 帯域別（{role}）({n1:.1f},{n2:.2f}): m1={m1:.2f} m2={m2:.2f}  実現 <6h {st['<6h確率成分の分散比']:.2f}"
          f" 6-24h {st['6-24h確率成分の分散比']:.2f} R_ns {st['確率成分の日内分散比R_ns']:.2f} ±5%:{ok}  PF {r['完全予見粗利(円/kW-年)']:.0f}")

tab = pd.DataFrame(rows)
tab["ΔPF(%)"] = (tab["完全予見粗利(円/kW-年)"] / BASE_PF - 1) * 100
tab["ΔTB4h中央値(%)"] = (tab["TB4h中央値"] / base_r["TB4h中央値"] - 1) * 100
for s in SEASONS:
    tab[f"Δβ_{SLAB[s]}"] = tab[f"β風力→TB4h_{SLAB[s]}"] - base_r[f"β風力→TB4h_{SLAB[s]}"]
tab.round(4).to_csv(os.path.join(PROC, "spatial_dispersion_v3_table64.csv"), index=False)
print(tab[["仕様", "実現の日内分散比R", "確率成分の日内分散比R_ns", "系統的日周の比率(%)", "日周振幅(max−min)/平均", "実効振幅倍率√R", "s1(%)", "<6h分散比", "6-24h分散比", "1日超の分散比", "日次エネルギー誤差 平均(%)", "日次エネルギー誤差 最大(%)",
           "下限張り付き(h/年)", "TB4h中央値", "p95", "完全予見粗利(円/kW-年)", "ΔPF(%)", "β風力→TB4h_夏", "β風力→TB4h_冬", "β風力→TB4h_不需要期"]].round(3).to_string(index=False))

# 一様増幅の曲線（実現R → 指標）
uni = pd.concat([tab[tab["区分"] == "実フリート"], tab[tab["区分"] == "ロジット一様"]]).sort_values("実現の日内分散比R")
uni_ns = pd.concat([tab[tab["区分"] == "実フリート"], tab[tab["区分"] == "ロジット一様・確率成分（主）"]]).sort_values("実現の日内分散比R")


def uni_at(R, col, u=None):
    u = uni if u is None else u
    return float(np.interp(R, u["実現の日内分散比R"], u[col]))


# ======================================================================
# (C) 日周位相の付与
# ======================================================================
def phase_series(a, h0):
    y = x * (1 + a * np.cos(2 * np.pi * (hour - h0) / 24))
    for _ in range(3):
        y = y.clip(lower=0.0, upper=cap)
        y = y * (x.groupby(day).sum() / y.groupby(day).sum().replace(0, np.nan)).reindex(day).to_numpy()
    return y.clip(lower=0.0, upper=cap)


DZ = (BZ["<6h"] + BZ["6-24h"]).groupby([sea_h.to_numpy(), hour]).transform("mean").to_numpy()


def own_diurnal(k):
    """フリート自身の日周（ロジット空間の日内帯域の季節×時刻平均）を k 倍にし、日次エネルギーを保存"""
    return logit_daily(ZN + (k - 1) * DZ)


ph_specs = [("夜ピーク", a, 3) for a in (0.1, 0.2, 0.3)] + [("昼ピーク", a, 13) for a in (0.1, 0.2, 0.3)] + \
           [("夕方ピーク", a, 18) for a in (0.1, 0.2, 0.3)] + [("位相の掃引", 0.2, h) for h in (0, 6, 9, 12, 15, 21)]
prow = []
for lab, a, h0 in ph_specs:
    y = phase_series(a, h0)
    st = stats_series(y)
    r, _ = run_price(y)
    prow.append({"区分": lab, "仕様": f"a={a:g}, h0={h0}時", "a": a, "h0": h0, **st, **r})
    print(f"  位相 {lab} a={a} h0={h0}: R {st['実現の日内分散比R']:.2f} 日周振幅 {st['日周振幅(max−min)/平均']:.2f}  PF {r['完全予見粗利(円/kW-年)']:.0f}"
          f"  β {r['β風力→TB4h_夏']:+.3f}/{r['β風力→TB4h_冬']:+.3f}/{r['β風力→TB4h_不需要期']:+.3f}")
for k in (3.0, 6.0):
    y = own_diurnal(k)
    st = stats_series(y)
    r, _ = run_price(y)
    prow.append({"区分": "フリート自身の日周×k", "仕様": f"k={k:g}", "a": np.nan, "h0": np.nan, **st, **r})
    print(f"  フリートの日周×{k}: R {st['実現の日内分散比R']:.2f} 日周振幅 {st['日周振幅(max−min)/平均']:.2f}  PF {r['完全予見粗利(円/kW-年)']:.0f}")
ph = pd.DataFrame(prow)
ph["ΔPF(%)"] = (ph["完全予見粗利(円/kW-年)"] / BASE_PF - 1) * 100
ph["同じRの一様増幅のΔPF(%)"] = [(uni_at(R, "完全予見粗利(円/kW-年)") / BASE_PF - 1) * 100 for R in ph["実現の日内分散比R"]]
ph["ΔPF/(R−1)（位相）"] = ph["ΔPF(%)"] / (ph["実現の日内分散比R"] - 1)
ph["ΔPF/(R−1)（一様）"] = ph["同じRの一様増幅のΔPF(%)"] / (ph["実現の日内分散比R"] - 1)
ph["同じRの一様増幅（確率成分）のΔPF(%)"] = [(uni_at(R, "完全予見粗利(円/kW-年)", uni_ns) / BASE_PF - 1) * 100 for R in ph["実現の日内分散比R"]]
ph["ΔPF/(R−1)（一様・確率成分）"] = ph["同じRの一様増幅（確率成分）のΔPF(%)"] / (ph["実現の日内分散比R"] - 1)
for s in SEASONS:
    ph[f"Δβ_{SLAB[s]}"] = ph[f"β風力→TB4h_{SLAB[s]}"] - base_r[f"β風力→TB4h_{SLAB[s]}"]
    ph[f"同じRの一様増幅のΔβ_{SLAB[s]}"] = [uni_at(R, f"β風力→TB4h_{SLAB[s]}") - base_r[f"β風力→TB4h_{SLAB[s]}"] for R in ph["実現の日内分散比R"]]
ph.round(4).to_csv(os.path.join(PROC, "spatial_dispersion_v3_phase.csv"), index=False)
print(ph[["区分", "仕様", "実現の日内分散比R", "系統的日周の比率(%)", "日周振幅(max−min)/平均", "下限張り付き(h/年)", "TB4h中央値", "完全予見粗利(円/kW-年)",
          "ΔPF(%)", "同じRの一様増幅のΔPF(%)", "Δβ_夏", "Δβ_冬", "Δβ_不需要期", "同じRの一様増幅のΔβ_夏"]].round(3).to_string(index=False))

# ======================================================================
# (D) 価格過程の検証
# ======================================================================
est["p_mod"] = predict_A(est, theta=1.0)
m_act, m_mod = metrics26(est, "p_hokkaido").mean(), metrics26(est, "p_mod").mean()
tb_act, tb_mod = tb4_daily(est, "p_hokkaido"), tb4_daily(est, "p_mod")
val = []
for lab, col in (("下限張り付き(h/年)", "床(≤0.01円)時間"), ("TB4h中央値", "TB4h中央値"), ("p05", "p05"), ("p95", "p95"), ("完全予見粗利(円/kW-年)", "PF価値(円/kW-年)")):
    val.append({"表": "(i) 価格指標", "項目": lab, "実績": float(m_act[col]), "モデル": float(m_mod[col]), "差": float(m_act[col] - m_mod[col])})
ra, rm, rd = wind_coef(tb_act), wind_coef(tb_mod), wind_coef(tb_act - tb_mod)
for s in SEASONS:
    k = f"wind_{s}"
    val.append({"表": "(i) 風力日量→TB4h（FY・季節FE）", "項目": SLAB[s], "実績": ra[k]["b"], "実績SE": ra[k]["se"], "実績p": ra[k]["p"],
                "モデル": rm[k]["b"], "モデルSE": rm[k]["se"], "モデルp": rm[k]["p"], "差": rd[k]["b"], "差SE": rd[k]["se"], "差p": rd[k]["p"], "ν": rd[k]["nu"]})
cor = pd.DataFrame({"a": tb_act, "m": tb_mod})
cor["cell"] = (cor.index.year - (cor.index.month < 4)).astype(str) + cor.index.month.map(SEASON_MAP)
dc = cor[["a", "m"]] - cor.groupby("cell")[["a", "m"]].transform("mean")
for s in SEASONS:
    mm = cor.index.month.map(SEASON_MAP) == s
    val.append({"表": "(i) 日次TB4h の実績とモデルの相関（年度×季節内）", "項目": SLAB[s], "実績": float(np.corrcoef(dc.loc[mm, "a"], dc.loc[mm, "m"])[0, 1]),
                "モデル": np.nan, "差": np.nan, "注": f"SD比 実績/モデル {dc.loc[mm, 'a'].std() / dc.loc[mm, 'm'].std():.2f}"})

# (ii) 日内SD への感応度
dd = D0.copy()
sys_tb4 = tb4_daily(est, "p_system")
EXTRA = pd.DataFrame({"dem_isd": daily_sd_intra(DEM_H), "sol_isd": daily_sd_intra(SOL_H)}).reindex(dd.index)
EXTRA["dwind_abs"] = dd["wind"].diff().abs().fillna(0.0)
EXTRA["wind_sq"] = dd["wind"] ** 2
EXTRA_SYS = EXTRA.assign(sys_tb4=sys_tb4.reindex(dd.index))
SPECS = [("FY・季節FE", dict(isd=True), [f"isd_{s}" for s in SEASONS]),
         ("追加統制", dict(isd=True, extra=EXTRA), [f"isd_{s}" for s in SEASONS]),
         ("追加統制＋システムプライスTB4h（参考）", dict(isd=True, extra=EXTRA_SYS), [f"isd_{s}" for s in SEASONS]),
         ("年月FE・夏を7-8月と9月に分割", dict(isd=True, ymfe=True, split_sep=True), ["isd_夏7-8", "isd_9月", "isd_冬", "isd_春秋"]),
         ("年月FE・追加統制・夏を分割", dict(isd=True, ymfe=True, split_sep=True, extra=EXTRA), ["isd_夏7-8", "isd_9月", "isd_冬", "isd_春秋"])]
def ewc_joint_cov(ya, ym, X, keys):
    """実績とモデルの係数の同時の EWC 共分散（同じ X・同じ日の影響関数を2列に積んで射影）。{key: 2×2 行列}"""
    Xn = X.to_numpy(float)
    XtXi = np.linalg.pinv(Xn.T @ Xn)
    ea = np.asarray(ya, float) - Xn @ (XtXi @ Xn.T @ np.asarray(ya, float))
    em = np.asarray(ym, float) - Xn @ (XtXi @ Xn.T @ np.asarray(ym, float))
    cols = list(X.columns)
    pos = (X.index - X.index[0]).days.to_numpy()
    T = int(pos.max()) + 1
    nu = int(np.floor(0.4 * T ** (2 / 3)))
    if (T, nu) not in _COS:
        t = np.arange(1, T + 1) - 0.5
        _COS[(T, nu)] = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, nu + 1), t) / T)
    out = {}
    for k in keys:
        w = Xn @ XtXi[cols.index(k)]
        G = np.zeros((T, 2))
        G[pos, 0], G[pos, 1] = w * ea, w * em
        L = _COS[(T, nu)] @ G
        out[k] = L.T @ L / nu
    return out, nu


def fieller(ba, bm, V, nu, level=0.95):
    """比 ba/bm の Fieller 区間。(ba − r·bm)² ≤ t²·(Vaa − 2r·Vam + r²·Vmm) を満たす r。有界でなければ (nan, nan)"""
    t2 = stats.t.ppf(0.5 + level / 2, nu) ** 2
    A = bm ** 2 - t2 * V[1, 1]
    B = -2 * (ba * bm - t2 * V[0, 1])
    C = ba ** 2 - t2 * V[0, 0]
    disc = B * B - 4 * A * C
    if A <= 0 or disc < 0:
        return np.nan, np.nan
    return (-B - np.sqrt(disc)) / (2 * A), (-B + np.sqrt(disc)) / (2 * A)


SENS, SENS_J = {}, {}
for lab, kw, keys in SPECS:
    X = design(**kw)
    fa = ewc_fit(tb_act.reindex(X.index), X, keys)
    fm = ewc_fit(tb_mod.reindex(X.index), X, keys)
    fd = ewc_fit((tb_act - tb_mod).reindex(X.index), X, keys)
    SENS[lab] = (fa, fm)
    SENS_J[lab] = ewc_joint_cov(tb_act.reindex(X.index), tb_mod.reindex(X.index), X, keys)
    for k in keys:
        nm = k.replace("isd_", "").replace("春秋", "不需要期")
        val.append({"表": f"(ii) 風力の日内SD(GW)→TB4h：{lab}", "項目": nm, "実績": fa[k]["b"], "実績SE": fa[k]["se"], "実績p": fa[k]["p"],
                    "モデル": fm[k]["b"], "モデルSE": fm[k]["se"], "モデルp": fm[k]["p"], "差": fd[k]["b"], "差SE": fd[k]["se"], "差p": fd[k]["p"], "ν": fd[k]["nu"]})
vt = pd.DataFrame(val)
vt.round(4).to_csv(os.path.join(PROC, "spatial_dispersion_v3_validation.csv"), index=False)
print("\n(D) 価格過程の検証")
print(vt.round(3).to_string(index=False))

# (iii) 感応度比による補正（参考値）
corr_rows = []
targets = tab[tab["区分"].isin(["旧版（加法・打ち切り）", "ロジット一様", "ロジット帯域別", "ロジット一様・確率成分（主）", "ロジット帯域別・確率成分"])]
for spec in ("FY・季節FE", "追加統制"):
    fa, fm = SENS[spec]
    VJ, nuJ = SENS_J[spec]
    ratio, rlo, rhi, flo, fhi = {}, {}, {}, {}, {}
    for s in SEASONS:
        k = f"isd_{s}"
        tq = stats.t.ppf(0.975, fa[k]["nu"])
        ratio[s] = fa[k]["b"] / fm[k]["b"]
        rlo[s] = (fa[k]["b"] - tq * fa[k]["se"]) / fm[k]["b"]
        rhi[s] = (fa[k]["b"] + tq * fa[k]["se"]) / fm[k]["b"]
        assert abs(np.sqrt(VJ[k][0, 0]) - fa[k]["se"]) < 1e-9 and abs(np.sqrt(VJ[k][1, 1]) - fm[k]["se"]) < 1e-9
        flo[s], fhi[s] = fieller(fa[k]["b"], fm[k]["b"], VJ[k], nuJ)
    for _, rr in targets.iterrows():
        d = {s: rr[f"完全予見粗利_{SLAB[s]}"] - base_r[f"完全予見粗利_{SLAB[s]}"] for s in SEASONS}
        out = {"感応度の仕様": spec, "区分": rr["区分"], "仕様": rr["仕様"], "実現の日内分散比R": rr["実現の日内分散比R"],
               "確率成分の日内分散比R_ns": rr["確率成分の日内分散比R_ns"], "モデルのΔPF": sum(d.values()),
               "モデルのΔPF(%)": sum(d.values()) / BASE_PF * 100}
        for s in SEASONS:
            out[f"モデルのΔPF_{SLAB[s]}"] = d[s]
            out[f"感応度比_{SLAB[s]}"] = ratio[s]
            out[f"感応度比95%下_{SLAB[s]}"] = rlo[s]
            out[f"感応度比95%上_{SLAB[s]}"] = rhi[s]
            out[f"感応度比Fieller95%下_{SLAB[s]}"] = flo[s]
            out[f"感応度比Fieller95%上_{SLAB[s]}"] = fhi[s]
        for lab, ss in (("全季節", SEASONS), ("夏のみ", ["夏"])):
            c = sum(d[s] * (ratio[s] if s in ss else 1.0) for s in SEASONS)
            lo_ = sum(d[s] * (min(rlo[s], rhi[s]) if s in ss else 1.0) for s in SEASONS)
            hi_ = sum(d[s] * (max(rlo[s], rhi[s]) if s in ss else 1.0) for s in SEASONS)
            out[f"補正後ΔPF(%)_{lab}"] = c / BASE_PF * 100
            out[f"補正後ΔPF(%)_{lab}_95%下"] = lo_ / BASE_PF * 100
            out[f"補正後ΔPF(%)_{lab}_95%上"] = hi_ / BASE_PF * 100
            # Fieller（モデル係数の誤差も含む）。d[s] の符号に応じて下限・上限を入れ替える。有界でない季節があれば NaN
            flo_ = sum((min(d[s] * flo[s], d[s] * fhi[s]) if s in ss else d[s]) for s in SEASONS)
            fhi_ = sum((max(d[s] * flo[s], d[s] * fhi[s]) if s in ss else d[s]) for s in SEASONS)
            out[f"補正後ΔPF(%)_{lab}_Fieller95%下"] = flo_ / BASE_PF * 100
            out[f"補正後ΔPF(%)_{lab}_Fieller95%上"] = fhi_ / BASE_PF * 100
        corr_rows.append(out)
corr = pd.DataFrame(corr_rows)
corr.round(4).to_csv(os.path.join(PROC, "spatial_dispersion_v3_correction.csv"), index=False)
print("\n(D)(iii) 感応度比による補正（参考値）")
print(corr[["感応度の仕様", "仕様", "実現の日内分散比R", "モデルのΔPF(%)", "モデルのΔPF_夏", "モデルのΔPF_冬", "モデルのΔPF_不需要期", "感応度比_夏", "感応度比_冬", "感応度比_不需要期",
            "補正後ΔPF(%)_全季節", "補正後ΔPF(%)_全季節_95%下", "補正後ΔPF(%)_全季節_95%上", "補正後ΔPF(%)_夏のみ", "補正後ΔPF(%)_夏のみ_95%下", "補正後ΔPF(%)_夏のみ_95%上"]]
      .round(2).to_string(index=False))
print("  感応度比の Fieller 95%区間（モデル係数の誤差も含む。NaN は有界でない）:")
for spec in ("FY・季節FE", "追加統制"):
    r0 = corr[corr["感応度の仕様"] == spec].iloc[0]
    print(f"    {spec}: " + "、".join(f"{SLAB[s]} {r0[f'感応度比_{SLAB[s]}']:.2f}［{r0[f'感応度比Fieller95%下_{SLAB[s]}']:.2f}, {r0[f'感応度比Fieller95%上_{SLAB[s]}']:.2f}］"
                                     f"（実績の誤差のみ［{r0[f'感応度比95%下_{SLAB[s]}']:.2f}, {r0[f'感応度比95%上_{SLAB[s]}']:.2f}］）" for s in SEASONS))
print(corr.loc[corr["仕様"].str.contains("校正"), ["感応度の仕様", "仕様", "モデルのΔPF(%)", "補正後ΔPF(%)_夏のみ", "補正後ΔPF(%)_夏のみ_95%下", "補正後ΔPF(%)_夏のみ_95%上",
                                                "補正後ΔPF(%)_夏のみ_Fieller95%下", "補正後ΔPF(%)_夏のみ_Fieller95%上"]].round(2).to_string(index=False))

# ======================================================================
# 図
# ======================================================================
C_BLUE, C_ORG, C_TEAL, C_PUR = "#0079C2", "#D95B20", "#176871", "#7F4F9F"
XT = [1, 2, 3, 5, 7.5, 10, 20]
# 論文の本文幅（15.5cm）で載せるので幅6.1インチで作り、2つのパネルを縦に並べ、文字は8.5pt 以上にする。凡例は各パネルの下に置く。
# 日内分散比の測り方（確率成分・全成分）、日周の付与の振幅（0.1〜0.3）は図の注に書く
fig = plt.figure(figsize=(6.1, 8.6), layout="constrained")
sf_a, sf_b = fig.subfigures(2, 1, height_ratios=[1.1, 1.0], hspace=0.03)
ax = sf_a.subplots()
axes = [ax]
for lab, ls in (("下限", ":"), ("中央", "--"), ("上限", "--")):
    R = TARGET_NS[lab][2]
    ax.axvline(R, color="#9a9a9a", lw=1, ls=ls, zorder=0)
    ax.text(R, 0.02, f"校正の{lab}\n{R:.2f}", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8.5, color=GRAY,
            bbox=dict(fc="white", ec="none", pad=1))
ax.plot(uni_ns["確率成分の日内分散比R_ns"], (uni_ns["完全予見粗利(円/kW-年)"] / BASE_PF - 1) * 100, color=C_BLUE, lw=1.6, marker="o", ms=3.5,
        label="一様な増幅・確率成分（主）")
ax.plot(uni["実現の日内分散比R"], (uni["完全予見粗利(円/kW-年)"] / BASE_PF - 1) * 100, color="#7fb8e0", lw=1.1, ls="--", marker="o", ms=2.5,
        label="一様な増幅・全成分（日周も増幅）")
bsn = tab[tab["区分"] == "ロジット帯域別・確率成分"]
ax.scatter(bsn["確率成分の日内分散比R_ns"], bsn["ΔPF(%)"], s=34, marker="^", facecolor="white", edgecolor=C_BLUE, lw=1.4, zorder=3,
           label="帯域別の増幅・確率成分")
bs = tab[tab["区分"] == "ロジット帯域別"]
ax.scatter(bs["実現の日内分散比R"], bs["ΔPF(%)"], s=30, marker="^", facecolor="white", edgecolor="#7fb8e0", lw=1.2, zorder=3,
           label="帯域別の増幅・全成分")
ad = tab[tab["区分"] == "旧版（加法・打ち切り）"]
ax.scatter(ad["実現の日内分散比R"], ad["ΔPF(%)"], s=26, marker="s", color="#8c8c8c", zorder=3, label="参考：加法・打ち切り（数字は名目の倍率）")
for _, rr in ad.iterrows():
    ax.annotate(rr["仕様"].replace("名目λ=", "×"), (rr["実現の日内分散比R"], rr["ΔPF(%)"]), textcoords="offset points", xytext=(4, -9), fontsize=8.5, color=GRAY)
PH_LABEL = {"夜ピーク": "未明（3時）", "昼ピーク": "昼（13時）", "夕方ピーク": "夕方（18時）"}
for lab, c, mk in (("夜ピーク", C_TEAL, "D"), ("昼ピーク", C_ORG, "o"), ("夕方ピーク", C_PUR, "v")):
    pp = ph[ph["区分"] == lab]
    ax.scatter(pp["実現の日内分散比R"], pp["ΔPF(%)"], s=24, marker=mk, color=c, zorder=4,
               label=f"日周の付与：ピーク{PH_LABEL[lab]}")
ax.axhline(0, color="#bdbdbd", lw=0.8)
ax.set_xscale("log")
ax.set_xticks(XT)
ax.set_xticklabels([str(v) for v in XT])
ax.set_xlabel("日内分散比（実フリート=1、対数目盛）", color=GRAY, fontsize=9)
ax.set_ylabel("完全予見粗利の変化（実フリート比、%）", color=GRAY, fontsize=9)
ax.set_title("(a) 日内の分散と位相が完全予見粗利に与える効果", fontsize=9.5, loc="left")
ax.set_ylim(-8, 27)
sf_a.legend(*ax.get_legend_handles_labels(), fontsize=8.5, frameon=False, loc="outside lower center", ncol=2,
            handlelength=1.8, columnspacing=1.0, labelspacing=0.35)
ax = sf_b.subplots()
axes.append(ax)
for s, c, mk in (("夏", C_ORG, "o"), ("冬", C_BLUE, "s"), ("春秋", C_TEAL, "D")):
    ax.plot(uni_ns["確率成分の日内分散比R_ns"], uni_ns[f"β風力→TB4h_{SLAB[s]}"], color=c, lw=1.5, marker=mk, ms=3,
            label=SLAB[s])
    ax.plot(uni["実現の日内分散比R"], uni[f"β風力→TB4h_{SLAB[s]}"], color=c, lw=0.9, ls="--", alpha=0.6)
    ax.scatter([1.0], [ra[f"wind_{s}"]["b"]], marker=mk, s=36, facecolor="white", edgecolor=c, lw=1.3, zorder=4)
ax.plot([], [], color=GRAY, lw=1.5, label="実線：モデル価格・一様な増幅・確率成分")
ax.plot([], [], color=GRAY, lw=0.9, ls="--", label="破線：一様な増幅・全成分（日周も増幅）")
ax.scatter([], [], marker="o", s=36, facecolor="white", edgecolor=GRAY, lw=1.3, label="白抜き：実績の価格（FY2023〜25）")
ax.axhline(0, color="#999999", lw=1)
for lab in ("下限", "中央", "上限"):
    ax.axvline(TARGET_NS[lab][2], color="#9a9a9a", lw=1, ls=":", zorder=0)
ax.set_xscale("log")
ax.set_xticks(XT)
ax.set_xticklabels([str(v) for v in XT])
ax.set_xlabel("日内分散比（実フリート=1、対数目盛）", color=GRAY, fontsize=9)
ax.set_ylabel("風力→TB4h の係数（円/kWh per GWh/日）", color=GRAY, fontsize=9)
ax.set_title("(b) 風力の日次発電量の TB4h への係数", fontsize=9.5, loc="left")
sf_b.legend(*ax.get_legend_handles_labels(), fontsize=8.5, frameon=False, loc="outside lower center", ncol=2,
            handlelength=1.8, columnspacing=1.0, labelspacing=0.35)
for a_ in axes:
    a_.tick_params(colors=GRAY, labelsize=8.5)
    a_.xaxis.set_minor_formatter(plt.NullFormatter())
    for sp_ in ("top", "right"):
        a_.spines[sp_].set_visible(False)
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "spatial_dispersion_v3.png"), dpi=300)
print("\nsaved spatial_dispersion_v3_*.csv, spatial_dispersion_v3.png")
