/**
 * Helpers for the optional x402 (pay-per-request) integration.
 *
 * x402 is an HTTP payment protocol: instead of an API key, requests are
 * authenticated by signing a small USDC payment. See the docs at
 * `cloud/guides/x402` and https://www.x402.org for details.
 *
 * The peer deps `@x402/fetch`, `@x402/evm`, and `viem` are optional. They are
 * imported lazily so users who only use API-key auth never pay the cost.
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type X402Client = any;
export type FetchLike = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

export const X402_BASE_URL_DEFAULT = "https://x402.api.browser-use.com/api/v3";
export const X402_BASE_URL_DEFAULT_V2 = "https://x402.api.browser-use.com/api/v2";

const MISSING_X402 =
  "x402 mode requires the optional peer deps. Install them with: " +
  "npm install @x402/fetch @x402/evm viem  " +
  "(or the equivalent for pnpm/yarn).";

/** Build a ready-to-use x402 client from an EVM private key (`0x...`). */
export async function x402ClientFromPrivateKey(
  privateKey: `0x${string}` | string,
): Promise<X402Client> {
  let viem;
  let fetchPkg;
  let evmPkg;
  try {
    // @ts-ignore - optional peer dep, may not be installed
    viem = await import("viem/accounts");
    // @ts-ignore - optional peer dep, may not be installed
    fetchPkg = await import("@x402/fetch");
    // @ts-ignore - optional peer dep, may not be installed
    evmPkg = await import("@x402/evm");
  } catch (e) {
    throw new Error(MISSING_X402);
  }

  const key = privateKey.startsWith("0x") ? privateKey : `0x${privateKey}`;
  const signer = viem.privateKeyToAccount(key as `0x${string}`);
  const client = new fetchPkg.x402Client();
  client.register("eip155:*", new evmPkg.ExactEvmScheme(signer));
  return client;
}

/** Wrap a fetch with x402 payment handling. */
export async function wrapFetchWithX402(
  fetch: FetchLike,
  x402Client: X402Client,
): Promise<FetchLike> {
  let fetchPkg;
  try {
    // @ts-ignore - optional peer dep, may not be installed
    fetchPkg = await import("@x402/fetch");
  } catch (e) {
    throw new Error(MISSING_X402);
  }
  return fetchPkg.wrapFetchWithPayment(fetch, x402Client);
}
