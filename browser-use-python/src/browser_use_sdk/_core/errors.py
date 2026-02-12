from __future__ import annotations

from typing import Any, Optional


class BrowserUseError(Exception):
    """Raised when the Browser Use API returns a non-2xx response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        detail: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(f"{status_code}: {message}")
