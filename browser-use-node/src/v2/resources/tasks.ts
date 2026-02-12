import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

/** User-facing body: only `task` is required; everything else has API defaults. */
export type CreateTaskBody = Pick<components["schemas"]["CreateTaskRequest"], "task"> &
  Partial<Omit<components["schemas"]["CreateTaskRequest"], "task">>;
type TaskCreatedResponse = components["schemas"]["TaskCreatedResponse"];
type TaskListResponse = components["schemas"]["TaskListResponse"];
type TaskLogFileResponse = components["schemas"]["TaskLogFileResponse"];
type TaskStatusView = components["schemas"]["TaskStatusView"];
type TaskView = components["schemas"]["TaskView"];

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

  /** Stop a running task. */
  stop(taskId: string): Promise<TaskView> {
    return this.http.patch<TaskView>(`/tasks/${taskId}`, { action: "stop" });
  }

  /** Get lightweight task status (optimized for polling). */
  status(taskId: string): Promise<TaskStatusView> {
    return this.http.get<TaskStatusView>(`/tasks/${taskId}/status`);
  }

  /** Get secure download URL for task execution logs. */
  logs(taskId: string): Promise<TaskLogFileResponse> {
    return this.http.get<TaskLogFileResponse>(`/tasks/${taskId}/logs`);
  }
}
