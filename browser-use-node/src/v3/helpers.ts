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

/**
 * Dual-purpose session handle: `await` it for the output value,
 * or access `.result` for the full SessionResponse after resolution.
 */
export class SessionRun implements PromiseLike<unknown> {
  private readonly _createPromise: Promise<SessionResponse>;
  private readonly _sessions: Sessions;
  private readonly _timeout: number;
  private readonly _interval: number;
  private _sessionId: string | null = null;
  private _result: SessionResponse | null = null;

  constructor(
    createPromise: Promise<SessionResponse>,
    sessions: Sessions,
    options?: RunOptions,
  ) {
    this._createPromise = createPromise;
    this._sessions = sessions;
    this._timeout = options?.timeout ?? 300_000;
    this._interval = options?.interval ?? 2_000;
  }

  /** The session ID, available after task creation resolves. */
  get sessionId(): string | null {
    return this._sessionId;
  }

  /** The full SessionResponse, available after polling completes. */
  get result(): SessionResponse | null {
    return this._result;
  }

  /** Enable `await client.run(...)` — polls until terminal, returns output. */
  then<R1 = unknown, R2 = never>(
    onFulfilled?:
      | ((value: unknown) => R1 | PromiseLike<R1>)
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

  private async _waitForOutput(): Promise<unknown> {
    const sessionId = await this._ensureSessionId();
    const deadline = Date.now() + this._timeout;

    while (Date.now() < deadline) {
      const session = await this._sessions.get(sessionId);
      if (TERMINAL_STATUSES.has(session.status)) {
        this._result = session;
        return session.output ?? null;
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
}
