import { afterEach, describe, expect, it, vi } from "vitest";

import { BrowserUseError } from "../src/core/errors.js";
import { BrowserUse as V2 } from "../src/v2/client.js";
import { BrowserUse as V3 } from "../src/v3/client.js";

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("v2/v3 run()", () => {
  it.each([
    ["v2", () => new V2({ apiKey: "test", baseUrl: "https://api.example.com" })],
    ["v3", () => new V3({ apiKey: "test", baseUrl: "https://api.example.com" })],
  ])("%s surfaces a failed eager create at await without an unhandled rejection", async (_, make) => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ detail: "Insufficient credits" }, 402)));
    const unhandled = vi.fn();
    process.on("unhandledRejection", unhandled);
    try {
      const run = make().run("Find pricing");
      await new Promise((resolve) => setTimeout(resolve, 20));
      expect(unhandled).not.toHaveBeenCalled();
      await expect(run).rejects.toMatchObject({ statusCode: 402 });
      await expect(run).rejects.toBeInstanceOf(BrowserUseError);
    } finally {
      process.off("unhandledRejection", unhandled);
    }
  });
});

describe("v2 tasks.wait", () => {
  it("treats failed as terminal", async () => {
    const fetch = vi.fn(async (input: string) =>
      json(new URL(input).pathname.endsWith("/status") ? { status: "failed" } : { id: "t", status: "failed" }),
    );
    vi.stubGlobal("fetch", fetch);
    const client = new V2({ apiKey: "test", baseUrl: "https://api.example.com" });
    expect(await client.tasks.wait("t", { timeout: 1_000, interval: 10_000 })).toMatchObject({ status: "failed" });
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});

describe("v3 profiles.list", () => {
  it("sends pageNumber/pageSize and maps the deprecated page/page_size aliases", async () => {
    const urls: URL[] = [];
    vi.stubGlobal("fetch", vi.fn(async (input: string) => {
      urls.push(new URL(input));
      return json({ items: [], totalItems: 0, pageNumber: 2, pageSize: 2 });
    }));
    const client = new V3({ apiKey: "test", baseUrl: "https://api.example.com" });
    await client.profiles.list({ pageNumber: 2, pageSize: 2 });
    await client.profiles.list({ page: 2, page_size: 2 });
    for (const url of urls) {
      expect(Object.fromEntries(url.searchParams)).toEqual({ pageNumber: "2", pageSize: "2" });
    }
  });
});
