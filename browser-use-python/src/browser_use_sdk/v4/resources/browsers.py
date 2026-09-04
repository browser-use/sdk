from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    BrowserSessionItemView,
    BrowserSessionView,
    CustomProxy,
)

if TYPE_CHECKING:
    from uuid import UUID


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
        body["proxyCountryCode"] = (
            proxy_country_code.lower()
            if isinstance(proxy_country_code, str)
            else proxy_country_code
        )
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

    def stop(self, session_id: str | UUID) -> BrowserSessionView:
        """Stop a browser session and refund its unused time."""
        return BrowserSessionView.model_validate(
            self._http.request(
                "PATCH", f"/browsers/{session_id}", json={"action": "stop"}
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

    async def stop(self, session_id: str | UUID) -> BrowserSessionView:
        """Stop a browser session and refund its unused time."""
        return BrowserSessionView.model_validate(
            await self._http.request(
                "PATCH", f"/browsers/{session_id}", json={"action": "stop"}
            )
        )
