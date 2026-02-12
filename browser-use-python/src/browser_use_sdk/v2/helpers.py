from __future__ import annotations

import json
import time
import asyncio
from typing import Generator, AsyncGenerator, Generic, Optional, Type, TypeVar, overload

from pydantic import BaseModel

from ..generated.v2.models import TaskCreatedResponse, TaskStatusView, TaskView
from .resources.tasks import AsyncTasks, Tasks

_TERMINAL_STATUSES = {"finished", "stopped", "failed"}

T = TypeVar("T")


class TaskHandle(Generic[T]):
    """Wraps a created task and provides polling helpers.

    When created with an ``output_schema`` (a Pydantic BaseModel subclass),
    :meth:`parse_output` will deserialise the task's ``output`` string into
    a typed model instance.
    """

    def __init__(
        self,
        data: TaskCreatedResponse,
        tasks: Tasks,
        output_schema: Optional[Type[T]] = None,
    ) -> None:
        self.data = data
        self._tasks = tasks
        self._output_schema = output_schema

    @property
    def id(self) -> str:
        return str(self.data.id)

    def complete(self, *, timeout: float = 300, interval: float = 3) -> TaskView:
        """Poll until the task reaches a terminal status, then return the full TaskView.

        Uses the lightweight status endpoint for polling.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = self._tasks.status(self.id)
            if status.status in _TERMINAL_STATUSES:
                return self._tasks.get(self.id)
            time.sleep(interval)
        raise TimeoutError(f"Task {self.id} did not complete within {timeout}s")

    def stream(self, *, interval: float = 3) -> Generator[TaskStatusView, None, None]:
        """Yield lightweight task status on each poll until terminal."""
        while True:
            status = self._tasks.status(self.id)
            yield status
            if status.status in _TERMINAL_STATUSES:
                return
            time.sleep(interval)

    def parse_output(self, result: TaskView) -> Optional[T]:
        """Parse the task's output string using the structured output schema.

        Returns ``None`` if the task has no output. If no ``output_schema``
        was provided, returns the raw output string.

        Args:
            result: A TaskView (from complete() or tasks.get()).

        Returns:
            Parsed model instance, raw string, or None.
        """
        if result.output is None:
            return None
        if self._output_schema is not None and issubclass(self._output_schema, BaseModel):
            return self._output_schema.model_validate_json(result.output)  # type: ignore[return-value]
        return result.output  # type: ignore[return-value]


class AsyncTaskHandle(Generic[T]):
    """Async variant of TaskHandle."""

    def __init__(
        self,
        data: TaskCreatedResponse,
        tasks: AsyncTasks,
        output_schema: Optional[Type[T]] = None,
    ) -> None:
        self.data = data
        self._tasks = tasks
        self._output_schema = output_schema

    @property
    def id(self) -> str:
        return str(self.data.id)

    async def complete(self, *, timeout: float = 300, interval: float = 3) -> TaskView:
        """Poll until the task reaches a terminal status, then return the full TaskView.

        Uses the lightweight status endpoint for polling.
        """
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            status = await self._tasks.status(self.id)
            if status.status in _TERMINAL_STATUSES:
                return await self._tasks.get(self.id)
            await asyncio.sleep(interval)
        raise TimeoutError(f"Task {self.id} did not complete within {timeout}s")

    async def stream(self, *, interval: float = 3) -> AsyncGenerator[TaskStatusView, None]:
        """Yield lightweight task status on each poll until terminal."""
        while True:
            status = await self._tasks.status(self.id)
            yield status
            if status.status in _TERMINAL_STATUSES:
                return
            await asyncio.sleep(interval)

    def parse_output(self, result: TaskView) -> Optional[T]:
        """Parse the task's output string using the structured output schema.

        Returns ``None`` if the task has no output. If no ``output_schema``
        was provided, returns the raw output string.

        Args:
            result: A TaskView (from complete() or tasks.get()).

        Returns:
            Parsed model instance, raw string, or None.
        """
        if result.output is None:
            return None
        if self._output_schema is not None and issubclass(self._output_schema, BaseModel):
            return self._output_schema.model_validate_json(result.output)  # type: ignore[return-value]
        return result.output  # type: ignore[return-value]
