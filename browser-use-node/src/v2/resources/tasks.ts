import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";
import { TERMINAL_STATUSES } from "../helpers.js";

/** User-facing body: only `task` is required; everything else has API defaults. */
export type CreateTaskBody = Pick<components["schemas"]["CreateTaskRequest"], "task"> &
  Partial<Omit<components["schemas"]["CreateTaskRequest"], "task">>;
type TaskCreatedResponse = components["schemas"]["TaskCreatedResponse"];
type TaskListResponse = components["schemas"]["TaskListResponse"];
type TaskLogFileResponse = components["schemas"]["TaskLogFileResponse"];
type TaskStatusView = components["schemas"]["TaskStatusView"];
type TaskView = components["schemas"]["TaskView"];
type UpdateTaskRequest = components["schemas"]["UpdateTaskRequest"];

export interface TaskListParams {
  pageSize?: number;
  pageNumber?: number;
  sessionId?: string;
  filterBy?: string;
  after?: string;
  before?: string;
}

export class Tasks {
  constructor(private readonly http: HttpClient) {}

  /** Create and start a new AI agent task. */
  create(body: CreateTaskBody): Promise<TaskCreatedResponse> {
    return this.http.post<TaskCreatedResponse>("/tasks", body);
  }

  /** List tasks with optional filtering. */
  list(params?: TaskListParams): Promise<TaskListResponse> {
    return this.http.get<TaskListResponse>("/tasks", params as Record<string, unknown>);
  }

  /** Get detailed task information. */
  get(taskId: string): Promise<TaskView> {
    return this.http.get<TaskView>(`/tasks/${taskId}`);
  }

  /** Update a task (generic PATCH). */
  update(taskId: string, body: UpdateTaskRequest): Promise<TaskView> {
    return this.http.patch<TaskView>(`/tasks/${taskId}`, body);
  }

  /** Stop a running task. */
  stop(taskId: string): Promise<TaskView> {
    return this.update(taskId, { action: "stop" });
  }

  /** Stop a running task and its associated browser session. */
  stopTaskAndSession(taskId: string): Promise<TaskView> {
    return this.update(taskId, { action: "stop_task_and_session" });
  }

  /** Get lightweight task status (optimized for polling). */
  status(taskId: string): Promise<TaskStatusView> {
    return this.http.get<TaskStatusView>(`/tasks/${taskId}/status`);
  }

  /** Get secure download URL for task execution logs. */
  logs(taskId: string): Promise<TaskLogFileResponse> {
    return this.http.get<TaskLogFileResponse>(`/tasks/${taskId}/logs`);
  }

  /** Poll until a task reaches a terminal status, then return the full TaskView. */
  async wait(taskId: string, opts?: { timeout?: number; interval?: number }): Promise<TaskView> {
    const timeout = opts?.timeout ?? 300_000;
    const interval = opts?.interval ?? 2_000;
    const deadline = Date.now() + timeout;

    while (Date.now() < deadline) {
      const status = await this.status(taskId);
      if (TERMINAL_STATUSES.has(status.status)) {
        return this.get(taskId);
      }
      const remaining = deadline - Date.now();
      if (remaining <= 0) break;
      await new Promise((r) => setTimeout(r, Math.min(interval, remaining)));
    }

    throw new Error(`Task ${taskId} did not complete within ${timeout}ms`);
  }
}
