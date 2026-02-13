import { HttpClient } from "../core/http.js";
import { Sessions } from "./resources/sessions.js";
import { SessionRun } from "./helpers.js";
import type { components } from "../generated/v3/types.js";
import type { RunOptions } from "./helpers.js";

type RunTaskRequest = components["schemas"]["RunTaskRequest"];

const DEFAULT_BASE_URL = "https://api.browser-use.com/api/v3";

export interface BrowserUseOptions {
  apiKey?: string;
  baseUrl?: string;
  maxRetries?: number;
  timeout?: number;
}

export type RunSessionOptions = Partial<Omit<RunTaskRequest, "task">> &
  RunOptions;

export class BrowserUse {
  readonly sessions: Sessions;

  private readonly http: HttpClient;

  constructor(options: BrowserUseOptions = {}) {
    const apiKey =
      options.apiKey ?? process.env.BROWSER_USE_API_KEY ?? "";
    if (!apiKey) {
      throw new Error(
        "No API key provided. Pass apiKey or set BROWSER_USE_API_KEY.",
      );
    }
    this.http = new HttpClient({
      apiKey,
      baseUrl: options.baseUrl ?? DEFAULT_BASE_URL,
      maxRetries: options.maxRetries,
      timeout: options.timeout,
    });

    this.sessions = new Sessions(this.http);
  }

  /**
   * Create a session and run a task. `await` the result for the output string.
   *
   * ```ts
   * const output = await client.run("Find the top HN post");
   * ```
   */
  run(task: string, options?: RunSessionOptions): SessionRun {
    const { timeout, interval, ...rest } = options ?? {};
    const body = { task, ...rest } as RunTaskRequest;
    const promise = this.sessions.create(body);
    return new SessionRun(promise, this.sessions, { timeout, interval });
  }
}
