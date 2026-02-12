from __future__ import annotations

from typing import Any, Optional

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    BrowserSessionListResponse,
    BrowserSessionView,
)


class Browsers:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(self, **kwargs: Any) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            self._http.request("POST", "/browsers", json=kwargs)
        )

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        filter_by: Optional[str] = None,
    ) -> BrowserSessionListResponse:
        return BrowserSessionListResponse.model_validate(
            self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                },
            )
        )

    def get(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            self._http.request("GET", f"/browsers/{session_id}")
        )

    def stop(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            self._http.request(
                "PATCH", f"/browsers/{session_id}", json={"action": "stop"}
            )
        )


class AsyncBrowsers:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, **kwargs: Any) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            await self._http.request("POST", "/browsers", json=kwargs)
        )

    async def list(
        self,
        *,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        filter_by: Optional[str] = None,
    ) -> BrowserSessionListResponse:
        return BrowserSessionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/browsers",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                    "filterBy": filter_by,
                },
            )
        )

    async def get(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            await self._http.request("GET", f"/browsers/{session_id}")
        )

    async def stop(self, session_id: str) -> BrowserSessionView:
        return BrowserSessionView.model_validate(
            await self._http.request(
                "PATCH", f"/browsers/{session_id}", json={"action": "stop"}
            )
        )
