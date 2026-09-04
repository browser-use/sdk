from __future__ import annotations

from typing import Any

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    BrowserDownloadListResponse,
    BrowserSessionItemView,
    BrowserSessionListResponse,
    BrowserSessionUpdateAction,
    BrowserSessionView,
    CustomProxy,
)


def _build_create_body(
    *,
    profile_id: str | None = None,
    proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
    metadata: dict[str, str] | None = None,
    timeout: int | None = None,
    browser_screen_width: int | None = None,
    browser_screen_height: int | None = None,
    allow_resizing: bool | None = None,
    pdf_renderer_enabled: bool | None = None,
    solve_captchas: bool | None = None,
    custom_proxy: CustomProxy | None = None,
    enable_recording: bool | None = None,
    **extra: Any,
) -> dict[str, Any]:
    if metadata is not None and len(metadata) > 10:
        raise ValueError("metadata supports at most 10 key-value pairs")

    body: dict[str, Any] = {}
    if profile_id is not None:
        body["profileId"] = profile_id
    if proxy_country_code is not _UNSET:
        body["proxyCountryCode"] = proxy_country_code.lower() if isinstance(proxy_country_code, str) else proxy_country_code
    if metadata is not None:
        body["metadata"] = metadata
    if timeout is not None:
        body["timeout"] = timeout
    if browser_screen_width is not None:
        body["browserScreenWidth"] = browser_screen_width
    if browser_screen_height is not None:
        body["browserScreenHeight"] = browser_screen_height
    if allow_resizing is not None:
        body["allowResizing"] = allow_resizing
    if pdf_renderer_enabled is not None:
        body["pdfRendererEnabled"] = pdf_renderer_enabled
    if solve_captchas is not None:
        body["solveCaptchas"] = solve_captchas
    if custom_proxy is not None:
        body["customProxy"] = custom_proxy.model_dump(by_alias=True, exclude_none=True)
    if enable_recording is not None:
        body["enableRecording"] = enable_recording
    body.update(extra)
    return body


class Browsers:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        metadata: dict[str, str] | None = None,
        timeout: int | None = None,
        browser_screen_width: int | None = None,
        browser_screen_height: int | None = None,
        allow_resizing: bool | None = None,
        pdf_renderer_enabled: bool | None = None,
        solve_captchas: bool | None = None,
        custom_proxy: CustomProxy | None = None,
        enable_recording: bool | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        """Create a new standalone browser session."""
        body = _build_create_body(
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            metadata=metadata,
            timeout=timeout,
            browser_screen_width=browser_screen_width,
            browser_screen_height=browser_screen_height,
            allow_resizing=allow_resizing,
            pdf_renderer_enabled=pdf_renderer_enabled,
            solve_captchas=solve_captchas,
            custom_proxy=custom_proxy,
            enable_recording=enable_recording,
            **extra,
        )
        return BrowserSessionItemView.model_validate(
            self._http.request("POST", "/browsers", json=body)
        )

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        filter_by: str | None = None,
        agent_session_id: str | None = None,
        metadata: list[str] | None = None,
    ) -> BrowserSessionListResponse:
        """List browser sessions with optional filtering."""
        return BrowserSessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                    "agentSessionId": agent_session_id,
                    "metadata": metadata,
                },
            )
        )

    def get(self, session_id: str) -> BrowserSessionView:
        """Get detailed browser session information."""
        return BrowserSessionView.model_validate(
            self._http.request("GET", f"/browsers/{session_id}")
        )

    def update(self, session_id: str, *, action: BrowserSessionUpdateAction | str, **extra: Any) -> BrowserSessionView:
        """Update a browser session (generic PATCH)."""
        body: dict[str, Any] = {"action": action, **extra}
        return BrowserSessionView.model_validate(
            self._http.request("PATCH", f"/browsers/{session_id}", json=body)
        )

    def stop(self, session_id: str, **extra: Any) -> BrowserSessionView:
        """Stop a running browser session."""
        return self.update(session_id, action=BrowserSessionUpdateAction.stop, **extra)

    def downloads(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
    ) -> BrowserDownloadListResponse:
        """List files the browser downloaded to S3 during the session."""
        return BrowserDownloadListResponse.model_validate(
            self._http.request(
                "GET",
                f"/browsers/{session_id}/downloads",
                params={
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                },
            )
        )


class AsyncBrowsers:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        profile_id: str | None = None,
        proxy_country_code: str | None = _UNSET,  # type: ignore[assignment]
        metadata: dict[str, str] | None = None,
        timeout: int | None = None,
        browser_screen_width: int | None = None,
        browser_screen_height: int | None = None,
        allow_resizing: bool | None = None,
        pdf_renderer_enabled: bool | None = None,
        solve_captchas: bool | None = None,
        custom_proxy: CustomProxy | None = None,
        enable_recording: bool | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        """Create a new standalone browser session."""
        body = _build_create_body(
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            metadata=metadata,
            timeout=timeout,
            browser_screen_width=browser_screen_width,
            browser_screen_height=browser_screen_height,
            allow_resizing=allow_resizing,
            pdf_renderer_enabled=pdf_renderer_enabled,
            solve_captchas=solve_captchas,
            custom_proxy=custom_proxy,
            enable_recording=enable_recording,
            **extra,
        )
        return BrowserSessionItemView.model_validate(
            await self._http.request("POST", "/browsers", json=body)
        )

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        filter_by: str | None = None,
        agent_session_id: str | None = None,
        metadata: list[str] | None = None,
    ) -> BrowserSessionListResponse:
        """List browser sessions with optional filtering."""
        return BrowserSessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                    "agentSessionId": agent_session_id,
                    "metadata": metadata,
                },
            )
        )

    async def get(self, session_id: str) -> BrowserSessionView:
        """Get detailed browser session information."""
        return BrowserSessionView.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}")
        )

    async def update(self, session_id: str, *, action: BrowserSessionUpdateAction | str, **extra: Any) -> BrowserSessionView:
        """Update a browser session (generic PATCH)."""
        body: dict[str, Any] = {"action": action, **extra}
        return BrowserSessionView.model_validate(
            await self._http.request("PATCH", f"/browsers/{session_id}", json=body)
        )

    async def stop(self, session_id: str, **extra: Any) -> BrowserSessionView:
        """Stop a running browser session."""
        return await self.update(session_id, action=BrowserSessionUpdateAction.stop, **extra)

    async def downloads(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
    ) -> BrowserDownloadListResponse:
        """List files the browser downloaded to S3 during the session."""
        return BrowserDownloadListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/browsers/{session_id}/downloads",
                params={
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                },
            )
        )
