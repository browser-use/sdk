"""Request and response shaping for the v4 run, session and integration additions (mocked HTTP)."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

import pytest

from browser_use_sdk.v4 import (
    AsyncBrowserUse,
    BrowserAccessEventList,
    BrowserAccessTokenRevoked,
    BrowserAccessTokenCreated,
    BrowserAccessTokenList,
    BrowserProxyMode,
    BrowserProxyView,
    BrowserUse,
    CustomProxy,
    NetworkPolicyDefaultAction,
    NetworkPolicyDomainList,
    NetworkPolicyListResponse,
    NetworkPolicyView,
    ProxyProtocol,
    QueuedMessage,
    RunListResponse,
    RunModel,
    SessionCompactResponse,
)
from browser_use_sdk.v4 import client as client_module
from browser_use_sdk.v4.resources.integrations import Integrations
from browser_use_sdk.v4.resources.profiles import Profiles
from browser_use_sdk.v4.resources.runs import Runs
from browser_use_sdk.v4.resources.sessions import Sessions

from .test_v4 import FakeAsyncHttp, FakeSyncHttp, _queued_message

SESSION_ID = "00000000-0000-0000-0000-000000000002"
LINK_ID = "00000000-0000-0000-0000-000000000021"
PROFILE_ID = "00000000-0000-0000-0000-000000000040"

_RUN = {
    "id": "00000000-0000-0000-0000-000000000001",
    "status": "queued",
    "model": "bu-ultrafast",
    "sessionId": SESSION_ID,
    "workspaceId": "00000000-0000-0000-0000-000000000003",
    "eventsUrl": "https://api.browser-use.com/api/v4/runs/x/events",
}
_SESSION = {
    "sessionId": SESSION_ID,
    "workspaceId": None,
    "latestRunId": "00000000-0000-0000-0000-000000000001",
    "task": "Find pricing",
    "title": None,
    "status": "completed",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}
_SHARE = {
    "id": "00000000-0000-0000-0000-000000000030",
    "shareToken": "tok",
    "sessionId": SESSION_ID,
    "isActive": False,
    "viewCount": 0,
    "createdAt": "2026-01-01T00:00:00Z",
    "shareUrl": "https://cloud.browser-use.com/share/v4/tok",
}
_ANY = object()

# Shaping the wire depends on: snake_case kwargs to camelCase bodies, the enum unwrapped to its
# value, the unset-vs-None title sentinel, query names, and a null share body. Plain path
# passthroughs are covered by test_vibe.py's endpoint map.
CASES: list[Any] = [
    pytest.param(
        Runs,
        lambda r: r.create(
            "Buy the cheapest one",
            model=RunModel.bu_ultrafast,
            metadata={"flow": "checkout"},
            stripeLinkConnectionId=LINK_ID,
            op_vault_id="vault",
            op_vault_allowed_domains=["amazon.com"],
            keep_alive=None,
        ),
        _RUN,
        (
            "POST",
            "/runs",
            {
                "task": "Buy the cheapest one",
                "model": "bu-ultrafast",
                "metadata": {"flow": "checkout"},
                "opVaultId": "vault",
                "opVaultAllowedDomains": ["amazon.com"],
                "stripeLinkConnectionId": LINK_ID,
                "keepAlive": None,
            },
            None,
        ),
        _ANY,
        id="runs.create camelCases the new fields, passes extras through and unwraps the model enum",
    ),
    pytest.param(
        Sessions,
        lambda s: s.update(SESSION_ID, title=None),
        _SESSION,
        ("PATCH", f"/sessions/{SESSION_ID}", {"title": None}, None),
        _ANY,
        id="sessions.update sends a null title to clear it",
    ),
    pytest.param(
        Sessions,
        lambda s: s.update(SESSION_ID),
        _SESSION,
        ("PATCH", f"/sessions/{SESSION_ID}", {}, None),
        _ANY,
        id="sessions.update without a title sends an empty body",
    ),
    pytest.param(
        Sessions,
        lambda s: s.update_share(SESSION_ID, is_active=False),
        _SHARE,
        ("PUT", f"/sessions/{SESSION_ID}/share", {"isActive": False}, None),
        _ANY,
        id="sessions.update_share camelCases is_active",
    ),
    pytest.param(
        Sessions,
        lambda s: s.get_share(SESSION_ID),
        None,
        ("GET", f"/sessions/{SESSION_ID}/share", None, None),
        None,
        id="sessions.get_share returns None for a never-shared session",
    ),
    pytest.param(
        Sessions,
        lambda s: s.update_cost_cap(SESSION_ID, max_cost_usd="2.50"),
        {"sessionId": SESSION_ID, "maxCostUsd": "2.50"},
        ("PATCH", f"/sessions/{SESSION_ID}/cost-cap", {"maxCostUsd": "2.50"}, None),
        _ANY,
        id="sessions.update_cost_cap camelCases max_cost_usd",
    ),
    pytest.param(
        Profiles,
        lambda p: p.update(PROFILE_ID, name=None),
        {"id": PROFILE_ID, "createdAt": "2026-01-01T00:00:00Z", "updatedAt": "2026-01-01T00:00:00Z"},
        ("PATCH", f"/profiles/{PROFILE_ID}", {"name": None}, None),
        _ANY,
        id="profiles.update sends a null name to clear it and omits unset user_id",
    ),
    pytest.param(
        Profiles,
        lambda p: p.list(page_size=5, page_number=2),
        {"items": [], "totalItems": 0, "pageNumber": 2, "pageSize": 5},
        ("GET", "/profiles", None, {"query": None, "pageSize": 5, "pageNumber": 2}),
        _ANY,
        id="profiles.list passes the API's camelCase query names",
    ),
    pytest.param(
        Integrations,
        lambda i: i.list(limit=5, search="gmail", connected_only=True),
        {"integrations": [], "total": 0, "limit": 5, "offset": 0},
        (
            "GET",
            "/integrations",
            None,
            {"limit": 5, "offset": None, "search": "gmail", "popular_only": None, "connected_only": True},
        ),
        _ANY,
        id="integrations.list passes the API's query names",
    ),
]


@pytest.mark.parametrize(("resource", "call", "response", "expected_call", "expected_result"), CASES)
def test_v4_request_shaping(
    resource: Callable[[Any], Any],
    call: Callable[[Any], Any],
    response: Any,
    expected_call: tuple[Any, ...],
    expected_result: Any,
) -> None:
    http = FakeSyncHttp([response])
    result = call(resource(http))
    assert http.calls == [expected_call]
    if expected_result is not _ANY:
        assert result == expected_result


_POLICY = {
    "id": SESSION_ID,
    "name": "Block ads",
    "defaultAction": "allow",
    "allow": {"domains": []},
    "block": {"domains": ["ads.example.com"]},
    "version": 1,
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}
_PROXY = {"mode": "custom", "country": None, "exitIp": "192.0.2.1"}
_POLICY_PATH = f"/network-policies/{SESSION_ID}"
_PROXY_PATH = f"/browsers/{SESSION_ID}/proxy"
_TOKEN_ID = "00000000-0000-0000-0000-000000000031"
_TOKENS_PATH = f"/browsers/{SESSION_ID}/access-tokens"
_REVOKED = {"effectiveBy": "2026-01-01T00:00:02Z"}
_ACCESS_EVENT = {
    "id": "00000000-0000-0000-0000-000000000032",
    "event": "tokens_revoked",
    "tokenId": None,
    "tokenKind": None,
    "revokedKinds": ["customer", "viewer"],
    "actor": {"type": "api_key", "id": "key-1", "runId": None},
    "createdAt": "2026-01-01T00:00:00Z",
}


@pytest.mark.parametrize(
    ("call", "response", "expected_call", "model"),
    [
        pytest.param(
            lambda c: c.network_policies.create(
                "Block ads", default_action=NetworkPolicyDefaultAction.allow, future=True
            ),
            _POLICY,
            ("POST", "/network-policies", {"name": "Block ads", "defaultAction": "allow", "future": True}, None),
            NetworkPolicyView,
            id="network-policies-create",
        ),
        pytest.param(
            lambda c: c.network_policies.list(page_size=5, page_number=2),
            {"items": [], "totalItems": 0, "pageNumber": 2, "pageSize": 5},
            ("GET", "/network-policies", None, {"pageSize": 5, "pageNumber": 2}),
            NetworkPolicyListResponse,
            id="network-policies-list",
        ),
        pytest.param(
            lambda c: c.network_policies.get(SESSION_ID),
            _POLICY,
            ("GET", _POLICY_PATH, None, None),
            NetworkPolicyView,
            id="network-policies-get",
        ),
        pytest.param(
            lambda c: c.network_policies.update(SESSION_ID, block=NetworkPolicyDomainList(domains=[]), future=True),
            {**_POLICY, "block": {"domains": []}},
            ("PATCH", _POLICY_PATH, {"block": {"domains": []}, "future": True}, None),
            NetworkPolicyView,
            id="network-policies-update",
        ),
        pytest.param(
            lambda c: c.network_policies.delete(SESSION_ID),
            None,
            ("DELETE", _POLICY_PATH, None, None),
            None,
            id="network-policies-delete",
        ),
        pytest.param(
            lambda c: c.browsers.get_proxy(SESSION_ID),
            _PROXY,
            ("GET", _PROXY_PATH, None, None),
            BrowserProxyView,
            id="browsers-get-proxy",
        ),
        pytest.param(
            lambda c: c.browsers.update_proxy(
                SESSION_ID,
                mode=BrowserProxyMode.custom,
                custom_proxy=CustomProxy.model_validate(
                    {"host": "proxy.example.com", "port": 443, "protocol": ProxyProtocol.https, "caBundle": "pem"}
                ),
                future=True,
            ),
            _PROXY,
            (
                "PATCH",
                _PROXY_PATH,
                {
                    "mode": "custom",
                    "customProxy": {
                        "host": "proxy.example.com", "port": 443, "ignoreCertErrors": False,
                        "protocol": "https", "caBundle": "pem",
                    },
                    "future": True,
                },
                None,
            ),
            BrowserProxyView,
            id="browsers-update-proxy",
        ),
        pytest.param(
            lambda c: c.browsers.create_access_token(
                SESSION_ID, ttl_seconds=300, label="ci", close_connections_on_expiry=True, future=True
            ),
            {
                "id": _TOKEN_ID,
                "token": "secret",
                "cdpUrl": "wss://cdp.example.com/?token=secret",
                "liveUrl": None,
                "expiresAt": "2026-01-01T00:05:00Z",
            },
            (
                "POST",
                _TOKENS_PATH,
                {"ttlSeconds": 300, "label": "ci", "closeConnectionsOnExpiry": True, "future": True},
                None,
            ),
            BrowserAccessTokenCreated,
            id="browsers-create-access-token",
        ),
        pytest.param(
            lambda c: c.browsers.list_access_tokens(SESSION_ID),
            {"items": [{
                "id": _TOKEN_ID, "label": "", "kind": "system", "createdAt": "2026-01-01T00:00:00Z",
                "expiresAt": None, "lastUsedAt": None,
            }]},
            ("GET", _TOKENS_PATH, None, None),
            BrowserAccessTokenList,
            id="browsers-list-access-tokens",
        ),
        pytest.param(
            lambda c: c.browsers.revoke_access_token(SESSION_ID, _TOKEN_ID),
            _REVOKED,
            ("DELETE", f"{_TOKENS_PATH}/{_TOKEN_ID}", None, None),
            BrowserAccessTokenRevoked,
            id="browsers-revoke-access-token",
        ),
        pytest.param(
            lambda c: c.browsers.revoke_all_access_tokens(SESSION_ID),
            _REVOKED,
            ("DELETE", _TOKENS_PATH, None, None),
            BrowserAccessTokenRevoked,
            id="browsers-revoke-all-access-tokens",
        ),
        pytest.param(
            lambda c: c.browsers.get_access_log(SESSION_ID, page_size=5, page_number=2),
            {"items": [_ACCESS_EVENT], "totalItems": 1, "pageNumber": 2, "pageSize": 5},
            ("GET", f"/browsers/{SESSION_ID}/access-log", None, {"pageSize": 5, "pageNumber": 2}),
            BrowserAccessEventList,
            id="browsers-get-access-log",
        ),
        pytest.param(
            lambda c: c.sessions.compact(SESSION_ID),
            {"sessionId": SESSION_ID, "requested": True},
            ("POST", f"/sessions/{SESSION_ID}/compact", None, None),
            SessionCompactResponse,
            id="sessions-compact",
        ),
        pytest.param(
            lambda c: c.sessions.send_message(SESSION_ID, confirm_input_id=7),
            {**_queued_message(), "needsConfirmation": True, "reason": "review required"},
            ("POST", f"/sessions/{SESSION_ID}/queue", {"confirmInputId": 7}, None),
            QueuedMessage,
            id="sessions-confirm-input",
        ),
        pytest.param(
            lambda c: c.runs.list(metadata=["flow", "source=api"]),
            {"runs": [], "nextCursor": None},
            ("GET", "/runs", None, {"sessionId": None, "cursor": None, "limit": None, "metadata": ["flow", "source=api"]}),
            RunListResponse,
            id="runs-list-metadata",
        ),
    ],
)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
def test_v4_client_requests(
    call: Callable[[Any], Any],
    response: Any,
    expected_call: tuple[Any, ...],
    model: Any,
    asynchronous: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if asynchronous:
        http = FakeAsyncHttp([response])
        monkeypatch.setattr(client_module, "AsyncHttpClient", lambda **kwargs: http)
        result = asyncio.run(call(AsyncBrowserUse(api_key="test")))
    else:
        http = FakeSyncHttp([response])
        monkeypatch.setattr(client_module, "SyncHttpClient", lambda **kwargs: http)
        result = call(BrowserUse(api_key="test"))

    assert http.calls == [expected_call]
    assert result == (model.model_validate(response) if model else None)
