import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v3/types.js";

type CreateBrowserSessionRequest = components["schemas"]["CreateBrowserSessionRequest"];
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type BrowserSessionListResponse = components["schemas"]["BrowserSessionListResponse"];
type UpdateBrowserSessionRequest = components["schemas"]["UpdateBrowserSessionRequest"];
type BrowserDownloadListResponse = components["schemas"]["BrowserDownloadListResponse"];

export interface BrowserListParams {
  page?: number;
  page_size?: number;
}

export interface BrowserDownloadsParams {
  limit?: number;
  cursor?: string;
  includeUrls?: boolean;
}

export class Browsers {
  constructor(private readonly http: HttpClient) {}

  /** Create a standalone browser session. */
  create(body: Partial<CreateBrowserSessionRequest> = {}): Promise<BrowserSessionItemView> {
    return this.http.post<BrowserSessionItemView>("/browsers", body);
  }

  /** List browser sessions for the authenticated project. */
  list(params?: BrowserListParams): Promise<BrowserSessionListResponse> {
    return this.http.get<BrowserSessionListResponse>("/browsers", params as Record<string, unknown>);
  }

  /** Get browser session details. */
  get(sessionId: string): Promise<BrowserSessionView> {
    return this.http.get<BrowserSessionView>(`/browsers/${sessionId}`);
  }

  /** Update a browser session (e.g. stop it). */
  update(sessionId: string, body: UpdateBrowserSessionRequest): Promise<BrowserSessionView> {
    return this.http.patch<BrowserSessionView>(`/browsers/${sessionId}`, body);
  }

  /** Stop a browser session. Convenience wrapper around update. */
  stop(sessionId: string): Promise<BrowserSessionView> {
    return this.update(sessionId, { action: "stop" });
  }

  /** List files the browser downloaded to S3 during the session. */
  downloads(sessionId: string, params?: BrowserDownloadsParams): Promise<BrowserDownloadListResponse> {
    return this.http.get<BrowserDownloadListResponse>(
      `/browsers/${sessionId}/downloads`,
      params as Record<string, unknown>,
    );
  }
}
