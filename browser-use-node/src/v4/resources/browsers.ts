import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type BrowserProxyUpdateRequest = components["schemas"]["BrowserProxyUpdateRequest"];
type CustomProxy = components["schemas"]["CustomProxy"];

export type UpdateBrowserProxyBody = Omit<BrowserProxyUpdateRequest, "customProxy"> & {
  customProxy?: Omit<CustomProxy, "ignoreCertErrors"> & { ignoreCertErrors?: boolean };
} & Record<string, unknown>;
type BrowserProxyView = components["schemas"]["BrowserProxyView"];
type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
type BrowserSessionListResponse = components["schemas"]["BrowserSessionListResponse"];
type BrowserDownloadListResponse = components["schemas"]["BrowserDownloadListResponse"];
type BrowserAccessTokenCreated = components["schemas"]["BrowserAccessTokenCreated"];
type BrowserAccessTokenList = components["schemas"]["BrowserAccessTokenList"];
type BrowserAccessTokenRevoked = components["schemas"]["BrowserAccessTokenRevoked"];
type BrowserAccessEventList = components["schemas"]["BrowserAccessEventList"];
export type CreateAccessTokenBody = Partial<components["schemas"]["CreateBrowserAccessTokenRequest"]> & Record<string, unknown>;
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

export interface BrowserAccessLogParams {
  pageSize?: number;
  pageNumber?: number;
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

  /** Get the proxy for a browser session. */
  getProxy(sessionId: string): Promise<BrowserProxyView> {
    return this.http.get<BrowserProxyView>(`/browsers/${sessionId}/proxy`);
  }

  /** Update the proxy for a browser session. */
  updateProxy(
    sessionId: string,
    body?: UpdateBrowserProxyBody,
  ): Promise<BrowserProxyView> {
    return this.http.patch<BrowserProxyView>(`/browsers/${sessionId}/proxy`, body);
  }

  /** List files the browser downloaded during the session. */
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

  /** Revoke one access token and close its open connections. */
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
