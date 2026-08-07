import csv
import json

from potsugami import config
from potsugami.buildings import StaticProvider
from potsugami.nuisance import NuisanceFeature, NuisanceIndex
from potsugami.pipeline import build_candidates
from potsugami.report import (
    link_directions,
    link_gmap,
    link_gsi,
    link_streetview,
    write_report,
)
from potsugami.shrines import Shrine
from potsugami.steps import StepsWay


def _shrine(key, lat, lon, name, tags=None):
    t = {"amenity": "place_of_worship", "religion": "shinto", "name": name}
    t.update(tags or {})
    return Shrine(key=key, lat=lat, lon=lon, name=name, tags=t)


def _world():
    # ポツ神 (建物なし) / 村の鎮守 (建物 36 戸) / 有名だが孤立 (wikipedia タグ)
    potsu = _shrine("node/1", 35.30, 140.30, "ポツ神社")
    village = _shrine("node/2", 35.00, 140.00, "村祭神社")
    famous = _shrine("node/3", 35.50, 140.50, "須佐之男</script>神社")
    buildings = [
        (35.00 + dy * 0.0008, 140.00 + dx * 0.0008)
        for dx in range(-3, 3) for dy in range(-3, 3)
    ]
    return [potsu, village, famous], buildings


def test_ranking_order_and_ranks():
    shrines, buildings = _world()
    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(), log=lambda m: None
    )
    cands = result.candidates
    assert [c.rank for c in cands] == [1, 2, 3]
    names = [c.shrine.name for c in cands]
    assert names[-1] == "村祭神社"           # 集落の中は最下位
    assert cands[0].final_score == 100.0
    assert cands[-1].final_score < 40


def test_fame_penalty_default_on():
    shrines, buildings = _world()
    shrines[0].tags["wikipedia"] = "ja:ポツ神社"
    default = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(), log=lambda m: None
    )
    off = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(),
        apply_fame_penalty=False, log=lambda m: None,
    )
    c_def = next(c for c in default.candidates if c.shrine.key == "node/1")
    c_off = next(c for c in off.candidates if c.shrine.key == "node/1")
    assert c_off.final_score == c_off.iso.score
    assert abs(c_def.final_score - c_off.iso.score * 0.85) < 0.02


def test_nuisance_multiplier_applied():
    shrines, buildings = _world()
    # ポツ神の 100m 東にメガソーラー
    solar = NuisanceFeature("solar", [(35.30, 140.3011), (35.30, 140.3055)])
    idx = NuisanceIndex([solar], [])
    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(),
        nuisance_index=idx, log=lambda m: None,
    )
    c = next(c for c in result.candidates if c.shrine.key == "node/1")
    assert c.nuisance.mult == config.NuisanceParams().near_mult
    assert c.final_score == round(c.iso.score * c.nuisance.mult, 2)


def test_road_distance_top_n():
    shrines, buildings = _world()
    calls = []

    def fake_roads(subset):
        calls.append([s.key for s in subset])
        return {s.key: 42.0 for s in subset}

    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(),
        road_distance_fn=fake_roads, roads_top=2, log=lambda m: None,
    )
    checked = [c for c in result.candidates if c.road_checked]
    assert len(checked) == 2
    assert all(c.road_dist_m == 42.0 for c in checked)
    assert calls and len(calls[0]) == 2
    # 上位 2 件 (rank 1, 2) だけが対象
    assert {c.rank for c in checked} == {1, 2}


def test_dist_home_km():
    shrines, buildings = _world()
    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(), log=lambda m: None
    )
    for c in result.candidates:
        assert 30 < c.dist_home_km < 120  # 江東区から千葉県内は概ねこの範囲


def test_write_report_files(tmp_path):
    shrines, buildings = _world()
    steps = [StepsWay("way/9", [(35.300, 140.2995), (35.300, 140.2999)],
                      {"step_count": "148"})]
    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(),
        steps_ways=steps, elevation=None, log=lambda m: None,
    )
    out = tmp_path / "rep"
    write_report(result.candidates, out, "テスト", coverage=result.coverage,
                 home=(config.HOME_LAT, config.HOME_LON))

    # CSV
    with (out / "ranking.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert rows[0]["rank"] == "1"
    assert float(rows[0]["score"]) >= float(rows[1]["score"])
    potsu_row = next(r for r in rows if r["name"] == "ポツ神社")
    assert potsu_row["steps_matched"] == "True"
    assert potsu_row["step_count_tag"] == "148"
    assert potsu_row["road_dist_m"] == ""  # 未計算は空欄

    # GeoJSON
    gj = json.loads((out / "shrines.geojson").read_text(encoding="utf-8"))
    assert gj["type"] == "FeatureCollection"
    assert len(gj["features"]) == 3
    props = gj["features"][0]["properties"]
    assert {"score", "iso_score", "nuisance_mult", "fame_mult",
            "link_gsi", "link_gmap", "link_sv", "link_dir"} <= set(props)

    # HTML
    html = (out / "map.html").read_text(encoding="utf-8")
    assert "ポツ神社" in html
    assert "PAYLOAD" in html
    assert "cyberjapandata.gsi.go.jp" in html
    assert "地理院タイル" in html
    assert "openstreetmap.org" in html
    # 名前中の </script> は <\/script> にエスケープされ、素の形では現れない
    assert "須佐之男<\\/script>神社" in html
    assert "須佐之男</script>神社" not in html

    # summary
    txt = (out / "summary.txt").read_text(encoding="utf-8")
    assert "石段データ網羅性" in txt


def test_road_csv_value_for_none(tmp_path):
    shrines, buildings = _world()
    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(),
        road_distance_fn=lambda subset: {s.key: None for s in subset},
        roads_top=10, log=lambda m: None,
    )
    out = tmp_path / "rep"
    write_report(result.candidates, out, "テスト")
    with (out / "ranking.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert all(r["road_dist_m"] == ">500" for r in rows)


def test_deep_link_formats():
    assert link_gsi(35.123456, 140.654321) == \
        "https://maps.gsi.go.jp/#17/35.123456/140.654321/"
    assert "query=35.123456%2C140.654321" in link_gmap(35.123456, 140.654321)
    sv = link_streetview(35.123456, 140.654321)
    assert "map_action=pano" in sv and "viewpoint=35.123456%2C140.654321" in sv
    d = link_directions(35.123456, 140.654321)
    assert "dir/?api=1" in d and "travelmode=driving" in d


def test_html_json_payload_is_parseable(tmp_path):
    shrines, buildings = _world()
    result = build_candidates(
        shrines, StaticProvider(buildings), config.ScoreParams(), log=lambda m: None
    )
    out = tmp_path / "rep"
    write_report(result.candidates, out, "テスト", home=None)
    html = (out / "map.html").read_text(encoding="utf-8")
    start = html.index("const PAYLOAD = ") + len("const PAYLOAD = ")
    end = html.index(";\n", start)
    payload = json.loads(html[start:end].replace("<\\/", "</"))
    assert len(payload["data"]["features"]) == 3
