from __future__ import annotations

import os
from typing import Any

from .._core.http import AsyncHttpClient, SyncHttpClient
from .resources.sessions import AsyncSessions, Sessions
from .helpers import AsyncSessionHandle, SessionHandle

_V3_BASE_URL = "https://api.browser-use.com/api/v3"


class BrowserUse:
    """Synchronous Browser Use v3 client."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
            )
        self._http = SyncHttpClient(
            base_url=base_url or _V3_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.sessions = Sessions(self._http)

    def run(
        self,
        task: str,
        *,
        model: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        **extra: Any,
    ) -> SessionHandle:
        """Create a session and return a SessionHandle for polling/streaming.

        Example::

            handle = client.run("Find the top HN post")
            result = handle.complete()
        """
        data = self.sessions.create(
            task,
            model=model,
            keep_alive=keep_alive,
            max_cost_usd=max_cost_usd,
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            **extra,
        )
        return SessionHandle(data, self.sessions)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> BrowserUse:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncBrowserUse:
    """Asynchronous Browser Use v3 client."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
            )
        self._http = AsyncHttpClient(
            base_url=base_url or _V3_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.sessions = AsyncSessions(self._http)

    async def run(
        self,
        task: str,
        *,
        model: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        **extra: Any,
    ) -> AsyncSessionHandle:
        """Create a session and return an AsyncSessionHandle for polling/streaming.

        Example::

            handle = await client.run("Find the top HN post")
            result = await handle.complete()
        """
        data = await self.sessions.create(
            task,
            model=model,
            keep_alive=keep_alive,
            max_cost_usd=max_cost_usd,
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            **extra,
        )
        return AsyncSessionHandle(data, self.sessions)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncBrowserUse:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
