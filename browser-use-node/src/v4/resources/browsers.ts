import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
type BrowserSessionListResponse = components["schemas"]["BrowserSessionListResponse"];
type BrowserDownloadListResponse = components["schemas"]["BrowserDownloadListResponse"];
export type CreateBrowserBody = Partial<components["schemas"]["CreateBrowserSessionRequest"]>;

export interface BrowserListParams {
  /** Tag terms: `key` matches any value, `key=value` matches exactly; all must match. */
  metadata?: string[];
  pageSize?: number;
  pageNumber?: number;
  filterBy?: components["schemas"]["BrowserSessionStatus"] | null;
  agentSessionId?: string | null;
}

export interface BrowserDownloadsParams {
  limit?: number;
  cursor?: string | null;
  includeUrls?: boolean;
}

export class Browsers {
  constructor(private readonly http: HttpClient) {}

  /** Create a new standalone browser session. */
  create(body: CreateBrowserBody = {}): Promise<BrowserSessionItemView> {
    if (body.metadata && Object.keys(body.metadata).length > 10) {
      throw new RangeError("metadata supports at most 10 key-value pairs");
    }
    return this.http.post<BrowserSessionItemView>("/browsers", body);
  }

  /** Stop a browser session and refund its unused time. */
  stop(sessionId: string): Promise<BrowserSessionView> {
    return this.http.patch<BrowserSessionView>(`/browsers/${sessionId}`, {
      action: "stop",
    });
  }

  /** List browser sessions for the project, most recent first. */
  list(params?: BrowserListParams): Promise<BrowserSessionListResponse> {
    return this.http.get<BrowserSessionListResponse>("/browsers", params as Record<string, unknown>);
  }

  /** Get a browser session, including its recording URL when ready. */
  get(sessionId: string): Promise<BrowserSessionView> {
    return this.http.get<BrowserSessionView>(`/browsers/${sessionId}`);
  }

  /** List files the browser downloaded during the session. */
  downloads(sessionId: string, params?: BrowserDownloadsParams): Promise<BrowserDownloadListResponse> {
    return this.http.get<BrowserDownloadListResponse>(
      `/browsers/${sessionId}/downloads`,
      params as Record<string, unknown>,
    );
  }
}
