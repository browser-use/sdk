from __future__ import annotations

import time
import asyncio
from typing import Generator, AsyncGenerator

from ..generated.v3.models import SessionResponse
from .resources.sessions import AsyncSessions, Sessions

_TERMINAL_STATUSES = {"stopped", "timed_out", "error"}
_IDLE_OR_TERMINAL = _TERMINAL_STATUSES | {"idle"}


class SessionHandle:
    """Wraps a created v3 session and provides polling helpers."""

    def __init__(self, data: SessionResponse, sessions: Sessions) -> None:
        self.data = data
        self._sessions = sessions

    @property
    def id(self) -> str:
        return str(self.data.id)

    def complete(self, *, timeout: float = 300, interval: float = 3) -> SessionResponse:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = self._sessions.get(self.id)
            if result.status in _IDLE_OR_TERMINAL:
                return result
            time.sleep(interval)
        raise TimeoutError(f"Session {self.id} did not complete within {timeout}s")

    def stream(self, *, interval: float = 3) -> Generator[SessionResponse, None, None]:
        while True:
            result = self._sessions.get(self.id)
            yield result
            if result.status in _IDLE_OR_TERMINAL:
                return
            time.sleep(interval)


class AsyncSessionHandle:
    """Async variant of SessionHandle."""

    def __init__(self, data: SessionResponse, sessions: AsyncSessions) -> None:
        self.data = data
        self._sessions = sessions

    @property
    def id(self) -> str:
        return str(self.data.id)

    async def complete(self, *, timeout: float = 300, interval: float = 3) -> SessionResponse:
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            result = await self._sessions.get(self.id)
            if result.status in _IDLE_OR_TERMINAL:
                return result
            await asyncio.sleep(interval)
        raise TimeoutError(f"Session {self.id} did not complete within {timeout}s")

    async def stream(self, *, interval: float = 3) -> AsyncGenerator[SessionResponse, None]:
        while True:
            result = await self._sessions.get(self.id)
            yield result
            if result.status in _IDLE_OR_TERMINAL:
                return
            await asyncio.sleep(interval)
