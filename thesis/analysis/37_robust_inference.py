#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日次回帰（表6.2）の系列相関に頑健な推論と同月内の識別、冬の TB4h の上位・下位4時間への分解（5.2.3・6.2・6.5、ゼミ指摘1）

手法:
  (1) 表6.2 の仕様（24_vol_verification.py の右辺。季節×太陽光・風力の日次発電量（制御前, GWh/日）＋需要＋FY固定効果＋季節固定効果）
      を北海道・九州の日平均価格・TB4h・日内SD について OLS で再推定し、係数と HC3 SE が原稿・vol_regression_results.csv と一致することを確かめる。
  (2) 推論の比較: HC3（原稿）、Newey-West（Bartlett、ラグ7・14日、正規臨界値）、Andrews (1991) の AR(1) プラグイン自動帯域
      （係数ごとの影響関数系列に当てはめる。正規臨界値。パイロットの残差に当てはめる版も併記）、年月クラスタ（CR1、t(G−1)）、
      Lazarus, Lewis, Stock & Watson (2018, LLSW) の規則 S=⌈1.3T^{1/2}⌉ の NW に Kiefer & Vogelsang (2005) の固定b臨界値
      （位置モデルの帰無分布をシミュレーション）、および**主の推論法**として LLSW の EWC: 影響関数 ψ_t=(X'X)^{-1}x_t e_t を
      第II種離散余弦 √2·cos(πj(t−1/2)/T)（j=1..ν）に射影し、その2乗を等重みで平均して長期分散とする。ν=⌊0.4T^{2/3}⌋、t_ν 臨界値。
      欠測日（24時間そろわない日。北海道は 2018-09-07〜26 の20日）は暦日の格子上で ψ を0とする振幅変調法（Parzen 1963;
      Rho & Vogelsang 2019）で扱い、ラグ・余弦の時点は暦日で数える。標本の行を連続とみなす等間隔法の結果も併記する。
      冬の日だけの回帰は冬の日を詰めた等間隔法で計算する（暦日の格子では毎年9か月の空白が入るため）。
  (3) 設計に合わせた臨界値（ふるいブートストラップ、Bühlmann 1997）: 各仕様の X を固定し、同じ標本の主仕様の OLS 残差に
      当てはめた AR(p)（暦日、BIC、p≤60）と、季節別に復元抽出したイノベーションから帰無仮説（再エネ係数=0）の下の被説明変数を
      作る。各推論法の t 統計量の帰無分布から、EWC の p 値（p_EWC_ブート）と名目5%の両側検定の実効サイズを求める。
      季節交互作用の係数は影響関数が主にその季節の日に集中し（他の季節の日の寄与は北海道 TB4h で ψ² の2〜26%）、年の中で強弱をくり返すので、
      EWC・固定b の漸近分布が前提とする分散の時間的一様性を満たさない。そのため
      この補正を確認に使う。i.i.d. 正規誤差での実効サイズ（設計だけの効果）も1行出す。
  (4) 同月内の識別と仕様の頑健性: +曜日・祝日（S2）、S2 の季節FE→月FE（S3）、需要＋曜日・祝日＋年月FE（S4）、
      S4＋日平均価格の1〜7日ラグ（暦日、S5）、夏を7〜8月に限る4季節版、FY2023〜25 の主仕様と年月FE版、
      燃料危機期（FY2021〜22）を除く主仕様（表6.8）、2021年1月（JEPX の価格高騰。FY2020 なので燃料危機期の除外に含まれない）を
      除く S1・S3・S4、FGLS（暦日で準差分する Cochrane-Orcutt 反復。準差分後の回帰に EWC・NW をかけ直す）。祝日は「国民の祝日に関する法律」の
      規則（振替休日・国民の休日・2019〜21年の特例を含む）から作り、年末年始（12/29〜1/3）とお盆（8/13〜16）のダミーを加える。
  (5) 冬の TB4h（＝上位4時間平均−下位4時間平均）を上位・下位に分けた係数。主仕様のプール推定（表6.2 と整合）と、
      冬の日だけの回帰（太陽光・風力・需要・FY固定効果。10/5 の再計算の仕様）について、年月FE版・FY2023〜25 版・期間別を並べる。
      風力が冬の価格を比例的に下げるか（H0: 上位の係数 = 冬の上位・下位4時間の平均価格の比 r × 下位の係数）を、
      y = top4 − r·bot4 の回帰係数（右辺が共通なので β_top − r·β_bot に等しい）の EWC とブートストラップで検定する。
出力: data/processed/robust_inference_table62.csv（表6.2 の推論の比較）
      data/processed/robust_inference_specs.csv（仕様別の係数と推論）
      data/processed/robust_inference_winter_legs.csv（冬の上位・下位4時間への分解）
      data/processed/robust_inference_winter_proportional.csv（冬の比例的な引下げの検定）
      data/processed/robust_inference_size_mc.csv（推論法の実効サイズ）
      figures/hokkaido/robust_inference_ci.png（推論法・仕様別の95%信頼区間）
限界: 気温（HDD/CDD）は統制していない（data/raw に気温データがない）。ブートストラップの誤差過程は X と独立な AR(p) で、
      X と連動する分散や係数の周波数依存は再現しない。AR は OLS 残差に当てはめるので、生成した誤差の残差の自己相関は
      データよりわずかに低く（北海道 TB4h の1次で0.74 対0.76）、実効サイズと補正 p 値は歪みをやや小さめに示す。
      S5（価格ラグ）と FGLS はブートストラップしない（X が y に依存するため）。
"""
import logging
import os
import zlib
from datetime import date, timedelta

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.signal import lfilter
from matplotlib import font_manager
import matplotlib.pyplot as plt

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
SEED = 20261020
R_BOOT = int(os.environ.get("R_BOOT", "1999"))    # ふるいブートストラップの反復数
R_FB = int(os.environ.get("R_FB", "20000"))       # 固定b 帰無分布のシミュレーション回数

# 季節区分は 24_vol_verification.py と同一（夏=7-9月、冬=12-2月、不需要期（内部名 "春秋"）=3-6・10-11月）
SEASON_MAP = {7: "夏", 8: "夏", 9: "夏", 12: "冬", 1: "冬", 2: "冬",
              3: "春秋", 4: "春秋", 5: "春秋", 6: "春秋", 10: "春秋", 11: "春秋"}
MAIN_SEASONS = ["夏", "冬", "春秋"]
SLAB = {"夏": "夏", "冬": "冬", "春秋": "不需要期", "夏78": "夏(7-8月)", "端境": "9月"}
SRCLAB = {"solar": "太陽光", "wind": "風力"}
KEYS = [f"{src}_{s}" for s in MAIN_SEASONS for src in ("solar", "wind")]
YLAB = {"mean_p": "日平均価格", "tb4": "TB4h", "sd": "日内SD", "top4": "上位4時間平均", "bot4": "下位4時間平均"}
AREAS = [("hokkaido", "p_hokkaido", "北海道"), ("kyushu", "p_kyushu", "九州")]
METHODS = ["HC3", "NW7", "NW14", "NWAndrews", "NWAndrews残差", "クラスタ", "NWfb", "EWC"]

# 原稿 表6.2（水準・TB4h）と 6.2 本文（日内SD の2値）の係数。再現の確認に使う
MANUSCRIPT = {
    ("hokkaido", "mean_p"): dict(zip(KEYS, [-0.406, -0.245, -0.761, -0.353, -0.351, -0.355])),
    ("hokkaido", "tb4"): dict(zip(KEYS, [0.033, -0.156, -0.807, -0.363, 0.233, -0.067])),
    ("kyushu", "mean_p"): dict(zip(KEYS, [-0.065, -0.013, -0.062, -0.272, -0.055, 0.065])),
    ("kyushu", "tb4"): dict(zip(KEYS, [0.027, 0.126, 0.123, -0.349, 0.104, 0.275])),
    ("hokkaido", "sd"): {"solar_春秋": 0.09},
    ("kyushu", "sd"): {"wind_春秋": 0.115},
}


# ---------------------------------------------------------------- 祝日（国民の祝日に関する法律の規則から作成）
EQUINOX = {2016: ((3, 20), (9, 22)), 2017: ((3, 20), (9, 23)), 2018: ((3, 21), (9, 23)), 2019: ((3, 21), (9, 23)),
           2020: ((3, 20), (9, 22)), 2021: ((3, 20), (9, 23)), 2022: ((3, 21), (9, 23)), 2023: ((3, 21), (9, 23)),
           2024: ((3, 20), (9, 22)), 2025: ((3, 20), (9, 23)), 2026: ((3, 20), (9, 23))}


def _nth_monday(y, m, n):
    first = date(y, m, 1)
    return first + timedelta(days=(0 - first.weekday()) % 7 + 7 * (n - 1))


def jp_holidays(y):
    """国民の祝日＋国民の休日＋振替休日（2016〜2026年）"""
    h = {date(y, 1, 1), _nth_monday(y, 1, 2), date(y, 2, 11), date(y, *EQUINOX[y][0]), date(y, 4, 29),
         date(y, 5, 3), date(y, 5, 4), date(y, 5, 5), _nth_monday(y, 9, 3), date(y, *EQUINOX[y][1]),
         date(y, 11, 3), date(y, 11, 23)}
    if y <= 2018:
        h.add(date(y, 12, 23))           # 天皇誕生日（平成）
    elif y >= 2020:
        h.add(date(y, 2, 23))            # 天皇誕生日（令和）。2019年はなし
    h.add({2020: date(2020, 7, 23), 2021: date(2021, 7, 22)}.get(y, _nth_monday(y, 7, 3)))   # 海の日（五輪特例）
    h.add({2020: date(2020, 8, 10), 2021: date(2021, 8, 8)}.get(y, date(y, 8, 11)))          # 山の日
    h.add({2020: date(2020, 7, 24), 2021: date(2021, 7, 23)}.get(y, _nth_monday(y, 10, 2)))  # 体育の日／スポーツの日
    if y == 2019:
        h |= {date(2019, 5, 1), date(2019, 10, 22)}                                            # 即位の日・即位礼正殿の儀
    sandwich = {d + timedelta(days=1) for d in h
                if (d + timedelta(days=2)) in h and (d + timedelta(days=1)) not in h}          # 国民の休日
    h |= sandwich
    subs = set()
    for d in sorted(h):                                                                        # 振替休日
        if d.weekday() == 6:
            n = d + timedelta(days=1)
            while n in h or n in subs:
                n += timedelta(days=1)
            subs.add(n)
    return h | subs


HOLIDAYS = set().union(*[jp_holidays(y) for y in range(2016, 2027)])


def JAN21(idx):
    """2021年1月の日（JEPX の価格高騰。北海道・九州とも TB4h の月平均が他の年の1月の約8倍）"""
    return (idx.year == 2021) & (idx.month == 1)


def calendar_dummies(idx):
    out = pd.DataFrame(index=idx)
    for k in range(1, 7):
        out[f"dow{k}"] = (idx.dayofweek == k).astype(float)
    out["holiday"] = np.array([d.date() in HOLIDAYS for d in idx], dtype=float)
    m, dd = idx.month, idx.day
    out["yearend"] = (((m == 12) & (dd >= 29)) | ((m == 1) & (dd <= 3))).astype(float)
    out["obon"] = ((m == 8) & (dd >= 13) & (dd <= 16)).astype(float)
    return out


# ---------------------------------------------------------------- データ（24_vol_verification.build_daily と同一＋上位・下位4時間）
def build_daily(area, pcol):
    p = pd.read_csv(os.path.join(PROC, f"{area}_hourly_panel.csv"), parse_dates=["ts"])
    p = p.dropna(subset=[pcol]).copy()
    p["day"] = p["ts"].dt.normalize()
    p["hour"] = p["ts"].dt.hour
    cnt = p.groupby("day")["hour"].count()
    p = p[p["day"].isin(cnt[cnt == 24].index)]
    p["solar_pre"] = p["solar"].fillna(0) + p["solar_curt"].fillna(0)
    p["wind_pre"] = p["wind"].fillna(0) + p["wind_curt"].fillna(0)
    P = p.pivot(index="day", columns="hour", values=pcol)
    srt = np.sort(P.to_numpy(), axis=1)
    d = pd.DataFrame(index=P.index)
    d["mean_p"] = P.mean(axis=1)
    d["sd"] = P.std(axis=1)
    d["tb4"] = srt[:, -4:].mean(axis=1) - srt[:, :4].mean(axis=1)
    d["top4"] = srt[:, -4:].mean(axis=1)
    d["bot4"] = srt[:, :4].mean(axis=1)
    d["solar"] = p.groupby("day")["solar_pre"].sum() / 1000   # GWh/日
    d["wind"] = p.groupby("day")["wind_pre"].sum() / 1000
    d["demand"] = p.groupby("day")["demand"].sum(min_count=24) / 1000   # 需要が欠測の日（九州 2019-03-12〜31）は NaN にして除く
    d["fy"] = d.index.year - (d.index.month < 4).astype(int)
    d["season"] = d.index.month.map(SEASON_MAP)
    d = d[(d["fy"] >= 2016) & (d["fy"] <= 2025)].dropna()
    d.index.name = "day"
    return d


def dummies(s, prefix):
    out = pd.get_dummies(s, prefix=prefix, drop_first=True).astype(float)
    out.index = s.index
    return out


def design(d, spec, seasons=MAIN_SEASONS, season_col="season"):
    """spec: S1 主仕様 / S2 +曜日・祝日 / S3 S2の季節FE→月FE / S4 年月FE / S5 S4+日平均価格の1〜7日ラグ（暦日）
       W1・W4 は冬の日だけの回帰（太陽光・風力・需要＋FY固定効果／＋曜日・祝日＋年月FE）"""
    X = pd.DataFrame(index=d.index)
    if spec.startswith("W"):
        X["solar"] = d["solar"]
        X["wind"] = d["wind"]
    else:
        for s in seasons:
            m = (d[season_col] == s).astype(float)
            X[f"solar_{s}"] = d["solar"] * m
            X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    if spec in ("S2", "S3", "S4", "S5", "W4"):
        X = pd.concat([X, calendar_dummies(d.index)], axis=1)
    if spec in ("S1", "S2", "S3", "W1"):
        X = pd.concat([X, dummies(d["fy"], "fy")], axis=1)
    if spec in ("S1", "S2"):
        X = pd.concat([X, dummies(d[season_col], "ssn")], axis=1)
    if spec == "S3":
        X = pd.concat([X, dummies(pd.Series(d.index.month, index=d.index), "m")], axis=1)
    if spec in ("S4", "S5", "W4"):
        X = pd.concat([X, dummies(pd.Series(d.index.year * 100 + d.index.month, index=d.index), "ym")], axis=1)
    if spec == "S5":
        cal = d["mean_p"].reindex(pd.date_range(d.index.min(), d.index.max(), freq="D"))
        for L in range(1, 8):
            X[f"lag_mean_p{L}"] = cal.shift(L).reindex(d.index).to_numpy()
    X = X.loc[:, X.std() > 0]                          # 部分標本で定数になったダミーを落とす
    return sm.add_constant(X, has_constant="add")


# ---------------------------------------------------------------- 共分散推定
class Fit:
    """OLS と係数ごとの影響関数 ψ_t = (X'X)^{-1} x_t e_t。pos は推論に使う時点（暦日、欠測日は格子上で0）"""

    def __init__(self, y, X, keys, pos=None):
        self.cols = list(X.columns)
        self.keys = [k for k in keys if k in self.cols]
        Xn = X.to_numpy(float)
        yn = np.asarray(y, float)
        self.n, self.k = Xn.shape
        XtX_inv = np.linalg.inv(Xn.T @ Xn)
        self.beta = XtX_inv @ Xn.T @ yn
        self.e = yn - Xn @ self.beta
        self.rows = [self.cols.index(k) for k in self.keys]
        self.B = Xn @ XtX_inv[self.rows].T                       # n×m（ψ = B·e）
        self.P = XtX_inv @ Xn.T                                  # β̂ = P y
        self.Xn = Xn
        self.psi = self.B * self.e[:, None]
        self.h = np.einsum("ij,jk,ik->i", Xn, XtX_inv, Xn)       # てこ比（HC3 用）
        self.r2 = 1 - (self.e @ self.e) / ((yn - yn.mean()) @ (yn - yn.mean()))
        self.cal_pos = (X.index - X.index[0]).days.to_numpy()    # 暦日の位置（誤差の生成に使う）
        self.pos = self.cal_pos if pos is None else np.asarray(pos)
        self.T = int(self.pos.max()) + 1
        self.obs = np.zeros(self.T, bool)
        self.obs[self.pos] = True
        self.codes = pd.factorize(X.index.year * 100 + X.index.month)[0]
        self.G = self.codes.max() + 1
        self.cfac = self.G / (self.G - 1) * (self.n - 1) / (self.n - self.k)
        self.season = X.index.month.map(SEASON_MAP).to_numpy()

    def b(self):
        return pd.Series(self.beta[self.rows], index=self.keys)

    def grid_of(self, v):
        g = np.zeros((self.T,) + v.shape[1:])
        g[self.pos] = v
        return g

    def resid_rho1(self, e=None):
        eg = self.grid_of(self.e if e is None else e)
        both = self.obs[1:] & self.obs[:-1]
        return float(np.corrcoef(eg[1:][both], eg[:-1][both])[0, 1])

    def score_rho1(self):
        g = self.grid_of(self.psi)
        both = self.obs[1:] & self.obs[:-1]
        return np.array([np.corrcoef(g[1:, a][both], g[:-1, a][both])[0, 1] for a in range(g.shape[1])])


def autocov(grid, J):
    """Γ_j = Σ_t ψ_t ψ_{t−j}（列ごと, j=0..J）を FFT で"""
    T = grid.shape[0]
    nfft = 1 << int(np.ceil(np.log2(2 * T)))
    F = np.fft.rfft(grid, n=nfft, axis=0)
    return np.fft.irfft(F * np.conj(F), n=nfft, axis=0)[:J + 1]


def nw_var(ac, S):
    """Bartlett 窓 k(j/S)=1−j/S（|j|<S）の長期分散（和の形）。ac は autocov の出力"""
    J = min(int(np.ceil(S)) - 1, ac.shape[0] - 1)
    w = 1 - np.arange(1, J + 1) / S
    return ac[0] + 2 * (w[:, None] * ac[1:J + 1]).sum(axis=0)


def ar1_on_grid(v, obs):
    both = obs[1:] & obs[:-1]
    v1, v0 = v[1:][both], v[:-1][both]
    return float(np.clip((v1 @ v0) / (v0 @ v0), -0.97, 0.97))


def andrews_S_from_rho(rho, n):
    """Andrews (1991) の Bartlett 窓の AR(1) プラグイン帯域 S_T = 1.1447(α(1)n)^{1/3}、α(1)=4ρ²/((1−ρ)²(1+ρ)²)"""
    alpha = 4 * rho ** 2 / ((1 - rho) ** 2 * (1 + rho) ** 2)
    return max(1.0, 1.1447 * (alpha * n) ** (1 / 3))


_COS = {}


def ewc_var(grid, nu):
    """LLSW (2018) 式(10): Λ_j = √(2/T) Σ_t z_t cos(πj(t−1/2)/T)、Ω = (1/ν) Σ Λ_j²。和の形にするため √2 Σ ψ_t cos(・)"""
    T = grid.shape[0]
    if (T, nu) not in _COS:
        t = np.arange(1, T + 1) - 0.5
        _COS[(T, nu)] = np.sqrt(2.0) * np.cos(np.pi * np.outer(np.arange(1, nu + 1), t) / T)
    L = _COS[(T, nu)] @ grid
    return (L ** 2).mean(axis=0)


def ewc_nu(T):
    return int(np.floor(0.4 * T ** (2 / 3)))


def llsw_S(T):
    return int(np.ceil(1.3 * np.sqrt(T)))


_FB = {}


def fixed_b_null(T, S, rng):
    """固定b 帰無分布: 位置モデル（i.i.d. 正規、定数項だけの回帰）で Bartlett S の NW t 統計量 |t| を R_FB 回シミュレーション"""
    if (T, S) not in _FB:
        out = []
        for _ in range(R_FB // 500):
            u = rng.standard_normal((T, 500))
            e = u - u.mean(axis=0)
            out.append(np.abs(u.sum(axis=0)) / np.sqrt(nw_var(autocov(e, S), S)))
        _FB[(T, S)] = np.sort(np.concatenate(out))
    return _FB[(T, S)]


def kv_cv975(b):
    """Kiefer & Vogelsang (2005) の Bartlett 窓・97.5% 分位の多項式近似（検算用）"""
    return 1.9600 + 2.9694 * b + 0.4160 * b ** 2 - 0.5324 * b ** 3


def p_from_null(tabs, null_sorted):
    return 1 - np.searchsorted(null_sorted, tabs, side="left") / len(null_sorted)


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


def se_all(fit, e, bk=None):
    """残差 e（標本順）から推論法別の SE を返す。fit は X・時点・クラスタの情報だけ使う"""
    psi = fit.B * e[:, None]
    grid = fit.grid_of(psi)
    m = psi.shape[1]
    out = {"HC3": np.sqrt(((psi / (1 - fit.h)[:, None]) ** 2).sum(axis=0))}
    n = fit.n
    S_and = np.array([andrews_S_from_rho(ar1_on_grid(grid[:, a], fit.obs), n) for a in range(m)])
    bw_res = int(np.floor(andrews_S_from_rho(ar1_on_grid(fit.grid_of(e), fit.obs), n)))   # パイロットと同じ（残差の AR(1)）
    S_ll = llsw_S(fit.T)
    ac = autocov(grid, int(max(S_and.max(), bw_res + 1, S_ll, 15)) + 1)
    out["NW7"] = np.sqrt(nw_var(ac, 8))                 # 「ラグ L」は重み 1−j/(L+1)（statsmodels の maxlags=L と同じ）
    out["NW14"] = np.sqrt(nw_var(ac, 15))
    out["NWAndrews"] = np.array([np.sqrt(nw_var(ac[:, [a]], S_and[a]))[0] for a in range(m)])
    out["NWAndrews残差"] = np.sqrt(nw_var(ac, bw_res + 1))
    sums = np.zeros((fit.G, m))
    np.add.at(sums, fit.codes, psi)
    out["クラスタ"] = np.sqrt(fit.cfac * (sums ** 2).sum(axis=0))
    out["NWfb"] = np.sqrt(nw_var(ac, S_ll))
    out["EWC"] = np.sqrt(ewc_var(grid, ewc_nu(fit.T)))
    return out, S_and, bw_res


def ref_p(method, tabs, fit, rng):
    """推論法ごとの参照分布による両側 p 値"""
    if method == "EWC":
        return 2 * stats.t.sf(tabs, ewc_nu(fit.T))
    if method == "クラスタ":
        return 2 * stats.t.sf(tabs, fit.G - 1)
    if method == "NWfb":
        return p_from_null(tabs, fixed_b_null(fit.T, llsw_S(fit.T), rng))
    return 2 * stats.norm.sf(tabs)


def ref_cv(method, fit, rng):
    if method == "EWC":
        return stats.t.ppf(0.975, ewc_nu(fit.T))
    if method == "クラスタ":
        return stats.t.ppf(0.975, fit.G - 1)
    if method == "NWfb":
        return float(np.quantile(fixed_b_null(fit.T, llsw_S(fit.T), rng), 0.95))
    return stats.norm.ppf(0.975)


def inference(fit, rng):
    b = fit.b().to_numpy()
    se, S_and, bw_res = se_all(fit, fit.e)
    res = pd.DataFrame(index=fit.keys)
    res["推定値"] = b
    for mth in METHODS:
        res[f"SE_{mth}"] = se[mth]
        res[f"p_{mth}"] = ref_p(mth, np.abs(b) / se[mth], fit, rng)
    res["Andrews帯域"] = S_and
    res["Andrews帯域_残差"] = bw_res
    res["EWC_ν"] = ewc_nu(fit.T)
    res["NWfb_S"] = llsw_S(fit.T)
    res["NWfb_5%臨界値"] = ref_cv("NWfb", fit, rng)
    res["クラスタ数"] = fit.G
    return res


# ---------------------------------------------------------------- ふるいブートストラップ（設計に合わせた帰無分布）
def fit_ar_bic(eg, obs, pmax=60):
    """暦日の格子上の残差に AR(p) を OLS で当てはめ、BIC で p を選ぶ（全ラグが観測される日のみ、共通の標本で比較）"""
    T = len(eg)
    full = np.array([obs[t - pmax:t + 1].all() if t >= pmax else False for t in range(T)])
    tt = np.where(full)[0]
    if len(tt) < 200:                                   # 冬だけの標本など、60日の連続が足りない場合は p≤20
        pmax = 20
        full = np.array([obs[t - pmax:t + 1].all() if t >= pmax else False for t in range(T)])
        tt = np.where(full)[0]
    best = None
    for p in range(1, pmax + 1):
        Y = eg[tt]
        Z = np.column_stack([eg[tt - j] for j in range(1, p + 1)])
        phi = np.linalg.lstsq(Z, Y, rcond=None)[0]
        u = Y - Z @ phi
        bic = len(Y) * np.log(u @ u / len(Y)) + np.log(len(Y)) * p
        if best is None or bic < best[0]:
            best = (bic, p, phi, u, tt)
    return best[1:]


def boot_null(fit, base, rng, R=None, dgp="ar"):
    """X（fit）を固定し、base（同じ標本の主仕様）の残差に当てはめた AR(p) で帰無の y を作り、推論法別の |t| を返す"""
    R = R_BOOT if R is None else R
    Tc = int(base.cal_pos.max()) + 1
    obs_c = np.zeros(Tc, bool)
    obs_c[base.cal_pos] = True
    eg = np.zeros(Tc)
    eg[base.cal_pos] = base.e
    p, phi, u, tt = fit_ar_bic(eg, obs_c)
    ssn_c = np.empty(Tc, dtype=object)
    ssn_c[base.cal_pos] = base.season
    # 欠測日の季節は前後から補う（イノベーションの抽出だけに使う）
    ssn_c = pd.Series(ssn_c).ffill().bfill().to_numpy()
    burn = 730
    if dgp == "iid_normal":
        E = rng.standard_normal((Tc, R))
    else:
        innov = np.empty((Tc + burn, R))
        innov[:burn] = rng.choice(u, (burn, R))
        for s in np.unique(ssn_c):
            msk = np.where(ssn_c == s)[0] + burn
            pool = u[ssn_c[tt] == s]
            innov[msk] = rng.choice(pool if len(pool) > 30 else u, (len(msk), R))
        E = lfilter([1.0], np.concatenate([[1.0], -phi]), innov, axis=0)[burn:]
    # fit と base は同じ標本（同じ日）なので暦日の位置は共通
    Ys = E[fit.cal_pos]
    BH = fit.P @ Ys
    tabs = {m: np.empty((R, len(fit.keys))) for m in METHODS}
    rho_b = []
    for r in range(R):
        e = Ys[:, r] - fit.Xn @ BH[:, r]
        se, _, _ = se_all(fit, e)
        bk = np.abs(BH[fit.rows, r])
        for m in METHODS:
            tabs[m][r] = bk / se[m]
        if r < 200:                                       # 生成した誤差の持続性がデータに見合うかの確認
            rho_b.append(fit.resid_rho1(e))
    return tabs, {"AR次数p": p, "AR係数和": float(phi.sum()), "ブート残差ρ1": float(np.mean(rho_b)),
                  "データ残差ρ1": fit.resid_rho1()}


def boot_summary(fit, base, rng, label, R=None, dgp="ar"):
    """ブートストラップの p 値（EWC）と各推論法の実効サイズ。乱数は設計（X の列・主仕様の残差・誤差過程）ごとに固定し、
    同じ設計を別の表で使っても同じ値になるようにする"""
    key = zlib.crc32(base.e.tobytes() + "|".join(fit.cols).encode() + dgp.encode())
    tabs, info = boot_null(fit, base, np.random.default_rng([SEED, key]), R=R, dgp=dgp)
    b = fit.b().to_numpy()
    se, _, _ = se_all(fit, fit.e)
    t_obs = np.abs(b) / se["EWC"]
    Rn = tabs["EWC"].shape[0]
    p_boot = (1 + (tabs["EWC"] >= t_obs[None, :]).sum(axis=0)) / (Rn + 1)
    size_rows = []
    for m in METHODS:
        cv = ref_cv(m, fit, rng)
        rej = (tabs[m] > cv).mean(axis=0)
        for i, k in enumerate(fit.keys):
            size_rows.append({**label, "誤差過程": dgp, "推論法": m, "係数": k, "棄却率(名目5%)": rej[i], "反復数": Rn, **info})
    q95 = np.quantile(tabs["EWC"], 0.95, axis=0)
    return pd.Series(p_boot, index=fit.keys), pd.Series(q95, index=fit.keys), size_rows, info


# ---------------------------------------------------------------- FGLS（暦日の Cochrane-Orcutt 反復）
def fgls_co(y, X, keys, maxit=100, tol=1e-8):
    pos = (X.index - X.index[0]).days.to_numpy()
    Xn, yn = X.to_numpy(float), np.asarray(y, float)
    idx_of = {p: i for i, p in enumerate(pos)}
    prev = np.array([idx_of.get(p - 1, -1) for p in pos])
    m = prev >= 0
    beta = np.linalg.lstsq(Xn, yn, rcond=None)[0]
    rho = 0.0
    for _ in range(maxit):
        e = yn - Xn @ beta
        rho_new = float(e[m] @ e[prev[m]] / (e[prev[m]] @ e[prev[m]]))
        ys = yn[m] - rho_new * yn[prev[m]]
        Xs = Xn[m] - rho_new * Xn[prev[m]]
        beta = np.linalg.lstsq(Xs, ys, rcond=None)[0]
        if abs(rho_new - rho) < tol:
            rho = rho_new
            break
        rho = rho_new
    Xs_df = pd.DataFrame(Xs, columns=X.columns, index=X.index[m])
    fit = Fit(ys, Xs_df, keys)
    return fit, rho


# ================================================================ 実行
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
D = {area: build_daily(area, pcol) for area, pcol, _ in AREAS}
ALAB = {a: l for a, _, l in AREAS}

print("=== 標本 ===")
for area, d in D.items():
    full = pd.date_range(d.index.min(), d.index.max(), freq="D")
    miss = full.difference(d.index)
    print(f"{area}: {len(d)}日（暦日 {len(full)}）、欠測 {len(miss)}日"
          + (f"（{miss.min():%Y-%m-%d}〜{miss.max():%Y-%m-%d}）" if len(miss) else ""))
nhol = [d for d in HOLIDAYS if date(2016, 4, 1) <= d <= date(2026, 3, 31)]
print("祝日（国民の祝日・国民の休日・振替休日）: FY2016〜25 で", len(nhol), "日、うち平日", sum(d.weekday() < 5 for d in nhol), "日")
T0 = len(pd.date_range("2016-04-01", "2026-03-31"))
nb = fixed_b_null(T0, llsw_S(T0), rng)
print(f"固定b（T={T0}, S={llsw_S(T0)}, b={llsw_S(T0)/T0:.4f}）: シミュレーションの97.5%分位 {np.quantile(nb, 0.95):.3f}"
      f"、KV (2005) の多項式 {kv_cv975(llsw_S(T0)/T0):.3f}。EWC ν={ewc_nu(T0)}（t_ν の97.5%分位 {stats.t.ppf(0.975, ewc_nu(T0)):.3f}）")

size_all = []

# ---------- (1)(2)(3) 表6.2 の推論の比較
rows62 = []
old = pd.read_csv(os.path.join(PROC, "vol_regression_results.csv"))
old["y"] = old["被説明変数"].map({"水準: 日平均価格": "mean_p", "変動性: 日内SD": "sd", "変動性: TB4hスプレッド": "tb4"})
BASE = {}
for area, _, alab in AREAS:
    d = D[area]
    X = design(d, "S1")
    for y in ("mean_p", "tb4", "sd"):
        fit = Fit(d[y], X, KEYS)
        BASE[(area, "FY2016-25", y)] = fit
        res = inference(fit, rng)
        fit_es = Fit(d[y], X, KEYS, pos=np.arange(len(d)))         # 等間隔法（行を連続とみなす）
        res_es = inference(fit_es, rng)
        p_boot, q95, size_rows, info = boot_summary(fit, fit, rng, {"エリア": alab, "被説明変数": YLAB[y], "y": y,
                                                                    "仕様": "S1", "標本": "FY2016-25"})
        size_all += size_rows
        sm_hc3 = sm.OLS(d[y], X).fit(cov_type="HC3")
        o = old[(old["エリア"] == area) & (old["y"] == y)].set_index("係数")
        srho = fit.score_rho1()
        for i, k in enumerate(KEYS):
            r = {"エリア": alab, "被説明変数": YLAB[y], "y": y, "係数": k,
                 "電源": SRCLAB[k.split("_")[0]], "季節": SLAB[k.split("_")[1]],
                 "n": fit.n, "暦日T": fit.T, "R2": fit.r2, "残差ρ1": fit.resid_rho1(), "影響関数ρ1": srho[i]}
            r.update(res.loc[k].to_dict())
            r["p_EWC_ブート"] = p_boot[k]
            r["EWC_ブート95%臨界値"] = q95[k]
            r["AR次数p"] = info["AR次数p"]
            r["AR係数和"] = info["AR係数和"]
            r["ブート残差ρ1"] = info["ブート残差ρ1"]
            r["p_EWC_等間隔法"] = res_es.loc[k, "p_EWC"]
            r["p_NWAndrews_等間隔法"] = res_es.loc[k, "p_NWAndrews"]
            r["原稿の値"] = MANUSCRIPT.get((area, y), {}).get(k, np.nan)
            r["24の推定値"] = o.loc[k, "推定値"]
            r["24のHC3_SE"] = o.loc[k, "SE"]
            r["検算_statsmodelsHC3_SE"] = sm_hc3.bse[k]
            r["星_HC3"] = stars(res.loc[k, "p_HC3"])
            r["星_EWC"] = stars(res.loc[k, "p_EWC"])
            r["星_EWCブート"] = stars(p_boot[k])
            rows62.append(r)
    # 設計だけの効果: i.i.d. 正規誤差での実効サイズ（TB4h）
    _, _, size_rows, _ = boot_summary(BASE[(area, "FY2016-25", "tb4")], BASE[(area, "FY2016-25", "tb4")], rng,
                                      {"エリア": alab, "被説明変数": "TB4h", "y": "tb4", "仕様": "S1", "標本": "FY2016-25"},
                                      dgp="iid_normal")
    size_all += size_rows
t62 = pd.DataFrame(rows62)
assert np.allclose(t62["推定値"], t62["24の推定値"], atol=1e-10), "係数が 24 の出力と一致しない"
assert np.allclose(t62["SE_HC3"], t62["24のHC3_SE"], rtol=1e-8), "HC3 SE が 24 の出力と一致しない"
assert np.allclose(t62["SE_HC3"], t62["検算_statsmodelsHC3_SE"], rtol=1e-8)
# 九州は 2019-03-12〜31 の需要欠測日を除く修正（2026-10-20、24 と同じ）で v0.2 原稿の値から変わるので、再現の確認は北海道に限る
chk = t62.dropna(subset=["原稿の値"])
chk = chk[chk["エリア"] == ALAB["hokkaido"]]
nd = chk["原稿の値"].map(lambda v: len(f"{abs(v)}".split(".")[1]))
dev = np.array([abs(round(b, int(k)) - m) for b, k, m in zip(chk["推定値"], nd, chk["原稿の値"])])
assert dev.max() < 1e-9, "原稿の係数を再現しない"
print(f"\n=== 表6.2 の再現: 北海道の原稿の係数 {len(chk)} 個を表記の桁で再現（最大差 {dev.max():.4f}）、HC3 SE は 24 の出力と一致 ===")
t62.to_csv(os.path.join(PROC, "robust_inference_table62.csv"), index=False, encoding="utf-8-sig")

for (alab, ylab), g in t62.groupby(["エリア", "被説明変数"], sort=False):
    print(f"\n--- {alab} {ylab}  残差ρ1={g['残差ρ1'].iloc[0]:.3f}  影響関数ρ1={g['影響関数ρ1'].min():.2f}〜{g['影響関数ρ1'].max():.2f}"
          f"  EWC ν={int(g['EWC_ν'].iloc[0])}  NW固定b S={int(g['NWfb_S'].iloc[0])}（5%臨界値 {g['NWfb_5%臨界値'].iloc[0]:.3f}）"
          f"  ブートの AR(p) p={int(g['AR次数p'].iloc[0])}・係数和 {g['AR係数和'].iloc[0]:.3f}"
          f"・生成誤差の残差ρ1 {g['ブート残差ρ1'].iloc[0]:.3f} ---")
    tt = pd.DataFrame({"係数": g["電源"] + "・" + g["季節"], "推定値": g["推定値"].round(3)})
    for c in ["HC3", "NW7", "NW14", "NWAndrews", "NWAndrews残差", "クラスタ", "NWfb", "EWC"]:
        tt[c] = [f"{se:.3f}{stars(p)}" for se, p in zip(g[f"SE_{c}"], g[f"p_{c}"])]
    tt["帯域"] = g["Andrews帯域"].round(0).astype(int).to_numpy()
    tt["p_EWC"] = g["p_EWC"].round(3).to_numpy()
    tt["p_ブート"] = g["p_EWC_ブート"].round(3).to_numpy()
    tt["p_等間隔"] = g["p_EWC_等間隔法"].round(3).to_numpy()
    print(tt.to_string(index=False))

# ---------- (4) 仕様の頑健性
rows_sp = []
SPECS = {"S1": "主仕様（FY・季節FE＋需要）", "S2": "S1＋曜日・祝日", "S3": "S2 の季節FE→月FE",
         "S4": "年月FE＋需要＋曜日・祝日", "S5": "S4＋日平均価格の1〜7日ラグ"}
for area, _, alab in AREAS:
    d = D[area]
    d23 = d[d["fy"] >= 2023]
    dex = d[~d["fy"].isin([2021, 2022])]                 # 表6.8（燃料危機期を除外）と同じ標本
    dj = d[~JAN21(d.index)]                              # 2021年1月（JEPX の価格高騰。FY2020 で燃料危機期の除外に含まれない）を除く
    for y in ("mean_p", "tb4", "sd"):
        BASE[(area, "FY2023-25", y)] = Fit(d23[y], design(d23, "S1"), KEYS)
        BASE[(area, "除FY2021-22", y)] = Fit(dex[y], design(dex, "S1"), KEYS)
        BASE[(area, "除2021年1月", y)] = Fit(dj[y], design(dj, "S1"), KEYS)
        variants = [(sp_, "FY2016-25", d) for sp_ in ("S1", "S2", "S3", "S4", "S5")] + \
                   [("S1", "FY2023-25", d23), ("S4", "FY2023-25", d23), ("S1", "除FY2021-22", dex)] + \
                   [(sp_, "除2021年1月", dj) for sp_ in ("S1", "S3", "S4")]
        for sp_, smp, dd in variants:
            X = design(dd, sp_)
            ok = X.notna().all(axis=1)
            fit = Fit(dd.loc[ok, y], X[ok], KEYS)
            res = inference(fit, rng)
            label = {"エリア": alab, "被説明変数": YLAB[y], "y": y, "仕様": sp_, "標本": smp}
            if sp_ != "S5":
                p_boot, _, size_rows, info = boot_summary(fit, BASE[(area, smp, y)], rng, label)
                if sp_ in ("S4",) or smp == "FY2023-25":
                    size_all += size_rows
            else:
                p_boot = pd.Series(np.nan, index=KEYS)
            for k in KEYS:
                rows_sp.append({**label, "仕様の説明": SPECS[sp_], "係数": k, "n": fit.n, "R2": fit.r2,
                                "残差ρ1": fit.resid_rho1(), **res.loc[k].to_dict(), "p_EWC_ブート": p_boot[k]})
        # 夏を7〜8月に限る4季節版（9月を別の季節に分ける。他は主仕様と同じ）
        d4 = d.copy()
        d4["season4"] = np.where(d4.index.month.isin([7, 8]), "夏78", np.where(d4.index.month == 9, "端境", d4["season"]))
        X4 = design(d4, "S1", seasons=["夏78", "端境", "冬", "春秋"], season_col="season4")
        k4 = [f"{s}_{x}" for x in ("夏78", "端境") for s in ("solar", "wind")]
        fit = Fit(d4[y], X4, k4)
        res = inference(fit, rng)
        p_boot, _, _, _ = boot_summary(fit, BASE[(area, "FY2016-25", y)], rng, {})
        for k in k4:
            rows_sp.append({"エリア": alab, "被説明変数": YLAB[y], "y": y, "標本": "FY2016-25", "仕様": "S1-4季節",
                            "仕様の説明": "主仕様で夏を7〜8月に限り9月を別季節に", "係数": k, "n": fit.n, "R2": fit.r2,
                            "残差ρ1": fit.resid_rho1(), **res.loc[k].to_dict(), "p_EWC_ブート": p_boot[k]})
        # FGLS（暦日の Cochrane-Orcutt、準差分後に EWC・NW をかけ直す）
        fit, rho = fgls_co(d[y], design(d, "S1"), KEYS)
        res = inference(fit, rng)
        for k in KEYS:
            rows_sp.append({"エリア": alab, "被説明変数": YLAB[y], "y": y, "標本": "FY2016-25", "仕様": "FGLS",
                            "仕様の説明": "主仕様の FGLS（AR(1)、暦日の準差分）", "係数": k, "n": fit.n,
                            "R2": fit.r2, "残差ρ1": fit.resid_rho1(), "FGLS_ρ": rho, **res.loc[k].to_dict()})
sp = pd.DataFrame(rows_sp)
# 表6.8（vol_regression_results_ex21-22.csv）の係数を再現するか
ex = pd.read_csv(os.path.join(PROC, "vol_regression_results_ex21-22.csv"))
ex["y"] = ex["被説明変数"].map({"水準: 日平均価格": "mean_p", "変動性: 日内SD": "sd", "変動性: TB4hスプレッド": "tb4"})
ex["エリア"] = ex["エリア"].map(ALAB)
chk = sp[sp["標本"] == "除FY2021-22"].merge(ex, on=["エリア", "y", "係数"], suffixes=("", "_24"))
assert len(chk) == 36 and np.allclose(chk["推定値"], chk["推定値_24"], atol=1e-10), "表6.8 の係数を再現しない"
print("\n=== 表6.8（燃料危機期を除外）の係数を再現（36個） ===")
sp["電源"] = sp["係数"].str.split("_").str[0].map(SRCLAB)
sp["季節"] = sp["係数"].str.split("_").str[1].map(SLAB)
sp["星_EWC"] = sp["p_EWC"].map(stars)
sp["星_EWCブート"] = sp["p_EWC_ブート"].map(stars)
sp.to_csv(os.path.join(PROC, "robust_inference_specs.csv"), index=False, encoding="utf-8-sig")

print("\n=== 仕様の頑健性（推定値、EWC の星／ブートストラップの星） ===")
sp["表示"] = [f"{b:+.3f}{stars(p) or '-'}/{stars(q) if q == q else '.'}" for b, p, q in
              zip(sp["推定値"], sp["p_EWC"], sp["p_EWC_ブート"])]
sp["列"] = sp["標本"].str.replace("FY", "") + " " + sp["仕様"]
order = ["2016-25 S1", "2016-25 S2", "2016-25 S3", "2016-25 S4", "2016-25 S5", "2016-25 FGLS", "2023-25 S1", "2023-25 S4",
         "除2021-22 S1", "除2021年1月 S1", "除2021年1月 S3", "除2021年1月 S4"]
for (alab, ylab), g in sp[sp["係数"].isin(KEYS)].groupby(["エリア", "被説明変数"], sort=False):
    tt = g.pivot_table(index="係数", columns="列", values="表示", aggfunc="first").loc[KEYS, order]
    print(f"--- {alab} {ylab} ---")
    print(tt.to_string())
print("--- 夏を7〜8月に限った係数（4季節版）---")
print(sp[sp["仕様"] == "S1-4季節"][["エリア", "被説明変数", "係数", "表示", "p_HC3", "p_EWC"]].round(3).to_string(index=False))


# パイロット（p2_hac_identification.py の S4）との差の確認: 祝日の近似（土日＋年末年始＋GW＋お盆）で再現するか
def pilot_holiday(idx):
    m, dd = idx.month, idx.day
    h = (idx.dayofweek >= 5)
    h |= ((m == 12) & (dd >= 29)) | ((m == 1) & (dd <= 3))
    h |= (m == 5) & (dd >= 3) & (dd <= 5)
    h |= (m == 8) & (dd >= 13) & (dd <= 16)
    return h.astype(float)


print("\n=== パイロット S4（祝日の近似）の再現確認 ===")
for area, _, alab in AREAS:
    d = D[area]
    X = pd.DataFrame(index=d.index)
    for s in MAIN_SEASONS:
        m = (d["season"] == s).astype(float)
        X[f"solar_{s}"] = d["solar"] * m
        X[f"wind_{s}"] = d["wind"] * m
    X["demand"] = d["demand"]
    X = pd.concat([X, dummies(pd.Series(d.index.dayofweek, index=d.index), "dow")], axis=1)
    X["holiday"] = pilot_holiday(d.index)
    X = sm.add_constant(pd.concat([X, dummies(pd.Series(d.index.year * 100 + d.index.month, index=d.index), "ym")], axis=1))
    f = sm.OLS(d["tb4"], X).fit()
    print(alab, "TB4h（パイロットの祝日）:", {k: round(f.params[k], 3) for k in ("solar_冬", "wind_冬", "solar_春秋", "wind_春秋")})

print("\n=== FGLS: レビュー版（GLSAR・行を連続とみなす・準差分後 HAC maxlags=max(帯域,7)）の再現と暦日版 ===")
d = D["hokkaido"]
for y in ("mean_p", "tb4"):
    X = design(d, "S1")
    g = sm.GLSAR(d[y], X, rho=1).iterative_fit(maxiter=20)
    rho = float(np.atleast_1d(g.model.rho)[0])
    yt = d[y].to_numpy()[1:] - rho * d[y].to_numpy()[:-1]
    Xt = X.to_numpy()[1:] - rho * X.to_numpy()[:-1]
    f0 = sm.OLS(yt, Xt).fit()
    e = f0.resid
    r1 = float(e[1:] @ e[:-1] / (e[:-1] @ e[:-1]))
    bw = int(np.floor(andrews_S_from_rho(r1, len(e))))
    fh = sm.OLS(yt, Xt).fit(cov_type="HAC", cov_kwds={"maxlags": max(bw, 7)})
    j = list(X.columns).index("wind_冬")
    row = sp[(sp["エリア"] == "北海道") & (sp["y"] == y) & (sp["仕様"] == "FGLS") & (sp["係数"] == "wind_冬")].iloc[0]
    print(f"{YLAB[y]} 風力・冬: レビュー版 ρ={rho:.3f} b={f0.params[j]:+.3f} p_HAC={fh.pvalues[j]:.3f}"
          f" ／ 暦日版 ρ={row['FGLS_ρ']:.3f} b={row['推定値']:+.3f} p_EWC={row['p_EWC']:.3f} p_NWAndrews={row['p_NWAndrews']:.3f}")

# ---------- (5) 冬の TB4h の上位・下位4時間への分解
rows_w = []
for area, _, alab in AREAS:
    d = D[area]
    w = d[d["season"] == "冬"]
    designs = []
    pk = ["solar_冬", "wind_冬", "solar_春秋", "wind_春秋", "solar_夏", "wind_夏"]
    for sp_, smp, dd in [("S1", "FY2016-25", d), ("S4", "FY2016-25", d), ("S5", "FY2016-25", d),
                         ("S1", "FY2023-25", d[d["fy"] >= 2023]), ("S4", "FY2023-25", d[d["fy"] >= 2023]),
                         ("S1", "除2021年1月", d[~JAN21(d.index)]), ("S4", "除2021年1月", d[~JAN21(d.index)])]:
        designs.append(("プール（全季節・季節交互作用）", sp_, smp, dd, pk))
    for sp_, smp, dd in [("W1", "FY2016-25", w), ("W4", "FY2016-25", w), ("W1", "FY2016-19", w[w["fy"] <= 2019]),
                         ("W1", "FY2020-22", w[(w["fy"] >= 2020) & (w["fy"] <= 2022)]), ("W1", "FY2023-25", w[w["fy"] >= 2023]),
                         ("W4", "FY2023-25", w[w["fy"] >= 2023])]:
        designs.append(("冬の日のみ", sp_, smp, dd, ["solar", "wind"]))
    for kind, sp_, smp, dd, keys in designs:
        X = design(dd, sp_)
        ok = X.notna().all(axis=1)
        Xo = X[ok]
        base_X = design(dd, "S1" if kind.startswith("プール") else "W1")
        for y in ("top4", "bot4", "tb4"):
            es = kind == "冬の日のみ"
            pos = np.arange(int(ok.sum())) if es else None              # 冬だけの回帰は冬の日を詰める（等間隔法）
            fit = Fit(dd.loc[ok, y], Xo, keys, pos=pos)
            res = inference(fit, rng)
            label = {"エリア": alab, "推定の形": kind, "仕様": sp_, "標本": smp, "被説明変数": YLAB[y], "y": y}
            if sp_ != "S5":
                base = Fit(dd[y], base_X, keys, pos=np.arange(len(dd)) if es else None)
                p_boot, _, size_rows, info = boot_summary(fit, base, rng, label)
                if kind == "冬の日のみ" and smp == "FY2016-25" and sp_ == "W1" and y == "tb4":
                    size_all += size_rows
            else:
                p_boot = pd.Series(np.nan, index=keys)
            for k in keys:
                src, ssn = (k.split("_") + ["冬"])[:2]
                ys_ = dd.loc[ok, y][dd.loc[ok, "season"] == {"夏": "夏", "冬": "冬", "春秋": "春秋"}[ssn]]
                rows_w.append({**label, "電源": SRCLAB[src], "季節": SLAB[ssn], "係数": k, "n": fit.n, "R2": fit.r2,
                               "残差ρ1": fit.resid_rho1(), "推論の時点": "冬の日を詰めた等間隔法" if es else "暦日（振幅変調法）",
                               **res.loc[k].to_dict(), "p_EWC_ブート": p_boot[k],
                               "その季節の被説明変数の平均（円/kWh）": float(ys_.mean())})
wl = pd.DataFrame(rows_w)
wl["星_HC3"] = wl["p_HC3"].map(stars)
wl["星_EWC"] = wl["p_EWC"].map(stars)
wl["星_EWCブート"] = wl["p_EWC_ブート"].map(stars)
wl.to_csv(os.path.join(PROC, "robust_inference_winter_legs.csv"), index=False, encoding="utf-8-sig")

print("\n=== 冬の上位・下位4時間への分解（推定値、HC3／EWC／ブートの星） ===")
for alab in ("北海道", "九州"):
    g = wl[(wl["エリア"] == alab) & (wl["季節"] == "冬")].copy()
    g["表示"] = [f"{b:+.3f} {stars(p1) or '-'}/{stars(p2) or '-'}/{(stars(p3) or '-') if p3 == p3 else '.'}"
                 for b, p1, p2, p3 in zip(g["推定値"], g["p_HC3"], g["p_EWC"], g["p_EWC_ブート"])]
    g["行"] = g["推定の形"].str[:2] + " " + g["仕様"] + " " + g["標本"]
    tt = g.pivot_table(index="行", columns=["電源", "被説明変数"], values="表示", aggfunc="first")
    tt = tt.reindex(columns=pd.MultiIndex.from_product([["太陽光", "風力"], ["上位4時間平均", "下位4時間平均", "TB4h"]]))
    print(f"--- {alab} ---")
    print(tt.to_string())

# 太陽光・冬の係数が月の違いを拾っていることの確認: 北海道の冬の月別平均（FY2016-25）
print("\n=== 北海道・冬の月別平均（FY2016-25、日次の平均） ===")
wm = D["hokkaido"][D["hokkaido"]["season"] == "冬"]
for lab, ww in [("全期間", wm), ("2021年1月を除く", wm[~JAN21(wm.index)])]:
    print(f"[{lab}・平均]")
    print(ww.groupby(ww.index.month)[["solar", "wind", "demand", "mean_p", "top4", "bot4", "tb4"]].mean().round(2)
          .rename(index={12: "12月", 1: "1月", 2: "2月"}).loc[["12月", "1月", "2月"]].to_string())
print("[全期間・中央値]")
print(wm.groupby(wm.index.month)[["solar", "tb4"]].median().round(2).rename(index={12: "12月", 1: "1月", 2: "2月"})
      .loc[["12月", "1月", "2月"]].to_string())
for area, _, alab in AREAS:
    dd = D[area]
    print(f"{alab}: 2021年1月の TB4h 平均 {dd.loc[JAN21(dd.index), 'tb4'].mean():.2f}円/kWh（最大 {dd.loc[JAN21(dd.index), 'tb4'].max():.2f}）、"
          f"他の年の1月 {dd.loc[(dd.index.month == 1) & ~JAN21(dd.index), 'tb4'].mean():.2f}円/kWh")

# 風力の冬の効果が比例的な引下げ（Δp=λ·p）と整合するか: 上位・下位の係数の比と、冬の上位・下位4時間の平均価格の比
print("\n=== 北海道・冬の風力: 上位/下位の係数比と平均価格の比（比例的な引下げなら一致） ===")
for kind, sp_, smp in [("プール（全季節・季節交互作用）", "S1", "FY2016-25"), ("プール（全季節・季節交互作用）", "S4", "FY2016-25"),
                       ("プール（全季節・季節交互作用）", "S1", "FY2023-25"), ("プール（全季節・季節交互作用）", "S4", "FY2023-25")]:
    g = wl[(wl["エリア"] == "北海道") & (wl["推定の形"] == kind) & (wl["仕様"] == sp_) & (wl["標本"] == smp) & (wl["係数"] == "wind_冬")]
    top, bot = g[g["y"] == "top4"].iloc[0], g[g["y"] == "bot4"].iloc[0]
    print(f"{sp_} {smp}: 係数比 {top['推定値'] / bot['推定値']:.2f}（{top['推定値']:+.3f}/{bot['推定値']:+.3f}）、"
          f"平均価格の比 {top['その季節の被説明変数の平均（円/kWh）'] / bot['その季節の被説明変数の平均（円/kWh）']:.2f}"
          f"（{top['その季節の被説明変数の平均（円/kWh）']:.2f}/{bot['その季節の被説明変数の平均（円/kWh）']:.2f} 円/kWh）")

# 比例的な引下げの検定: H0 は β_top = r·β_bot（r は同じ標本の冬の日の上位・下位4時間の平均価格の比）。
# 上位と下位の回帰は右辺が共通なので β_top − r·β_bot は y = top4 − r·bot4 の回帰係数に等しく、同じ推論法で検定できる
print("\n=== 北海道・冬の比例的な引下げの検定（H0: 上位の係数 = 平均価格の比 × 下位の係数） ===")
rows_prop = []
dh = D["hokkaido"]
for sp_, smp, dd in [("S1", "FY2016-25", dh), ("S4", "FY2016-25", dh), ("S1", "FY2023-25", dh[dh["fy"] >= 2023]),
                     ("S4", "FY2023-25", dh[dh["fy"] >= 2023]), ("S1", "除2021年1月", dh[~JAN21(dh.index)]),
                     ("S4", "除2021年1月", dh[~JAN21(dh.index)])]:
    wd = dd[dd["season"] == "冬"]
    ratio = wd["top4"].mean() / wd["bot4"].mean()
    X = design(dd, sp_)
    yy = dd["top4"] - ratio * dd["bot4"]
    fit = Fit(yy, X, KEYS)
    res = inference(fit, rng)
    p_boot, _, _, _ = boot_summary(fit, Fit(yy, design(dd, "S1"), KEYS), rng, {})
    bt, bb = Fit(dd["top4"], X, KEYS).b(), Fit(dd["bot4"], X, KEYS).b()
    for k in ("wind_冬", "solar_冬"):
        rows_prop.append({"エリア": "北海道", "仕様": sp_, "仕様の説明": SPECS[sp_], "標本": smp, "係数": k,
                          "電源": SRCLAB[k.split("_")[0]], "n": fit.n, "冬の上位4時間の平均価格": wd["top4"].mean(),
                          "冬の下位4時間の平均価格": wd["bot4"].mean(), "平均価格の比r": ratio,
                          "上位の係数": bt[k], "下位の係数": bb[k], "係数比": bt[k] / bb[k],
                          "上位−r×下位": res.loc[k, "推定値"], "SE_EWC": res.loc[k, "SE_EWC"], "p_EWC": res.loc[k, "p_EWC"],
                          "p_HC3": res.loc[k, "p_HC3"], "p_EWC_ブート": p_boot[k]})
        print(f"{SRCLAB[k.split('_')[0]]} {sp_} {smp}: 係数比 {bt[k] / bb[k]:.2f}、平均価格の比 {ratio:.2f}、"
              f"上位−r×下位 {res.loc[k, '推定値']:+.3f}（EWC p={res.loc[k, 'p_EWC']:.3f}、ブート p={p_boot[k]:.3f}）")
pd.DataFrame(rows_prop).to_csv(os.path.join(PROC, "robust_inference_winter_proportional.csv"), index=False, encoding="utf-8-sig")

# ---------- 実効サイズの表
mc = pd.DataFrame(size_all)
mc.to_csv(os.path.join(PROC, "robust_inference_size_mc.csv"), index=False, encoding="utf-8-sig")
print(f"\n=== 推論法の実効サイズ（名目5%の両側検定の棄却率、係数6本の平均［最小〜最大］、反復 {R_BOOT}） ===")
mc["設計"] = mc["エリア"] + " " + mc["被説明変数"] + " " + mc["仕様"] + " " + mc["標本"].str.replace("FY", "") + " " + mc["誤差過程"]
agg = mc.groupby(["設計", "推論法"], sort=False)["棄却率(名目5%)"].agg(
    lambda s: f"{s.mean():.3f}[{s.min():.2f}-{s.max():.2f}]").unstack("推論法")[METHODS]
print(agg.to_string())

# ---------- 図（(a) を上、(b) を下に並べる。Word では本文幅15.5cm（6.1インチ）で載せるので、その大きさで描き、文字は8.5〜9.5pt）
FIG_W = 6.1
FS_TICK, FS_LAB, FS_TTL, FS_LEG = 8.5, 9.0, 9.5, 8.5
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
fig, axes = plt.subplots(2, 1, figsize=(FIG_W, 6.7), layout="constrained", gridspec_kw={"height_ratios": [1, 1.75]})
fig.get_layout_engine().set(h_pad=0.04, hspace=0.05)
ax = axes[0]
g = t62[(t62["エリア"] == "北海道") & (t62["y"] == "tb4")].reset_index(drop=True)
for m, col, lab, off, mk in [("HC3", "#9a9893", "HC3（不均一分散のみ）", -0.22, "s"), ("NWAndrews", C2, "Newey–West（Andrews の自動帯域）", 0.0, "^"),
                             ("EWC", C1, f"EWC（ν={int(g['EWC_ν'].iloc[0])}、主の推論法）", 0.22, "o")]:
    cv = stats.t.ppf(0.975, int(g["EWC_ν"].iloc[0])) if m == "EWC" else 1.959964
    ax.errorbar(g["推定値"], np.arange(len(g)) + off, xerr=cv * g[f"SE_{m}"], fmt=mk, color=col, ms=4, lw=1.4,
                capsize=0, label=lab, markeredgecolor="white", markeredgewidth=0.6)
ax.axvline(0, color=MUTED, lw=0.8)
ax.set_yticks(np.arange(len(g)))
ax.set_yticklabels((g["電源"] + "・" + g["季節"]).tolist())
ax.set_ylim(len(g) - 0.5, -0.5)
ax.set_xlabel("TB4h への係数（円/kWh per GWh/日）", fontsize=FS_LAB, color=INK)
ax.set_title("(a) 主仕様の TB4h の係数：推論法別の95%区間", fontsize=FS_TTL, loc="left", color=INK, pad=4)
ax.legend(fontsize=FS_LEG, frameon=False, loc="lower left", handlelength=1.8, borderaxespad=0.2, labelspacing=0.3)

ax = axes[1]
gw = wl[(wl["エリア"] == "北海道") & (wl["季節"] == "冬")]
specs_fig = [("冬の日のみ", "W1", "FY2016-25", "冬の日のみの回帰"),
             ("プール（全季節・季節交互作用）", "S1", "FY2016-25", "主仕様"),
             ("プール（全季節・季節交互作用）", "S1", "除2021年1月", "主仕様・2021年1月を除く"),
             ("プール（全季節・季節交互作用）", "S4", "FY2016-25", "年月固定効果"),
             ("プール（全季節・季節交互作用）", "S5", "FY2016-25", "年月固定効果＋価格ラグ"),
             ("プール（全季節・季節交互作用）", "S1", "FY2023-25", "主仕様・FY2023〜25")]
ycat, ylabs, pos_y = [], [], 0.0
for src in ("太陽光", "風力"):
    for kind, sp_, smp, lab in specs_fig:
        ycat.append(pos_y)
        ylabs.append(f"{src}｜{lab}")
        for yv, col, off, ylab_, mk in [("top4", C2, -0.25, "上位4時間の平均価格", "^"), ("bot4", C3, 0.0, "下位4時間の平均価格", "s"),
                                        ("tb4", C1, 0.25, "TB4h（上位−下位）", "o")]:
            r = gw[(gw["推定の形"] == kind) & (gw["仕様"] == sp_) & (gw["標本"] == smp) & (gw["電源"] == src) & (gw["y"] == yv)].iloc[0]
            half = stats.t.ppf(0.975, int(r["EWC_ν"])) * r["SE_EWC"]
            ax.errorbar(r["推定値"], pos_y + off, xerr=half, fmt=mk, color=col, ms=3.6, lw=1.3, capsize=0,
                        markeredgecolor="white", markeredgewidth=0.5, label=ylab_ if pos_y == 0 else None)
        pos_y += 1
    pos_y += 0.6
ax.axvline(0, color=MUTED, lw=0.8)
ax.set_yticks(ycat)
ax.set_yticklabels(ylabs)
ax.set_ylim(ycat[-1] + 0.5, -0.5)
ax.set_xlabel("冬の係数（円/kWh per GWh/日）。EWC の95%区間", fontsize=FS_LAB, color=INK)
ax.set_title("(b) 冬の係数：上位・下位4時間の平均価格と TB4h", fontsize=FS_TTL, loc="left", color=INK, pad=4)
ax.legend(fontsize=FS_LEG, frameon=False, loc="lower left", handlelength=1.8, borderaxespad=0.2, labelspacing=0.3)
for a in axes:
    a.grid(axis="x", color=GRID, lw=0.6)
    a.set_axisbelow(True)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        a.spines[s].set_color(MUTED)
    a.tick_params(colors=MUTED, labelsize=FS_TICK, length=2.5, pad=2)
    a.tick_params(axis="y", labelcolor=INK)
    a.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}".replace("-", "−")))
# 図題・注・出所は論文本文（図の下）に置くので、画像には入れない
fig.savefig(os.path.join(FIGDIR, "robust_inference_ci.png"), dpi=300, bbox_inches="tight", pad_inches=0.03)
print("\nsaved robust_inference_table62.csv, robust_inference_specs.csv, robust_inference_winter_legs.csv,"
      " robust_inference_winter_proportional.csv, robust_inference_size_mc.csv, figures/hokkaido/robust_inference_ci.png")
