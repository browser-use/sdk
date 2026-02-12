import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

type UploadFileRequest = components["schemas"]["UploadFileRequest"];
type UploadFilePresignedUrlResponse = components["schemas"]["UploadFilePresignedUrlResponse"];
type TaskOutputFileResponse = components["schemas"]["TaskOutputFileResponse"];

export class Files {
  constructor(private readonly http: HttpClient) {}

  /** Generate a presigned URL for uploading files to an agent session. */
  sessionUrl(sessionId: string, body: UploadFileRequest): Promise<UploadFilePresignedUrlResponse> {
    return this.http.post<UploadFilePresignedUrlResponse>(
      `/files/sessions/${sessionId}/presigned-url`,
      body,
    );
  }

  /** Generate a presigned URL for uploading files to a browser session. */
  browserUrl(sessionId: string, body: UploadFileRequest): Promise<UploadFilePresignedUrlResponse> {
    return this.http.post<UploadFilePresignedUrlResponse>(
      `/files/browsers/${sessionId}/presigned-url`,
      body,
    );
  }

  /** Get secure download URL for a task output file. */
  taskOutput(taskId: string, fileId: string): Promise<TaskOutputFileResponse> {
    return this.http.get<TaskOutputFileResponse>(
      `/files/tasks/${taskId}/output-files/${fileId}`,
    );
  }
}
