from potsugami.fame import fame_signals


def test_no_tags_no_penalty():
    r = fame_signals({"amenity": "place_of_worship", "religion": "shinto"})
    assert r.multiplier == 1.0
    assert r.flags == []
    assert r.penalty_pct == 0


def test_wikipedia_variants():
    assert "wikipedia" in fame_signals({"wikipedia": "ja:X"}).flags
    assert "wikipedia" in fame_signals({"wikipedia:ja": "X"}).flags
    assert fame_signals({"wikipedia": "ja:X"}).multiplier == 0.85


def test_combined_and_clamped():
    tags = {
        "wikipedia": "ja:X", "wikidata": "Q1", "tourism": "attraction",
        "heritage": "2", "website": "https://example.jp",
    }
    r = fame_signals(tags)
    assert set(r.flags) == {"wikipedia", "wikidata", "tourism", "heritage", "website"}
    # 0.85*0.90*0.85*0.90*0.95 = 0.5559... → 下限 0.5 より上
    assert 0.5 <= r.multiplier < 0.6


def test_multiplier_floor():
    # 下限 0.5 を割らない (将来シグナルが増えても)
    tags = {"wikipedia": "x", "wikidata": "x", "tourism": "x",
            "heritage": "x", "website": "x"}
    assert fame_signals(tags).multiplier >= 0.5


def test_website_variants():
    r = fame_signals({"contact:website": "x"})
    assert r.flags == ["website"]
    assert r.multiplier == 0.95
