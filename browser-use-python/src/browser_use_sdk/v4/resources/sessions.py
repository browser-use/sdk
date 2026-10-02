from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    QueuedMessage,
    QueueListResponse,
    SessionCostResponse,
    SessionInfo,
    SessionListResponse,
    SessionShareInfo,
)

if TYPE_CHECKING:
    from uuid import UUID


def _build_message_body(
    text: str,
    interrupt: bool | None,
    attached_file_ids: list[str | UUID] | None,
    extra: dict[str, Any],
) -> dict[str, Any]:
    body: dict[str, Any] = {"text": text}
    if interrupt is not None:
        body["interrupt"] = interrupt
    if attached_file_ids is not None:
        body["attachedFileIds"] = [str(f) for f in attached_file_ids]
    body.update(extra)
    return body


class Sessions:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> SessionListResponse:
        """List sessions with cursor-based pagination, most recent first."""
        return SessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/sessions",
                params={
                    "cursor": cursor,
                    "limit": limit,
                },
            )
        )

    def get(self, session_id: str | UUID) -> SessionInfo:
        """Get session metadata (latest run id, status, ...)."""
        return SessionInfo.model_validate(
            self._http.request("GET", f"/sessions/{session_id}")
        )

    def purge(self, session_id: str | UUID) -> None:
        """Immediately purge all data for a session on a ZDR-enabled project."""
        self._http.request("POST", f"/sessions/{session_id}/purge")

    def update(
        self,
        session_id: str | UUID,
        *,
        title: str | None = _UNSET,  # type: ignore[assignment]
        **extra: Any,
    ) -> SessionInfo:
        """Rename a session; pass ``title=None`` to clear its name."""
        body: dict[str, Any] = {}
        if title is not _UNSET:
            body["title"] = title
        body.update(extra)
        return SessionInfo.model_validate(
            self._http.request("PATCH", f"/sessions/{session_id}", json=body)
        )

    def delete(self, session_id: str | UUID) -> None:
        """Delete a session, cancelling its active run and pending messages."""
        self._http.request("DELETE", f"/sessions/{session_id}")

    def cost(self, session_id: str | UUID) -> SessionCostResponse:
        """Get what the session has cost so far: LLM, search, browser and proxy."""
        return SessionCostResponse.model_validate(
            self._http.request("GET", f"/sessions/{session_id}/cost")
        )

    def get_share(self, session_id: str | UUID) -> SessionShareInfo | None:
        """Get the session's public share link, or None if it was never shared."""
        data = self._http.request("GET", f"/sessions/{session_id}/share")
        return None if data is None else SessionShareInfo.model_validate(data)

    def create_share(self, session_id: str | UUID) -> SessionShareInfo:
        """Enable a public share link for the session, reusing its token if one exists."""
        return SessionShareInfo.model_validate(
            self._http.request("POST", f"/sessions/{session_id}/share")
        )

    def update_share(
        self, session_id: str | UUID, *, is_active: bool, **extra: Any
    ) -> SessionShareInfo:
        """Turn the session's public share link on or off."""
        return SessionShareInfo.model_validate(
            self._http.request(
                "PUT",
                f"/sessions/{session_id}/share",
                json={"isActive": is_active, **extra},
            )
        )

    def send_message(
        self,
        session_id: str | UUID,
        text: str,
        *,
        interrupt: bool | None = None,
        attached_file_ids: list[str | UUID] | None = None,
        deduplicate: str | None = None,
        **extra: Any,
    ) -> QueuedMessage:
        """Send a message to the session.

        Runs as the next turn when the session is busy; pass ``interrupt=True``
        to cancel the active run so the message runs immediately. Pass
        ``deduplicate="exact-text-v1"`` to reuse an equivalent queued message.
        """
        request_kwargs: dict[str, Any] = {
            "json": _build_message_body(text, interrupt, attached_file_ids, extra)
        }
        if deduplicate is not None:
            request_kwargs["headers"] = {"X-V4-Queue-Deduplicate": deduplicate}
        return QueuedMessage.model_validate(
            self._http.request("POST", f"/sessions/{session_id}/queue", **request_kwargs)
        )

    def queue(self, session_id: str | UUID) -> QueueListResponse:
        """List the session's pending queued messages."""
        return QueueListResponse.model_validate(
            self._http.request("GET", f"/sessions/{session_id}/queue")
        )

    def get_message(self, session_id: str | UUID, message_id: int) -> QueuedMessage:
        """Get one queued message, including terminal handoff states."""
        return QueuedMessage.model_validate(
            self._http.request("GET", f"/sessions/{session_id}/queue/{message_id}")
        )

    def remove_message(self, session_id: str | UUID, message_id: int) -> QueuedMessage:
        """Remove a pending message from the session's queue."""
        return QueuedMessage.model_validate(
            self._http.request("DELETE", f"/sessions/{session_id}/queue/{message_id}")
        )


class AsyncSessions:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> SessionListResponse:
        """List sessions with cursor-based pagination, most recent first."""
        return SessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/sessions",
                params={
                    "cursor": cursor,
                    "limit": limit,
                },
            )
        )

    async def get(self, session_id: str | UUID) -> SessionInfo:
        """Get session metadata (latest run id, status, ...)."""
        return SessionInfo.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}")
        )

    async def purge(self, session_id: str | UUID) -> None:
        """Immediately purge all data for a session on a ZDR-enabled project."""
        await self._http.request("POST", f"/sessions/{session_id}/purge")

    async def update(
        self,
        session_id: str | UUID,
        *,
        title: str | None = _UNSET,  # type: ignore[assignment]
        **extra: Any,
    ) -> SessionInfo:
        """Rename a session; pass ``title=None`` to clear its name."""
        body: dict[str, Any] = {}
        if title is not _UNSET:
            body["title"] = title
        body.update(extra)
        return SessionInfo.model_validate(
            await self._http.request("PATCH", f"/sessions/{session_id}", json=body)
        )

    async def delete(self, session_id: str | UUID) -> None:
        """Delete a session, cancelling its active run and pending messages."""
        await self._http.request("DELETE", f"/sessions/{session_id}")

    async def cost(self, session_id: str | UUID) -> SessionCostResponse:
        """Get what the session has cost so far: LLM, search, browser and proxy."""
        return SessionCostResponse.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}/cost")
        )

    async def get_share(self, session_id: str | UUID) -> SessionShareInfo | None:
        """Get the session's public share link, or None if it was never shared."""
        data = await self._http.request("GET", f"/sessions/{session_id}/share")
        return None if data is None else SessionShareInfo.model_validate(data)

    async def create_share(self, session_id: str | UUID) -> SessionShareInfo:
        """Enable a public share link for the session, reusing its token if one exists."""
        return SessionShareInfo.model_validate(
            await self._http.request("POST", f"/sessions/{session_id}/share")
        )

    async def update_share(
        self, session_id: str | UUID, *, is_active: bool, **extra: Any
    ) -> SessionShareInfo:
        """Turn the session's public share link on or off."""
        return SessionShareInfo.model_validate(
            await self._http.request(
                "PUT",
                f"/sessions/{session_id}/share",
                json={"isActive": is_active, **extra},
            )
        )

    async def send_message(
        self,
        session_id: str | UUID,
        text: str,
        *,
        interrupt: bool | None = None,
        attached_file_ids: list[str | UUID] | None = None,
        deduplicate: str | None = None,
        **extra: Any,
    ) -> QueuedMessage:
        """Send a message to the session.

        Runs as the next turn when the session is busy; pass ``interrupt=True``
        to cancel the active run so the message runs immediately. Pass
        ``deduplicate="exact-text-v1"`` to reuse an equivalent queued message.
        """
        request_kwargs: dict[str, Any] = {
            "json": _build_message_body(text, interrupt, attached_file_ids, extra)
        }
        if deduplicate is not None:
            request_kwargs["headers"] = {"X-V4-Queue-Deduplicate": deduplicate}
        return QueuedMessage.model_validate(
            await self._http.request(
                "POST", f"/sessions/{session_id}/queue", **request_kwargs
            )
        )

    async def queue(self, session_id: str | UUID) -> QueueListResponse:
        """List the session's pending queued messages."""
        return QueueListResponse.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}/queue")
        )

    async def get_message(
        self, session_id: str | UUID, message_id: int
    ) -> QueuedMessage:
        """Get one queued message, including terminal handoff states."""
        return QueuedMessage.model_validate(
            await self._http.request(
                "GET", f"/sessions/{session_id}/queue/{message_id}"
            )
        )

    async def remove_message(self, session_id: str | UUID, message_id: int) -> QueuedMessage:
        """Remove a pending message from the session's queue."""
        return QueuedMessage.model_validate(
            await self._http.request("DELETE", f"/sessions/{session_id}/queue/{message_id}")
        )
