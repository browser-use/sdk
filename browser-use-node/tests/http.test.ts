import { describe, expect, it } from "vitest";

import { HttpClient } from "../src/core/http.js";

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
