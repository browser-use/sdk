from __future__ import annotations

import time
import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..generated.v3.models import MessageResponse, SessionResponse
from .resources.sessions import AsyncSessions, Sessions

_TERMINAL_STATUSES = {"idle", "stopped", "timed_out", "error"}

T = TypeVar("T")


class SessionResult(Generic[T]):
    """Session result with typed output. All SessionResponse fields accessible directly."""

    session: SessionResponse
    output: T
    task_id: str | None

    def __init__(self, session: SessionResponse, output: T, task_id: str | None = None) -> None:
        self.session = session
        self.output = output
        self.task_id = task_id

    def __getattr__(self, name: str) -> Any:
        return getattr(self.session, name)

    def __repr__(self) -> str:
        extra = f", task_id={self.task_id!r}" if self.task_id else ""
        return f"SessionResult(id={self.session.id}, status={self.session.status.value}, output={self.output!r}{extra})"


def _parse_output(output: Any, output_schema: type[Any] | None) -> Any:
    """Parse raw output into the target type."""
    if output is None:
        return None
    if output_schema is not None and issubclass(output_schema, BaseModel):
        if isinstance(output, str):
            return output_schema.model_validate_json(output)
        return output_schema.model_validate(output)
    return output


def _poll_output(
    sessions: Sessions,
    session_id: str,
    output_schema: type[Any] | None = None,
    *,
    timeout: float = 14400,
    interval: float = 2,
) -> SessionResult[Any]:
    """Poll session status until terminal, return SessionResult."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        session = sessions.get(session_id)
        if session.status.value in _TERMINAL_STATUSES:
            return SessionResult(session, _parse_output(session.output, output_schema))
        time.sleep(interval)
    raise TimeoutError(f"Session {session_id} did not complete within {timeout}s")


async def _async_poll_output(
    sessions: AsyncSessions,
    session_id: str,
    output_schema: type[Any] | None = None,
    *,
    timeout: float = 14400,
    interval: float = 2,
) -> SessionResult[Any]:
    """Async poll session status until terminal, return SessionResult."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        session = await sessions.get(session_id)
        if session.status.value in _TERMINAL_STATUSES:
            return SessionResult(session, _parse_output(session.output, output_schema))
        await asyncio.sleep(interval)
    raise TimeoutError(f"Session {session_id} did not complete within {timeout}s")


class AsyncSessionRun(Generic[T]):
    """Lazy async session handle — awaitable, returns SessionResult on await."""

    def __init__(
        self,
        create_fn: Callable[[], Awaitable[SessionResponse]],
        sessions: AsyncSessions,
        output_schema: type[T] | None = None,
        *,
        timeout: float = 14400,
        interval: float = 2,
        _start_cursor: str | None = None,
        _start_cursor_ref: Callable[[], str | None] | None = None,
    ) -> None:
        self._create_fn = create_fn
        self._sessions = sessions
        self._output_schema = output_schema
        self._timeout = timeout
        self._interval = interval
        self._start_cursor = _start_cursor
        self._start_cursor_ref = _start_cursor_ref
        self.session_id: str | None = None
        self.result: SessionResult[T] | None = None
        self._cache_task_id: str | None = None  # Set by client when cache=True

    @property
    def output(self) -> T | None:
        """Final typed output (available after awaiting)."""
        return self.result.output if self.result else None

    async def _wait_for_output(self) -> SessionResult[T]:
        data = await self._create_fn()
        self.session_id = str(data.id)
        result = await _async_poll_output(
            self._sessions,
            self.session_id,
            self._output_schema,
            timeout=self._timeout,
            interval=self._interval,
        )
        if self._cache_task_id:
            result.task_id = self._cache_task_id
        self.result = result
        return result

    def __await__(self):
        return self._wait_for_output().__await__()

    async def __aiter__(self) -> AsyncIterator[MessageResponse]:
        """Yield new messages as they appear, then set .result when done.

        Usage::

            run = client.run("Find the top story on HN")
            async for msg in run:
                print(f"[{msg.role}] {msg.summary}")
            print(run.result.output)
        """
        data = await self._create_fn()
        self.session_id = str(data.id)
        # Resolve cursor: prefer the ref callback (set during create_fn) over static value
        cursor: str | None = self._start_cursor_ref() if self._start_cursor_ref else self._start_cursor
        deadline = time.monotonic() + self._timeout

        while time.monotonic() < deadline:
            resp = await self._sessions.messages(self.session_id, after=cursor, limit=100)
            for msg in resp.messages:
                yield msg
                cursor = str(msg.id)

            session = await self._sessions.get(self.session_id)
            if session.status.value in _TERMINAL_STATUSES:
                # Drain all remaining messages (may be multiple pages)
                while True:
                    resp = await self._sessions.messages(self.session_id, after=cursor, limit=100)
                    if not resp.messages:
                        break
                    for msg in resp.messages:
                        yield msg
                        cursor = str(msg.id)
                self.result = SessionResult(session, _parse_output(session.output, self._output_schema), task_id=self._cache_task_id)
                return

            await asyncio.sleep(self._interval)

        raise TimeoutError(f"Session {self.session_id} did not complete within {self._timeout}s")


class SessionStream(Generic[T]):
    """Sync iterator that yields new messages as they appear.

    Usage::

        stream = client.stream("Find the top story on HN")
        for msg in stream:
            print(f"[{msg.role}] {msg.summary}")
        print(stream.result.output)
    """

    def __init__(
        self,
        session: SessionResponse,
        sessions: Sessions,
        output_schema: type[T] | None = None,
        *,
        timeout: float = 14400,
        interval: float = 2,
        _start_cursor: str | None = None,
    ) -> None:
        self.session_id = str(session.id)
        self._sessions = sessions
        self._output_schema = output_schema
        self._timeout = timeout
        self._interval = interval
        self._start_cursor = _start_cursor
        self.result: SessionResult[T] | None = None

    @property
    def output(self) -> T | None:
        """Final typed output (available after iteration completes)."""
        return self.result.output if self.result else None

    def __iter__(self) -> Iterator[MessageResponse]:
        cursor: str | None = self._start_cursor
        deadline = time.monotonic() + self._timeout

        while time.monotonic() < deadline:
            resp = self._sessions.messages(self.session_id, after=cursor, limit=100)
            for msg in resp.messages:
                yield msg
                cursor = str(msg.id)

            session = self._sessions.get(self.session_id)
            if session.status.value in _TERMINAL_STATUSES:
                while True:
                    resp = self._sessions.messages(self.session_id, after=cursor, limit=100)
                    if not resp.messages:
                        break
                    for msg in resp.messages:
                        yield msg
                        cursor = str(msg.id)
                self.result = SessionResult(session, _parse_output(session.output, self._output_schema))
                return

            time.sleep(self._interval)

        raise TimeoutError(f"Session {self.session_id} did not complete within {self._timeout}s")
