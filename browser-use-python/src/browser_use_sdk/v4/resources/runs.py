from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    RunAttachmentsResponse,
    RunBrowserSettings,
    RunCreateResponse,
    RunEvent,
    RunEventsResponse,
    RunJudgeSettings,
    RunListResponse,
    RunStatusResponse,
    RunSummary,
    SecretBinding,
)

if TYPE_CHECKING:
    from uuid import UUID

# Terminal run statuses — closed enum in the v4 spec.
_TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


def _build_create_body(
    task: str,
    model: str | None,
    model_params: dict[str, Any] | None,
    session_id: str | UUID | None,
    workspace_id: str | UUID | None,
    browser_settings: RunBrowserSettings | dict[str, Any] | None,
    agentmail: bool | None,
    attached_file_ids: list[str | UUID] | None,
    secret_bindings: list[SecretBinding | dict[str, Any]] | None,
    judge: RunJudgeSettings | dict[str, Any] | None,
    max_cost_usd: float | str | None,
    extra: dict[str, Any],
) -> dict[str, Any]:
    body: dict[str, Any] = {"task": task}
    if model is not None:
        body["model"] = model
    if model_params is not None:
        body["modelParams"] = model_params
    if session_id is not None:
        body["sessionId"] = str(session_id)
    if workspace_id is not None:
        body["workspaceId"] = str(workspace_id)
    if browser_settings is not None:
        if isinstance(browser_settings, RunBrowserSettings):
            body["browserSettings"] = browser_settings.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            )
        else:
            body["browserSettings"] = browser_settings
    if agentmail is not None:
        body["agentmail"] = agentmail
    if attached_file_ids is not None:
        body["attachedFileIds"] = [str(f) for f in attached_file_ids]
    if secret_bindings is not None:
        body["secretBindings"] = [
            {
                "alias": binding.alias,
                "source": {
                    "type": binding.source.type,
                    "value": binding.source.value.get_secret_value(),
                },
                "allowedDomains": binding.allowed_domains,
            }
            if isinstance(binding, SecretBinding)
            else binding
            for binding in secret_bindings
        ]
    if judge is not None:
        if isinstance(judge, RunJudgeSettings):
            body["judge"] = judge.model_dump(
                by_alias=True, exclude_none=True, mode="json"
            )
        else:
            body["judge"] = judge
    if max_cost_usd is not None:
        body["maxCostUsd"] = max_cost_usd
    body.update(extra)
    return body


class Runs:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        task: str,
        *,
        model: str | None = None,
        model_params: dict[str, Any] | None = None,
        session_id: str | UUID | None = None,
        workspace_id: str | UUID | None = None,
        browser_settings: RunBrowserSettings | dict[str, Any] | None = None,
        agentmail: bool | None = None,
        attached_file_ids: list[str | UUID] | None = None,
        secret_bindings: list[SecretBinding | dict[str, Any]] | None = None,
        judge: RunJudgeSettings | dict[str, Any] | None = None,
        max_cost_usd: float | str | None = None,
        **extra: Any,
    ) -> RunCreateResponse:
        """Create a run (a new session, or a follow-up turn when session_id is set)."""
        body = _build_create_body(
            task,
            model,
            model_params,
            session_id,
            workspace_id,
            browser_settings,
            agentmail,
            attached_file_ids,
            secret_bindings,
            judge,
            max_cost_usd,
            extra,
        )
        return RunCreateResponse.model_validate(
            self._http.request("POST", "/runs", json=body)
        )

    def list(
        self,
        *,
        session_id: str | UUID | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> RunListResponse:
        """List runs with cursor-based pagination, most recent first."""
        return RunListResponse.model_validate(
            self._http.request(
                "GET",
                "/runs",
                params={
                    "sessionId": str(session_id) if session_id is not None else None,
                    "cursor": cursor,
                    "limit": limit,
                },
            )
        )

    def get(self, run_id: str | UUID) -> RunSummary:
        """Get the full run summary."""
        return RunSummary.model_validate(self._http.request("GET", f"/runs/{run_id}"))

    def status(self, run_id: str | UUID) -> RunStatusResponse:
        """Get just the run's status — the cheap poll target."""
        return RunStatusResponse.model_validate(
            self._http.request("GET", f"/runs/{run_id}/status")
        )

    def events(
        self,
        run_id: str | UUID,
        *,
        after: int | None = None,
        limit: int | None = None,
    ) -> RunEventsResponse:
        """List run events incrementally — pass ``after`` from the previous page's next_after."""
        return RunEventsResponse.model_validate(
            self._http.request(
                "GET",
                f"/runs/{run_id}/events",
                params={
                    "after": after,
                    "limit": limit,
                },
            )
        )

    def wait_for_event(
        self,
        run_id: str | UUID,
        event_type: str,
        *,
        timeout: float = 300,
        interval: float = 1,
        after: int | None = None,
        limit: int = 100,
    ) -> RunEvent:
        """Poll run events until ``event_type`` appears."""
        deadline = time.monotonic() + timeout
        while True:
            page = self.events(run_id, after=after, limit=limit)
            event = next(
                (item for item in page.events if item.type == event_type), None
            )
            if event is not None:
                return event
            after = page.next_after if page.next_after is not None else after
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Run {run_id} did not emit {event_type} within {timeout}s"
                )
            time.sleep(min(interval, remaining))

    def cancel(self, run_id: str | UUID) -> RunSummary:
        """Cancel a run. Returns the updated run summary."""
        return RunSummary.model_validate(
            self._http.request("POST", f"/runs/{run_id}/cancel")
        )

    def attachments(self, run_id: str | UUID) -> RunAttachmentsResponse:
        """List files the agent attached to the run."""
        return RunAttachmentsResponse.model_validate(
            self._http.request("GET", f"/runs/{run_id}/attachments")
        )

    def wait_for_completion(
        self,
        run_id: str | UUID,
        *,
        timeout: float = 14400,
        interval: float = 2,
    ) -> RunSummary:
        """Poll the run's status until terminal, then return the full run summary.

        Polls GET /runs/{id}/status (tiny indexed lookup) until the status is
        completed, failed, or cancelled, then fetches the full RunSummary once.
        This is the loop the v4 API was designed for.

        Usage::

            created = client.runs.create("Find the top HN post")
            run = client.runs.wait_for_completion(created.id)
            print(run.status, run.result)
        """
        deadline = time.monotonic() + timeout
        # A terminal status is always returned, even if the status() call itself
        # finished slightly past the deadline — a completed run is never thrown
        # away. Only a non-terminal status seen past the deadline is a timeout.
        while True:
            status = self.status(run_id)
            if status.status.value in _TERMINAL_STATUSES:
                return self.get(run_id)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")
            time.sleep(min(interval, remaining))


class AsyncRuns:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        task: str,
        *,
        model: str | None = None,
        model_params: dict[str, Any] | None = None,
        session_id: str | UUID | None = None,
        workspace_id: str | UUID | None = None,
        browser_settings: RunBrowserSettings | dict[str, Any] | None = None,
        agentmail: bool | None = None,
        attached_file_ids: list[str | UUID] | None = None,
        secret_bindings: list[SecretBinding | dict[str, Any]] | None = None,
        judge: RunJudgeSettings | dict[str, Any] | None = None,
        max_cost_usd: float | str | None = None,
        **extra: Any,
    ) -> RunCreateResponse:
        """Create a run (a new session, or a follow-up turn when session_id is set)."""
        body = _build_create_body(
            task,
            model,
            model_params,
            session_id,
            workspace_id,
            browser_settings,
            agentmail,
            attached_file_ids,
            secret_bindings,
            judge,
            max_cost_usd,
            extra,
        )
        return RunCreateResponse.model_validate(
            await self._http.request("POST", "/runs", json=body)
        )

    async def list(
        self,
        *,
        session_id: str | UUID | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> RunListResponse:
        """List runs with cursor-based pagination, most recent first."""
        return RunListResponse.model_validate(
            await self._http.request(
                "GET",
                "/runs",
                params={
                    "sessionId": str(session_id) if session_id is not None else None,
                    "cursor": cursor,
                    "limit": limit,
                },
            )
        )

    async def get(self, run_id: str | UUID) -> RunSummary:
        """Get the full run summary."""
        return RunSummary.model_validate(
            await self._http.request("GET", f"/runs/{run_id}")
        )

    async def status(self, run_id: str | UUID) -> RunStatusResponse:
        """Get just the run's status — the cheap poll target."""
        return RunStatusResponse.model_validate(
            await self._http.request("GET", f"/runs/{run_id}/status")
        )

    async def events(
        self,
        run_id: str | UUID,
        *,
        after: int | None = None,
        limit: int | None = None,
    ) -> RunEventsResponse:
        """List run events incrementally — pass ``after`` from the previous page's next_after."""
        return RunEventsResponse.model_validate(
            await self._http.request(
                "GET",
                f"/runs/{run_id}/events",
                params={
                    "after": after,
                    "limit": limit,
                },
            )
        )

    async def wait_for_event(
        self,
        run_id: str | UUID,
        event_type: str,
        *,
        timeout: float = 300,
        interval: float = 1,
        after: int | None = None,
        limit: int = 100,
    ) -> RunEvent:
        """Poll run events until ``event_type`` appears."""
        deadline = time.monotonic() + timeout
        while True:
            page = await self.events(run_id, after=after, limit=limit)
            event = next(
                (item for item in page.events if item.type == event_type), None
            )
            if event is not None:
                return event
            after = page.next_after if page.next_after is not None else after
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(
                    f"Run {run_id} did not emit {event_type} within {timeout}s"
                )
            await asyncio.sleep(min(interval, remaining))

    async def cancel(self, run_id: str | UUID) -> RunSummary:
        """Cancel a run. Returns the updated run summary."""
        return RunSummary.model_validate(
            await self._http.request("POST", f"/runs/{run_id}/cancel")
        )

    async def attachments(self, run_id: str | UUID) -> RunAttachmentsResponse:
        """List files the agent attached to the run."""
        return RunAttachmentsResponse.model_validate(
            await self._http.request("GET", f"/runs/{run_id}/attachments")
        )

    async def wait_for_completion(
        self,
        run_id: str | UUID,
        *,
        timeout: float = 14400,
        interval: float = 2,
    ) -> RunSummary:
        """Poll the run's status until terminal, then return the full run summary.

        Polls GET /runs/{id}/status (tiny indexed lookup) until the status is
        completed, failed, or cancelled, then fetches the full RunSummary once.
        This is the loop the v4 API was designed for.

        Usage::

            created = await client.runs.create("Find the top HN post")
            run = await client.runs.wait_for_completion(created.id)
            print(run.status, run.result)
        """
        deadline = time.monotonic() + timeout
        # A terminal status is always returned, even if the status() call itself
        # finished slightly past the deadline — a completed run is never thrown
        # away. Only a non-terminal status seen past the deadline is a timeout.
        while True:
            status = await self.status(run_id)
            if status.status.value in _TERMINAL_STATUSES:
                return await self.get(run_id)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")
            await asyncio.sleep(min(interval, remaining))
