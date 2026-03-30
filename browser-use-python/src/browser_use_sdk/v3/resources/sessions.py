from __future__ import annotations

import asyncio
import time
from typing import Any
from uuid import UUID

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v3.models import (
    FileListResponse,
    FileUploadItem,
    FileUploadResponse,
    MessageListResponse,
    SessionListResponse,
    SessionResponse,
)

# Accept both str and UUID for session IDs
_ID = str | UUID


class Sessions:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        task: str | None = None,
        *,
        model: str | None = None,
        session_id: _ID | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        output_schema: dict[str, Any] | None = None,
        workspace_id: str | None = None,
        enable_scheduled_tasks: bool | None = None,
        enable_recording: bool | None = None,
        **extra: Any,
    ) -> SessionResponse:
        """Create a session and optionally dispatch a task."""
        body: dict[str, Any] = {}
        if task is not None:
            body["task"] = task
        if model is not None:
            body["model"] = model
        if session_id is not None:
            body["sessionId"] = str(session_id)
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
        if workspace_id is not None:
            body["workspaceId"] = workspace_id
        if enable_scheduled_tasks is not None:
            body["enableScheduledTasks"] = enable_scheduled_tasks
        if enable_recording is not None:
            body["enableRecording"] = enable_recording
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

    def get(self, session_id: _ID) -> SessionResponse:
        """Get session details."""
        return SessionResponse.model_validate(
            self._http.request("GET", f"/sessions/{session_id}")
        )

    def stop(self, session_id: _ID, *, strategy: str | None = None, **extra: Any) -> SessionResponse:
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

    def delete(self, session_id: _ID) -> None:
        """Soft-delete a session."""
        self._http.request("DELETE", f"/sessions/{session_id}")

    def upload_files(
        self,
        session_id: _ID,
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
        session_id: _ID,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
        shallow: bool | None = None,
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
                    "shallow": shallow,
                },
            )
        )

    def messages(
        self,
        session_id: _ID,
        *,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> MessageListResponse:
        """List messages for a session with cursor-based pagination."""
        return MessageListResponse.model_validate(
            self._http.request(
                "GET",
                f"/sessions/{session_id}/messages",
                params={
                    "after": after,
                    "before": before,
                    "limit": limit,
                },
            )
        )

    def wait_for_recording(
        self,
        session_id: _ID,
        *,
        timeout: float = 15,
        interval: float = 2,
    ) -> list[str]:
        """Poll until recording URLs are available. Returns a list of presigned MP4 URLs.

        Returns an empty list if no recording was produced (e.g. the agent
        answered without opening a browser, or recording was not enabled).
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            session = self.get(session_id)
            if session.recording_urls:
                return list(session.recording_urls)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(interval, remaining))
        return []


class AsyncSessions:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        task: str | None = None,
        *,
        model: str | None = None,
        session_id: _ID | None = None,
        keep_alive: bool | None = None,
        max_cost_usd: float | None = None,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        output_schema: dict[str, Any] | None = None,
        workspace_id: str | None = None,
        enable_scheduled_tasks: bool | None = None,
        enable_recording: bool | None = None,
        **extra: Any,
    ) -> SessionResponse:
        """Create a session and optionally dispatch a task."""
        body: dict[str, Any] = {}
        if task is not None:
            body["task"] = task
        if model is not None:
            body["model"] = model
        if session_id is not None:
            body["sessionId"] = str(session_id)
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
        if workspace_id is not None:
            body["workspaceId"] = workspace_id
        if enable_scheduled_tasks is not None:
            body["enableScheduledTasks"] = enable_scheduled_tasks
        if enable_recording is not None:
            body["enableRecording"] = enable_recording
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

    async def get(self, session_id: _ID) -> SessionResponse:
        """Get session details."""
        return SessionResponse.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}")
        )

    async def stop(self, session_id: _ID, *, strategy: str | None = None, **extra: Any) -> SessionResponse:
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

    async def delete(self, session_id: _ID) -> None:
        """Soft-delete a session."""
        await self._http.request("DELETE", f"/sessions/{session_id}")

    async def upload_files(
        self,
        session_id: _ID,
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
        session_id: _ID,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
        shallow: bool | None = None,
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
                    "shallow": shallow,
                },
            )
        )

    async def messages(
        self,
        session_id: _ID,
        *,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> MessageListResponse:
        """List messages for a session with cursor-based pagination."""
        return MessageListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/sessions/{session_id}/messages",
                params={
                    "after": after,
                    "before": before,
                    "limit": limit,
                },
            )
        )

    async def wait_for_recording(
        self,
        session_id: _ID,
        *,
        timeout: float = 15,
        interval: float = 2,
    ) -> list[str]:
        """Poll until recording URLs are available. Returns a list of presigned MP4 URLs.

        Returns an empty list if no recording was produced (e.g. the agent
        answered without opening a browser, or recording was not enabled).
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            session = await self.get(session_id)
            if session.recording_urls:
                return list(session.recording_urls)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            await asyncio.sleep(min(interval, remaining))
        return []
