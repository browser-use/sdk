import { tool } from "ai";
import { z } from "zod";
import { BrowserUse } from "browser-use-sdk/v4";

export interface BrowserUseToolsOptions {
  /** Defaults to process.env.BROWSER_USE_API_KEY. */
  apiKey?: string;
  /** Browser Use agent model, e.g. "bu-4.0" or "bu-ultrafast". Omit for the project default. */
  model?: string;
  /** Max time to wait for one task, in ms. Default 10 minutes. */
  timeoutMs?: number;
  /** Pass an existing client (tests, custom base URL). */
  client?: BrowserUse;
}

export interface BrowserUseTaskResult {
  status: string;
  result: string | null;
  error: string | null;
  sessionId: string;
  costUsd: string;
}

/**
 * Tools that let a model hand a web task to a Browser Use agent running in a stealth cloud browser.
 * Each call creates one run on the Browser Use Cloud v4 API and waits for it to finish.
 */
export function createBrowserUseTools(options: BrowserUseToolsOptions = {}) {
  let client = options.client;
  const getClient = () => (client ??= new BrowserUse({ apiKey: options.apiKey }));
  const timeout = options.timeoutMs ?? 600_000;

  const browserUseTask = tool({
    description:
      "Complete a task on the live web with a Browser Use agent in a cloud browser (stealth, proxies, CAPTCHA handling). " +
      "Use it to read pages that need JavaScript, log-in flows, forms, multi-step navigation or data extraction. " +
      "Describe the goal and what to return, e.g. 'Open news.ycombinator.com and return the top 3 titles'. Returns the agent's final answer.",
    inputSchema: z.object({
      task: z.string().min(1).describe("The goal in plain language, including what to return."),
      sessionId: z
        .string()
        .optional()
        .describe("Continue in the same browser session as an earlier call (pass its sessionId)."),
    }),
    execute: async ({ task, sessionId }): Promise<BrowserUseTaskResult> => {
      const c = getClient();
      const run = await c.runs.create({
        task,
        ...(options.model ? { model: options.model } : {}),
        ...(sessionId ? { sessionId } : {}),
      });
      const done = await c.runs.waitForCompletion(run.id, { timeout });
      return {
        status: done.status,
        result: done.result,
        error: done.error,
        sessionId: done.sessionId,
        costUsd: done.totalCostUsd,
      };
    },
  });

  return { tools: { browserUseTask } };
}
