import type { z } from "zod";
import type { components } from "../generated/v2/types.js";
import type { Tasks } from "./resources/tasks.js";

type TaskCreatedResponse = components["schemas"]["TaskCreatedResponse"];
type TaskStatusView = components["schemas"]["TaskStatusView"];
type TaskView = components["schemas"]["TaskView"];

const TERMINAL_STATUSES = new Set(["finished", "stopped", "failed"]);

export interface PollOptions {
  /** Maximum time to wait in milliseconds. Default: 300_000 (5 min). */
  timeout?: number;
  /** Polling interval in milliseconds. Default: 2_000. */
  interval?: number;
}

export class TaskHandle<T = string> {
  private readonly createPromise: Promise<TaskCreatedResponse>;
  private readonly tasks: Tasks;
  private readonly schema?: z.ZodType<T>;

  constructor(
    createPromise: Promise<TaskCreatedResponse>,
    tasks: Tasks,
    schema?: z.ZodType<T>,
  ) {
    this.createPromise = createPromise;
    this.tasks = tasks;
    this.schema = schema;
  }

  /** Get the raw creation response. */
  async created(): Promise<TaskCreatedResponse> {
    return this.createPromise;
  }

  /**
   * Poll until the task reaches a terminal status and return the final TaskView.
   * When a Zod schema was provided, the result includes a `parsed` property
   * with the validated output (or null if parsing fails or there is no output).
   */
  async complete(opts?: PollOptions): Promise<TaskView & { parsed: T | null }> {
    const timeout = opts?.timeout ?? 300_000;
    const interval = opts?.interval ?? 2_000;
    const created = await this.createPromise;
    const taskId = created.id;
    const deadline = Date.now() + timeout;

    while (Date.now() < deadline) {
      const status = await this.tasks.status(taskId);
      if (TERMINAL_STATUSES.has(status.status)) {
        const task = await this.tasks.get(taskId);
        return Object.assign(task, { parsed: this._parse(task.output) });
      }
      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((resolve) => setTimeout(resolve, Math.min(interval, remaining)));
    }

    throw new Error(`Task ${taskId} did not complete within ${timeout}ms`);
  }

  /**
   * Yield lightweight task status on each poll until it reaches a terminal status.
   */
  async *stream(opts?: Pick<PollOptions, "interval">): AsyncGenerator<TaskStatusView, TaskView & { parsed: T | null }> {
    const interval = opts?.interval ?? 2_000;
    const created = await this.createPromise;
    const taskId = created.id;

    while (true) {
      const status = await this.tasks.status(taskId);
      if (TERMINAL_STATUSES.has(status.status)) {
        const task = await this.tasks.get(taskId);
        return Object.assign(task, { parsed: this._parse(task.output) });
      }
      yield status;
      await new Promise((resolve) => setTimeout(resolve, interval));
    }
  }

  /** @internal Parse raw output using the Zod schema (if provided). */
  private _parse(output: string | null | undefined): T | null {
    if (output == null) return null;
    if (!this.schema) return output as unknown as T;
    const result = this.schema.safeParse(JSON.parse(output));
    if (!result.success) return null;
    return result.data;
  }
}
