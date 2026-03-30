from .errors import BrowserUseError
from .http import AsyncHttpClient, SyncHttpClient

_UNSET: object = object()
"""Sentinel for parameters where ``None`` has explicit API meaning (e.g. sending
JSON ``null`` to disable proxies).  Using ``_UNSET`` as the default lets the SDK
distinguish "caller didn't pass a value" from "caller explicitly passed ``None``"."""

__all__ = ["BrowserUseError", "SyncHttpClient", "AsyncHttpClient", "_UNSET"]
