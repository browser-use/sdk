from __future__ import annotations

from typing import Any, Optional

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    ExecuteSkillResponse,
    MarketplaceSkillListResponse,
    MarketplaceSkillResponse,
    SkillResponse,
)


class Marketplace:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> MarketplaceSkillListResponse:
        return MarketplaceSkillListResponse.model_validate(
            self._http.request(
                "GET",
                "/marketplace/skills",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "category": category,
                    "query": query,
                    "fromDate": from_date,
                    "toDate": to_date,
                },
            )
        )

    def get(self, slug: str) -> MarketplaceSkillResponse:
        return MarketplaceSkillResponse.model_validate(
            self._http.request("GET", f"/marketplace/skills/{slug}")
        )

    def clone(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("POST", f"/marketplace/skills/{skill_id}/clone")
        )

    def execute(self, skill_id: str, **kwargs: Any) -> ExecuteSkillResponse:
        return ExecuteSkillResponse.model_validate(
            self._http.request(
                "POST", f"/marketplace/skills/{skill_id}/execute", json=kwargs
            )
        )


class AsyncMarketplace:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> MarketplaceSkillListResponse:
        return MarketplaceSkillListResponse.model_validate(
            await self._http.request(
                "GET",
                "/marketplace/skills",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "category": category,
                    "query": query,
                    "fromDate": from_date,
                    "toDate": to_date,
                },
            )
        )

    async def get(self, slug: str) -> MarketplaceSkillResponse:
        return MarketplaceSkillResponse.model_validate(
            await self._http.request("GET", f"/marketplace/skills/{slug}")
        )

    async def clone(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("POST", f"/marketplace/skills/{skill_id}/clone")
        )

    async def execute(self, skill_id: str, **kwargs: Any) -> ExecuteSkillResponse:
        return ExecuteSkillResponse.model_validate(
            await self._http.request(
                "POST", f"/marketplace/skills/{skill_id}/execute", json=kwargs
            )
        )
