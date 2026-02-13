from __future__ import annotations

from typing import Any

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
        page_size: int | None = None,
        page_number: int | None = None,
        category: str | None = None,
        query: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> MarketplaceSkillListResponse:
        """List marketplace skills."""
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
        """Get marketplace skill details."""
        return MarketplaceSkillResponse.model_validate(
            self._http.request("GET", f"/marketplace/skills/{slug}")
        )

    def clone(self, skill_id: str) -> SkillResponse:
        """Clone a marketplace skill to your account."""
        return SkillResponse.model_validate(
            self._http.request("POST", f"/marketplace/skills/{skill_id}/clone")
        )

    def execute(
        self,
        skill_id: str,
        *,
        parameters: dict[str, Any] | None = None,
        session_id: str | None = None,
        **extra: Any,
    ) -> ExecuteSkillResponse:
        """Execute a marketplace skill."""
        body: dict[str, Any] = {}
        if parameters is not None:
            body["parameters"] = parameters
        if session_id is not None:
            body["sessionId"] = session_id
        body.update(extra)
        return ExecuteSkillResponse.model_validate(
            self._http.request(
                "POST", f"/marketplace/skills/{skill_id}/execute", json=body
            )
        )


class AsyncMarketplace:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        category: str | None = None,
        query: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> MarketplaceSkillListResponse:
        """List marketplace skills."""
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
        """Get marketplace skill details."""
        return MarketplaceSkillResponse.model_validate(
            await self._http.request("GET", f"/marketplace/skills/{slug}")
        )

    async def clone(self, skill_id: str) -> SkillResponse:
        """Clone a marketplace skill to your account."""
        return SkillResponse.model_validate(
            await self._http.request("POST", f"/marketplace/skills/{skill_id}/clone")
        )

    async def execute(
        self,
        skill_id: str,
        *,
        parameters: dict[str, Any] | None = None,
        session_id: str | None = None,
        **extra: Any,
    ) -> ExecuteSkillResponse:
        """Execute a marketplace skill."""
        body: dict[str, Any] = {}
        if parameters is not None:
            body["parameters"] = parameters
        if session_id is not None:
            body["sessionId"] = session_id
        body.update(extra)
        return ExecuteSkillResponse.model_validate(
            await self._http.request(
                "POST", f"/marketplace/skills/{skill_id}/execute", json=body
            )
        )
