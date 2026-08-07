"""オフライン合成データデモ。

ネットワーク不要でパイプライン全体 (スコア → 石段 → レポート) を動かし、
出力の見た目とスコアの挙動を確認するためのもの。座標は千葉県南部の実在エリア
だが、神社・建物・石段はすべて架空。
"""
from __future__ import annotations

import random
from pathlib import Path

from . import config
from .buildings import StaticProvider
from .nuisance import NuisanceFeature, NuisanceIndex
from .pipeline import build_candidates
from .report import write_report
from .shrines import Shrine
from .steps import StepsWay

_CENTER_LAT = 35.20
_CENTER_LON = 140.10
_M_PER_DEG_LAT = 111_320.0


def _offset(lat: float, lon: float, dx_m: float, dy_m: float) -> tuple[float, float]:
    import math
    return (
        lat + dy_m / _M_PER_DEG_LAT,
        lon + dx_m / (_M_PER_DEG_LAT * math.cos(math.radians(lat))),
    )


class DemoElevation:
    """東ほど高い斜面という単純な合成地形 (石段 150m 強で標高差 ~35m 程度)。"""

    def elevation(self, lat: float, lon: float) -> float | None:
        return max((lon - _CENTER_LON) * 20_000.0, 0.0)


def build_demo_world(seed: int = 20260807):
    rng = random.Random(seed)
    shrines: list[Shrine] = []
    buildings: list[tuple[float, float]] = []
    steps: list[StepsWay] = []

    def add_shrine(i: int, lat: float, lon: float, name: str, tags: dict | None = None):
        t = {"amenity": "place_of_worship", "religion": "shinto", "name": name}
        t.update(tags or {})
        shrines.append(Shrine(key=f"node/{i}", lat=lat, lon=lon, name=name, tags=t))

    # 1) 集落密集タイプ: 建物に囲まれた鎮守 (低スコアになるはず)
    for i in range(8):
        base = _offset(_CENTER_LAT, _CENTER_LON, rng.uniform(-4000, 4000), rng.uniform(-4000, 4000))
        add_shrine(1000 + i, base[0], base[1], f"合成第{i + 1}村社")
        for _ in range(rng.randint(25, 60)):
            buildings.append(
                _offset(base[0], base[1], rng.uniform(-350, 350), rng.uniform(-350, 350))
            )

    # 2) 集落はずれタイプ: 100〜300m 先に集落 (中スコア)
    for i in range(10):
        base = _offset(_CENTER_LAT, _CENTER_LON, rng.uniform(-6000, 6000), rng.uniform(-6000, 6000))
        add_shrine(2000 + i, base[0], base[1], f"合成第{i + 1}辺社")
        gap = rng.uniform(120, 320)
        for _ in range(rng.randint(6, 18)):
            buildings.append(
                _offset(base[0], base[1], gap + rng.uniform(0, 200), rng.uniform(-150, 150))
            )

    # 3) ポツ神タイプ: 半径 500m に建物ゼロ〜数戸 (高スコア)。一部に長い石段。
    for i in range(9):
        base = _offset(_CENTER_LAT, _CENTER_LON, rng.uniform(4000, 9000), rng.uniform(-8000, 8000))
        add_shrine(3000 + i, base[0], base[1], f"合成第{i + 1}山社")
        if rng.random() < 0.5:
            buildings.append(
                _offset(base[0], base[1], rng.uniform(380, 490), rng.uniform(-100, 100))
            )
        if i % 3 == 0:
            # 参道石段: 神社から西へ下る 2 分割の way
            v0 = _offset(base[0], base[1], -180, 0)
            v1 = _offset(base[0], base[1], -90, 0)
            v2 = _offset(base[0], base[1], -15, 0)
            steps.append(StepsWay(key=f"way/{9000 + i * 2}", verts=[v0, v1]))
            tags = {"step_count": "148"} if i == 0 else {}
            steps.append(StepsWay(key=f"way/{9001 + i * 2}", verts=[v1, v2], tags=tags))

    # 4) 有名神社タイプ: 孤立しているが wikipedia タグあり (有名度係数の確認用)
    base = _offset(_CENTER_LAT, _CENTER_LON, -8000, 6000)
    add_shrine(
        4000, base[0], base[1], "合成大社",
        {"wikipedia": "ja:合成大社", "wikidata": "Q0", "tourism": "attraction"},
    )
    buildings.append(_offset(base[0], base[1], 450, 0))

    # 5) ソーラー隣接タイプ: 建物ゼロだがメガソーラーの隣 (騒がしさ減点の確認用)
    base = _offset(_CENTER_LAT, _CENTER_LON, -6000, -7000)
    add_shrine(5000, base[0], base[1], "合成日照神社")
    nw = _offset(base[0], base[1], 100, -50)
    se = _offset(base[0], base[1], 400, -350)
    nuisances = [
        NuisanceFeature(
            kind="solar",
            verts=[nw, (nw[0], se[1]), se, (se[0], nw[1]), nw],
        )
    ]
    # 幹線道路: 村社エリアを東西に貫く 1 本
    road_a = _offset(_CENTER_LAT, _CENTER_LON, -10000, 60)
    road_b = _offset(_CENTER_LAT, _CENTER_LON, 10000, 60)
    major_roads = [[road_a, road_b]]

    return shrines, buildings, steps, nuisances, major_roads


def run_demo(out_dir: Path, seed: int = 20260807) -> None:
    shrines, buildings, steps, nuisances, major_roads = build_demo_world(seed)
    result = build_candidates(
        shrines,
        StaticProvider(buildings),
        config.ScoreParams(),
        steps_ways=steps,
        elevation=DemoElevation(),
        steps_params=config.StepsParams(),
        nuisance_index=NuisanceIndex(nuisances, major_roads),
    )
    write_report(
        result.candidates,
        out_dir,
        "ポツ神ファインダー デモ (合成データ)",
        coverage=result.coverage,
        home=(config.HOME_LAT, config.HOME_LON),
    )
