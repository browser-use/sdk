import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type BrowserSessionView = components["schemas"]["BrowserSessionView"];
type BrowserSessionItemView = components["schemas"]["BrowserSessionItemView"];
export type CreateBrowserBody = Partial<components["schemas"]["CreateBrowserSessionRequest"]>;

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
}
