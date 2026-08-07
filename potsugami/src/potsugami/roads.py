"""最寄り車道までの距離。

孤立度だけで並べるとランキング上位が「徒歩数時間の奥宮」に退化しうるため、
上位候補についてのみ最寄りの車が通れる道からの距離を計算し、検証の軸として
レポートに出す (スコアには入れない。v0 では列表示のみ)。

Overpass 負荷を抑えるため全神社ではなく上位 N 社に限定する。
"""
from __future__ import annotations

from typing import Sequence

from .geo import point_polyline_dist_m
from .overpass import OverpassClient
from .shrines import Shrine

# 車で通行できるとみなす highway 値
DRIVABLE_HIGHWAYS = (
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential", "service", "track",
    "motorway_link", "trunk_link", "primary_link", "secondary_link",
    "tertiary_link", "living_street", "road",
)

_HIGHWAY_REGEX = "^(" + "|".join(DRIVABLE_HIGHWAYS) + ")$"


def _batch_query(batch: Sequence[Shrine], radius_m: float) -> str:
    lines = []
    for s in batch:
        around = f"around:{int(radius_m)},{s.lat:.7f},{s.lon:.7f}"
        lines.append(f'  way({around})["highway"~"{_HIGHWAY_REGEX}"];')
    body = "\n".join(lines)
    return f"[out:json][timeout:300];\n(\n{body}\n);\nout geom qt;\n"


def _parse_road_ways(data: dict) -> list[list[tuple[float, float]]]:
    seen: set[int] = set()
    ways: list[list[tuple[float, float]]] = []
    for el in data.get("elements", []):
        if el.get("type") != "way" or el.get("id") in seen:
            continue
        seen.add(el.get("id"))
        geom = el.get("geometry") or []
        verts = [(g["lat"], g["lon"]) for g in geom if "lat" in g and "lon" in g]
        if len(verts) >= 2:
            ways.append(verts)
    return ways


def nearest_road_distances(
    client: OverpassClient,
    shrines: Sequence[Shrine],
    radius_m: float = 500.0,
    batch_size: int = 20,
) -> dict[str, float | None]:
    """各神社の最寄り車道距離 (m)。radius_m 内に車道がなければ None (>radius)。"""
    out: dict[str, float | None] = {}
    for i in range(0, len(shrines), batch_size):
        batch = shrines[i:i + batch_size]
        data = client.query(_batch_query(batch, radius_m))
        ways = _parse_road_ways(data)
        for s in batch:
            best: float | None = None
            for verts in ways:
                d = point_polyline_dist_m(s.lat, s.lon, verts)
                if d <= radius_m and (best is None or d < best):
                    best = d
            out[s.key] = round(best, 1) if best is not None else None
    return out
