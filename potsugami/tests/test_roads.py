import math

from potsugami.roads import _batch_query, nearest_road_distances
from potsugami.shrines import Shrine


def _offset(lat, lon, dx_m, dy_m):
    return (
        lat + dy_m / 111_320.0,
        lon + dx_m / (111_320.0 * math.cos(math.radians(lat))),
    )


class FakeOverpass:
    def __init__(self, response):
        self.response = response
        self.queries = []

    def query(self, ql):
        self.queries.append(ql)
        return self.response


def test_batch_query_format():
    s = Shrine(key="node/1", lat=35.2, lon=140.1, name=None, tags={})
    q = _batch_query([s], 500.0)
    assert "around:500" in q
    assert "highway" in q and "track" in q
    assert "out geom" in q


def test_nearest_road_distance():
    s = Shrine(key="node/1", lat=35.0, lon=140.0, name=None, tags={})
    a = _offset(35.0, 140.0, -300, 80)
    b = _offset(35.0, 140.0, 300, 80)
    response = {"elements": [
        {"type": "way", "id": 1,
         "geometry": [{"lat": a[0], "lon": a[1]}, {"lat": b[0], "lon": b[1]}]},
    ]}
    client = FakeOverpass(response)
    got = nearest_road_distances(client, [s])
    assert got["node/1"] is not None
    assert 70 < got["node/1"] < 92


def test_no_road_within_radius():
    s = Shrine(key="node/1", lat=35.0, lon=140.0, name=None, tags={})
    client = FakeOverpass({"elements": []})
    got = nearest_road_distances(client, [s])
    assert got["node/1"] is None


def test_batching():
    shrines = [
        Shrine(key=f"node/{i}", lat=35.0 + i * 0.01, lon=140.0, name=None, tags={})
        for i in range(45)
    ]
    client = FakeOverpass({"elements": []})
    nearest_road_distances(client, shrines, batch_size=20)
    assert len(client.queries) == 3
