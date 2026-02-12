from __future__ import annotations

from typing import Any, Optional

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    ExecuteSkillResponse,
    RefineSkillResponse,
    SkillExecutionListResponse,
    SkillExecutionOutputResponse,
    SkillListResponse,
    SkillResponse,
)


class Skills:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(self, **kwargs: Any) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("POST", "/skills", json=kwargs)
        )

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        is_public: Optional[bool] = None,
        is_enabled: Optional[bool] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> SkillListResponse:
        return SkillListResponse.model_validate(
            self._http.request(
                "GET",
                "/skills",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "isPublic": is_public,
                    "isEnabled": is_enabled,
                    "category": category,
                    "query": query,
                    "fromDate": from_date,
                    "toDate": to_date,
                },
            )
        )

    def get(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("GET", f"/skills/{skill_id}")
        )

    def update(self, skill_id: str, **kwargs: Any) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("PATCH", f"/skills/{skill_id}", json=kwargs)
        )

    def delete(self, skill_id: str) -> None:
        self._http.request("DELETE", f"/skills/{skill_id}")

    def cancel(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/cancel")
        )

    def execute(self, skill_id: str, **kwargs: Any) -> ExecuteSkillResponse:
        return ExecuteSkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/execute", json=kwargs)
        )

    def refine(self, skill_id: str, **kwargs: Any) -> RefineSkillResponse:
        return RefineSkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/refine", json=kwargs)
        )

    def rollback(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/rollback")
        )

    def executions(
        self,
        skill_id: str,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
    ) -> SkillExecutionListResponse:
        return SkillExecutionListResponse.model_validate(
            self._http.request(
                "GET",
                f"/skills/{skill_id}/executions",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                },
            )
        )

    def execution_output(self, skill_id: str, execution_id: str) -> SkillExecutionOutputResponse:
        return SkillExecutionOutputResponse.model_validate(
            self._http.request(
                "GET",
                f"/skills/{skill_id}/executions/{execution_id}/output",
            )
        )


class AsyncSkills:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, **kwargs: Any) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("POST", "/skills", json=kwargs)
        )

    async def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        is_public: Optional[bool] = None,
        is_enabled: Optional[bool] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> SkillListResponse:
        return SkillListResponse.model_validate(
            await self._http.request(
                "GET",
                "/skills",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "isPublic": is_public,
                    "isEnabled": is_enabled,
                    "category": category,
                    "query": query,
                    "fromDate": from_date,
                    "toDate": to_date,
                },
            )
        )

    async def get(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("GET", f"/skills/{skill_id}")
        )

    async def update(self, skill_id: str, **kwargs: Any) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("PATCH", f"/skills/{skill_id}", json=kwargs)
        )

    async def delete(self, skill_id: str) -> None:
        await self._http.request("DELETE", f"/skills/{skill_id}")

    async def cancel(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/cancel")
        )

    async def execute(self, skill_id: str, **kwargs: Any) -> ExecuteSkillResponse:
        return ExecuteSkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/execute", json=kwargs)
        )

    async def refine(self, skill_id: str, **kwargs: Any) -> RefineSkillResponse:
        return RefineSkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/refine", json=kwargs)
        )

    async def rollback(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/rollback")
        )

    async def executions(
        self,
        skill_id: str,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
    ) -> SkillExecutionListResponse:
        return SkillExecutionListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/skills/{skill_id}/executions",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                },
            )
        )

    async def execution_output(self, skill_id: str, execution_id: str) -> SkillExecutionOutputResponse:
        return SkillExecutionOutputResponse.model_validate(
            await self._http.request(
                "GET",
                f"/skills/{skill_id}/executions/{execution_id}/output",
            )
        )
