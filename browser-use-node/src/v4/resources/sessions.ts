import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type SessionInfo = components["schemas"]["SessionInfo"];
type SessionListResponse = components["schemas"]["SessionListResponse"];
type QueueMessageRequest = components["schemas"]["QueueMessageRequest"];
type QueuedMessage = components["schemas"]["QueuedMessage"];
type QueueListResponse = components["schemas"]["QueueListResponse"];

export interface SessionListParams {
  cursor?: string | null;
  limit?: number;
}

export interface SendMessageOptions {
  /** Optional server-side deduplication strategy, such as `exact-text-v1`. */
  deduplicate?: string | null;
}

export class Sessions {
  constructor(private readonly http: HttpClient) {}

  /** List sessions with cursor-based pagination, most recent first. */
  list(params?: SessionListParams): Promise<SessionListResponse> {
    return this.http.get<SessionListResponse>("/sessions", params as Record<string, unknown>);
  }

  /** Get session metadata (latest run id, status, ...). */
  get(sessionId: string): Promise<SessionInfo> {
    return this.http.get<SessionInfo>(`/sessions/${sessionId}`);
  }

  /** Immediately purge all data for a session on a ZDR-enabled project. */
  purge(sessionId: string): Promise<void> {
    return this.http.post<void>(`/sessions/${sessionId}/purge`);
  }

  /**
   * Send a message to the session. Runs as the next turn when the session is
   * busy; set `interrupt: true` to cancel the active run so the message runs
   * immediately.
   */
  sendMessage(
    sessionId: string,
    body: QueueMessageRequest,
    options?: SendMessageOptions,
  ): Promise<QueuedMessage> {
    if (options?.deduplicate != null) {
      return this.http.post<QueuedMessage>(
        `/sessions/${sessionId}/queue`,
        body,
        undefined,
        { "X-V4-Queue-Deduplicate": options.deduplicate },
      );
    }
    return this.http.post<QueuedMessage>(`/sessions/${sessionId}/queue`, body);
  }

  /** List the session's pending queued messages. */
  queue(sessionId: string): Promise<QueueListResponse> {
    return this.http.get<QueueListResponse>(`/sessions/${sessionId}/queue`);
  }

  /** Get one queued message, including terminal handoff states. */
  getMessage(sessionId: string, messageId: number): Promise<QueuedMessage> {
    return this.http.get<QueuedMessage>(`/sessions/${sessionId}/queue/${messageId}`);
  }

  /** Remove a pending message from the session's queue. */
  removeMessage(sessionId: string, messageId: number): Promise<QueuedMessage> {
    return this.http.delete<QueuedMessage>(`/sessions/${sessionId}/queue/${messageId}`);
  }
}
