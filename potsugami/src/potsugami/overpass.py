"""Overpass API クライアント。

- ディスクキャッシュ (クエリ内容の SHA-256 キー) で再実行を無料化
- ミラー 2 系統フォールバック、429/504 はバックオフ付きリトライ
- リクエスト間に最小インターバルを置く (公共インスタンスへの配慮)
"""
from __future__ import annotations

import json
import sys
import time
from typing import Callable

from .cache import DiskCache, query_key
from . import config


class OverpassError(RuntimeError):
    pass


class OverpassClient:
    def __init__(
        self,
        cache: DiskCache,
        endpoints: list[str] | None = None,
        min_interval_s: float = 2.0,
        max_attempts: int = 4,
        transport: Callable[[str, str], tuple[int, bytes]] | None = None,
        log: Callable[[str], None] | None = None,
    ):
        """transport(endpoint, ql) -> (status_code, body) を差し替え可能 (テスト用)。"""
        self.cache = cache
        self.endpoints = endpoints or list(config.OVERPASS_ENDPOINTS)
        self.min_interval_s = min_interval_s
        self.max_attempts = max_attempts
        self._transport = transport or self._http_transport
        self._last_request = 0.0
        self._log = log or (lambda m: print(m, file=sys.stderr))

    @staticmethod
    def _http_transport(endpoint: str, ql: str) -> tuple[int, bytes]:
        import requests
        resp = requests.post(
            endpoint,
            data={"data": ql},
            headers={"User-Agent": config.USER_AGENT},
            timeout=360,
        )
        return resp.status_code, resp.content

    def _throttle(self) -> None:
        wait = self._last_request + self.min_interval_s - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def query(self, ql: str) -> dict:
        """Overpass QL を実行し JSON を返す。同一クエリはキャッシュから返す。"""
        key = query_key("overpass", ql) + ".json"
        cached = self.cache.get(key)
        if cached is not None:
            return json.loads(cached)

        last_err: str = ""
        for attempt in range(self.max_attempts):
            endpoint = self.endpoints[attempt % len(self.endpoints)]
            self._throttle()
            try:
                status, body = self._transport(endpoint, ql)
            except Exception as e:  # ネットワーク断など
                last_err = f"{endpoint}: {e}"
                self._log(f"[overpass] transport error, retrying: {last_err}")
                time.sleep(2 ** attempt)
                continue
            if status == 200:
                try:
                    data = json.loads(body)
                except json.JSONDecodeError as e:
                    raise OverpassError(f"invalid JSON from {endpoint}: {e}") from e
                if "remark" in data and "error" in str(data.get("remark", "")).lower():
                    # タイムアウト等で途中打ち切りの応答。信用しない。
                    last_err = f"{endpoint}: remark={data['remark']}"
                    self._log(f"[overpass] truncated result, retrying: {last_err}")
                    time.sleep(2 ** attempt)
                    continue
                self.cache.put(key, body)
                return data
            if status in (429, 502, 503, 504):
                last_err = f"{endpoint}: HTTP {status}"
                backoff = 2 ** (attempt + 2)
                self._log(f"[overpass] HTTP {status}, backing off {backoff}s")
                time.sleep(backoff)
                continue
            raise OverpassError(f"HTTP {status} from {endpoint}: {body[:300]!r}")
        raise OverpassError(f"all attempts failed; last error: {last_err}")
