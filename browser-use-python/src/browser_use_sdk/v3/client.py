from __future__ import annotations

import os
from collections.abc import Awaitable
from typing import Any, TypeVar, overload
from uuid import UUID

from pydantic import BaseModel

from .._core import _UNSET
from .._core.http import AsyncHttpClient, SyncHttpClient
from .._core.x402 import X402_BASE_URL_DEFAULT, x402_client_from_private_key
from .resources.billing import AsyncBilling, Billing as BillingResource
from .resources.browsers import AsyncBrowsers, Browsers as BrowsersResource
from .resources.profiles import AsyncProfiles, Profiles as ProfilesResource
from .resources.sessions import AsyncSessions, Sessions
from .resources.workspaces import AsyncWorkspaces, Workspaces
from .helpers import AsyncSessionRun, SessionResult, SessionStream, _poll_output
from ..generated.v3.models import SessionResponse

_V3_BASE_URL = "https://api.browser-use.com/api/v3"

T = TypeVar("T")


def _resolve_x402(x402: Any | None, x402_private_key: str | None) -> Any | None:
    """Resolve x402 client from explicit args + env vars. Returns None if unused."""
    if x402 is not None:
        return x402
    key = x402_private_key or os.environ.get("BROWSER_USE_X402_PRIVATE_KEY")
    if key:
        return x402_client_from_private_key(key)
    return None


class BrowserUse:
    """Synchronous Browser Use v3 client.

    For x402 (pay-per-request) authentication, use :class:`AsyncBrowserUse` —
    x402 settlement is async-only.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        x402: Any | None = None,
        x402_private_key: str | None = None,
    ) -> None:
        if x402 is not None or x402_private_key is not None or os.environ.get("BROWSER_USE_X402_PRIVATE_KEY"):
            raise ValueError(
                "x402 mode is async-only. Use AsyncBrowserUse instead of BrowserUse "
                "(or remove x402 / x402_private_key / BROWSER_USE_X402_PRIVATE_KEY)."
            )
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
        self.billing = BillingResource(self._http)
        self.browsers = BrowsersResource(self._http)
        self.profiles = ProfilesResource(self._http)
        self.sessions = Sessions(self._http)
        self.workspaces = Workspaces(self._http)

    @overload
    def run(
        self,
        task: str,
        *,
        schema: type[T],
        model: str | None = ...,
        session_id: str | UUID | None = ...,
        keep_alive: bool | None = ...,
        max_cost_usd: float | None = ...,
        profile_id: str | None = ...,
        proxy_country_code: str | None = ...,
        workspace_id: str | None = ...,
        sensitive_data: dict[str, str] | None = ...,
        enable_recording: bool | None = ...,
        cache_script: bool | None = ...,
        code_mode: bool | None = ...,
        use_own_key: bool | None = ...,
        **extra: Any,
    ) -> SessionResult[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        output_schema: type[T],
        model: str | None = ...,
        session_id: str | UUID | None = ...,
        keep_alive: bool | None = ...,
        max_cost_usd: float | None = ...,
        profile_id: str | None = ...,
        proxy_country_code: str | None = ...,
        workspace_id: str | None = ...,
        sensitive_data: dict[str, str] | None = ...,
        enable_recording: bool | None = ...,
        cache_script: bool | None = ...,
        code_mode: bool | None = ...,
        use_own_key: bool | None = ...,
        **extra: Any,
    ) -> SessionResult[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        model: str | None = ...,
        session_id: str | UUID | None = ...,
        keep_alive: bool | None = ...,
        max_cost_usd: float | None = ...,
        profile_id: str | None = ...,
        proxy_country_code: str | None = ...,
        workspace_id: str | None = ...,
        sensitive_data: dict[str, str] | None = ...,
        enable_recording: bool | None = ...,
        cache_script: bool | None = ...,
        code_mode: bool | None = ...,
        use_own_key: bool | None = ...,
        **extra: Any,
    ) -> SessionResult[str]: ...

    def run(
        self,
        task: str,
        *,
        schema: type[Any] | None = None,
        output_schema: type[Any] | None = None,
        model: str | None = None,
        session_id: str | UUID | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        workspace_id: str | None = None,
        sensitive_data: dict[str, str] | None = None,
        enable_recording: bool | None = None,
        cache_script: bool | None = None,
        code_mode: bool | None = None,
        use_own_key: bool | None = None,
        **extra: Any,
    ) -> Any:
        """Run a task and block until complete. Returns a SessionResult.

        Script caching (cache_script):
        - None (default): auto-detected. If the task contains @{{value}} brackets
          and a workspace is attached, caching is enabled automatically.
        - True: force-enable caching (even without brackets).
        - False: force-disable caching.

        When active, the first call runs the full agent and saves a reusable script.
        Subsequent calls with the same task template execute the script with $0 LLM cost.
        """
        if cache_script is True and not workspace_id:
            raise ValueError("workspace_id is required when cache_script=True")

        resolved_schema = schema or output_schema
        schema_dict: dict[str, Any] | None = None
        if resolved_schema is not None:
            if not issubclass(resolved_schema, BaseModel):
                raise TypeError(
                    "output_schema must be a Pydantic BaseModel subclass, "
                    f"got {resolved_schema!r}"
                )
            schema_dict = resolved_schema.model_json_schema()

        # Auto keep_alive when dispatching to an existing session
        if session_id is not None and keep_alive is None:
            keep_alive = True

        data = self.sessions.create(
            task,
            model=model,
            session_id=session_id,
            keep_alive=keep_alive,
            max_cost_usd=max_cost_usd,
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            output_schema=schema_dict,
            workspace_id=workspace_id,
            sensitive_data=sensitive_data,
            enable_recording=enable_recording,
            cache_script=cache_script,
            code_mode=code_mode,
            use_own_key=use_own_key,
            **extra,
        )
        return _poll_output(self.sessions, str(data.id), resolved_schema)

    def stream(
        self,
        task: str,
        *,
        schema: type[Any] | None = None,
        output_schema: type[Any] | None = None,
        model: str | None = None,
        session_id: str | UUID | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        workspace_id: str | None = None,
        sensitive_data: dict[str, str] | None = None,
        enable_recording: bool | None = None,
        cache_script: bool | None = None,
        code_mode: bool | None = None,
        use_own_key: bool | None = None,
        **extra: Any,
    ) -> SessionStream[Any]:
        """Run a task and yield messages as they happen.

        Usage::

            stream = client.stream("Find the top story on HN")
            for msg in stream:
                print(f"[{msg.role}] {msg.summary}")
            print(stream.result.output)
        """
        if cache_script is True and not workspace_id:
            raise ValueError("workspace_id is required when cache_script=True")

        resolved_schema = schema or output_schema
        schema_dict: dict[str, Any] | None = None
        if resolved_schema is not None:
            if not issubclass(resolved_schema, BaseModel):
                raise TypeError(
                    "output_schema must be a Pydantic BaseModel subclass, "
                    f"got {resolved_schema!r}"
                )
            schema_dict = resolved_schema.model_json_schema()

        if session_id is not None and keep_alive is None:
            keep_alive = True

        # For follow-up runs, snapshot the latest message cursor so the
        # stream skips messages from previous tasks on this session.
        start_cursor: str | None = None
        if session_id is not None:
            resp = self.sessions.messages(session_id, limit=1)
            if resp.messages:
                start_cursor = str(resp.messages[-1].id)

        data = self.sessions.create(
            task,
            model=model,
            session_id=session_id,
            keep_alive=keep_alive,
            max_cost_usd=max_cost_usd,
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            output_schema=schema_dict,
            workspace_id=workspace_id,
            sensitive_data=sensitive_data,
            enable_recording=enable_recording,
            cache_script=cache_script,
            code_mode=code_mode,
            use_own_key=use_own_key,
            **extra,
        )
        return SessionStream(data, self.sessions, resolved_schema, _start_cursor=start_cursor)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> BrowserUse:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncBrowserUse:
    """Asynchronous Browser Use v3 client.

    Auth priority: ``x402`` arg → ``x402_private_key`` arg →
    ``BROWSER_USE_X402_PRIVATE_KEY`` env → ``api_key`` arg → ``BROWSER_USE_API_KEY``
    env. When both an API key and x402 are configured, x402 mode is used in
    "top-up" mode — the API key is forwarded as a header so the backend
    credits the existing project (instead of auto-creating a wallet-keyed one).
    x402 mode requires the optional extra: ``pip install "browser-use-sdk[x402]"``.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        x402: Any | None = None,
        x402_private_key: str | None = None,
    ) -> None:
        x402_client = _resolve_x402(x402, x402_private_key)
        if x402_client is not None:
            topup_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
            self._http = AsyncHttpClient(
                base_url=base_url or X402_BASE_URL_DEFAULT,
                api_key=topup_key,
                timeout=timeout,
                x402_client=x402_client,
            )
        else:
            resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
            if not resolved_key:
                raise ValueError(
                    "No credentials provided. Pass api_key / set BROWSER_USE_API_KEY, "
                    "or pass x402_private_key / set BROWSER_USE_X402_PRIVATE_KEY for "
                    "pay-per-request access via USDC."
                )
            self._http = AsyncHttpClient(
                base_url=base_url or _V3_BASE_URL,
                api_key=resolved_key,
                timeout=timeout,
            )
        self.billing = AsyncBilling(self._http)
        self.browsers = AsyncBrowsers(self._http)
        self.profiles = AsyncProfiles(self._http)
        self.sessions = AsyncSessions(self._http)
        self.workspaces = AsyncWorkspaces(self._http)

    @overload
    def run(
        self,
        task: str,
        *,
        schema: type[T],
        model: str | None = ...,
        session_id: str | UUID | None = ...,
        keep_alive: bool | None = ...,
        max_cost_usd: float | None = ...,
        profile_id: str | None = ...,
        proxy_country_code: str | None = ...,
        workspace_id: str | None = ...,
        sensitive_data: dict[str, str] | None = ...,
        enable_recording: bool | None = ...,
        cache_script: bool | None = ...,
        code_mode: bool | None = ...,
        use_own_key: bool | None = ...,
        **extra: Any,
    ) -> AsyncSessionRun[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        output_schema: type[T],
        model: str | None = ...,
        session_id: str | UUID | None = ...,
        keep_alive: bool | None = ...,
        max_cost_usd: float | None = ...,
        profile_id: str | None = ...,
        proxy_country_code: str | None = ...,
        workspace_id: str | None = ...,
        sensitive_data: dict[str, str] | None = ...,
        enable_recording: bool | None = ...,
        cache_script: bool | None = ...,
        code_mode: bool | None = ...,
        use_own_key: bool | None = ...,
        **extra: Any,
    ) -> AsyncSessionRun[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        model: str | None = ...,
        session_id: str | UUID | None = ...,
        keep_alive: bool | None = ...,
        max_cost_usd: float | None = ...,
        profile_id: str | None = ...,
        proxy_country_code: str | None = ...,
        workspace_id: str | None = ...,
        sensitive_data: dict[str, str] | None = ...,
        enable_recording: bool | None = ...,
        cache_script: bool | None = ...,
        code_mode: bool | None = ...,
        use_own_key: bool | None = ...,
        **extra: Any,
    ) -> AsyncSessionRun[str]: ...

    def run(
        self,
        task: str,
        *,
        schema: type[Any] | None = None,
        output_schema: type[Any] | None = None,
        model: str | None = None,
        session_id: str | UUID | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        workspace_id: str | None = None,
        sensitive_data: dict[str, str] | None = None,
        enable_recording: bool | None = None,
        cache_script: bool | None = None,
        code_mode: bool | None = None,
        use_own_key: bool | None = None,
        **extra: Any,
    ) -> AsyncSessionRun[Any]:
        """Run a task. Await the result for a SessionResult.

        Script caching (cache_script):
        - None (default): auto-detected. If the task contains @{{value}} brackets
          and a workspace is attached, caching is enabled automatically.
        - True: force-enable caching (even without brackets).
        - False: force-disable caching.

        When active, the first call runs the full agent and saves a reusable script.
        Subsequent calls with the same task template execute the script with $0 LLM cost.
        """
        if cache_script is True and not workspace_id:
            raise ValueError("workspace_id is required when cache_script=True")

        resolved_schema = schema or output_schema
        schema_dict: dict[str, Any] | None = None
        if resolved_schema is not None:
            if not issubclass(resolved_schema, BaseModel):
                raise TypeError(
                    "output_schema must be a Pydantic BaseModel subclass, "
                    f"got {resolved_schema!r}"
                )
            schema_dict = resolved_schema.model_json_schema()

        # Auto keep_alive when dispatching to an existing session
        effective_keep_alive = keep_alive
        if session_id is not None and keep_alive is None:
            effective_keep_alive = True

        # For follow-up runs, snapshot the latest message cursor so the
        # iterator skips messages from previous tasks on this session.
        start_cursor: str | None = None

        async def create_fn() -> SessionResponse:
            nonlocal start_cursor
            if session_id is not None:
                resp = await self.sessions.messages(str(session_id), limit=1)
                if resp.messages:
                    start_cursor = str(resp.messages[-1].id)
            return await self.sessions.create(
                task,
                model=model,
                session_id=session_id,
                keep_alive=effective_keep_alive,
                max_cost_usd=max_cost_usd,
                profile_id=profile_id,
                proxy_country_code=proxy_country_code,
                output_schema=schema_dict,
                workspace_id=workspace_id,
                sensitive_data=sensitive_data,
                enable_recording=enable_recording,
                cache_script=cache_script,
                code_mode=code_mode,
                use_own_key=use_own_key,
                **extra,
            )

        return AsyncSessionRun(create_fn, self.sessions, resolved_schema, _start_cursor_ref=lambda: start_cursor)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()
