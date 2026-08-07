import math

from potsugami.geo import (
    GridIndex,
    centroid,
    haversine_m,
    lonlat_to_tile,
    lonlat_to_tile_frac,
    point_polyline_dist_m,
    point_segment_dist_m,
    polyline_length_m,
    tile_bounds,
    tiles_covering_disc,
)


def test_haversine_tokyo_osaka():
    d = haversine_m(35.6812, 139.7671, 34.7025, 135.4959)
    assert 390_000 < d < 410_000


def test_haversine_zero():
    assert haversine_m(35.0, 139.0, 35.0, 139.0) == 0.0


def test_haversine_small_distance():
    # 緯度 0.001 度 ≈ 111.3m
    d = haversine_m(35.0, 139.0, 35.001, 139.0)
    assert 110 < d < 113


def test_point_segment_perpendicular():
    # 東西の線分の真上 0.001 度 (≈111m)
    d = point_segment_dist_m(35.001, 139.005, 35.0, 139.0, 35.0, 139.01)
    assert 105 < d < 118


def test_point_segment_beyond_endpoint():
    d = point_segment_dist_m(35.0, 138.99, 35.0, 139.0, 35.0, 139.01)
    expected = haversine_m(35.0, 138.99, 35.0, 139.0)
    assert abs(d - expected) < expected * 0.02


def test_point_polyline_takes_min():
    verts = [(35.0, 139.0), (35.0, 139.01), (35.01, 139.01)]
    d = point_polyline_dist_m(35.0, 139.0201, verts)
    # 頂点 (35.0, 139.01) が最近傍… ではなく縦の線分への垂線はないので端点距離
    expected = haversine_m(35.0, 139.0201, 35.0, 139.01)
    assert d <= expected + 1


def test_polyline_length():
    verts = [(35.0, 139.0), (35.0, 139.001), (35.0, 139.002)]
    ln = polyline_length_m(verts)
    assert 178 < ln < 186


def test_tile_roundtrip():
    lon, lat, z = 139.7671, 35.6812, 16
    x, y = lonlat_to_tile(lon, lat, z)
    west, south, east, north = tile_bounds(x, y, z)
    assert west <= lon < east
    assert south < lat <= north


def test_tile_frac_consistent_with_int():
    lon, lat, z = 140.1, 35.2, 15
    fx, fy = lonlat_to_tile_frac(lon, lat, z)
    assert (int(fx), int(fy)) == lonlat_to_tile(lon, lat, z)


def test_tiles_covering_disc_contains_center():
    lat, lon, z = 35.2, 140.1, 16
    tiles = tiles_covering_disc(lat, lon, 300, z)
    assert lonlat_to_tile(lon, lat, z) in tiles
    # z16 タイルは幅 ~470m なので半径 300m は最大 9 枚に収まる
    assert 1 <= len(tiles) <= 9


def test_grid_index_finds_all_within_radius():
    idx = GridIndex(cell_deg=0.005)
    pts = [(35.0 + i * 0.0005, 140.0 + j * 0.0005, (i, j))
           for i in range(10) for j in range(10)]
    for lat, lon, v in pts:
        idx.insert(lat, lon, v)
    center = (35.002, 140.002)
    radius = 200.0
    got = {v for _lat, _lon, v in idx.near(center[0], center[1], radius)}
    for lat, lon, v in pts:
        if haversine_m(center[0], center[1], lat, lon) <= radius:
            assert v in got, f"missing point {v}"


def test_centroid():
    lat, lon = centroid([(35.0, 140.0), (35.002, 140.0), (35.001, 140.003)])
    assert abs(lat - 35.001) < 1e-9
    assert abs(lon - 140.001) < 1e-9
