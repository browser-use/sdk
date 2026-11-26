from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    DefaultAction,
    NetworkPolicyDomainList,
    NetworkPolicyListResponse,
    NetworkPolicyView,
)

if TYPE_CHECKING:
    from uuid import UUID


def _build_policy_body(
    name: str | None,
    default_action: DefaultAction | Literal["allow", "block"] | None,
    allow: NetworkPolicyDomainList | None,
    block: NetworkPolicyDomainList | None,
    extra: dict[str, Any],
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if name is not None:
        body["name"] = name
    if default_action is not None:
        body["defaultAction"] = (
            default_action.value if isinstance(default_action, DefaultAction) else default_action
        )
    if allow is not None:
        body["allow"] = allow.model_dump(by_alias=True, exclude_unset=True, mode="json")
    if block is not None:
        body["block"] = block.model_dump(by_alias=True, exclude_unset=True, mode="json")
    body.update(extra)
    return body


class NetworkPolicies:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        name: str,
        *,
        default_action: DefaultAction | Literal["allow", "block"] | None = None,
        allow: NetworkPolicyDomainList | None = None,
        block: NetworkPolicyDomainList | None = None,
        **extra: Any,
    ) -> NetworkPolicyView:
        """Create a network policy."""
        body = _build_policy_body(name, default_action, allow, block, extra)
        return NetworkPolicyView.model_validate(
            self._http.request("POST", "/network-policies", json=body)
        )

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> NetworkPolicyListResponse:
        """List network policies for the project."""
        return NetworkPolicyListResponse.model_validate(
            self._http.request(
                "GET",
                "/network-policies",
                params={"pageSize": page_size, "pageNumber": page_number},
            )
        )

    def get(self, policy_id: str | UUID) -> NetworkPolicyView:
        """Get a network policy."""
        return NetworkPolicyView.model_validate(
            self._http.request("GET", f"/network-policies/{policy_id}")
        )

    def update(
        self,
        policy_id: str | UUID,
        *,
        name: str | None = None,
        default_action: DefaultAction | Literal["allow", "block"] | None = None,
        allow: NetworkPolicyDomainList | None = None,
        block: NetworkPolicyDomainList | None = None,
        **extra: Any,
    ) -> NetworkPolicyView:
        """Update a network policy."""
        body = _build_policy_body(name, default_action, allow, block, extra)
        return NetworkPolicyView.model_validate(
            self._http.request("PATCH", f"/network-policies/{policy_id}", json=body)
        )

    def delete(self, policy_id: str | UUID) -> None:
        """Delete a network policy."""
        self._http.request("DELETE", f"/network-policies/{policy_id}")


class AsyncNetworkPolicies:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        name: str,
        *,
        default_action: DefaultAction | Literal["allow", "block"] | None = None,
        allow: NetworkPolicyDomainList | None = None,
        block: NetworkPolicyDomainList | None = None,
        **extra: Any,
    ) -> NetworkPolicyView:
        """Create a network policy."""
        body = _build_policy_body(name, default_action, allow, block, extra)
        return NetworkPolicyView.model_validate(
            await self._http.request("POST", "/network-policies", json=body)
        )

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> NetworkPolicyListResponse:
        """List network policies for the project."""
        return NetworkPolicyListResponse.model_validate(
            await self._http.request(
                "GET",
                "/network-policies",
                params={"pageSize": page_size, "pageNumber": page_number},
            )
        )

    async def get(self, policy_id: str | UUID) -> NetworkPolicyView:
        """Get a network policy."""
        return NetworkPolicyView.model_validate(
            await self._http.request("GET", f"/network-policies/{policy_id}")
        )

    async def update(
        self,
        policy_id: str | UUID,
        *,
        name: str | None = None,
        default_action: DefaultAction | Literal["allow", "block"] | None = None,
        allow: NetworkPolicyDomainList | None = None,
        block: NetworkPolicyDomainList | None = None,
        **extra: Any,
    ) -> NetworkPolicyView:
        """Update a network policy."""
        body = _build_policy_body(name, default_action, allow, block, extra)
        return NetworkPolicyView.model_validate(
            await self._http.request("PATCH", f"/network-policies/{policy_id}", json=body)
        )

    async def delete(self, policy_id: str | UUID) -> None:
        """Delete a network policy."""
        await self._http.request("DELETE", f"/network-policies/{policy_id}")
