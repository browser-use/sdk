"""Request and response shaping for the v4 run, session and integration additions (mocked HTTP)."""

from __future__ import annotations

from typing import Any, Callable

import pytest

from browser_use_sdk.v4 import RunModel
from browser_use_sdk.v4.resources.integrations import Integrations
from browser_use_sdk.v4.resources.runs import Runs
from browser_use_sdk.v4.resources.sessions import Sessions

from .test_v4 import FakeSyncHttp

SESSION_ID = "00000000-0000-0000-0000-000000000002"
WALLET_ID = "00000000-0000-0000-0000-000000000020"
LINK_ID = "00000000-0000-0000-0000-000000000021"

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
            agentcard_wallet_id=WALLET_ID,
            stripe_link_connection_id=LINK_ID,
            op_vault_id="vault",
            op_vault_allowed_domains=["amazon.com"],
        ),
        _RUN,
        (
            "POST",
            "/runs",
            {
                "task": "Buy the cheapest one",
                "model": "bu-ultrafast",
                "opVaultId": "vault",
                "opVaultAllowedDomains": ["amazon.com"],
                "agentcardWalletId": WALLET_ID,
                "stripeLinkConnectionId": LINK_ID,
            },
            None,
        ),
        _ANY,
        id="runs.create camelCases the new fields and unwraps the model enum",
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
