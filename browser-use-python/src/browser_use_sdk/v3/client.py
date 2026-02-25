from __future__ import annotations

import os
from collections.abc import Awaitable
from typing import Any

from .._core.http import AsyncHttpClient, SyncHttpClient
from .resources.sessions import AsyncSessions, Sessions
from .helpers import AsyncSessionRun, _poll_output
from ..generated.v3.models import SessionResponse

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
        output_schema: dict[str, Any] | None = None,
        **extra: Any,
    ) -> Any:
        """Run a task and block until complete. Returns the output."""
        data = self.sessions.create(
            task,
            model=model,
            keep_alive=keep_alive,
            max_cost_usd=max_cost_usd,
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            output_schema=output_schema,
            **extra,
        )
        return _poll_output(self.sessions, str(data.id))

    def close(self) -> None:
        """Close the underlying HTTP client."""
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

    def run(
        self,
        task: str,
        *,
        model: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        output_schema: dict[str, Any] | None = None,
        **extra: Any,
    ) -> AsyncSessionRun:
        """Run a task. Await the result for the output."""
        def create_fn() -> Awaitable[SessionResponse]:
            return self.sessions.create(
                task,
                model=model,
                keep_alive=keep_alive,
                max_cost_usd=max_cost_usd,
                profile_id=profile_id,
                proxy_country_code=proxy_country_code,
                output_schema=output_schema,
                **extra,
            )

        return AsyncSessionRun(create_fn, self.sessions)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()
