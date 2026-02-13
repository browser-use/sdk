import { z } from "zod";
import { HttpClient } from "../core/http.js";
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
