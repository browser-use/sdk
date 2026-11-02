import { generateText, isStepCount } from "ai";
import { MockLanguageModelV4 } from "ai/test";
import { describe, expect, it, vi } from "vitest";

import { browserUse } from "../src/ai-sdk.js";
import type { BrowserUse } from "../src/v4/client.js";

const RUN_ID = "00000000-0000-0000-0000-000000000001";
const SESSION_ID = "00000000-0000-0000-0000-000000000002";

const usage = {
  inputTokens: { total: 1, noCache: 1, cacheRead: 0, cacheWrite: 0 },
  outputTokens: { total: 1, text: 1, reasoning: 0 },
};

function fakeClient(status: () => Promise<{ status: string }>) {
  const runs = {
    create: vi.fn(async (_body: Record<string, unknown>) => ({ id: RUN_ID, sessionId: SESSION_ID })),
    cancel: vi.fn(async (_runId: string) => ({})),
    waitForCompletion: vi.fn(async (runId: string, _options?: unknown) => {
      const { status: s } = await status();
      return {
        id: runId,
        sessionId: SESSION_ID,
        status: s,
        result: s === "completed" ? "Top story: Show HN" : null,
        output: s === "completed" ? { rank: 0, isShowHN: false } : null,
        error: s === "failed" ? "Site blocked" : null,
      };
    }),
  };
  return { client: { runs } as unknown as BrowserUse, runs };
}

describe("ai-sdk browserUse tool", () => {
  it("runs inside generateText and feeds the run result back to the model", async () => {
    const { client, runs } = fakeClient(async () => ({ status: "completed" }));
    let call = 0;
    const model = new MockLanguageModelV4({
      doGenerate: async () => {
        call += 1;
        if (call === 1) {
          return {
            content: [
              {
                type: "tool-call",
                toolCallId: "call-1",
                toolName: "browserUse",
                input: JSON.stringify({ task: "Find the top Hacker News story" }),
              },
            ],
            finishReason: { unified: "tool-calls", raw: "tool_calls" },
            usage,
            warnings: [],
          };
        }
        return {
          content: [{ type: "text", text: "The top story is Show HN." }],
          finishReason: { unified: "stop", raw: "stop" },
          usage,
          warnings: [],
        };
      },
    });

    const result = await generateText({
      model,
      tools: { browserUse: browserUse({ client, runOptions: { maxCostUsd: 1 } }) },
      stopWhen: isStepCount(3),
      prompt: "What is the top story on Hacker News?",
    });

    expect(runs.create).toHaveBeenCalledWith({
      maxCostUsd: 1,
      task: "Find the top Hacker News story",
    });
    expect(result.steps[0].toolResults[0].output).toEqual({
      runId: RUN_ID,
      sessionId: SESSION_ID,
      status: "completed",
      result: "Top story: Show HN",
      output: { rank: 0, isShowHN: false },
      error: null,
    });
    expect(result.text).toBe("The top story is Show HN.");
    expect(runs.cancel).not.toHaveBeenCalled();
  });

  it("continues an existing browser session when the model passes sessionId", async () => {
    const { client, runs } = fakeClient(async () => ({ status: "completed" }));
    await browserUse({ client }).execute({ task: "Click Next", sessionId: SESSION_ID });
    expect(runs.create).toHaveBeenCalledWith({ task: "Click Next", sessionId: SESSION_ID });
  });

  it("returns a failed run to the model instead of throwing", async () => {
    const { client } = fakeClient(async () => ({ status: "failed" }));
    const output = await browserUse({ client }).execute({ task: "Open a blocked site" });
    expect(output).toMatchObject({ status: "failed", error: "Site blocked", result: null });
  });

  it("times out on a stalled status poll and rethrows even if the cancel request hangs", async () => {
    vi.useFakeTimers();
    try {
      const { client, runs } = fakeClient(() => new Promise(() => {}));
      runs.cancel.mockImplementationOnce(() => new Promise(() => {}));
      const pending = browserUse({ client, waitTimeout: 20 }).execute({ task: "Slow task" });
      const settled = expect(pending).rejects.toThrow(`Run ${RUN_ID} did not complete within 20ms`);
      await vi.advanceTimersByTimeAsync(20 + 10_000);
      await settled;
      expect(runs.cancel).toHaveBeenCalledWith(RUN_ID);
    } finally {
      vi.useRealTimers();
    }
  });

  it("does not start polling when aborted while the run is being created", async () => {
    const { client, runs } = fakeClient(async () => ({ status: "completed" }));
    const controller = new AbortController();
    runs.create.mockImplementationOnce(async () => {
      controller.abort(new Error("user stopped"));
      return { id: RUN_ID, sessionId: SESSION_ID };
    });
    await expect(
      browserUse({ client }).execute({ task: "x" }, { abortSignal: controller.signal }),
    ).rejects.toThrow("user stopped");
    expect(runs.waitForCompletion).not.toHaveBeenCalled();
    expect(runs.cancel).toHaveBeenCalledWith(RUN_ID);
  });

  it("cancels the run when the caller aborts", async () => {
    const { client, runs } = fakeClient(() => new Promise(() => {}));
    const controller = new AbortController();
    const pending = browserUse({ client }).execute(
      { task: "Long task" },
      { abortSignal: controller.signal },
    );
    await vi.waitFor(() => expect(runs.waitForCompletion).toHaveBeenCalled());
    controller.abort(new Error("user stopped"));
    await expect(pending).rejects.toThrow("user stopped");
    expect(runs.cancel).toHaveBeenCalledWith(RUN_ID);
  });

  it("does not create a run when already aborted", async () => {
    const { client, runs } = fakeClient(async () => ({ status: "completed" }));
    const controller = new AbortController();
    controller.abort();
    await expect(
      browserUse({ client }).execute({ task: "x" }, { abortSignal: controller.signal }),
    ).rejects.toThrow();
    expect(runs.create).not.toHaveBeenCalled();
  });
});
