"""Tests for the v2 namespace."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

import browser_use_sdk
import browser_use_sdk.v2 as v2
from browser_use_sdk.generated.v2.models import TaskCreatedResponse, TaskStatusView, TaskView
from browser_use_sdk.v2.helpers import AsyncTaskRun
from browser_use_sdk.v2.resources.tasks import Tasks

TASK_ID = "00000000-0000-0000-0000-000000000001"


def test_v2_namespace_exports_the_root_api() -> None:
    assert set(browser_use_sdk.__all__) <= set(v2.__all__)
    assert all(getattr(v2, name) is getattr(browser_use_sdk, name) for name in browser_use_sdk.__all__)


class FakeHttp:
    def __init__(self) -> None:
        self.paths: list[str] = []

    def request(self, method: str, path: str) -> dict[str, Any]:
        self.paths.append(path)
        if path.endswith("/status"):
            return {"id": TASK_ID, "status": "failed"}
        return {
            "id": TASK_ID, "sessionId": TASK_ID, "llm": "browser-use-2.0", "task": "t", "status": "failed",
            "createdAt": "2026-01-01T00:00:00Z", "metadata": {}, "steps": [], "outputFiles": [],
            "browserUseVersion": "0.12", "isSuccess": False,
        }


def test_wait_returns_failed_task_without_polling_to_timeout() -> None:
    http = FakeHttp()

    task = Tasks(http).wait(TASK_ID, timeout=0.05, interval=0.01)  # type: ignore[arg-type]

    assert task.status.value == "failed"
    assert http.paths == [f"/tasks/{TASK_ID}/status", f"/tasks/{TASK_ID}"]


class FakeAsyncTasks:
    async def status(self, task_id: str) -> TaskStatusView:
        return TaskStatusView.model_validate(FakeHttp().request("GET", f"/tasks/{task_id}/status"))

    async def get(self, task_id: str) -> TaskView:
        return TaskView.model_validate(FakeHttp().request("GET", f"/tasks/{task_id}"))


def test_async_run_handle_creates_task_once() -> None:
    creates: list[int] = []

    async def slow_create() -> TaskCreatedResponse:
        creates.append(1)
        await asyncio.sleep(0.05)
        return TaskCreatedResponse.model_validate({"id": TASK_ID, "sessionId": TASK_ID})

    async def exercise() -> None:
        run: AsyncTaskRun[Any] = AsyncTaskRun(slow_create, FakeAsyncTasks(), interval=0)  # type: ignore[arg-type]
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(run, 0.01)
        await asyncio.gather(asyncio.ensure_future(run._wait_for_output()), asyncio.ensure_future(run._wait_for_output()))
        assert run.task_id == TASK_ID and len(creates) == 1

    asyncio.run(exercise())
