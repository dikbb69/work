"""パイプライン統括: 神社取得 → 孤立度 → 減点係数 → 石段マッチ → 候補リスト。

最終スコア = S_iso (孤立度 0..100)
           × 迷惑施設・幹線道路係数 (nuisance, 既定 ON)
           × 有名度係数 (fame, 既定 ON)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Sequence

from . import config
from .buildings import BuildingProvider
from .dem import ElevationProvider
from .fame import fame_signals
from .geo import haversine_m
from .isolation import isolation_score
from .nuisance import NuisanceIndex, NuisanceResult
from .report import Candidate
from .shrines import Shrine
from .steps import ShrineSteps, StepsCoverage, StepsWay, coverage_stats, match_steps


@dataclass
class PipelineResult:
    candidates: list[Candidate]      # final_score 降順、rank 付与済み
    coverage: StepsCoverage | None


def build_candidates(
    shrines: Sequence[Shrine],
    building_provider: BuildingProvider,
    score_params: config.ScoreParams,
    steps_ways: Sequence[StepsWay] | None = None,
    elevation: ElevationProvider | None = None,
    steps_params: config.StepsParams | None = None,
    nuisance_index: NuisanceIndex | None = None,
    apply_fame_penalty: bool = True,
    home: tuple[float, float] = (config.HOME_LAT, config.HOME_LON),
    road_distance_fn: Callable[[Sequence[Shrine]], dict[str, float | None]] | None = None,
    roads_top: int = 400,
    log: Callable[[str], None] | None = None,
) -> PipelineResult:
    log = log or (lambda m: print(m, file=sys.stderr))

    log(f"[score] 建物データ取得中 ({building_provider.name}, "
        f"{len(shrines)} 社, 半径 {score_params.search_radius_m:.0f}m)…")
    obs = building_provider.bulk_for_shrines(shrines, score_params.search_radius_m)

    steps_by_shrine: dict[str, ShrineSteps] = {}
    coverage: StepsCoverage | None = None
    if steps_ways is not None:
        sp = steps_params or config.StepsParams()
        log(f"[steps] 石段マッチング中 ({len(steps_ways)} 本)…")
        steps_by_shrine = match_steps(shrines, steps_ways, elevation, sp)
        coverage = coverage_stats(shrines, steps_ways, steps_by_shrine)

    cands: list[Candidate] = []
    for s in shrines:
        iso = isolation_score(obs.get(s.key, []), score_params)
        fame = fame_signals(s.tags)
        nui = nuisance_index.evaluate(s) if nuisance_index else NuisanceResult()
        final = iso.score * nui.mult
        if apply_fame_penalty:
            final *= fame.multiplier
        cands.append(
            Candidate(
                shrine=s,
                iso=iso,
                fame=fame,
                nuisance=nui,
                steps=steps_by_shrine.get(s.key),
                dist_home_km=haversine_m(home[0], home[1], s.lat, s.lon) / 1000.0,
                final_score=round(final, 2),
            )
        )

    # スコア降順。同点は最寄り建物が遠い順 → 名前順で安定させる
    cands.sort(
        key=lambda c: (
            -c.final_score,
            -(c.iso.d_nearest_m if c.iso.d_nearest_m is not None else 1e9),
            c.shrine.display_name,
        )
    )
    for i, c in enumerate(cands, start=1):
        c.rank = i

    # 上位候補のみ最寄り車道距離を付ける (「車で行けない奥宮」検出用)
    if road_distance_fn is not None and cands:
        top = cands[: roads_top]
        log(f"[roads] 上位 {len(top)} 社の最寄り車道距離を取得中…")
        road_dists = road_distance_fn([c.shrine for c in top])
        for c in top:
            c.road_checked = True
            c.road_dist_m = road_dists.get(c.shrine.key)

    return PipelineResult(candidates=cands, coverage=coverage)
