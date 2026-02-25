import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v3/types.js";

type RunTaskRequest = components["schemas"]["RunTaskRequest"];
/** Like RunTaskRequest but only `task` is required; fields with server defaults are optional. */
export type CreateSessionBody = Pick<RunTaskRequest, "task"> & Partial<Omit<RunTaskRequest, "task">>;
type SessionResponse = components["schemas"]["SessionResponse"];
type SessionListResponse = components["schemas"]["SessionListResponse"];
type FileListResponse = components["schemas"]["FileListResponse"];

export interface SessionListParams {
  page?: number;
  page_size?: number;
}

export interface SessionFilesParams {
  prefix?: string;
  limit?: number;
  cursor?: string | null;
  includeUrls?: boolean;
}

export class Sessions {
  constructor(private readonly http: HttpClient) {}

  /** Create a session and run a task. */
  create(body: CreateSessionBody): Promise<SessionResponse> {
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

  /** Stop a session. */
  stop(sessionId: string): Promise<SessionResponse> {
    return this.http.post<SessionResponse>(`/sessions/${sessionId}/stop`);
  }

  /** List files in a session's workspace. */
  files(sessionId: string, params?: SessionFilesParams): Promise<FileListResponse> {
    return this.http.get<FileListResponse>(
      `/sessions/${sessionId}/files`,
      params as Record<string, unknown>,
    );
  }
}
