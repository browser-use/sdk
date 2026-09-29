"""Mocked-HTTP tests for v4 session management, integrations, wallets and model presets."""

from __future__ import annotations

import asyncio
from typing import Any

from browser_use_sdk.v4 import AsyncBrowserUse, BrowserUse, RunModel
from browser_use_sdk.v4.resources.integrations import AsyncIntegrations, Integrations
from browser_use_sdk.v4.resources.runs import Runs
from browser_use_sdk.v4.resources.sessions import AsyncSessions, Sessions
from browser_use_sdk.v4.resources.wallets import AsyncWallets, Wallets

from .test_v4 import FakeAsyncHttp, FakeSyncHttp

SESSION_ID = "00000000-0000-0000-0000-000000000002"
WALLET_ID = "00000000-0000-0000-0000-000000000020"
LINK_ID = "00000000-0000-0000-0000-000000000021"


def _session_info(title: str | None = None) -> dict[str, Any]:
    return {
        "sessionId": SESSION_ID,
        "workspaceId": None,
        "latestRunId": "00000000-0000-0000-0000-000000000001",
        "task": "Find pricing",
        "title": title,
        "status": "completed",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }


def _share(active: bool = True) -> dict[str, Any]:
    return {
        "id": "00000000-0000-0000-0000-000000000030",
        "shareToken": "tok",
        "sessionId": SESSION_ID,
        "isActive": active,
        "viewCount": 0,
        "createdAt": "2026-01-01T00:00:00Z",
        "shareUrl": "https://cloud.browser-use.com/share/v4/tok",
    }


_COST = {
    "sessionId": SESSION_ID,
    "numRuns": 2,
    "llmCostUsd": "0.05",
    "searchCostUsd": "0.00",
    "browserCostUsd": "0.03",
    "proxyCostUsd": "0.02",
    "proxyUsedMb": "1.5",
    "totalCostUsd": "0.10",
}


def test_clients_expose_integrations_and_wallets() -> None:
    client = BrowserUse(api_key="bu_test")
    assert isinstance(client.integrations, Integrations)
    assert isinstance(client.wallets, Wallets)
    client.close()
    async_client = AsyncBrowserUse(api_key="bu_test")
    assert isinstance(async_client.integrations, AsyncIntegrations)
    assert isinstance(async_client.wallets, AsyncWallets)
    asyncio.run(async_client.close())


def test_run_model_enum_lists_ultrafast_presets() -> None:
    assert RunModel("bu-ultrafast") is RunModel.bu_ultrafast
    assert RunModel("bu-fast") is RunModel.bu_fast


def test_runs_create_sends_presets_payment_and_vault_fields() -> None:
    http = FakeSyncHttp(
        [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "status": "queued",
                "model": "bu-ultrafast",
                "sessionId": SESSION_ID,
                "workspaceId": "00000000-0000-0000-0000-000000000003",
                "eventsUrl": "https://api.browser-use.com/api/v4/runs/x/events",
            }
        ]
    )
    runs = Runs(http)  # type: ignore[arg-type]

    runs.create(
        "Buy the cheapest one",
        model=RunModel.bu_ultrafast,
        agentcard_wallet_id=WALLET_ID,
        stripe_link_connection_id=LINK_ID,
        op_vault_id="vault",
        op_vault_allowed_domains=["amazon.com"],
    )

    assert http.calls[0][:3] == (
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
    )


def test_sessions_update_delete_and_cost() -> None:
    http = FakeSyncHttp([_session_info(), None, _COST])
    sessions = Sessions(http)  # type: ignore[arg-type]

    info = sessions.update(SESSION_ID, title=None)
    sessions.delete(SESSION_ID)
    cost = sessions.cost(SESSION_ID)

    assert info.title is None
    assert http.calls[0][:3] == ("PATCH", f"/sessions/{SESSION_ID}", {"title": None})
    assert http.calls[1][:2] == ("DELETE", f"/sessions/{SESSION_ID}")
    assert http.calls[2][:2] == ("GET", f"/sessions/{SESSION_ID}/cost")
    assert cost.total_cost_usd == "0.10"


def test_sessions_update_without_title_sends_empty_body() -> None:
    http = FakeSyncHttp([_session_info("kept")])
    Sessions(http).update(SESSION_ID)  # type: ignore[arg-type]
    assert http.calls[0][2] == {}


def test_sessions_share_lifecycle() -> None:
    http = FakeSyncHttp([None, _share(), _share(active=False)])
    sessions = Sessions(http)  # type: ignore[arg-type]

    assert sessions.get_share(SESSION_ID) is None
    assert sessions.create_share(SESSION_ID).share_url.endswith("/tok")
    assert sessions.update_share(SESSION_ID, is_active=False).is_active is False

    assert http.calls[0][:2] == ("GET", f"/sessions/{SESSION_ID}/share")
    assert http.calls[1][:2] == ("POST", f"/sessions/{SESSION_ID}/share")
    assert http.calls[2][:3] == ("PUT", f"/sessions/{SESSION_ID}/share", {"isActive": False})


def test_async_sessions_share_and_cost() -> None:
    http = FakeAsyncHttp([_share(), _COST])
    sessions = AsyncSessions(http)  # type: ignore[arg-type]

    async def go() -> None:
        assert (await sessions.get_share(SESSION_ID)) is not None
        assert (await sessions.cost(SESSION_ID)).num_runs == 2

    asyncio.run(go())
    assert http.calls[1][:2] == ("GET", f"/sessions/{SESSION_ID}/cost")


def test_integrations_routes() -> None:
    http = FakeSyncHttp(
        [
            {"integrations": [], "total": 0, "limit": 5, "offset": 0},
            {"categories": ["email"]},
            {"redirect_url": "https://composio.example/auth", "provider": "gmail"},
            {"provider": "gmail", "is_connected": True},
            {"success": True, "provider": "gmail"},
        ]
    )
    integrations = Integrations(http)  # type: ignore[arg-type]

    integrations.list(limit=5, search="gmail", connected_only=True)
    assert integrations.categories().categories == ["email"]
    assert integrations.authorize("gmail").redirect_url.startswith("https://")
    assert integrations.status("gmail").is_connected is True
    assert integrations.disconnect("gmail").success is True

    assert http.calls[0][:2] == ("GET", "/integrations")
    assert http.calls[0][3] == {
        "limit": 5,
        "offset": None,
        "search": "gmail",
        "popular_only": None,
        "connected_only": True,
    }
    assert [c[:2] for c in http.calls[1:]] == [
        ("GET", "/integrations/categories"),
        ("POST", "/integrations/gmail/authorize"),
        ("GET", "/integrations/gmail/status"),
        ("DELETE", "/integrations/gmail"),
    ]


def test_wallets_routes() -> None:
    http = FakeSyncHttp(
        [
            {"wallets": []},
            {"isConnected": True, "connectionId": LINK_ID, "mode": "live"},
        ]
    )
    wallets = Wallets(http)  # type: ignore[arg-type]

    assert wallets.agentcard().wallets == []
    link = wallets.stripe_link()

    assert str(link.connection_id) == LINK_ID
    assert [c[:2] for c in http.calls] == [("GET", "/agentcard/wallets"), ("GET", "/stripe-link")]
