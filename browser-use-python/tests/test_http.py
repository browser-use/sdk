from collections.abc import Callable
from unittest.mock import patch

import httpx
import pytest

from browser_use_sdk import APIKeySpendLimitError
from browser_use_sdk._core.http import SyncHttpClient, _clean_params
from browser_use_sdk.v4.resources.runs import Runs
from browser_use_sdk.v4.resources.sessions import Sessions

_RUN_SUMMARY = {
    "id": "00000000-0000-0000-0000-000000000001",
    "task": "t",
    "title": None,
    "model": "minimax-m3",
    "contextLimit": 200000,
    "status": "cancelled",
    "result": None,
    "error": None,
    "sessionId": "00000000-0000-0000-0000-000000000002",
    "workspaceId": None,
    "totalInputTokens": 1,
    "totalOutputTokens": 1,
    "totalCostUsd": "0.01",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}


def test_clean_params_repeats_sequence_values() -> None:
    cleaned = _clean_params(
        {
            "metadata": ["team", "env=prod"],
            "pageSize": 10,
            "includeUrls": False,
            "cursor": None,
        }
    )
    assert cleaned == {
        "metadata": ["team", "env=prod"],
        "pageSize": "10",
        "includeUrls": "false",
    }
    assert httpx.QueryParams(cleaned).multi_items() == [
        ("metadata", "team"),
        ("metadata", "env=prod"),
        ("pageSize", "10"),
        ("includeUrls", "false"),
    ]


def test_request_forwards_headers_alongside_authentication() -> None:
    requested_headers = httpx.Headers()

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requested_headers
        requested_headers = request.headers
        return httpx.Response(200, json={})

    client = SyncHttpClient("https://api.example.com", "test")
    client._client.close()
    client._client = httpx.Client(
        base_url="https://api.example.com",
        headers={"X-Browser-Use-API-Key": "test"},
        transport=httpx.MockTransport(handler),
    )
    try:
        client.request(
            "POST",
            "/sessions/id/queue",
            json={"text": "hello"},
            headers={"X-V4-Queue-Deduplicate": "exact-text-v1"},
        )
    finally:
        client.close()

    assert requested_headers["X-V4-Queue-Deduplicate"] == "exact-text-v1"
    assert requested_headers["X-Browser-Use-API-Key"] == "test"


def _mock_client(handler: Callable[[httpx.Request], httpx.Response]) -> SyncHttpClient:
    client = SyncHttpClient("https://api.example.com", "test")
    client._client.close()
    client._client = httpx.Client(
        base_url="https://api.example.com", transport=httpx.MockTransport(handler)
    )
    return client


def test_purge_accepts_202_with_empty_body() -> None:
    client = _mock_client(lambda _: httpx.Response(202, headers={"Retry-After": "60"}))

    assert Sessions(client).purge("session-id") is None


def test_spend_limit_402_raises_typed_error() -> None:
    detail = {
        "code": "api_key_monthly_spend_limit_reached",
        "message": "Monthly spend limit of $5.00 reached",
        "cap": 5.0,
        "spent": 5.01,
    }
    client = _mock_client(lambda _: httpx.Response(402, json={"detail": detail}))

    with pytest.raises(APIKeySpendLimitError) as raised:
        client.request("POST", "/runs", json={"task": "x"})

    error = raised.value
    assert (error.status_code, error.message) == (402, detail["message"])
    assert (error.code, error.cap, error.spent) == (detail["code"], 5.0, 5.01)


def test_cancel_retries_busy_503_after_retry_after() -> None:
    replies = [
        httpx.Response(503, json={"detail": "busy"}, headers={"Retry-After": "2"}),
        httpx.Response(200, json=_RUN_SUMMARY),
    ]
    client = _mock_client(lambda _: replies.pop(0))

    with patch("browser_use_sdk._core.http.time.sleep") as sleep:
        run = Runs(client).cancel(_RUN_SUMMARY["id"])

    sleep.assert_called_once_with(2.0)
    assert run.status.value == "cancelled"
