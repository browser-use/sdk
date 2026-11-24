import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";
import type { RunListParams } from "./runs.js";

type ScheduleCreateRequest = components["schemas"]["ScheduleCreateRequest"];
type ScheduleUpdateRequest = components["schemas"]["ScheduleUpdateRequest"];
type ScheduleView = components["schemas"]["ScheduleView"];
type ScheduleListResponse = components["schemas"]["ScheduleListResponse"];
type RunListResponse = components["schemas"]["RunListResponse"];

/** Known V4 schedule model ids. */
export type ScheduleModel = NonNullable<ScheduleCreateRequest["model"]>;

export type ScheduleCreateBody = Omit<ScheduleCreateRequest, "model" | "cronExpr" | "runAt"> & {
  model?: ScheduleModel | (string & {});
} & (
  | { cronExpr: string; runAt?: null }
  | { runAt: string; cronExpr?: null }
);

export interface ScheduleListParams {
  cursor?: string | null;
  limit?: number;
  enabled?: boolean;
}

export interface ScheduleRunsParams extends RunListParams {
  metadata?: string[] | null;
}

export class Schedules {
  constructor(private readonly http: HttpClient) {}

  /** Schedule a task to run once or on a recurring cron. */
  create<T extends ScheduleCreateBody>(body: T): Promise<ScheduleView> {
    return this.http.post<ScheduleView>("/schedules", body);
  }

  /** List project schedules with cursor-based pagination, newest first. */
  list(params?: ScheduleListParams): Promise<ScheduleListResponse> {
    return this.http.get<ScheduleListResponse>("/schedules", params as Record<string, unknown>);
  }

  /** Get a schedule. */
  get(scheduleId: string): Promise<ScheduleView> {
    return this.http.get<ScheduleView>(`/schedules/${scheduleId}`);
  }

  /** Update a schedule's task, timing, time zone, or enabled state. */
  update<T extends object>(scheduleId: string, body: ScheduleUpdateRequest & T): Promise<ScheduleView> {
    return this.http.patch<ScheduleView>(`/schedules/${scheduleId}`, body);
  }

  /** Delete a schedule. */
  delete(scheduleId: string): Promise<void> {
    return this.http.delete<void>(`/schedules/${scheduleId}`);
  }

  /** List the runs started by a schedule with cursor-based pagination. */
  runs(scheduleId: string, params?: ScheduleRunsParams): Promise<RunListResponse> {
    return this.http.get<RunListResponse>(
      `/schedules/${scheduleId}/runs`,
      params as Record<string, unknown>,
    );
  }
}
