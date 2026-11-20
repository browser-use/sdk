import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v4/types.js";

type AgentCardWalletListResponse = components["schemas"]["AgentCardWalletListResponse"];
type StripeLinkStatusResponse = components["schemas"]["StripeLinkStatusResponse"];

/** Payment sources a run may spend from: pass an id as `agentcardWalletId` or `stripeLinkConnectionId`. */
export class Payments {
  constructor(private readonly http: HttpClient) {}

  /** List the project's active AgentCard wallets, newest first. */
  wallets(): Promise<AgentCardWalletListResponse> {
    return this.http.get<AgentCardWalletListResponse>("/agentcard/wallets");
  }

  /** Get the project's Stripe Link connection; `connectionId` is null until one is connected. */
  stripeLink(): Promise<StripeLinkStatusResponse> {
    return this.http.get<StripeLinkStatusResponse>("/stripe-link");
  }
}
