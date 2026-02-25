from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..generated.v2.models import TaskCreatedResponse, TaskStepView, TaskView
from .resources.tasks import AsyncTasks, Tasks

TERMINAL_STATUSES = {"finished", "stopped"}

T = TypeVar("T")


class TaskResult(Generic[T]):
    """Task result with typed output. All TaskView fields accessible directly (e.g. result.id, result.steps)."""

    task: TaskView
    output: T

    def __init__(self, task: TaskView, output: T) -> None:
        self.task = task
        self.output = output

    def __getattr__(self, name: str) -> Any:
        return getattr(self.task, name)

    def __repr__(self) -> str:
        return f"TaskResult(id={self.task.id}, status={self.task.status.value}, output={self.output!r})"


def _parse_output(output: str | None, output_schema: type[Any] | None) -> Any:
    """Parse raw output string into the target type."""
    if output is None:
        return None
    if output_schema is not None and issubclass(output_schema, BaseModel):
        return output_schema.model_validate_json(output)
    return output


def _poll_output(
    tasks: Tasks,
    task_id: str,
    output_schema: type[Any] | None,
    *,
    timeout: float = 300,
    interval: float = 2,
) -> TaskResult[Any]:
    """Poll lightweight status endpoint until terminal, return TaskResult."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = tasks.status(task_id)
        if status.status.value in TERMINAL_STATUSES:
            result = tasks.get(task_id)
            return TaskResult(result, _parse_output(result.output, output_schema))
        time.sleep(interval)
    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")


async def _async_poll_output(
    tasks: AsyncTasks,
    task_id: str,
    output_schema: type[Any] | None,
    *,
    timeout: float = 300,
    interval: float = 2,
) -> TaskResult[Any]:
    """Poll lightweight status endpoint until terminal, return TaskResult."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = await tasks.status(task_id)
        if status.status.value in TERMINAL_STATUSES:
            result = await tasks.get(task_id)
            return TaskResult(result, _parse_output(result.output, output_schema))
        await asyncio.sleep(interval)
    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")


class TaskStream(Generic[T]):
    """Iterable that polls the full task and yields new steps as they appear.

    After iteration, ``.result`` contains the ``TaskResult``.

    Usage::

        for step in client.stream("Go to google.com"):
            print(f"[{step.number}] {step.next_goal}")
    """

    def __init__(
        self,
        data: TaskCreatedResponse,
        tasks: Tasks,
        output_schema: type[T] | None = None,
        *,
        timeout: float = 300,
        interval: float = 2,
    ) -> None:
        self.task_id = str(data.id)
        self._tasks = tasks
        self._output_schema = output_schema
        self._timeout = timeout
        self._interval = interval
        self.result: TaskResult[T] | None = None

    @property
    def output(self) -> T | None:
        """Final typed output (available after iteration completes)."""
        return self.result.output if self.result else None

    def __iter__(self) -> Iterator[TaskStepView]:
        seen = 0
        deadline = time.monotonic() + self._timeout

        while time.monotonic() < deadline:
            task = self._tasks.get(self.task_id)

            for i in range(seen, len(task.steps)):
                yield task.steps[i]
            seen = len(task.steps)

            if task.status.value in TERMINAL_STATUSES:
                self.result = TaskResult(task, _parse_output(task.output, self._output_schema))
                return

            time.sleep(self._interval)

        raise TimeoutError(
            f"Task {self.task_id} did not complete within {self._timeout}s"
        )


class AsyncTaskRun(Generic[T]):
    """Lazy async task handle returned by ``client.run()``.

    - ``await client.run(...)`` polls the lightweight status endpoint, returns a ``TaskResult``.
    - ``async for step in client.run(...)`` polls the full task, yields new steps.

    Usage::

        # Simple
        result = await client.run("Find the top HN post")
        print(result.output)

        # Step-by-step
        async for step in client.run("Go to google.com"):
            print(f"[{step.number}] {step.next_goal}")
    """

    def __init__(
        self,
        create_fn: Callable[[], Awaitable[TaskCreatedResponse]],
        tasks: AsyncTasks,
        output_schema: type[T] | None = None,
        *,
        timeout: float = 300,
        interval: float = 2,
    ) -> None:
        self._create_fn = create_fn
        self._tasks = tasks
        self._output_schema = output_schema
        self._timeout = timeout
        self._interval = interval
        self._task_id: str | None = None
        self.result: TaskResult[T] | None = None

    @property
    def task_id(self) -> str | None:
        """Task ID (available after creation resolves)."""
        return self._task_id

    @property
    def output(self) -> T | None:
        """Final typed output (available after awaiting or iterating to completion)."""
        return self.result.output if self.result else None

    async def _ensure_task_id(self) -> str:
        if self._task_id is None:
            data: TaskCreatedResponse = await self._create_fn()
            self._task_id = str(data.id)
        return self._task_id

    def __await__(self):  # type: ignore[override]
        return self._wait_for_output().__await__()

    async def _wait_for_output(self) -> TaskResult[T]:
        task_id = await self._ensure_task_id()
        result = await _async_poll_output(
            self._tasks,
            task_id,
            self._output_schema,
            timeout=self._timeout,
            interval=self._interval,
        )
        self.result = result
        return result

    async def __aiter__(self) -> AsyncIterator[TaskStepView]:
        task_id = await self._ensure_task_id()
        seen = 0
        deadline = time.monotonic() + self._timeout

        while time.monotonic() < deadline:
            task = await self._tasks.get(task_id)

            for i in range(seen, len(task.steps)):
                yield task.steps[i]
            seen = len(task.steps)

            if task.status.value in TERMINAL_STATUSES:
                self.result = TaskResult(task, _parse_output(task.output, self._output_schema))
                return

            await asyncio.sleep(self._interval)

        raise TimeoutError(
            f"Task {task_id} did not complete within {self._timeout}s"
        )
