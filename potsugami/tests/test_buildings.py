import math

from mvt_encoder import encode_feature, encode_layer, encode_tile

from potsugami import mvt
from potsugami.buildings import (
    GsiBvmapProvider,
    OsmBuildingProvider,
    StaticProvider,
    _parse_osm_buildings,
)
from potsugami.geo import lonlat_to_tile, lonlat_to_tile_frac
from potsugami.shrines import Shrine

SHRINE = Shrine(key="node/1", lat=35.2, lon=140.1, name="試験神社",
                tags={"amenity": "place_of_worship", "religion": "shinto"})


def _offset_latlon(lat, lon, dx_m, dy_m):
    return (
        lat + dy_m / 111_320.0,
        lon + dx_m / (111_320.0 * math.cos(math.radians(lat))),
    )


def test_static_provider_filters_radius():
    b_near = _offset_latlon(35.2, 140.1, 0, 100)
    b_far = _offset_latlon(35.2, 140.1, 0, 1500)
    p = StaticProvider([b_near, b_far])
    got = p.bulk_for_shrines([SHRINE], 1000.0)["node/1"]
    assert len(got) == 1
    assert 95 < got[0].dist_m < 108
    assert got[0].area_m2 is None
    assert got[0].roofless is False


def test_static_provider_area_and_roofless():
    b = _offset_latlon(35.2, 140.1, 100, 0)
    p = StaticProvider([(b[0], b[1], 250.0, True)])
    got = p.bulk_for_shrines([SHRINE], 1000.0)["node/1"]
    assert got[0].area_m2 == 250.0
    assert got[0].roofless is True


def test_static_provider_precinct_exclusion():
    b = _offset_latlon(35.2, 140.1, 100, 0)
    shrine = Shrine(key="node/9", lat=35.2, lon=140.1, name=None, tags={},
                    precinct_points=[(b[0], b[1])])
    p = StaticProvider([b])
    assert p.bulk_for_shrines([shrine], 1000.0)["node/9"] == []


# ---------------------------------------------------------------------------
# GSI ベクトルタイルプロバイダ
# ---------------------------------------------------------------------------

def _building_square(z, tx, ty, extent, lat, lon, size_px=8):
    """(lat, lon) を左上角とする extent 座標系の正方形リング (閉じない)。"""
    fx, fy = lonlat_to_tile_frac(lon, lat, z)
    px = int((fx - tx) * extent)
    py = int((fy - ty) * extent)
    return [(px, py), (px + size_px, py), (px + size_px, py + size_px), (px, py + size_px)]


class FakeTileFetcher:
    def __init__(self, tiles: dict):
        self.tiles = tiles  # {(x, y): bytes}
        self.calls = []

    def fetch(self, url_template, z, x, y, kind):
        self.calls.append((z, x, y, kind))
        return self.tiles.get((x, y))


def _make_tile(z, tx, ty, rings, layer_name="BldA", extent=4096, tags_list=None):
    feats = []
    for i, ring in enumerate(rings):
        tag_idx = []
        keys, values = [], []
        if tags_list and tags_list[i]:
            for j, (k, v) in enumerate(tags_list[i].items()):
                keys.append(k)
                values.append(v)
                tag_idx += [j, j]
        feats.append((encode_feature(None, mvt.GEOM_POLYGON, [ring], tag_idx), keys, values))
    # 全 feature でキー/値テーブルを共有できるよう単純化: 1 feature ずつ layer を分けず、
    # tags_list がある場合は最初の feature のキー/値を使う
    all_keys = feats[0][1] if feats and tags_list else []
    all_values = feats[0][2] if feats and tags_list else []
    return encode_tile([
        encode_layer(layer_name, [f[0] for f in feats], all_keys, all_values, extent=extent)
    ])


def test_gsi_provider_returns_distance_and_area():
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    b_lat, b_lon = _offset_latlon(SHRINE.lat, SHRINE.lon, 100, 0)
    ring = _building_square(z, tx, ty, 4096, b_lat, b_lon)
    fetcher = FakeTileFetcher({(tx, ty): _make_tile(z, tx, ty, [ring])})
    p = GsiBvmapProvider(fetcher)
    got = p.bulk_for_shrines([SHRINE], 1000.0)["node/1"]
    assert len(got) == 1
    assert 80 < got[0].dist_m < 110  # ポリゴン最近縁までの距離
    # 8px 四方 @z16: 1px ≈ 0.15m² 程度ではなく… タイル幅 ≈ 470m/4096px ≈ 0.115m/px
    # → 8px ≈ 0.92m 四方 ≈ 0.85m²。面積が正で妥当なオーダーであること
    assert got[0].area_m2 is not None
    assert 0.1 < got[0].area_m2 < 10


def test_gsi_provider_roofless_ftcode():
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    b_lat, b_lon = _offset_latlon(SHRINE.lat, SHRINE.lon, 100, 0)
    ring = _building_square(z, tx, ty, 4096, b_lat, b_lon)
    tile = _make_tile(z, tx, ty, [ring], tags_list=[{"ftCode": 3103}])
    fetcher = FakeTileFetcher({(tx, ty): tile})
    got = GsiBvmapProvider(fetcher).bulk_for_shrines([SHRINE], 1000.0)["node/1"]
    assert len(got) == 1
    assert got[0].roofless is True


def test_gsi_provider_ignores_unrelated_layers():
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    b_lat, b_lon = _offset_latlon(SHRINE.lat, SHRINE.lon, 100, 0)
    ring = _building_square(z, tx, ty, 4096, b_lat, b_lon)
    fetcher = FakeTileFetcher({(tx, ty): _make_tile(z, tx, ty, [ring], layer_name="RdCL")})
    p = GsiBvmapProvider(fetcher)
    assert p.bulk_for_shrines([SHRINE], 1000.0)["node/1"] == []


def test_gsi_provider_excludes_centroid_outside_tile():
    """クリップバッファ相当: タイル範囲外に重心があるポリゴンは数えない。"""
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    ring = [(-100, -100), (-92, -100), (-92, -92), (-100, -92)]
    fetcher = FakeTileFetcher({(tx, ty): _make_tile(z, tx, ty, [ring])})
    p = GsiBvmapProvider(fetcher)
    assert p.bulk_for_shrines([SHRINE], 1000.0)["node/1"] == []


def test_gsi_provider_layer_name_variants():
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    b_lat, b_lon = _offset_latlon(SHRINE.lat, SHRINE.lon, 100, 0)
    ring = _building_square(z, tx, ty, 4096, b_lat, b_lon)
    for name in ("BldA", "blda", "building", "建築物"):
        fetcher = FakeTileFetcher({(tx, ty): _make_tile(z, tx, ty, [ring], layer_name=name)})
        got = GsiBvmapProvider(fetcher).bulk_for_shrines([SHRINE], 1000.0)["node/1"]
        assert len(got) == 1, name


def test_gsi_provider_experimental_source():
    from potsugami import config
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    b_lat, b_lon = _offset_latlon(SHRINE.lat, SHRINE.lon, 100, 0)
    ring = _building_square(z, tx, ty, 4096, b_lat, b_lon)
    fetcher = FakeTileFetcher(
        {(tx, ty): _make_tile(z, tx, ty, [ring], layer_name="building")})
    p = GsiBvmapProvider(fetcher, source="experimental")
    got = p.bulk_for_shrines([SHRINE], 1000.0)["node/1"]
    assert len(got) == 1
    assert "experimental_bvmap" in fetcher.calls[0][3] or \
        fetcher.calls[0][3] == "experimental"
    assert "experimental_bvmap" in config.GSI_BVMAP_SOURCES["experimental"][0]


def test_gsi_provider_unknown_source():
    import pytest
    with pytest.raises(ValueError):
        GsiBvmapProvider(FakeTileFetcher({}), source="nope")


def test_gsi_provider_tile_decode_cached_across_shrines():
    z = 16
    tx, ty = lonlat_to_tile(SHRINE.lon, SHRINE.lat, z)
    fetcher = FakeTileFetcher({(tx, ty): _make_tile(z, tx, ty, [])})
    p = GsiBvmapProvider(fetcher)
    s2 = Shrine(key="node/2", lat=SHRINE.lat + 0.0001, lon=SHRINE.lon, name=None, tags={})
    p.bulk_for_shrines([SHRINE, s2], 300.0)
    keys = [(x, y) for _z, x, y, _k in fetcher.calls]
    assert len(set(keys)) == len(keys)  # 同一タイルの再フェッチなし


# ---------------------------------------------------------------------------
# OSM プロバイダ
# ---------------------------------------------------------------------------

def test_parse_osm_buildings_excludes_shrine_buildings():
    data = {"elements": [
        {"type": "way", "id": 1, "center": {"lat": 35.2, "lon": 140.1},
         "tags": {"building": "shrine"}},
        {"type": "way", "id": 2, "center": {"lat": 35.201, "lon": 140.1},
         "tags": {"building": "house"}},
        {"type": "way", "id": 2, "center": {"lat": 35.201, "lon": 140.1},
         "tags": {"building": "house"}},  # 重複 ID は 1 回だけ
        {"type": "way", "id": 3, "tags": {"building": "yes"}},  # center なし
        {"type": "way", "id": 4, "center": {"lat": 35.202, "lon": 140.1},
         "tags": {"building": "greenhouse"}},
    ]}
    got = _parse_osm_buildings(data)
    assert len(got) == 2
    roofless = {r for _lat, _lon, r in got}
    assert roofless == {False, True}


class FakeOverpass:
    def __init__(self, response):
        self.response = response
        self.queries = []

    def query(self, ql):
        self.queries.append(ql)
        return self.response


def test_osm_provider_assigns_by_distance():
    b1 = _offset_latlon(SHRINE.lat, SHRINE.lon, 120, 0)
    b2 = _offset_latlon(SHRINE.lat, SHRINE.lon, 5000, 0)  # 別の神社の周辺の建物
    response = {"elements": [
        {"type": "way", "id": 1, "center": {"lat": b1[0], "lon": b1[1]},
         "tags": {"building": "house"}},
        {"type": "way", "id": 2, "center": {"lat": b2[0], "lon": b2[1]},
         "tags": {"building": "house"}},
    ]}
    client = FakeOverpass(response)
    p = OsmBuildingProvider(client, batch_size=40)
    got = p.bulk_for_shrines([SHRINE], 1000.0)["node/1"]
    assert len(got) == 1
    assert 110 < got[0].dist_m < 130
    assert "around:1000" in client.queries[0]


def test_osm_provider_batches():
    shrines = [
        Shrine(key=f"node/{i}", lat=35.2 + i * 0.01, lon=140.1, name=None, tags={})
        for i in range(90)
    ]
    client = FakeOverpass({"elements": []})
    p = OsmBuildingProvider(client, batch_size=40)
    got = p.bulk_for_shrines(shrines, 500.0)
    assert len(client.queries) == 3  # 40 + 40 + 10
    assert all(got[s.key] == [] for s in shrines)
