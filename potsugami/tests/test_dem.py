import io

from PIL import Image

from potsugami import config
from potsugami.dem import GsiDemProvider, NullElevationProvider, decode_dem_pixel


def _png_filled(r: int, g: int, b: int) -> bytes:
    img = Image.new("RGB", (256, 256), (r, g, b))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _rgb_for_elevation_cm(x: int) -> tuple[int, int, int]:
    return (x >> 16) & 0xFF, (x >> 8) & 0xFF, x & 0xFF


class FakeFetcher:
    """kind → png bytes (None なら 404 相当) を返すダミー。"""

    def __init__(self, tiles: dict):
        self.tiles = tiles
        self.calls: list[tuple[str, int]] = []

    def fetch(self, url_template, z, x, y, kind):
        self.calls.append((kind, z))
        return self.tiles.get(kind)


def test_decode_dem_pixel_positive():
    assert decode_dem_pixel(0, 0, 100) == 1.0
    r, g, b = _rgb_for_elevation_cm(12345)
    assert decode_dem_pixel(r, g, b) == 123.45


def test_decode_dem_pixel_invalid():
    assert decode_dem_pixel(0x80, 0, 0) is None


def test_decode_dem_pixel_negative():
    # x = 2^24 - 100 → -1.00m
    r, g, b = _rgb_for_elevation_cm((1 << 24) - 100)
    assert decode_dem_pixel(r, g, b) == -1.0


def test_provider_reads_first_source():
    r, g, b = _rgb_for_elevation_cm(12345)
    fetcher = FakeFetcher({"dem5a_png": _png_filled(r, g, b)})
    p = GsiDemProvider(fetcher)
    assert p.elevation(35.2, 140.1) == 123.45
    assert fetcher.calls[0][0] == "dem5a_png"


def test_provider_falls_back_when_missing():
    r, g, b = _rgb_for_elevation_cm(500)  # 5.0m
    fetcher = FakeFetcher({"dem_png": _png_filled(r, g, b)})
    p = GsiDemProvider(fetcher)
    assert p.elevation(35.2, 140.1) == 5.0
    kinds = [k for k, _z in fetcher.calls]
    assert kinds == ["dem5a_png", "dem5b_png", "dem5c_png", "dem_png"]


def test_provider_falls_back_on_invalid_pixel():
    invalid = _png_filled(0x80, 0, 0)
    r, g, b = _rgb_for_elevation_cm(2000)  # 20.0m
    fetcher = FakeFetcher({"dem5a_png": invalid, "dem5b_png": _png_filled(r, g, b)})
    p = GsiDemProvider(fetcher)
    assert p.elevation(35.2, 140.1) == 20.0


def test_provider_all_missing():
    p = GsiDemProvider(FakeFetcher({}))
    assert p.elevation(35.2, 140.1) is None


def test_provider_caches_decoded_tiles():
    r, g, b = _rgb_for_elevation_cm(100)
    fetcher = FakeFetcher({"dem5a_png": _png_filled(r, g, b)})
    p = GsiDemProvider(fetcher)
    p.elevation(35.2, 140.1)
    p.elevation(35.2000001, 140.1000001)  # 同じタイル
    assert len(fetcher.calls) == 1


def test_null_provider():
    assert NullElevationProvider().elevation(35.0, 140.0) is None


def test_sources_config_order():
    kinds = [k for k, _z in config.GSI_DEM_SOURCES]
    assert kinds == ["dem5a_png", "dem5b_png", "dem5c_png", "dem_png"]


def test_elevation_ex_reports_source():
    r, g, b = _rgb_for_elevation_cm(500)
    fetcher = FakeFetcher({"dem_png": _png_filled(r, g, b)})
    p = GsiDemProvider(fetcher)
    h, kind = p.elevation_ex(35.2, 140.1)
    assert h == 5.0
    assert kind == "dem_png"
    assert kind in config.DEM_LOW_PRECISION_KINDS
