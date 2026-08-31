from __future__ import annotations

import asyncio
import mimetypes
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

from ..._core import _UNSET
from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v4.models import (
    WorkspaceFileListResponse,
    WorkspaceFileUploadItem,
    WorkspaceFileUploadResponse,
    WorkspaceFileUploadResponseItem,
    WorkspaceInfo,
    WorkspaceSizeInfo,
)

if TYPE_CHECKING:
    from uuid import UUID


def _guess_content_type(path: str) -> str:
    ct, _ = mimetypes.guess_type(path)
    return ct or "application/octet-stream"


def _safe_join(base: Path, untrusted: str) -> Path:
    """Join a workspace path below ``base`` without allowing traversal."""
    base_resolved = base.resolve()
    resolved = (base / untrusted).resolve()
    if base_resolved != resolved and base_resolved not in resolved.parents:
        raise ValueError(f"Path traversal detected: {untrusted}")
    return resolved


def _new_temp_file(destination: Path):
    """Open a sibling temp file so the final replace stays on one filesystem."""
    return tempfile.NamedTemporaryFile(
        mode="wb",
        delete=False,
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )


def _stream_to_path(response: httpx.Response, destination: Path) -> None:
    """Stream a response to a temp file, then atomically replace destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_file = _new_temp_file(destination)
    temp_path = Path(temp_file.name)
    try:
        with temp_file:
            for chunk in response.iter_bytes():
                temp_file.write(chunk)
        os.replace(temp_path, destination)
    except BaseException:
        temp_file.close()
        temp_path.unlink(missing_ok=True)
        raise


async def _stream_to_path_async(
    response: httpx.Response, destination: Path
) -> None:
    """Async response streaming with blocking file writes moved off-loop."""
    await asyncio.to_thread(destination.parent.mkdir, parents=True, exist_ok=True)
    temp_file = await asyncio.to_thread(_new_temp_file, destination)
    temp_path = Path(temp_file.name)
    try:
        async for chunk in response.aiter_bytes():
            await asyncio.to_thread(temp_file.write, chunk)
        await asyncio.to_thread(temp_file.close)
        await asyncio.to_thread(os.replace, temp_path, destination)
    except BaseException:
        await asyncio.to_thread(temp_file.close)
        await asyncio.to_thread(temp_path.unlink, missing_ok=True)
        raise


def _presign_items(resolved: list[Path]) -> list[WorkspaceFileUploadItem]:
    """Build the presign request from each file's size via `stat` — no payload
    held in memory yet. Bytes are read one file at a time at PUT time (see
    `_read_checked`) so a multi-file upload never buffers everything at once."""
    return [
        WorkspaceFileUploadItem(
            name=p.name,
            contentType=_guess_content_type(str(p)),
            size=p.stat().st_size,
        )
        for p in resolved
    ]


def _read_checked(path: Path, expected_size: int) -> bytes:
    """Read a file's bytes and confirm they match the size sent at presign time.

    The presigned URL is pinned to the stat'd size; if the file changed between
    stat and read the PUT would fail opaquely, so we catch it here with a clear
    error instead."""
    data = path.read_bytes()
    if len(data) != expected_size:
        raise ValueError(
            f"File {path} changed size during upload (presigned {expected_size} bytes, "
            f"read {len(data)}). Retry the upload."
        )
    return data


def _check_presign_length(
    resp_files: list[WorkspaceFileUploadResponseItem],
    items: list[WorkspaceFileUploadItem],
) -> None:
    """Raise a descriptive error if the presign response is short an upload URL."""
    if len(resp_files) < len(items):
        missing = ", ".join(
            f"{it.name} (position {len(resp_files) + i})"
            for i, it in enumerate(items[len(resp_files) :])
        )
        raise ValueError(
            f"Presign response has {len(resp_files)} upload URL(s) but "
            f"{len(items)} file(s) were requested. Missing upload URL for: {missing}"
        )


class Workspaces:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> WorkspaceInfo:
        """Create a new workspace."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return WorkspaceInfo.model_validate(
            self._http.request("POST", "/workspaces", json=body)
        )

    def get(self, workspace_id: str | UUID) -> WorkspaceInfo:
        """Get workspace details."""
        return WorkspaceInfo.model_validate(
            self._http.request("GET", f"/workspaces/{workspace_id}")
        )

    def update(
        self,
        workspace_id: str | UUID,
        *,
        name: str | None = _UNSET,  # type: ignore[assignment]
        **extra: Any,
    ) -> WorkspaceInfo:
        """Rename a workspace; pass ``name=None`` to clear its name."""
        body: dict[str, Any] = {}
        if name is not _UNSET:
            body["name"] = name
        body.update(extra)
        return WorkspaceInfo.model_validate(
            self._http.request("PATCH", f"/workspaces/{workspace_id}", json=body)
        )

    def delete(self, workspace_id: str | UUID) -> None:
        """Archive a workspace."""
        self._http.request("DELETE", f"/workspaces/{workspace_id}")

    def size(self, workspace_id: str | UUID) -> WorkspaceSizeInfo:
        """Get current storage usage and the workspace quota."""
        return WorkspaceSizeInfo.model_validate(
            self._http.request("GET", f"/workspaces/{workspace_id}/size")
        )

    def files(
        self,
        workspace_id: str | UUID,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
        content_disposition: str | None = None,
    ) -> WorkspaceFileListResponse:
        """List files in a workspace with cursor-based pagination."""
        return WorkspaceFileListResponse.model_validate(
            self._http.request(
                "GET",
                f"/workspaces/{workspace_id}/files",
                params={
                    "prefix": prefix,
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                    "contentDisposition": content_disposition,
                },
            )
        )

    def upload_files(
        self,
        workspace_id: str | UUID,
        files: list[WorkspaceFileUploadItem],
        *,
        allow_overrides: bool = True,
        **extra: Any,
    ) -> WorkspaceFileUploadResponse:
        """Get presigned PUT URLs for workspace file uploads."""
        body: dict[str, Any] = {
            "files": [f.model_dump(by_alias=True, exclude_none=True) for f in files],
            "allowOverrides": allow_overrides,
        }
        body.update(extra)
        return WorkspaceFileUploadResponse.model_validate(
            self._http.request(
                "POST",
                f"/workspaces/{workspace_id}/files/upload",
                json=body,
            )
        )

    def delete_file(self, workspace_id: str | UUID, *, path: str) -> None:
        """Delete one exact path from a workspace."""
        self._http.request(
            "DELETE",
            f"/workspaces/{workspace_id}/files",
            params={"path": path},
        )

    def upload(
        self,
        workspace_id: str | UUID,
        *paths: str | Path,
    ) -> list[WorkspaceFileUploadResponseItem]:
        """Upload local files to a workspace: presign + PUT in one call.

        Returns the upload items — pass their ``id``s as ``attached_file_ids``
        in ``runs.create()`` to attach the files to a run.

        Usage::

            uploaded = client.workspaces.upload(ws_id, "data.csv")
            client.runs.create("...", workspace_id=ws_id, attached_file_ids=[f.id for f in uploaded])


        Each file is read at PUT time and its byte length checked against the
        presigned size; a size change raises. Don't modify a file while it is
        being uploaded — a same-length in-place edit could upload newer bytes.
        """
        if not paths:
            raise ValueError("at least one file path is required")
        resolved = [Path(p) for p in paths]
        items = _presign_items(resolved)
        resp = self.upload_files(workspace_id, items)
        _check_presign_length(resp.files, items)
        # Read + PUT one file at a time so only one payload is ever in memory.
        with httpx.Client(timeout=60) as http:
            for path, item, resp_item in zip(resolved, items, resp.files):
                data = _read_checked(path, item.size)
                http.put(
                    resp_item.upload_url,
                    content=data,
                    headers={"Content-Type": item.content_type or "application/octet-stream"},
                ).raise_for_status()
        return list(resp.files)

    def download(
        self,
        workspace_id: str | UUID,
        path: str,
        *,
        to: str | Path | None = None,
    ) -> Path:
        """Download one exact workspace file and return its local path.

        Usage::

            local = client.workspaces.download(ws_id, "reports/result.csv", to="./result.csv")
        """
        cursor: str | None = None
        while True:
            file_list = self.files(
                workspace_id,
                prefix=path,
                include_urls=True,
                cursor=cursor,
            )
            match = next((f for f in file_list.files if f.path == path), None)
            if match is not None:
                break
            if not file_list.has_more:
                raise FileNotFoundError(f"File not found in workspace: {path}")
            if file_list.next_cursor is None:
                raise RuntimeError(
                    "Workspace file response has_more=True but no next_cursor"
                )
            cursor = file_list.next_cursor

        if match.url is None:
            raise ValueError(f"No download URL for {path!r}; ensure include_urls=True")

        dest = Path(to) if to is not None else Path(os.path.basename(match.path))
        with httpx.Client(timeout=60) as http:
            with http.stream("GET", match.url) as response:
                response.raise_for_status()
                _stream_to_path(response, dest)
        return dest

    def download_all(
        self,
        workspace_id: str | UUID,
        *,
        to: str | Path = ".",
        prefix: str | None = None,
    ) -> list[Path]:
        """Download matching workspace files below ``to`` and return their paths.

        Usage::

            paths = client.workspaces.download_all(ws_id, to="./output", prefix="reports/")
        """
        dest_dir = Path(to)
        dest_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []
        cursor: str | None = None

        while True:
            # List metadata without URLs. Each file is re-read with include_urls
            # immediately before its GET so a 60-second URL cannot expire while
            # earlier files are still downloading.
            file_list = self.files(
                workspace_id,
                prefix=prefix,
                cursor=cursor,
            )
            for file in file_list.files:
                local = _safe_join(dest_dir, file.path)
                results.append(self.download(workspace_id, file.path, to=local))
            if not file_list.has_more:
                return results
            if file_list.next_cursor is None:
                raise RuntimeError(
                    "Workspace file response has_more=True but no next_cursor"
                )
            cursor = file_list.next_cursor


class AsyncWorkspaces:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> WorkspaceInfo:
        """Create a new workspace."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return WorkspaceInfo.model_validate(
            await self._http.request("POST", "/workspaces", json=body)
        )

    async def get(self, workspace_id: str | UUID) -> WorkspaceInfo:
        """Get workspace details."""
        return WorkspaceInfo.model_validate(
            await self._http.request("GET", f"/workspaces/{workspace_id}")
        )

    async def update(
        self,
        workspace_id: str | UUID,
        *,
        name: str | None = _UNSET,  # type: ignore[assignment]
        **extra: Any,
    ) -> WorkspaceInfo:
        """Rename a workspace; pass ``name=None`` to clear its name."""
        body: dict[str, Any] = {}
        if name is not _UNSET:
            body["name"] = name
        body.update(extra)
        return WorkspaceInfo.model_validate(
            await self._http.request(
                "PATCH", f"/workspaces/{workspace_id}", json=body
            )
        )

    async def delete(self, workspace_id: str | UUID) -> None:
        """Archive a workspace."""
        await self._http.request("DELETE", f"/workspaces/{workspace_id}")

    async def size(self, workspace_id: str | UUID) -> WorkspaceSizeInfo:
        """Get current storage usage and the workspace quota."""
        return WorkspaceSizeInfo.model_validate(
            await self._http.request("GET", f"/workspaces/{workspace_id}/size")
        )

    async def files(
        self,
        workspace_id: str | UUID,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
        content_disposition: str | None = None,
    ) -> WorkspaceFileListResponse:
        """List files in a workspace with cursor-based pagination."""
        return WorkspaceFileListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/workspaces/{workspace_id}/files",
                params={
                    "prefix": prefix,
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                    "contentDisposition": content_disposition,
                },
            )
        )

    async def upload_files(
        self,
        workspace_id: str | UUID,
        files: list[WorkspaceFileUploadItem],
        *,
        allow_overrides: bool = True,
        **extra: Any,
    ) -> WorkspaceFileUploadResponse:
        """Get presigned PUT URLs for workspace file uploads."""
        body: dict[str, Any] = {
            "files": [f.model_dump(by_alias=True, exclude_none=True) for f in files],
            "allowOverrides": allow_overrides,
        }
        body.update(extra)
        return WorkspaceFileUploadResponse.model_validate(
            await self._http.request(
                "POST",
                f"/workspaces/{workspace_id}/files/upload",
                json=body,
            )
        )

    async def delete_file(self, workspace_id: str | UUID, *, path: str) -> None:
        """Delete one exact path from a workspace."""
        await self._http.request(
            "DELETE",
            f"/workspaces/{workspace_id}/files",
            params={"path": path},
        )

    async def upload(
        self,
        workspace_id: str | UUID,
        *paths: str | Path,
    ) -> list[WorkspaceFileUploadResponseItem]:
        """Upload local files to a workspace: presign + PUT in one call.

        Returns the upload items — pass their ``id``s as ``attached_file_ids``
        in ``runs.create()`` to attach the files to a run.

        Usage::

            uploaded = await client.workspaces.upload(ws_id, "data.csv")


        Each file is read at PUT time and its byte length checked against the
        presigned size; a size change raises. Don't modify a file while it is
        being uploaded — a same-length in-place edit could upload newer bytes.
        """
        if not paths:
            raise ValueError("at least one file path is required")
        resolved = [Path(p) for p in paths]
        # stat is cheap; run it off the loop anyway to keep all disk I/O on a
        # thread. No payload in memory here — bytes are read per-file below.
        items = await asyncio.to_thread(_presign_items, resolved)
        resp = await self.upload_files(workspace_id, items)
        _check_presign_length(resp.files, items)
        # Read + PUT one file at a time (reads offloaded to a thread) so only one
        # payload is ever in memory and the event loop never blocks on disk.
        async with httpx.AsyncClient(timeout=60) as http:
            for path, item, resp_item in zip(resolved, items, resp.files):
                data = await asyncio.to_thread(_read_checked, path, item.size)
                r = await http.put(
                    resp_item.upload_url,
                    content=data,
                    headers={"Content-Type": item.content_type or "application/octet-stream"},
                )
                r.raise_for_status()
        return list(resp.files)

    async def download(
        self,
        workspace_id: str | UUID,
        path: str,
        *,
        to: str | Path | None = None,
    ) -> Path:
        """Download one exact workspace file and return its local path.

        Usage::

            local = await client.workspaces.download(
                ws_id, "reports/result.csv", to="./result.csv"
            )
        """
        cursor: str | None = None
        while True:
            file_list = await self.files(
                workspace_id,
                prefix=path,
                include_urls=True,
                cursor=cursor,
            )
            match = next((f for f in file_list.files if f.path == path), None)
            if match is not None:
                break
            if not file_list.has_more:
                raise FileNotFoundError(f"File not found in workspace: {path}")
            if file_list.next_cursor is None:
                raise RuntimeError(
                    "Workspace file response has_more=True but no next_cursor"
                )
            cursor = file_list.next_cursor

        if match.url is None:
            raise ValueError(f"No download URL for {path!r}; ensure include_urls=True")

        dest = Path(to) if to is not None else Path(os.path.basename(match.path))
        async with httpx.AsyncClient(timeout=60) as http:
            async with http.stream("GET", match.url) as response:
                response.raise_for_status()
                await _stream_to_path_async(response, dest)
        return dest

    async def download_all(
        self,
        workspace_id: str | UUID,
        *,
        to: str | Path = ".",
        prefix: str | None = None,
    ) -> list[Path]:
        """Download matching workspace files below ``to`` and return their paths.

        Usage::

            paths = await client.workspaces.download_all(
                ws_id, to="./output", prefix="reports/"
            )
        """
        dest_dir = Path(to)
        await asyncio.to_thread(dest_dir.mkdir, parents=True, exist_ok=True)
        results: list[Path] = []
        cursor: str | None = None

        while True:
            # Do not request a page of short-lived URLs. Refresh one exact file
            # immediately before streaming it, after the previous file finished.
            file_list = await self.files(
                workspace_id,
                prefix=prefix,
                cursor=cursor,
            )
            for file in file_list.files:
                local = await asyncio.to_thread(_safe_join, dest_dir, file.path)
                results.append(
                    await self.download(workspace_id, file.path, to=local)
                )
            if not file_list.has_more:
                return results
            if file_list.next_cursor is None:
                raise RuntimeError(
                    "Workspace file response has_more=True but no next_cursor"
                )
            cursor = file_list.next_cursor
