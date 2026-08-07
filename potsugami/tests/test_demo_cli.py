import csv

from potsugami.cli import main
from potsugami.demo import build_demo_world, run_demo


def test_demo_world_composition():
    shrines, buildings, steps, nuisances, roads = build_demo_world()
    assert len(shrines) == 29
    assert len(buildings) > 100
    assert len(steps) == 6
    assert len(nuisances) == 1
    assert len(roads) == 1


def test_run_demo_outputs(tmp_path):
    out = tmp_path / "demo"
    run_demo(out)
    for name in ("map.html", "ranking.csv", "shrines.geojson", "summary.txt"):
        assert (out / name).is_file(), name

    with (out / "ranking.csv").open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 29
    # 上位は山社 (孤立)、下位は村社 (集落内) になるはず
    assert "山社" in rows[0]["name"]
    assert "村社" in rows[-1]["name"]
    assert float(rows[0]["score"]) > 90
    assert float(rows[-1]["score"]) < 40
    # 石段の合成データ: step_count タグ 148 がどこかに現れる
    assert any(r["step_count_tag"] == "148" for r in rows)
    # 標高差推定が計算されている神社がある
    assert any(r["est_steps_min"] not in ("", None) for r in rows)
    # 有名神社タイプには有名度係数がかかる
    famous = next(r for r in rows if r["name"] == "合成大社")
    assert "wikipedia" in famous["fame_flags"]
    assert float(famous["fame_mult"]) < 1.0
    # ソーラー隣接タイプには騒がしさ減点がかかる
    solar = next(r for r in rows if r["name"] == "合成日照神社")
    assert "solar" in solar["nuisance_flags"]
    assert float(solar["nuisance_mult"]) < 1.0
    assert float(solar["score"]) < float(solar["iso_score"])


def test_cli_demo(tmp_path, capsys):
    assert main(["demo", "--out", str(tmp_path / "d")]) == 0
    assert (tmp_path / "d" / "map.html").is_file()
    assert "候補数" in capsys.readouterr().out


def test_cli_query(capsys):
    assert main(["query", "--pref", "千葉県"]) == 0
    out = capsys.readouterr().out
    assert "JP-12" in out
    assert "highway" in out
    assert "solar" in out


def test_cli_run_default_out_dir():
    from potsugami.cli import build_parser
    args = build_parser().parse_args(["run", "--pref", "千葉県"])
    assert args.out is None
    assert args.pref == ["千葉県"]
    assert args.buildings == "gsi"
    assert args.gsi_source == "optimal"
    assert args.no_fame_penalty is False
    args2 = build_parser().parse_args(
        ["run", "--pref", "千葉県", "--pref", "茨城県"])
    assert args2.pref == ["千葉県", "茨城県"]
