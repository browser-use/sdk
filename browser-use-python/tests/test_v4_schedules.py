"""Mocked HTTP coverage for the synchronous and asynchronous V4 schedules resources."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from uuid import UUID

import httpx
import pytest

from browser_use_sdk.v4 import (
    AsyncBrowserUse,
    BrowserUse,
    OnePasswordSecretSource,
    RunListResponse,
    ScheduleBrowserSettings,
    ScheduleListResponse,
    ScheduleModel,
    ScheduleSecretBinding,
    ScheduleView,
)

from .test_v4 import SESSION_ID, _run_summary

SCHEDULE_ID = "00000000-0000-0000-0000-000000000030"
NEXT_RUN_AT = "2027-03-15T13:00:00Z"
SCHEDULE = {
    "id": SCHEDULE_ID,
    "task": "Read the page title",
    "cronExpr": "0 9 * * *",
    "runAt": None,
    "timezone": "America/New_York",
    "nextRunAt": NEXT_RUN_AT,
    "enabled": True,
    "sessionId": SESSION_ID,
    "settings": {"maxCostUsd": "2.50"},
    "createdAt": NEXT_RUN_AT,
    "updatedAt": NEXT_RUN_AT,
}
SECRET_SOURCE = {
    "type": "onepassword",
    "integrationId": "00000000-0000-0000-0000-000000000040",
    "vaultId": "vault",
    "itemId": "item",
    "fieldId": "password",
}


@pytest.mark.parametrize("async_client", [False, True], ids=["sync", "async"])
def test_schedule_requests(async_client: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[httpx.Request] = []
    responses = iter([
        httpx.Response(201, json=SCHEDULE),
        httpx.Response(201, json={**SCHEDULE, "runAt": NEXT_RUN_AT, "cronExpr": None}),
        httpx.Response(200, json={"schedules": [SCHEDULE], "nextCursor": "next", "hasMore": True}),
        httpx.Response(200, json=SCHEDULE),
        httpx.Response(200, json={**SCHEDULE, "enabled": False}),
        httpx.Response(
            200,
            json={
                "runs": [{**_run_summary("completed"), "scheduleId": SCHEDULE_ID}],
                "nextCursor": None,
                "hasMore": False,
            },
        ),
        httpx.Response(204),
    ])

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return next(responses)

    transport = httpx.MockTransport(respond)
    sync_http, async_http = httpx.Client, httpx.AsyncClient
    if async_client:
        monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: async_http(transport=transport, **kwargs))
    else:
        monkeypatch.setattr(httpx, "Client", lambda **kwargs: sync_http(transport=transport, **kwargs))
    client_type = AsyncBrowserUse if async_client else BrowserUse
    client = client_type(api_key="test", base_url="https://api.example.com/api/v4")

    async def call(method: str, *args: Any, **kwargs: Any) -> Any:
        result = getattr(client.schedules, method)(*args, **kwargs)
        return await result if async_client else result

    async def exercise() -> None:
        try:
            binding = ScheduleSecretBinding.model_validate({
                "alias": "login",
                "source": SECRET_SOURCE,
                "allowedDomains": ["example.com"],
            })
            assert isinstance(binding.source, OnePasswordSecretSource)
            created = await call(
                "create",
                SCHEDULE["task"],
                cron_expr=SCHEDULE["cronExpr"],
                timezone=SCHEDULE["timezone"],
                session_id=UUID(SESSION_ID),
                model=ScheduleModel.bu_ultrafast,
                output_schema={"type": "object"},
                browser_settings=ScheduleBrowserSettings(proxyCountryCode=None),
                secret_bindings=[binding],
                keep_alive=None,
                futureField="pass through",
            )
            assert isinstance(created, ScheduleView)
            assert created.id == UUID(SCHEDULE_ID)
            assert created.settings.max_cost_usd.root == "2.50"

            once = await call(
                "create", "Check once", run_at="2027-03-15T09:00:00", output_schema=None
            )
            assert once.run_at.isoformat() == "2027-03-15T13:00:00+00:00"

            page = await call("list", enabled=False, limit=5, cursor="prior")
            assert isinstance(page, ScheduleListResponse)
            assert page.schedules == [created]
            assert page.next_cursor == "next"
            assert page.has_more

            assert await call("get", created.id) == created
            updated = await call(
                "update",
                created.id,
                enabled=False,
                task="Check again",
                cron_expr="0 10 * * *",
                timezone="UTC",
                futureField="pass through",
            )
            assert updated.enabled is False
            runs = await call(
                "runs", created.id, session_id=UUID(SESSION_ID), metadata=["watch", "region=us"]
            )
            assert isinstance(runs, RunListResponse)
            assert runs.runs[0].schedule_id == created.id
            assert await call("delete", created.id) is None
        finally:
            if isinstance(client, AsyncBrowserUse):
                await client.close()
            else:
                client.close()

    asyncio.run(exercise())

    base = "/api/v4/schedules"
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", base),
        ("POST", base),
        ("GET", base),
        ("GET", f"{base}/{SCHEDULE_ID}"),
        ("PATCH", f"{base}/{SCHEDULE_ID}"),
        ("GET", f"{base}/{SCHEDULE_ID}/runs"),
        ("DELETE", f"{base}/{SCHEDULE_ID}"),
    ]
    assert json.loads(requests[0].content) == {
        "task": SCHEDULE["task"],
        "cronExpr": SCHEDULE["cronExpr"],
        "timezone": SCHEDULE["timezone"],
        "sessionId": SESSION_ID,
        "model": "bu-ultrafast",
        "outputSchema": {"type": "object"},
        "browserSettings": {"proxyCountryCode": None},
        "secretBindings": [{
            "alias": "login", "source": SECRET_SOURCE, "allowedDomains": ["example.com"]
        }],
        "keepAlive": None,
        "futureField": "pass through",
    }
    assert json.loads(requests[1].content) == {
        "task": "Check once",
        "runAt": "2027-03-15T09:00:00",
        "outputSchema": None,
    }
    assert dict(requests[2].url.params) == {"enabled": "false", "limit": "5", "cursor": "prior"}
    assert json.loads(requests[4].content) == {
        "enabled": False,
        "task": "Check again",
        "cronExpr": "0 10 * * *",
        "timezone": "UTC",
        "futureField": "pass through",
    }
    assert requests[5].url.params["sessionId"] == SESSION_ID
    assert requests[5].url.params.get_list("metadata") == ["watch", "region=us"]
