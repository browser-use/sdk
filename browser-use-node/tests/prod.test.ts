/**
 * Production smoke tests — verify the SDK works against the real API.
 *
 * Run: npx tsx tests/prod.test.ts
 *
 * Uses .env.prod (or .env as fallback) for BROWSER_USE_API_KEY.
 * Does NOT override baseUrl — hits the default prod endpoint.
 */

import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

// Load .env.prod (fallback to .env)
const prodEnvPath = resolve(import.meta.dirname, "../../.env.prod");
const fallbackEnvPath = resolve(import.meta.dirname, "../../.env");
const envPath = existsSync(prodEnvPath) ? prodEnvPath : fallbackEnvPath;
const env = Object.fromEntries(
  readFileSync(envPath, "utf-8")
    .split("\n")
    .filter((l) => l && !l.startsWith("#"))
    .map((l) => {
      const eq = l.indexOf("=");
      return [l.slice(0, eq).trim(), l.slice(eq + 1).trim()];
    }),
);

const API_KEY = env.BROWSER_USE_API_KEY;
if (!API_KEY) {
  console.error("Missing BROWSER_USE_API_KEY in .env.prod");
  process.exit(1);
}

import { BrowserUse, BrowserUseError } from "../src/index.js";
import { z } from "zod";

// No baseUrl override — uses default prod URL
const client = new BrowserUse({ apiKey: API_KEY });

let passed = 0;
let failed = 0;
const failures: string[] = [];
const cleanups: (() => Promise<void>)[] = [];

async function test(name: string, fn: () => Promise<void>) {
  try {
    await fn();
    console.log(`  \u2713 ${name}`);
    passed++;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.log(`  \u2717 ${name}: ${msg}`);
    failed++;
    failures.push(`${name}: ${msg}`);
  }
}

function assert(condition: boolean, msg: string) {
  if (!condition) throw new Error(msg);
}

// ── Tests ──────────────────────────────────────────────────────────────────

console.log("\n=== Prod Smoke Tests ===\n");

// 1. Auth / Billing (cheapest call — verifies API key works)
await test("billing.account() returns valid data", async () => {
  const account = await client.billing.account();
  assert(typeof account.totalCreditsBalanceUsd === "number", "Missing credits balance");
  assert(typeof account.rateLimit === "number", "Missing rate limit");
  assert("projectId" in account, "Missing projectId");
});

// 2. Profile CRUD (no sessions consumed)
let profileId: string | undefined;
await test("profiles CRUD lifecycle", async () => {
  // Create
  const profile = await client.profiles.create({ name: "SDK Prod Test" });
  assert(profile.id !== undefined, "No profile id");
  profileId = profile.id;
  cleanups.push(async () => {
    try { await client.profiles.delete(profileId!); } catch {}
  });

  // Get
  const got = await client.profiles.get(profileId);
  assert(got.id === profileId, "Wrong profile");

  // Update
  const updated = await client.profiles.update(profileId, { name: "SDK Prod Updated" });
  assert(updated.id === profileId, "Wrong profile after update");

  // List
  const list = await client.profiles.list({ pageSize: 5 });
  assert(Array.isArray(list.items), "items should be array");

  // Delete
  await client.profiles.delete(profileId);
  profileId = undefined;
  cleanups.pop();
});

// 3. Task lifecycle — await run() directly, verify TaskResult
await test("await run() returns TaskResult with output and metadata", async () => {
  const run = client.run("Return the exact text: hello world");
  const result = await run;
  assert(typeof result.output === "string", `Expected string output, got ${typeof result.output}`);
  assert(result.output.length > 0, "Output should not be empty");
  assert(typeof result.id === "string", "result.id should be a string");
  assert(Array.isArray(result.steps), "result.steps should be an array");
  assert(
    result.status === "finished" || result.status === "stopped",
    `Expected terminal status, got ${result.status}`,
  );

  // .result on the run handle should match
  assert(run.result !== null, "run.result should be set after await");
  assert(run.result!.id === result.id, "run.result should match awaited result");
});

// 4. Structured output — await run() with schema, verify typed result
await test("structured output parses correctly", async () => {
  const MathResult = z.object({
    answer: z.number(),
    explanation: z.string(),
  });

  const result = await client.run(
    "What is 7 * 8? Return the answer and a one-sentence explanation.",
    { schema: MathResult },
  );

  assert(result.output !== null, "output should not be null");
  assert(typeof result.output.answer === "number", `answer should be number, got ${typeof result.output.answer}`);
  assert(typeof result.output.explanation === "string", `explanation should be string, got ${typeof result.output.explanation}`);
  assert(typeof result.id === "string", "result.id should be a string");
});

// 5. Streaming — for-await yields step-by-step progress
await test("for-await yields TaskStepView steps", async () => {
  const run = client.run("Return the exact text: ping");
  let count = 0;
  for await (const step of run) {
    assert(typeof step.number === "number", "step.number should be number");
    assert(typeof step.nextGoal === "string", "step.nextGoal should be string");
    assert(typeof step.url === "string", "step.url should be string");
    count++;
    if (count > 50) break; // safety valve
  }
  assert(count >= 1, "Should yield at least 1 step");

  // result should be a TaskResult after iteration
  assert(run.result !== null, "result should be set after iteration");
  assert(typeof run.result!.id === "string", "result.id should be a string");
  assert(typeof run.result!.output === "string", "result.output should be a string");
});

// 6. Session lifecycle
await test("session create + stop + delete", async () => {
  const session = await client.sessions.create();
  assert(session.id !== undefined, "No session id");
  cleanups.push(async () => {
    try { await client.sessions.stop(session.id); } catch {}
    try { await client.sessions.delete(session.id); } catch {}
  });

  // List
  const list = await client.sessions.list({ pageSize: 5 });
  assert(Array.isArray(list.items), "items should be array");

  // Get
  const got = await client.sessions.get(session.id);
  assert(got.id === session.id, "Wrong session");

  // Stop + delete
  await client.sessions.stop(session.id);
  await client.sessions.delete(session.id);
  cleanups.pop();
});

// 7. Error handling
await test("404 on invalid task id", async () => {
  try {
    await client.tasks.get("00000000-0000-0000-0000-000000000000");
    throw new Error("Should have thrown");
  } catch (err) {
    assert(err instanceof BrowserUseError, `Expected BrowserUseError, got ${err?.constructor?.name}`);
    assert(err.statusCode === 404, `Expected 404, got ${err.statusCode}`);
  }
});

await test("401/403 on invalid API key", async () => {
  const bad = new BrowserUse({ apiKey: "bu_invalid_key", maxRetries: 0 });
  try {
    await bad.billing.account();
    throw new Error("Should have thrown");
  } catch (err) {
    assert(err instanceof BrowserUseError, `Expected BrowserUseError, got ${err?.constructor?.name}`);
    assert(
      err.statusCode === 401 || err.statusCode === 403 || err.statusCode === 404,
      `Expected 401/403/404, got ${err.statusCode}`,
    );
  }
});

// ── Cleanup + Summary ──────────────────────────────────────────────────────

for (const cleanup of cleanups) {
  try { await cleanup(); } catch {}
}

console.log(`\n${"─".repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
if (failures.length > 0) {
  console.log("\nFailures:");
  for (const f of failures) {
    console.log(`  \u2022 ${f}`);
  }
}
console.log();

process.exit(failed > 0 ? 1 : 0);
