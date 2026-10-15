from __future__ import annotations

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import AgentCardWalletListResponse, StripeLinkStatusResponse


class Wallets:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def agentcard(self) -> AgentCardWalletListResponse:
        """List the project's active AgentCard wallets, newest first."""
        return AgentCardWalletListResponse.model_validate(
            self._http.request("GET", "/agentcard/wallets")
        )

    def stripe_link(self) -> StripeLinkStatusResponse:
        """Get the project's Stripe Link connection; pass its id as ``stripe_link_connection_id``."""
        return StripeLinkStatusResponse.model_validate(
            self._http.request("GET", "/stripe-link")
        )


class AsyncWallets:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def agentcard(self) -> AgentCardWalletListResponse:
        """List the project's active AgentCard wallets, newest first."""
        return AgentCardWalletListResponse.model_validate(
            await self._http.request("GET", "/agentcard/wallets")
        )

    async def stripe_link(self) -> StripeLinkStatusResponse:
        """Get the project's Stripe Link connection; pass its id as ``stripe_link_connection_id``."""
        return StripeLinkStatusResponse.model_validate(
            await self._http.request("GET", "/stripe-link")
        )
