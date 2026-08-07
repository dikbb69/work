"""Mapbox Vector Tile (MVT) の純 Python デコーダ。

地理院ベクトルタイル (experimental_bvmap) の建物レイヤを読むための最小実装。
protobuf ライブラリへの依存を避けるため、ワイヤフォーマットを直接パースする。
仕様: https://github.com/mapbox/vector-tile-spec/tree/master/2.1

対応範囲: Tile > Layer > Feature の全フィールド、POINT/LINESTRING/POLYGON ジオメトリ。
ポリゴンの内外環判定 (巻き方向) は行わず、環のリストとして返す (建物の距離・重心
計算にはそれで十分)。
"""
from __future__ import annotations

from dataclasses import dataclass, field

GEOM_UNKNOWN = 0
GEOM_POINT = 1
GEOM_LINESTRING = 2
GEOM_POLYGON = 3

_WIRE_VARINT = 0
_WIRE_I64 = 1
_WIRE_LEN = 2
_WIRE_I32 = 5


class MvtError(ValueError):
    pass


def _read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        if pos >= len(buf):
            raise MvtError("truncated varint")
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, pos
        shift += 7
        if shift > 63:
            raise MvtError("varint too long")


def _zigzag_decode(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def _iter_fields(buf: bytes):
    """(field_number, wire_type, value) を順に yield する。

    value は varint なら int、length-delimited なら bytes、固定長は bytes。
    """
    pos = 0
    while pos < len(buf):
        key, pos = _read_varint(buf, pos)
        fnum = key >> 3
        wtype = key & 0x7
        if wtype == _WIRE_VARINT:
            val, pos = _read_varint(buf, pos)
        elif wtype == _WIRE_LEN:
            ln, pos = _read_varint(buf, pos)
            if pos + ln > len(buf):
                raise MvtError("truncated length-delimited field")
            val = buf[pos:pos + ln]
            pos += ln
        elif wtype == _WIRE_I64:
            val = buf[pos:pos + 8]
            pos += 8
        elif wtype == _WIRE_I32:
            val = buf[pos:pos + 4]
            pos += 4
        else:
            raise MvtError(f"unsupported wire type {wtype}")
        yield fnum, wtype, val


def _decode_packed_varints(buf: bytes) -> list[int]:
    out = []
    pos = 0
    while pos < len(buf):
        v, pos = _read_varint(buf, pos)
        out.append(v)
    return out


def _decode_value(buf: bytes):
    """Layer.values の Value メッセージ → Python 値。"""
    import struct
    for fnum, wtype, val in _iter_fields(buf):
        if fnum == 1:      # string
            return val.decode("utf-8", errors="replace")
        if fnum == 2:      # float
            return struct.unpack("<f", val)[0]
        if fnum == 3:      # double
            return struct.unpack("<d", val)[0]
        if fnum == 4:      # int64 (varint)
            # 負値は 10 バイト varint (2 の補数)。64bit で解釈し直す。
            return val - (1 << 64) if val >= (1 << 63) else val
        if fnum == 5:      # uint64
            return val
        if fnum == 6:      # sint64 (zigzag)
            return _zigzag_decode(val)
        if fnum == 7:      # bool
            return bool(val)
    return None


def _decode_geometry(cmds: list[int], geom_type: int) -> list[list[tuple[int, int]]]:
    """geometry コマンド列 → パート (点列) のリスト。タイルローカル整数座標。

    POINT: 各点が 1 パート。LINESTRING: 各線が 1 パート。
    POLYGON: 各環が 1 パート (ClosePath で始点を複製して閉じる)。
    """
    parts: list[list[tuple[int, int]]] = []
    cur: list[tuple[int, int]] = []
    x = y = 0
    i = 0
    n = len(cmds)
    while i < n:
        cmd = cmds[i]
        i += 1
        cmd_id = cmd & 0x7
        count = cmd >> 3
        if cmd_id == 1:  # MoveTo
            for _ in range(count):
                if i + 2 > n:
                    raise MvtError("truncated MoveTo params")
                x += _zigzag_decode(cmds[i])
                y += _zigzag_decode(cmds[i + 1])
                i += 2
                if cur:
                    parts.append(cur)
                cur = [(x, y)]
                if geom_type == GEOM_POINT:
                    parts.append(cur)
                    cur = []
        elif cmd_id == 2:  # LineTo
            for _ in range(count):
                if i + 2 > n:
                    raise MvtError("truncated LineTo params")
                x += _zigzag_decode(cmds[i])
                y += _zigzag_decode(cmds[i + 1])
                i += 2
                cur.append((x, y))
        elif cmd_id == 7:  # ClosePath
            for _ in range(count):
                if cur:
                    cur.append(cur[0])
        else:
            raise MvtError(f"unknown geometry command {cmd_id}")
    if cur:
        parts.append(cur)
    return parts


@dataclass
class MvtFeature:
    fid: int | None
    geom_type: int
    tags: dict
    # タイルローカル整数座標のパート列 (extent 基準)
    parts: list[list[tuple[int, int]]] = field(default_factory=list)


@dataclass
class MvtLayer:
    name: str
    extent: int
    features: list[MvtFeature] = field(default_factory=list)


def decode(tile_bytes: bytes) -> dict[str, MvtLayer]:
    """MVT タイル全体をデコードし {レイヤ名: MvtLayer} を返す。"""
    layers: dict[str, MvtLayer] = {}
    for fnum, wtype, val in _iter_fields(tile_bytes):
        if fnum != 3 or wtype != _WIRE_LEN:
            continue
        layer = _decode_layer(val)
        layers[layer.name] = layer
    return layers


def _decode_layer(buf: bytes) -> MvtLayer:
    name = ""
    extent = 4096
    keys: list[str] = []
    values: list = []
    feature_bufs: list[bytes] = []
    for fnum, wtype, val in _iter_fields(buf):
        if fnum == 1:
            name = val.decode("utf-8", errors="replace")
        elif fnum == 2:
            feature_bufs.append(val)
        elif fnum == 3:
            keys.append(val.decode("utf-8", errors="replace"))
        elif fnum == 4:
            values.append(_decode_value(val))
        elif fnum == 5:
            extent = val
    layer = MvtLayer(name=name, extent=extent)
    for fbuf in feature_bufs:
        layer.features.append(_decode_feature(fbuf, keys, values))
    return layer


def _decode_feature(buf: bytes, keys: list[str], values: list) -> MvtFeature:
    fid: int | None = None
    geom_type = GEOM_UNKNOWN
    tag_idx: list[int] = []
    geom_cmds: list[int] = []
    for fnum, wtype, val in _iter_fields(buf):
        if fnum == 1:
            fid = val
        elif fnum == 2:
            if wtype == _WIRE_LEN:
                tag_idx.extend(_decode_packed_varints(val))
            else:
                tag_idx.append(val)
        elif fnum == 3:
            geom_type = val
        elif fnum == 4:
            if wtype == _WIRE_LEN:
                geom_cmds.extend(_decode_packed_varints(val))
            else:
                geom_cmds.append(val)
    tags = {}
    for k_i, v_i in zip(tag_idx[0::2], tag_idx[1::2]):
        if k_i < len(keys) and v_i < len(values):
            tags[keys[k_i]] = values[v_i]
    parts = _decode_geometry(geom_cmds, geom_type)
    return MvtFeature(fid=fid, geom_type=geom_type, tags=tags, parts=parts)
