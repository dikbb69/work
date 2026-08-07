"""ポツ神ファインダー CLI。

使い方:
  potsugami run --pref 千葉県 --out out/chiba
  potsugami run --pref 千葉県 --pref 茨城県          # 複数県を 1 枚の地図に
  potsugami demo --out out/demo
  potsugami query --pref 千葉県        # 発行する Overpass クエリを表示して終了
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import config


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _parse_params(kvs: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for kv in kvs:
        if "=" not in kv:
            raise SystemExit(f"--param は key=value 形式で指定してください: {kv!r}")
        k, v = kv.split("=", 1)
        out[k.strip()] = float(v)
    return out


def cmd_run(args: argparse.Namespace) -> int:
    from .buildings import make_provider
    from .cache import DiskCache
    from .dem import GsiDemProvider, NullElevationProvider
    from .nuisance import fetch_nuisance_index
    from .overpass import OverpassClient
    from .pipeline import build_candidates
    from .report import write_report
    from .roads import nearest_road_distances
    from .shrines import dedupe, fetch_shrines
    from .steps import fetch_steps
    from .tiles import TileFetcher

    prefs: list[str] = args.pref
    score_params = config.ScoreParams().override(_parse_params(args.param))
    cache = DiskCache(args.cache_dir)
    overpass = OverpassClient(cache, log=_log)
    tile_fetcher = TileFetcher(cache, log=_log)

    shrines = []
    for pref in prefs:
        _log(f"[shrines] {pref} の神社を Overpass から取得中…")
        shrines.extend(
            fetch_shrines(overpass, pref, include_hokora=args.include_hokora)
        )
    if len(prefs) > 1:
        shrines = dedupe(shrines)  # 県境の重複を統合
    _log(f"[shrines] 重複排除後 {len(shrines)} 社")
    if not shrines:
        _log("[shrines] 神社が 0 件です。県名を確認してください。")
        return 1
    if args.limit:
        shrines = shrines[: args.limit]
        _log(f"[shrines] --limit により先頭 {len(shrines)} 社に制限")

    steps_ways = None
    elevation = None
    if not args.no_steps:
        steps_ways = []
        for pref in prefs:
            _log(f"[steps] {pref} の highway=steps を取得中…")
            steps_ways.extend(fetch_steps(overpass, pref))
        _log(f"[steps] {len(steps_ways)} 本")
        elevation = (
            NullElevationProvider() if args.no_dem else GsiDemProvider(tile_fetcher)
        )

    nuisance_index = None
    if not args.no_nuisance:
        _log("[nuisance] メガソーラー・工場・幹線道路などを取得中…")
        nuisance_index = fetch_nuisance_index(overpass, prefs)

    provider = make_provider(
        args.buildings,
        tile_fetcher=tile_fetcher,
        overpass=overpass,
        gsi_source=args.gsi_source,
    )
    road_fn = None
    if not args.no_roads:
        road_fn = lambda subset: nearest_road_distances(overpass, subset)  # noqa: E731

    result = build_candidates(
        shrines,
        provider,
        score_params,
        steps_ways=steps_ways,
        elevation=elevation,
        steps_params=config.StepsParams(),
        nuisance_index=nuisance_index,
        apply_fame_penalty=not args.no_fame_penalty,
        road_distance_fn=road_fn,
        roads_top=args.roads_top,
        log=_log,
    )

    out_dir = Path(args.out)
    title = "ポツ神ファインダー v0 — " + "・".join(prefs)
    write_report(
        result.candidates, out_dir, title,
        coverage=result.coverage, home=(config.HOME_LAT, config.HOME_LON),
    )
    _log(f"[report] {out_dir}/map.html, ranking.csv, shrines.geojson, summary.txt")
    print((out_dir / "summary.txt").read_text(encoding="utf-8"))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from .demo import run_demo

    out_dir = Path(args.out)
    run_demo(out_dir)
    _log(f"[demo] {out_dir}/map.html をブラウザで開いてください")
    print((out_dir / "summary.txt").read_text(encoding="utf-8"))
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    from .nuisance import build_major_road_query, build_nuisance_query
    from .shrines import build_query
    from .steps import build_steps_query

    for pref in args.pref:
        print(f"# {pref}: 神社クエリ")
        print(build_query(pref, include_hokora=args.include_hokora))
        print(f"# {pref}: 石段クエリ")
        print(build_steps_query(pref))
        print(f"# {pref}: 迷惑土地利用クエリ")
        print(build_nuisance_query(pref))
        print(f"# {pref}: 幹線道路クエリ")
        print(build_major_road_query(pref))
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="potsugami",
        description="ポツ神ファインダー: 田舎にポツンと佇む無名の小神社を探す",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="県単位でポツ神スコアを計算してレポートを出力")
    run.add_argument("--pref", action="append", required=True,
                     help="都道府県名 (例: 千葉県) または JP-12。複数回指定可")
    run.add_argument("--out", default=None, help="出力ディレクトリ (既定: out/<県名>)")
    run.add_argument("--buildings", choices=["gsi", "osm"], default="gsi",
                     help="建物データソース (既定: gsi = 地理院ベクトルタイル)")
    run.add_argument("--gsi-source", choices=list(config.GSI_BVMAP_SOURCES),
                     default=config.GSI_BVMAP_DEFAULT_SOURCE,
                     help="地理院ベクトルタイルの系統 (既定: optimal)")
    run.add_argument("--cache-dir", default=".potsugami_cache",
                     help="HTTP キャッシュディレクトリ")
    run.add_argument("--include-hokora", action="store_true",
                     help="路傍の祠 (historic=wayside_shrine) も含める")
    run.add_argument("--no-fame-penalty", action="store_true",
                     help="有名度係数をスコアに掛けない (列表示のみにする)")
    run.add_argument("--no-nuisance", action="store_true",
                     help="メガソーラー・工場・幹線道路の減点を行わない")
    run.add_argument("--no-steps", action="store_true", help="石段マッチングを行わない")
    run.add_argument("--no-dem", action="store_true",
                     help="標高タイルを取得しない (石段の標高差推定を省略)")
    run.add_argument("--no-roads", action="store_true",
                     help="最寄り車道距離を取得しない")
    run.add_argument("--roads-top", type=int, default=400,
                     help="最寄り車道距離を付ける上位候補数 (既定: 400)")
    run.add_argument("--limit", type=int, default=None,
                     help="処理する神社数の上限 (お試し実行用)")
    run.add_argument("--param", action="append", default=[],
                     help="スコアパラメータ上書き (例: --param tau_m=200)。複数可")
    run.set_defaults(func=cmd_run)

    demo = sub.add_parser("demo", help="合成データでオフラインデモを実行")
    demo.add_argument("--out", default="out/demo", help="出力ディレクトリ")
    demo.set_defaults(func=cmd_demo)

    q = sub.add_parser("query", help="発行する Overpass クエリを表示 (実行はしない)")
    q.add_argument("--pref", action="append", required=True)
    q.add_argument("--include-hokora", action="store_true")
    q.set_defaults(func=cmd_query)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "cmd", None) == "run" and args.out is None:
        args.out = "out/" + "+".join(args.pref)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
