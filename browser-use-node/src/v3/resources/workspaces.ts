import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v3/types.js";

type WorkspaceView = components["schemas"]["WorkspaceView"];
type WorkspaceListResponse = components["schemas"]["WorkspaceListResponse"];
type WorkspaceCreateRequest = components["schemas"]["WorkspaceCreateRequest"];
type WorkspaceUpdateRequest = components["schemas"]["WorkspaceUpdateRequest"];
type FileListResponse = components["schemas"]["FileListResponse"];
type FileUploadRequest = components["schemas"]["FileUploadRequest"];
type FileUploadResponse = components["schemas"]["FileUploadResponse"];

export interface WorkspaceListParams {
  pageSize?: number;
  pageNumber?: number;
}

export interface WorkspaceFilesParams {
  prefix?: string;
  limit?: number;
  cursor?: string | null;
  includeUrls?: boolean;
  shallow?: boolean;
}

export class Workspaces {
  constructor(private readonly http: HttpClient) {}

  /** List workspaces for the authenticated project. */
  list(params?: WorkspaceListParams): Promise<WorkspaceListResponse> {
    return this.http.get<WorkspaceListResponse>("/workspaces", params as Record<string, unknown>);
  }

  /** Create a new workspace. */
  create(body?: WorkspaceCreateRequest): Promise<WorkspaceView> {
    return this.http.post<WorkspaceView>("/workspaces", body);
  }

  /** Get workspace details. */
  get(workspaceId: string): Promise<WorkspaceView> {
    return this.http.get<WorkspaceView>(`/workspaces/${workspaceId}`);
  }

  /** Update a workspace. */
  update(workspaceId: string, body: WorkspaceUpdateRequest): Promise<WorkspaceView> {
    return this.http.patch<WorkspaceView>(`/workspaces/${workspaceId}`, body);
  }

  /** Delete a workspace and its data. */
  delete(workspaceId: string): Promise<void> {
    return this.http.delete<void>(`/workspaces/${workspaceId}`);
  }

  /** List files in a workspace. */
  files(workspaceId: string, params?: WorkspaceFilesParams): Promise<FileListResponse> {
    return this.http.get<FileListResponse>(
      `/workspaces/${workspaceId}/files`,
      params as Record<string, unknown>,
    );
  }

  /** Delete a file from a workspace. */
  deleteFile(workspaceId: string, path: string): Promise<void> {
    return this.http.delete<void>(`/workspaces/${workspaceId}/files`, { path });
  }

  /** Get workspace storage usage. */
  getSize(workspaceId: string): Promise<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`/workspaces/${workspaceId}/size`);
  }

  /** Get presigned upload URLs for workspace files. */
  uploadFiles(workspaceId: string, body: FileUploadRequest, prefix?: string): Promise<FileUploadResponse> {
    return this.http.post<FileUploadResponse>(
      `/workspaces/${workspaceId}/files/upload`,
      body,
      prefix != null ? { prefix } : undefined,
    );
  }
}
