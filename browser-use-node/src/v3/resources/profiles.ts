import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v3/types.js";

type ProfileView = components["schemas"]["ProfileView"];
type ProfileListResponse = components["schemas"]["ProfileListResponse"];
type ProfileCreateRequest = components["schemas"]["ProfileCreateRequest"];
type ProfileUpdateRequest = components["schemas"]["ProfileUpdateRequest"];

export interface ProfileListParams {
  query?: string;
  pageSize?: number;
  pageNumber?: number;
  /** @deprecated Use `pageNumber`. */
  page?: number;
  /** @deprecated Use `pageSize`. */
  page_size?: number;
}

export class Profiles {
  constructor(private readonly http: HttpClient) {}

  /** Create a browser profile. */
  create(body?: ProfileCreateRequest): Promise<ProfileView> {
    return this.http.post<ProfileView>("/profiles", body);
  }

  /** List profiles for the authenticated project. */
  list(params?: ProfileListParams): Promise<ProfileListResponse> {
    const { page, page_size, ...rest } = params ?? {};
    return this.http.get<ProfileListResponse>("/profiles", {
      ...rest,
      pageNumber: rest.pageNumber ?? page,
      pageSize: rest.pageSize ?? page_size,
    });
  }

  /** Get profile details. */
  get(profileId: string): Promise<ProfileView> {
    return this.http.get<ProfileView>(`/profiles/${profileId}`);
  }

  /** Update a profile. */
  update(profileId: string, body: ProfileUpdateRequest): Promise<ProfileView> {
    return this.http.patch<ProfileView>(`/profiles/${profileId}`, body);
  }

  /** Delete a profile. */
  delete(profileId: string): Promise<void> {
    return this.http.delete<void>(`/profiles/${profileId}`);
  }
}
