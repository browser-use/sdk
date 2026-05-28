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
export const X402_BALANCE_BASE_URL_DEFAULT = "https://api.browser-use.com/api/v3";

export interface X402WalletBalance {
  wallet: string;
  project_id: string;
  total_credits_usd: number;
  additional_credits_usd: number;
}

function buildWalletAuthMessage(address: string, issuedAt: string, nonce: string): string {
  return (
    "Browser Use x402 wallet authentication\n" +
    "Action: read credit balance\n" +
    `Wallet: ${address}\n` +
    `Issued At: ${issuedAt}\n` +
    `Nonce: ${nonce}`
  );
}

/**
 * Read a wallet-derived project's credit balance
 *
 * Authenticates with an off-chain wallet signature (EIP-191): signs a
 * message proving control of the address; the server resolves the wallet to its
 * project and returns the balance
 */
export async function getWalletBalance(
  privateKey: `0x${string}` | string,
  opts: { baseUrl?: string } = {},
): Promise<X402WalletBalance> {
  let viem;
  try {
    // @ts-ignore - optional peer dep, may not be installed
    viem = await import("viem/accounts");
  } catch {
    throw new Error(MISSING_X402);
  }
  const key = privateKey.startsWith("0x") ? privateKey : `0x${privateKey}`;
  const account = viem.privateKeyToAccount(key as `0x${string}`);

  const issuedAt = new Date().toISOString();
  const nonce = crypto.randomUUID().replace(/-/g, "");
  const message = buildWalletAuthMessage(account.address, issuedAt, nonce);
  const signature = await account.signMessage({ message });

  const baseUrl = (opts.baseUrl ?? X402_BALANCE_BASE_URL_DEFAULT).replace(/\/$/, "");
  const resp = await fetch(`${baseUrl}/x402/balance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address: account.address, issued_at: issuedAt, nonce, signature }),
  });
  if (!resp.ok) {
    throw new Error(`x402 balance check failed: ${resp.status} ${await resp.text()}`);
  }
  return (await resp.json()) as X402WalletBalance;
}

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
