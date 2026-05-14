import { z } from "zod";
import { HttpClient } from "../core/http.js";
import {
  X402_BASE_URL_DEFAULT,
  type X402Client,
  wrapFetchWithX402,
  x402ClientFromPrivateKey,
} from "../core/x402.js";
import { Billing } from "./resources/billing.js";
import { Browsers } from "./resources/browsers.js";
import { Profiles } from "./resources/profiles.js";
import { Sessions } from "./resources/sessions.js";
import { Workspaces } from "./resources/workspaces.js";
import { SessionRun } from "./helpers.js";
import type { components } from "../generated/v3/types.js";
import type { RunOptions } from "./helpers.js";

type RunTaskRequest = components["schemas"]["app__endpoints__api__v3__sessions__views__RunTaskRequest"];

const DEFAULT_BASE_URL = "https://api.browser-use.com/api/v3";

export interface BrowserUseOptions {
  apiKey?: string;
  baseUrl?: string;
  maxRetries?: number;
  timeout?: number;
  /**
   * Use your own LLM API key configured in Browser Use project settings for v3 agent runs.
   */
  useOwnKey?: boolean;
  /**
   * Pre-built x402 client (advanced — for custom signers / multi-network).
   * If set, the SDK uses pay-per-request authentication via USDC instead of
   * an API key. Requires the optional peer deps `@x402/fetch`, `@x402/evm`,
   * and `viem`.
   */
  x402?: X402Client;
  /**
   * EVM wallet private key for x402 mode. Equivalent to building an x402
   * client from this key and passing it as `x402`. Falls back to
   * `BROWSER_USE_X402_PRIVATE_KEY`.
   */
  x402PrivateKey?: string;
}

export type RunSessionOptions = Partial<Omit<RunTaskRequest, "task">> &
  RunOptions & { schema?: z.ZodType };

export class BrowserUse {
  readonly billing: Billing;
  readonly browsers: Browsers;
  readonly profiles: Profiles;
  readonly sessions: Sessions;
  readonly workspaces: Workspaces;

  private readonly http: HttpClient;

  constructor(options: BrowserUseOptions = {}) {
    const x402PrivateKey =
      options.x402PrivateKey ?? process.env.BROWSER_USE_X402_PRIVATE_KEY;

    if (options.x402 || x402PrivateKey) {
      // x402 mode — defer x402 client + wrapped fetch resolution to first request.
      // If apiKey is also set, it's forwarded as a header so the backend
      // credits the API key's project (top-up mode) instead of one keyed
      // to the wallet.
      const topupKey = options.apiKey ?? process.env.BROWSER_USE_API_KEY ?? "";
      const fetchPromise = (async () => {
        const x402Client = options.x402 ?? (await x402ClientFromPrivateKey(x402PrivateKey!));
        return wrapFetchWithX402(globalThis.fetch, x402Client);
      })();
      // Suppress unhandled-rejection warnings if the user constructs the client
      // but never makes a request
      fetchPromise.catch(() => {});
      this.http = new HttpClient({
        apiKey: topupKey,
        baseUrl: options.baseUrl ?? X402_BASE_URL_DEFAULT,
        maxRetries: options.maxRetries,
        timeout: options.timeout,
        fetch: fetchPromise,
      });
    } else {
      const apiKey =
        options.apiKey ?? process.env.BROWSER_USE_API_KEY ?? "";
      if (!apiKey) {
        throw new Error(
          "No credentials provided. Pass apiKey / set BROWSER_USE_API_KEY, " +
            "or pass x402PrivateKey / set BROWSER_USE_X402_PRIVATE_KEY for " +
            "pay-per-request access via USDC.",
        );
      }
      this.http = new HttpClient({
        apiKey,
        baseUrl: options.baseUrl ?? DEFAULT_BASE_URL,
        maxRetries: options.maxRetries,
        timeout: options.timeout,
      });
    }

    this.billing = new Billing(this.http);
    this.browsers = new Browsers(this.http);
    this.profiles = new Profiles(this.http);
    this.sessions = new Sessions(this.http, { useOwnKey: options.useOwnKey });
    this.workspaces = new Workspaces(this.http);
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
    if (body.proxyCountryCode) {
      body.proxyCountryCode = body.proxyCountryCode.toLowerCase() as any;
    }
    if (schema) {
      if (typeof schema !== "object" || !("_zod" in schema || "_def" in schema)) {
        throw new Error(
          "schema must be a Zod schema (e.g. z.object({...})). " +
          "Make sure you are using Zod v4: npm install zod@4"
        );
      }
      body.outputSchema = z.toJSONSchema(schema) as Record<string, unknown>;
    }
    // Auto keep_alive when dispatching to an existing session
    if (body.sessionId && body.keepAlive === undefined) {
      body.keepAlive = true;
    }
    // For follow-up runs on an existing session, snapshot the latest message
    // cursor before creating the new task so the iterator skips old messages.
    if (body.sessionId) {
      const sid = body.sessionId;
      const sessions = this.sessions;
      let startCursor: string | undefined;
      const promise = sessions
        .messages(sid, { limit: 1 })
        .then((resp) => {
          const last = resp.messages[resp.messages.length - 1];
          startCursor = last?.id;
        })
        .then(() => sessions.create(body));
      // startCursor is set before createPromise resolves, so the iterator
      // (which awaits _ensureSessionId first) will see the correct value.
      return new SessionRun(promise, this.sessions, schema, {
        timeout,
        interval,
        get _startCursor() { return startCursor; },
      });
    }
    const promise = this.sessions.create(body);
    return new SessionRun(promise, this.sessions, schema, { timeout, interval });
  }
}
