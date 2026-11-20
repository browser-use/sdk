"""client.feedback() posts to /api/v4/feedback, which is not in the OpenAPI spec (mocked HTTP)."""

from __future__ import annotations

import asyncio
import functools
import json
from unittest.mock import patch

import httpx
import pytest

from browser_use_sdk.v4 import AsyncBrowserUse, BrowserUse, BrowserUseError

BASE_URL = "https://api.example.com/api/v4"


def _transport(status: int, seen: list[httpx.Request]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if status == 204:
            return httpx.Response(204)
        return httpx.Response(status, json={"detail": "message must be 1 to 5000 characters"})

    return httpx.MockTransport(handler)


def _send(client_cls: type, status: int, message: str, **extra: str) -> tuple[object, list[httpx.Request]]:
    seen: list[httpx.Request] = []
    transport = _transport(status, seen)
    if client_cls is BrowserUse:
        with patch.object(httpx, "Client", functools.partial(httpx.Client, transport=transport)):
            client = BrowserUse(api_key="bu_test", base_url=BASE_URL)
        with client:
            return client.feedback(message, **extra), seen

    async def run() -> object:
        with patch.object(httpx, "AsyncClient", functools.partial(httpx.AsyncClient, transport=transport)):
            client = AsyncBrowserUse(api_key="bu_test", base_url=BASE_URL)
        async with client:
            return await client.feedback(message, **extra)

    return asyncio.run(run()), seen


@pytest.mark.parametrize("client_cls", [BrowserUse, AsyncBrowserUse])
def test_feedback_posts_message_with_api_key(client_cls: type) -> None:
    result, seen = _send(client_cls, 204, "kind: bug\nruns.create 500s", source="ci")

    assert result is None
    [request] = seen
    assert (request.method, str(request.url)) == ("POST", f"{BASE_URL}/feedback")
    assert request.headers["X-Browser-Use-API-Key"] == "bu_test"
    assert json.loads(request.content) == {"message": "kind: bug\nruns.create 500s", "source": "ci"}


@pytest.mark.parametrize("client_cls", [BrowserUse, AsyncBrowserUse])
def test_feedback_raises_browser_use_error_on_rejection(client_cls: type) -> None:
    with pytest.raises(BrowserUseError) as raised:
        _send(client_cls, 422, "")

    assert raised.value.status_code == 422
    assert raised.value.message == "message must be 1 to 5000 characters"
