import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

type CreateBrowserSessionRequest = components["schemas"]["CreateBrowserSessionRequest"];
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
type BrowserSessionListResponse = components["schemas"]["BrowserSessionListResponse"];
type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type UpdateBrowserSessionRequest = components["schemas"]["UpdateBrowserSessionRequest"];

export interface BrowserListParams {
  pageSize?: number;
  pageNumber?: number;
  filterBy?: string;
}

export class Browsers {
  constructor(private readonly http: HttpClient) {}

  /** Create a new browser session. */
  create(body?: CreateBrowserSessionRequest): Promise<BrowserSessionItemView> {
    return this.http.post<BrowserSessionItemView>("/browsers", body);
  }

  /** List browser sessions with optional filtering. */
  list(params?: BrowserListParams): Promise<BrowserSessionListResponse> {
    return this.http.get<BrowserSessionListResponse>(
      "/browsers",
      params as Record<string, unknown>,
    );
  }

  /** Get detailed browser session information. */
  get(sessionId: string): Promise<BrowserSessionView> {
    return this.http.get<BrowserSessionView>(`/browsers/${sessionId}`);
  }

  /** Update a browser session (generic PATCH). */
  update(sessionId: string, body: UpdateBrowserSessionRequest): Promise<BrowserSessionView> {
    return this.http.patch<BrowserSessionView>(`/browsers/${sessionId}`, body);
  }

  /** Stop a browser session. */
  stop(sessionId: string): Promise<BrowserSessionView> {
    return this.update(sessionId, { action: "stop" });
  }
}
