import json

import pytest

from potsugami.cache import DiskCache
from potsugami.overpass import OverpassClient, OverpassError


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("potsugami.overpass.time.sleep", lambda s: None)


def _client(tmp_path, transport, **kw):
    return OverpassClient(
        DiskCache(tmp_path / "cache"),
        endpoints=["https://a.example/api", "https://b.example/api"],
        min_interval_s=0.0,
        transport=transport,
        log=lambda m: None,
        **kw,
    )


def test_query_success_and_cache(tmp_path):
    calls = []

    def transport(endpoint, ql):
        calls.append(endpoint)
        return 200, json.dumps({"elements": [1, 2]}).encode()

    c = _client(tmp_path, transport)
    assert c.query("QL1")["elements"] == [1, 2]
    assert c.query("QL1")["elements"] == [1, 2]  # 2 回目はキャッシュ
    assert len(calls) == 1


def test_retry_on_429_switches_endpoint(tmp_path):
    calls = []

    def transport(endpoint, ql):
        calls.append(endpoint)
        if len(calls) == 1:
            return 429, b""
        return 200, b'{"elements": []}'

    c = _client(tmp_path, transport)
    assert c.query("QL")["elements"] == []
    assert calls[0] != calls[1]


def test_truncated_remark_is_retried(tmp_path):
    calls = []

    def transport(endpoint, ql):
        calls.append(endpoint)
        if len(calls) == 1:
            return 200, json.dumps(
                {"remark": "runtime error: Query timed out", "elements": []}
            ).encode()
        return 200, b'{"elements": [1]}'

    c = _client(tmp_path, transport)
    assert c.query("QL")["elements"] == [1]
    assert len(calls) == 2


def test_transport_exception_is_retried(tmp_path):
    calls = []

    def transport(endpoint, ql):
        calls.append(endpoint)
        if len(calls) == 1:
            raise OSError("connection reset")
        return 200, b'{"elements": []}'

    c = _client(tmp_path, transport)
    assert c.query("QL")["elements"] == []


def test_hard_error_raises(tmp_path):
    def transport(endpoint, ql):
        return 400, b"parse error"

    with pytest.raises(OverpassError, match="400"):
        _client(tmp_path, transport).query("bad QL")


def test_all_attempts_fail(tmp_path):
    def transport(endpoint, ql):
        return 503, b""

    with pytest.raises(OverpassError, match="all attempts failed"):
        _client(tmp_path, transport, max_attempts=2).query("QL")


def test_different_queries_have_different_cache_keys(tmp_path):
    def transport(endpoint, ql):
        return 200, json.dumps({"q": ql}).encode()

    c = _client(tmp_path, transport)
    assert c.query("A")["q"] == "A"
    assert c.query("B")["q"] == "B"
