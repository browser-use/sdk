from __future__ import annotations

from typing import Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v3.models import (
    FileListResponse,
    SessionListResponse,
    SessionResponse,
)


class Sessions:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        task: str,
        *,
        model: str | None = None,
        session_id: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        **extra: Any,
    ) -> SessionResponse:
        """Create a session and run a task."""
        body: dict[str, Any] = {"task": task}
        if model is not None:
            body["model"] = model
        if session_id is not None:
            body["sessionId"] = session_id
        if keep_alive is not None:
            body["keepAlive"] = keep_alive
        if max_cost_usd is not None:
            body["maxCostUsd"] = max_cost_usd
        if profile_id is not None:
            body["profileId"] = profile_id
        if proxy_country_code is not None:
            body["proxyCountryCode"] = proxy_country_code
        body.update(extra)
        return SessionResponse.model_validate(
            self._http.request("POST", "/sessions", json=body)
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> SessionListResponse:
        """List sessions for the authenticated project."""
        return SessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/sessions",
                params={
                    "page": page,
                    "page_size": page_size,
                },
            )
        )

    def get(self, session_id: str) -> SessionResponse:
        """Get session details."""
        return SessionResponse.model_validate(
            self._http.request("GET", f"/sessions/{session_id}")
        )

    def stop(self, session_id: str) -> SessionResponse:
        """Stop a session."""
        return SessionResponse.model_validate(
            self._http.request("POST", f"/sessions/{session_id}/stop")
        )

    def files(
        self,
        session_id: str,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
    ) -> FileListResponse:
        """List files in a session's workspace."""
        return FileListResponse.model_validate(
            self._http.request(
                "GET",
                f"/sessions/{session_id}/files",
                params={
                    "prefix": prefix,
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                },
            )
        )


class AsyncSessions:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        task: str,
        *,
        model: str | None = None,
        session_id: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        **extra: Any,
    ) -> SessionResponse:
        """Create a session and run a task."""
        body: dict[str, Any] = {"task": task}
        if model is not None:
            body["model"] = model
        if session_id is not None:
            body["sessionId"] = session_id
        if keep_alive is not None:
            body["keepAlive"] = keep_alive
        if max_cost_usd is not None:
            body["maxCostUsd"] = max_cost_usd
        if profile_id is not None:
            body["profileId"] = profile_id
        if proxy_country_code is not None:
            body["proxyCountryCode"] = proxy_country_code
        body.update(extra)
        return SessionResponse.model_validate(
            await self._http.request("POST", "/sessions", json=body)
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> SessionListResponse:
        """List sessions for the authenticated project."""
        return SessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/sessions",
                params={
                    "page": page,
                    "page_size": page_size,
                },
            )
        )

    async def get(self, session_id: str) -> SessionResponse:
        """Get session details."""
        return SessionResponse.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}")
        )

    async def stop(self, session_id: str) -> SessionResponse:
        """Stop a session."""
        return SessionResponse.model_validate(
            await self._http.request("POST", f"/sessions/{session_id}/stop")
        )

    async def files(
        self,
        session_id: str,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
    ) -> FileListResponse:
        """List files in a session's workspace."""
        return FileListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/sessions/{session_id}/files",
                params={
                    "prefix": prefix,
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                },
            )
        )
