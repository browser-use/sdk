import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type S = components["schemas"];
type NetworkPolicyView = S["NetworkPolicyView"];
type NetworkPolicyListResponse = S["NetworkPolicyListResponse"];
type NetworkPolicyCreateRequest = S["NetworkPolicyCreateRequest"];
type NetworkPolicyUpdateRequest = S["NetworkPolicyUpdateRequest"];

export interface NetworkPolicyListParams {
  pageSize?: number;
  pageNumber?: number;
}

export class NetworkPolicies {
  constructor(private readonly http: HttpClient) {}

  /** Create a network policy. */
  create(
    body: Pick<NetworkPolicyCreateRequest, "name"> &
      Partial<NetworkPolicyCreateRequest> & Record<string, unknown>,
  ): Promise<NetworkPolicyView> {
    return this.http.post<NetworkPolicyView>("/network-policies", body);
  }

  /** List network policies for the project. */
  list(params?: NetworkPolicyListParams): Promise<NetworkPolicyListResponse> {
    return this.http.get<NetworkPolicyListResponse>("/network-policies", params as Record<string, unknown>);
  }

  /** Get a network policy. */
  get(policyId: string): Promise<NetworkPolicyView> {
    return this.http.get<NetworkPolicyView>(`/network-policies/${policyId}`);
  }

  /** Update a network policy. */
  update(
    policyId: string,
    body: NetworkPolicyUpdateRequest & Record<string, unknown>,
  ): Promise<NetworkPolicyView> {
    return this.http.patch<NetworkPolicyView>(`/network-policies/${policyId}`, body);
  }

  /** Delete a network policy. */
  delete(policyId: string): Promise<void> {
    return this.http.delete<void>(`/network-policies/${policyId}`);
  }
}
