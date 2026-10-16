from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    ProfileListResponse,
    ProfileView,
)

if TYPE_CHECKING:
    from uuid import UUID


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
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> ProfileListResponse:
        """List profiles for the authenticated project."""
        return ProfileListResponse.model_validate(
            self._http.request(
                "GET",
                "/profiles",
                params={"query": query, "pageSize": page_size, "pageNumber": page_number},
            )
        )

    def get(self, profile_id: str | UUID) -> ProfileView:
        """Get profile details."""
        return ProfileView.model_validate(
            self._http.request("GET", f"/profiles/{profile_id}")
        )

    def update(
        self,
        profile_id: str | UUID,
        *,
        name: str | None = _UNSET,  # type: ignore[assignment]
        user_id: str | None = _UNSET,  # type: ignore[assignment]
        **extra: Any,
    ) -> ProfileView:
        """Update a profile; pass ``None`` to clear ``name`` or ``user_id``."""
        body: dict[str, Any] = {}
        if name is not _UNSET:
            body["name"] = name
        if user_id is not _UNSET:
            body["userId"] = user_id
        body.update(extra)
        return ProfileView.model_validate(
            self._http.request("PATCH", f"/profiles/{profile_id}", json=body)
        )

    def delete(self, profile_id: str | UUID) -> None:
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
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> ProfileListResponse:
        """List profiles for the authenticated project."""
        return ProfileListResponse.model_validate(
            await self._http.request(
                "GET",
                "/profiles",
                params={"query": query, "pageSize": page_size, "pageNumber": page_number},
            )
        )

    async def get(self, profile_id: str | UUID) -> ProfileView:
        """Get profile details."""
        return ProfileView.model_validate(
            await self._http.request("GET", f"/profiles/{profile_id}")
        )

    async def update(
        self,
        profile_id: str | UUID,
        *,
        name: str | None = _UNSET,  # type: ignore[assignment]
        user_id: str | None = _UNSET,  # type: ignore[assignment]
        **extra: Any,
    ) -> ProfileView:
        """Update a profile; pass ``None`` to clear ``name`` or ``user_id``."""
        body: dict[str, Any] = {}
        if name is not _UNSET:
            body["name"] = name
        if user_id is not _UNSET:
            body["userId"] = user_id
        body.update(extra)
        return ProfileView.model_validate(
            await self._http.request("PATCH", f"/profiles/{profile_id}", json=body)
        )

    async def delete(self, profile_id: str | UUID) -> None:
        """Delete a profile."""
        await self._http.request("DELETE", f"/profiles/{profile_id}")
