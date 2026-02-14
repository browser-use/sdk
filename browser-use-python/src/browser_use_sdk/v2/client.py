from __future__ import annotations

import json
import os
from collections.abc import Awaitable
from typing import Any, TypeVar, overload

from pydantic import BaseModel

from .._core.http import AsyncHttpClient, SyncHttpClient
from ..generated.v2.models import SessionSettings, TaskCreatedResponse
from .resources.billing import AsyncBilling, Billing
from .resources.browsers import AsyncBrowsers, Browsers
from .resources.files import AsyncFiles, Files
from .resources.marketplace import AsyncMarketplace, Marketplace
from .resources.profiles import AsyncProfiles, Profiles
from .resources.sessions import AsyncSessions, Sessions
from .resources.skills import AsyncSkills, Skills
from .resources.tasks import AsyncTasks, Tasks
from .helpers import AsyncTaskRun, TaskResult, TaskStream, _poll_output

_V2_BASE_URL = "https://api.browser-use.com/api/v2"

T = TypeVar("T")


class BrowserUse:
    """Synchronous Browser Use v2 client."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
            )
        self._http = SyncHttpClient(
            base_url=base_url or _V2_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.billing = Billing(self._http)
        self.tasks = Tasks(self._http)
        self.sessions = Sessions(self._http)
        self.files = Files(self._http)
        self.profiles = Profiles(self._http)
        self.browsers = Browsers(self._http)
        self.skills = Skills(self._http)
        self.marketplace = Marketplace(self._http)

    @overload
    def run(
        self,
        task: str,
        *,
        schema: type[T],
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> TaskResult[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        output_schema: type[T],
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> TaskResult[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> TaskResult[str]: ...

    def run(
        self,
        task: str,
        *,
        schema: type[Any] | None = None,
        output_schema: type[Any] | None = None,
        session_id: str | None = None,
        llm: str | None = None,
        start_url: str | None = None,
        max_steps: int | None = None,
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
    ) -> Any:
        """Run an AI agent task. Blocks until complete, returns a TaskResult."""
        resolved_schema = schema or output_schema
        if resolved_schema is not None and issubclass(resolved_schema, BaseModel):
            extra["structured_output"] = json.dumps(resolved_schema.model_json_schema())

        data = self.tasks.create(
            task,
            session_id=session_id,
            llm=llm,
            start_url=start_url,
            max_steps=max_steps,
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
        return _poll_output(self.tasks, str(data.id), resolved_schema)

    @overload
    def stream(
        self,
        task: str,
        *,
        schema: type[T],
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> TaskStream[T]: ...

    @overload
    def stream(
        self,
        task: str,
        *,
        output_schema: type[T],
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> TaskStream[T]: ...

    @overload
    def stream(
        self,
        task: str,
        *,
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> TaskStream[str]: ...

    def stream(
        self,
        task: str,
        *,
        schema: type[Any] | None = None,
        output_schema: type[Any] | None = None,
        session_id: str | None = None,
        llm: str | None = None,
        start_url: str | None = None,
        max_steps: int | None = None,
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
    ) -> TaskStream[Any]:
        """Run a task and yield steps as they happen."""
        resolved_schema = schema or output_schema
        if resolved_schema is not None and issubclass(resolved_schema, BaseModel):
            extra["structured_output"] = json.dumps(resolved_schema.model_json_schema())

        data = self.tasks.create(
            task,
            session_id=session_id,
            llm=llm,
            start_url=start_url,
            max_steps=max_steps,
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
        return TaskStream(data, self.tasks, resolved_schema)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> BrowserUse:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncBrowserUse:
    """Asynchronous Browser Use v2 client."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        resolved_key = api_key or os.environ.get("BROWSER_USE_API_KEY") or ""
        if not resolved_key:
            raise ValueError(
                "No API key provided. Pass api_key or set BROWSER_USE_API_KEY."
            )
        self._http = AsyncHttpClient(
            base_url=base_url or _V2_BASE_URL,
            api_key=resolved_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.billing = AsyncBilling(self._http)
        self.tasks = AsyncTasks(self._http)
        self.sessions = AsyncSessions(self._http)
        self.files = AsyncFiles(self._http)
        self.profiles = AsyncProfiles(self._http)
        self.browsers = AsyncBrowsers(self._http)
        self.skills = AsyncSkills(self._http)
        self.marketplace = AsyncMarketplace(self._http)

    @overload
    def run(
        self,
        task: str,
        *,
        schema: type[T],
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> AsyncTaskRun[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        output_schema: type[T],
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> AsyncTaskRun[T]: ...

    @overload
    def run(
        self,
        task: str,
        *,
        session_id: str | None = ...,
        llm: str | None = ...,
        start_url: str | None = ...,
        max_steps: int | None = ...,
        metadata: dict[str, str] | None = ...,
        secrets: dict[str, str] | None = ...,
        allowed_domains: list[str] | None = ...,
        highlight_elements: bool | None = ...,
        flash_mode: bool | None = ...,
        thinking: bool | None = ...,
        vision: bool | str | None = ...,
        system_prompt_extension: str | None = ...,
        judge: bool | None = ...,
        judge_ground_truth: str | None = ...,
        judge_llm: str | None = ...,
        skill_ids: list[str] | None = ...,
        op_vault_id: str | None = ...,
        session_settings: SessionSettings | None = ...,
        **extra: Any,
    ) -> AsyncTaskRun[str]: ...

    def run(
        self,
        task: str,
        *,
        schema: type[Any] | None = None,
        output_schema: type[Any] | None = None,
        session_id: str | None = None,
        llm: str | None = None,
        start_url: str | None = None,
        max_steps: int | None = None,
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
    ) -> AsyncTaskRun[Any]:
        """Run an AI agent task. ``await`` for a TaskResult, or ``async for`` for steps."""
        resolved_schema = schema or output_schema
        if resolved_schema is not None and issubclass(resolved_schema, BaseModel):
            extra["structured_output"] = json.dumps(resolved_schema.model_json_schema())

        def create_fn() -> Awaitable[TaskCreatedResponse]:
            return self.tasks.create(
                task,
                session_id=session_id,
                llm=llm,
                start_url=start_url,
                max_steps=max_steps,
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

        return AsyncTaskRun(create_fn, self.tasks, resolved_schema)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncBrowserUse:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
