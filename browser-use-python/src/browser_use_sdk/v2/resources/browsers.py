from __future__ import annotations

from typing import Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    BrowserSessionItemView,
    BrowserSessionListResponse,
    BrowserSessionView,
    CustomProxy,
)


def _build_create_body(
    *,
    profile_id: str | None = None,
    proxy_country_code: str | None = None,
    timeout: int | None = None,
    browser_screen_width: int | None = None,
    browser_screen_height: int | None = None,
    allow_resizing: bool | None = None,
    custom_proxy: CustomProxy | None = None,
    **extra: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if profile_id is not None:
        body["profileId"] = profile_id
    if proxy_country_code is not None:
        body["proxyCountryCode"] = proxy_country_code
    if timeout is not None:
        body["timeout"] = timeout
    if browser_screen_width is not None:
        body["browserScreenWidth"] = browser_screen_width
    if browser_screen_height is not None:
        body["browserScreenHeight"] = browser_screen_height
    if allow_resizing is not None:
        body["allowResizing"] = allow_resizing
    if custom_proxy is not None:
        body["customProxy"] = custom_proxy.model_dump(by_alias=True, exclude_none=True)
    body.update(extra)
    return body


class Browsers:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        profile_id: str | None = None,
        proxy_country_code: str | None = None,
        timeout: int | None = None,
        browser_screen_width: int | None = None,
        browser_screen_height: int | None = None,
        allow_resizing: bool | None = None,
        custom_proxy: CustomProxy | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        body = _build_create_body(
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            timeout=timeout,
            browser_screen_width=browser_screen_width,
            browser_screen_height=browser_screen_height,
            allow_resizing=allow_resizing,
            custom_proxy=custom_proxy,
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
    ) -> BrowserSessionListResponse:
        return BrowserSessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                },
            )
        )

    def get(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            self._http.request("GET", f"/browsers/{session_id}")
        )

    def stop(self, session_id: str) -> BrowserSessionView:
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
        proxy_country_code: str | None = None,
        timeout: int | None = None,
        browser_screen_width: int | None = None,
        browser_screen_height: int | None = None,
        allow_resizing: bool | None = None,
        custom_proxy: CustomProxy | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        body = _build_create_body(
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            timeout=timeout,
            browser_screen_width=browser_screen_width,
            browser_screen_height=browser_screen_height,
            allow_resizing=allow_resizing,
            custom_proxy=custom_proxy,
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
    ) -> BrowserSessionListResponse:
        return BrowserSessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                },
            )
        )

    async def get(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}")
        )

    async def stop(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            await self._http.request(
                "PATCH", f"/browsers/{session_id}", json={"action": "stop"}
            )
        )
