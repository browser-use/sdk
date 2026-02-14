from __future__ import annotations

import time
import asyncio
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

import httpx
from pydantic import BaseModel

from .errors import BrowserUseError

_RETRY_STATUSES = {429}
_MAX_RETRIES = 3
_BACKOFF_BASE = 0.5


def _clean_json(data: Any) -> Any:
    """Prepare data for JSON serialization."""
    if isinstance(data, dict):
        return {k: _clean_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_clean_json(v) for v in data]
    if isinstance(data, BaseModel):
        return data.model_dump(by_alias=True, exclude_none=True)
    if isinstance(data, Enum):
        return data.value
    if isinstance(data, UUID):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    return data


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
        json = _clean_json(json) if json is not None else None
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
        json = _clean_json(json) if json is not None else None
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
    """Remove None values and stringify query params."""
    if params is None:
        return None
    return {k: str(v) for k, v in params.items() if v is not None}
