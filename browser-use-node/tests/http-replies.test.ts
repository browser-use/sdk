import { afterEach, describe, expect, it, vi } from "vitest";

import { APIKeySpendLimitError, BrowserUseError } from "../src/v4.js";
import { HttpClient } from "../src/core/http.js";
import type { FetchLike } from "../src/core/x402.js";
import { Runs } from "../src/v4/resources/runs.js";
import { Sessions } from "../src/v4/resources/sessions.js";

const RUN_ID = "00000000-0000-0000-0000-000000000001";

function client(fetch: FetchLike) {
  return new HttpClient({ apiKey: "test", baseUrl: "https://api.example.com", fetch });
}

afterEach(() => {
  vi.useRealTimers();
});

describe("HttpClient replies", () => {
  it("resolves a 202 purge with an empty body to undefined", async () => {
    const http = client(async () => new Response(null, { status: 202, headers: { "Retry-After": "60" } }));

    await expect(new Sessions(http).purge("session-id")).resolves.toBeUndefined();
  });

  it("throws a typed error for the 402 API key spend limit", async () => {
    const detail = {
      code: "api_key_monthly_spend_limit_reached",
      message: "Monthly spend limit of $5.00 reached",
      cap: 5,
      spent: 5.01,
    };
    const http = client(async () => new Response(JSON.stringify({ detail }), { status: 402 }));

    const error = await http.post("/runs", { task: "x" }).catch((e: unknown) => e);

    expect(error).toBeInstanceOf(APIKeySpendLimitError);
    expect(error).toMatchObject({ statusCode: 402, message: detail.message, code: detail.code, cap: 5, spent: 5.01 });
  });

  it("retries a busy 503 cancel after Retry-After", async () => {
    vi.useFakeTimers();
    const fetch = vi.fn<FetchLike>()
      .mockResolvedValueOnce(new Response('{"detail":"busy"}', { status: 503, headers: { "Retry-After": "2" } }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: RUN_ID, status: "cancelled" })));

    const pending = new Runs(client(fetch)).cancel(RUN_ID);
    await vi.advanceTimersByTimeAsync(1_999);
    expect(fetch).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(1);

    expect((await pending).status).toBe("cancelled");
    expect(fetch).toHaveBeenLastCalledWith(
      `https://api.example.com/runs/${RUN_ID}/cancel`,
      expect.objectContaining({ method: "POST" }),
    );
  });
});

describe("v4 runs.waitForCompletion visibility grace", () => {
  it("retries an initial 404 until the new run's status is visible", async () => {
    const status = vi.fn()
      .mockRejectedValueOnce(new BrowserUseError(404, "Run not found"))
      .mockResolvedValueOnce({ status: "running" })
      .mockResolvedValueOnce({ status: "completed" });
    const http = {
      get: vi.fn(async (path: string) => (path.endsWith("/status") ? status() : { id: RUN_ID, status: "completed" })),
    };

    const run = await new Runs(http as any).waitForCompletion(RUN_ID, { interval: 1 });

    expect(run.status).toBe("completed");
    expect(status).toHaveBeenCalledTimes(3);
  });
});
