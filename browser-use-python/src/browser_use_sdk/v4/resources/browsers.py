from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    BrowserAccessEventList,
    BrowserAccessTokenRevoked,
    BrowserAccessTokenCreated,
    BrowserAccessTokenList,
    BrowserDownloadListResponse,
    BrowserProxyView,
    BrowserSessionItemView,
    BrowserSessionListResponse,
    BrowserSessionView,
    CustomProxy,
    Mode2 as BrowserProxyMode,
)

if TYPE_CHECKING:
    from uuid import UUID


def _build_create_body(
    *,
    profile_id: str | None = None,
    network_policy_id: str | UUID | None = None,
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
    extension_ids: list[str] | None = None,
    cdp_token_ttl_seconds: int | None = None,
    close_connections_on_expiry: bool | None = None,
    **extra: Any,
) -> dict[str, Any]:
    if metadata is not None and len(metadata) > 10:
        raise ValueError("metadata supports at most 10 key-value pairs")

    body: dict[str, Any] = {}
    if profile_id is not None:
        body["profileId"] = profile_id
    if network_policy_id is not None:
        body["networkPolicyId"] = str(network_policy_id)
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
        body["customProxy"] = custom_proxy.model_dump(by_alias=True, exclude_none=True, mode="json")
    if enable_recording is not None:
        body["enableRecording"] = enable_recording
    if extension_ids is not None:
        body["extensionIds"] = extension_ids
    if cdp_token_ttl_seconds is not None:
        body["cdpTokenTtlSeconds"] = cdp_token_ttl_seconds
    if close_connections_on_expiry is not None:
        body["closeConnectionsOnExpiry"] = close_connections_on_expiry
    body.update(extra)
    return body


def _build_proxy_body(
    mode: BrowserProxyMode | Literal["managed", "direct", "custom"] | None,
    country: str | None,
    target: str | None,
    rotate: bool | None,
    custom_proxy: CustomProxy | None,
    extra: dict[str, Any],
) -> dict[str, Any] | None:
    body: dict[str, Any] = {}
    if mode is not None:
        body["mode"] = mode.value if isinstance(mode, BrowserProxyMode) else mode
    if country is not None:
        body["country"] = country
    if target is not None:
        body["target"] = target
    if rotate is not None:
        body["rotate"] = rotate
    if custom_proxy is not None:
        body["customProxy"] = custom_proxy.model_dump(by_alias=True, exclude_none=True, mode="json")
    body.update(extra)
    return body or None


def _build_access_token_body(
    ttl_seconds: int | None,
    label: str | None,
    close_connections_on_expiry: bool | None,
    extra: dict[str, Any],
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if ttl_seconds is not None:
        body["ttlSeconds"] = ttl_seconds
    if label is not None:
        body["label"] = label
    if close_connections_on_expiry is not None:
        body["closeConnectionsOnExpiry"] = close_connections_on_expiry
    body.update(extra)
    return body


class Browsers:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        profile_id: str | None = None,
        network_policy_id: str | UUID | None = None,
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
        extension_ids: list[str] | None = None,
        cdp_token_ttl_seconds: int | None = None,
        close_connections_on_expiry: bool | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        """Create a new standalone browser session."""
        body = _build_create_body(
            profile_id=profile_id,
            network_policy_id=network_policy_id,
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
            extension_ids=extension_ids,
            cdp_token_ttl_seconds=cdp_token_ttl_seconds,
            close_connections_on_expiry=close_connections_on_expiry,
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

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        filter_by: str | None = None,
        agent_session_id: str | UUID | None = None,
        metadata: list[str] | None = None,
    ) -> BrowserSessionListResponse:
        """List browser sessions; ``metadata`` terms are ``key`` or ``key=value``."""
        return BrowserSessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                    "agentSessionId": (
                        str(agent_session_id) if agent_session_id is not None else None
                    ),
                    "metadata": metadata,
                },
            )
        )

    def get(self, session_id: str | UUID) -> BrowserSessionView:
        """Get a browser session, including its recording URL when ready."""
        return BrowserSessionView.model_validate(
            self._http.request("GET", f"/browsers/{session_id}")
        )

    def get_proxy(self, session_id: str | UUID) -> BrowserProxyView:
        """Get the proxy for a browser session."""
        return BrowserProxyView.model_validate(
            self._http.request("GET", f"/browsers/{session_id}/proxy")
        )

    def update_proxy(
        self,
        session_id: str | UUID,
        *,
        mode: BrowserProxyMode | Literal["managed", "direct", "custom"] | None = None,
        country: str | None = None,
        target: str | None = None,
        rotate: bool | None = None,
        custom_proxy: CustomProxy | None = None,
        **extra: Any,
    ) -> BrowserProxyView:
        """Update the proxy for a browser session."""
        body = _build_proxy_body(mode, country, target, rotate, custom_proxy, extra)
        return BrowserProxyView.model_validate(
            self._http.request("PATCH", f"/browsers/{session_id}/proxy", json=body)
        )

    def downloads(
        self,
        session_id: str | UUID,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
    ) -> BrowserDownloadListResponse:
        """List files the browser downloaded during the session."""
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

    def create_access_token(
        self,
        session_id: str | UUID,
        *,
        ttl_seconds: int | None = None,
        label: str | None = None,
        close_connections_on_expiry: bool | None = None,
        **extra: Any,
    ) -> BrowserAccessTokenCreated:
        """Create an access token and a CDP URL that holds it; only this answer shows the token."""
        body = _build_access_token_body(ttl_seconds, label, close_connections_on_expiry, extra)
        return BrowserAccessTokenCreated.model_validate(
            self._http.request("POST", f"/browsers/{session_id}/access-tokens", json=body)
        )

    def list_access_tokens(self, session_id: str | UUID) -> BrowserAccessTokenList:
        """List the access tokens of a browser session, without the secret values."""
        return BrowserAccessTokenList.model_validate(
            self._http.request("GET", f"/browsers/{session_id}/access-tokens")
        )

    def revoke_access_token(self, session_id: str | UUID, token_id: str | UUID) -> BrowserAccessTokenRevoked:
        """Revoke one access token and close its open connections."""
        return BrowserAccessTokenRevoked.model_validate(
            self._http.request("DELETE", f"/browsers/{session_id}/access-tokens/{token_id}")
        )

    def revoke_all_access_tokens(self, session_id: str | UUID) -> BrowserAccessTokenRevoked:
        """Revoke all customer and viewer tokens of a browser session and close their connections."""
        return BrowserAccessTokenRevoked.model_validate(
            self._http.request("DELETE", f"/browsers/{session_id}/access-tokens")
        )

    def get_access_log(
        self,
        session_id: str | UUID,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> BrowserAccessEventList:
        """List the access token events of a browser session, newest first."""
        return BrowserAccessEventList.model_validate(
            self._http.request(
                "GET",
                f"/browsers/{session_id}/access-log",
                params={"pageSize": page_size, "pageNumber": page_number},
            )
        )


class AsyncBrowsers:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        profile_id: str | None = None,
        network_policy_id: str | UUID | None = None,
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
        extension_ids: list[str] | None = None,
        cdp_token_ttl_seconds: int | None = None,
        close_connections_on_expiry: bool | None = None,
        **extra: Any,
    ) -> BrowserSessionItemView:
        """Create a new standalone browser session."""
        body = _build_create_body(
            profile_id=profile_id,
            network_policy_id=network_policy_id,
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
            extension_ids=extension_ids,
            cdp_token_ttl_seconds=cdp_token_ttl_seconds,
            close_connections_on_expiry=close_connections_on_expiry,
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

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        filter_by: str | None = None,
        agent_session_id: str | UUID | None = None,
        metadata: list[str] | None = None,
    ) -> BrowserSessionListResponse:
        """List browser sessions; ``metadata`` terms are ``key`` or ``key=value``."""
        return BrowserSessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                    "agentSessionId": (
                        str(agent_session_id) if agent_session_id is not None else None
                    ),
                    "metadata": metadata,
                },
            )
        )

    async def get(self, session_id: str | UUID) -> BrowserSessionView:
        """Get a browser session, including its recording URL when ready."""
        return BrowserSessionView.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}")
        )

    async def get_proxy(self, session_id: str | UUID) -> BrowserProxyView:
        """Get the proxy for a browser session."""
        return BrowserProxyView.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}/proxy")
        )

    async def update_proxy(
        self,
        session_id: str | UUID,
        *,
        mode: BrowserProxyMode | Literal["managed", "direct", "custom"] | None = None,
        country: str | None = None,
        target: str | None = None,
        rotate: bool | None = None,
        custom_proxy: CustomProxy | None = None,
        **extra: Any,
    ) -> BrowserProxyView:
        """Update the proxy for a browser session."""
        body = _build_proxy_body(mode, country, target, rotate, custom_proxy, extra)
        return BrowserProxyView.model_validate(
            await self._http.request("PATCH", f"/browsers/{session_id}/proxy", json=body)
        )

    async def downloads(
        self,
        session_id: str | UUID,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
    ) -> BrowserDownloadListResponse:
        """List files the browser downloaded during the session."""
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

    async def create_access_token(
        self,
        session_id: str | UUID,
        *,
        ttl_seconds: int | None = None,
        label: str | None = None,
        close_connections_on_expiry: bool | None = None,
        **extra: Any,
    ) -> BrowserAccessTokenCreated:
        """Create an access token and a CDP URL that holds it; only this answer shows the token."""
        body = _build_access_token_body(ttl_seconds, label, close_connections_on_expiry, extra)
        return BrowserAccessTokenCreated.model_validate(
            await self._http.request("POST", f"/browsers/{session_id}/access-tokens", json=body)
        )

    async def list_access_tokens(self, session_id: str | UUID) -> BrowserAccessTokenList:
        """List the access tokens of a browser session, without the secret values."""
        return BrowserAccessTokenList.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}/access-tokens")
        )

    async def revoke_access_token(self, session_id: str | UUID, token_id: str | UUID) -> BrowserAccessTokenRevoked:
        """Revoke one access token and close its open connections."""
        return BrowserAccessTokenRevoked.model_validate(
            await self._http.request("DELETE", f"/browsers/{session_id}/access-tokens/{token_id}")
        )

    async def revoke_all_access_tokens(self, session_id: str | UUID) -> BrowserAccessTokenRevoked:
        """Revoke all customer and viewer tokens of a browser session and close their connections."""
        return BrowserAccessTokenRevoked.model_validate(
            await self._http.request("DELETE", f"/browsers/{session_id}/access-tokens")
        )

    async def get_access_log(
        self,
        session_id: str | UUID,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> BrowserAccessEventList:
        """List the access token events of a browser session, newest first."""
        return BrowserAccessEventList.model_validate(
            await self._http.request(
                "GET",
                f"/browsers/{session_id}/access-log",
                params={"pageSize": page_size, "pageNumber": page_number},
            )
        )
