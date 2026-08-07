"""建物データプロバイダ。

孤立度スコアの分母となる「神社の周囲の建物」を取得する。プロバイダは
    bulk_for_shrines(shrines, radius_m) -> {shrine.key: [BuildingObs, ...]}
だけを契約とし、スコア計算はデータソースを知らない。BuildingObs は
距離・面積 (分かる場合)・無壁舎フラグを持つ (isolation.py 参照)。

- GsiBvmapProvider (既定): 地理院ベクトルタイルの建物ポリゴン。基盤地図情報由来で
  全国均一の被覆。田舎の建物が歯抜けの OSM と違い「未記入の集落が偽ポツ神になる」
  問題がない。既定は現行の最適化ベクトルタイル (optimal_bvmap-v1, レイヤ BldA)。
  無壁舎 (ftCode 3103/3104: 温室・車庫など) は除外せず低重み (roofless) で算入する
  — 除外するとビニールハウス地帯が「無人」判定になるため。
- OsmBuildingProvider: Overpass で building=* を取得。田舎での被覆率に難があるため
  代替という位置づけ。面積は取れない (代表点のみ)。

境内建物の除外は 2 段構え:
  1. 幾何学的除外 (このモジュール): 重複排除で神社に統合された OSM 要素
     (building=shrine の社殿ポリゴン等) の位置 (Shrine.precinct_points) から
     30m 以内の建物は返さない。
  2. 距離しきい値 (isolation.py): 神社中心から self_exclusion_m 以内は P に入れない
     (OSM に社殿が描かれていない神社のためのフォールバック)。

注意 (GSI): ベクトルタイルはタイル境界で建物ポリゴンがクリップされ、境界付近の
建物は隣接タイルにも重複収録される。各建物をその重心が属するタイルにのみ帰属させる
ことでバッファ由来の重複は除くが、真にまたがる建物は 2 分割のまま両側で数えられる
(合計面積はほぼ保存されるので、面積重み方式ではほぼ無害)。
"""
from __future__ import annotations

from typing import Iterable, Protocol, Sequence

from . import config, mvt
from .geo import (
    centroid,
    haversine_m,
    point_polyline_dist_m,
    polygon_area_m2,
    tile_bounds,
    tile_to_lonlat,
    tiles_covering_disc,
)
from .isolation import BuildingObs
from .overpass import OverpassClient
from .shrines import Shrine
from .tiles import TileFetcher

# 境内建物とみなして除外する OSM building 値
_OSM_EXCLUDE_BUILDING = {"shrine", "temple"}
# 無壁舎相当とみなす OSM building 値
_OSM_ROOFLESS_BUILDING = {
    "greenhouse", "garage", "garages", "carport", "shed", "hut", "roof",
}
# Shrine.precinct_points からこの距離以内の建物は境内建物として除外
PRECINCT_EXCLUSION_M = 30.0


class BuildingProvider(Protocol):
    name: str

    def bulk_for_shrines(
        self, shrines: Sequence[Shrine], radius_m: float
    ) -> dict[str, list[BuildingObs]]: ...


def _near_precinct(shrine: Shrine, b_lat: float, b_lon: float) -> bool:
    return any(
        haversine_m(p_lat, p_lon, b_lat, b_lon) <= PRECINCT_EXCLUSION_M
        for p_lat, p_lon in shrine.precinct_points
    )


class GsiBvmapProvider:
    name = "gsi_bvmap"

    def __init__(
        self,
        fetcher: TileFetcher,
        source: str = config.GSI_BVMAP_DEFAULT_SOURCE,
        roofless_ftcodes: set[str] = config.GSI_ROOFLESS_FTCODES,
    ):
        if source not in config.GSI_BVMAP_SOURCES:
            raise ValueError(
                f"unknown GSI source: {source} ({'/'.join(config.GSI_BVMAP_SOURCES)})"
            )
        self.source = source
        url, zoom, layers = config.GSI_BVMAP_SOURCES[source]
        self.url_template = url
        self.zoom = zoom
        self.layer_names = tuple(n.lower() for n in layers)
        self.roofless_ftcodes = roofless_ftcodes
        self.fetcher = fetcher
        # デコード済みタイルの建物キャッシュ: (重心, 頂点列, 面積, 無壁舎)
        self._tile_buildings: dict[tuple[int, int], list[tuple]] = {}

    def _match_layer(self, name: str) -> bool:
        low = name.lower()
        return any(want in low for want in self.layer_names)

    def _is_roofless(self, tags: dict) -> bool:
        ft = tags.get("ftCode", tags.get("ftcode"))
        return ft is not None and str(ft) in self.roofless_ftcodes

    def _buildings_in_tile(self, x: int, y: int) -> list[tuple]:
        key = (x, y)
        if key in self._tile_buildings:
            return self._tile_buildings[key]
        result: list[tuple] = []
        data = self.fetcher.fetch(self.url_template, self.zoom, x, y, self.source)
        if data:
            try:
                layers = mvt.decode(data)
            except mvt.MvtError:
                layers = {}
            west, south, east, north = tile_bounds(x, y, self.zoom)
            for lname, layer in layers.items():
                if not self._match_layer(lname):
                    continue
                for feat in layer.features:
                    if feat.geom_type != mvt.GEOM_POLYGON or not feat.parts:
                        continue
                    # 外環 (最初のパート) だけ使う。距離・面積用途では十分。
                    ring = feat.parts[0]
                    verts = [
                        self._local_to_latlon(x, y, layer.extent, px, py)
                        for px, py in ring
                    ]
                    # 重心がこのタイルの外にある建物は隣接タイル側に帰属させる
                    # (クリップバッファによる重複カウント防止)
                    c_lat, c_lon = centroid(verts[:-1] if len(verts) > 1 else verts)
                    if not (west <= c_lon < east and south < c_lat <= north):
                        continue
                    result.append(
                        (c_lat, c_lon, verts, polygon_area_m2(verts),
                         self._is_roofless(feat.tags))
                    )
        self._tile_buildings[key] = result
        return result

    def _local_to_latlon(
        self, x: int, y: int, extent: int, px: int, py: int
    ) -> tuple[float, float]:
        lon, lat = tile_to_lonlat(x + px / extent, y + py / extent, self.zoom)
        return lat, lon

    def bulk_for_shrines(
        self, shrines: Sequence[Shrine], radius_m: float
    ) -> dict[str, list[BuildingObs]]:
        out: dict[str, list[BuildingObs]] = {}
        for s in shrines:
            obs: list[BuildingObs] = []
            for tx, ty in tiles_covering_disc(s.lat, s.lon, radius_m, self.zoom):
                for c_lat, c_lon, verts, area, roofless in self._buildings_in_tile(tx, ty):
                    d = point_polyline_dist_m(s.lat, s.lon, verts)
                    if d <= radius_m and not _near_precinct(s, c_lat, c_lon):
                        obs.append(BuildingObs(dist_m=d, area_m2=area, roofless=roofless))
            obs.sort(key=lambda b: b.dist_m)
            out[s.key] = obs
        return out


class OsmBuildingProvider:
    name = "osm"

    def __init__(self, client: OverpassClient, batch_size: int = 40):
        self.client = client
        self.batch_size = batch_size

    def _batch_query(self, batch: Sequence[Shrine], radius_m: float) -> str:
        lines = []
        for s in batch:
            around = f"around:{int(radius_m)},{s.lat:.7f},{s.lon:.7f}"
            lines.append(f'  nwr({around})["building"];')
        body = "\n".join(lines)
        return f"[out:json][timeout:300];\n(\n{body}\n);\nout tags center qt;\n"

    def bulk_for_shrines(
        self, shrines: Sequence[Shrine], radius_m: float
    ) -> dict[str, list[BuildingObs]]:
        out: dict[str, list[BuildingObs]] = {s.key: [] for s in shrines}
        for i in range(0, len(shrines), self.batch_size):
            batch = shrines[i:i + self.batch_size]
            data = self.client.query(self._batch_query(batch, radius_m))
            buildings = _parse_osm_buildings(data)
            for s in batch:
                obs = [
                    BuildingObs(
                        dist_m=haversine_m(s.lat, s.lon, b_lat, b_lon),
                        area_m2=None,
                        roofless=roofless,
                    )
                    for b_lat, b_lon, roofless in buildings
                    if not _near_precinct(s, b_lat, b_lon)
                ]
                out[s.key] = sorted(
                    (b for b in obs if b.dist_m <= radius_m),
                    key=lambda b: b.dist_m,
                )
        return out


def _parse_osm_buildings(data: dict) -> list[tuple[float, float, bool]]:
    """Overpass 応答 → (lat, lon, roofless) リスト。境内建物 (shrine/temple) は除外。"""
    seen: set[str] = set()
    pts: list[tuple[float, float, bool]] = []
    for el in data.get("elements", []):
        key = f"{el.get('type')}/{el.get('id')}"
        if key in seen:
            continue
        seen.add(key)
        tags = el.get("tags", {}) or {}
        bval = tags.get("building")
        if bval in _OSM_EXCLUDE_BUILDING:
            continue
        if el.get("type") == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:
            c = el.get("center") or {}
            lat, lon = c.get("lat"), c.get("lon")
        if lat is None or lon is None:
            continue
        pts.append((float(lat), float(lon), bval in _OSM_ROOFLESS_BUILDING))
    return pts


class StaticProvider:
    """テスト・デモ用: 事前に与えた建物点列から距離を計算する。

    要素は (lat, lon) または (lat, lon, area_m2) または BuildingObs 用の
    (lat, lon, area_m2, roofless)。
    """

    name = "static"

    def __init__(self, buildings: Iterable[tuple]):
        self.buildings = [tuple(b) for b in buildings]

    def bulk_for_shrines(
        self, shrines: Sequence[Shrine], radius_m: float
    ) -> dict[str, list[BuildingObs]]:
        out: dict[str, list[BuildingObs]] = {}
        for s in shrines:
            obs = []
            for b in self.buildings:
                b_lat, b_lon = b[0], b[1]
                if _near_precinct(s, b_lat, b_lon):
                    continue
                d = haversine_m(s.lat, s.lon, b_lat, b_lon)
                if d <= radius_m:
                    obs.append(
                        BuildingObs(
                            dist_m=d,
                            area_m2=b[2] if len(b) > 2 else None,
                            roofless=bool(b[3]) if len(b) > 3 else False,
                        )
                    )
            obs.sort(key=lambda b: b.dist_m)
            out[s.key] = obs
        return out


def make_provider(
    kind: str,
    tile_fetcher: TileFetcher | None = None,
    overpass: OverpassClient | None = None,
    gsi_source: str = config.GSI_BVMAP_DEFAULT_SOURCE,
) -> BuildingProvider:
    if kind == "gsi":
        assert tile_fetcher is not None
        return GsiBvmapProvider(tile_fetcher, source=gsi_source)
    if kind == "osm":
        assert overpass is not None
        return OsmBuildingProvider(overpass)
    raise ValueError(f"unknown building provider: {kind} (gsi / osm)")
