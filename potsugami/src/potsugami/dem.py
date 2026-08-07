"""地理院 標高タイル (PNG) による標高取得。

標高タイルの色 → 標高の変換仕様 (地理院の定義):
  x = 2^16 * R + 2^8 * G + B
  x <  2^23 : h = x * 0.01 [m]
  x == 2^23 : 無効値 (欠測)
  x >  2^23 : h = (x - 2^24) * 0.01 [m]  (負の標高)

dem5a (5m レーザ) → dem5b (5m 写真) → dem (10m 全国) の順でフォールバックする。
"""
from __future__ import annotations

import io
from typing import Protocol

from . import config
from .geo import lonlat_to_tile_frac
from .tiles import TileFetcher

_INVALID = 1 << 23
_TWO24 = 1 << 24


def decode_dem_pixel(r: int, g: int, b: int) -> float | None:
    """標高タイルの 1 ピクセル (RGB) → 標高 (m)。欠測は None。"""
    x = (r << 16) | (g << 8) | b
    if x == _INVALID:
        return None
    if x > _INVALID:
        return (x - _TWO24) * 0.01
    return x * 0.01


class ElevationProvider(Protocol):
    def elevation(self, lat: float, lon: float) -> float | None: ...

    def elevation_ex(self, lat: float, lon: float) -> tuple[float | None, str | None]:
        """(標高, ソース名)。ソース名は精度フラグ判定に使う。"""
        ...


class GsiDemProvider:
    """地理院標高タイルから任意地点の標高を返す。デコード済みタイルはメモリにも保持。"""

    def __init__(self, fetcher: TileFetcher, sources=config.GSI_DEM_SOURCES):
        self.fetcher = fetcher
        self.sources = sources
        self._decoded: dict[tuple[str, int, int, int], object] = {}
        self._decoded_order: list[tuple[str, int, int, int]] = []
        self._max_decoded = 256

    def _tile_pixels(self, kind: str, z: int, x: int, y: int):
        key = (kind, z, x, y)
        if key in self._decoded:
            return self._decoded[key]
        data = self.fetcher.fetch(
            config.GSI_TILE_BASE + "/" + kind + "/{z}/{x}/{y}.png", z, x, y, kind
        )
        px = None
        if data is not None:
            from PIL import Image
            try:
                img = Image.open(io.BytesIO(data)).convert("RGB")
                px = img.load()
            except Exception:
                px = None
        self._decoded[key] = px
        self._decoded_order.append(key)
        if len(self._decoded_order) > self._max_decoded:
            old = self._decoded_order.pop(0)
            self._decoded.pop(old, None)
        return px

    def elevation_ex(self, lat: float, lon: float) -> tuple[float | None, str | None]:
        for kind, z in self.sources:
            fx, fy = lonlat_to_tile_frac(lon, lat, z)
            tx, ty = int(fx), int(fy)
            px = self._tile_pixels(kind, z, tx, ty)
            if px is None:
                continue
            # タイルは 256x256 px
            ix = min(int((fx - tx) * 256), 255)
            iy = min(int((fy - ty) * 256), 255)
            r, g, b = px[ix, iy][:3]
            h = decode_dem_pixel(r, g, b)
            if h is not None:
                return h, kind
        return None, None

    def elevation(self, lat: float, lon: float) -> float | None:
        return self.elevation_ex(lat, lon)[0]


class NullElevationProvider:
    """標高を返さないダミー (オフラインデモ・--no-dem 用)。"""

    def elevation(self, lat: float, lon: float) -> float | None:
        return None

    def elevation_ex(self, lat: float, lon: float) -> tuple[float | None, str | None]:
        return None, None
