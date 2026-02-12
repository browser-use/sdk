from __future__ import annotations

from typing import Any, Optional

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import ProfileListResponse, ProfileView


class Profiles:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(self, **kwargs: Any) -> ProfileView:
        return ProfileView.model_validate(
            self._http.request("POST", "/profiles", json=kwargs)
        )

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
    ) -> ProfileListResponse:
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
        return ProfileView.model_validate(
            self._http.request("GET", f"/profiles/{profile_id}")
        )

    def update(self, profile_id: str, **kwargs: Any) -> ProfileView:
        return ProfileView.model_validate(
            self._http.request("PATCH", f"/profiles/{profile_id}", json=kwargs)
        )

    def delete(self, profile_id: str) -> None:
        self._http.request("DELETE", f"/profiles/{profile_id}")


class AsyncProfiles:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, **kwargs: Any) -> ProfileView:
        return ProfileView.model_validate(
            await self._http.request("POST", "/profiles", json=kwargs)
        )

    async def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
    ) -> ProfileListResponse:
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
        return ProfileView.model_validate(
            await self._http.request("GET", f"/profiles/{profile_id}")
        )

    async def update(self, profile_id: str, **kwargs: Any) -> ProfileView:
        return ProfileView.model_validate(
            await self._http.request("PATCH", f"/profiles/{profile_id}", json=kwargs)
        )

    async def delete(self, profile_id: str) -> None:
        await self._http.request("DELETE", f"/profiles/{profile_id}")
