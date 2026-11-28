from __future__ import annotations

import asyncio
from typing import Any

import pytest

from browser_use_sdk.v2.resources.browsers import AsyncBrowsers as V2AsyncBrowsers
from browser_use_sdk.v2.resources.browsers import Browsers as V2Browsers
from browser_use_sdk.v3.resources.browsers import AsyncBrowsers as V3AsyncBrowsers
from browser_use_sdk.v3.resources.browsers import Browsers as V3Browsers

from .test_v4 import FakeAsyncHttp, FakeSyncHttp


class FakeHttp:
    def __init__(self) -> None:
        self.calls: list[
            tuple[str, str, dict[str, Any] | None, dict[str, Any] | None]
        ] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, json, params))
        if method == "POST":
            return {
                "id": "00000000-0000-0000-0000-000000000001",
                "status": "active",
                "timeoutAt": "2026-08-21T20:00:00Z",
                "startedAt": "2026-08-21T19:00:00Z",
                "metadata": json["metadata"] if json else {},
            }
        return {"items": [], "totalItems": 0, "pageNumber": 1, "pageSize": 10}


@pytest.mark.parametrize("browser_cls", [V2Browsers, V3Browsers])
def test_browser_metadata_create_and_list(browser_cls: type[Any]) -> None:
    http = FakeHttp()
    browsers = browser_cls(http)

    created = browsers.create(
        metadata={"team": "sdk", "env": "test"},
        pdf_renderer_enabled=False,
        solve_captchas=False,
        extension_ids=["00000000-0000-0000-0000-000000000020"],
        cdp_token_ttl_seconds=300,
        close_connections_on_expiry=True,
    )
    browsers.list(metadata=["team", "env=test"])

    assert created.metadata == {"team": "sdk", "env": "test"}
    assert http.calls[0][2] == {
        "metadata": {"team": "sdk", "env": "test"},
        "pdfRendererEnabled": False,
        "solveCaptchas": False,
        "extensionIds": ["00000000-0000-0000-0000-000000000020"],
        "cdpTokenTtlSeconds": 300,
        "closeConnectionsOnExpiry": True,
    }
    assert http.calls[1][3] == {
        "pageSize": None,
        "pageNumber": None,
        "filterBy": None,
        "agentSessionId": None,
        "metadata": ["team", "env=test"],
    }


@pytest.mark.parametrize("browser_cls", [V2Browsers, V3Browsers])
def test_browser_metadata_rejects_more_than_10_entries(browser_cls: type[Any]) -> None:
    http = FakeHttp()
    browsers = browser_cls(http)
    metadata = {f"key-{index}": f"value-{index}" for index in range(11)}

    with pytest.raises(ValueError, match="metadata supports at most 10"):
        browsers.create(metadata=metadata)

    assert http.calls == []


@pytest.mark.parametrize(
    ("browser_cls", "fake_http"),
    [
        (V2Browsers, FakeSyncHttp),
        (V3Browsers, FakeSyncHttp),
        (V2AsyncBrowsers, FakeAsyncHttp),
        (V3AsyncBrowsers, FakeAsyncHttp),
    ],
)
def test_browser_access_token_routes(browser_cls: type[Any], fake_http: type[Any]) -> None:
    token_id = "00000000-0000-0000-0000-000000000031"
    revoked = {"effectiveBy": "2026-01-01T00:00:02Z"}
    http = fake_http([
        {"id": token_id, "token": "secret", "cdpUrl": "wss://cdp", "liveUrl": None, "expiresAt": None},
        {"items": []},
        revoked,
        revoked,
        {"items": [], "totalItems": 0, "pageNumber": 1, "pageSize": 5},
    ])
    browsers = browser_cls(http)
    calls = [
        browsers.create_access_token("b1", ttl_seconds=300),
        browsers.list_access_tokens("b1"),
        browsers.revoke_access_token("b1", token_id),
        browsers.revoke_all_access_tokens("b1"),
        browsers.get_access_log("b1", page_size=5),
    ]
    if fake_http is FakeAsyncHttp:

        async def in_order() -> None:
            for call in calls:
                await call

        asyncio.run(in_order())

    assert http.calls == [
        ("POST", "/browsers/b1/access-tokens", {"ttlSeconds": 300}, None),
        ("GET", "/browsers/b1/access-tokens", None, None),
        ("DELETE", f"/browsers/b1/access-tokens/{token_id}", None, None),
        ("DELETE", "/browsers/b1/access-tokens", None, None),
        ("GET", "/browsers/b1/access-log", None, {"pageSize": 5, "pageNumber": None}),
    ]
