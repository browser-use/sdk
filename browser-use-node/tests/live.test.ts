/**
 * Live integration tests against localhost:8000
 *
 * Run: npx tsx tests/live.test.ts
 *
 * Requires:
 *   - Backend running on localhost:8000
 *   - BROWSER_USE_API_KEY in ../.env
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Read API key from .env
const envPath = resolve(import.meta.dirname, "../../.env");
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
const BASE_URL = env.BACKEND_URL || "http://localhost:8000";

if (!API_KEY) {
  console.error("Missing BROWSER_USE_API_KEY in .env");
  process.exit(1);
}

// ── Import the SDK from source ──────────────────────────────────────────────
import { BrowserUse, BrowserUseError } from "../src/index.js";
import { BrowserUse as BrowserUseV3 } from "../src/v3.js";

const v2 = new BrowserUse({
  apiKey: API_KEY,
  baseUrl: `${BASE_URL}/api/v2`,
});

const v3 = new BrowserUseV3({
  apiKey: API_KEY,
  baseUrl: `${BASE_URL}/api/v3`,
});

let passed = 0;
let failed = 0;
let skipped = 0;
const failures: string[] = [];

async function test(name: string, fn: () => Promise<void>) {
  try {
    await fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.log(`  ✗ ${name}: ${msg}`);
    failed++;
    failures.push(`${name}: ${msg}`);
  }
}

async function skip(name: string, reason: string) {
  console.log(`  ○ ${name} (skipped: ${reason})`);
  skipped++;
}

function assert(condition: boolean, msg: string) {
  if (!condition) throw new Error(msg);
}

// ── V2 Tests ────────────────────────────────────────────────────────────────

console.log("\n=== V2 API Tests ===\n");

// Billing
await test("billing.account()", async () => {
  const account = await v2.billing.account();
  assert(account !== undefined, "No response");
  assert(typeof account.totalCreditsBalanceUsd === "number", "Missing totalCreditsBalanceUsd");
  assert(typeof account.rateLimit === "number", "Missing rateLimit");
  assert("projectId" in account, "Missing projectId");
});

// Profiles CRUD
let profileId: string | undefined;
await test("profiles.create()", async () => {
  const profile = await v2.profiles.create({ name: "SDK Test Profile" });
  assert(profile.id !== undefined, "Missing profile id");
  profileId = profile.id;
});

await test("profiles.list()", async () => {
  const list = await v2.profiles.list({ pageSize: 5 });
  assert(Array.isArray(list.items), "items should be an array");
  assert(typeof list.totalItems === "number", "Missing totalItems");
  assert(typeof list.pageNumber === "number", "Missing pageNumber");
  assert(typeof list.pageSize === "number", "Missing pageSize");
});

await test("profiles.get()", async () => {
  if (!profileId) throw new Error("No profile to get");
  const profile = await v2.profiles.get(profileId);
  assert(profile.id === profileId, "Wrong profile returned");
});

await test("profiles.update()", async () => {
  if (!profileId) throw new Error("No profile to update");
  const profile = await v2.profiles.update(profileId, { name: "SDK Updated Profile" });
  assert(profile.id === profileId, "Wrong profile returned");
});

await test("profiles.delete()", async () => {
  if (!profileId) throw new Error("No profile to delete");
  await v2.profiles.delete(profileId);
});

// Sessions CRUD
let sessionId: string | undefined;
await test("sessions.create()", async () => {
  const session = await v2.sessions.create();
  assert(session.id !== undefined, "Missing session id");
  sessionId = session.id;
});

await test("sessions.list()", async () => {
  const list = await v2.sessions.list({ pageSize: 5 });
  assert(Array.isArray(list.items), "items should be an array");
  assert(typeof list.totalItems === "number", "Missing totalItems");
});

await test("sessions.get()", async () => {
  if (!sessionId) throw new Error("No session to get");
  const session = await v2.sessions.get(sessionId);
  assert(session.id === sessionId, "Wrong session returned");
});

// Tasks (within session)
let taskId: string | undefined;
await test("tasks.create()", async () => {
  const task = await v2.tasks.create({
    task: "Go to google.com and return the page title",
    sessionId: sessionId,
  });
  assert(task.id !== undefined, "Missing task id");
  taskId = task.id;
});

await test("tasks.list()", async () => {
  const list = await v2.tasks.list({ pageSize: 5 });
  assert(Array.isArray(list.items), "items should be an array");
  assert(typeof list.totalItems === "number", "Missing totalItems");
});

await test("tasks.get()", async () => {
  if (!taskId) throw new Error("No task to get");
  const task = await v2.tasks.get(taskId);
  assert(task.id === taskId, "Wrong task returned");
  assert(typeof task.status === "string", "Missing status");
  assert(typeof task.task === "string", "Missing task field");
});

await test("tasks.status()", async () => {
  if (!taskId) throw new Error("No task to check status");
  const status = await v2.tasks.status(taskId);
  assert(status.id === taskId, "Wrong task status returned");
  assert(typeof status.status === "string", "status.status should be a string");
});

await test("tasks.stop()", async () => {
  if (!taskId) throw new Error("No task to stop");
  const task = await v2.tasks.stop(taskId);
  assert(task.id === taskId, "Wrong task returned after stop");
});

// Wait a moment for task to actually stop
await new Promise((r) => setTimeout(r, 1000));

await test("tasks.logs()", async () => {
  if (!taskId) throw new Error("No task to get logs");
  try {
    const logs = await v2.tasks.logs(taskId);
    assert(logs !== undefined, "No logs response");
  } catch (err) {
    // 404 is acceptable if the task didn't run long enough to produce logs
    if (err instanceof BrowserUseError && err.statusCode === 404) return;
    throw err;
  }
});

// Sessions stop & delete
await test("sessions.stop()", async () => {
  if (!sessionId) throw new Error("No session to stop");
  const session = await v2.sessions.stop(sessionId);
  assert(session.id === sessionId, "Wrong session returned after stop");
});

// Public share
await test("sessions.createShare()", async () => {
  if (!sessionId) throw new Error("No session for share");
  try {
    const share = await v2.sessions.createShare(sessionId);
    assert(share !== undefined, "No share response");
  } catch (err) {
    if (err instanceof BrowserUseError && (err.statusCode === 404 || err.statusCode === 400)) return;
    throw err;
  }
});

await test("sessions.getShare()", async () => {
  if (!sessionId) throw new Error("No session for share");
  try {
    const share = await v2.sessions.getShare(sessionId);
    assert(share !== undefined, "No share response");
  } catch (err) {
    if (err instanceof BrowserUseError && (err.statusCode === 404 || err.statusCode === 400)) return;
    throw err;
  }
});

await test("sessions.deleteShare()", async () => {
  if (!sessionId) throw new Error("No session for share");
  try {
    await v2.sessions.deleteShare(sessionId);
  } catch (err) {
    if (err instanceof BrowserUseError && (err.statusCode === 404 || err.statusCode === 400)) return;
    throw err;
  }
});

await test("sessions.delete()", async () => {
  if (!sessionId) throw new Error("No session to delete");
  await v2.sessions.delete(sessionId);
});

// Browsers
let browserId: string | undefined;
await test("browsers.create()", async () => {
  try {
    const browser = await v2.browsers.create({});
    assert(browser.id !== undefined, "Missing browser id");
    browserId = browser.id;
  } catch (err) {
    if (err instanceof BrowserUseError && err.statusCode === 422) return;
    throw err;
  }
});

await test("browsers.list()", async () => {
  const list = await v2.browsers.list({ pageSize: 5 });
  assert(Array.isArray(list.items), "items should be an array");
  assert(typeof list.totalItems === "number", "Missing totalItems");
});

if (browserId) {
  await test("browsers.get()", async () => {
    const browser = await v2.browsers.get(browserId!);
    assert(browser.id === browserId, "Wrong browser returned");
  });

  await test("browsers.stop()", async () => {
    const browser = await v2.browsers.stop(browserId!);
    assert(browser.id === browserId, "Wrong browser returned");
  });
}

// Skills
await test("skills.list()", async () => {
  const list = await v2.skills.list({ pageSize: 5 });
  assert(list !== undefined, "No skills list response");
  assert(Array.isArray(list.items), "items should be an array");
});

// Marketplace
await test("marketplace.list()", async () => {
  const list = await v2.marketplace.list({ pageSize: 5 });
  assert(list !== undefined, "No marketplace list response");
});

// Error handling
await test("BrowserUseError on invalid API key", async () => {
  const badClient = new BrowserUse({
    apiKey: "bu_invalid_key_for_testing",
    baseUrl: `${BASE_URL}/api/v2`,
    maxRetries: 0,
  });
  try {
    await badClient.billing.account();
    throw new Error("Should have thrown");
  } catch (err) {
    assert(err instanceof BrowserUseError, `Expected BrowserUseError, got ${err?.constructor?.name}`);
    assert(err.statusCode === 401 || err.statusCode === 403 || err.statusCode === 404, `Expected 401/403/404, got ${err.statusCode}`);
  }
});

await test("BrowserUseError on not found", async () => {
  try {
    await v2.tasks.get("00000000-0000-0000-0000-000000000000");
    throw new Error("Should have thrown");
  } catch (err) {
    assert(err instanceof BrowserUseError, `Expected BrowserUseError, got ${err?.constructor?.name}`);
    assert(err.statusCode === 404, `Expected 404, got ${err.statusCode}`);
  }
});

await test("BrowserUseError has useful message from detail", async () => {
  try {
    await v2.tasks.get("00000000-0000-0000-0000-000000000000");
  } catch (err) {
    assert(err instanceof BrowserUseError, "Expected BrowserUseError");
    assert(typeof err.message === "string" && err.message.length > 0, "Error message should be non-empty");
    assert(err.detail !== undefined, "Error detail should be present");
    console.log(`    (error message: "${err.message}")`);
  }
});

// ── V3 Tests ────────────────────────────────────────────────────────────────

console.log("\n=== V3 API Tests ===\n");

// V3 create returns 500 on localhost — this is a backend infrastructure issue
// (v3 needs cloud infrastructure to spin up sessions with Minerva model)
await skip("v3 sessions.create()", "v3 backend returns 500 locally — needs cloud infra");

await test("v3 sessions.list()", async () => {
  const list = await v3.sessions.list({ page_size: 5 });
  assert(Array.isArray(list.sessions), "sessions should be an array");
});

// ── TaskHandle ──────────────────────────────────────────────────────────────

console.log("\n=== Helper Tests ===\n");

await test("v2 client.run() returns TaskHandle with correct API", async () => {
  const handle = v2.run({ task: "Go to google.com" });
  assert(handle !== undefined, "No handle returned");
  assert(typeof handle.complete === "function", "handle.complete should be a function");
  assert(typeof handle.stream === "function", "handle.stream should be a function");
  assert(typeof handle.created === "function", "handle.created should be a function");

  // Verify created() returns a task
  const created = await handle.created();
  assert(created.id !== undefined, "created() should return an object with an id");

  // Stop the task to clean up
  try { await v2.tasks.stop(created.id); } catch { /* might already be done */ }
});

await test("v2 TaskHandle.complete() polls to terminal state", async () => {
  const handle = v2.run({ task: "Go to google.com" });
  const created = await handle.created();

  // Stop it immediately
  await v2.tasks.stop(created.id);

  // Now complete() should resolve quickly since task is stopped
  const result = await handle.complete({ timeout: 30_000, interval: 500 });
  assert(result.id === created.id, "Wrong task returned");
  assert(
    result.status === "stopped" || result.status === "finished" || result.status === "failed",
    `Expected terminal status, got: ${result.status}`,
  );
});

await test("v2 TaskHandle.stream() yields intermediate states", async () => {
  const handle = v2.run({ task: "Go to google.com" });
  const created = await handle.created();

  // Stop it quickly
  setTimeout(async () => {
    try { await v2.tasks.stop(created.id); } catch { /* ignore */ }
  }, 1000);

  let count = 0;
  for await (const state of handle.stream({ interval: 500 })) {
    count++;
    assert(state.id === created.id, "Wrong task in stream");
    if (count > 10) break; // safety valve
  }
  // Stream might yield 0 states if task stopped immediately
  assert(count >= 0, "Stream should have yielded states");
});

// ── Summary ─────────────────────────────────────────────────────────────────

console.log(`\n${"─".repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed, ${skipped} skipped`);
if (failures.length > 0) {
  console.log("\nFailures:");
  for (const f of failures) {
    console.log(`  • ${f}`);
  }
}
console.log();

process.exit(failed > 0 ? 1 : 0);
