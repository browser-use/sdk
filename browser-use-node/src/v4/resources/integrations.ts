import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type IntegrationListResponse = components["schemas"]["IntegrationListResponse"];
type IntegrationCategoryResponse = components["schemas"]["IntegrationCategoryResponse"];
type AuthorizeResponse = components["schemas"]["AuthorizeResponse"];
type ConnectionStatusResponse = components["schemas"]["ConnectionStatusResponse"];
type DisconnectResponse = components["schemas"]["DisconnectResponse"];

export interface IntegrationListParams {
  limit?: number | null;
  offset?: number;
  search?: string | null;
  popularOnly?: boolean;
  connectedOnly?: boolean;
}

export class Integrations {
  constructor(private readonly http: HttpClient) {}

  /** List available integrations with this project's connection status. */
  list(params?: IntegrationListParams): Promise<IntegrationListResponse> {
    return this.http.get<IntegrationListResponse>("/integrations", {
      limit: params?.limit,
      offset: params?.offset,
      search: params?.search,
      popular_only: params?.popularOnly,
      connected_only: params?.connectedOnly,
    });
  }

  /** List integration categories. */
  categories(): Promise<IntegrationCategoryResponse> {
    return this.http.get<IntegrationCategoryResponse>("/integrations/categories");
  }

  /** Get the OAuth URL that connects a provider; poll `status()` after opening it. */
  authorize(provider: string): Promise<AuthorizeResponse> {
    return this.http.post<AuthorizeResponse>(`/integrations/${provider}/authorize`);
  }

  /** Check whether this project has connected a provider. */
  status(provider: string): Promise<ConnectionStatusResponse> {
    return this.http.get<ConnectionStatusResponse>(`/integrations/${provider}/status`);
  }

  /** Disconnect a provider from this project. */
  disconnect(provider: string): Promise<DisconnectResponse> {
    return this.http.delete<DisconnectResponse>(`/integrations/${provider}`);
  }
}
