import { z } from "zod";
import { HttpClient } from "../core/http.js";
import {
  X402_BASE_URL_DEFAULT_V2,
  type X402Client,
  wrapFetchWithX402,
  x402ClientFromPrivateKey,
} from "../core/x402.js";
import { Billing } from "./resources/billing.js";
import { Browsers } from "./resources/browsers.js";
import { Files } from "./resources/files.js";
import { Marketplace } from "./resources/marketplace.js";
import { Profiles } from "./resources/profiles.js";
import { Sessions } from "./resources/sessions.js";
import { Skills } from "./resources/skills.js";
import { Tasks } from "./resources/tasks.js";
import { TaskRun } from "./helpers.js";
import type { CreateTaskBody } from "./resources/tasks.js";
import type { RunOptions } from "./helpers.js";

const DEFAULT_BASE_URL = "https://api.browser-use.com/api/v2";

export interface BrowserUseOptions {
  apiKey?: string;
  baseUrl?: string;
  maxRetries?: number;
  timeout?: number;
  /** Pre-built x402 client for pay-per-request authentication. */
  x402?: X402Client;
  /** EVM wallet private key for x402 mode (also reads `BROWSER_USE_X402_PRIVATE_KEY`). */
  x402PrivateKey?: string;
}

export type RunTaskOptions = Partial<Omit<CreateTaskBody, "task">> &
  RunOptions & { schema?: z.ZodType };

export class BrowserUse {
  readonly billing: Billing;
  readonly tasks: Tasks;
  readonly sessions: Sessions;
  readonly files: Files;
  readonly profiles: Profiles;
  readonly browsers: Browsers;
  readonly skills: Skills;
  readonly marketplace: Marketplace;

  private readonly http: HttpClient;

  constructor(options: BrowserUseOptions = {}) {
    const x402PrivateKey =
      options.x402PrivateKey ?? process.env.BROWSER_USE_X402_PRIVATE_KEY;

    if (options.x402 || x402PrivateKey) {
      // Top-up mode: when apiKey is also set, forward it as a header so the
      // backend credits the API key's project instead of one keyed to the wallet.
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
        baseUrl: options.baseUrl ?? X402_BASE_URL_DEFAULT_V2,
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
    this.tasks = new Tasks(this.http);
    this.sessions = new Sessions(this.http);
    this.files = new Files(this.http);
    this.profiles = new Profiles(this.http);
    this.browsers = new Browsers(this.http);
    this.skills = new Skills(this.http);
    this.marketplace = new Marketplace(this.http);
  }

  /**
   * Run an AI agent task.
   *
   * ```ts
   * // Simple — just get the output
   * const output = await client.run("Find the top HN post");
   *
   * // Structured output (Zod)
   * const data = await client.run("Find product info", { schema: ProductSchema });
   *
   * // Step-by-step progress
   * for await (const step of client.run("Go to google.com")) {
   *   console.log(`[${step.number}] ${step.nextGoal}`);
   * }
   * ```
   */
  run(task: string, options?: Omit<RunTaskOptions, "schema">): TaskRun<string>;
  run<T extends z.ZodType>(task: string, options: RunTaskOptions & { schema: T }): TaskRun<z.output<T>>;
  run(task: string, options?: RunTaskOptions): TaskRun<any> {
    const { schema, timeout, interval, ...rest } = options ?? {};
    const body: CreateTaskBody = { task, ...rest };
    if (schema) {
      body.structuredOutput = JSON.stringify(z.toJSONSchema(schema));
    }
    const promise = this.tasks.create(body);
    return new TaskRun(promise, this.tasks, schema, { timeout, interval });
  }
}
