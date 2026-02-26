from __future__ import annotations

from typing import Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v3.models import (
    FileListResponse,
    FileUploadItem,
    FileUploadResponse,
    SessionListResponse,
    SessionResponse,
)


class Sessions:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        task: str | None = None,
        *,
        model: str | None = None,
        session_id: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        output_schema: dict[str, Any] | None = None,
        **extra: Any,
    ) -> SessionResponse:
        """Create a session and optionally dispatch a task."""
        body: dict[str, Any] = {}
        if task is not None:
            body["task"] = task
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
        if output_schema is not None:
            body["outputSchema"] = output_schema
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

    def stop(self, session_id: str, *, strategy: str | None = None, **extra: Any) -> SessionResponse:
        """Stop a session or the running task."""
        body: dict[str, Any] | None = None
        if strategy is not None or extra:
            body = {}
            if strategy is not None:
                body["strategy"] = strategy
            body.update(extra)
        return SessionResponse.model_validate(
            self._http.request("POST", f"/sessions/{session_id}/stop", json=body)
        )

    def delete(self, session_id: str) -> None:
        """Soft-delete a session."""
        self._http.request("DELETE", f"/sessions/{session_id}")

    def upload_files(
        self,
        session_id: str,
        files: list[FileUploadItem],
        **extra: Any,
    ) -> FileUploadResponse:
        """Get presigned upload URLs for session files."""
        body: dict[str, Any] = {
            "files": [f.model_dump(by_alias=True, exclude_none=True) for f in files],
        }
        body.update(extra)
        return FileUploadResponse.model_validate(
            self._http.request("POST", f"/sessions/{session_id}/files/upload", json=body)
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
        task: str | None = None,
        *,
        model: str | None = None,
        session_id: str | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        output_schema: dict[str, Any] | None = None,
        **extra: Any,
    ) -> SessionResponse:
        """Create a session and optionally dispatch a task."""
        body: dict[str, Any] = {}
        if task is not None:
            body["task"] = task
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
        if output_schema is not None:
            body["outputSchema"] = output_schema
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

    async def stop(self, session_id: str, *, strategy: str | None = None, **extra: Any) -> SessionResponse:
        """Stop a session or the running task."""
        body: dict[str, Any] | None = None
        if strategy is not None or extra:
            body = {}
            if strategy is not None:
                body["strategy"] = strategy
            body.update(extra)
        return SessionResponse.model_validate(
            await self._http.request("POST", f"/sessions/{session_id}/stop", json=body)
        )

    async def delete(self, session_id: str) -> None:
        """Soft-delete a session."""
        await self._http.request("DELETE", f"/sessions/{session_id}")

    async def upload_files(
        self,
        session_id: str,
        files: list[FileUploadItem],
        **extra: Any,
    ) -> FileUploadResponse:
        """Get presigned upload URLs for session files."""
        body: dict[str, Any] = {
            "files": [f.model_dump(by_alias=True, exclude_none=True) for f in files],
        }
        body.update(extra)
        return FileUploadResponse.model_validate(
            await self._http.request("POST", f"/sessions/{session_id}/files/upload", json=body)
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
