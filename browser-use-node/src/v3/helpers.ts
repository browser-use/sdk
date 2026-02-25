import type { z } from "zod";
import type { components } from "../generated/v3/types.js";
import type { Sessions } from "./resources/sessions.js";

type SessionResponse = components["schemas"]["SessionResponse"];

const TERMINAL_STATUSES = new Set(["idle", "stopped", "timed_out", "error"]);

export interface RunOptions {
  /** Maximum time to wait in milliseconds. Default: 300_000 (5 min). */
  timeout?: number;
  /** Polling interval in milliseconds. Default: 2_000. */
  interval?: number;
}

/** Session result with typed output. All SessionResponse fields are directly accessible. */
export type SessionResult<T = string | null> = Omit<SessionResponse, "output"> & { output: T };

/**
 * Dual-purpose session handle: `await` it for a typed SessionResult,
 * or access `.result` for the full SessionResult after resolution.
 */
export class SessionRun<T = string> implements PromiseLike<SessionResult<T>> {
  private readonly _createPromise: Promise<SessionResponse>;
  private readonly _sessions: Sessions;
  private readonly _schema?: z.ZodType<T>;
  private readonly _timeout: number;
  private readonly _interval: number;
  private _sessionId: string | null = null;
  private _result: SessionResult<T> | null = null;

  constructor(
    createPromise: Promise<SessionResponse>,
    sessions: Sessions,
    schema?: z.ZodType<T>,
    options?: RunOptions,
  ) {
    this._createPromise = createPromise;
    this._sessions = sessions;
    this._schema = schema;
    this._timeout = options?.timeout ?? 300_000;
    this._interval = options?.interval ?? 2_000;
  }

  /** The session ID, available after task creation resolves. */
  get sessionId(): string | null {
    return this._sessionId;
  }

  /** The full SessionResult, available after polling completes. */
  get result(): SessionResult<T> | null {
    return this._result;
  }

  /** Enable `await client.run(...)` — polls until terminal, returns SessionResult. */
  then<R1 = SessionResult<T>, R2 = never>(
    onFulfilled?:
      | ((value: SessionResult<T>) => R1 | PromiseLike<R1>)
      | null,
    onRejected?: ((reason: unknown) => R2 | PromiseLike<R2>) | null,
  ): Promise<R1 | R2> {
    return this._waitForOutput().then(onFulfilled, onRejected);
  }

  private async _ensureSessionId(): Promise<string> {
    if (this._sessionId) return this._sessionId;
    const created = await this._createPromise;
    this._sessionId = created.id;
    return this._sessionId;
  }

  /** Poll session until terminal, return SessionResult. */
  private async _waitForOutput(): Promise<SessionResult<T>> {
    const sessionId = await this._ensureSessionId();
    const deadline = Date.now() + this._timeout;

    while (Date.now() < deadline) {
      const session = await this._sessions.get(sessionId);
      if (TERMINAL_STATUSES.has(session.status)) {
        const { output, ...rest } = session;
        const parsed = this._parseOutput(output);
        this._result = { ...rest, output: parsed } as SessionResult<T>;
        return this._result;
      }
      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((r) =>
        setTimeout(r, Math.min(this._interval, remaining)),
      );
    }

    throw new Error(
      `Session ${sessionId} did not complete within ${this._timeout}ms`,
    );
  }

  private _parseOutput(output: unknown): T {
    if (output == null) return null as T;
    if (!this._schema) return output as unknown as T;
    const raw = typeof output === "string" ? JSON.parse(output) : output;
    return this._schema.parse(raw);
  }
}
