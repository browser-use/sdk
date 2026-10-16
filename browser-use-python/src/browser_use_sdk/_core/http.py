from __future__ import annotations

import time
import asyncio
import random
import ssl
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

import httpx
from pydantic import BaseModel

from .errors import APIKeySpendLimitError, BrowserUseError

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


# GET only: a write may have reached the server. Read timeouts are excluded so a hang fails after one timeout.
_RETRY_GET_TRANSPORT = (httpx.NetworkError, httpx.RemoteProtocolError, httpx.ConnectTimeout)


def _is_cert_error(error: BaseException | None) -> bool:
    # httpx chains the ssl error through httpcore, as __cause__ or __context__.
    while error is not None:
        if isinstance(error, ssl.SSLCertVerificationError):
            return True
        error = error.__cause__ or error.__context__
    return False


def _should_retry_transport(method: str, error: httpx.TransportError) -> bool:
    return method.upper() == "GET" and isinstance(error, _RETRY_GET_TRANSPORT) and not _is_cert_error(error)


def _backoff_delay(attempt: int) -> float:
    backoff = min(_BACKOFF_BASE * (2 ** min(attempt + 1, 5)), _MAX_RETRY_DELAY)
    return min(_MAX_RETRY_DELAY, backoff + random.random() * 0.25)


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
    fields: dict[str, Any] = raw if isinstance(raw, dict) else {}
    if isinstance(fields.get("message"), str):
        raw = fields["message"]
    if raw is None:
        message = response.reason_phrase or str(response.status_code)
    elif isinstance(raw, str):
        message = raw
    else:
        import json
        message = json.dumps(raw)
    header = response.headers.get("Retry-After", "").strip()
    retry_after = int(header) if header.isascii() and header.isdigit() else None
    if response.status_code == 402 and fields.get("code") == _SPEND_LIMIT_CODE:
        raise APIKeySpendLimitError(
            response.status_code,
            message,
            detail,
            retry_after,
            code=_SPEND_LIMIT_CODE,
            cap=fields.get("cap"),
            spent=fields.get("spent"),
        )
    raise BrowserUseError(response.status_code, message, detail, retry_after)


_MAX_RETRY_AFTER = 10.0
_SPEND_LIMIT_CODE = "api_key_monthly_spend_limit_reached"


class SyncHttpClient:
    """Synchronous HTTP client with retry and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
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
        files: dict[str, Any] | None = None,
    ) -> Any:
        json = _clean_json(json) if json is not None else None
        cleaned_params = _clean_params(params)
        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method, path, json=json, params=cleaned_params, headers=headers, files=files
                )
            except httpx.TransportError as error:
                if attempt < self._max_retries and _should_retry_transport(method, error):
                    time.sleep(_backoff_delay(attempt))
                    continue
                raise

            if _should_retry(method, response.status_code) and attempt < self._max_retries:
                delay = _retry_delay(response, attempt)
                if delay is not None:
                    time.sleep(delay)
                    continue

            _raise_for_status(response)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        _raise_for_status(response)  # type: ignore[possibly-undefined]

    def request_idempotent(self, method: str, path: str) -> Any:
        """Send an idempotent request, retrying 503 busy replies after their Retry-After."""
        for attempt in range(self._max_retries + 1):
            try:
                return self.request(method, path)
            except BrowserUseError as error:
                if error.status_code != 503 or error.retry_after is None or attempt == self._max_retries:
                    raise
                time.sleep(min(error.retry_after, _MAX_RETRY_AFTER))

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
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        self._max_retries = max_retries
        # x402 pays per request, so a replayed GET could pay twice.
        self._retry_transport = x402_client is None
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
        files: dict[str, Any] | None = None,
    ) -> Any:
        json = _clean_json(json) if json is not None else None
        cleaned_params = _clean_params(params)
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method, path, json=json, params=cleaned_params, headers=headers, files=files
                )
            except httpx.TransportError as error:
                if self._retry_transport and attempt < self._max_retries and _should_retry_transport(method, error):
                    await asyncio.sleep(_backoff_delay(attempt))
                    continue
                raise

            if _should_retry(method, response.status_code) and attempt < self._max_retries:
                delay = _retry_delay(response, attempt)
                if delay is not None:
                    await asyncio.sleep(delay)
                    continue

            _raise_for_status(response)
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        _raise_for_status(response)  # type: ignore[possibly-undefined]

    async def request_idempotent(self, method: str, path: str) -> Any:
        """Send an idempotent request, retrying 503 busy replies after their Retry-After."""
        for attempt in range(self._max_retries + 1):
            try:
                return await self.request(method, path)
            except BrowserUseError as error:
                if error.status_code != 503 or error.retry_after is None or attempt == self._max_retries:
                    raise
                await asyncio.sleep(min(error.retry_after, _MAX_RETRY_AFTER))

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
