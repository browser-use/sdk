import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

type ExecuteSkillRequest = components["schemas"]["ExecuteSkillRequest"];
type ExecuteSkillResponse = components["schemas"]["ExecuteSkillResponse"];
type MarketplaceSkillListResponse = components["schemas"]["MarketplaceSkillListResponse"];
type MarketplaceSkillResponse = components["schemas"]["MarketplaceSkillResponse"];
type SkillResponse = components["schemas"]["SkillResponse"];

export interface MarketplaceListParams {
  pageSize?: number;
  pageNumber?: number;
  query?: string;
  category?: string;
  fromDate?: string;
  toDate?: string;
}

export class Marketplace {
  constructor(private readonly http: HttpClient) {}

  /** List all public skills in the marketplace. */
  list(params?: MarketplaceListParams): Promise<MarketplaceSkillListResponse> {
    return this.http.get<MarketplaceSkillListResponse>(
      "/marketplace/skills",
      params as Record<string, unknown>,
    );
  }

  /** Get details of a specific marketplace skill by slug. */
  get(skillSlug: string): Promise<MarketplaceSkillResponse> {
    return this.http.get<MarketplaceSkillResponse>(`/marketplace/skills/${skillSlug}`);
  }

  /** Clone a public marketplace skill to your project. */
  clone(skillId: string): Promise<SkillResponse> {
    return this.http.post<SkillResponse>(`/marketplace/skills/${skillId}/clone`);
  }

  /** Execute a marketplace skill. */
  execute(skillId: string, body: ExecuteSkillRequest): Promise<ExecuteSkillResponse> {
    return this.http.post<ExecuteSkillResponse>(
      `/marketplace/skills/${skillId}/execute`,
      body,
    );
  }
}
