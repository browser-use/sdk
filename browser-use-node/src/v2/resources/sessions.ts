import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

/** User-facing body: all fields are optional (API has defaults). */
type CreateSessionBody = Partial<components["schemas"]["CreateSessionRequest"]>;
type SessionItemView = components["schemas"]["SessionItemView"];
type SessionListResponse = components["schemas"]["SessionListResponse"];
type SessionView = components["schemas"]["SessionView"];
type ShareView = components["schemas"]["ShareView"];
type UpdateSessionRequest = components["schemas"]["UpdateSessionRequest"];

export interface SessionListParams {
  pageSize?: number;
  pageNumber?: number;
  filterBy?: string;
}

export class Sessions {
  constructor(private readonly http: HttpClient) {}

  /** Create a new session. */
  create(body?: CreateSessionBody): Promise<SessionItemView> {
    return this.http.post<SessionItemView>("/sessions", body);
  }

  /** List sessions with optional filtering. */
  list(params?: SessionListParams): Promise<SessionListResponse> {
    return this.http.get<SessionListResponse>("/sessions", params as Record<string, unknown>);
  }

  /** Get detailed session information. */
  get(sessionId: string): Promise<SessionView> {
    return this.http.get<SessionView>(`/sessions/${sessionId}`);
  }

  /** Update a session (generic PATCH). */
  update(sessionId: string, body: UpdateSessionRequest): Promise<SessionView> {
    return this.http.patch<SessionView>(`/sessions/${sessionId}`, body);
  }

  /** Stop a session and all its running tasks. */
  stop(sessionId: string): Promise<SessionView> {
    return this.update(sessionId, { action: "stop" });
  }

  /** Delete a session with all its tasks. */
  delete(sessionId: string): Promise<void> {
    return this.http.delete<void>(`/sessions/${sessionId}`);
  }

  /** Get public share information for a session. */
  getShare(sessionId: string): Promise<ShareView> {
    return this.http.get<ShareView>(`/sessions/${sessionId}/public-share`);
  }

  /** Create or return existing public share for a session. */
  createShare(sessionId: string): Promise<ShareView> {
    return this.http.post<ShareView>(`/sessions/${sessionId}/public-share`);
  }

  /** Remove public share for a session. */
  deleteShare(sessionId: string): Promise<void> {
    return this.http.delete<void>(`/sessions/${sessionId}/public-share`);
  }

  /** Purge all session data (ZDR projects only). */
  purge(sessionId: string): Promise<void> {
    return this.http.post<void>(`/sessions/${sessionId}/purge`);
  }
}
