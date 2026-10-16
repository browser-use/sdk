"""Browser Use Python SDK.

Default imports expose the v4 client and types since 4.0.0.
For v2 or v3, use ``from browser_use_sdk.v2 import BrowserUse`` or ``browser_use_sdk.v3``.
"""

from typing import TYPE_CHECKING

from .v4 import *  # noqa: F403
from .v4 import __all__ as __all__

if not TYPE_CHECKING:  # Hidden from type checkers so they still flag the moved names.

    def __getattr__(name: str) -> object:
        """Point former root-level v2 names at browser_use_sdk.v2."""
        from importlib import import_module

        # `from . import v2` would recurse into this hook before v2 is loaded.
        v2 = import_module(".v2", __name__)
        if name == "v2":
            return v2
        if name in v2.__all__:
            # ImportError, not AttributeError: `from x import y` drops AttributeError messages.
            raise ImportError(
                f"{name} moved to browser_use_sdk.v2 in 4.0.0, where V4 became the default; "
                f"use `from browser_use_sdk.v2 import {name}`"
            )
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
