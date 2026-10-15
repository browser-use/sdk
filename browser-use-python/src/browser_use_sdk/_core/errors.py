from __future__ import annotations

from typing import Any


class BrowserUseError(Exception):
    """Raised when the Browser Use API returns a non-2xx response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Any = None,
        retry_after: int | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.detail = detail
        self.retry_after = retry_after
        super().__init__(f"{status_code}: {message}")


class APIKeySpendLimitError(BrowserUseError):
    """Raised on 402 when the API key's monthly spend limit is reached."""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Any = None,
        retry_after: int | None = None,
        *,
        code: str,
        cap: float | None,
        spent: float | None,
    ) -> None:
        super().__init__(status_code, message, detail, retry_after)
        self.code = code
        self.cap = cap
        self.spent = spent
