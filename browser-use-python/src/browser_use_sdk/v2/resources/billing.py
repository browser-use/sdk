from __future__ import annotations

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import AccountView


class Billing:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def account(self) -> AccountView:
        return AccountView.model_validate(
            self._http.request("GET", "/billing/account")
        )


class AsyncBilling:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def account(self) -> AccountView:
        return AccountView.model_validate(
            await self._http.request("GET", "/billing/account")
        )
