from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v3.models import (
    BrowserSessionItemView,
    BrowserSessionListResponse,
    BrowserSessionView,
)

if TYPE_CHECKING:
    from uuid import UUID


class Browsers:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        timeout: int | None = None,
        browser_screen_width: int | None = None,
        browser_screen_height: int | None = None,
        allow_resizing: bool | None = None,
        enable_recording: bool | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        """Create a standalone browser session."""
        body: dict[str, Any] = {}
        if profile_id is not None:
            body["profileId"] = profile_id
        if proxy_country_code is not _UNSET:
            body["proxyCountryCode"] = proxy_country_code.lower() if isinstance(proxy_country_code, str) else proxy_country_code
        if timeout is not None:
            body["timeout"] = timeout
        if browser_screen_width is not None:
            body["browserScreenWidth"] = browser_screen_width
        if browser_screen_height is not None:
            body["browserScreenHeight"] = browser_screen_height
        if allow_resizing is not None:
            body["allowResizing"] = allow_resizing
        if enable_recording is not None:
            body["enableRecording"] = enable_recording
        body.update(extra)
        return BrowserSessionItemView.model_validate(
            self._http.request("POST", "/browsers", json=body)
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> BrowserSessionListResponse:
        """List browser sessions for the authenticated project."""
        return BrowserSessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/browsers",
                params={"page": page, "page_size": page_size},
            )
        )

    def get(self, session_id: str | UUID) -> BrowserSessionView:
        """Get browser session details."""
        return BrowserSessionView.model_validate(
            self._http.request("GET", f"/browsers/{session_id}")
        )

    def update(self, session_id: str | UUID, *, action: str, **extra: Any) -> BrowserSessionView:
        """Update a browser session (e.g. stop it)."""
        body: dict[str, Any] = {"action": action}
        body.update(extra)
        return BrowserSessionView.model_validate(
            self._http.request("PATCH", f"/browsers/{session_id}", json=body)
        )

    def stop(self, session_id: str | UUID) -> BrowserSessionView:
        """Stop a browser session."""
        return self.update(session_id, action="stop")


class AsyncBrowsers:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        timeout: int | None = None,
        browser_screen_width: int | None = None,
        browser_screen_height: int | None = None,
        allow_resizing: bool | None = None,
        enable_recording: bool | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        """Create a standalone browser session."""
        body: dict[str, Any] = {}
        if profile_id is not None:
            body["profileId"] = profile_id
        if proxy_country_code is not _UNSET:
            body["proxyCountryCode"] = proxy_country_code.lower() if isinstance(proxy_country_code, str) else proxy_country_code
        if timeout is not None:
            body["timeout"] = timeout
        if browser_screen_width is not None:
            body["browserScreenWidth"] = browser_screen_width
        if browser_screen_height is not None:
            body["browserScreenHeight"] = browser_screen_height
        if allow_resizing is not None:
            body["allowResizing"] = allow_resizing
        if enable_recording is not None:
            body["enableRecording"] = enable_recording
        body.update(extra)
        return BrowserSessionItemView.model_validate(
            await self._http.request("POST", "/browsers", json=body)
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
    ) -> BrowserSessionListResponse:
        """List browser sessions for the authenticated project."""
        return BrowserSessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/browsers",
                params={"page": page, "page_size": page_size},
            )
        )

    async def get(self, session_id: str | UUID) -> BrowserSessionView:
        """Get browser session details."""
        return BrowserSessionView.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}")
        )

    async def update(self, session_id: str | UUID, *, action: str, **extra: Any) -> BrowserSessionView:
        """Update a browser session (e.g. stop it)."""
        body: dict[str, Any] = {"action": action}
        body.update(extra)
        return BrowserSessionView.model_validate(
            await self._http.request("PATCH", f"/browsers/{session_id}", json=body)
        )

    async def stop(self, session_id: str | UUID) -> BrowserSessionView:
        """Stop a browser session."""
        return await self.update(session_id, action="stop")
