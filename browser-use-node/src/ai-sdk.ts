import { z } from "zod";

import { BrowserUse } from "./v4/client.js";
import type { BrowserUseOptions } from "./v4/client.js";
import type { RunCreateBody } from "./v4/resources/runs.js";

const DEFAULT_TIMEOUT_MS = 300_000;

const inputSchema = z.object({
  task: z
    .string()
    .min(1)
    .describe(
      "What to do on the web, in plain language. Include URLs, the data to collect, and the format to return it in.",
    ),
  sessionId: z
    .string()
    .optional()
    .describe(
      "sessionId from an earlier browserUse result. Pass it to continue in the same browser, with its pages and logins.",
    ),
});

export type BrowserUseToolInput = z.infer<typeof inputSchema>;

export interface BrowserUseToolOutput {
  runId: string;
  sessionId: string;
  status: "completed" | "failed" | "cancelled";
  result: string | null;
  error: string | null;
}

export interface BrowserUseToolOptions extends BrowserUseOptions {
  /** Reuse an existing V4 client instead of creating one from apiKey / BROWSER_USE_API_KEY. */
  client?: BrowserUse;
  /** Extra V4 run fields sent with every call, for example model, maxCostUsd, or browserSettings. */
  runOptions?: Partial<Omit<RunCreateBody, "task" | "sessionId">>;
  /** How long one tool call waits for its run, in ms. When it passes, the tool cancels the run and throws. Default 300_000. */
  waitTimeout?: number;
  /** Status poll interval in ms. Default 2_000. */
  pollInterval?: number;
  /** Tool description shown to the model. */
  description?: string;
}

/**
 * Create a Vercel AI SDK tool that runs a Browser Use Cloud agent in a real browser.
 *
 * ```ts
 * import { generateText, isStepCount } from "ai";
 * import { browserUse } from "browser-use-sdk/ai-sdk";
 *
 * const { text } = await generateText({
 *   model: "openai/gpt-5.6",
 *   tools: { browserUse: browserUse() },
 *   stopWhen: isStepCount(5),
 *   prompt: "Open news.ycombinator.com and summarize the top 3 stories.",
 * });
 * ```
 */
export function browserUse(options: BrowserUseToolOptions = {}) {
  const {
    client: providedClient,
    runOptions,
    waitTimeout = DEFAULT_TIMEOUT_MS,
    pollInterval,
    description,
    ...clientOptions
  } = options;
  let client = providedClient;

  return {
    description:
      description ??
      "Run a task in a real cloud browser with Browser Use. The agent navigates, clicks, types, logs in, and extracts data, then returns its final answer. Use it for live web pages, multi-step browsing, and sites without an API.",
    inputSchema,
    execute: async (
      { task, sessionId }: BrowserUseToolInput,
      { abortSignal }: { abortSignal?: AbortSignal } = {},
    ): Promise<BrowserUseToolOutput> => {
      abortSignal?.throwIfAborted();
      client ??= new BrowserUse(clientOptions);
      const runs = client.runs;

      const created = await runs.create({
        ...runOptions,
        task,
        ...(sessionId ? { sessionId } : {}),
      });

      try {
        abortSignal?.throwIfAborted();
        const run = await withDeadline(
          runs.waitForCompletion(created.id, { timeout: waitTimeout, interval: pollInterval }),
          created.id,
          waitTimeout,
          abortSignal,
        );
        return {
          runId: run.id,
          sessionId: run.sessionId,
          status: run.status as BrowserUseToolOutput["status"],
          result: run.result,
          error: run.error,
        };
      } catch (error) {
        // Best effort: stop the run so it does not keep billing after a timeout, abort, or poll error.
        await runs.cancel(created.id).catch(() => undefined);
        throw error;
      }
    },
  };
}

/** Settle with the poll result, or reject on the deadline or abort, whichever comes first. */
function withDeadline<T>(
  poll: Promise<T>,
  runId: string,
  timeout: number,
  signal?: AbortSignal,
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(
      () => reject(new Error(`Run ${runId} did not complete within ${timeout}ms`)),
      timeout,
    );
    const onAbort = () => reject(signal?.reason ?? new Error("Aborted"));
    signal?.addEventListener("abort", onAbort, { once: true });
    poll.then(resolve, reject).finally(() => {
      clearTimeout(timer);
      signal?.removeEventListener("abort", onAbort);
    });
  });
}
