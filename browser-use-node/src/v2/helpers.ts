import type { z } from "zod";
import type { components } from "../generated/v2/types.js";
import type { Tasks } from "./resources/tasks.js";

type TaskCreatedResponse = components["schemas"]["TaskCreatedResponse"];
type TaskStepView = components["schemas"]["TaskStepView"];
type TaskView = components["schemas"]["TaskView"];

export const TERMINAL_STATUSES = new Set(["finished", "stopped", "failed"]);

/** Task result with typed output. All TaskView fields are directly accessible. */
export type TaskResult<T = string | null> = Omit<TaskView, "output"> & { output: T };

export interface RunOptions {
  /** Maximum time to wait in milliseconds. Default: 300_000 (5 min). */
  timeout?: number;
  /** Polling interval in milliseconds. Default: 2_000. */
  interval?: number;
}

/**
 * Lazy task handle returned by `client.run()`.
 *
 * - `await client.run(...)` polls the lightweight status endpoint, returns a `TaskResult`.
 * - `for await (const step of client.run(...))` polls the full task, yields new steps.
 */
export class TaskRun<T = string> implements PromiseLike<TaskResult<T>> {
  private readonly _createPromise: Promise<TaskCreatedResponse>;
  private readonly _tasks: Tasks;
  private readonly _schema?: z.ZodType<T>;
  private readonly _timeout: number;
  private readonly _interval: number;

  private _taskId: string | null = null;
  private _result: TaskResult<T> | null = null;

  constructor(
    createPromise: Promise<TaskCreatedResponse>,
    tasks: Tasks,
    schema?: z.ZodType<T>,
    options?: RunOptions,
  ) {
    this._createPromise = createPromise;
    this._tasks = tasks;
    this._schema = schema;
    this._timeout = options?.timeout ?? 300_000;
    this._interval = options?.interval ?? 2_000;
  }

  /** Task ID (available after creation resolves). */
  get taskId(): string | null {
    return this._taskId;
  }

  /** Full task result (available after awaiting or iterating to completion). */
  get result(): TaskResult<T> | null {
    return this._result;
  }

  /** Enable `await client.run(...)` — polls status endpoint, returns TaskResult. */
  then<R1 = TaskResult<T>, R2 = never>(
    onFulfilled?: ((value: TaskResult<T>) => R1 | PromiseLike<R1>) | null,
    onRejected?: ((reason: unknown) => R2 | PromiseLike<R2>) | null,
  ): Promise<R1 | R2> {
    return this._waitForOutput().then(onFulfilled, onRejected);
  }

  /** Enable `for await (const step of client.run(...))` — polls full task, yields new steps. */
  async *[Symbol.asyncIterator](): AsyncGenerator<TaskStepView> {
    const taskId = await this._ensureTaskId();
    let seen = 0;
    const deadline = Date.now() + this._timeout;

    while (Date.now() < deadline) {
      const task = await this._tasks.get(taskId);

      for (let i = seen; i < task.steps.length; i++) {
        yield task.steps[i];
      }
      seen = task.steps.length;

      if (TERMINAL_STATUSES.has(task.status)) {
        this._result = this._buildResult(task);
        return;
      }

      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((r) => setTimeout(r, Math.min(this._interval, remaining)));
    }

    throw new Error(`Task ${taskId} did not complete within ${this._timeout}ms`);
  }

  private async _ensureTaskId(): Promise<string> {
    if (this._taskId) return this._taskId;
    const created = await this._createPromise;
    this._taskId = created.id;
    return this._taskId;
  }

  /** Poll lightweight status endpoint until terminal, return TaskResult. */
  private async _waitForOutput(): Promise<TaskResult<T>> {
    const taskId = await this._ensureTaskId();
    const deadline = Date.now() + this._timeout;

    while (Date.now() < deadline) {
      const status = await this._tasks.status(taskId);
      if (TERMINAL_STATUSES.has(status.status)) {
        const task = await this._tasks.get(taskId);
        this._result = this._buildResult(task);
        return this._result;
      }
      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((r) => setTimeout(r, Math.min(this._interval, remaining)));
    }

    throw new Error(`Task ${taskId} did not complete within ${this._timeout}ms`);
  }

  private _buildResult(task: TaskView): TaskResult<T> {
    const output = this._parseOutput(task.output);
    return { ...task, output };
  }

  private _parseOutput(output: string | null | undefined): T {
    if (output == null) return null as T;
    if (!this._schema) return output as unknown as T;
    return this._schema.parse(JSON.parse(output));
  }
}
