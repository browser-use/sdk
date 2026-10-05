from __future__ import annotations

import time
import asyncio
import random
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

import httpx
from pydantic import BaseModel

from .errors import BrowserUseError

_RETRY_GET_STATUSES = {502, 503, 504}
_DEFAULT_MAX_RETRIES = 3
_BACKOFF_BASE = 0.5
_MAX_RETRY_DELAY = 10.0


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


def _should_retry(method: str, status_code: int) -> bool:
    return status_code == 429 or (
        method.upper() == "GET" and status_code in _RETRY_GET_STATUSES
    )


def _retry_delay(response: httpx.Response, attempt: int) -> float | None:
    """Honor Cloud's integer-second Retry-After; other formats use normal backoff."""
    raw = response.headers.get("Retry-After", "").strip()
    retry_after = float(raw) if raw.isascii() and raw.isdigit() else None
    # Timeout remains per attempt; preserve the existing ten-second delay cap.
    if retry_after is not None and retry_after > _MAX_RETRY_DELAY:
        return None
    backoff = min(_BACKOFF_BASE * (2 ** min(attempt + 1, 5)), _MAX_RETRY_DELAY)
    # Positive jitter spreads clients without violating the server's minimum.
    return min(_MAX_RETRY_DELAY, max(backoff, retry_after or 0.0) + random.random() * 0.25)


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        body = response.json()
    except Exception:
        body = None
    detail = body
    if isinstance(body, dict):
        raw = body.get("message", body.get("detail"))
    else:
        raw = None
    if raw is None:
        message = response.reason_phrase or str(response.status_code)
    elif isinstance(raw, str):
        message = raw
    else:
        import json
        message = json.dumps(raw)
    raise BrowserUseError(response.status_code, message, detail)


class SyncHttpClient:
    """Synchronous HTTP client with retry and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        self._max_retries = max_retries
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
        headers: dict[str, str] | None = None,
    ) -> Any:
        json = _clean_json(json) if json is not None else None
        cleaned_params = _clean_params(params)
        for attempt in range(self._max_retries + 1):
            response = self._client.request(
                method, path, json=json, params=cleaned_params, headers=headers
            )

            if _should_retry(method, response.status_code) and attempt < self._max_retries:
                delay = _retry_delay(response, attempt)
                if delay is not None:
                    time.sleep(delay)
                    continue

            _raise_for_status(response)
            if response.status_code == 204:
                return None
            return response.json()

        _raise_for_status(response)  # type: ignore[possibly-undefined]

    def close(self) -> None:
        self._client.close()


class AsyncHttpClient:
    """Asynchronous HTTP client with retry and error handling.

    Pass ``x402_client`` to authenticate via the x402 payment protocol instead
    of an API key. When ``x402_client`` is set, an ``x402HttpxClient`` is used
    as the underlying transport. ``api_key`` is optional in that mode — if
    non-empty, it triggers top-up behavior (backend credits the API key's
    project instead of one auto-created from the wallet).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        *,
        x402_client: Any = None,
    ) -> None:
        self._max_retries = max_retries
        if x402_client is not None:
            from .x402 import x402_async_httpx_client
            self._client = x402_async_httpx_client(
                x402_client, base_url=base_url, timeout=timeout, api_key=api_key
            )
        else:
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
        headers: dict[str, str] | None = None,
    ) -> Any:
        json = _clean_json(json) if json is not None else None
        cleaned_params = _clean_params(params)
        for attempt in range(self._max_retries + 1):
            response = await self._client.request(
                method, path, json=json, params=cleaned_params, headers=headers
            )

            if _should_retry(method, response.status_code) and attempt < self._max_retries:
                delay = _retry_delay(response, attempt)
                if delay is not None:
                    await asyncio.sleep(delay)
                    continue

            _raise_for_status(response)
            if response.status_code == 204:
                return None
            return response.json()

        _raise_for_status(response)  # type: ignore[possibly-undefined]

    async def close(self) -> None:
        await self._client.aclose()


def _clean_params(
    params: dict[str, Any] | None,
) -> dict[str, str | list[str]] | None:
    """Remove None values and stringify query params, repeating sequence values."""
    if params is None:
        return None
    cleaned: dict[str, str | list[str]] = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            cleaned[k] = [
                "true" if value is True else "false" if value is False else str(value)
                for value in v
                if value is not None
            ]
        elif isinstance(v, bool):
            cleaned[k] = "true" if v else "false"
        else:
            cleaned[k] = str(v)
    return cleaned
