"""地理計算の純関数群。

外部依存なし。距離はすべてメートル、座標は WGS84 (lat, lon) 度。
タイル座標は Web メルカトル (slippy map) 方式。
"""
from __future__ import annotations

import math
from typing import Iterable, Iterator, Sequence

EARTH_RADIUS_M = 6_371_008.8


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2点間の大円距離 (m)。"""
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def local_xy_m(lat0: float, lon0: float, lat: float, lon: float) -> tuple[float, float]:
    """(lat0, lon0) を原点とする局所平面座標 (m)。数 km 以内の近距離計算用。"""
    kx = math.cos(math.radians(lat0)) * (math.pi / 180) * EARTH_RADIUS_M
    ky = (math.pi / 180) * EARTH_RADIUS_M
    return (lon - lon0) * kx, (lat - lat0) * ky


def point_segment_dist_m(
    lat: float, lon: float,
    lat_a: float, lon_a: float,
    lat_b: float, lon_b: float,
) -> float:
    """点から線分 A-B までの最短距離 (m)。局所平面近似 (数 km 以内で十分な精度)。"""
    ax, ay = local_xy_m(lat, lon, lat_a, lon_a)
    bx, by = local_xy_m(lat, lon, lat_b, lon_b)
    dx, dy = bx - ax, by - ay
    seg2 = dx * dx + dy * dy
    if seg2 <= 0:
        return math.hypot(ax, ay)
    t = -(ax * dx + ay * dy) / seg2
    t = max(0.0, min(1.0, t))
    return math.hypot(ax + t * dx, ay + t * dy)


def point_polyline_dist_m(lat: float, lon: float, verts: Sequence[tuple[float, float]]) -> float:
    """点からポリライン (頂点列 [(lat, lon), ...]) までの最短距離 (m)。"""
    if not verts:
        raise ValueError("empty polyline")
    if len(verts) == 1:
        return haversine_m(lat, lon, verts[0][0], verts[0][1])
    best = math.inf
    for (a_lat, a_lon), (b_lat, b_lon) in zip(verts, verts[1:]):
        d = point_segment_dist_m(lat, lon, a_lat, a_lon, b_lat, b_lon)
        if d < best:
            best = d
    return best


def polyline_length_m(verts: Sequence[tuple[float, float]]) -> float:
    """ポリラインの全長 (m)。"""
    return sum(
        haversine_m(a[0], a[1], b[0], b[1]) for a, b in zip(verts, verts[1:])
    )


# ---------------------------------------------------------------------------
# Slippy map タイル座標
# ---------------------------------------------------------------------------

def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    """経緯度 → タイル座標 (x, y)。"""
    n = 1 << z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def lonlat_to_tile_frac(lon: float, lat: float, z: int) -> tuple[float, float]:
    """経緯度 → タイル座標 (小数)。整数部がタイル番号、小数部がタイル内位置。"""
    n = 1 << z
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(lat)
    y = (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n
    return x, y


def tile_to_lonlat(x: float, y: float, z: int) -> tuple[float, float]:
    """タイル座標 (小数可) の北西角 → (lon, lat)。"""
    n = 1 << z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def tile_bounds(x: int, y: int, z: int) -> tuple[float, float, float, float]:
    """タイルの範囲 (west, south, east, north)。"""
    west, north = tile_to_lonlat(x, y, z)
    east, south = tile_to_lonlat(x + 1, y + 1, z)
    return west, south, east, north


def tiles_covering_disc(lat: float, lon: float, radius_m: float, z: int) -> list[tuple[int, int]]:
    """中心 (lat, lon)・半径 radius_m の円板を覆うタイル (x, y) の一覧。"""
    dlat = radius_m / 111_320.0
    coslat = max(math.cos(math.radians(lat)), 1e-6)
    dlon = radius_m / (111_320.0 * coslat)
    x0, y0 = lonlat_to_tile(lon - dlon, lat + dlat, z)  # 北西
    x1, y1 = lonlat_to_tile(lon + dlon, lat - dlat, z)  # 南東
    return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


# ---------------------------------------------------------------------------
# 近傍検索用の簡易グリッドインデックス
# ---------------------------------------------------------------------------

class GridIndex:
    """経緯度点の近傍検索用ハッシュグリッド。セル幅は度単位。

    数千×数万件の総当たりを避けるための素朴な実装。値は任意のオブジェクト。
    """

    def __init__(self, cell_deg: float = 0.01):
        self.cell_deg = cell_deg
        self._cells: dict[tuple[int, int], list[tuple[float, float, object]]] = {}

    def _key(self, lat: float, lon: float) -> tuple[int, int]:
        return (int(math.floor(lat / self.cell_deg)), int(math.floor(lon / self.cell_deg)))

    def insert(self, lat: float, lon: float, value: object) -> None:
        self._cells.setdefault(self._key(lat, lon), []).append((lat, lon, value))

    def near(self, lat: float, lon: float, radius_m: float) -> Iterator[tuple[float, float, object]]:
        """半径 radius_m 円板と交差しうるセル内の全点を返す (距離での最終判定は呼び出し側)。"""
        dlat = radius_m / 111_320.0
        coslat = max(math.cos(math.radians(lat)), 1e-6)
        dlon = radius_m / (111_320.0 * coslat)
        k0 = self._key(lat - dlat, lon - dlon)
        k1 = self._key(lat + dlat, lon + dlon)
        for ky in range(k0[0], k1[0] + 1):
            for kx in range(k0[1], k1[1] + 1):
                yield from self._cells.get((ky, kx), ())


def densify_polyline(
    verts: Sequence[tuple[float, float]], step_m: float
) -> list[tuple[float, float]]:
    """頂点間隔が step_m を超えないよう中間点を補ったポリラインを返す。

    グリッドインデックスに載せる際、頂点だけだと長い直線区間の中間部分が
    近傍検索から漏れるのを防ぐ。
    """
    pts = list(verts)
    if len(pts) < 2:
        return pts
    out: list[tuple[float, float]] = [pts[0]]
    for (a_lat, a_lon), (b_lat, b_lon) in zip(pts, pts[1:]):
        d = haversine_m(a_lat, a_lon, b_lat, b_lon)
        n = int(d // step_m)
        for i in range(1, n + 1):
            t = i * step_m / d
            if t >= 1.0:
                break
            out.append((a_lat + (b_lat - a_lat) * t, a_lon + (b_lon - a_lon) * t))
        out.append((b_lat, b_lon))
    return out


def polygon_area_m2(verts: Sequence[tuple[float, float]]) -> float:
    """閉じたリング (始点=終点でも可) の面積 (m²)。局所平面近似 + 靴紐公式。"""
    pts = list(verts)
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        return 0.0
    lat0, lon0 = pts[0]
    xy = [local_xy_m(lat0, lon0, lat, lon) for lat, lon in pts]
    s = 0.0
    for (x1, y1), (x2, y2) in zip(xy, xy[1:] + [xy[0]]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def centroid(verts: Iterable[tuple[float, float]]) -> tuple[float, float]:
    """頂点列の単純平均重心 (lat, lon)。閉じたリングの重複終点は呼び出し側で除くこと。"""
    pts = list(verts)
    if not pts:
        raise ValueError("empty vertex list")
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
