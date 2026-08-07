import math

from potsugami.config import NuisanceParams
from potsugami.nuisance import (
    NuisanceFeature,
    NuisanceIndex,
    build_major_road_query,
    build_nuisance_query,
    parse_nuisance,
    parse_roads,
)
from potsugami.shrines import Shrine


def _shrine(lat, lon):
    return Shrine(key="node/1", lat=lat, lon=lon, name="X", tags={})


def _offset(lat, lon, dx_m, dy_m):
    return (
        lat + dy_m / 111_320.0,
        lon + dx_m / (111_320.0 * math.cos(math.radians(lat))),
    )


def test_queries_contain_selectors():
    q = build_nuisance_query("千葉県")
    assert "JP-12" in q
    assert "solar" in q and "quarry" in q and "golf_course" in q
    r = build_major_road_query("千葉県")
    assert "trunk" in r and "secondary" in r


def test_parse_nuisance_classification():
    data = {"elements": [
        {"type": "way", "id": 1, "tags": {"power": "plant", "plant:source": "solar"},
         "geometry": [{"lat": 35.0, "lon": 140.0}, {"lat": 35.001, "lon": 140.0}]},
        {"type": "way", "id": 2, "tags": {"landuse": "quarry"},
         "center": {"lat": 35.1, "lon": 140.1}},
        {"type": "way", "id": 3, "tags": {"landuse": "farmland"},
         "center": {"lat": 35.2, "lon": 140.2}},  # 対象外
    ]}
    feats = parse_nuisance(data)
    assert [f.kind for f in feats] == ["solar", "quarry"]
    assert len(feats[0].verts) == 2
    assert feats[1].verts == [(35.1, 140.1)]  # geometry なし → center


def test_parse_roads():
    data = {"elements": [
        {"type": "way", "id": 1,
         "geometry": [{"lat": 35.0, "lon": 140.0}, {"lat": 35.0, "lon": 140.01}]},
        {"type": "node", "id": 2, "lat": 35.0, "lon": 140.0},
    ]}
    assert len(parse_roads(data)) == 1


def test_index_near_solar_penalized():
    s = _shrine(35.0, 140.0)
    solar_edge = _offset(35.0, 140.0, 100, 0)
    feat = NuisanceFeature("solar", [solar_edge, _offset(35.0, 140.0, 400, 0)])
    idx = NuisanceIndex([feat], [])
    res = idx.evaluate(s)
    p = NuisanceParams()
    assert res.mult == p.near_mult
    assert res.nearest_m is not None and 90 < res.nearest_m < 110
    assert any(f.startswith("solar@") for f in res.flags)


def test_index_far_solar_smaller_penalty():
    s = _shrine(35.0, 140.0)
    feat = NuisanceFeature("solar", [_offset(35.0, 140.0, 300, 0)])
    idx = NuisanceIndex([feat], [])
    res = idx.evaluate(s)
    assert res.mult == NuisanceParams().far_mult


def test_index_no_nuisance():
    s = _shrine(35.0, 140.0)
    feat = NuisanceFeature("solar", [_offset(35.0, 140.0, 3000, 0)])
    idx = NuisanceIndex([feat], [])
    res = idx.evaluate(s)
    assert res.mult == 1.0
    assert res.flags == []


def test_index_major_road():
    s = _shrine(35.0, 140.0)
    road = [_offset(35.0, 140.0, -500, 60), _offset(35.0, 140.0, 500, 60)]
    idx = NuisanceIndex([], [road])
    res = idx.evaluate(s)
    assert res.mult == NuisanceParams().road_mult
    assert any(f.startswith("road@") for f in res.flags)


def test_index_combined_multiplies():
    s = _shrine(35.0, 140.0)
    feat = NuisanceFeature("industrial", [_offset(35.0, 140.0, 120, 0)])
    road = [_offset(35.0, 140.0, -500, 50), _offset(35.0, 140.0, 500, 50)]
    idx = NuisanceIndex([feat], [road])
    p = NuisanceParams()
    assert idx.evaluate(s).mult == round(p.near_mult * p.road_mult, 4)
