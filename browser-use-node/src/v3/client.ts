import { HttpClient } from "../core/http.js";
import { Sessions } from "./resources/sessions.js";
import { SessionHandle } from "./helpers.js";
import type { components } from "../generated/v3/types.js";

type RunTaskRequest = components["schemas"]["RunTaskRequest"];

const DEFAULT_BASE_URL = "https://api.browser-use.com/api/v3";

export interface BrowserUseOptions {
  apiKey: string;
  baseUrl?: string;
  maxRetries?: number;
  timeout?: number;
}

export class BrowserUse {
  readonly sessions: Sessions;

  private readonly http: HttpClient;

  constructor(options: BrowserUseOptions) {
    this.http = new HttpClient({
      apiKey: options.apiKey,
      baseUrl: options.baseUrl ?? DEFAULT_BASE_URL,
      maxRetries: options.maxRetries,
      timeout: options.timeout,
    });

    this.sessions = new Sessions(this.http);
  }

  /**
   * Create a session and return a SessionHandle for polling/streaming.
   *
   * ```ts
   * const handle = client.run({ task: "Find the top HN post" });
   * const result = await handle.complete();
   * ```
   */
  run(body: RunTaskRequest): SessionHandle {
    const promise = this.sessions.create(body);
    return new SessionHandle(promise, this.sessions);
  }
}
