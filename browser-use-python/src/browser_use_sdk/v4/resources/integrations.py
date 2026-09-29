from __future__ import annotations

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    AuthorizeResponse,
    ConnectionStatusResponse,
    DisconnectResponse,
    IntegrationCategoryResponse,
    IntegrationListResponse,
)


class Integrations:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        popular_only: bool | None = None,
        connected_only: bool | None = None,
    ) -> IntegrationListResponse:
        """List available integrations with this project's connection status."""
        return IntegrationListResponse.model_validate(
            self._http.request(
                "GET",
                "/integrations",
                params={
                    "limit": limit,
                    "offset": offset,
                    "search": search,
                    "popular_only": popular_only,
                    "connected_only": connected_only,
                },
            )
        )

    def categories(self) -> IntegrationCategoryResponse:
        """List integration categories."""
        return IntegrationCategoryResponse.model_validate(
            self._http.request("GET", "/integrations/categories")
        )

    def authorize(self, provider: str) -> AuthorizeResponse:
        """Get the OAuth URL that connects a provider; poll ``status()`` after opening it."""
        return AuthorizeResponse.model_validate(
            self._http.request("POST", f"/integrations/{provider}/authorize")
        )

    def status(self, provider: str) -> ConnectionStatusResponse:
        """Check whether this project has connected a provider."""
        return ConnectionStatusResponse.model_validate(
            self._http.request("GET", f"/integrations/{provider}/status")
        )

    def disconnect(self, provider: str) -> DisconnectResponse:
        """Disconnect a provider from this project."""
        return DisconnectResponse.model_validate(
            self._http.request("DELETE", f"/integrations/{provider}")
        )


class AsyncIntegrations:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
        popular_only: bool | None = None,
        connected_only: bool | None = None,
    ) -> IntegrationListResponse:
        """List available integrations with this project's connection status."""
        return IntegrationListResponse.model_validate(
            await self._http.request(
                "GET",
                "/integrations",
                params={
                    "limit": limit,
                    "offset": offset,
                    "search": search,
                    "popular_only": popular_only,
                    "connected_only": connected_only,
                },
            )
        )

    async def categories(self) -> IntegrationCategoryResponse:
        """List integration categories."""
        return IntegrationCategoryResponse.model_validate(
            await self._http.request("GET", "/integrations/categories")
        )

    async def authorize(self, provider: str) -> AuthorizeResponse:
        """Get the OAuth URL that connects a provider; poll ``status()`` after opening it."""
        return AuthorizeResponse.model_validate(
            await self._http.request("POST", f"/integrations/{provider}/authorize")
        )

    async def status(self, provider: str) -> ConnectionStatusResponse:
        """Check whether this project has connected a provider."""
        return ConnectionStatusResponse.model_validate(
            await self._http.request("GET", f"/integrations/{provider}/status")
        )

    async def disconnect(self, provider: str) -> DisconnectResponse:
        """Disconnect a provider from this project."""
        return DisconnectResponse.model_validate(
            await self._http.request("DELETE", f"/integrations/{provider}")
        )
