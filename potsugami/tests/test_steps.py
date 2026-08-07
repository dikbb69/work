from potsugami.config import StepsParams
from potsugami.shrines import Shrine
from potsugami.steps import (
    ShrineSteps,
    StepsWay,
    build_steps_query,
    coverage_stats,
    match_steps,
    parse_steps,
)


def _shrine(key, lat, lon):
    return Shrine(key=key, lat=lat, lon=lon, name=key,
                  tags={"amenity": "place_of_worship", "religion": "shinto"})


class GradientElevation:
    """経度に比例して高くなる合成地形 (1 度 = 80000m 勾配)。"""

    def elevation(self, lat, lon):
        return (lon - 140.0) * 80_000.0


def test_step_count_tag_parse():
    assert StepsWay("way/1", [(0, 0), (1, 1)], {"step_count": "148"}).step_count_tag == 148
    assert StepsWay("way/1", [(0, 0), (1, 1)], {"step_count": " 20 ; x"}).step_count_tag == 20
    assert StepsWay("way/1", [(0, 0), (1, 1)], {"step_count": "many"}).step_count_tag is None
    assert StepsWay("way/1", [(0, 0), (1, 1)], {}).step_count_tag is None


def test_build_steps_query():
    q = build_steps_query("茨城県")
    assert "JP-08" in q
    assert '"highway"="steps"' in q
    assert "out tags geom" in q


def test_parse_steps():
    data = {
        "elements": [
            {"type": "way", "id": 10,
             "geometry": [{"lat": 35.0, "lon": 140.0}, {"lat": 35.001, "lon": 140.0}],
             "tags": {"highway": "steps", "step_count": "50"}},
            {"type": "node", "id": 11, "lat": 35.0, "lon": 140.0},
            {"type": "way", "id": 12, "geometry": [{"lat": 35.0, "lon": 140.0}]},
        ]
    }
    got = parse_steps(data)
    assert [w.key for w in got] == ["way/10"]
    assert got[0].step_count_tag == 50
    assert 105 < got[0].length_m < 118


def test_match_within_radius_only():
    s1 = _shrine("node/1", 35.0, 140.0)
    s2 = _shrine("node/2", 35.1, 140.1)
    # s1 から約 55m 西に始まる石段
    near = StepsWay("way/100", [(35.0, 139.9994), (35.0, 139.999)], {})
    far = StepsWay("way/101", [(35.005, 140.0), (35.006, 140.0)], {})
    m = match_steps([s1, s2], [near, far], None, StepsParams())
    assert m["node/1"].matched
    assert [w.key for w in m["node/1"].ways] == ["way/100"]
    assert not m["node/2"].matched


def test_elevation_diff_and_estimate():
    s = _shrine("node/1", 35.0, 140.001)
    # 東西方向の石段: 西端 140.0000 (標高 0m)、東端 140.0005 (標高 40m)
    w = StepsWay("way/1", [(35.0, 140.0), (35.0, 140.0005)], {})
    p = StepsParams()
    m = match_steps([s], [w], GradientElevation(), p)
    ss = m["node/1"]
    assert ss.matched
    assert ss.elev_diff_m == 40.0
    assert ss.est_steps_min == int(40 / p.riser_max_m)  # 133
    assert ss.est_steps_max == int(40 / p.riser_min_m)  # 222


def test_split_ways_aggregate_elevation():
    s = _shrine("node/1", 35.0, 140.001)
    w1 = StepsWay("way/1", [(35.0, 140.0), (35.0, 140.00025)], {})
    w2 = StepsWay("way/2", [(35.0, 140.00025), (35.0, 140.0005)], {"step_count": "80"})
    m = match_steps([s], [w1, w2], GradientElevation(), StepsParams())
    ss = m["node/1"]
    assert len(ss.ways) == 2
    assert ss.elev_diff_m == 40.0  # 全端点の max - min
    assert ss.step_count_tagged == 80
    assert 40 < ss.total_length_m < 50  # 経度 0.0005 度 ≈ 45.6m (2 本合計)


def test_no_elevation_provider_still_matches():
    s = _shrine("node/1", 35.0, 140.001)
    w = StepsWay("way/1", [(35.0, 140.0), (35.0, 140.0005)], {})
    m = match_steps([s], [w], None, StepsParams())
    ss = m["node/1"]
    assert ss.matched
    assert ss.elev_diff_m is None
    assert ss.est_steps_min is None


def test_coverage_stats():
    s1, s2 = _shrine("node/1", 35.0, 140.0), _shrine("node/2", 36.0, 140.0)
    w = StepsWay("way/1", [(35.0, 140.0002), (35.0, 140.0004)], {"step_count": "10"})
    matches = match_steps([s1, s2], [w], None, StepsParams())
    cov = coverage_stats([s1, s2], [w], matches)
    assert cov.n_shrines == 2
    assert cov.n_matched == 1
    assert cov.n_with_count_tag == 1
    assert cov.n_steps_ways == 1
    assert cov.match_rate == 0.5


def test_shrine_steps_default():
    assert not ShrineSteps().matched
