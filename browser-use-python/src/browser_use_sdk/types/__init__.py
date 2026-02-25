"""Backward-compatible type stubs.

These modules exist solely to prevent ImportError in older versions of
browser-use (<=0.11.x) that import from ``browser_use_sdk.types.<name>``.

All types now live in ``browser_use_sdk.generated.v2.models`` and are
re-exported at the top-level ``browser_use_sdk`` package.  These stub
files are effectively dead code and will be removed in a future release.
"""
