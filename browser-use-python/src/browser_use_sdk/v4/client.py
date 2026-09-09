from __future__ import annotations

import os

from .._core.http import AsyncHttpClient, SyncHttpClient
from .resources.browsers import AsyncBrowsers, Browsers
from .resources.runs import AsyncRuns, Runs
from .resources.sessions import AsyncSessions, Sessions
from .resources.workspaces import AsyncWorkspaces, Workspaces

_V4_BASE_URL = "https://api.browser-use.com/api/v4"


class BrowserUse:
    """Synchronous Browser Use v4 client.

    The v4 API is polling-first: create a run, then
    ``runs.wait_for_completion(run.id)`` polls the cheap status endpoint until
    the run is terminal and returns the full run summary.
    """

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
            base_url=base_url or _V4_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.browsers = Browsers(self._http)
        self.runs = Runs(self._http)
        self.sessions = Sessions(self._http)
        self.workspaces = Workspaces(self._http)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> BrowserUse:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncBrowserUse:
    """Asynchronous Browser Use v4 client.

    The v4 API is polling-first: create a run, then
    ``await runs.wait_for_completion(run.id)`` polls the cheap status endpoint
    until the run is terminal and returns the full run summary.
    """

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
            base_url=base_url or _V4_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.browsers = AsyncBrowsers(self._http)
        self.runs = AsyncRuns(self._http)
        self.sessions = AsyncSessions(self._http)
        self.workspaces = AsyncWorkspaces(self._http)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> AsyncBrowserUse:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
