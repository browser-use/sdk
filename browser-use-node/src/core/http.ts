import { BrowserUseError } from "./errors.js";

export interface HttpClientOptions {
  apiKey: string;
  baseUrl: string;
  maxRetries?: number;
  timeout?: number;
}

export class HttpClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly maxRetries: number;
  private readonly timeout: number;

  constructor(options: HttpClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl.replace(/\/+$/, "");
    this.maxRetries = options.maxRetries ?? 3;
    this.timeout = options.timeout ?? 30_000;
  }

  async request<T>(
    method: string,
    path: string,
    options?: {
      body?: unknown;
      query?: Record<string, unknown>;
      signal?: AbortSignal;
    },
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    if (options?.query) {
      for (const [key, value] of Object.entries(options.query)) {
        if (value !== undefined && value !== null) {
          url.searchParams.set(key, String(value));
        }
      }
    }

    const headers: Record<string, string> = {
      "X-Browser-Use-API-Key": this.apiKey,
    };
    if (options?.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    let lastError: unknown;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      if (attempt > 0) {
        const delay = Math.min(1000 * 2 ** (attempt - 1), 10_000);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      try {
        const response = await fetch(url.toString(), {
          method,
          headers,
          body: options?.body !== undefined ? JSON.stringify(options.body) : undefined,
          signal: options?.signal ?? controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          if (response.status === 204) {
            return undefined as T;
          }
          return (await response.json()) as T;
        }

        const shouldRetry =
          (response.status === 429 || response.status >= 500) &&
          attempt < this.maxRetries;

        if (shouldRetry) {
          let errorBody: unknown;
          try {
            errorBody = await response.json();
          } catch {
            /* ignore parse errors */
          }
          lastError = new BrowserUseError(
            response.status,
            `HTTP ${response.status}`,
            errorBody,
          );
          continue;
        }

        let errorBody: unknown;
        try {
          errorBody = await response.json();
        } catch {
          /* ignore parse errors */
        }
        const message =
          typeof errorBody === "object" &&
          errorBody !== null &&
          "detail" in errorBody
            ? String((errorBody as Record<string, unknown>).detail)
            : `HTTP ${response.status}`;
        throw new BrowserUseError(response.status, message, errorBody);
      } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof BrowserUseError) {
          throw error;
        }
        lastError = error;
        if (attempt >= this.maxRetries) {
          throw error;
        }
      }
    }

    throw lastError;
  }

  get<T>(path: string, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("GET", path, { query });
  }

  post<T>(path: string, body?: unknown, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("POST", path, { body, query });
  }

  patch<T>(path: string, body?: unknown, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("PATCH", path, { body, query });
  }

  delete<T>(path: string, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("DELETE", path, { query });
  }
}
