import { describe, expect, it, vi } from "vitest";

import { applyX402MaxPaymentUsd } from "../src/core/x402.js";

describe("x402 payment cap", () => {
  it("filters v2 and v1 payment requirements above the USD cap", () => {
    const registerPolicy = vi.fn();
    const client = { registerPolicy };

    applyX402MaxPaymentUsd(client, 0.75);

    const policy = registerPolicy.mock.calls[0][0] as (
      version: number,
      requirements: unknown[],
    ) => unknown[];
    expect(
      policy(2, [
        { amount: "750000" },
        { amount: "750001" },
        { amount: "not-a-number" },
      ]),
    ).toEqual([{ amount: "750000" }]);
    expect(
      policy(1, [
        { maxAmountRequired: "749999" },
        { maxAmountRequired: "1000000" },
      ]),
    ).toEqual([{ maxAmountRequired: "749999" }]);
  });

  it.each([0, -1, Number.NaN, Number.POSITIVE_INFINITY])(
    "rejects invalid caps (%s)",
    (cap) => {
      expect(() => applyX402MaxPaymentUsd({ registerPolicy: vi.fn() }, cap)).toThrow(
        /positive finite number/,
      );
    },
  );

  it("rejects clients that cannot enforce a policy", () => {
    expect(() => applyX402MaxPaymentUsd({}, 1)).toThrow(/does not support payment policies/);
  });
});
