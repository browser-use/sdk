import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type AgentCardWalletListResponse = components["schemas"]["AgentCardWalletListResponse"];
type StripeLinkStatusResponse = components["schemas"]["StripeLinkStatusResponse"];

export class Wallets {
  constructor(private readonly http: HttpClient) {}

  /** List the project's active AgentCard wallets, newest first. */
  agentcard(): Promise<AgentCardWalletListResponse> {
    return this.http.get<AgentCardWalletListResponse>("/agentcard/wallets");
  }

  /** Get the project's Stripe Link connection; pass its id as `stripeLinkConnectionId`. */
  stripeLink(): Promise<StripeLinkStatusResponse> {
    return this.http.get<StripeLinkStatusResponse>("/stripe-link");
  }
}
