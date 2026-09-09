import { describe, expect, it, vi } from "vitest";

import { Sessions } from "../src/v3/resources/sessions.js";

describe("v3 BYOK settings", () => {
  it("adds useOwnKey when configured on the sessions resource", async () => {
    const post = vi.fn(async (_path: string, body: unknown) => body);
    const sessions = new Sessions({ post } as any, { useOwnKey: true });

    await sessions.create({ task: "Find pricing" });

    expect(post).toHaveBeenCalledWith("/sessions", {
      task: "Find pricing",
      useOwnKey: true,
    });
  });

  it("lets per-request useOwnKey override the default", async () => {
    const post = vi.fn(async (_path: string, body: unknown) => body);
    const sessions = new Sessions({ post } as any, { useOwnKey: true });

    await sessions.create({ task: "Find pricing", useOwnKey: false });

    expect(post).toHaveBeenCalledWith("/sessions", {
      task: "Find pricing",
      useOwnKey: false,
    });
  });
});
