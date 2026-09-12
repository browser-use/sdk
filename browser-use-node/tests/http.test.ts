import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { HttpClient } from "../src/core/http.js";
import type { FetchLike } from "../src/core/x402.js";
import { BrowserUse } from "../src/v4/client.js";

describe("HttpClient query serialization", () => {
  it("repeats array query parameters", async () => {
    let requestedUrl = "";
    const http = new HttpClient({
      apiKey: "test",
      baseUrl: "https://api.example.com",
      fetch: async (input) => {
        requestedUrl = String(input);
        return new Response("{}", {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      },
    });

    await http.get("/browsers", {
      metadata: ["team", "env=prod"],
      pageSize: 10,
    });

    const url = new URL(requestedUrl);
    expect(url.searchParams.getAll("metadata")).toEqual(["team", "env=prod"]);
    expect(url.searchParams.get("pageSize")).toBe("10");
  });

  it("forwards per-request headers alongside authentication", async () => {
    let requestedHeaders = new Headers();
    const http = new HttpClient({
      apiKey: "test",
      baseUrl: "https://api.example.com",
      fetch: async (_input, init) => {
        requestedHeaders = new Headers(init?.headers);
        return new Response("{}", {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      },
    });

    await http.post(
      "/sessions/id/queue",
      { text: "hello" },
      undefined,
      { "X-V4-Queue-Deduplicate": "exact-text-v1" },
    );

    expect(requestedHeaders.get("X-V4-Queue-Deduplicate")).toBe("exact-text-v1");
    expect(requestedHeaders.get("X-Browser-Use-API-Key")).toBe("test");
  });
});

function response(status: number, retryAfter?: string): Response {
  return new Response(JSON.stringify({ detail: "temporary failure" }), {
    status,
    headers: retryAfter === undefined ? {} : { "Retry-After": retryAfter },
  });
}

describe("HttpClient retries", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.spyOn(Math, "random").mockReturnValue(0);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  function client(fetch: FetchLike, maxRetries?: number) {
    return new HttpClient({ apiKey: "test", baseUrl: "https://api.example.com", fetch, maxRetries });
  }

  it.each([502, 503, 504])("recovers a transient GET %i", async (status) => {
    const failed = response(status);
    const cancel = vi.spyOn(failed.body!, "cancel");
    const fetch = vi.fn<FetchLike>()
      .mockResolvedValueOnce(failed)
      .mockResolvedValueOnce(new Response('{"status":"completed"}'));
    const pending = client(fetch).get("/runs/id/status");
    await vi.advanceTimersByTimeAsync(999);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(cancel).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    expect(await pending).toEqual({ status: "completed" });
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("lets the public completion helper survive temporary status and result failures", async () => {
    const paths: string[] = [];
    const responses = [
      response(503, "2"),
      new Response('{"status":"completed"}'),
      response(502),
      new Response('{"id":"run-id","status":"completed","result":"done"}'),
    ];
    vi.stubGlobal("fetch", vi.fn(async (input: string) => {
      paths.push(new URL(input).pathname);
      return responses.shift()!;
    }));
    const sdk = new BrowserUse({ apiKey: "test", baseUrl: "https://api.example.com" });
    const pending = sdk.runs.waitForCompletion("run-id");
    await vi.advanceTimersByTimeAsync(3_000);
    expect((await pending).result).toBe("done");
    expect(paths).toEqual([
      "/runs/run-id/status", "/runs/run-id/status", "/runs/run-id", "/runs/run-id",
    ]);
  });

  it("honors Retry-After through public browser creation", async () => {
    const fetch = vi.fn<FetchLike>()
      .mockResolvedValueOnce(response(429, "5"))
      .mockResolvedValueOnce(new Response('{"id":"browser-id","status":"active"}'));
    vi.stubGlobal("fetch", fetch);
    const sdk = new BrowserUse({ apiKey: "test", baseUrl: "https://api.example.com" });
    const pending = sdk.browsers.create();
    await vi.advanceTimersByTimeAsync(4_999);
    expect(fetch).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    expect((await pending).id).toBe("browser-id");
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(fetch).toHaveBeenLastCalledWith("https://api.example.com/browsers", expect.objectContaining({ method: "POST" }));
  });

  it.each([429, 503])("bounds persistent %i to four total attempts by default", async (status) => {
    const fetch = vi.fn<FetchLike>().mockImplementation(async () => response(status));
    const pending = client(fetch).get("/runs/id/status");
    const rejected = expect(pending).rejects.toMatchObject({ statusCode: status, message: "temporary failure" });
    await vi.advanceTimersByTimeAsync(7_000);
    await rejected;
    expect(fetch).toHaveBeenCalledTimes(4);
    expect(vi.getTimerCount()).toBe(0);
  });

  it.each([429, 503])("disables retries for %i when maxRetries is zero", async (status) => {
    const fetch = vi.fn<FetchLike>().mockImplementation(async () => response(status));
    await expect(client(fetch, 0).get("/runs/id/status")).rejects.toMatchObject({ statusCode: status });
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(vi.getTimerCount()).toBe(0);
  });

  it.each([
    ["5", 5_000],
    [" 5 ", 5_000],
    ["10", 10_000],
    ["0", 1_000],
    ["", 1_000],
    ["garbage", 1_000],
    ["-1", 1_000],
    ["1.5", 1_000],
    ["Fri, 11 Sep 2026 00:00:05 GMT", 1_000],
  ])("uses numeric Retry-After %s or falls back to normal backoff", async (header, delay) => {
    const fetch = vi.fn<FetchLike>()
      .mockResolvedValueOnce(response(429, header as string))
      .mockResolvedValueOnce(new Response("{}"));
    const pending = client(fetch).post("/browsers", {});
    await vi.advanceTimersByTimeAsync((delay as number) - 1);
    expect(fetch).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1);
    await pending;
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it.each(["11", "60", "9".repeat(400)])(
    "surfaces Retry-After %s immediately when the wait exceeds the bound", async (header) => {
      const fetch = vi.fn<FetchLike>().mockImplementation(async () => response(429, header));
      await expect(client(fetch).post("/browsers", {})).rejects.toMatchObject({ statusCode: 429 });
      expect(fetch).toHaveBeenCalledOnce();
      expect(vi.getTimerCount()).toBe(0);
    },
  );

  it("adds positive jitter to the server delay", async () => {
    vi.mocked(Math.random).mockReturnValue(0.5);
    const fetch = vi.fn<FetchLike>()
      .mockResolvedValueOnce(response(429, "5"))
      .mockResolvedValueOnce(new Response("{}"));
    const pending = client(fetch).post("/browsers", {});
    await vi.advanceTimersByTimeAsync(5_124);
    expect(fetch).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    await pending;
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it.each([undefined, "0", "1"])("caps exponential backoff with Retry-After %s including jitter at ten seconds", async (header) => {
    vi.mocked(Math.random).mockReturnValue(0.5);
    const times: number[] = [];
    const start = Date.now();
    const fetch = vi.fn<FetchLike>().mockImplementation(async () => {
      times.push(Date.now() - start);
      return response(429, header);
    });
    const rejected = expect(client(fetch, 5).get("/browsers")).rejects.toMatchObject({ statusCode: 429 });
    await vi.runAllTimersAsync();
    await rejected;
    expect(times).toEqual([0, 1_125, 3_250, 7_375, 15_500, 25_500]);
  });

  it.each(["POST", "PATCH", "DELETE"])("never retries ambiguous %s 5xx", async (method) => {
    for (const status of [500, 502, 503, 504]) {
      const fetch = vi.fn<FetchLike>().mockImplementation(async () => response(status, "2"));
      await expect(client(fetch).request(method, "/browsers")).rejects.toMatchObject({ statusCode: status });
      expect(fetch).toHaveBeenCalledOnce();
    }
  });

  it.each([400, 401, 403, 404, 409, 500, 501, 505])("does not retry GET %i", async (status) => {
    const fetch = vi.fn<FetchLike>().mockImplementation(async () => response(status));
    await expect(client(fetch).get("/browsers")).rejects.toMatchObject({ statusCode: status });
    expect(fetch).toHaveBeenCalledOnce();
  });

  it.each(["GET", "POST"])("does not retry %s transport failures", async (method) => {
    const failure = new TypeError("fetch failed");
    const fetch = vi.fn<FetchLike>().mockRejectedValue(failure);
    await expect(client(fetch).request(method, "/browsers")).rejects.toBe(failure);
    expect(fetch).toHaveBeenCalledOnce();
  });

  it("aborts during backoff without sending another request or leaving a timer", async () => {
    const controller = new AbortController();
    const fetch = vi.fn<FetchLike>().mockImplementation(async () => response(503, "10"));
    const pending = client(fetch).request("GET", "/browsers", { signal: controller.signal });
    const rejected = expect(pending).rejects.toMatchObject({ name: "AbortError" });
    await vi.advanceTimersByTimeAsync(100);
    controller.abort();
    await rejected;
    await vi.advanceTimersByTimeAsync(10_000);
    expect(fetch).toHaveBeenCalledOnce();
    expect(vi.getTimerCount()).toBe(0);
  });

  it("does not send a request when its signal is already aborted", async () => {
    const fetch = vi.fn<FetchLike>();
    await expect(client(fetch).request("GET", "/browsers", { signal: AbortSignal.abort() }))
      .rejects.toMatchObject({ name: "AbortError" });
    expect(fetch).not.toHaveBeenCalled();
  });
});
