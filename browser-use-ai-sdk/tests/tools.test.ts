import { describe, expect, it, vi } from "vitest";
import type { BrowserUse } from "browser-use-sdk/v4";
import { createBrowserUseTools } from "../src/index";

function fakeClient() {
  const create = vi.fn(async () => ({ id: "run_1", sessionId: "ses_1" }));
  const waitForCompletion = vi.fn(async () => ({
    status: "completed",
    result: "Top story: Example",
    error: null,
    sessionId: "ses_1",
    totalCostUsd: "0.012",
  }));
  return { client: { runs: { create, waitForCompletion } } as unknown as BrowserUse, create, waitForCompletion };
}

const ctx = { toolCallId: "t1", messages: [] };

describe("createBrowserUseTools", () => {
  it("creates a run, waits for it, and returns the result", async () => {
    const f = fakeClient();
    const { tools } = createBrowserUseTools({ client: f.client, model: "bu-ultrafast", timeoutMs: 1000 });
    const out = await tools.browserUseTask.execute!({ task: "Find the top HN story" }, ctx);
    expect(f.create).toHaveBeenCalledWith({ task: "Find the top HN story", model: "bu-ultrafast" });
    expect(f.waitForCompletion).toHaveBeenCalledWith("run_1", { timeout: 1000 });
    expect(out).toEqual({
      status: "completed",
      result: "Top story: Example",
      error: null,
      sessionId: "ses_1",
      costUsd: "0.012",
    });
  });

  it("continues an existing session and omits model when unset", async () => {
    const f = fakeClient();
    const { tools } = createBrowserUseTools({ client: f.client });
    await tools.browserUseTask.execute!({ task: "Now open the second story", sessionId: "ses_1" }, ctx);
    expect(f.create).toHaveBeenCalledWith({ task: "Now open the second story", sessionId: "ses_1" });
  });

  it("rejects an empty task in the input schema", () => {
    const { tools } = createBrowserUseTools({ client: fakeClient().client });
    const schema = tools.browserUseTask.inputSchema as { safeParse: (v: unknown) => { success: boolean } };
    expect(schema.safeParse({ task: "" }).success).toBe(false);
    expect(schema.safeParse({ task: "x" }).success).toBe(true);
  });
});
