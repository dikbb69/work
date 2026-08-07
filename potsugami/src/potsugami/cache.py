"""ディスクキャッシュ。

外部 API (Overpass, 地理院タイル) の応答をそのまま保存し、再実行を無料にする。
404 などの「存在しない」結果もマーカーとして記録し、再問い合わせを避ける。
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

_SAFE = re.compile(r"[^A-Za-z0-9._/-]")


class DiskCache:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        key = _SAFE.sub("_", key)
        if ".." in key.split("/"):
            raise ValueError(f"invalid cache key: {key}")
        return self.root / key

    def get(self, key: str) -> bytes | None:
        p = self._path(key)
        if p.is_file():
            return p.read_bytes()
        return None

    def put(self, key: str, data: bytes) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(p)

    def has_miss(self, key: str) -> bool:
        return self._path(key + ".miss").is_file()

    def put_miss(self, key: str) -> None:
        self.put(key + ".miss", b"")


def query_key(prefix: str, text: str) -> str:
    """クエリ文字列からキャッシュキーを作る。"""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}/{h}"
