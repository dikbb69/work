import math

import pytest

from potsugami.config import ScoreParams
from potsugami.isolation import BuildingObs, building_weight, isolation_score


P = ScoreParams()


def _obs(*dists, area=None, roofless=False):
    return [BuildingObs(dist_m=d, area_m2=area, roofless=roofless) for d in dists]


def test_no_buildings_is_perfect_score():
    r = isolation_score([], P)
    assert r.score == 100.0
    assert r.d_nearest_m is None
    assert r.p_sum == 0.0


def test_self_exclusion_ignores_precinct_buildings():
    # 社殿 (10m)・社務所 (25m) だけ → スコアは満点、ただし n_adjacent に記録
    r = isolation_score(_obs(10.0, 25.0), P)
    assert r.score == 100.0
    assert r.d_nearest_m is None
    assert r.n_adjacent == 2


def test_dense_village_scores_low():
    dists = [50 + i * 8 for i in range(30)]  # 50〜282m に 30 戸
    r = isolation_score(_obs(*dists), P)
    assert r.score < 10
    assert r.n_inner > 0


def test_design_review_reference_cases():
    """スコア式レビューの検算ケース (a_i=1)。

    集落 30 戸 (300m 中心) ≈ 7 点、小屋 1 棟 80m ≈ 77 点、無建物 = 100 点。
    集落鎮守が山中のポツ神を逆転しないこと。
    """
    village = isolation_score(_obs(*[300.0] * 30), P)
    hut = isolation_score(_obs(80.0), P)
    empty = isolation_score([], P)
    assert empty.score == 100.0
    assert 60 < hut.score < 90
    assert village.score < 15
    assert village.score < hut.score < empty.score


def test_adding_building_never_raises_score():
    base = _obs(200.0, 300.0, 450.0)
    r0 = isolation_score(base, P)
    for extra in [45.0, 100.0, 200.0, 350.0, 999.0]:
        r1 = isolation_score(base + _obs(extra), P)
        assert r1.score <= r0.score, f"extra={extra}"


def test_closer_building_scores_lower():
    far = isolation_score(_obs(250.0), P)
    near = isolation_score(_obs(100.0), P)
    assert near.score < far.score


def test_no_saturation_below_search_radius():
    # 旧式は 300m で飽和して同点タイになっていた。カーネル式は順序が残る。
    a = isolation_score(_obs(350.0), P)
    b = isolation_score(_obs(600.0), P)
    assert a.score < b.score < 100.0


def test_larger_building_scores_lower():
    small = isolation_score(_obs(150.0, area=60.0), P)
    big = isolation_score(_obs(150.0, area=5000.0), P)
    assert big.score < small.score


def test_area_weight_capped():
    w = building_weight(BuildingObs(100.0, area_m2=1e6), P)
    assert w == P.area_cap


def test_roofless_weight_reduced_but_not_zero():
    solid = isolation_score(_obs(100.0), P)
    house = isolation_score(_obs(100.0, roofless=False), P)
    greenhouse = isolation_score(_obs(100.0, roofless=True), P)
    assert house.score == solid.score
    # ビニールハウスは減点が軽いが、ゼロではない
    assert solid.score < greenhouse.score < 100.0


def test_ring_display_counts():
    r = isolation_score(_obs(10.0, 45.0, 100.0, 149.9, 150.0, 300.0, 499.0, 600.0), P)
    assert r.n_adjacent == 1
    assert r.n_inner == 3
    assert r.n_outer == 3
    assert r.d_nearest_m == 45.0


def test_param_override():
    p = P.override({"tau_m": 250.0})
    assert p.tau_m == 250.0
    assert p.p_scale == P.p_scale
    with pytest.raises(ValueError):
        P.override({"typo_key": 1.0})


def test_score_bounds():
    cases = [[], _obs(*[41.0] * 200), _obs(999.0), _obs(41.0, 200.0, 480.0, area=1e5)]
    for obs in cases:
        r = isolation_score(list(obs), P)
        assert 0.0 <= r.score <= 100.0


def test_formula_matches_definition():
    obs = _obs(100.0, 300.0)
    r = isolation_score(obs, P)
    p_expected = math.exp(-100 / P.tau_m) + math.exp(-300 / P.tau_m)
    assert abs(r.p_sum - p_expected) < 1e-3
    assert abs(r.score - 100 * math.exp(-p_expected / P.p_scale)) < 0.02
