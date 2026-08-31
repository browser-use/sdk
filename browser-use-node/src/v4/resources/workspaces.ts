import { randomUUID } from "crypto";
import { lstat, mkdir, open, readFile, rename, rm, stat } from "fs/promises";
import { basename, dirname, extname, isAbsolute, join, relative, resolve, sep } from "path";
import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type WorkspaceInfo = components["schemas"]["WorkspaceInfo"];
type WorkspaceCreateRequest = components["schemas"]["WorkspaceCreateRequest"];
type WorkspaceUpdateRequest = components["schemas"]["WorkspaceUpdateRequest"];
type WorkspaceSizeInfo = components["schemas"]["WorkspaceSizeInfo"];
type WorkspaceFileInfo = components["schemas"]["WorkspaceFileInfo"];
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

const DOWNLOAD_TIMEOUT_MS = 60_000;

function guessContentType(path: string): string {
  return MIME_TYPES[extname(path).toLowerCase()] ?? "application/octet-stream";
}

async function safeJoin(base: string, untrusted: string): Promise<string> {
  const root = resolve(base);
  const destination = resolve(root, untrusted);
  const remainder = relative(root, destination);
  if (remainder === ".." || remainder.startsWith(`..${sep}`) || isAbsolute(remainder)) {
    throw new Error(`Path traversal detected: ${untrusted}`);
  }

  // Reject existing symlinked parents so a workspace-controlled path cannot
  // redirect a bulk download outside the caller's destination directory.
  let current = root;
  const parentRemainder = relative(root, dirname(destination));
  for (const component of parentRemainder.split(sep).filter(Boolean)) {
    current = join(current, component);
    try {
      const info = await lstat(current);
      if (info.isSymbolicLink() || !info.isDirectory()) {
        throw new Error(`Path traversal detected: ${untrusted}`);
      }
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
      await mkdir(current);
    }
  }
  return destination;
}

async function streamToPath(url: string, destination: string): Promise<void> {
  await mkdir(dirname(destination), { recursive: true });
  const temporary = join(
    dirname(destination),
    `.${basename(destination)}.${randomUUID()}.tmp`,
  );
  let output: Awaited<ReturnType<typeof open>> | undefined;
  try {
    const response = await fetch(url, {
      signal: AbortSignal.timeout(DOWNLOAD_TIMEOUT_MS),
    });
    if (!response.ok) {
      await response.body?.cancel().catch(() => undefined);
      throw new Error(`Download failed: ${response.status} ${response.statusText}`);
    }
    if (!response.body) {
      throw new Error("Download failed: response body is empty");
    }
    output = await open(temporary, "wx");
    for await (const chunk of response.body) {
      let offset = 0;
      while (offset < chunk.byteLength) {
        const { bytesWritten } = await output.write(
          chunk,
          offset,
          chunk.byteLength - offset,
        );
        if (bytesWritten === 0) {
          throw new Error("Download failed: file write made no progress");
        }
        offset += bytesWritten;
      }
    }
    await output.close();
    output = undefined;
    await rename(temporary, destination);
  } catch (error) {
    await output?.close().catch(() => undefined);
    await rm(temporary, { force: true }).catch(() => undefined);
    throw error;
  }
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

  private async fileWithFreshUrl(workspaceId: string, path: string): Promise<WorkspaceFileInfo> {
    let cursor: string | null | undefined;
    while (true) {
      const page = await this.files(workspaceId, {
        prefix: path,
        includeUrls: true,
        cursor,
      });
      const match = page.files.find((file) => file.path === path);
      if (match) return match;
      if (!page.hasMore) throw new Error(`File not found in workspace: ${path}`);
      if (!page.nextCursor) {
        throw new Error("Workspace file response hasMore=true but no nextCursor");
      }
      cursor = page.nextCursor;
    }
  }

  /** Download one exact workspace file with a fresh presigned URL. */
  async download(
    workspaceId: string,
    path: string,
    options: { to?: string } = {},
  ): Promise<string> {
    const file = await this.fileWithFreshUrl(workspaceId, path);
    if (!file.url) {
      throw new Error(`No download URL for ${JSON.stringify(path)}; ensure includeUrls=true`);
    }
    const destination = options.to ?? basename(file.path);
    await streamToPath(file.url, destination);
    return destination;
  }

  /**
   * Download matching workspace files below `to`. Each file gets a fresh URL
   * immediately before it streams, so earlier downloads cannot expire later URLs.
   */
  async downloadAll(
    workspaceId: string,
    options: { to?: string; prefix?: string } = {},
  ): Promise<string[]> {
    const destination = resolve(options.to ?? ".");
    await mkdir(destination, { recursive: true });
    const results: string[] = [];
    let cursor: string | null | undefined;
    while (true) {
      const page = await this.files(workspaceId, {
        prefix: options.prefix,
        cursor,
      });
      for (const file of page.files) {
        const local = await safeJoin(destination, file.path);
        results.push(await this.download(workspaceId, file.path, { to: local }));
      }
      if (!page.hasMore) return results;
      if (!page.nextCursor) {
        throw new Error("Workspace file response hasMore=true but no nextCursor");
      }
      cursor = page.nextCursor;
    }
  }
}
