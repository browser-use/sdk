from __future__ import annotations

import asyncio
from typing import Any

from browser_use_sdk.v3.resources.sessions import AsyncSessions, Sessions


def _session_response() -> dict[str, Any]:
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "status": "running",
        "model": "bu-mini",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }


class FakeSyncHttp:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any] | None] = []

    def request(self, method: str, path: str, *, json: dict[str, Any] | None = None) -> dict[str, Any]:
        self.requests.append(json)
        return _session_response()


class FakeAsyncHttp:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any] | None] = []

    async def request(self, method: str, path: str, *, json: dict[str, Any] | None = None) -> dict[str, Any]:
        self.requests.append(json)
        return _session_response()


def test_v3_sessions_add_use_own_key_when_configured() -> None:
    http = FakeSyncHttp()
    sessions = Sessions(http, use_own_key=True)  # type: ignore[arg-type]

    sessions.create("Find pricing")

    assert http.requests == [{"task": "Find pricing", "useOwnKey": True}]


def test_v3_sessions_allow_per_request_override() -> None:
    http = FakeSyncHttp()
    sessions = Sessions(http, use_own_key=True)  # type: ignore[arg-type]

    sessions.create("Find pricing", use_own_key=False)

    assert http.requests == [{"task": "Find pricing", "useOwnKey": False}]


def test_v3_sessions_send_current_run_controls() -> None:
    http = FakeSyncHttp()
    sessions = Sessions(http)  # type: ignore[arg-type]

    sessions.create(
        "Find pricing",
        thinking_level="high",
        browser_screen_width=1440,
        browser_screen_height=900,
        enable_scheduled_tasks=True,
        skills=False,
        agentmail=False,
        auto_heal=False,
    )

    assert http.requests == [
        {
            "task": "Find pricing",
            "thinkingLevel": "high",
            "browserScreenWidth": 1440,
            "browserScreenHeight": 900,
            "enableScheduledTasks": True,
            "skills": False,
            "agentmail": False,
            "autoHeal": False,
        }
    ]


def test_v3_async_sessions_add_use_own_key_when_configured() -> None:
    async def run() -> None:
        http = FakeAsyncHttp()
        sessions = AsyncSessions(http, use_own_key=True)  # type: ignore[arg-type]

        await sessions.create("Find pricing")

        assert http.requests == [{"task": "Find pricing", "useOwnKey": True}]

    asyncio.run(run())
