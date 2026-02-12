import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// ── Import SDK classes ─────────────────────────────────────────────────────

import { BrowserUse as BrowserUseV2 } from "../src/v2/client.js";
import { BrowserUse as BrowserUseV3 } from "../src/v3/client.js";

// ── Helpers ────────────────────────────────────────────────────────────────

const __dirname = dirname(fileURLToPath(import.meta.url));
const SDK_ROOT = resolve(__dirname, "..");
const REPO_ROOT = resolve(SDK_ROOT, "..");

/** Read CLOUD_REPO_PATH from .env */
function getCloudRepoPath(): string {
  const envPath = resolve(REPO_ROOT, ".env");
  const envContent = readFileSync(envPath, "utf-8");
  for (const line of envContent.split("\n")) {
    const trimmed = line.trim();
    if (trimmed.startsWith("CLOUD_REPO_PATH=") && !trimmed.startsWith("#")) {
      return trimmed.slice("CLOUD_REPO_PATH=".length).trim();
    }
  }
  throw new Error("CLOUD_REPO_PATH not found in .env");
}

const CLOUD_REPO = getCloudRepoPath();

function loadSpec(version: "v2" | "v3") {
  const specPath = resolve(CLOUD_REPO, "backend", "spec", "api", version, "openapi.json");
  const raw = readFileSync(specPath, "utf-8");
  return JSON.parse(raw);
}

/** Extract every {method, path} from an OpenAPI spec. */
function extractEndpoints(spec: any): Array<{ method: string; path: string; operationId: string }> {
  const endpoints: Array<{ method: string; path: string; operationId: string }> = [];
  for (const [path, methods] of Object.entries(spec.paths ?? {})) {
    for (const [method, op] of Object.entries(methods as Record<string, any>)) {
      if (["get", "post", "patch", "put", "delete"].includes(method) && op.operationId) {
        endpoints.push({ method, path, operationId: op.operationId });
      }
    }
  }
  return endpoints;
}

// ── Map from OpenAPI endpoint to SDK method ────────────────────────────────

function v2EndpointToSdkMethod(
  ep: { method: string; path: string },
): { resource: string; method: string } | null {
  const { method, path } = ep;

  // Billing
  if (method === "get" && path === "/billing/account") return { resource: "billing", method: "account" };

  // Tasks
  if (method === "post" && path === "/tasks") return { resource: "tasks", method: "create" };
  if (method === "get" && path === "/tasks") return { resource: "tasks", method: "list" };
  if (method === "get" && path === "/tasks/{task_id}") return { resource: "tasks", method: "get" };
  if (method === "patch" && path === "/tasks/{task_id}") return { resource: "tasks", method: "stop" };
  if (method === "get" && path === "/tasks/{task_id}/status") return { resource: "tasks", method: "status" };
  if (method === "get" && path === "/tasks/{task_id}/logs") return { resource: "tasks", method: "logs" };

  // Sessions
  if (method === "post" && path === "/sessions") return { resource: "sessions", method: "create" };
  if (method === "get" && path === "/sessions") return { resource: "sessions", method: "list" };
  if (method === "get" && path === "/sessions/{session_id}") return { resource: "sessions", method: "get" };
  if (method === "patch" && path === "/sessions/{session_id}") return { resource: "sessions", method: "stop" };
  if (method === "delete" && path === "/sessions/{session_id}") return { resource: "sessions", method: "delete" };
  if (method === "get" && path === "/sessions/{session_id}/public-share") return { resource: "sessions", method: "getShare" };
  if (method === "post" && path === "/sessions/{session_id}/public-share") return { resource: "sessions", method: "createShare" };
  if (method === "delete" && path === "/sessions/{session_id}/public-share") return { resource: "sessions", method: "deleteShare" };

  // Files
  if (method === "post" && path === "/files/sessions/{session_id}/presigned-url") return { resource: "files", method: "sessionUrl" };
  if (method === "post" && path === "/files/browsers/{session_id}/presigned-url") return { resource: "files", method: "browserUrl" };
  if (method === "get" && path === "/files/tasks/{task_id}/output-files/{file_id}") return { resource: "files", method: "taskOutput" };

  // Profiles
  if (method === "post" && path === "/profiles") return { resource: "profiles", method: "create" };
  if (method === "get" && path === "/profiles") return { resource: "profiles", method: "list" };
  if (method === "get" && path === "/profiles/{profile_id}") return { resource: "profiles", method: "get" };
  if (method === "patch" && path === "/profiles/{profile_id}") return { resource: "profiles", method: "update" };
  if (method === "delete" && path === "/profiles/{profile_id}") return { resource: "profiles", method: "delete" };

  // Browsers
  if (method === "post" && path === "/browsers") return { resource: "browsers", method: "create" };
  if (method === "get" && path === "/browsers") return { resource: "browsers", method: "list" };
  if (method === "get" && path === "/browsers/{session_id}") return { resource: "browsers", method: "get" };
  if (method === "patch" && path === "/browsers/{session_id}") return { resource: "browsers", method: "stop" };

  // Skills
  if (method === "post" && path === "/skills") return { resource: "skills", method: "create" };
  if (method === "get" && path === "/skills") return { resource: "skills", method: "list" };
  if (method === "get" && path === "/skills/{skill_id}") return { resource: "skills", method: "get" };
  if (method === "delete" && path === "/skills/{skill_id}") return { resource: "skills", method: "delete" };
  if (method === "patch" && path === "/skills/{skill_id}") return { resource: "skills", method: "update" };
  if (method === "post" && path === "/skills/{skill_id}/cancel") return { resource: "skills", method: "cancel" };
  if (method === "post" && path === "/skills/{skill_id}/execute") return { resource: "skills", method: "execute" };
  if (method === "post" && path === "/skills/{skill_id}/refine") return { resource: "skills", method: "refine" };
  if (method === "post" && path === "/skills/{skill_id}/rollback") return { resource: "skills", method: "rollback" };
  if (method === "get" && path === "/skills/{skill_id}/executions") return { resource: "skills", method: "executions" };
  if (method === "get" && path === "/skills/{skill_id}/executions/{execution_id}/output") return { resource: "skills", method: "executionOutput" };

  // Marketplace
  if (method === "get" && path === "/marketplace/skills") return { resource: "marketplace", method: "list" };
  if (method === "get" && path === "/marketplace/skills/{skill_slug}") return { resource: "marketplace", method: "get" };
  if (method === "post" && path === "/marketplace/skills/{skill_id}/clone") return { resource: "marketplace", method: "clone" };
  if (method === "post" && path === "/marketplace/skills/{skill_id}/execute") return { resource: "marketplace", method: "execute" };

  return null;
}

function v3EndpointToSdkMethod(
  ep: { method: string; path: string },
): { resource: string; method: string } | null {
  const { method, path } = ep;

  if (method === "post" && path === "/sessions") return { resource: "sessions", method: "create" };
  if (method === "get" && path === "/sessions") return { resource: "sessions", method: "list" };
  if (method === "get" && path === "/sessions/{session_id}") return { resource: "sessions", method: "get" };
  if (method === "post" && path === "/sessions/{session_id}/stop") return { resource: "sessions", method: "stop" };
  if (method === "get" && path === "/sessions/{session_id}/files") return { resource: "sessions", method: "files" };

  return null;
}

// ── Tests ──────────────────────────────────────────────────────────────────

describe("V2 SDK coverage", () => {
  const spec = loadSpec("v2");
  const endpoints = extractEndpoints(spec);

  const client = new BrowserUseV2({ apiKey: "test" });

  it("should map every v2 endpoint to a known SDK method", () => {
    const unmapped: string[] = [];
    for (const ep of endpoints) {
      const mapping = v2EndpointToSdkMethod(ep);
      if (!mapping) {
        unmapped.push(`${ep.method.toUpperCase()} ${ep.path}`);
      }
    }
    expect(unmapped).toEqual([]);
  });

  it.each(endpoints)("$method $path -> SDK method exists", (ep) => {
    const mapping = v2EndpointToSdkMethod(ep);
    if (!mapping) return;

    const resource = (client as any)[mapping.resource];
    expect(resource).toBeDefined();
    expect(typeof resource[mapping.method]).toBe("function");
  });

  it("should have run() helper on client", () => {
    expect(typeof client.run).toBe("function");
  });
});

describe("V3 SDK coverage", () => {
  const spec = loadSpec("v3");
  const endpoints = extractEndpoints(spec);

  const client = new BrowserUseV3({ apiKey: "test" });

  it("should map every v3 endpoint to a known SDK method", () => {
    const unmapped: string[] = [];
    for (const ep of endpoints) {
      const mapping = v3EndpointToSdkMethod(ep);
      if (!mapping) {
        unmapped.push(`${ep.method.toUpperCase()} ${ep.path}`);
      }
    }
    expect(unmapped).toEqual([]);
  });

  it.each(endpoints)("$method $path -> SDK method exists", (ep) => {
    const mapping = v3EndpointToSdkMethod(ep);
    if (!mapping) return;

    const resource = (client as any)[mapping.resource];
    expect(resource).toBeDefined();
    expect(typeof resource[mapping.method]).toBe("function");
  });

  it("should have run() helper on client", () => {
    expect(typeof client.run).toBe("function");
  });
});
