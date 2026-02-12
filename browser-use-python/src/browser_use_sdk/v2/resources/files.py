from __future__ import annotations

from ..._core.http import AsyncHttpClient, SyncHttpClient
from ...generated.v2.models import (
    TaskOutputFileResponse,
    UploadFilePresignedUrlResponse,
)


class Files:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def session_url(
        self,
        session_id: str,
        *,
        file_name: str,
        content_type: str,
        size_bytes: int,
    ) -> UploadFilePresignedUrlResponse:
        """Generate a presigned URL for uploading files to an agent session."""
        return UploadFilePresignedUrlResponse.model_validate(
            self._http.request(
                "POST",
                f"/files/sessions/{session_id}/presigned-url",
                json={
                    "fileName": file_name,
                    "contentType": content_type,
                    "sizeBytes": size_bytes,
                },
            )
        )

    def browser_url(
        self,
        session_id: str,
        *,
        file_name: str,
        content_type: str,
        size_bytes: int,
    ) -> UploadFilePresignedUrlResponse:
        """Generate a presigned URL for uploading files to a browser session."""
        return UploadFilePresignedUrlResponse.model_validate(
            self._http.request(
                "POST",
                f"/files/browsers/{session_id}/presigned-url",
                json={
                    "fileName": file_name,
                    "contentType": content_type,
                    "sizeBytes": size_bytes,
                },
            )
        )

    def task_output(self, task_id: str, file_id: str) -> TaskOutputFileResponse:
        """Get secure download URL for a task output file."""
        return TaskOutputFileResponse.model_validate(
            self._http.request(
                "GET",
                f"/files/tasks/{task_id}/output-files/{file_id}",
            )
        )


class AsyncFiles:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def session_url(
        self,
        session_id: str,
        *,
        file_name: str,
        content_type: str,
        size_bytes: int,
    ) -> UploadFilePresignedUrlResponse:
        """Generate a presigned URL for uploading files to an agent session."""
        return UploadFilePresignedUrlResponse.model_validate(
            await self._http.request(
                "POST",
                f"/files/sessions/{session_id}/presigned-url",
                json={
                    "fileName": file_name,
                    "contentType": content_type,
                    "sizeBytes": size_bytes,
                },
            )
        )

    async def browser_url(
        self,
        session_id: str,
        *,
        file_name: str,
        content_type: str,
        size_bytes: int,
    ) -> UploadFilePresignedUrlResponse:
        """Generate a presigned URL for uploading files to a browser session."""
        return UploadFilePresignedUrlResponse.model_validate(
            await self._http.request(
                "POST",
                f"/files/browsers/{session_id}/presigned-url",
                json={
                    "fileName": file_name,
                    "contentType": content_type,
                    "sizeBytes": size_bytes,
                },
            )
        )

    async def task_output(self, task_id: str, file_id: str) -> TaskOutputFileResponse:
        """Get secure download URL for a task output file."""
        return TaskOutputFileResponse.model_validate(
            await self._http.request(
                "GET",
                f"/files/tasks/{task_id}/output-files/{file_id}",
            )
        )
