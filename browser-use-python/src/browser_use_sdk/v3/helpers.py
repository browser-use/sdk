from __future__ import annotations

import time
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..generated.v3.models import SessionResponse
from .resources.sessions import AsyncSessions, Sessions

_TERMINAL_STATUSES = {"idle", "stopped", "timed_out", "error"}

T = TypeVar("T")


class SessionResult(Generic[T]):
    """Session result with typed output. All SessionResponse fields accessible directly."""

    session: SessionResponse
    output: T

    def __init__(self, session: SessionResponse, output: T) -> None:
        self.session = session
        self.output = output

    def __getattr__(self, name: str) -> Any:
        return getattr(self.session, name)

    def __repr__(self) -> str:
        return f"SessionResult(id={self.session.id}, status={self.session.status.value}, output={self.output!r})"


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
    timeout: float = 300,
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
    timeout: float = 300,
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
        timeout: float = 300,
        interval: float = 2,
    ) -> None:
        self._create_fn = create_fn
        self._sessions = sessions
        self._output_schema = output_schema
        self._timeout = timeout
        self._interval = interval
        self.session_id: str | None = None
        self.result: SessionResult[T] | None = None

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
        self.result = result
        return result

    def __await__(self):
        return self._wait_for_output().__await__()
