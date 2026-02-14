from __future__ import annotations

import asyncio
import time
from typing import Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    SessionSettings,
    TaskCreatedResponse,
    TaskListResponse,
    TaskLogFileResponse,
    TaskStatusView,
    TaskView,
)

_TERMINAL_STATUSES = {"finished", "stopped", "failed"}


def _build_create_body(
    task: str,
    *,
    session_id: str | None = None,
    llm: str | None = None,
    start_url: str | None = None,
    max_steps: int | None = None,
    structured_output: str | None = None,
    metadata: dict[str, str] | None = None,
    secrets: dict[str, str] | None = None,
    allowed_domains: list[str] | None = None,
    highlight_elements: bool | None = None,
    flash_mode: bool | None = None,
    thinking: bool | None = None,
    vision: bool | str | None = None,
    system_prompt_extension: str | None = None,
    judge: bool | None = None,
    judge_ground_truth: str | None = None,
    judge_llm: str | None = None,
    skill_ids: list[str] | None = None,
    op_vault_id: str | None = None,
    session_settings: SessionSettings | None = None,
    **extra: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {"task": task}
    if session_id is not None:
        body["sessionId"] = session_id
    if llm is not None:
        body["llm"] = llm
    if start_url is not None:
        body["startUrl"] = start_url
    if max_steps is not None:
        body["maxSteps"] = max_steps
    if structured_output is not None:
        body["structuredOutput"] = structured_output
    if metadata is not None:
        body["metadata"] = metadata
    if secrets is not None:
        body["secrets"] = secrets
    if allowed_domains is not None:
        body["allowedDomains"] = allowed_domains
    if highlight_elements is not None:
        body["highlightElements"] = highlight_elements
    if flash_mode is not None:
        body["flashMode"] = flash_mode
    if thinking is not None:
        body["thinking"] = thinking
    if vision is not None:
        body["vision"] = vision
    if system_prompt_extension is not None:
        body["systemPromptExtension"] = system_prompt_extension
    if judge is not None:
        body["judge"] = judge
    if judge_ground_truth is not None:
        body["judgeGroundTruth"] = judge_ground_truth
    if judge_llm is not None:
        body["judgeLlm"] = judge_llm
    if skill_ids is not None:
        body["skillIds"] = skill_ids
    if op_vault_id is not None:
        body["opVaultId"] = op_vault_id
    if session_settings is not None:
        body["sessionSettings"] = session_settings.model_dump(by_alias=True, exclude_none=True)
    body.update(extra)
    return body


class Tasks:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        task: str,
        *,
        session_id: str | None = None,
        llm: str | None = None,
        start_url: str | None = None,
        max_steps: int | None = None,
        structured_output: str | None = None,
        metadata: dict[str, str] | None = None,
        secrets: dict[str, str] | None = None,
        allowed_domains: list[str] | None = None,
        highlight_elements: bool | None = None,
        flash_mode: bool | None = None,
        thinking: bool | None = None,
        vision: bool | str | None = None,
        system_prompt_extension: str | None = None,
        judge: bool | None = None,
        judge_ground_truth: str | None = None,
        judge_llm: str | None = None,
        skill_ids: list[str] | None = None,
        op_vault_id: str | None = None,
        session_settings: SessionSettings | None = None,
        **extra: Any,
    ) -> TaskCreatedResponse:
        """Create and start a new AI agent task."""
        body = _build_create_body(
            task,
            session_id=session_id,
            llm=llm,
            start_url=start_url,
            max_steps=max_steps,
            structured_output=structured_output,
            metadata=metadata,
            secrets=secrets,
            allowed_domains=allowed_domains,
            highlight_elements=highlight_elements,
            flash_mode=flash_mode,
            thinking=thinking,
            vision=vision,
            system_prompt_extension=system_prompt_extension,
            judge=judge,
            judge_ground_truth=judge_ground_truth,
            judge_llm=judge_llm,
            skill_ids=skill_ids,
            op_vault_id=op_vault_id,
            session_settings=session_settings,
            **extra,
        )
        return TaskCreatedResponse.model_validate(
            self._http.request("POST", "/tasks", json=body)
        )

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        session_id: str | None = None,
        filter_by: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> TaskListResponse:
        """List tasks with optional filtering."""
        return TaskListResponse.model_validate(
            self._http.request(
                "GET",
                "/tasks",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "sessionId": session_id,
                    "filterBy": filter_by,
                    "after": after,
                    "before": before,
                },
            )
        )

    def get(self, task_id: str) -> TaskView:
        """Get detailed task information."""
        return TaskView.model_validate(
            self._http.request("GET", f"/tasks/{task_id}")
        )

    def stop(self, task_id: str) -> TaskView:
        """Stop a running task."""
        return TaskView.model_validate(
            self._http.request("PATCH", f"/tasks/{task_id}", json={"action": "stop"})
        )

    def stop_task_and_session(self, task_id: str) -> TaskView:
        """Stop a running task and its associated browser session."""
        return TaskView.model_validate(
            self._http.request(
                "PATCH", f"/tasks/{task_id}", json={"action": "stop_task_and_session"}
            )
        )

    def status(self, task_id: str) -> TaskStatusView:
        """Get lightweight task status (optimized for polling)."""
        return TaskStatusView.model_validate(
            self._http.request("GET", f"/tasks/{task_id}/status")
        )

    def logs(self, task_id: str) -> TaskLogFileResponse:
        """Get secure download URL for task execution logs."""
        return TaskLogFileResponse.model_validate(
            self._http.request("GET", f"/tasks/{task_id}/logs")
        )

    def wait(self, task_id: str, *, timeout: float = 300, interval: float = 2) -> TaskView:
        """Poll until a task reaches a terminal status, then return the full TaskView."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = self.status(task_id)
            if status.status.value in _TERMINAL_STATUSES:
                return self.get(task_id)
            time.sleep(interval)
        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")


class AsyncTasks:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        task: str,
        *,
        session_id: str | None = None,
        llm: str | None = None,
        start_url: str | None = None,
        max_steps: int | None = None,
        structured_output: str | None = None,
        metadata: dict[str, str] | None = None,
        secrets: dict[str, str] | None = None,
        allowed_domains: list[str] | None = None,
        highlight_elements: bool | None = None,
        flash_mode: bool | None = None,
        thinking: bool | None = None,
        vision: bool | str | None = None,
        system_prompt_extension: str | None = None,
        judge: bool | None = None,
        judge_ground_truth: str | None = None,
        judge_llm: str | None = None,
        skill_ids: list[str] | None = None,
        op_vault_id: str | None = None,
        session_settings: SessionSettings | None = None,
        **extra: Any,
    ) -> TaskCreatedResponse:
        """Create and start a new AI agent task."""
        body = _build_create_body(
            task,
            session_id=session_id,
            llm=llm,
            start_url=start_url,
            max_steps=max_steps,
            structured_output=structured_output,
            metadata=metadata,
            secrets=secrets,
            allowed_domains=allowed_domains,
            highlight_elements=highlight_elements,
            flash_mode=flash_mode,
            thinking=thinking,
            vision=vision,
            system_prompt_extension=system_prompt_extension,
            judge=judge,
            judge_ground_truth=judge_ground_truth,
            judge_llm=judge_llm,
            skill_ids=skill_ids,
            op_vault_id=op_vault_id,
            session_settings=session_settings,
            **extra,
        )
        return TaskCreatedResponse.model_validate(
            await self._http.request("POST", "/tasks", json=body)
        )

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
        session_id: str | None = None,
        filter_by: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> TaskListResponse:
        """List tasks with optional filtering."""
        return TaskListResponse.model_validate(
            await self._http.request(
                "GET",
                "/tasks",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "sessionId": session_id,
                    "filterBy": filter_by,
                    "after": after,
                    "before": before,
                },
            )
        )

    async def get(self, task_id: str) -> TaskView:
        """Get detailed task information."""
        return TaskView.model_validate(
            await self._http.request("GET", f"/tasks/{task_id}")
        )

    async def stop(self, task_id: str) -> TaskView:
        """Stop a running task."""
        return TaskView.model_validate(
            await self._http.request("PATCH", f"/tasks/{task_id}", json={"action": "stop"})
        )

    async def stop_task_and_session(self, task_id: str) -> TaskView:
        """Stop a running task and its associated browser session."""
        return TaskView.model_validate(
            await self._http.request(
                "PATCH",
                f"/tasks/{task_id}",
                json={"action": "stop_task_and_session"},
            )
        )

    async def status(self, task_id: str) -> TaskStatusView:
        """Get lightweight task status (optimized for polling)."""
        return TaskStatusView.model_validate(
            await self._http.request("GET", f"/tasks/{task_id}/status")
        )

    async def logs(self, task_id: str) -> TaskLogFileResponse:
        """Get secure download URL for task execution logs."""
        return TaskLogFileResponse.model_validate(
            await self._http.request("GET", f"/tasks/{task_id}/logs")
        )

    async def wait(self, task_id: str, *, timeout: float = 300, interval: float = 2) -> TaskView:
        """Poll until a task reaches a terminal status, then return the full TaskView."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = await self.status(task_id)
            if status.status.value in _TERMINAL_STATUSES:
                return await self.get(task_id)
            await asyncio.sleep(interval)
        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
