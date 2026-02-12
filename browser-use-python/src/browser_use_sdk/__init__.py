"""Browser Use Python SDK.

Default imports expose the v2 client and core error type.
For v3, use ``from browser_use_sdk.v3 import BrowserUse``.
"""

from ._core.errors import BrowserUseError
from .v2.client import AsyncBrowserUse, BrowserUse
from .v2.helpers import AsyncTaskHandle, TaskHandle

__all__ = [
    "BrowserUse",
    "AsyncBrowserUse",
    "BrowserUseError",
    "TaskHandle",
    "AsyncTaskHandle",
]
