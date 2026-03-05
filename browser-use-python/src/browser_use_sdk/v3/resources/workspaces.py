from __future__ import annotations

from typing import Any

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

    def get(self, workspace_id: str) -> WorkspaceView:
        """Get workspace details."""
        return WorkspaceView.model_validate(
            self._http.request("GET", f"/workspaces/{workspace_id}")
        )

    def update(
        self,
        workspace_id: str,
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

    def delete(self, workspace_id: str) -> None:
        """Delete a workspace and its data."""
        self._http.request("DELETE", f"/workspaces/{workspace_id}")

    def files(
        self,
        workspace_id: str,
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
        workspace_id: str,
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

    def delete_file(self, workspace_id: str, *, path: str) -> None:
        """Delete a file from a workspace."""
        self._http.request(
            "DELETE",
            f"/workspaces/{workspace_id}/files",
            params={"path": path},
        )

    def size(self, workspace_id: str) -> Any:
        """Get storage usage for a workspace."""
        return self._http.request("GET", f"/workspaces/{workspace_id}/size")


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

    async def get(self, workspace_id: str) -> WorkspaceView:
        """Get workspace details."""
        return WorkspaceView.model_validate(
            await self._http.request("GET", f"/workspaces/{workspace_id}")
        )

    async def update(
        self,
        workspace_id: str,
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

    async def delete(self, workspace_id: str) -> None:
        """Delete a workspace and its data."""
        await self._http.request("DELETE", f"/workspaces/{workspace_id}")

    async def files(
        self,
        workspace_id: str,
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
        workspace_id: str,
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

    async def delete_file(self, workspace_id: str, *, path: str) -> None:
        """Delete a file from a workspace."""
        await self._http.request(
            "DELETE",
            f"/workspaces/{workspace_id}/files",
            params={"path": path},
        )

    async def size(self, workspace_id: str) -> Any:
        """Get storage usage for a workspace."""
        return await self._http.request("GET", f"/workspaces/{workspace_id}/size")
