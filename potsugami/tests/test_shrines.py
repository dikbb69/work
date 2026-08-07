from potsugami.shrines import Shrine, build_query, dedupe, parse_elements


def test_build_query_basic():
    q = build_query("千葉県")
    assert 'ISO3166-2"="JP-12' in q
    assert '"religion"="shinto"' in q
    assert '"building"="shrine"' in q
    assert "wayside_shrine" not in q
    assert "out tags center" in q


def test_build_query_hokora():
    q = build_query("JP-08", include_hokora=True)
    assert "wayside_shrine" in q
    assert 'JP-08' in q


def test_build_query_unknown_pref():
    import pytest
    with pytest.raises(ValueError):
        build_query("存在しない県")


def test_parse_elements():
    data = {
        "elements": [
            {"type": "node", "id": 1, "lat": 35.0, "lon": 140.0,
             "tags": {"name": "甲神社"}},
            {"type": "way", "id": 2, "center": {"lat": 35.1, "lon": 140.1},
             "tags": {"building": "shrine"}},
            {"type": "way", "id": 3, "tags": {}},  # center なし → 捨てる
        ]
    }
    got = parse_elements(data)
    assert [s.key for s in got] == ["node/1", "way/2"]
    assert got[0].name == "甲神社"
    assert got[1].name is None


def _shrine(key, lat, lon, name=None, tags=None):
    tags = dict(tags or {})
    if name:
        tags["name"] = name
    return Shrine(key=key, lat=lat, lon=lon, name=name, tags=tags)


def test_dedupe_merges_node_and_way():
    pow_tags = {"amenity": "place_of_worship", "religion": "shinto"}
    a = _shrine("node/1", 35.0, 140.0, "諏訪神社", pow_tags)
    # 30m ほど北の社殿ポリゴン (名前なし)
    b = _shrine("way/2", 35.00027, 140.0, None, {"building": "shrine"})
    # 500m 離れた別の神社
    c = _shrine("node/3", 35.0045, 140.0, "浅間神社", pow_tags)
    got = dedupe([a, b, c])
    assert len(got) == 2
    rep = next(s for s in got if s.name == "諏訪神社")
    assert rep.key == "node/1"  # POW+shinto が代表
    assert "way/2" in rep.merged_keys
    assert rep.tags.get("building") == "shrine"  # タグは補完される
    # 統合された社殿の座標は境内除外用に残る
    assert rep.precinct_points == [(35.00027, 140.0)]


def test_dedupe_keeps_differently_named_neighbors():
    """40m 差で隣接していても、両方に異なる名前があれば別の神社として残す。"""
    pow_tags = {"amenity": "place_of_worship", "religion": "shinto"}
    a = _shrine("node/1", 35.0, 140.0, "諏訪神社", pow_tags)
    b = _shrine("node/2", 35.00035, 140.0, "琴平神社", pow_tags)
    got = dedupe([a, b])
    assert len(got) == 2


def test_dedupe_merges_name_containment():
    pow_tags = {"amenity": "place_of_worship", "religion": "shinto"}
    a = _shrine("node/1", 35.0, 140.0, "諏訪神社", pow_tags)
    b = _shrine("way/2", 35.0002, 140.0, "諏訪神社 拝殿", {"building": "shrine"})
    got = dedupe([a, b])
    assert len(got) == 1


def test_dedupe_fills_name_from_secondary():
    a = _shrine("way/1", 35.0, 140.0, None,
                {"amenity": "place_of_worship", "religion": "shinto"})
    b = _shrine("node/2", 35.0002, 140.0, "白山神社", {"building": "shrine"})
    got = dedupe([a, b])
    assert len(got) == 1
    assert got[0].key == "way/1"
    assert got[0].name == "白山神社"


def test_dedupe_keeps_distant_shrines():
    pow_tags = {"amenity": "place_of_worship", "religion": "shinto"}
    shrines = [
        _shrine(f"node/{i}", 35.0 + i * 0.01, 140.0, f"第{i}神社", pow_tags)
        for i in range(5)
    ]
    assert len(dedupe(shrines)) == 5


def test_dedupe_prefers_richer_tags():
    t1 = {"amenity": "place_of_worship", "religion": "shinto"}
    t2 = {"amenity": "place_of_worship", "religion": "shinto",
          "name:en": "X", "operator": "y"}
    a = _shrine("node/1", 35.0, 140.0, "甲神社", t1)
    b = _shrine("way/2", 35.0001, 140.0, "甲神社", t2)
    got = dedupe([a, b])
    assert len(got) == 1
    assert got[0].key == "way/2"


def test_display_name_and_url():
    s = _shrine("node/5", 35.0, 140.0)
    assert s.display_name == "(名称未登録)"
    assert s.osm_url.endswith("/node/5")
