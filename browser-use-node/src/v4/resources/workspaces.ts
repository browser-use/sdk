import { readFile, stat } from "fs/promises";
import { basename, extname } from "path";
import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type WorkspaceInfo = components["schemas"]["WorkspaceInfo"];
type WorkspaceCreateRequest = components["schemas"]["WorkspaceCreateRequest"];
type WorkspaceUpdateRequest = components["schemas"]["WorkspaceUpdateRequest"];
type WorkspaceSizeInfo = components["schemas"]["WorkspaceSizeInfo"];
type WorkspaceFileListResponse = components["schemas"]["WorkspaceFileListResponse"];
type WorkspaceFileUploadRequest = components["schemas"]["WorkspaceFileUploadRequest"];
type WorkspaceFileUploadResponse = components["schemas"]["WorkspaceFileUploadResponse"];
type WorkspaceFileUploadResponseItem = components["schemas"]["WorkspaceFileUploadResponseItem"];

const MIME_TYPES: Record<string, string> = {
  ".csv": "text/csv",
  ".json": "application/json",
  ".txt": "text/plain",
  ".md": "text/markdown",
  ".html": "text/html",
  ".xml": "application/xml",
  ".yaml": "application/yaml",
  ".yml": "application/yaml",
  ".pdf": "application/pdf",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
  ".mp4": "video/mp4",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".zip": "application/zip",
  ".gz": "application/gzip",
  ".tar": "application/x-tar",
  ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  ".xls": "application/vnd.ms-excel",
  ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  ".doc": "application/msword",
  ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
};

function guessContentType(path: string): string {
  return MIME_TYPES[extname(path).toLowerCase()] ?? "application/octet-stream";
}

export interface WorkspaceFilesParams {
  prefix?: string;
  limit?: number;
  cursor?: string | null;
  includeUrls?: boolean;
  contentDisposition?: string;
}

export class Workspaces {
  constructor(private readonly http: HttpClient) {}

  /** Create a new workspace. */
  create(body?: WorkspaceCreateRequest): Promise<WorkspaceInfo> {
    return this.http.post<WorkspaceInfo>("/workspaces", body ?? {});
  }

  /** Get workspace details. */
  get(workspaceId: string): Promise<WorkspaceInfo> {
    return this.http.get<WorkspaceInfo>(`/workspaces/${workspaceId}`);
  }

  /** Rename a workspace; pass `name: null` to clear its name. */
  update(workspaceId: string, body: WorkspaceUpdateRequest): Promise<WorkspaceInfo> {
    return this.http.patch<WorkspaceInfo>(`/workspaces/${workspaceId}`, body);
  }

  /** Archive a workspace. */
  delete(workspaceId: string): Promise<void> {
    return this.http.delete<void>(`/workspaces/${workspaceId}`);
  }

  /** Get current storage usage and the workspace quota. */
  size(workspaceId: string): Promise<WorkspaceSizeInfo> {
    return this.http.get<WorkspaceSizeInfo>(`/workspaces/${workspaceId}/size`);
  }

  /** List files in a workspace with cursor-based pagination. */
  files(workspaceId: string, params?: WorkspaceFilesParams): Promise<WorkspaceFileListResponse> {
    return this.http.get<WorkspaceFileListResponse>(
      `/workspaces/${workspaceId}/files`,
      params as Record<string, unknown>,
    );
  }

  /** Get presigned PUT URLs for workspace file uploads. */
  uploadFiles(workspaceId: string, body: WorkspaceFileUploadRequest): Promise<WorkspaceFileUploadResponse> {
    return this.http.post<WorkspaceFileUploadResponse>(
      `/workspaces/${workspaceId}/files/upload`,
      body,
    );
  }

  /** Delete one exact path from a workspace. */
  deleteFile(workspaceId: string, path: string): Promise<void> {
    return this.http.delete<void>(`/workspaces/${workspaceId}/files`, { path });
  }

  /**
   * Upload local files to a workspace: presign + PUT in one call. Returns the
   * upload items — pass their `id`s in `RunCreateRequest.attachedFileIds` to
   * attach the files to a run.
   *
   * ```ts
   * const uploaded = await client.workspaces.upload(wsId, "data.csv", "config.json");
   * await client.runs.create({ task: "...", workspaceId: wsId, attachedFileIds: uploaded.map(f => f.id) });
   * ```
   *
   * Each file is read at PUT time and its byte length is checked against the
   * size sent at presign; a size change raises. Don't modify a file while it is
   * being uploaded — a same-length in-place edit could upload the newer bytes.
   */
  async upload(workspaceId: string, ...paths: string[]): Promise<WorkspaceFileUploadResponseItem[]> {
    if (paths.length === 0) {
      throw new Error("At least one file path is required");
    }
    // Presign from each file's size via async stat (no payload in memory yet),
    // then read + PUT each file one at a time so only ONE file's bytes are ever
    // held in RAM. All I/O is promise-based — nothing blocks the event loop.
    const items = await Promise.all(
      paths.map(async (p) => ({
        name: basename(p),
        contentType: guessContentType(p),
        size: (await stat(p)).size,
      })),
    );
    const resp = await this.uploadFiles(workspaceId, { files: items, allowOverrides: true });
    if (resp.files.length < items.length) {
      const missing = items
        .slice(resp.files.length)
        .map((it, i) => `${it.name} (position ${resp.files.length + i})`)
        .join(", ");
      throw new Error(
        `Presign response has ${resp.files.length} upload URL(s) but ${items.length} file(s) were requested. Missing upload URL for: ${missing}`,
      );
    }
    for (let i = 0; i < paths.length; i++) {
      const buffer = await readFile(paths[i]);
      // Guard the TOCTOU: if the file changed size between stat and read, the
      // presigned URL was pinned to the old size and the PUT would fail opaquely.
      if (buffer.byteLength !== items[i].size) {
        throw new Error(
          `File ${paths[i]} changed size during upload (presigned ${items[i].size} bytes, read ${buffer.byteLength}). Retry the upload.`,
        );
      }
      const res = await fetch(resp.files[i].uploadUrl, {
        method: "PUT",
        headers: { "Content-Type": items[i].contentType },
        body: buffer,
      });
      if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
    }
    return resp.files;
  }
}
