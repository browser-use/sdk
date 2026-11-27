from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    Harness as ScheduleHarness,
    Model as RunModel,
    Model2 as ScheduleModel,
    Mode2 as ScheduleMode,
    RunJudgeSettings,
    RunListResponse,
    ScheduleBrowserSettings,
    ScheduleListResponse,
    ScheduleSecretBinding,
    ScheduleView,
)

if TYPE_CHECKING:
    from uuid import UUID

# Use the SDK sentinel so an explicit None can be sent as JSON null.
_OMITTED: None = _UNSET  # type: ignore[assignment]


def _update_body(fields: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in fields.items() if value is not None} | extra


def _create_body(fields: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in fields.items() if value is not _UNSET}
    for key in ("browserSettings", "judge"):
        setting = body.get(key)
        if isinstance(setting, (ScheduleBrowserSettings, RunJudgeSettings)):
            body[key] = setting.model_dump(by_alias=True, mode="json", exclude_unset=True)
    if body.get("secretBindings") is not None:
        body["secretBindings"] = [
            binding.model_dump(by_alias=True, mode="json", exclude_unset=True)
            for binding in body["secretBindings"]
        ]
    return body | extra


class Schedules:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        task: str,
        *,
        cron_expr: str | None = _OMITTED,
        run_at: str | None = _OMITTED,
        timezone: str | None = None,
        session_id: str | UUID | None = _OMITTED,
        model: ScheduleModel | RunModel | str | None = None,
        model_params: dict[str, Any] | None = _OMITTED,
        output_schema: dict[str, Any] | None = _OMITTED,
        workspace_id: str | UUID | None = _OMITTED,
        browser_settings: ScheduleBrowserSettings | None = _OMITTED,
        keep_alive: int | None = _OMITTED,
        agentmail: bool | None = None,
        stripe_link_connection_id: str | UUID | None = _OMITTED,
        secret_bindings: list[ScheduleSecretBinding] | None = _OMITTED,
        op_vault_id: str | None = _OMITTED,
        op_vault_allowed_domains: list[str] | None = _OMITTED,
        judge: RunJudgeSettings | None = _OMITTED,
        max_cost_usd: float | str | None = _OMITTED,
        metadata: dict[str, str] | None = _OMITTED,
        agentcard_wallet_id: str | UUID | None = _OMITTED,
        harness: ScheduleHarness | Literal["browsercode", "bu-pi"] | None = _OMITTED,
        mode: ScheduleMode | Literal["default", "ultrafast"] | None = _OMITTED,
        **extra: Any,
    ) -> ScheduleView:
        """Schedule a task to run once or on a recurring cron."""
        body = _create_body(
            {
                "task": task,
                "cronExpr": cron_expr,
                "runAt": run_at,
                "timezone": timezone if timezone is not None else _UNSET,
                "sessionId": session_id,
                "model": model if model is not None else _UNSET,
                "modelParams": model_params,
                "outputSchema": output_schema,
                "workspaceId": workspace_id,
                "browserSettings": browser_settings,
                "keepAlive": keep_alive,
                "agentmail": agentmail if agentmail is not None else _UNSET,
                "stripeLinkConnectionId": stripe_link_connection_id,
                "secretBindings": secret_bindings,
                "opVaultId": op_vault_id,
                "opVaultAllowedDomains": op_vault_allowed_domains,
                "judge": judge,
                "maxCostUsd": max_cost_usd,
                "metadata": metadata,
                "agentcardWalletId": agentcard_wallet_id,
                "harness": harness,
                "mode": mode,
            },
            extra,
        )
        return ScheduleView.model_validate(
            self._http.request("POST", "/schedules", json=body)
        )

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        enabled: bool | None = None,
    ) -> ScheduleListResponse:
        """List project schedules with cursor-based pagination, newest first."""
        return ScheduleListResponse.model_validate(
            self._http.request(
                "GET", "/schedules", params={"cursor": cursor, "limit": limit, "enabled": enabled}
            )
        )

    def get(self, schedule_id: str | UUID) -> ScheduleView:
        """Get a schedule."""
        return ScheduleView.model_validate(
            self._http.request("GET", f"/schedules/{schedule_id}")
        )

    def update(
        self,
        schedule_id: str | UUID,
        *,
        enabled: bool | None = None,
        task: str | None = None,
        cron_expr: str | None = None,
        run_at: str | None = None,
        timezone: str | None = None,
        **extra: Any,
    ) -> ScheduleView:
        """Update a schedule's task, timing, time zone, or enabled state."""
        body = _update_body(
            {
                "enabled": enabled,
                "task": task,
                "cronExpr": cron_expr,
                "runAt": run_at,
                "timezone": timezone,
            },
            extra,
        )
        return ScheduleView.model_validate(
            self._http.request("PATCH", f"/schedules/{schedule_id}", json=body)
        )

    def delete(self, schedule_id: str | UUID) -> None:
        """Delete a schedule."""
        self._http.request("DELETE", f"/schedules/{schedule_id}")

    def runs(
        self,
        schedule_id: str | UUID,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        metadata: list[str] | None = None,
    ) -> RunListResponse:
        """List the runs started by a schedule, newest first."""
        return RunListResponse.model_validate(
            self._http.request(
                "GET",
                f"/schedules/{schedule_id}/runs",
                params={
                    "cursor": cursor,
                    "limit": limit,
                    "metadata": metadata,
                },
            )
        )


class AsyncSchedules:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        task: str,
        *,
        cron_expr: str | None = _OMITTED,
        run_at: str | None = _OMITTED,
        timezone: str | None = None,
        session_id: str | UUID | None = _OMITTED,
        model: ScheduleModel | RunModel | str | None = None,
        model_params: dict[str, Any] | None = _OMITTED,
        output_schema: dict[str, Any] | None = _OMITTED,
        workspace_id: str | UUID | None = _OMITTED,
        browser_settings: ScheduleBrowserSettings | None = _OMITTED,
        keep_alive: int | None = _OMITTED,
        agentmail: bool | None = None,
        stripe_link_connection_id: str | UUID | None = _OMITTED,
        secret_bindings: list[ScheduleSecretBinding] | None = _OMITTED,
        op_vault_id: str | None = _OMITTED,
        op_vault_allowed_domains: list[str] | None = _OMITTED,
        judge: RunJudgeSettings | None = _OMITTED,
        max_cost_usd: float | str | None = _OMITTED,
        metadata: dict[str, str] | None = _OMITTED,
        agentcard_wallet_id: str | UUID | None = _OMITTED,
        harness: ScheduleHarness | Literal["browsercode", "bu-pi"] | None = _OMITTED,
        mode: ScheduleMode | Literal["default", "ultrafast"] | None = _OMITTED,
        **extra: Any,
    ) -> ScheduleView:
        """Schedule a task to run once or on a recurring cron."""
        body = _create_body(
            {
                "task": task,
                "cronExpr": cron_expr,
                "runAt": run_at,
                "timezone": timezone if timezone is not None else _UNSET,
                "sessionId": session_id,
                "model": model if model is not None else _UNSET,
                "modelParams": model_params,
                "outputSchema": output_schema,
                "workspaceId": workspace_id,
                "browserSettings": browser_settings,
                "keepAlive": keep_alive,
                "agentmail": agentmail if agentmail is not None else _UNSET,
                "stripeLinkConnectionId": stripe_link_connection_id,
                "secretBindings": secret_bindings,
                "opVaultId": op_vault_id,
                "opVaultAllowedDomains": op_vault_allowed_domains,
                "judge": judge,
                "maxCostUsd": max_cost_usd,
                "metadata": metadata,
                "agentcardWalletId": agentcard_wallet_id,
                "harness": harness,
                "mode": mode,
            },
            extra,
        )
        return ScheduleView.model_validate(
            await self._http.request("POST", "/schedules", json=body)
        )

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        enabled: bool | None = None,
    ) -> ScheduleListResponse:
        """List project schedules with cursor-based pagination, newest first."""
        return ScheduleListResponse.model_validate(
            await self._http.request(
                "GET", "/schedules", params={"cursor": cursor, "limit": limit, "enabled": enabled}
            )
        )

    async def get(self, schedule_id: str | UUID) -> ScheduleView:
        """Get a schedule."""
        return ScheduleView.model_validate(
            await self._http.request("GET", f"/schedules/{schedule_id}")
        )

    async def update(
        self,
        schedule_id: str | UUID,
        *,
        enabled: bool | None = None,
        task: str | None = None,
        cron_expr: str | None = None,
        run_at: str | None = None,
        timezone: str | None = None,
        **extra: Any,
    ) -> ScheduleView:
        """Update a schedule's task, timing, time zone, or enabled state."""
        body = _update_body(
            {
                "enabled": enabled,
                "task": task,
                "cronExpr": cron_expr,
                "runAt": run_at,
                "timezone": timezone,
            },
            extra,
        )
        return ScheduleView.model_validate(
            await self._http.request("PATCH", f"/schedules/{schedule_id}", json=body)
        )

    async def delete(self, schedule_id: str | UUID) -> None:
        """Delete a schedule."""
        await self._http.request("DELETE", f"/schedules/{schedule_id}")

    async def runs(
        self,
        schedule_id: str | UUID,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        metadata: list[str] | None = None,
    ) -> RunListResponse:
        """List the runs started by a schedule, newest first."""
        return RunListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/schedules/{schedule_id}/runs",
                params={
                    "cursor": cursor,
                    "limit": limit,
                    "metadata": metadata,
                },
            )
        )
