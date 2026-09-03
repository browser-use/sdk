import { HttpClient } from "../core/http.js";
import { Browsers } from "./resources/browsers.js";
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
    this.runs = new Runs(this.http);
    this.sessions = new Sessions(this.http);
    this.workspaces = new Workspaces(this.http);
  }
}
