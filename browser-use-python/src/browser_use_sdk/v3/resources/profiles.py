from __future__ import annotations

from typing import Any
from uuid import UUID

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v3.models import (
    ProfileListResponse,
    ProfileView,
)

_ID = str | UUID


class Profiles:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        name: str | None = None,
        user_id: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Create a browser profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if user_id is not None:
            body["userId"] = user_id
        body.update(extra)
        return ProfileView.model_validate(
            self._http.request("POST", "/profiles", json=body)
        )

    def list(
        self,
        *,
        query: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ProfileListResponse:
        """List profiles for the authenticated project."""
        return ProfileListResponse.model_validate(
            self._http.request(
                "GET",
                "/profiles",
                params={"query": query, "page": page, "page_size": page_size},
            )
        )

    def get(self, profile_id: _ID) -> ProfileView:
        """Get profile details."""
        return ProfileView.model_validate(
            self._http.request("GET", f"/profiles/{profile_id}")
        )

    def update(
        self,
        profile_id: _ID,
        *,
        name: str | None = None,
        user_id: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Update a profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if user_id is not None:
            body["userId"] = user_id
        body.update(extra)
        return ProfileView.model_validate(
            self._http.request("PATCH", f"/profiles/{profile_id}", json=body)
        )

    def delete(self, profile_id: _ID) -> None:
        """Delete a profile."""
        self._http.request("DELETE", f"/profiles/{profile_id}")


class AsyncProfiles:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        name: str | None = None,
        user_id: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Create a browser profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if user_id is not None:
            body["userId"] = user_id
        body.update(extra)
        return ProfileView.model_validate(
            await self._http.request("POST", "/profiles", json=body)
        )

    async def list(
        self,
        *,
        query: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> ProfileListResponse:
        """List profiles for the authenticated project."""
        return ProfileListResponse.model_validate(
            await self._http.request(
                "GET",
                "/profiles",
                params={"query": query, "page": page, "page_size": page_size},
            )
        )

    async def get(self, profile_id: _ID) -> ProfileView:
        """Get profile details."""
        return ProfileView.model_validate(
            await self._http.request("GET", f"/profiles/{profile_id}")
        )

    async def update(
        self,
        profile_id: _ID,
        *,
        name: str | None = None,
        user_id: str | None = None,
        **extra: Any,
    ) -> ProfileView:
        """Update a profile."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if user_id is not None:
            body["userId"] = user_id
        body.update(extra)
        return ProfileView.model_validate(
            await self._http.request("PATCH", f"/profiles/{profile_id}", json=body)
        )

    async def delete(self, profile_id: _ID) -> None:
        """Delete a profile."""
        await self._http.request("DELETE", f"/profiles/{profile_id}")
