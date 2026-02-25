from __future__ import annotations

from typing import Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import ProfileListResponse, ProfileView


class Profiles:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Create a new browser profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return ProfileView.model_validate(
            self._http.request("POST", "/profiles", json=body)
        )

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> ProfileListResponse:
        """List browser profiles."""
        return ProfileListResponse.model_validate(
            self._http.request(
                "GET",
                "/profiles",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                },
            )
        )

    def get(self, profile_id: str) -> ProfileView:
        """Get browser profile details."""
        return ProfileView.model_validate(
            self._http.request("GET", f"/profiles/{profile_id}")
        )

    def update(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Update a browser profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return ProfileView.model_validate(
            self._http.request("PATCH", f"/profiles/{profile_id}", json=body)
        )

    def delete(self, profile_id: str) -> None:
        """Delete a browser profile."""
        self._http.request("DELETE", f"/profiles/{profile_id}")

    # Deprecated aliases for older browser-use versions (<=0.11.x)
    create_profile = create
    list_profiles = list
    get_profile = get
    update_profile = update
    delete_browser_profile = delete


class AsyncProfiles:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Create a new browser profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return ProfileView.model_validate(
            await self._http.request("POST", "/profiles", json=body)
        )

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> ProfileListResponse:
        """List browser profiles."""
        return ProfileListResponse.model_validate(
            await self._http.request(
                "GET",
                "/profiles",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                },
            )
        )

    async def get(self, profile_id: str) -> ProfileView:
        """Get browser profile details."""
        return ProfileView.model_validate(
            await self._http.request("GET", f"/profiles/{profile_id}")
        )

    async def update(
        self,
        profile_id: str,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Update a browser profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return ProfileView.model_validate(
            await self._http.request("PATCH", f"/profiles/{profile_id}", json=body)
        )

    async def delete(self, profile_id: str) -> None:
        """Delete a browser profile."""
        await self._http.request("DELETE", f"/profiles/{profile_id}")

    # Deprecated aliases for older browser-use versions (<=0.11.x)
    create_profile = create
    list_profiles = list
    get_profile = get
    update_profile = update
    delete_browser_profile = delete
