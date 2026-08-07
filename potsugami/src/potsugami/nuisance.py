"""迷惑土地利用と幹線道路による減点。

「建物がない」≠「静かで人がいない」の穴を塞ぐ。メガソーラーは建物ポリゴンを
持たないため、鎮守の森ごと周囲をパネルに囲まれた神社が孤立度満点で最上位に
出てしまう (千葉の房総で現実に起きている状況)。露天の工場・採石場・ゴルフ場、
交通量の多い幹線道路も同様。

OSM から対象地物を県単位で取得し、各神社について
  - 最寄り迷惑施設までの距離 → near_mult / far_mult
  - 最寄り幹線道路までの距離 → road_mult
を返す。スコアへは乗算で効かせる (pipeline.py)。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .config import NuisanceParams, pref_iso
from .geo import GridIndex, densify_polyline, haversine_m, point_polyline_dist_m
from .overpass import OverpassClient
from .shrines import Shrine

# グリッド登録時のポリライン密化間隔 (m)。近傍検索半径はこの半分を上乗せする。
_DENSIFY_STEP_M = 200.0

# 対象とする迷惑土地利用 (Overpass セレクタ, フラグ名)
_NUISANCE_SELECTORS = [
    ('nwr["power"="plant"]["plant:source"="solar"]', "solar"),
    ('nwr["landuse"="industrial"]', "industrial"),
    ('nwr["landuse"="quarry"]', "quarry"),
    ('nwr["landuse"="landfill"]', "landfill"),
    ('nwr["leisure"="golf_course"]', "golf"),
]

# 幹線道路 (国道・主要地方道クラス)
_MAJOR_HIGHWAYS = "motorway|trunk|primary|secondary"


@dataclass
class NuisanceFeature:
    kind: str
    verts: list[tuple[float, float]]   # 外周頂点列 (node は 1 点)


@dataclass
class NuisanceResult:
    mult: float = 1.0                  # 迷惑施設 × 幹線道路の合成係数
    flags: list[str] = field(default_factory=list)   # 例: ["solar@120m", "road@80m"]
    nearest_m: float | None = None     # 最寄り迷惑施設距離 (半径内にあれば)


def build_nuisance_query(pref: str, timeout_s: int = 300) -> str:
    iso = pref_iso(pref)
    body = "\n".join(f"  {sel}(area.pref);" for sel, _k in _NUISANCE_SELECTORS)
    return (
        f"[out:json][timeout:{timeout_s}];\n"
        f'area["ISO3166-2"="{iso}"]["admin_level"="4"]->.pref;\n'
        f"(\n{body}\n);\nout tags geom center;\n"
    )


def build_major_road_query(pref: str, timeout_s: int = 300) -> str:
    iso = pref_iso(pref)
    return (
        f"[out:json][timeout:{timeout_s}];\n"
        f'area["ISO3166-2"="{iso}"]["admin_level"="4"]->.pref;\n'
        f'way["highway"~"^({_MAJOR_HIGHWAYS})$"](area.pref);\n'
        "out geom;\n"
    )


def _classify(tags: dict) -> str | None:
    if tags.get("power") == "plant" and tags.get("plant:source") == "solar":
        return "solar"
    lu = tags.get("landuse")
    if lu in ("industrial", "quarry", "landfill"):
        return lu
    if tags.get("leisure") == "golf_course":
        return "golf"
    return None


def parse_nuisance(data: dict) -> list[NuisanceFeature]:
    out: list[NuisanceFeature] = []
    for el in data.get("elements", []):
        tags = el.get("tags", {}) or {}
        kind = _classify(tags)
        if kind is None:
            continue
        geom = el.get("geometry") or []
        verts = [(g["lat"], g["lon"]) for g in geom if "lat" in g and "lon" in g]
        if not verts:
            if el.get("type") == "node":
                lat, lon = el.get("lat"), el.get("lon")
            else:
                c = el.get("center") or {}
                lat, lon = c.get("lat"), c.get("lon")
            if lat is None or lon is None:
                continue
            verts = [(float(lat), float(lon))]
        out.append(NuisanceFeature(kind=kind, verts=verts))
    return out


def parse_roads(data: dict) -> list[list[tuple[float, float]]]:
    ways = []
    for el in data.get("elements", []):
        if el.get("type") != "way":
            continue
        geom = el.get("geometry") or []
        verts = [(g["lat"], g["lon"]) for g in geom if "lat" in g and "lon" in g]
        if len(verts) >= 2:
            ways.append(verts)
    return ways


class NuisanceIndex:
    """迷惑施設・幹線道路の頂点をグリッドに載せ、神社ごとの係数を計算する。"""

    def __init__(
        self,
        features: Sequence[NuisanceFeature],
        major_roads: Sequence[list[tuple[float, float]]],
        params: NuisanceParams | None = None,
    ):
        self.params = params or NuisanceParams()
        cell = max(self.params.far_m / 111_320.0 * 2, 0.001)
        self._feat_index = GridIndex(cell_deg=cell)
        for f in features:
            for lat, lon in densify_polyline(f.verts, _DENSIFY_STEP_M):
                self._feat_index.insert(lat, lon, f)
        cell_r = max(self.params.road_dist_m / 111_320.0 * 4, 0.001)
        self._road_index = GridIndex(cell_deg=cell_r)
        for i, verts in enumerate(major_roads):
            for lat, lon in densify_polyline(verts, _DENSIFY_STEP_M):
                self._road_index.insert(lat, lon, i)
        self._roads = list(major_roads)

    def evaluate(self, shrine: Shrine) -> NuisanceResult:
        p = self.params
        res = NuisanceResult()

        # 迷惑施設: 密化点の近傍 → 頂点列への正確な距離
        lookup_r = p.far_m + _DENSIFY_STEP_M / 2
        cand: dict[int, NuisanceFeature] = {}
        for _lat, _lon, obj in self._feat_index.near(shrine.lat, shrine.lon, lookup_r):
            cand[id(obj)] = obj  # type: ignore[arg-type]
        best: tuple[float, str] | None = None
        for f in cand.values():
            d = (
                haversine_m(shrine.lat, shrine.lon, f.verts[0][0], f.verts[0][1])
                if len(f.verts) == 1
                else point_polyline_dist_m(shrine.lat, shrine.lon, f.verts)
            )
            if d <= p.far_m and (best is None or d < best[0]):
                best = (d, f.kind)
        if best is not None:
            res.nearest_m = round(best[0], 1)
            if best[0] <= p.near_m:
                res.mult *= p.near_mult
            else:
                res.mult *= p.far_mult
            res.flags.append(f"{best[1]}@{best[0]:.0f}m")

        # 幹線道路
        road_ids = {
            obj for _lat, _lon, obj in
            self._road_index.near(
                shrine.lat, shrine.lon, p.road_dist_m + _DENSIFY_STEP_M / 2
            )
        }
        for i in road_ids:
            d = point_polyline_dist_m(shrine.lat, shrine.lon, self._roads[i])  # type: ignore[index]
            if d <= p.road_dist_m:
                res.mult *= p.road_mult
                res.flags.append(f"road@{d:.0f}m")
                break

        res.mult = round(res.mult, 4)
        return res


def fetch_nuisance_index(
    client: OverpassClient, prefs: Sequence[str], params: NuisanceParams | None = None
) -> NuisanceIndex:
    feats: list[NuisanceFeature] = []
    roads: list[list[tuple[float, float]]] = []
    for pref in prefs:
        feats.extend(parse_nuisance(client.query(build_nuisance_query(pref))))
        roads.extend(parse_roads(client.query(build_major_road_query(pref))))
    return NuisanceIndex(feats, roads, params)
