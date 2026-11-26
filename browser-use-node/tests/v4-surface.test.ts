import { expect, it } from "vitest";

import { HttpClient } from "../src/core/http.js";
import { Browsers, Integrations, NetworkPolicies, Profiles, Runs, Sessions } from "../src/v4.js";

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
  {
    name: "networkPolicies.create uses the server default and forwards extra fields",
    call: (http: HttpClient) => new NetworkPolicies(http).create({ name: "Block ads", future: true }),
    method: "POST",
    url: "/network-policies",
    body: '{"name":"Block ads","future":true}',
  },
  {
    name: "networkPolicies.list passes page params",
    call: (http: HttpClient) => new NetworkPolicies(http).list({ pageSize: 5, pageNumber: 2 }),
    method: "GET",
    url: "/network-policies?pageSize=5&pageNumber=2",
    body: undefined,
  },
  {
    name: "networkPolicies.get reads the policy",
    call: (http: HttpClient) => new NetworkPolicies(http).get(SESSION_ID),
    method: "GET",
    url: `/network-policies/${SESSION_ID}`,
    body: undefined,
  },
  {
    name: "networkPolicies.update replaces the blocked domains",
    call: (http: HttpClient) => new NetworkPolicies(http).update(SESSION_ID, {
      block: { domains: [] },
      future: true,
    }),
    method: "PATCH",
    url: `/network-policies/${SESSION_ID}`,
    body: '{"block":{"domains":[]},"future":true}',
  },
  {
    name: "networkPolicies.delete deletes the policy",
    call: (http: HttpClient) => new NetworkPolicies(http).delete(SESSION_ID),
    method: "DELETE",
    url: `/network-policies/${SESSION_ID}`,
    body: undefined,
  },
  {
    name: "browsers.getProxy reads proxy settings",
    call: (http: HttpClient) => new Browsers(http).getProxy(SESSION_ID),
    method: "GET",
    url: `/browsers/${SESSION_ID}/proxy`,
    body: undefined,
  },
  {
    name: "browsers.updateProxy forwards custom proxy settings and extra fields",
    call: (http: HttpClient) => new Browsers(http).updateProxy(SESSION_ID, {
      mode: "custom",
      customProxy: { host: "proxy.example.com", port: 443, protocol: "https", caBundle: "pem" },
      future: true,
    }),
    method: "PATCH",
    url: `/browsers/${SESSION_ID}/proxy`,
    body: '{"mode":"custom","customProxy":{"host":"proxy.example.com","port":443,"protocol":"https","caBundle":"pem"},"future":true}',
  },
  {
    name: "sessions.compact posts without a body",
    call: (http: HttpClient) => new Sessions(http).compact(SESSION_ID),
    method: "POST",
    url: `/sessions/${SESSION_ID}/compact`,
    body: undefined,
  },
  {
    name: "sessions.sendMessage can confirm without sending text or interrupt",
    call: (http: HttpClient) => new Sessions(http).sendMessage(SESSION_ID, { confirmInputId: 7 }),
    method: "POST",
    url: `/sessions/${SESSION_ID}/queue`,
    body: '{"confirmInputId":7}',
  },
  {
    name: "runs.list repeats metadata query terms",
    call: (http: HttpClient) => new Runs(http).list({ metadata: ["flow", "source=api"] }),
    method: "GET",
    url: "/runs?metadata=flow&metadata=source%3Dapi",
    body: undefined,
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
