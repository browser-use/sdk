import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

type CreateSkillRequest = components["schemas"]["CreateSkillRequest"];
type CreateSkillResponse = components["schemas"]["CreateSkillResponse"];
type ExecuteSkillRequest = components["schemas"]["ExecuteSkillRequest"];
type ExecuteSkillResponse = components["schemas"]["ExecuteSkillResponse"];
type RefineSkillRequest = components["schemas"]["RefineSkillRequest"];
type RefineSkillResponse = components["schemas"]["RefineSkillResponse"];
type SkillExecutionListResponse = components["schemas"]["SkillExecutionListResponse"];
type SkillExecutionOutputResponse = components["schemas"]["SkillExecutionOutputResponse"];
type SkillListResponse = components["schemas"]["SkillListResponse"];
type SkillResponse = components["schemas"]["SkillResponse"];
type UpdateSkillRequest = components["schemas"]["UpdateSkillRequest"];

export interface SkillListParams {
  pageSize?: number;
  pageNumber?: number;
  isPublic?: boolean;
  isEnabled?: boolean;
  category?: string;
  query?: string;
  fromDate?: string;
  toDate?: string;
}

export interface SkillExecutionListParams {
  pageSize?: number;
  pageNumber?: number;
}

export class Skills {
  constructor(private readonly http: HttpClient) {}

  /** Create a new skill via automated generation. */
  create(body: CreateSkillRequest): Promise<CreateSkillResponse> {
    return this.http.post<CreateSkillResponse>("/skills", body);
  }

  /** List all skills owned by the project. */
  list(params?: SkillListParams): Promise<SkillListResponse> {
    return this.http.get<SkillListResponse>("/skills", params as Record<string, unknown>);
  }

  /** Get details of a specific skill. */
  get(skillId: string): Promise<SkillResponse> {
    return this.http.get<SkillResponse>(`/skills/${skillId}`);
  }

  /** Delete a skill. */
  delete(skillId: string): Promise<void> {
    return this.http.delete<void>(`/skills/${skillId}`);
  }

  /** Update skill metadata. */
  update(skillId: string, body: UpdateSkillRequest): Promise<SkillResponse> {
    return this.http.patch<SkillResponse>(`/skills/${skillId}`, body);
  }

  /** Cancel the current in-progress generation for a skill. */
  cancel(skillId: string): Promise<SkillResponse> {
    return this.http.post<SkillResponse>(`/skills/${skillId}/cancel`);
  }

  /** Execute a skill with the provided parameters. */
  execute(skillId: string, body: ExecuteSkillRequest): Promise<ExecuteSkillResponse> {
    return this.http.post<ExecuteSkillResponse>(`/skills/${skillId}/execute`, body);
  }

  /** Refine a skill based on feedback. */
  refine(skillId: string, body: RefineSkillRequest): Promise<RefineSkillResponse> {
    return this.http.post<RefineSkillResponse>(`/skills/${skillId}/refine`, body);
  }

  /** Rollback to the previous version. */
  rollback(skillId: string): Promise<SkillResponse> {
    return this.http.post<SkillResponse>(`/skills/${skillId}/rollback`);
  }

  /** List executions for a specific skill. */
  executions(skillId: string, params?: SkillExecutionListParams): Promise<SkillExecutionListResponse> {
    return this.http.get<SkillExecutionListResponse>(
      `/skills/${skillId}/executions`,
      params as Record<string, unknown>,
    );
  }

  /** Get presigned URL for downloading skill execution output. */
  executionOutput(skillId: string, executionId: string): Promise<SkillExecutionOutputResponse> {
    return this.http.get<SkillExecutionOutputResponse>(
      `/skills/${skillId}/executions/${executionId}/output`,
    );
  }
}
