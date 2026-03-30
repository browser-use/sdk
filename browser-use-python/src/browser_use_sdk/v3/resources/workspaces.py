from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

_ID = str | UUID

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v3.models import (
    FileListResponse,
    FileUploadItem,
    FileUploadResponse,
    WorkspaceCreateRequest,
    WorkspaceListResponse,
    WorkspaceUpdateRequest,
    WorkspaceView,
)


def _guess_content_type(path: str) -> str:
    ct, _ = mimetypes.guess_type(path)
    return ct or "application/octet-stream"


def _safe_join(base: Path, untrusted: str) -> Path:
    """Join base and untrusted path, raising if result escapes base."""
    resolved = (base / untrusted).resolve()
    if not str(resolved).startswith(str(base.resolve())):
        raise ValueError(f"Path traversal detected: {untrusted}")
    return resolved


class Workspaces:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> WorkspaceListResponse:
        """List workspaces for the authenticated project."""
        return WorkspaceListResponse.model_validate(
            self._http.request(
                "GET",
                "/workspaces",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                },
            )
        )

    def create(
        self,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> WorkspaceView:
        """Create a new workspace."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return WorkspaceView.model_validate(
            self._http.request("POST", "/workspaces", json=body or None)
        )

    def get(self, workspace_id: _ID) -> WorkspaceView:
        """Get workspace details."""
        return WorkspaceView.model_validate(
            self._http.request("GET", f"/workspaces/{workspace_id}")
        )

    def update(
        self,
        workspace_id: _ID,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> WorkspaceView:
        """Update a workspace."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return WorkspaceView.model_validate(
            self._http.request("PATCH", f"/workspaces/{workspace_id}", json=body)
        )

    def delete(self, workspace_id: _ID) -> None:
        """Delete a workspace and its data."""
        self._http.request("DELETE", f"/workspaces/{workspace_id}")

    def files(
        self,
        workspace_id: _ID,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
        shallow: bool | None = None,
    ) -> FileListResponse:
        """List files in a workspace."""
        return FileListResponse.model_validate(
            self._http.request(
                "GET",
                f"/workspaces/{workspace_id}/files",
                params={
                    "prefix": prefix,
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                    "shallow": shallow,
                },
            )
        )

    def upload_files(
        self,
        workspace_id: _ID,
        files: list[FileUploadItem],
        *,
        prefix: str | None = None,
        **extra: Any,
    ) -> FileUploadResponse:
        """Get presigned upload URLs for workspace files."""
        body: dict[str, Any] = {
            "files": [f.model_dump(by_alias=True, exclude_none=True) for f in files],
        }
        body.update(extra)
        return FileUploadResponse.model_validate(
            self._http.request(
                "POST",
                f"/workspaces/{workspace_id}/files/upload",
                json=body,
                params={"prefix": prefix} if prefix else None,
            )
        )

    def delete_file(self, workspace_id: _ID, *, path: str) -> None:
        """Delete a file from a workspace."""
        self._http.request(
            "DELETE",
            f"/workspaces/{workspace_id}/files",
            params={"path": path},
        )

    def size(self, workspace_id: _ID) -> Any:
        """Get storage usage for a workspace."""
        return self._http.request("GET", f"/workspaces/{workspace_id}/size")

    def upload(
        self,
        workspace_id: _ID,
        *paths: str | Path,
        prefix: str | None = None,
    ) -> list[str]:
        """Upload local files to a workspace. Returns the list of remote paths.

        Usage::

            client.workspaces.upload(ws_id, "data.csv", "config.json")
        """
        resolved = [Path(p) for p in paths]
        items = [
            FileUploadItem(
                name=p.name,
                contentType=_guess_content_type(str(p)),
                size=p.stat().st_size,
            )
            for p in resolved
        ]
        resp = self.upload_files(workspace_id, items, prefix=prefix)
        with httpx.Client(timeout=60) as http:
            for p, item in zip(resolved, resp.files):
                http.put(
                    item.upload_url,
                    content=p.read_bytes(),
                    headers={"Content-Type": _guess_content_type(str(p))},
                ).raise_for_status()
        return [f.path for f in resp.files]

    def download(
        self,
        workspace_id: _ID,
        path: str,
        *,
        to: str | Path | None = None,
    ) -> Path:
        """Download a single file from a workspace. Returns the local path.

        Usage::

            local = client.workspaces.download(ws_id, "uploads/data.csv", to="./data.csv")
        """
        file_list = self.files(workspace_id, prefix=path, include_urls=True)
        match = next((f for f in file_list.files if f.path == path), None)
        if not match:
            raise FileNotFoundError(f"File not found in workspace: {path}")
        dest = Path(to) if to else Path(os.path.basename(match.path))
        dest.parent.mkdir(parents=True, exist_ok=True)
        with httpx.Client(timeout=60) as http:
            resp = http.get(match.url)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        return dest

    def download_all(
        self,
        workspace_id: _ID,
        *,
        to: str | Path = ".",
        prefix: str | None = None,
    ) -> list[Path]:
        """Download all files from a workspace. Returns list of local paths.

        Usage::

            paths = client.workspaces.download_all(ws_id, to="./output")
        """
        dest_dir = Path(to)
        dest_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []
        cursor: str | None = None
        with httpx.Client(timeout=60) as http:
            while True:
                file_list = self.files(
                    workspace_id, prefix=prefix, include_urls=True, cursor=cursor,
                )
                for f in file_list.files:
                    local = _safe_join(dest_dir, f.path)
                    local.parent.mkdir(parents=True, exist_ok=True)
                    resp = http.get(f.url)
                    resp.raise_for_status()
                    local.write_bytes(resp.content)
                    results.append(local)
                if not file_list.has_more:
                    break
                cursor = file_list.next_cursor
        return results


class AsyncWorkspaces:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> WorkspaceListResponse:
        """List workspaces for the authenticated project."""
        return WorkspaceListResponse.model_validate(
            await self._http.request(
                "GET",
                "/workspaces",
                params={
                    "pageSize": page_size,
                    "pageNumber": page_number,
                },
            )
        )

    async def create(
        self,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> WorkspaceView:
        """Create a new workspace."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return WorkspaceView.model_validate(
            await self._http.request("POST", "/workspaces", json=body or None)
        )

    async def get(self, workspace_id: _ID) -> WorkspaceView:
        """Get workspace details."""
        return WorkspaceView.model_validate(
            await self._http.request("GET", f"/workspaces/{workspace_id}")
        )

    async def update(
        self,
        workspace_id: _ID,
        *,
        name: str | None = None,
        **extra: Any,
    ) -> WorkspaceView:
        """Update a workspace."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        body.update(extra)
        return WorkspaceView.model_validate(
            await self._http.request("PATCH", f"/workspaces/{workspace_id}", json=body)
        )

    async def delete(self, workspace_id: _ID) -> None:
        """Delete a workspace and its data."""
        await self._http.request("DELETE", f"/workspaces/{workspace_id}")

    async def files(
        self,
        workspace_id: _ID,
        *,
        prefix: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        include_urls: bool | None = None,
        shallow: bool | None = None,
    ) -> FileListResponse:
        """List files in a workspace."""
        return FileListResponse.model_validate(
            await self._http.request(
                "GET",
                f"/workspaces/{workspace_id}/files",
                params={
                    "prefix": prefix,
                    "limit": limit,
                    "cursor": cursor,
                    "includeUrls": include_urls,
                    "shallow": shallow,
                },
            )
        )

    async def upload_files(
        self,
        workspace_id: _ID,
        files: list[FileUploadItem],
        *,
        prefix: str | None = None,
        **extra: Any,
    ) -> FileUploadResponse:
        """Get presigned upload URLs for workspace files."""
        body: dict[str, Any] = {
            "files": [f.model_dump(by_alias=True, exclude_none=True) for f in files],
        }
        body.update(extra)
        return FileUploadResponse.model_validate(
            await self._http.request(
                "POST",
                f"/workspaces/{workspace_id}/files/upload",
                json=body,
                params={"prefix": prefix} if prefix else None,
            )
        )

    async def delete_file(self, workspace_id: _ID, *, path: str) -> None:
        """Delete a file from a workspace."""
        await self._http.request(
            "DELETE",
            f"/workspaces/{workspace_id}/files",
            params={"path": path},
        )

    async def size(self, workspace_id: _ID) -> Any:
        """Get storage usage for a workspace."""
        return await self._http.request("GET", f"/workspaces/{workspace_id}/size")

    async def upload(
        self,
        workspace_id: _ID,
        *paths: str | Path,
        prefix: str | None = None,
    ) -> list[str]:
        """Upload local files to a workspace. Returns the list of remote paths.

        Usage::

            await client.workspaces.upload(ws_id, "data.csv", "config.json")
        """
        resolved = [Path(p) for p in paths]
        items = [
            FileUploadItem(
                name=p.name,
                contentType=_guess_content_type(str(p)),
                size=p.stat().st_size,
            )
            for p in resolved
        ]
        resp = await self.upload_files(workspace_id, items, prefix=prefix)
        async with httpx.AsyncClient(timeout=60) as http:
            for p, item in zip(resolved, resp.files):
                r = await http.put(
                    item.upload_url,
                    content=p.read_bytes(),
                    headers={"Content-Type": _guess_content_type(str(p))},
                )
                r.raise_for_status()
        return [f.path for f in resp.files]

    async def download(
        self,
        workspace_id: _ID,
        path: str,
        *,
        to: str | Path | None = None,
    ) -> Path:
        """Download a single file from a workspace. Returns the local path.

        Usage::

            local = await client.workspaces.download(ws_id, "uploads/data.csv", to="./data.csv")
        """
        file_list = await self.files(workspace_id, prefix=path, include_urls=True, limit=1)
        if not file_list.files:
            raise FileNotFoundError(f"File not found in workspace: {path}")
        url = file_list.files[0].url
        dest = Path(to) if to else Path(os.path.basename(file_list.files[0].path))
        dest.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=60) as http:
            resp = await http.get(url)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
        return dest

    async def download_all(
        self,
        workspace_id: _ID,
        *,
        to: str | Path = ".",
        prefix: str | None = None,
    ) -> list[Path]:
        """Download all files from a workspace. Returns list of local paths.

        Usage::

            paths = await client.workspaces.download_all(ws_id, to="./output")
        """
        dest_dir = Path(to)
        dest_dir.mkdir(parents=True, exist_ok=True)
        results: list[Path] = []
        cursor: str | None = None
        async with httpx.AsyncClient(timeout=60) as http:
            while True:
                file_list = await self.files(
                    workspace_id, prefix=prefix, include_urls=True, cursor=cursor,
                )
                for f in file_list.files:
                    local = _safe_join(dest_dir, f.path)
                    local.parent.mkdir(parents=True, exist_ok=True)
                    resp = await http.get(f.url)
                    resp.raise_for_status()
                    local.write_bytes(resp.content)
                    results.append(local)
                if not file_list.has_more:
                    break
                cursor = file_list.next_cursor
        return results
