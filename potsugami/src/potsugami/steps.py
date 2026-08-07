"""石段フィルタ: OSM highway=steps と神社の近接マッチ + 段数推定。

引き継ぎ書 5 章の仮説の実装:
- OSM の highway=steps が石段そのもの → 神社から match_radius_m 以内の steps を参道候補とする
- 段数は (a) step_count タグがあればそれを採用、
  (b) なければ標高差から レンジ推定 (Δh / riser_max 〜 Δh / riser_min)
- 標高差は マッチした全 steps way の端点標高の max - min (参道が複数 way に
  分割されていても合算できる)

網羅性の検証 (「田舎で OSM の石段データは実用に耐えるか」) のため、
マッチ率などの統計も返す。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .config import DEM_LOW_PRECISION_KINDS, StepsParams, pref_iso
from .dem import ElevationProvider
from .geo import (
    GridIndex,
    densify_polyline,
    point_polyline_dist_m,
    polyline_length_m,
)

# グリッド登録時の密化間隔 (m)。頂点間隔の長い way の取りこぼし防止
_DENSIFY_STEP_M = 100.0
from .overpass import OverpassClient
from .shrines import Shrine


@dataclass
class StepsWay:
    key: str                                # "way/123"
    verts: list[tuple[float, float]]        # [(lat, lon), ...]
    tags: dict = field(default_factory=dict)

    @property
    def length_m(self) -> float:
        return polyline_length_m(self.verts)

    @property
    def step_count_tag(self) -> int | None:
        raw = self.tags.get("step_count")
        if raw is None:
            return None
        try:
            return int(str(raw).strip().split(";")[0])
        except ValueError:
            return None


@dataclass
class ShrineSteps:
    ways: list[StepsWay] = field(default_factory=list)
    total_length_m: float = 0.0
    match_dist_m: float | None = None       # 最も近い石段までの距離 (信頼度の目安)
    elev_diff_m: float | None = None        # 端点標高の max - min (DEM が引けた場合)
    elev_low_precision: bool = False        # 10m メッシュ DEM (±5m 級) を使った
    step_count_tagged: int | None = None    # step_count タグの合算 (1 本でもあれば)
    est_steps_min: int | None = None        # Δh ベースの推定レンジ
    est_steps_max: int | None = None

    @property
    def matched(self) -> bool:
        return bool(self.ways)


def build_steps_query(pref: str, timeout_s: int = 300) -> str:
    iso = pref_iso(pref)
    return (
        f"[out:json][timeout:{timeout_s}];\n"
        f'area["ISO3166-2"="{iso}"]["admin_level"="4"]->.pref;\n'
        'way["highway"="steps"](area.pref);\n'
        "out tags geom;\n"
    )


def parse_steps(data: dict) -> list[StepsWay]:
    out: list[StepsWay] = []
    for el in data.get("elements", []):
        if el.get("type") != "way":
            continue
        geom = el.get("geometry") or []
        verts = [(g["lat"], g["lon"]) for g in geom if "lat" in g and "lon" in g]
        if len(verts) < 2:
            continue
        out.append(
            StepsWay(key=f"way/{el.get('id')}", verts=verts, tags=el.get("tags", {}) or {})
        )
    return out


def fetch_steps(client: OverpassClient, pref: str) -> list[StepsWay]:
    return parse_steps(client.query(build_steps_query(pref)))


def match_steps(
    shrines: Sequence[Shrine],
    steps: Sequence[StepsWay],
    elevation: ElevationProvider | None,
    p: StepsParams,
) -> dict[str, ShrineSteps]:
    """各神社に近接 steps をマッチし、段数を推定する。

    steps way は複数の神社にマッチしうる (隣接する神社仏閣で共有される石段など)。
    """
    # steps の頂点 (密化済み) をグリッドに載せ、神社側から近傍検索する
    index = GridIndex(cell_deg=max(p.match_radius_m / 111_320.0 * 2, 0.001))
    for w in steps:
        for lat, lon in densify_polyline(w.verts, _DENSIFY_STEP_M):
            index.insert(lat, lon, w)

    lookup_r = p.match_radius_m + _DENSIFY_STEP_M / 2
    result: dict[str, ShrineSteps] = {}
    for s in shrines:
        cand: dict[str, StepsWay] = {}
        for _lat, _lon, obj in index.near(s.lat, s.lon, lookup_r):
            w: StepsWay = obj  # type: ignore[assignment]
            if w.key not in cand:
                cand[w.key] = w
        matched: list[StepsWay] = []
        match_dists: list[float] = []
        for w in cand.values():
            d = point_polyline_dist_m(s.lat, s.lon, w.verts)
            if d <= p.match_radius_m:
                matched.append(w)
                match_dists.append(d)
        ss = ShrineSteps(ways=sorted(matched, key=lambda w: w.key))
        if matched:
            ss.match_dist_m = round(min(match_dists), 1)
            ss.total_length_m = round(sum(w.length_m for w in matched), 1)
            tagged = [w.step_count_tag for w in matched if w.step_count_tag]
            if tagged:
                ss.step_count_tagged = sum(tagged)
            if elevation is not None:
                elevs: list[float] = []
                kinds: set[str] = set()
                elevation_ex = getattr(elevation, "elevation_ex", None)
                for w in matched:
                    for lat, lon in (w.verts[0], w.verts[-1]):
                        if elevation_ex is not None:
                            h, kind = elevation_ex(lat, lon)
                        else:
                            h, kind = elevation.elevation(lat, lon), None
                        if h is not None:
                            elevs.append(h)
                            if kind is not None:
                                kinds.add(kind)
                if len(elevs) >= 2:
                    diff = max(elevs) - min(elevs)
                    ss.elev_diff_m = round(diff, 1)
                    ss.elev_low_precision = bool(kinds & DEM_LOW_PRECISION_KINDS)
                    if diff > 0:
                        ss.est_steps_min = int(diff / p.riser_max_m)
                        ss.est_steps_max = int(diff / p.riser_min_m)
        result[s.key] = ss
    return result


@dataclass
class StepsCoverage:
    n_shrines: int
    n_matched: int          # steps が 1 本以上マッチした神社数
    n_with_count_tag: int   # step_count タグ付きが 1 本以上ある神社数
    n_steps_ways: int       # 県内の steps way 総数

    @property
    def match_rate(self) -> float:
        return self.n_matched / self.n_shrines if self.n_shrines else 0.0


def coverage_stats(
    shrines: Sequence[Shrine],
    steps: Sequence[StepsWay],
    matches: dict[str, ShrineSteps],
) -> StepsCoverage:
    return StepsCoverage(
        n_shrines=len(shrines),
        n_matched=sum(1 for s in shrines if matches.get(s.key, ShrineSteps()).matched),
        n_with_count_tag=sum(
            1 for s in shrines
            if matches.get(s.key, ShrineSteps()).step_count_tagged is not None
        ),
        n_steps_ways=len(steps),
    )
