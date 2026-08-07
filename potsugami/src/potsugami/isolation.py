"""孤立度スコア v0.1 (距離減衰カーネル和)。

入力は「神社から周囲の建物までの距離 + 面積 + 種別」のリストだけ。
データソース非依存。

  P     = Σ_i a_i · exp(-d_i / tau)
  S_iso = 100 · exp(-P / p_scale)

- a_i = min(面積 / area_norm, area_cap)。面積不明は 1.0。無壁舎は × roofless_weight
- 自己除外: self_exclusion_m 以内は境内建物とみなして P に入れない
  (ただし件数を n_adjacent として返し、屋敷神チェック用に表示する)
- 単調性: 建物が増える・近づく・大きくなるほどスコアは下がる (テストで保証)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .config import ScoreParams


@dataclass(frozen=True)
class BuildingObs:
    """建物 1 棟の観測値。"""
    dist_m: float
    area_m2: float | None = None   # 不明 (OSM 代表点など) は None
    roofless: bool = False         # 無壁舎 (温室・車庫・上屋)


@dataclass
class IsolationResult:
    score: float                 # S_iso 0..100
    p_sum: float                 # カーネル和 P (デバッグ・調整用)
    d_nearest_m: float | None    # 自己除外後の最寄り建物距離。半径内ゼロなら None
    n_adjacent: int              # [0, self_exclusion) の建物数 (境内 or 屋敷神の母屋)
    n_inner: int                 # [self_exclusion, inner_r) の建物数 (表示用)
    n_outer: int                 # [inner_r, outer_r) の建物数 (表示用)


def building_weight(obs: BuildingObs, p: ScoreParams) -> float:
    a = 1.0 if obs.area_m2 is None else min(obs.area_m2 / p.area_norm_m2, p.area_cap)
    if obs.roofless:
        a *= p.roofless_weight
    return a


def isolation_score(buildings: list[BuildingObs], p: ScoreParams) -> IsolationResult:
    eff = [b for b in buildings if b.dist_m >= p.self_exclusion_m]
    n_adjacent = len(buildings) - len(eff)
    d_nearest = min((b.dist_m for b in eff), default=None)
    n_inner = sum(1 for b in eff if b.dist_m < p.inner_r_m)
    n_outer = sum(1 for b in eff if p.inner_r_m <= b.dist_m < p.outer_r_m)

    p_sum = sum(
        building_weight(b, p) * math.exp(-b.dist_m / p.tau_m) for b in eff
    )
    score = 100.0 * math.exp(-p_sum / p.p_scale)
    return IsolationResult(
        score=round(score, 2),
        p_sum=round(p_sum, 4),
        d_nearest_m=round(d_nearest, 1) if d_nearest is not None else None,
        n_adjacent=n_adjacent,
        n_inner=n_inner,
        n_outer=n_outer,
    )
