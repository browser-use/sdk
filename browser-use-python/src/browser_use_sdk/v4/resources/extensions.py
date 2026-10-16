from __future__ import annotations

import asyncio
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import ExtensionListResponse, ExtensionView

if TYPE_CHECKING:
    from uuid import UUID


def _build_files(file: str | Path | bytes | IO[bytes], extra: dict[str, Any]) -> dict[str, Any]:
    """Read the ZIP into memory so a 429 retry resends the same bytes."""
    if isinstance(file, (str, Path)):
        part = (Path(file).name, Path(file).read_bytes())
    else:
        part = ("extension.zip", file if isinstance(file, bytes) else file.read())
    return {"file": part, **{key: (None, str(value)) for key, value in extra.items()}}


class Extensions:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(self, file: str | Path | bytes | IO[bytes], **extra: Any) -> ExtensionView:
        """Upload a Manifest V3 extension ZIP from a path, bytes, or binary file."""
        return ExtensionView.model_validate(
            self._http.request("POST", "/extensions", files=_build_files(file, extra))
        )

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> ExtensionListResponse:
        """List uploaded extensions."""
        return ExtensionListResponse.model_validate(
            self._http.request(
                "GET",
                "/extensions",
                params={"pageSize": page_size, "pageNumber": page_number},
            )
        )

    def get(self, extension_id: str | UUID) -> ExtensionView:
        """Get an uploaded extension."""
        return ExtensionView.model_validate(
            self._http.request("GET", f"/extensions/{extension_id}")
        )

    def delete(self, extension_id: str | UUID) -> None:
        """Permanently delete an extension without affecting running browsers."""
        self._http.request("DELETE", f"/extensions/{extension_id}")


class AsyncExtensions:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, file: str | Path | bytes | IO[bytes], **extra: Any) -> ExtensionView:
        """Upload a Manifest V3 extension ZIP from a path, bytes, or binary file."""
        files = await asyncio.to_thread(_build_files, file, extra)
        return ExtensionView.model_validate(
            await self._http.request("POST", "/extensions", files=files)
        )

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> ExtensionListResponse:
        """List uploaded extensions."""
        return ExtensionListResponse.model_validate(
            await self._http.request(
                "GET",
                "/extensions",
                params={"pageSize": page_size, "pageNumber": page_number},
            )
        )

    async def get(self, extension_id: str | UUID) -> ExtensionView:
        """Get an uploaded extension."""
        return ExtensionView.model_validate(
            await self._http.request("GET", f"/extensions/{extension_id}")
        )

    async def delete(self, extension_id: str | UUID) -> None:
        """Permanently delete an extension without affecting running browsers."""
        await self._http.request("DELETE", f"/extensions/{extension_id}")
