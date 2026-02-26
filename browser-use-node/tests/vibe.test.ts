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
  if (method === "patch" && path === "/tasks/{task_id}") return { resource: "tasks", method: "stop" }; // also stopTaskAndSession (action variant)
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
  if (method === "post" && path === "/sessions/{session_id}/purge") return { resource: "sessions", method: "purge" };

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
  if (method === "delete" && path === "/sessions/{session_id}") return { resource: "sessions", method: "delete" };
  if (method === "post" && path === "/sessions/{session_id}/stop") return { resource: "sessions", method: "stop" };
  if (method === "get" && path === "/sessions/{session_id}/files") return { resource: "sessions", method: "files" };
  if (method === "post" && path === "/sessions/{session_id}/files/upload") return { resource: "sessions", method: "uploadFiles" };

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

// ── Spec drift detection ────────────────────────────────────────────────────

describe("spec drift", () => {
  const spec = loadSpec("v2");
  const resourceDir = resolve(SDK_ROOT, "src/v2/resources");

  /** Read a resource source file. */
  function readResource(name: string): string {
    return readFileSync(resolve(resourceDir, `${name}.ts`), "utf-8");
  }

  /** Get query parameter names from the spec for an endpoint. */
  function getQueryParams(method: string, path: string): string[] {
    const op = (spec.paths as any)?.[path]?.[method];
    if (!op?.parameters) return [];
    return op.parameters
      .filter((p: any) => p.in === "query")
      .map((p: any) => p.name as string);
  }

  /** Get the response schema name ($ref) for a success response. */
  function getResponseSchemaName(method: string, path: string): string | null {
    const op = (spec.paths as any)?.[path]?.[method];
    if (!op) return null;
    for (const status of ["200", "201"]) {
      const ref =
        op.responses?.[status]?.content?.["application/json"]?.schema?.$ref;
      if (ref) return ref.split("/").pop()!;
    }
    return null;
  }

  /** Resolve $ref to a schema object. */
  function resolveRef(ref: string): any {
    const parts = ref.replace("#/", "").split("/");
    let obj: any = spec;
    for (const part of parts) obj = obj[part];
    return obj;
  }

  /** Get enum values for the 'action' field in a request body. */
  function getActionEnum(method: string, path: string): string[] {
    const op = (spec.paths as any)?.[path]?.[method];
    if (!op) return [];
    let schema = op.requestBody?.content?.["application/json"]?.schema ?? {};
    if (schema.$ref) schema = resolveRef(schema.$ref);
    let action = schema.properties?.action ?? {};
    if (action.$ref) action = resolveRef(action.$ref);
    return action.enum ?? [];
  }

  const endpoints = extractEndpoints(spec);

  // Cache resource file contents
  const resourceSources = new Map<string, string>();
  for (const name of [
    "tasks", "sessions", "browsers", "skills", "marketplace",
    "billing", "files", "profiles",
  ]) {
    try {
      resourceSources.set(name, readResource(name));
    } catch {
      // file may not exist (e.g. billing)
    }
  }

  it("should have all spec query params in SDK resource files", () => {
    const missing: string[] = [];

    for (const ep of endpoints) {
      const mapping = v2EndpointToSdkMethod(ep);
      if (!mapping) continue;

      const specParams = getQueryParams(ep.method, ep.path);
      if (specParams.length === 0) continue;

      const source = resourceSources.get(mapping.resource);
      if (!source) continue;

      for (const param of specParams) {
        if (!source.includes(param)) {
          missing.push(
            `${mapping.resource}.${mapping.method}() missing param '${param}' ` +
              `(from ${ep.method.toUpperCase()} ${ep.path})`,
          );
        }
      }
    }

    expect(missing).toEqual([]);
  });

  it("should use correct response types from spec", () => {
    const mismatches: string[] = [];

    for (const ep of endpoints) {
      const mapping = v2EndpointToSdkMethod(ep);
      if (!mapping) continue;

      const specType = getResponseSchemaName(ep.method, ep.path);
      if (!specType) continue;

      const source = resourceSources.get(mapping.resource);
      if (!source) continue;

      // Match: methodName(...): Promise<TypeName> {
      const regex = new RegExp(
        `\\b${mapping.method}\\b[^{]*?Promise<(\\w+)>`,
      );
      const match = source.match(regex);
      if (!match) continue;

      const sdkType = match[1];
      if (sdkType !== specType) {
        mismatches.push(
          `${mapping.resource}.${mapping.method}() returns '${sdkType}' ` +
            `but spec says '${specType}' (${ep.method.toUpperCase()} ${ep.path})`,
        );
      }
    }

    expect(mismatches).toEqual([]);
  });

  it("should have SDK methods for all task action variants", () => {
    const actions = getActionEnum("patch", "/tasks/{task_id}");
    expect(actions.length).toBeGreaterThan(0);

    const actionToMethod: Record<string, string> = {
      stop: "stop",
      stop_task_and_session: "stopTaskAndSession",
    };

    const client = new BrowserUseV2({ apiKey: "test" });
    const missing: string[] = [];

    for (const action of actions) {
      const methodName = actionToMethod[action];
      if (!methodName) {
        missing.push(`No SDK method mapping for action '${action}'`);
        continue;
      }
      if (typeof (client.tasks as any)[methodName] !== "function") {
        missing.push(`tasks.${methodName}() missing for action '${action}'`);
      }
    }

    expect(missing).toEqual([]);
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
