from __future__ import annotations

import time
import asyncio
from typing import Any

import httpx

from .errors import BrowserUseError

_RETRY_STATUSES = {429}
_MAX_RETRIES = 3
_BACKOFF_BASE = 0.5


def _should_retry(status_code: int) -> bool:
    return status_code in _RETRY_STATUSES


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        body = response.json()
    except Exception:
        body = None
    message = ""
    detail = body
    if isinstance(body, dict):
        message = body.get("message", body.get("detail", response.reason_phrase or ""))
    else:
        message = response.reason_phrase or str(response.status_code)
    raise BrowserUseError(response.status_code, message, detail)


class SyncHttpClient:
    """Synchronous HTTP client with retry and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={"X-Browser-Use-API-Key": api_key},
            timeout=timeout,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        params = _clean_params(params)
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
                response = self._client.request(method, path, json=json, params=params)
            except httpx.TransportError as exc:
                last_exc = exc
                time.sleep(min(_BACKOFF_BASE * (2 ** attempt), 10))
                continue

            if _should_retry(response.status_code) and attempt < _MAX_RETRIES - 1:
                time.sleep(min(_BACKOFF_BASE * (2 ** attempt), 10))
                continue

            _raise_for_status(response)
            if response.status_code == 204:
                return None
            return response.json()

        raise last_exc  # type: ignore[misc]

    def close(self) -> None:
        self._client.close()


class AsyncHttpClient:
    """Asynchronous HTTP client with retry and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-Browser-Use-API-Key": api_key},
            timeout=timeout,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        params = _clean_params(params)
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
                response = await self._client.request(method, path, json=json, params=params)
            except httpx.TransportError as exc:
                last_exc = exc
                await asyncio.sleep(min(_BACKOFF_BASE * (2 ** attempt), 10))
                continue

            if _should_retry(response.status_code) and attempt < _MAX_RETRIES - 1:
                await asyncio.sleep(min(_BACKOFF_BASE * (2 ** attempt), 10))
                continue

            _raise_for_status(response)
            if response.status_code == 204:
                return None
            return response.json()

        raise last_exc  # type: ignore[misc]

    async def close(self) -> None:
        await self._client.aclose()


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove None values from query params."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
