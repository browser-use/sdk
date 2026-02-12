import type { HttpClient } from "../../core/http.js";
import type { components } from "../../generated/v2/types.js";

type AccountView = components["schemas"]["AccountView"];

export class Billing {
  constructor(private readonly http: HttpClient) {}

  /** Get authenticated account billing information including credit balance. */
  account(): Promise<AccountView> {
    return this.http.get<AccountView>("/billing/account");
  }
}
