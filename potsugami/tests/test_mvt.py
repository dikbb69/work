from mvt_encoder import encode_feature, encode_layer, encode_tile

from potsugami import mvt


def _square(x0: int, y0: int, size: int) -> list[tuple[int, int]]:
    return [(x0, y0), (x0 + size, y0), (x0 + size, y0 + size), (x0, y0 + size)]


def test_roundtrip_polygon_with_tags():
    keys = ["name", "height", "ok", "neg"]
    values = ["社殿", 12.5, True, -3]
    feat = encode_feature(
        fid=42,
        geom_type=mvt.GEOM_POLYGON,
        parts=[_square(100, 200, 50)],
        tag_indices=[0, 0, 1, 1, 2, 2, 3, 3],
    )
    tile = encode_tile([encode_layer("building", [feat], keys, values)])

    layers = mvt.decode(tile)
    assert set(layers) == {"building"}
    layer = layers["building"]
    assert layer.extent == 4096
    assert len(layer.features) == 1
    f = layer.features[0]
    assert f.fid == 42
    assert f.geom_type == mvt.GEOM_POLYGON
    assert f.tags == {"name": "社殿", "height": 12.5, "ok": True, "neg": -3}
    # ClosePath で始点が複製される
    ring = f.parts[0]
    assert ring[0] == (100, 200)
    assert ring[-1] == ring[0]
    assert (150, 250) in ring


def test_negative_deltas_across_features():
    # 2 つ目の feature はカーソルがリセットされる (feature 単位で独立)
    f1 = encode_feature(None, mvt.GEOM_POLYGON, [_square(1000, 1000, 10)], [])
    f2 = encode_feature(None, mvt.GEOM_POLYGON, [_square(50, 60, 10)], [])
    tile = encode_tile([encode_layer("building", [f1, f2], [], [])])
    layer = mvt.decode(tile)["building"]
    assert layer.features[0].parts[0][0] == (1000, 1000)
    assert layer.features[1].parts[0][0] == (50, 60)


def test_multi_ring_polygon():
    parts = [_square(0, 0, 100), _square(20, 20, 10)]
    feat = encode_feature(None, mvt.GEOM_POLYGON, parts, [])
    tile = encode_tile([encode_layer("building", [feat], [], [])])
    f = mvt.decode(tile)["building"].features[0]
    assert len(f.parts) == 2
    assert f.parts[1][0] == (20, 20)


def test_point_geometry():
    feat = encode_feature(7, mvt.GEOM_POINT, [[(10, 20)], [(30, 40)]], [])
    tile = encode_tile([encode_layer("symbol", [feat], [], [])])
    f = mvt.decode(tile)["symbol"].features[0]
    assert f.parts == [[(10, 20)], [(30, 40)]]


def test_linestring_geometry():
    feat = encode_feature(
        None, mvt.GEOM_LINESTRING, [[(0, 0), (10, 0), (10, 10)]], []
    )
    tile = encode_tile([encode_layer("road", [feat], [], [])])
    f = mvt.decode(tile)["road"].features[0]
    assert f.parts == [[(0, 0), (10, 0), (10, 10)]]


def test_multiple_layers_and_custom_extent():
    l1 = encode_layer("building", [], [], [], extent=8192)
    l2 = encode_layer("道路", [], [], [])
    layers = mvt.decode(encode_tile([l1, l2]))
    assert layers["building"].extent == 8192
    assert "道路" in layers


def test_truncated_input_raises():
    import pytest
    with pytest.raises(mvt.MvtError):
        mvt.decode(b"\x1a\xff")  # 長さだけ宣言して中身がない
