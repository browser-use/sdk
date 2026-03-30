import { readFileSync, writeFileSync, mkdirSync, statSync } from "fs";
import { basename, dirname, extname, join, resolve } from "path";
import type { HttpClient } from "../../core/http.js";

function safeJoin(base: string, untrusted: string): string {
  const baseResolved = resolve(base) + "/";
  const resolved = resolve(base, untrusted);
  if (resolved !== resolve(base) && !resolved.startsWith(baseResolved)) {
    throw new Error(`Path traversal detected: ${untrusted}`);
  }
  return resolved;
}

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

  /** Get presigned upload URLs for workspace files. */
  uploadFiles(workspaceId: string, body: FileUploadRequest, query?: { prefix?: string }): Promise<FileUploadResponse> {
    return this.http.post<FileUploadResponse>(
      `/workspaces/${workspaceId}/files/upload`,
      body,
      query as Record<string, unknown>,
    );
  }

  /** Delete a file from a workspace. */
  deleteFile(workspaceId: string, path: string): Promise<void> {
    return this.http.delete<void>(`/workspaces/${workspaceId}/files`, { path });
  }

  /** Get storage usage for a workspace. */
  size(workspaceId: string): Promise<unknown> {
    return this.http.get<unknown>(`/workspaces/${workspaceId}/size`);
  }

  /**
   * Upload local files to a workspace. Returns the list of remote paths.
   *
   * ```ts
   * await client.workspaces.upload(wsId, "data.csv", "config.json");
   * ```
   */
  async upload(workspaceId: string, ...paths: string[]): Promise<string[]> {
    const items = paths.map((p) => ({
      name: basename(p),
      contentType: guessContentType(p),
      size: statSync(p).size,
    }));
    const resp = await this.uploadFiles(workspaceId, { files: items });
    for (let i = 0; i < paths.length; i++) {
      const body = readFileSync(paths[i]);
      const res = await fetch(resp.files[i].uploadUrl, {
        method: "PUT",
        headers: { "Content-Type": items[i].contentType },
        body,
      });
      if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
    }
    return resp.files.map((f) => f.path);
  }

  /**
   * Download a single file from a workspace. Returns the local path.
   *
   * ```ts
   * const local = await client.workspaces.download(wsId, "uploads/data.csv", { to: "./data.csv" });
   * ```
   */
  async download(workspaceId: string, path: string, options?: { to?: string }): Promise<string> {
    const fileList = await this.files(workspaceId, { prefix: path, includeUrls: true });
    const match = fileList.files?.find((f) => f.path === path);
    if (!match) throw new Error(`File not found in workspace: ${path}`);
    const dest = options?.to ?? basename(match.path);
    mkdirSync(dirname(dest), { recursive: true });
    const resp = await fetch(match.url!);
    if (!resp.ok) throw new Error(`Download failed: ${resp.status}`);
    writeFileSync(dest, Buffer.from(await resp.arrayBuffer()));
    return dest;
  }

  /**
   * Download all files from a workspace. Returns list of local paths.
   *
   * ```ts
   * const paths = await client.workspaces.downloadAll(wsId, { to: "./output" });
   * ```
   */
  async downloadAll(workspaceId: string, options?: { to?: string; prefix?: string }): Promise<string[]> {
    const destDir = options?.to ?? ".";
    mkdirSync(destDir, { recursive: true });
    const results: string[] = [];
    let cursor: string | undefined;
    do {
      const fileList = await this.files(workspaceId, {
        prefix: options?.prefix,
        includeUrls: true,
        cursor,
      });
      for (const f of fileList.files ?? []) {
        const local = safeJoin(destDir, f.path);
        mkdirSync(dirname(local), { recursive: true });
        const resp = await fetch(f.url!);
        if (!resp.ok) throw new Error(`Download failed for ${f.path}: ${resp.status}`);
        writeFileSync(local, Buffer.from(await resp.arrayBuffer()));
        results.push(local);
      }
      cursor = fileList.hasMore ? (fileList.nextCursor ?? undefined) : undefined;
    } while (cursor);
    return results;
  }
}
