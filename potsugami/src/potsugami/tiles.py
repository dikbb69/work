"""地理院タイルの取得 (キャッシュ・404 マーカー付き)。"""
from __future__ import annotations

import sys
import time
from typing import Callable

from .cache import DiskCache
from . import config


class TileError(RuntimeError):
    pass


class TileFetcher:
    def __init__(
        self,
        cache: DiskCache,
        min_interval_s: float = 0.05,
        max_attempts: int = 3,
        transport: Callable[[str], tuple[int, bytes]] | None = None,
        log: Callable[[str], None] | None = None,
    ):
        """transport(url) -> (status_code, body) を差し替え可能 (テスト用)。"""
        self.cache = cache
        self.min_interval_s = min_interval_s
        self.max_attempts = max_attempts
        self._transport = transport or self._http_transport
        self._last_request = 0.0
        self._log = log or (lambda m: print(m, file=sys.stderr))

    @staticmethod
    def _http_transport(url: str) -> tuple[int, bytes]:
        import requests
        resp = requests.get(url, headers={"User-Agent": config.USER_AGENT}, timeout=60)
        return resp.status_code, resp.content

    def fetch(self, url_template: str, z: int, x: int, y: int, kind: str) -> bytes | None:
        """タイルを取得。存在しないタイル (404) は None。結果はディスクキャッシュされる。"""
        n = 1 << z
        if not (0 <= x < n and 0 <= y < n):
            return None
        ext = url_template.rsplit(".", 1)[-1]
        key = f"tiles/{kind}/{z}/{x}/{y}.{ext}"
        if self.cache.has_miss(key):
            return None
        cached = self.cache.get(key)
        if cached is not None:
            return cached

        url = url_template.format(z=z, x=x, y=y)
        last_err = ""
        for attempt in range(self.max_attempts):
            wait = self._last_request + self.min_interval_s - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()
            try:
                status, body = self._transport(url)
            except Exception as e:
                last_err = str(e)
                self._log(f"[tiles] transport error, retrying: {url}: {e}")
                time.sleep(2 ** attempt)
                continue
            if status == 200:
                self.cache.put(key, body)
                return body
            if status in (404, 204):
                self.cache.put_miss(key)
                return None
            if status in (429, 502, 503, 504):
                last_err = f"HTTP {status}"
                time.sleep(2 ** (attempt + 1))
                continue
            raise TileError(f"HTTP {status} for {url}")
        raise TileError(f"failed to fetch {url}: {last_err}")
