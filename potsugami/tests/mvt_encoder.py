"""テスト用の最小 MVT エンコーダ。

デコーダ (potsugami.mvt) の逆操作を独立に実装し、ラウンドトリップで検証する。
"""
from __future__ import annotations


def encode_varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def zigzag(n: int) -> int:
    return (n << 1) ^ (n >> 63) if n < 0 else n << 1


def field_varint(fnum: int, value: int) -> bytes:
    return encode_varint((fnum << 3) | 0) + encode_varint(value)


def field_bytes(fnum: int, value: bytes) -> bytes:
    return encode_varint((fnum << 3) | 2) + encode_varint(len(value)) + value


def field_str(fnum: int, value: str) -> bytes:
    return field_bytes(fnum, value.encode("utf-8"))


def encode_value(v) -> bytes:
    """Layer.values の Value メッセージ。"""
    if isinstance(v, bool):
        return field_varint(7, int(v))
    if isinstance(v, str):
        return field_str(1, v)
    if isinstance(v, int):
        if v >= 0:
            return field_varint(5, v)  # uint64
        return field_varint(6, zigzag(v))  # sint64
    if isinstance(v, float):
        import struct
        return encode_varint((3 << 3) | 1) + struct.pack("<d", v)
    raise TypeError(type(v))


def geometry_commands(parts: list[list[tuple[int, int]]], geom_type: int) -> list[int]:
    """パート列 → geometry コマンド列。POLYGON はリングを閉じずに渡すこと。"""
    cmds: list[int] = []
    x = y = 0
    if geom_type == 1:  # POINT
        pts = [pt for part in parts for pt in part]
        cmds.append((len(pts) << 3) | 1)
        for px, py in pts:
            cmds += [zigzag(px - x), zigzag(py - y)]
            x, y = px, py
        return cmds
    for part in parts:
        cmds.append((1 << 3) | 1)  # MoveTo x1
        px, py = part[0]
        cmds += [zigzag(px - x), zigzag(py - y)]
        x, y = px, py
        rest = part[1:]
        cmds.append((len(rest) << 3) | 2)  # LineTo
        for px, py in rest:
            cmds += [zigzag(px - x), zigzag(py - y)]
            x, y = px, py
        if geom_type == 3:
            cmds.append((1 << 3) | 7)  # ClosePath
    return cmds


def encode_feature(
    fid: int | None,
    geom_type: int,
    parts: list[list[tuple[int, int]]],
    tag_indices: list[int],
) -> bytes:
    body = b""
    if fid is not None:
        body += field_varint(1, fid)
    if tag_indices:
        packed = b"".join(encode_varint(t) for t in tag_indices)
        body += field_bytes(2, packed)
    body += field_varint(3, geom_type)
    cmds = geometry_commands(parts, geom_type)
    body += field_bytes(4, b"".join(encode_varint(c) for c in cmds))
    return body


def encode_layer(
    name: str,
    features: list[bytes],
    keys: list[str],
    values: list,
    extent: int = 4096,
) -> bytes:
    body = field_varint(15, 2)  # version
    body += field_str(1, name)
    for f in features:
        body += field_bytes(2, f)
    for k in keys:
        body += field_str(3, k)
    for v in values:
        body += field_bytes(4, encode_value(v))
    body += field_varint(5, extent)
    return body


def encode_tile(layers: list[bytes]) -> bytes:
    return b"".join(field_bytes(3, layer) for layer in layers)
