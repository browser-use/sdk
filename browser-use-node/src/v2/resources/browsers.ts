import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

/** All fields are optional (server applies defaults); body itself is required by the spec. */
export type CreateBrowserBody = Partial<components["schemas"]["CreateBrowserSessionRequest"]>;
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
type BrowserSessionListResponse = components["schemas"]["BrowserSessionListResponse"];
type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type UpdateBrowserSessionRequest = components["schemas"]["UpdateBrowserSessionRequest"];
type BrowserDownloadListResponse = components["schemas"]["BrowserDownloadListResponse"];
type BrowserAccessTokenCreated = components["schemas"]["BrowserAccessTokenCreated"];
type BrowserAccessTokenList = components["schemas"]["BrowserAccessTokenList"];
type BrowserAccessTokenRevoked = components["schemas"]["BrowserAccessTokenRevoked"];
type BrowserAccessEventList = components["schemas"]["BrowserAccessEventList"];
export type CreateAccessTokenBody = Partial<components["schemas"]["CreateBrowserAccessTokenRequest"]>;

export interface BrowserListParams {
  metadata?: string[];
  pageSize?: number;
  pageNumber?: number;
  filterBy?: string;
  agentSessionId?: string | null;
}

export interface BrowserDownloadsParams {
  limit?: number;
  cursor?: string;
  includeUrls?: boolean;
}

export interface BrowserAccessLogParams {
  pageSize?: number;
  pageNumber?: number;
}

export class Browsers {
  constructor(private readonly http: HttpClient) {}

  /** Create a new browser session. */
  create(body: CreateBrowserBody = {}): Promise<BrowserSessionItemView> {
    if (body.metadata && Object.keys(body.metadata).length > 10) {
      throw new RangeError("metadata supports at most 10 key-value pairs");
    }
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

  /** Create an access token and a CDP URL that holds it; only this answer shows the token. */
  createAccessToken(sessionId: string, body?: CreateAccessTokenBody): Promise<BrowserAccessTokenCreated> {
    return this.http.post<BrowserAccessTokenCreated>(`/browsers/${sessionId}/access-tokens`, body);
  }

  /** List the access tokens of a browser session, without the secret values. */
  listAccessTokens(sessionId: string): Promise<BrowserAccessTokenList> {
    return this.http.get<BrowserAccessTokenList>(`/browsers/${sessionId}/access-tokens`);
  }

  /** Revoke one token and close its connections; viewer tokens answer 409, and a system token revoke stops our services. */
  revokeAccessToken(sessionId: string, tokenId: string): Promise<BrowserAccessTokenRevoked> {
    return this.http.delete<BrowserAccessTokenRevoked>(`/browsers/${sessionId}/access-tokens/${tokenId}`);
  }

  /** Revoke all customer and viewer tokens of a browser session and close their connections. */
  revokeAllAccessTokens(sessionId: string): Promise<BrowserAccessTokenRevoked> {
    return this.http.delete<BrowserAccessTokenRevoked>(`/browsers/${sessionId}/access-tokens`);
  }

  /** List the access token events of a browser session, newest first. */
  getAccessLog(sessionId: string, params?: BrowserAccessLogParams): Promise<BrowserAccessEventList> {
    return this.http.get<BrowserAccessEventList>(
      `/browsers/${sessionId}/access-log`,
      params as Record<string, unknown>,
    );
  }
}
