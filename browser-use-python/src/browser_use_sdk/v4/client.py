from __future__ import annotations

import os
import typing

from .._core.http import AsyncHttpClient, SyncHttpClient
from .resources.browsers import AsyncBrowsers, Browsers
from .resources.integrations import AsyncIntegrations, Integrations
from .resources.profiles import AsyncProfiles, Profiles
from .resources.extensions import AsyncExtensions, Extensions
from .resources.runs import AsyncRuns, Runs
from .resources.sessions import AsyncSessions, Sessions
from .resources.workspaces import AsyncWorkspaces, Workspaces

_V4_BASE_URL = "https://api.browser-use.com/api/v4"

# V2 client members that 3.x code reached through the root import.
_V2_ONLY = frozenset({"billing", "tasks", "files", "skills", "marketplace", "run", "stream"})


def _missing_attribute(obj: object, name: str) -> AttributeError:
    cls = type(obj).__name__
    if name in _V2_ONLY:
        return AttributeError(
            f"{cls!r} object has no attribute {name!r}: since browser-use-sdk 4.0.0 the root import is the V4 client. "
            f"For the V2 API use `from browser_use_sdk.v2 import {cls}`."
        )
    return AttributeError(f"{cls!r} object has no attribute {name!r}")


def _no_api_key() -> ValueError:
    message = "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
    if os.environ.get("BROWSER_USE_X402_PRIVATE_KEY"):
        message += " x402 payments are V2-only: use `from browser_use_sdk.v2 import BrowserUse`."
    return ValueError(message)


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
            raise _no_api_key()
        self._http = SyncHttpClient(
            base_url=base_url or _V4_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.browsers = Browsers(self._http)
        self.integrations = Integrations(self._http)
        self.profiles = Profiles(self._http)
        self.extensions = Extensions(self._http)
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

    if not typing.TYPE_CHECKING:  # Hidden from type checkers so they still flag unknown attributes.

        def __getattr__(self, name: str) -> object:
            raise _missing_attribute(self, name)


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
            raise _no_api_key()
        self._http = AsyncHttpClient(
            base_url=base_url or _V4_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
        )
        self.browsers = AsyncBrowsers(self._http)
        self.integrations = AsyncIntegrations(self._http)
        self.profiles = AsyncProfiles(self._http)
        self.extensions = AsyncExtensions(self._http)
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

    if not typing.TYPE_CHECKING:  # Hidden from type checkers so they still flag unknown attributes.

        def __getattr__(self, name: str) -> object:
            raise _missing_attribute(self, name)
