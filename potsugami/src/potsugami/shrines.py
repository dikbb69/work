"""神社リストの取得 (Overpass) と重複排除。

クエリの方針:
- 本命: amenity=place_of_worship + religion=shinto
- 補完: building=shrine (社殿だけがマップされている小社を拾う)
- 補完: religion 未記入だが名前が神社系の place_of_worship
- historic=wayside_shrine (路傍の祠) はデフォルト除外、--include-hokora で追加

同一の神社が node と way (境内・社殿ポリゴン) の両方で登録されていることが多いため、
近接クラスタ (既定 60m) で重複排除する。代表要素は
  amenity=place_of_worship かつ religion=shinto > 名前あり > その他
の優先順で選ぶ。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .geo import GridIndex, haversine_m
from .config import pref_iso
from .overpass import OverpassClient

DEDUPE_RADIUS_M = 60.0

# 名前ベースの補完で使う正規表現 (Overpass 側で評価される)
_NAME_REGEX = "神社$|神宮$|大社$|八幡宮$|天満宮$|稲荷$|東照宮$|権現$"


@dataclass
class Shrine:
    key: str                 # "node/123" など OSM 要素 ID
    lat: float
    lon: float
    name: str | None
    tags: dict = field(default_factory=dict)
    merged_keys: list[str] = field(default_factory=list)  # 統合された重複要素
    # 統合された要素 (building=shrine の社殿ポリゴン等) の座標。
    # 建物プロバイダが境内建物を幾何学的に除外するのに使う。
    precinct_points: list[tuple[float, float]] = field(default_factory=list)

    @property
    def is_hokora(self) -> bool:
        return self.tags.get("historic") == "wayside_shrine"

    @property
    def display_name(self) -> str:
        return self.name or "(名称未登録)"

    @property
    def osm_url(self) -> str:
        return f"https://www.openstreetmap.org/{self.key}"


def build_query(pref: str, include_hokora: bool = False, timeout_s: int = 300) -> str:
    iso = pref_iso(pref)
    parts = [
        f'nwr["amenity"="place_of_worship"]["religion"="shinto"](area.pref);',
        f'nwr["building"="shrine"](area.pref);',
        f'nwr["amenity"="place_of_worship"][!"religion"]["name"~"{_NAME_REGEX}"](area.pref);',
    ]
    if include_hokora:
        parts.append('nwr["historic"="wayside_shrine"](area.pref);')
    body = "\n  ".join(parts)
    return (
        f"[out:json][timeout:{timeout_s}];\n"
        f'area["ISO3166-2"="{iso}"]["admin_level"="4"]->.pref;\n'
        f"(\n  {body}\n);\n"
        "out tags center;\n"
    )


def parse_elements(data: dict) -> list[Shrine]:
    """Overpass JSON → Shrine リスト (重複排除前)。座標のない要素は捨てる。"""
    out: list[Shrine] = []
    for el in data.get("elements", []):
        etype = el.get("type")
        eid = el.get("id")
        if etype == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:
            c = el.get("center") or {}
            lat, lon = c.get("lat"), c.get("lon")
        if lat is None or lon is None or eid is None:
            continue
        tags = el.get("tags", {}) or {}
        out.append(
            Shrine(
                key=f"{etype}/{eid}",
                lat=float(lat),
                lon=float(lon),
                name=tags.get("name"),
                tags=tags,
            )
        )
    return out


def _priority(s: Shrine) -> tuple:
    """重複クラスタ内で代表を選ぶ優先度 (小さいほど優先)。"""
    is_pow_shinto = (
        s.tags.get("amenity") == "place_of_worship"
        and s.tags.get("religion") == "shinto"
    )
    is_pow = s.tags.get("amenity") == "place_of_worship"
    has_name = s.name is not None
    # way/relation (境内ポリゴン) の中心は node より位置代表性が高いことが多いが、
    # 逆のケースもあるので同率とし、タグの充実度で決める。
    return (
        0 if is_pow_shinto else 1,
        0 if is_pow else 1,
        0 if has_name else 1,
        -len(s.tags),
    )


def _names_compatible(a: str | None, b: str | None) -> bool:
    """統合してよい名前の組か。両方に異なる名前が付いていたら別の神社とみなす。

    「諏訪神社」と「諏訪神社 拝殿」のような包含関係は同一神社として扱う。
    """
    if a is None or b is None:
        return True
    if a == b:
        return True
    return a in b or b in a


def dedupe(shrines: list[Shrine], radius_m: float = DEDUPE_RADIUS_M) -> list[Shrine]:
    """近接クラスタで重複排除。優先度順に走査し、既採用と radius_m 以内かつ
    名前が矛盾しない要素を統合する。統合された要素の座標は precinct_points に
    残し、境内建物の除外に使う。"""
    ordered = sorted(shrines, key=_priority)
    accepted: list[Shrine] = []
    index = GridIndex(cell_deg=max(radius_m / 111_320.0 * 2, 0.001))
    for s in ordered:
        rep: Shrine | None = None
        for a_lat, a_lon, obj in index.near(s.lat, s.lon, radius_m):
            cand: Shrine = obj  # type: ignore[assignment]
            if (
                haversine_m(s.lat, s.lon, a_lat, a_lon) <= radius_m
                and _names_compatible(cand.name, s.name)
            ):
                rep = cand
                break
        if rep is None:
            accepted.append(s)
            index.insert(s.lat, s.lon, s)
        else:
            rep.merged_keys.append(s.key)
            rep.precinct_points.append((s.lat, s.lon))
            if rep.name is None and s.name is not None:
                rep.name = s.name
            for k, v in s.tags.items():
                rep.tags.setdefault(k, v)
    return accepted


def fetch_shrines(
    client: OverpassClient, pref: str, include_hokora: bool = False
) -> list[Shrine]:
    ql = build_query(pref, include_hokora=include_hokora)
    data = client.query(ql)
    return dedupe(parse_elements(data))
