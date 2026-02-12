import type { components } from "../generated/v3/types.js";
import type { Sessions } from "./resources/sessions.js";

type SessionResponse = components["schemas"]["SessionResponse"];

const TERMINAL_STATUSES = new Set(["idle", "stopped", "timed_out", "error"]);

export interface PollOptions {
  /** Maximum time to wait in milliseconds. Default: 300_000 (5 min). */
  timeout?: number;
  /** Polling interval in milliseconds. Default: 2_000. */
  interval?: number;
}

export class SessionHandle {
  private readonly createPromise: Promise<SessionResponse>;
  private readonly sessions: Sessions;

  constructor(createPromise: Promise<SessionResponse>, sessions: Sessions) {
    this.createPromise = createPromise;
    this.sessions = sessions;
  }

  /** Get the raw creation response. */
  async created(): Promise<SessionResponse> {
    return this.createPromise;
  }

  /**
   * Poll until the session reaches a terminal status and return the final SessionResponse.
   * Throws if the timeout is exceeded.
   */
  async complete(opts?: PollOptions): Promise<SessionResponse> {
    const timeout = opts?.timeout ?? 300_000;
    const interval = opts?.interval ?? 2_000;
    const created = await this.createPromise;
    const sessionId = created.id;
    const deadline = Date.now() + timeout;

    while (Date.now() < deadline) {
      const session = await this.sessions.get(sessionId);
      if (TERMINAL_STATUSES.has(session.status)) {
        return session;
      }
      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((resolve) => setTimeout(resolve, Math.min(interval, remaining)));
    }

    throw new Error(`Session ${sessionId} did not complete within ${timeout}ms`);
  }

  /**
   * Yield session state on each poll until it reaches a terminal status.
   */
  async *stream(opts?: Pick<PollOptions, "interval">): AsyncGenerator<SessionResponse, SessionResponse> {
    const interval = opts?.interval ?? 2_000;
    const created = await this.createPromise;
    const sessionId = created.id;

    while (true) {
      const session = await this.sessions.get(sessionId);
      if (TERMINAL_STATUSES.has(session.status)) {
        return session;
      }
      yield session;
      await new Promise((resolve) => setTimeout(resolve, interval));
    }
  }
}
