import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v3/types.js";

type RunTaskRequest = components["schemas"]["RunTaskRequest"];
/** All fields optional — omit `task` to create an idle session. */
export type CreateSessionBody = Partial<RunTaskRequest>;
type SessionResponse = components["schemas"]["SessionResponse"];
type SessionListResponse = components["schemas"]["SessionListResponse"];
type StopSessionRequest = components["schemas"]["StopSessionRequest"];
type MessageListResponse = components["schemas"]["MessageListResponse"];

export interface SessionListParams {
  page?: number;
  page_size?: number;
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
    return this.http.post<SessionResponse>("/sessions", body ?? {});
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

  /** List messages for a session with cursor-based pagination. */
  messages(sessionId: string, params?: SessionMessagesParams): Promise<MessageListResponse> {
    return this.http.get<MessageListResponse>(
      `/sessions/${sessionId}/messages`,
      params as Record<string, unknown>,
    );
  }

  /**
   * Poll until recording URLs are available. Returns presigned MP4 URLs.
   *
   * Returns an empty array if no recording was produced (e.g. the agent
   * answered without opening a browser, or recording was not enabled).
   */
  async waitForRecording(
    sessionId: string,
    options?: { timeout?: number; interval?: number },
  ): Promise<string[]> {
    const timeout = options?.timeout ?? 15_000;
    const interval = options?.interval ?? 2_000;
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      const session = await this.get(sessionId);
      if (session.recordingUrls?.length) return session.recordingUrls;
      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((r) => setTimeout(r, Math.min(interval, remaining)));
    }
    return [];
  }
}
