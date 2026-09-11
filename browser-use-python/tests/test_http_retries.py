"""Exercise retries through real HTTP clients with an in-memory transport."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any

import httpx
import pytest

from browser_use_sdk._core import http
from browser_use_sdk._core.errors import BrowserUseError
from browser_use_sdk.v4.resources.runs import AsyncRuns, Runs

RUN_ID = "00000000-0000-0000-0000-000000000001"
SESSION_ID = "00000000-0000-0000-0000-000000000002"


@contextmanager
def _replay(
    monkeypatch: pytest.MonkeyPatch,
    is_async: bool,
    handler: Callable[[httpx.Request], httpx.Response],
    max_retries: int = 3,
) -> Iterator[tuple[Any, list[float]]]:
    delays: list[float] = []
    monkeypatch.setattr(http, "random", SimpleNamespace(random=lambda: 0.5))
    monkeypatch.setattr(http, "time", SimpleNamespace(time=lambda: 0, sleep=delays.append))
    if is_async:
        async def sleep(delay: float) -> None:
            delays.append(delay)

        async_client = http.AsyncHttpClient("https://api.example.com", "test", max_retries=max_retries)
        asyncio.run(async_client.close())
        async_client._client = httpx.AsyncClient(
            base_url="https://api.example.com", transport=httpx.MockTransport(handler)
        )
        monkeypatch.setattr(http, "asyncio", SimpleNamespace(sleep=sleep))
        try:
            yield async_client, delays
        finally:
            asyncio.run(async_client.close())
    else:
        sync_client = http.SyncHttpClient("https://api.example.com", "test", max_retries=max_retries)
        sync_client.close()
        sync_client._client = httpx.Client(
            base_url="https://api.example.com", transport=httpx.MockTransport(handler)
        )
        try:
            yield sync_client, delays
        finally:
            sync_client.close()


def _request(client: Any, is_async: bool, method: str = "GET") -> Any:
    result = client.request(method, "/resource")
    return asyncio.run(result) if is_async else result


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("status", [502, 503, 504])
def test_transient_get_recovers(monkeypatch: pytest.MonkeyPatch, is_async: bool, status: int) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(status, json={"detail": "temporary"}, headers={"Retry-After": "2"})
        return httpx.Response(200, json={"result": "ready"})

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        assert _request(client, is_async, "get") == {"result": "ready"}
        assert delays == [2.125]
    assert len(requests) == 2


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("method,status", [("GET", 503), ("POST", 429)])
def test_persistent_failure_is_bounded_and_preserves_error(
    monkeypatch: pytest.MonkeyPatch, is_async: bool, method: str, status: int,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, json={"detail": "still unavailable", "reason": "test"})

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        with pytest.raises(BrowserUseError, match="still unavailable") as error:
            _request(client, is_async, method)
        assert error.value.status_code == status
        assert error.value.detail == {"detail": "still unavailable", "reason": "test"}
        assert delays == [1.125, 2.125, 4.125]
    assert len(requests) == 4


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("header,expected", [
    ("5", 5.125),
    ("Thu, 01 Jan 1970 00:00:05 GMT", 5.125),
    ("Thursday, 01-Jan-70 00:00:05 GMT", 5.125),
    ("Thu Jan  1 00:00:05 1970", 5.125),
    ("Thu, 01 Jan 1970 00:00:05", 1.125),
    ("January 1, 1970 00:00:05", 1.125),
    ("Wed, 31 Dec 1969 23:59:59 GMT", 1.125),
    ("0", 1.125),
    ("60", 60),
    ("-1", 1.125),
    ("1.5", 1.125),
    ("NaN", 1.125),
    ("not a date", 1.125),
])
def test_retry_after_and_jitter(
    monkeypatch: pytest.MonkeyPatch, is_async: bool, header: str, expected: float,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(429 if len(requests) == 1 else 200, json={}, headers={"Retry-After": header})

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        assert _request(client, is_async, "POST") == {}
        assert delays == [expected]
    assert len(requests) == 2


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("header", ["61", "9" * 400, "Thu, 01 Jan 1970 00:01:01 GMT"])
def test_long_retry_after_returns_error_without_early_retry(
    monkeypatch: pytest.MonkeyPatch, is_async: bool, header: str,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(429, json={"detail": "wait longer"}, headers={"Retry-After": header})

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        with pytest.raises(BrowserUseError, match="wait longer"):
            _request(client, is_async, "POST")
        assert delays == []
    assert len(requests) == 1


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("header", [None, "0", "1"])
def test_short_retry_after_does_not_extend_backoff_cap(
    monkeypatch: pytest.MonkeyPatch, is_async: bool, header: str | None,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"detail": "busy"}, headers={} if header is None else {"Retry-After": header})

    with _replay(monkeypatch, is_async, handler, max_retries=5) as (client, delays):
        with pytest.raises(BrowserUseError):
            _request(client, is_async)
        assert delays == [1.125, 2.125, 4.125, 8.125, 10.0]


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("status", [429, 503])
def test_zero_retries_sends_once(monkeypatch: pytest.MonkeyPatch, is_async: bool, status: int) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, json={"detail": "no retries"})

    with _replay(monkeypatch, is_async, handler, max_retries=0) as (client, delays):
        with pytest.raises(BrowserUseError, match="no retries"):
            _request(client, is_async)
        assert delays == []
    assert len(requests) == 1


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("method,status", [
    ("POST", 500), ("POST", 502), ("POST", 503), ("POST", 504),
    ("PATCH", 503), ("DELETE", 503), ("GET", 500), ("GET", 401), ("GET", 404),
])
def test_other_errors_are_not_retried(
    monkeypatch: pytest.MonkeyPatch, is_async: bool, method: str, status: int,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status, json={"detail": "unchanged"}, headers={"Retry-After": "2"})

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        with pytest.raises(BrowserUseError, match="unchanged"):
            _request(client, is_async, method)
        assert delays == []
    assert len(requests) == 1


@pytest.mark.parametrize("is_async", [False, True])
def test_ambiguous_post_transport_error_is_not_retried(monkeypatch: pytest.MonkeyPatch, is_async: bool) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ReadTimeout("response lost", request=request)

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        with pytest.raises(httpx.ReadTimeout, match="response lost"):
            _request(client, is_async, "POST")
        assert delays == []
    assert len(requests) == 1


@pytest.mark.parametrize("is_async", [False, True])
def test_completion_wait_recovers_from_status_and_result_errors(monkeypatch: pytest.MonkeyPatch, is_async: bool) -> None:
    requests: list[httpx.Request] = []
    responses = [
        httpx.Response(503, json={"detail": "pool timeout"}, headers={"Retry-After": "2"}),
        httpx.Response(200, json={"status": "completed"}),
        httpx.Response(502, json={"detail": "gateway"}),
        httpx.Response(200, json={
            "id": RUN_ID, "task": "Find pricing", "title": None, "model": "minimax-m3",
            "contextLimit": 200000, "status": "completed", "result": "done", "error": None,
            "sessionId": SESSION_ID, "workspaceId": None, "totalInputTokens": 1,
            "totalOutputTokens": 1, "totalCostUsd": "0.01", "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:00:00Z",
        }),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return responses.pop(0)

    with _replay(monkeypatch, is_async, handler) as (client, delays):
        result = asyncio.run(AsyncRuns(client).wait_for_completion(RUN_ID)) if is_async else Runs(client).wait_for_completion(RUN_ID)
        assert result.status.value == "completed"
        assert result.result == "done"
        assert delays == [2.125, 1.125]
    assert [(request.method, request.url.path) for request in requests] == [
        ("GET", f"/runs/{RUN_ID}/status"), ("GET", f"/runs/{RUN_ID}/status"),
        ("GET", f"/runs/{RUN_ID}"), ("GET", f"/runs/{RUN_ID}"),
    ]


def test_async_cancellation_during_retry_wait_stops_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(503, json={"detail": "temporary"})

    async def exercise() -> None:
        client = http.AsyncHttpClient("https://api.example.com", "test")
        await client.close()
        client._client = httpx.AsyncClient(base_url="https://api.example.com", transport=httpx.MockTransport(handler))
        waiting = asyncio.Event()

        async def sleep(delay: float) -> None:
            waiting.set()
            await asyncio.Event().wait()

        monkeypatch.setattr(http, "asyncio", SimpleNamespace(sleep=sleep))
        task = asyncio.create_task(client.request("GET", "/resource"))
        try:
            await waiting.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        finally:
            await client.close()

    asyncio.run(exercise())
    assert len(requests) == 1
