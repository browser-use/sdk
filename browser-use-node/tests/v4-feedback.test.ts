import { afterEach, expect, it, vi } from "vitest";

import { BrowserUseError } from "../src/core/errors.js";
import { BrowserUse } from "../src/v4/client.js";

// POST /feedback is not in the OpenAPI spec, so vibe.test.ts's endpoint map cannot cover it.
afterEach(() => vi.unstubAllGlobals());

function stubFetch(response: () => Response) {
  const fetch = vi.fn(async (_input: string, _init?: RequestInit) => response());
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

it("feedback posts the message with the API key and returns on 204", async () => {
  const fetch = stubFetch(() => new Response(null, { status: 204 }));
  const client = new BrowserUse({ apiKey: "bu_test", baseUrl: "https://api.example.com/api/v4" });

  await expect(client.feedback("kind: bug\nruns.create 500s", { source: "ci" })).resolves.toBeUndefined();

  expect(fetch).toHaveBeenCalledOnce();
  const [url, init] = fetch.mock.calls[0]!;
  expect([init?.method, url]).toEqual(["POST", "https://api.example.com/api/v4/feedback"]);
  expect((init?.headers as Record<string, string>)["X-Browser-Use-API-Key"]).toBe("bu_test");
  expect(JSON.parse(init?.body as string)).toEqual({ message: "kind: bug\nruns.create 500s", source: "ci" });
});

it("feedback throws BrowserUseError when the server rejects it", async () => {
  stubFetch(() => Response.json({ detail: "message must be 1 to 5000 characters" }, { status: 422 }));
  const client = new BrowserUse({ apiKey: "bu_test" });

  const error = await client.feedback("").catch((e: unknown) => e);

  expect(error).toBeInstanceOf(BrowserUseError);
  expect(error).toMatchObject({ statusCode: 422, message: "message must be 1 to 5000 characters" });
});
