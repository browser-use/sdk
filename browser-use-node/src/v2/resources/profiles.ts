import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

type ProfileCreateRequest = components["schemas"]["ProfileCreateRequest"];
type ProfileListResponse = components["schemas"]["ProfileListResponse"];
type ProfileUpdateRequest = components["schemas"]["ProfileUpdateRequest"];
type ProfileView = components["schemas"]["ProfileView"];

export interface ProfileListParams {
  pageSize?: number;
  pageNumber?: number;
}

export class Profiles {
  constructor(private readonly http: HttpClient) {}

  /** Create a new browser profile. */
  create(body?: ProfileCreateRequest): Promise<ProfileView> {
    return this.http.post<ProfileView>("/profiles", body);
  }

  /** List profiles with pagination. */
  list(params?: ProfileListParams): Promise<ProfileListResponse> {
    return this.http.get<ProfileListResponse>("/profiles", params as Record<string, unknown>);
  }

  /** Get profile details. */
  get(profileId: string): Promise<ProfileView> {
    return this.http.get<ProfileView>(`/profiles/${profileId}`);
  }

  /** Update a browser profile. */
  update(profileId: string, body: ProfileUpdateRequest): Promise<ProfileView> {
    return this.http.patch<ProfileView>(`/profiles/${profileId}`, body);
  }

  /** Delete a browser profile. */
  delete(profileId: string): Promise<void> {
    return this.http.delete<void>(`/profiles/${profileId}`);
  }
}
