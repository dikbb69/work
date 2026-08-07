"""結果の出力: CSV / GeoJSON / 単一ファイル HTML 地図。

HTML 地図は Leaflet (CDN) + 地理院タイル/OSM タイル。ネット接続がある環境の
ブラウザで開く前提の、依存ファイルなしの 1 ファイル。
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from .fame import FameResult
from .isolation import IsolationResult
from .nuisance import NuisanceResult
from .shrines import Shrine
from .steps import ShrineSteps, StepsCoverage


@dataclass
class Candidate:
    shrine: Shrine
    iso: IsolationResult
    fame: FameResult
    steps: ShrineSteps | None
    dist_home_km: float
    final_score: float
    nuisance: NuisanceResult = field(default_factory=NuisanceResult)
    rank: int = 0
    road_checked: bool = False           # 最寄り車道距離を計算したか (上位 N 社のみ)
    road_dist_m: float | None = None     # 計算済みで None なら「半径内に車道なし」


def link_gsi(lat: float, lon: float, zoom: int = 17) -> str:
    return f"https://maps.gsi.go.jp/#{zoom}/{lat:.6f}/{lon:.6f}/"


def link_gmap(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={lat:.6f}%2C{lon:.6f}"


def link_streetview(lat: float, lon: float) -> str:
    return (
        "https://www.google.com/maps/@?api=1&map_action=pano"
        f"&viewpoint={lat:.6f}%2C{lon:.6f}"
    )


def link_directions(lat: float, lon: float) -> str:
    """車での経路。スマホで開けばそのままカーナビになる、実質最重要リンク。"""
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&destination={lat:.6f}%2C{lon:.6f}&travelmode=driving"
    )


def _candidate_props(c: Candidate) -> dict:
    s = c.steps
    return {
        "rank": c.rank,
        "name": c.shrine.display_name,
        "score": c.final_score,
        "iso_score": c.iso.score,
        "p_sum": c.iso.p_sum,
        "d_nearest_m": c.iso.d_nearest_m,
        "n_adjacent": c.iso.n_adjacent,
        "n_inner": c.iso.n_inner,
        "n_outer": c.iso.n_outer,
        "nuisance_mult": c.nuisance.mult,
        "nuisance_flags": ";".join(c.nuisance.flags),
        "fame_mult": c.fame.multiplier,
        "fame_flags": ";".join(c.fame.flags),
        "steps_matched": bool(s.matched) if s else False,
        "steps_match_dist_m": s.match_dist_m if s else None,
        "steps_total_length_m": s.total_length_m if s and s.matched else None,
        "steps_elev_diff_m": s.elev_diff_m if s else None,
        "elev_low_precision": s.elev_low_precision if s else False,
        "est_steps_min": s.est_steps_min if s else None,
        "est_steps_max": s.est_steps_max if s else None,
        "step_count_tag": s.step_count_tagged if s else None,
        "road_checked": c.road_checked,
        "road_dist_m": c.road_dist_m,
        "hokora": c.shrine.is_hokora,
        "dist_home_km": round(c.dist_home_km, 1),
        "lat": round(c.shrine.lat, 6),
        "lon": round(c.shrine.lon, 6),
        "osm": c.shrine.key,
        "osm_url": c.shrine.osm_url,
        "link_gsi": link_gsi(c.shrine.lat, c.shrine.lon),
        "link_gmap": link_gmap(c.shrine.lat, c.shrine.lon),
        "link_sv": link_streetview(c.shrine.lat, c.shrine.lon),
        "link_dir": link_directions(c.shrine.lat, c.shrine.lon),
    }


_CSV_COLUMNS = [
    "rank", "name", "score", "iso_score", "p_sum",
    "d_nearest_m", "n_adjacent", "n_inner", "n_outer",
    "nuisance_mult", "nuisance_flags", "fame_mult", "fame_flags",
    "steps_matched", "steps_match_dist_m", "steps_total_length_m",
    "steps_elev_diff_m", "elev_low_precision",
    "est_steps_min", "est_steps_max", "step_count_tag",
    "road_dist_m", "hokora",
    "dist_home_km", "lat", "lon", "osm", "osm_url",
    "link_gsi", "link_gmap", "link_sv", "link_dir",
]


def write_csv(cands: Sequence[Candidate], path: Path) -> None:
    # utf-8-sig: Excel (日本語環境) でそのまま開けるように
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=_CSV_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for c in cands:
            row = _candidate_props(c)
            # 未計算 ("") と「半径内に車道なし」(">500") を区別する
            if not c.road_checked:
                row["road_dist_m"] = ""
            elif c.road_dist_m is None:
                row["road_dist_m"] = ">500"
            w.writerow(row)


def to_geojson(cands: Sequence[Candidate]) -> dict:
    features = []
    for c in cands:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(c.shrine.lon, 6), round(c.shrine.lat, 6)],
            },
            "properties": _candidate_props(c),
        })
    return {"type": "FeatureCollection", "features": features}


def write_geojson(cands: Sequence[Candidate], path: Path) -> None:
    path.write_text(
        json.dumps(to_geojson(cands), ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def summary_text(
    title: str,
    cands: Sequence[Candidate],
    coverage: StepsCoverage | None,
) -> str:
    lines = [f"# {title}", f"候補数: {len(cands)}"]
    if cands:
        top = cands[0]
        lines.append(
            f"最高スコア: {top.final_score:.1f} ({top.shrine.display_name})"
        )
        hi = sum(1 for c in cands if c.final_score >= 80)
        lines.append(f"スコア 80 以上: {hi} 社")
    if coverage:
        lines += [
            "",
            "## 石段データ網羅性 (OSM highway=steps)",
            f"県内 steps way 総数: {coverage.n_steps_ways}",
            f"石段がマッチした神社: {coverage.n_matched}/{coverage.n_shrines}"
            f" ({coverage.match_rate * 100:.1f}%)",
            f"うち step_count タグあり: {coverage.n_with_count_tag}",
            "",
            "マッチ率が数 % 程度なら、石段フィルタは OSM 単独では網羅性不足。",
            "引き継ぎ書 5 章の DEM ベース (鳥居記号と社殿の標高差) への切替を検討する。",
        ]
    return "\n".join(lines) + "\n"


def write_report(
    cands: Sequence[Candidate],
    out_dir: Path,
    title: str,
    coverage: StepsCoverage | None = None,
    home: tuple[float, float] | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(cands, out_dir / "ranking.csv")
    write_geojson(cands, out_dir / "shrines.geojson")
    (out_dir / "map.html").write_text(
        render_map_html(cands, title, coverage, home), encoding="utf-8"
    )
    (out_dir / "summary.txt").write_text(
        summary_text(title, cands, coverage), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# HTML 地図
# ---------------------------------------------------------------------------

def _load_template() -> str:
    from importlib import resources

    return (
        resources.files("potsugami")
        .joinpath("map_template.html")
        .read_text(encoding="utf-8")
    )


def render_map_html(
    cands: Sequence[Candidate],
    title: str,
    coverage: StepsCoverage | None = None,
    home: tuple[float, float] | None = None,
) -> str:
    data = to_geojson(cands)
    cov = None
    if coverage:
        cov = {
            "n_steps_ways": coverage.n_steps_ways,
            "n_matched": coverage.n_matched,
            "n_shrines": coverage.n_shrines,
            "match_rate": round(coverage.match_rate * 100, 1),
        }
    payload = json.dumps(
        {"title": title, "data": data, "coverage": cov, "home": home},
        ensure_ascii=False,
    ).replace("</", "<\\/")
    return _load_template().replace("__PAYLOAD__", payload).replace("__TITLE__", title)


