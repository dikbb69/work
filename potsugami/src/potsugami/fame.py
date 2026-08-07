"""有名度シグナル (未観光地化度の代理指標)。

OSM タグから「観光地化・有名である気配」を拾い、弱い乗算係数にする。
建物的に孤立していても観光客が絶えない著名な奥宮・パワースポットが
最上位を汚染するのを防ぐため、既定でランキングに適用する
(--no-fame-penalty で表示のみにできる)。

係数は控えめ (シグナル 1 つで ×0.85) に設定してある。OSM のタグ付与率は
低く「シグナルなし = 無名の証拠」ではないため、強い減点は誤爆が痛い。
"""
from __future__ import annotations

from dataclasses import dataclass

# シグナル → 係数。乗算で合成する。
_SIGNAL_MULTS = {
    "wikipedia": 0.85,
    "wikidata": 0.90,
    "tourism": 0.85,
    "heritage": 0.90,
    "website": 0.95,
}
_MIN_MULT = 0.5


@dataclass
class FameResult:
    multiplier: float     # 0.5..1.0。小さいほど「有名の気配」
    flags: list[str]

    @property
    def penalty_pct(self) -> int:
        """表示用: 減点率 (%)。"""
        return round((1.0 - self.multiplier) * 100)


def fame_signals(tags: dict) -> FameResult:
    flags: list[str] = []
    if any(k == "wikipedia" or k.startswith("wikipedia:") for k in tags):
        flags.append("wikipedia")
    if "wikidata" in tags:
        flags.append("wikidata")
    if any(k == "tourism" or k.startswith("tourism:") for k in tags):
        flags.append("tourism")
    if any(k == "heritage" or k.startswith("heritage:") for k in tags):
        flags.append("heritage")
    if any(k in ("website", "contact:website", "url") for k in tags):
        flags.append("website")

    mult = 1.0
    for f in flags:
        mult *= _SIGNAL_MULTS[f]
    return FameResult(multiplier=round(max(mult, _MIN_MULT), 4), flags=flags)
