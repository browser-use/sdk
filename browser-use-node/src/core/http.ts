import { BrowserUseError } from "./errors.js";
import type { FetchLike } from "./x402.js";

const MAX_RETRY_DELAY = 10_000;

/** Honor Cloud's integer-second Retry-After; other formats use normal backoff. */
function retryDelay(response: Response, attempt: number): number | undefined {
  const value = response.headers.get("Retry-After")?.trim();
  const retryAfter = value && /^\d+$/.test(value) ? Number(value) * 1000 : undefined;
  // Timeout remains per attempt; preserve the existing ten-second delay cap.
  if (retryAfter !== undefined && retryAfter > MAX_RETRY_DELAY) return undefined;

  const backoff = Math.min(1000 * 2 ** attempt, MAX_RETRY_DELAY);
  return Math.min(Math.max(backoff, retryAfter ?? 0) + Math.random() * 250, MAX_RETRY_DELAY);
}

async function sleep(delay: number, signal?: AbortSignal): Promise<void> {
  signal?.throwIfAborted();
  await new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      signal?.removeEventListener("abort", abort);
      resolve();
    }, delay);
    const abort = () => {
      clearTimeout(timer);
      reject(signal?.reason);
    };
    signal?.addEventListener("abort", abort, { once: true });
  });
}

export interface HttpClientOptions {
  apiKey: string;
  baseUrl: string;
  maxRetries?: number;
  timeout?: number;
  /**
   * Optional custom fetch implementation. May be a sync value or a Promise
   * (for lazy resolution of e.g. x402-wrapped fetch). When set, replaces
   * `globalThis.fetch`. The `X-Browser-Use-API-Key` header is still sent if
   * `apiKey` is non-empty (top-up mode in x402); pass `apiKey: ""` to omit.
   */
  fetch?: FetchLike | Promise<FetchLike>;
}

export class HttpClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly maxRetries: number;
  private readonly timeout: number;
  private readonly fetchPromise: Promise<FetchLike>;
  private readonly useApiKeyHeader: boolean;

  constructor(options: HttpClientOptions) {
    this.apiKey = options.apiKey;
    // Strip trailing slashes without a regex — CodeQL flags /\/+$/ as a
    // polynomial ReDoS even though baseUrl is developer config, not runtime
    // input. Linear and provably safe.
    let base = options.baseUrl;
    while (base.endsWith("/")) base = base.slice(0, -1);
    this.baseUrl = base;
    this.maxRetries = options.maxRetries ?? 3;
    this.timeout = options.timeout ?? 30_000;
    this.fetchPromise = Promise.resolve(
      options.fetch ?? ((input, init) => fetch(input, init)),
    );
    // Send the API key header whenever apiKey is non-empty. In x402 mode
    // an empty apiKey means "accountless" (wallet is identity); a non-empty
    // apiKey means "top up the existing key's project".
    this.useApiKeyHeader = options.apiKey !== "";
  }

  async request<T>(
    method: string,
    path: string,
    options?: {
      body?: unknown;
      query?: Record<string, unknown>;
      headers?: Record<string, string>;
      signal?: AbortSignal;
    },
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    if (options?.query) {
      for (const [key, value] of Object.entries(options.query)) {
        if (Array.isArray(value)) {
          for (const item of value) {
            if (item !== undefined && item !== null) {
              url.searchParams.append(key, String(item));
            }
          }
        } else if (value !== undefined && value !== null) {
          url.searchParams.set(key, String(value));
        }
      }
    }

    const headers: Record<string, string> = { ...options?.headers };
    if (this.useApiKeyHeader) {
      headers["X-Browser-Use-API-Key"] = this.apiKey;
    }
    if (options?.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      options?.signal?.throwIfAborted();

      const controller = new AbortController();
      const timeoutId = options?.signal
        ? undefined
        : setTimeout(() => controller.abort(), this.timeout);

      // Combine user signal with internal timeout when both are present
      const signal = options?.signal ?? controller.signal;

      try {
        const fetchImpl = await this.fetchPromise;
        const response = await fetchImpl(url.toString(), {
          method,
          headers,
          body: options?.body !== undefined ? JSON.stringify(options.body) : undefined,
          signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          if (response.status === 204) {
            return undefined as T;
          }
          return (await response.json()) as T;
        }

        // GETs are safe to replay after a temporary upstream failure. Writes
        // retain only the existing 429 retry: a 5xx may follow a successful write.
        const shouldRetry =
          (response.status === 429 ||
            (method.toUpperCase() === "GET" && [502, 503, 504].includes(response.status))) &&
          attempt < this.maxRetries;
        const delay = shouldRetry ? retryDelay(response, attempt) : undefined;

        if (delay !== undefined) {
          // Release the failed response before waiting or opening another request.
          await response.body?.cancel().catch(() => {});
          await sleep(delay, options?.signal);
          continue;
        }

        let errorBody: unknown;
        try {
          errorBody = await response.json();
        } catch {
          /* ignore parse errors */
        }
        const raw =
          typeof errorBody === "object" && errorBody !== null
            ? "message" in errorBody
              ? (errorBody as Record<string, unknown>).message
              : "detail" in errorBody
                ? (errorBody as Record<string, unknown>).detail
                : undefined
            : undefined;
        const message =
          raw === undefined
            ? `HTTP ${response.status}`
            : typeof raw === "string"
              ? raw
              : JSON.stringify(raw);
        throw new BrowserUseError(response.status, message, errorBody);
      } catch (error) {
        clearTimeout(timeoutId);
        throw error;
      }
    }

    throw new Error("Unreachable: retry loop exhausted");
  }

  get<T>(path: string, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("GET", path, { query });
  }

  post<T>(
    path: string,
    body?: unknown,
    query?: Record<string, unknown>,
    headers?: Record<string, string>,
  ): Promise<T> {
    return this.request<T>("POST", path, { body, query, headers });
  }

  patch<T>(path: string, body?: unknown, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("PATCH", path, { body, query });
  }

  delete<T>(path: string, query?: Record<string, unknown>): Promise<T> {
    return this.request<T>("DELETE", path, { query });
  }
}
