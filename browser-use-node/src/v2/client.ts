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
import { TaskHandle } from "./helpers.js";
import type { CreateTaskBody } from "./resources/tasks.js";

const DEFAULT_BASE_URL = "https://api.browser-use.com/api/v2";

export interface BrowserUseOptions {
  apiKey: string;
  baseUrl?: string;
  maxRetries?: number;
  timeout?: number;
}

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

  constructor(options: BrowserUseOptions) {
    this.http = new HttpClient({
      apiKey: options.apiKey,
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
   * Create a task and return a TaskHandle for polling/streaming.
   *
   * Pass a Zod `schema` to get auto-parsed typed output from `complete()`.
   * The schema is automatically converted to JSON Schema for the API and
   * used for client-side validation of the response.
   *
   * ```ts
   * // Without structured output
   * const handle = client.run({ task: "Find the top HN post" });
   * const result = await handle.complete();
   * console.log(result.output); // string | null
   *
   * // With structured output (Zod)
   * import { z } from "zod";
   * const Product = z.object({ name: z.string(), price: z.number() });
   * const handle = client.run({ task: "Find product info", schema: Product });
   * const result = await handle.complete();
   * console.log(result.parsed); // { name: string, price: number } | null
   * ```
   */
  run(body: CreateTaskBody): TaskHandle<string>;
  run<T extends z.ZodType>(body: CreateTaskBody & { schema: T }): TaskHandle<z.output<T>>;
  run(body: CreateTaskBody & { schema?: z.ZodType }): TaskHandle<any> {
    const { schema, ...rest } = body;
    if (schema) {
      rest.structuredOutput = JSON.stringify(z.toJSONSchema(schema));
    }
    const promise = this.tasks.create(rest);
    return new TaskHandle(promise, this.tasks, schema);
  }
}
