from __future__ import annotations

import time
import asyncio
from collections.abc import Awaitable, Callable

from ..generated.v3.models import SessionResponse
from .resources.sessions import AsyncSessions, Sessions

_TERMINAL_STATUSES = {"idle", "stopped", "timed_out", "error"}


def _poll_output(
    sessions: Sessions,
    session_id: str,
    *,
    timeout: float = 300,
    interval: float = 2,
) -> str | None:
    """Poll session status until terminal, return output."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        session = sessions.get(session_id)
        if session.status.value in _TERMINAL_STATUSES:
            return session.output
        time.sleep(interval)
    raise TimeoutError(f"Session {session_id} did not complete within {timeout}s")


async def _async_poll_output(
    sessions: AsyncSessions,
    session_id: str,
    *,
    timeout: float = 300,
    interval: float = 2,
) -> str | None:
    """Async poll session status until terminal, return output."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        session = await sessions.get(session_id)
        if session.status.value in _TERMINAL_STATUSES:
            return session.output
        await asyncio.sleep(interval)
    raise TimeoutError(f"Session {session_id} did not complete within {timeout}s")


class AsyncSessionRun:
    """Lazy async session handle — awaitable, returns output on await."""

    def __init__(
        self,
        create_fn: Callable[[], Awaitable[SessionResponse]],
        sessions: AsyncSessions,
        *,
        timeout: float = 300,
        interval: float = 2,
    ) -> None:
        self._create_fn = create_fn
        self._sessions = sessions
        self._timeout = timeout
        self._interval = interval
        self.session_id: str | None = None
        self.result: SessionResponse | None = None

    async def _wait_for_output(self) -> str | None:
        data = await self._create_fn()
        self.session_id = str(data.id)
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            session = await self._sessions.get(self.session_id)
            if session.status.value in _TERMINAL_STATUSES:
                self.result = session
                return session.output
            await asyncio.sleep(self._interval)
        raise TimeoutError(
            f"Session {self.session_id} did not complete within {self._timeout}s"
        )

    def __await__(self):
        return self._wait_for_output().__await__()
