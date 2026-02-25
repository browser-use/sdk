import { z } from "zod";
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
  RunOptions & { schema?: z.ZodType };

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
   * Create a session and run a task. `await` the result for a typed SessionResult.
   *
   * ```ts
   * // Simple — just get the output
   * const result = await client.run("Find the top HN post");
   * console.log(result.output);
   *
   * // Structured output (Zod)
   * const result = await client.run("Find product info", { schema: ProductSchema });
   * console.log(result.output.name); // fully typed
   * ```
   */
  run(task: string, options?: Omit<RunSessionOptions, "schema">): SessionRun<string>;
  run<T extends z.ZodType>(task: string, options: RunSessionOptions & { schema: T }): SessionRun<z.output<T>>;
  run(task: string, options?: RunSessionOptions): SessionRun<any> {
    const { schema, timeout, interval, ...rest } = options ?? {};
    const body = { task, ...rest } as RunTaskRequest;
    if (schema) {
      body.outputSchema = z.toJSONSchema(schema) as Record<string, unknown>;
    }
    const promise = this.sessions.create(body);
    return new SessionRun(promise, this.sessions, schema, { timeout, interval });
  }
}
