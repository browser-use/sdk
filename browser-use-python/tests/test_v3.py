"""Mocked-HTTP tests for the v3 namespace."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from browser_use_sdk.generated.v3.models import MessageListResponse, SessionResponse
from browser_use_sdk.v3.helpers import AsyncSessionRun
from browser_use_sdk.v3.resources.profiles import AsyncProfiles, Profiles

SESSION = {
    "id": "00000000-0000-0000-0000-000000000001",
    "status": "idle",
    "model": "bu-mini",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-01T00:00:00Z",
}


class FakeHttp:
    def __init__(self) -> None:
        self.params: list[dict[str, Any] | None] = []

    def request(self, method: str, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.params.append(params)
        return {"items": [], "totalItems": 0, "pageNumber": 2, "pageSize": 2}


class FakeAsyncHttp(FakeHttp):
    async def request(self, method: str, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:  # type: ignore[override]
        return FakeHttp.request(self, method, path, params=params)


def test_profiles_list_sends_spec_pagination_and_keeps_page_alias() -> None:
    sync_http, async_http = FakeHttp(), FakeAsyncHttp()
    profiles, async_profiles = Profiles(sync_http), AsyncProfiles(async_http)  # type: ignore[arg-type]

    profiles.list(page_number=2, page_size=2)
    profiles.list(page=2, page_size=2)
    asyncio.run(async_profiles.list(page_number=2, page_size=2))
    asyncio.run(async_profiles.list(page=2, page_size=2))

    expected = {"query": None, "pageNumber": 2, "pageSize": 2}
    assert sync_http.params == async_http.params == [expected, expected]


class FakeSessions:
    async def get(self, session_id: str) -> SessionResponse:
        return SessionResponse.model_validate(SESSION)

    async def messages(self, session_id: str, **_: Any) -> MessageListResponse:
        return MessageListResponse.model_validate({"messages": [], "hasMore": False})


def test_async_run_handle_creates_session_once() -> None:
    creates: list[int] = []

    async def create() -> SessionResponse:
        creates.append(1)
        await asyncio.sleep(0)
        return SessionResponse.model_validate(SESSION)

    async def failing_create() -> SessionResponse:
        creates.append(1)
        raise RuntimeError("create failed")

    async def exercise() -> None:
        run: AsyncSessionRun[Any] = AsyncSessionRun(create, FakeSessions(), interval=0)  # type: ignore[arg-type]
        await asyncio.gather(run, run)
        async for _ in run:
            pass
        assert (await run).session.status.value == "idle"
        assert len(creates) == 1

        failed: AsyncSessionRun[Any] = AsyncSessionRun(failing_create, FakeSessions(), interval=0)  # type: ignore[arg-type]
        for _ in range(2):
            with pytest.raises(RuntimeError, match="create failed"):
                await failed
        assert len(creates) == 2

    asyncio.run(exercise())


def test_async_run_handle_survives_cancelled_waiter() -> None:
    creates: list[int] = []

    async def slow_create() -> SessionResponse:
        creates.append(1)
        await asyncio.sleep(0.05)
        return SessionResponse.model_validate(SESSION)

    async def exercise() -> None:
        run: AsyncSessionRun[Any] = AsyncSessionRun(slow_create, FakeSessions(), interval=0)  # type: ignore[arg-type]
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(run, 0.01)
        assert (await run).session.status.value == "idle"
        assert run.session_id == SESSION["id"] and len(creates) == 1

    asyncio.run(exercise())
