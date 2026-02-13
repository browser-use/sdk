from __future__ import annotations

from typing import Any, Dict, Optional

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    CustomProxy,
    SessionItemView,
    SessionListResponse,
    SessionView,
    ShareView,
)


def _build_create_body(
    *,
    profile_id: Optional[str] = None,
    proxy_country_code: Optional[str] = None,
    start_url: Optional[str] = None,
    browser_screen_width: Optional[int] = None,
    browser_screen_height: Optional[int] = None,
    persist_memory: Optional[bool] = None,
    keep_alive: Optional[bool] = None,
    custom_proxy: CustomProxy | None = None,
    **extra: Any,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {}
    if profile_id is not None:
        body["profileId"] = profile_id
    if proxy_country_code is not None:
        body["proxyCountryCode"] = proxy_country_code
    if start_url is not None:
        body["startUrl"] = start_url
    if browser_screen_width is not None:
        body["browserScreenWidth"] = browser_screen_width
    if browser_screen_height is not None:
        body["browserScreenHeight"] = browser_screen_height
    if persist_memory is not None:
        body["persistMemory"] = persist_memory
    if keep_alive is not None:
        body["keepAlive"] = keep_alive
    if custom_proxy is not None:
        body["customProxy"] = custom_proxy.model_dump(by_alias=True, exclude_none=True)
    body.update(extra)
    return body


class Sessions:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        profile_id: Optional[str] = None,
        proxy_country_code: Optional[str] = None,
        start_url: Optional[str] = None,
        browser_screen_width: Optional[int] = None,
        browser_screen_height: Optional[int] = None,
        persist_memory: Optional[bool] = None,
        keep_alive: Optional[bool] = None,
        custom_proxy: CustomProxy | None = None,
        **extra: Any,
    ) -> SessionItemView:
        """Create a new session."""
        body = _build_create_body(
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            start_url=start_url,
            browser_screen_width=browser_screen_width,
            browser_screen_height=browser_screen_height,
            persist_memory=persist_memory,
            keep_alive=keep_alive,
            custom_proxy=custom_proxy,
            **extra,
        )
        return SessionItemView.model_validate(
            self._http.request("POST", "/sessions", json=body)
        )

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        filter_by: Optional[str] = None,
    ) -> SessionListResponse:
        """List sessions with optional filtering."""
        return SessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/sessions",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                },
            )
        )

    def get(self, session_id: str) -> SessionView:
        """Get detailed session information."""
        return SessionView.model_validate(
            self._http.request("GET", f"/sessions/{session_id}")
        )

    def stop(self, session_id: str) -> SessionView:
        """Stop a session and all its running tasks."""
        return SessionView.model_validate(
            self._http.request(
                "PATCH", f"/sessions/{session_id}", json={"action": "stop"}
            )
        )

    def delete(self, session_id: str) -> None:
        """Delete a session with all its tasks."""
        self._http.request("DELETE", f"/sessions/{session_id}")

    def get_share(self, session_id: str) -> ShareView:
        """Get public share information for a session."""
        return ShareView.model_validate(
            self._http.request("GET", f"/sessions/{session_id}/public-share")
        )

    def create_share(self, session_id: str) -> ShareView:
        """Create or return existing public share for a session."""
        return ShareView.model_validate(
            self._http.request("POST", f"/sessions/{session_id}/public-share")
        )

    def delete_share(self, session_id: str) -> None:
        """Remove public share for a session."""
        self._http.request("DELETE", f"/sessions/{session_id}/public-share")


class AsyncSessions:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        profile_id: Optional[str] = None,
        proxy_country_code: Optional[str] = None,
        start_url: Optional[str] = None,
        browser_screen_width: Optional[int] = None,
        browser_screen_height: Optional[int] = None,
        persist_memory: Optional[bool] = None,
        keep_alive: Optional[bool] = None,
        custom_proxy: CustomProxy | None = None,
        **extra: Any,
    ) -> SessionItemView:
        """Create a new session."""
        body = _build_create_body(
            profile_id=profile_id,
            proxy_country_code=proxy_country_code,
            start_url=start_url,
            browser_screen_width=browser_screen_width,
            browser_screen_height=browser_screen_height,
            persist_memory=persist_memory,
            keep_alive=keep_alive,
            custom_proxy=custom_proxy,
            **extra,
        )
        return SessionItemView.model_validate(
            await self._http.request("POST", "/sessions", json=body)
        )

    async def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        filter_by: Optional[str] = None,
    ) -> SessionListResponse:
        """List sessions with optional filtering."""
        return SessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/sessions",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                },
            )
        )

    async def get(self, session_id: str) -> SessionView:
        """Get detailed session information."""
        return SessionView.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}")
        )

    async def stop(self, session_id: str) -> SessionView:
        """Stop a session and all its running tasks."""
        return SessionView.model_validate(
            await self._http.request(
                "PATCH", f"/sessions/{session_id}", json={"action": "stop"}
            )
        )

    async def delete(self, session_id: str) -> None:
        """Delete a session with all its tasks."""
        await self._http.request("DELETE", f"/sessions/{session_id}")

    async def get_share(self, session_id: str) -> ShareView:
        """Get public share information for a session."""
        return ShareView.model_validate(
            await self._http.request("GET", f"/sessions/{session_id}/public-share")
        )

    async def create_share(self, session_id: str) -> ShareView:
        """Create or return existing public share for a session."""
        return ShareView.model_validate(
            await self._http.request("POST", f"/sessions/{session_id}/public-share")
        )

    async def delete_share(self, session_id: str) -> None:
        """Remove public share for a session."""
        await self._http.request("DELETE", f"/sessions/{session_id}/public-share")
