import { expect, it } from "vitest";

import { HttpClient } from "../src/core/http.js";
import { Integrations } from "../src/v4/resources/integrations.js";
import { Profiles } from "../src/v4/resources/profiles.js";
import { Sessions } from "../src/v4/resources/sessions.js";

const SESSION_ID = "00000000-0000-0000-0000-000000000002";

// Request shaping the wire depends on: query renames, a null body field and the PUT verb.
// Plain path passthroughs are covered by vibe.test.ts's endpoint map.
it.each([
  {
    name: "integrations.list renames query params",
    call: (http: HttpClient) =>
      new Integrations(http).list({ limit: 5, search: "gmail", connectedOnly: true }),
    method: "GET",
    url: "/integrations?limit=5&search=gmail&connected_only=true",
    body: undefined,
  },
  {
    name: "sessions.update sends a null title to clear it",
    call: (http: HttpClient) => new Sessions(http).update(SESSION_ID, { title: null }),
    method: "PATCH",
    url: `/sessions/${SESSION_ID}`,
    body: '{"title":null}',
  },
  {
    name: "profiles.list passes camelCase query params",
    call: (http: HttpClient) => new Profiles(http).list({ pageSize: 5, pageNumber: 2 }),
    method: "GET",
    url: "/profiles?pageSize=5&pageNumber=2",
    body: undefined,
  },
  {
    name: "sessions.updateCostCap patches the cost-cap path",
    call: (http: HttpClient) => new Sessions(http).updateCostCap(SESSION_ID, { maxCostUsd: "2.50" }),
    method: "PATCH",
    url: `/sessions/${SESSION_ID}/cost-cap`,
    body: '{"maxCostUsd":"2.50"}',
  },
  {
    name: "sessions.updateShare uses PUT",
    call: (http: HttpClient) => new Sessions(http).updateShare(SESSION_ID, { isActive: false }),
    method: "PUT",
    url: `/sessions/${SESSION_ID}/share`,
    body: '{"isActive":false}',
  },
])("v4 request shaping: $name", async ({ call, method, url, body }) => {
  const seen: { method?: string; url?: string; body?: unknown } = {};
  const http = new HttpClient({
    apiKey: "test",
    baseUrl: "https://api.example.com",
    fetch: async (input, init) => {
      seen.method = init?.method;
      seen.url = String(input);
      seen.body = init?.body;
      return new Response("{}", { status: 200, headers: { "Content-Type": "application/json" } });
    },
  });

  await call(http);

  expect(seen).toEqual({ method, url: `https://api.example.com${url}`, body });
});
