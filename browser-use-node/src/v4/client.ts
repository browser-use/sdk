import { HttpClient } from "../core/http.js";
import { Browsers } from "./resources/browsers.js";
import { Integrations } from "./resources/integrations.js";
import { NetworkPolicies } from "./resources/network-policies.js";
import { Profiles } from "./resources/profiles.js";
import { Extensions } from "./resources/extensions.js";
import { Runs } from "./resources/runs.js";
import { Sessions } from "./resources/sessions.js";
import { Workspaces } from "./resources/workspaces.js";

const DEFAULT_BASE_URL = "https://api.browser-use.com/api/v4";

export interface BrowserUseOptions {
  apiKey?: string;
  baseUrl?: string;
  maxRetries?: number;
  timeout?: number;
}

export class BrowserUse {
  readonly browsers: Browsers;
  readonly integrations: Integrations;
  readonly networkPolicies: NetworkPolicies;
  readonly profiles: Profiles;
  readonly extensions: Extensions;
  readonly runs: Runs;
  readonly sessions: Sessions;
  readonly workspaces: Workspaces;

  private readonly http: HttpClient;

  constructor(options: BrowserUseOptions = {}) {
    const apiKey = options.apiKey ?? process.env.BROWSER_USE_API_KEY ?? "";
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

    this.browsers = new Browsers(this.http);
    this.integrations = new Integrations(this.http);
    this.networkPolicies = new NetworkPolicies(this.http);
    this.profiles = new Profiles(this.http);
    this.extensions = new Extensions(this.http);
    this.runs = new Runs(this.http);
    this.sessions = new Sessions(this.http);
    this.workspaces = new Workspaces(this.http);
  }

  /** Send a feedback message (1-5000 chars) to the Browser Use team. */
  async feedback(message: string, extra: Record<string, unknown> = {}): Promise<void> {
    // POST /feedback is hand-written: the route is not in the OpenAPI spec.
    await this.http.post<void>("/feedback", { ...extra, message });
  }
}
