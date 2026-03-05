import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v3/types.js";

type RunTaskRequest = components["schemas"]["RunTaskRequest"];
/** All fields optional — omit `task` to create an idle session. */
export type CreateSessionBody = Partial<RunTaskRequest>;
type SessionResponse = components["schemas"]["SessionResponse"];
type SessionListResponse = components["schemas"]["SessionListResponse"];
type FileListResponse = components["schemas"]["FileListResponse"];
type StopSessionRequest = components["schemas"]["StopSessionRequest"];
type FileUploadRequest = components["schemas"]["FileUploadRequest"];
type FileUploadResponse = components["schemas"]["FileUploadResponse"];
type MessageListResponse = components["schemas"]["MessageListResponse"];

export interface SessionListParams {
  page?: number;
  page_size?: number;
}

export interface SessionFilesParams {
  prefix?: string;
  limit?: number;
  cursor?: string | null;
  includeUrls?: boolean;
  shallow?: boolean;
}

export interface SessionMessagesParams {
  after?: string | null;
  before?: string | null;
  limit?: number;
}

export class Sessions {
  constructor(private readonly http: HttpClient) {}

  /** Create a session and optionally dispatch a task. */
  create(body?: CreateSessionBody): Promise<SessionResponse> {
    return this.http.post<SessionResponse>("/sessions", body);
  }

  /** List sessions for the authenticated project. */
  list(params?: SessionListParams): Promise<SessionListResponse> {
    return this.http.get<SessionListResponse>("/sessions", params as Record<string, unknown>);
  }

  /** Get session details. */
  get(sessionId: string): Promise<SessionResponse> {
    return this.http.get<SessionResponse>(`/sessions/${sessionId}`);
  }

  /** Stop a session or the running task. */
  stop(sessionId: string, body?: StopSessionRequest): Promise<SessionResponse> {
    return this.http.post<SessionResponse>(`/sessions/${sessionId}/stop`, body);
  }

  /** Soft-delete a session. */
  delete(sessionId: string): Promise<void> {
    return this.http.delete<void>(`/sessions/${sessionId}`);
  }

  /** Get presigned upload URLs for session files. */
  uploadFiles(sessionId: string, body: FileUploadRequest): Promise<FileUploadResponse> {
    return this.http.post<FileUploadResponse>(`/sessions/${sessionId}/files/upload`, body);
  }

  /** List files in a session's workspace. */
  files(sessionId: string, params?: SessionFilesParams): Promise<FileListResponse> {
    return this.http.get<FileListResponse>(
      `/sessions/${sessionId}/files`,
      params as Record<string, unknown>,
    );
  }

  /** List messages for a session with cursor-based pagination. */
  messages(sessionId: string, params?: SessionMessagesParams): Promise<MessageListResponse> {
    return this.http.get<MessageListResponse>(
      `/sessions/${sessionId}/messages`,
      params as Record<string, unknown>,
    );
  }
}
