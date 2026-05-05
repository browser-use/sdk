import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

/** All fields are optional (server applies defaults); body itself is required by the spec. */
export type CreateBrowserBody = Partial<components["schemas"]["CreateBrowserSessionRequest"]>;
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
type BrowserSessionListResponse = components["schemas"]["BrowserSessionListResponse"];
type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type UpdateBrowserSessionRequest = components["schemas"]["UpdateBrowserSessionRequest"];
type BrowserDownloadListResponse = components["schemas"]["BrowserDownloadListResponse"];

export interface BrowserListParams {
  pageSize?: number;
  pageNumber?: number;
  filterBy?: string;
}

export interface BrowserDownloadsParams {
  limit?: number;
  cursor?: string;
  includeUrls?: boolean;
}

export class Browsers {
  constructor(private readonly http: HttpClient) {}

  /** Create a new browser session. */
  create(body: CreateBrowserBody = {}): Promise<BrowserSessionItemView> {
    if (body.proxyCountryCode) {
      body = { ...body, proxyCountryCode: body.proxyCountryCode.toLowerCase() as any };
    }
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

  /** List files the browser downloaded to S3 during the session. */
  downloads(sessionId: string, params?: BrowserDownloadsParams): Promise<BrowserDownloadListResponse> {
    return this.http.get<BrowserDownloadListResponse>(
      `/browsers/${sessionId}/downloads`,
      params as Record<string, unknown>,
    );
  }
}
