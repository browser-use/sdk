import { describe, expect, it, vi } from "vitest";

import { BrowserUse } from "../src/v4.js";
import { Integrations } from "../src/v4/resources/integrations.js";
import { Runs } from "../src/v4/resources/runs.js";
import { Sessions } from "../src/v4/resources/sessions.js";
import { Wallets } from "../src/v4/resources/wallets.js";

const SESSION_ID = "00000000-0000-0000-0000-000000000002";
const WALLET_ID = "00000000-0000-0000-0000-000000000020";
const LINK_ID = "00000000-0000-0000-0000-000000000021";

const share = {
  id: "00000000-0000-0000-0000-000000000030",
  shareToken: "tok",
  sessionId: SESSION_ID,
  isActive: true,
  viewCount: 0,
  createdAt: "2026-01-01T00:00:00Z",
  shareUrl: "https://cloud.browser-use.com/share/v4/tok",
};

describe("v4 client", () => {
  it("exposes integrations and wallets", () => {
    const client = new BrowserUse({ apiKey: "bu_test" });
    expect(client.integrations).toBeInstanceOf(Integrations);
    expect(client.wallets).toBeInstanceOf(Wallets);
  });
});

describe("v4 runs.create", () => {
  it("sends bu-ultrafast and the payment and vault fields unchanged", async () => {
    const http = { post: vi.fn(async () => ({})) };
    const runs = new Runs(http as any);

    await runs.create({
      task: "Buy the cheapest one",
      model: "bu-ultrafast",
      agentcardWalletId: WALLET_ID,
      stripeLinkConnectionId: LINK_ID,
      opVaultId: "vault",
      opVaultAllowedDomains: ["amazon.com"],
    });

    expect(http.post).toHaveBeenCalledWith("/runs", {
      task: "Buy the cheapest one",
      model: "bu-ultrafast",
      agentcardWalletId: WALLET_ID,
      stripeLinkConnectionId: LINK_ID,
      opVaultId: "vault",
      opVaultAllowedDomains: ["amazon.com"],
    });
  });
});

describe("v4 sessions", () => {
  it("renames, deletes and reads cost", async () => {
    const http = {
      patch: vi.fn(async () => ({ sessionId: SESSION_ID, title: null })),
      delete: vi.fn(async () => undefined),
      get: vi.fn(async () => ({ sessionId: SESSION_ID, totalCostUsd: "0.10" })),
    };
    const sessions = new Sessions(http as any);

    await sessions.update(SESSION_ID, { title: null });
    await sessions.delete(SESSION_ID);
    const cost = await sessions.cost(SESSION_ID);

    expect(http.patch).toHaveBeenCalledWith(`/sessions/${SESSION_ID}`, { title: null });
    expect(http.delete).toHaveBeenCalledWith(`/sessions/${SESSION_ID}`);
    expect(http.get).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/cost`);
    expect(cost.totalCostUsd).toBe("0.10");
  });

  it("gets, creates and toggles the share link", async () => {
    const http = {
      get: vi.fn(async () => null),
      post: vi.fn(async () => share),
      put: vi.fn(async () => ({ ...share, isActive: false })),
    };
    const sessions = new Sessions(http as any);

    expect(await sessions.getShare(SESSION_ID)).toBeNull();
    expect((await sessions.createShare(SESSION_ID)).shareUrl).toBe(share.shareUrl);
    expect((await sessions.updateShare(SESSION_ID, { isActive: false })).isActive).toBe(false);

    expect(http.get).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/share`);
    expect(http.post).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/share`);
    expect(http.put).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/share`, { isActive: false });
  });
});

describe("v4 integrations", () => {
  it("maps list params to the API's query names", async () => {
    const http = { get: vi.fn(async () => ({ integrations: [], total: 0, limit: 5, offset: 0 })) };
    const integrations = new Integrations(http as any);

    await integrations.list({ limit: 5, search: "gmail", connectedOnly: true });

    expect(http.get).toHaveBeenCalledWith("/integrations", {
      limit: 5,
      offset: undefined,
      search: "gmail",
      popular_only: undefined,
      connected_only: true,
    });
  });

  it("authorizes, polls and disconnects a provider", async () => {
    const http = {
      get: vi.fn(async (path: string) =>
        path.endsWith("/status") ? { provider: "gmail", is_connected: true } : { categories: ["email"] },
      ),
      post: vi.fn(async () => ({ redirect_url: "https://composio.example/auth", provider: "gmail" })),
      delete: vi.fn(async () => ({ success: true, provider: "gmail" })),
    };
    const integrations = new Integrations(http as any);

    expect((await integrations.categories()).categories).toEqual(["email"]);
    expect((await integrations.authorize("gmail")).redirect_url).toContain("composio");
    expect((await integrations.status("gmail")).is_connected).toBe(true);
    expect((await integrations.disconnect("gmail")).success).toBe(true);

    expect(http.get).toHaveBeenCalledWith("/integrations/categories");
    expect(http.post).toHaveBeenCalledWith("/integrations/gmail/authorize");
    expect(http.get).toHaveBeenCalledWith("/integrations/gmail/status");
    expect(http.delete).toHaveBeenCalledWith("/integrations/gmail");
  });
});

describe("v4 wallets", () => {
  it("lists AgentCard wallets and reads the Stripe Link connection", async () => {
    const http = {
      get: vi.fn(async (path: string) =>
        path === "/stripe-link" ? { isConnected: true, connectionId: LINK_ID } : { wallets: [] },
      ),
    };
    const wallets = new Wallets(http as any);

    expect((await wallets.agentcard()).wallets).toEqual([]);
    expect((await wallets.stripeLink()).connectionId).toBe(LINK_ID);
    expect(http.get).toHaveBeenCalledWith("/agentcard/wallets");
    expect(http.get).toHaveBeenCalledWith("/stripe-link");
  });
});
