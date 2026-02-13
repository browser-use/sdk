from __future__ import annotations

from typing import Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    CreateSkillResponse,
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

    def create(
        self,
        *,
        goal: str,
        agent_prompt: str,
        title: str | None = None,
        description: str | None = None,
        **extra: Any,
    ) -> CreateSkillResponse:
        body: dict[str, Any] = {"goal": goal, "agentPrompt": agent_prompt}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        body.update(extra)
        return CreateSkillResponse.model_validate(
            self._http.request("POST", "/skills", json=body)
        )

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        is_public: bool | None = None,
        is_enabled: bool | None = None,
        category: str | None = None,
        query: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
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

    def update(
        self,
        skill_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        categories: list[str] | None = None,
        domains: list[str] | None = None,
        is_enabled: bool | None = None,
        **extra: Any,
    ) -> SkillResponse:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if categories is not None:
            body["categories"] = categories
        if domains is not None:
            body["domains"] = domains
        if is_enabled is not None:
            body["isEnabled"] = is_enabled
        body.update(extra)
        return SkillResponse.model_validate(
            self._http.request("PATCH", f"/skills/{skill_id}", json=body)
        )

    def delete(self, skill_id: str) -> None:
        self._http.request("DELETE", f"/skills/{skill_id}")

    def cancel(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/cancel")
        )

    def execute(
        self,
        skill_id: str,
        *,
        parameters: dict[str, Any] | None = None,
        session_id: str | None = None,
        **extra: Any,
    ) -> ExecuteSkillResponse:
        body: dict[str, Any] = {}
        if parameters is not None:
            body["parameters"] = parameters
        if session_id is not None:
            body["sessionId"] = session_id
        body.update(extra)
        return ExecuteSkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/execute", json=body)
        )

    def refine(
        self,
        skill_id: str,
        *,
        feedback: str,
        test_output: str | None = None,
        test_logs: str | None = None,
        **extra: Any,
    ) -> RefineSkillResponse:
        body: dict[str, Any] = {"feedback": feedback}
        if test_output is not None:
            body["testOutput"] = test_output
        if test_logs is not None:
            body["testLogs"] = test_logs
        body.update(extra)
        return RefineSkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/refine", json=body)
        )

    def rollback(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            self._http.request("POST", f"/skills/{skill_id}/rollback")
        )

    def executions(
        self,
        skill_id: str,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
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

    async def create(
        self,
        *,
        goal: str,
        agent_prompt: str,
        title: str | None = None,
        description: str | None = None,
        **extra: Any,
    ) -> CreateSkillResponse:
        body: dict[str, Any] = {"goal": goal, "agentPrompt": agent_prompt}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        body.update(extra)
        return CreateSkillResponse.model_validate(
            await self._http.request("POST", "/skills", json=body)
        )

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        is_public: bool | None = None,
        is_enabled: bool | None = None,
        category: str | None = None,
        query: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
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

    async def update(
        self,
        skill_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        categories: list[str] | None = None,
        domains: list[str] | None = None,
        is_enabled: bool | None = None,
        **extra: Any,
    ) -> SkillResponse:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if categories is not None:
            body["categories"] = categories
        if domains is not None:
            body["domains"] = domains
        if is_enabled is not None:
            body["isEnabled"] = is_enabled
        body.update(extra)
        return SkillResponse.model_validate(
            await self._http.request("PATCH", f"/skills/{skill_id}", json=body)
        )

    async def delete(self, skill_id: str) -> None:
        await self._http.request("DELETE", f"/skills/{skill_id}")

    async def cancel(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/cancel")
        )

    async def execute(
        self,
        skill_id: str,
        *,
        parameters: dict[str, Any] | None = None,
        session_id: str | None = None,
        **extra: Any,
    ) -> ExecuteSkillResponse:
        body: dict[str, Any] = {}
        if parameters is not None:
            body["parameters"] = parameters
        if session_id is not None:
            body["sessionId"] = session_id
        body.update(extra)
        return ExecuteSkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/execute", json=body)
        )

    async def refine(
        self,
        skill_id: str,
        *,
        feedback: str,
        test_output: str | None = None,
        test_logs: str | None = None,
        **extra: Any,
    ) -> RefineSkillResponse:
        body: dict[str, Any] = {"feedback": feedback}
        if test_output is not None:
            body["testOutput"] = test_output
        if test_logs is not None:
            body["testLogs"] = test_logs
        body.update(extra)
        return RefineSkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/refine", json=body)
        )

    async def rollback(self, skill_id: str) -> SkillResponse:
        return SkillResponse.model_validate(
            await self._http.request("POST", f"/skills/{skill_id}/rollback")
        )

    async def executions(
        self,
        skill_id: str,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
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
