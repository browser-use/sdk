import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type GeneratedRunCreateRequest = components["schemas"]["RunCreateRequest"];
export type RunCreateRequest = Omit<GeneratedRunCreateRequest, "model"> & {
  /** Defaults to minimax-m3 when omitted. */
  model?: GeneratedRunCreateRequest["model"];
};
type RunCreateResponse = components["schemas"]["RunCreateResponse"];
type RunSummary = components["schemas"]["RunSummary"];
type RunStatusResponse = components["schemas"]["RunStatusResponse"];
type RunListResponse = components["schemas"]["RunListResponse"];
type RunEventsResponse = components["schemas"]["RunEventsResponse"];
type RunAttachmentsResponse = components["schemas"]["RunAttachmentsResponse"];

/** Terminal run statuses — closed enum in the v4 spec. */
const TERMINAL_STATUSES = new Set(["completed", "failed", "cancelled"]);

export interface RunListParams {
  sessionId?: string;
  cursor?: string | null;
  limit?: number;
}

export interface RunEventsParams {
  after?: number | null;
  limit?: number;
}

export interface WaitOptions {
  /** Maximum time to wait in milliseconds. Default: 14_400_000 (4 hours). */
  timeout?: number;
  /** Polling interval in milliseconds. Default: 2_000. */
  interval?: number;
}

export class Runs {
  constructor(private readonly http: HttpClient) {}

  /** Create a run (a new session, or a follow-up turn when sessionId is set). */
  create(body: RunCreateRequest): Promise<RunCreateResponse> {
    return this.http.post<RunCreateResponse>("/runs", body);
  }

  /** List runs with cursor-based pagination, most recent first. */
  list(params?: RunListParams): Promise<RunListResponse> {
    return this.http.get<RunListResponse>("/runs", params as Record<string, unknown>);
  }

  /** Get the full run summary. */
  get(runId: string): Promise<RunSummary> {
    return this.http.get<RunSummary>(`/runs/${runId}`);
  }

  /** Get just the run's status — the cheap poll target. */
  status(runId: string): Promise<RunStatusResponse> {
    return this.http.get<RunStatusResponse>(`/runs/${runId}/status`);
  }

  /** List run events incrementally — pass `after` from the previous page's nextAfter. */
  events(runId: string, params?: RunEventsParams): Promise<RunEventsResponse> {
    return this.http.get<RunEventsResponse>(
      `/runs/${runId}/events`,
      params as Record<string, unknown>,
    );
  }

  /** Cancel a run. Returns the updated run summary. */
  cancel(runId: string): Promise<RunSummary> {
    return this.http.post<RunSummary>(`/runs/${runId}/cancel`);
  }

  /** List files the agent attached to the run. */
  attachments(runId: string): Promise<RunAttachmentsResponse> {
    return this.http.get<RunAttachmentsResponse>(`/runs/${runId}/attachments`);
  }

  /**
   * Poll the run's status until terminal (completed | failed | cancelled),
   * then fetch and return the full run summary. This is the loop the v4 API
   * was designed for — status is a tiny indexed lookup, the full summary is
   * fetched exactly once at the end.
   *
   * ```ts
   * const created = await client.runs.create({ task: "Find the top HN post" });
   * const run = await client.runs.waitForCompletion(created.id);
   * console.log(run.status, run.result);
   * ```
   */
  async waitForCompletion(runId: string, options?: WaitOptions): Promise<RunSummary> {
    const timeout = options?.timeout ?? 14_400_000;
    const interval = options?.interval ?? 2_000;
    const deadline = Date.now() + timeout;

    // A terminal status is always returned, even if the status() call itself
    // finished slightly past the deadline — a completed run is never thrown
    // away. Only a non-terminal status seen past the deadline is a timeout.
    for (;;) {
      const { status } = await this.status(runId);
      if (TERMINAL_STATUSES.has(status)) {
        return this.get(runId);
      }
      const remaining = deadline - Date.now();
      if (remaining <= 0) {
        throw new Error(`Run ${runId} did not complete within ${timeout}ms`);
      }
      await new Promise((r) => setTimeout(r, Math.min(interval, remaining)));
    }
  }
}
