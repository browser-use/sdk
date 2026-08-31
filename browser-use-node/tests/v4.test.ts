import { mkdtempSync, readFileSync, readdirSync, symlinkSync, writeFileSync } from "fs";
import { open as openFile } from "fs/promises";
import { tmpdir } from "os";
import { join } from "path";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Browsers } from "../src/v4/resources/browsers.js";
import { Runs } from "../src/v4/resources/runs.js";
import { Sessions } from "../src/v4/resources/sessions.js";
import { Workspaces } from "../src/v4/resources/workspaces.js";

const RUN_ID = "00000000-0000-0000-0000-000000000001";
const SESSION_ID = "00000000-0000-0000-0000-000000000002";
const WORKSPACE_ID = "00000000-0000-0000-0000-000000000010";

function runSummary(status: string) {
  return {
    id: RUN_ID,
    task: "Find pricing",
    title: null,
    model: "minimax-m3",
    contextLimit: 200000,
    status,
    result: status === "completed" ? "done" : null,
    error: null,
    sessionId: SESSION_ID,
    workspaceId: null,
    totalInputTokens: 1,
    totalOutputTokens: 1,
    totalCostUsd: "0.01",
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-01T00:00:00Z",
  };
}

describe("v4 browsers", () => {
  it("stops a browser session", async () => {
    const stopped = {
      id: SESSION_ID,
      status: "stopped",
      timeoutAt: "2026-01-01T01:00:00Z",
      startedAt: "2026-01-01T00:00:00Z",
      proxyUsedMb: "0",
      proxyCost: "0",
      browserCost: "0.01",
      metadata: {},
    };
    const http = { patch: vi.fn(async () => stopped) };
    const browsers = new Browsers(http as any);

    const browser = await browsers.stop(SESSION_ID);

    expect(http.patch).toHaveBeenCalledWith(`/browsers/${SESSION_ID}`, {
      action: "stop",
    });
    expect(browser.status).toBe("stopped");
  });
});

describe("v4 runs.waitForCompletion", () => {
  it("polls status until terminal, then fetches the full run once", async () => {
    const statuses = ["queued", "running", "completed"];
    let statusCalls = 0;
    let getCalls = 0;
    const http = {
      get: vi.fn(async (path: string) => {
        if (path === `/runs/${RUN_ID}/status`) {
          return { status: statuses[statusCalls++] };
        }
        if (path === `/runs/${RUN_ID}`) {
          getCalls++;
          return runSummary("completed");
        }
        throw new Error(`Unexpected GET ${path}`);
      }),
    };
    const runs = new Runs(http as any);

    const run = await runs.waitForCompletion(RUN_ID, { interval: 1 });

    expect(statusCalls).toBe(3);
    expect(getCalls).toBe(1);
    expect(run.status).toBe("completed");
    expect(run.result).toBe("done");
  });

  it("stops immediately on failed status", async () => {
    const http = {
      get: vi.fn(async (path: string) =>
        path.endsWith("/status") ? { status: "failed" } : runSummary("failed"),
      ),
    };
    const runs = new Runs(http as any);

    const run = await runs.waitForCompletion(RUN_ID, { interval: 1 });

    expect(run.status).toBe("failed");
  });

  it("throws when the timeout elapses before a terminal status", async () => {
    const http = {
      get: vi.fn(async () => ({ status: "running" })),
    };
    const runs = new Runs(http as any);

    await expect(
      runs.waitForCompletion(RUN_ID, { timeout: 10, interval: 1 }),
    ).rejects.toThrow(/did not complete/);
  });
});

describe("v4 runs.waitForEvent", () => {
  it("returns browser.ready before any terminal-status wait", async () => {
    const http = { get: vi.fn(async (_path: string, query?: Record<string, unknown>) =>
      query?.after === 1
        ? { events: [{ runId: RUN_ID, id: 2, ts: "2026-01-01T00:00:01Z", type: "browser.ready", data: { live_view_url: "https://live" } }], nextAfter: 2, hasMore: false }
        : { events: [{ runId: RUN_ID, id: 1, ts: "2026-01-01T00:00:00Z", type: "run.created", data: {} }], nextAfter: 1, hasMore: true }) };
    const runs = new Runs(http as any);
    const event = await runs.waitForEvent(RUN_ID, "browser.ready", { interval: 0 });
    expect(event.data.live_view_url).toBe("https://live");
    expect(http.get).toHaveBeenLastCalledWith(`/runs/${RUN_ID}/events`, { after: 1, limit: 100 });
  });

  it("fails immediately when the run ends before the requested event", async () => {
    const http = {
      get: vi.fn(async () => ({
        events: [{ runId: RUN_ID, id: 1, ts: "2026-01-01T00:00:00Z", type: "run.dispatch_failed", data: {} }],
        nextAfter: 1,
        hasMore: false,
      })),
    };
    const runs = new Runs(http as any);
    await expect(runs.waitForEvent(RUN_ID, "browser.ready")).rejects.toThrow(
      /emitted run\.dispatch_failed before browser\.ready/,
    );
    expect(http.get).toHaveBeenCalledTimes(1);
  });
});

describe("v4 runs pagination + events", () => {
  it("passes agentmail and secret bindings through on create", async () => {
    const http = {
      post: vi.fn(async () => ({
        id: RUN_ID,
        status: "queued",
        model: "gpt-5.6-luna",
        sessionId: SESSION_ID,
        workspaceId: WORKSPACE_ID,
        eventsUrl: `https://api.browser-use.com/api/v4/runs/${RUN_ID}/events`,
      })),
    };
    const runs = new Runs(http as any);

    await runs.create({
      task: "Sign in",
      agentmail: true,
      secretBindings: [
        {
          alias: "github_password",
          source: { type: "inline", value: "not-masked" },
          allowedDomains: ["github.com"],
        },
      ],
    });

    expect(http.post).toHaveBeenCalledWith("/runs", {
      task: "Sign in",
      agentmail: true,
      secretBindings: [
        {
          alias: "github_password",
          source: { type: "inline", value: "not-masked" },
          allowedDomains: ["github.com"],
        },
      ],
    });
  });

  it("passes cursor pagination params on list", async () => {
    const http = {
      get: vi.fn(async () => ({ runs: [], nextCursor: null, hasMore: false })),
    };
    const runs = new Runs(http as any);

    await runs.list({ sessionId: SESSION_ID, cursor: "abc", limit: 5 });

    expect(http.get).toHaveBeenCalledWith("/runs", {
      sessionId: SESSION_ID,
      cursor: "abc",
      limit: 5,
    });
  });

  it("fetches events incrementally via after", async () => {
    const pages: Record<string, unknown> = {
      first: {
        events: [
          { runId: RUN_ID, id: 1, ts: "2026-01-01T00:00:00Z", type: "step", data: {} },
          { runId: RUN_ID, id: 2, ts: "2026-01-01T00:00:01Z", type: "step", data: {} },
        ],
        nextAfter: 2,
        hasMore: true,
      },
      second: {
        events: [
          { runId: RUN_ID, id: 3, ts: "2026-01-01T00:00:02Z", type: "done", data: {} },
        ],
        nextAfter: 3,
        hasMore: false,
      },
    };
    const http = {
      get: vi.fn(async (_path: string, query?: Record<string, unknown>) =>
        query?.after === 2 ? pages.second : pages.first,
      ),
    };
    const runs = new Runs(http as any);

    const first = await runs.events(RUN_ID, { limit: 2 });
    expect(first.nextAfter).toBe(2);
    expect(first.hasMore).toBe(true);

    const second = await runs.events(RUN_ID, { after: first.nextAfter, limit: 2 });
    expect(http.get).toHaveBeenLastCalledWith(`/runs/${RUN_ID}/events`, { after: 2, limit: 2 });
    expect(second.hasMore).toBe(false);
    expect(second.events[0].id).toBe(3);
  });
});

describe("v4 sessions queue", () => {
  const queuedMessage = {
    id: 7,
    sessionId: SESSION_ID,
    runId: null,
    mode: "queue",
    status: "pending",
    text: "also check the careers page",
    createdAt: "2026-01-01T00:00:00Z",
  };

  it("sends a message to the queue", async () => {
    const http = {
      post: vi.fn(async () => queuedMessage),
    };
    const sessions = new Sessions(http as any);

    const msg = await sessions.sendMessage(SESSION_ID, {
      text: "also check the careers page",
      interrupt: true,
    });

    expect(http.post).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/queue`, {
      text: "also check the careers page",
      interrupt: true,
    });
    expect(msg.status).toBe("pending");
  });

  it("lists pending queued messages", async () => {
    const http = {
      get: vi.fn(async () => ({ queue: [queuedMessage] })),
    };
    const sessions = new Sessions(http as any);

    const resp = await sessions.queue(SESSION_ID);

    expect(http.get).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/queue`);
    expect(resp.queue).toHaveLength(1);
  });

  it("gets one queued message", async () => {
    const http = { get: vi.fn(async () => queuedMessage) };
    const sessions = new Sessions(http as any);

    const msg = await sessions.getMessage(SESSION_ID, 7);

    expect(http.get).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/queue/7`);
    expect(msg.id).toBe(7);
  });

  it("purges a ZDR session", async () => {
    const http = { post: vi.fn(async () => undefined) };
    const sessions = new Sessions(http as any);

    await sessions.purge(SESSION_ID);

    expect(http.post).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/purge`);
  });

  it("removes a queued message", async () => {
    const http = {
      delete: vi.fn(async () => ({ ...queuedMessage, status: "cancelled" })),
    };
    const sessions = new Sessions(http as any);

    const msg = await sessions.removeMessage(SESSION_ID, 7);

    expect(http.delete).toHaveBeenCalledWith(`/sessions/${SESSION_ID}/queue/7`);
    expect(msg.status).toBe("cancelled");
  });

  it("passes cursor pagination params on list", async () => {
    const http = {
      get: vi.fn(async () => ({ sessions: [], nextCursor: null, hasMore: false })),
    };
    const sessions = new Sessions(http as any);

    await sessions.list({ cursor: "xyz", limit: 10 });

    expect(http.get).toHaveBeenCalledWith("/sessions", { cursor: "xyz", limit: 10 });
  });
});

describe("v4 workspaces", () => {
  const workspaceInfo = {
    id: WORKSPACE_ID,
    name: "my workspace",
    archived: false,
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-01T00:00:00Z",
  };

  it("creates a workspace", async () => {
    const http = { post: vi.fn(async () => workspaceInfo) };
    const workspaces = new Workspaces(http as any);

    const ws = await workspaces.create({ name: "my workspace" });

    expect(http.post).toHaveBeenCalledWith("/workspaces", { name: "my workspace" });
    expect(ws.id).toBe(WORKSPACE_ID);
  });

  it("defaults create body to {} when omitted", async () => {
    const http = { post: vi.fn(async () => workspaceInfo) };
    const workspaces = new Workspaces(http as any);

    await workspaces.create();

    expect(http.post).toHaveBeenCalledWith("/workspaces", {});
  });

  it("updates, sizes, deletes, and removes workspace files", async () => {
    const http = {
      patch: vi.fn(async () => ({ ...workspaceInfo, name: null })),
      get: vi.fn(async () => ({ usedBytes: 10, maxBytes: 100 })),
      delete: vi.fn(async () => undefined),
    };
    const workspaces = new Workspaces(http as any);

    const updated = await workspaces.update(WORKSPACE_ID, { name: null });
    const size = await workspaces.size(WORKSPACE_ID);
    await workspaces.deleteFile(WORKSPACE_ID, "uploads/data.csv");
    await workspaces.delete(WORKSPACE_ID);

    expect(http.patch).toHaveBeenCalledWith(`/workspaces/${WORKSPACE_ID}`, { name: null });
    expect(http.get).toHaveBeenCalledWith(`/workspaces/${WORKSPACE_ID}/size`);
    expect(http.delete).toHaveBeenNthCalledWith(
      1,
      `/workspaces/${WORKSPACE_ID}/files`,
      { path: "uploads/data.csv" },
    );
    expect(http.delete).toHaveBeenNthCalledWith(2, `/workspaces/${WORKSPACE_ID}`);
    expect(updated.name).toBeNull();
    expect(size.usedBytes).toBe(10);
  });

  it("passes cursor pagination params on files()", async () => {
    const http = {
      get: vi.fn(async () => ({ files: [], nextCursor: null, hasMore: false })),
    };
    const workspaces = new Workspaces(http as any);

    await workspaces.files(WORKSPACE_ID, {
      prefix: "uploads/",
      limit: 20,
      cursor: "cur-1",
      includeUrls: true,
      contentDisposition: "attachment",
    });

    expect(http.get).toHaveBeenCalledWith(`/workspaces/${WORKSPACE_ID}/files`, {
      prefix: "uploads/",
      limit: 20,
      cursor: "cur-1",
      includeUrls: true,
      contentDisposition: "attachment",
    });
  });

  it("posts the presign request on uploadFiles()", async () => {
    const files = [{ name: "data.csv", contentType: "text/csv", size: 3 }];
    const http = {
      post: vi.fn(async () => ({
        files: [
          {
            id: "00000000-0000-0000-0000-000000000099",
            name: "data.csv",
            storedName: "data.csv",
            path: "uploads/data.csv",
            willOverride: false,
            uploadUrl: "https://s3.example/put/data.csv",
          },
        ],
      })),
    };
    const workspaces = new Workspaces(http as any);

    const resp = await workspaces.uploadFiles(WORKSPACE_ID, {
      files,
      allowOverrides: false,
    });

    expect(http.post).toHaveBeenCalledWith(`/workspaces/${WORKSPACE_ID}/files/upload`, {
      files,
      allowOverrides: false,
    });
    expect(resp.files[0].uploadUrl).toBe("https://s3.example/put/data.csv");
  });

  describe("upload helper", () => {
    let tmpFile: string;

    function makeTmpFile(contents = "id,name\n1,a\n"): string {
      const dir = mkdtempSync(join(tmpdir(), "bu-v4-"));
      tmpFile = join(dir, "data.csv");
      writeFileSync(tmpFile, contents);
      return tmpFile;
    }

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it("presigns then PUTs the file bytes once", async () => {
      const path = makeTmpFile();
      const uploadItem = {
        id: "00000000-0000-0000-0000-000000000099",
        name: "data.csv",
        storedName: "data.csv",
        path: "uploads/data.csv",
        willOverride: false,
        uploadUrl: "https://s3.example/put/data.csv",
      };
      const http = { post: vi.fn(async () => ({ files: [uploadItem] })) };
      const fetchMock = vi
        .spyOn(globalThis, "fetch")
        .mockResolvedValue({ ok: true, status: 200, statusText: "OK" } as Response);
      const workspaces = new Workspaces(http as any);

      const result = await workspaces.upload(WORKSPACE_ID, path);

      // size is derived from the read buffer, not a separate stat call
      const presignBody = http.post.mock.calls[0][1] as { files: { size: number }[] };
      expect(presignBody.files[0].size).toBe(Buffer.byteLength("id,name\n1,a\n"));
      expect(fetchMock).toHaveBeenCalledTimes(1);
      expect(fetchMock).toHaveBeenCalledWith(
        "https://s3.example/put/data.csv",
        expect.objectContaining({ method: "PUT" }),
      );
      expect(result[0].id).toBe("00000000-0000-0000-0000-000000000099");
    });

    it("throws a descriptive error when the presign response is short", async () => {
      const path = makeTmpFile();
      const http = { post: vi.fn(async () => ({ files: [] })) };
      vi.spyOn(globalThis, "fetch");
      const workspaces = new Workspaces(http as any);

      await expect(workspaces.upload(WORKSPACE_ID, path)).rejects.toThrow(
        /Presign response has 0 upload URL\(s\).*data\.csv \(position 0\)/,
      );
    });

    it("throws when a PUT returns non-200", async () => {
      const path = makeTmpFile();
      const http = {
        post: vi.fn(async () => ({
          files: [
            {
              id: "00000000-0000-0000-0000-000000000099",
              name: "data.csv",
              storedName: "data.csv",
              path: "uploads/data.csv",
              willOverride: false,
              uploadUrl: "https://s3.example/put/data.csv",
            },
          ],
        })),
      };
      vi.spyOn(globalThis, "fetch").mockResolvedValue({
        ok: false,
        status: 403,
        statusText: "Forbidden",
      } as Response);
      const workspaces = new Workspaces(http as any);

      await expect(workspaces.upload(WORKSPACE_ID, path)).rejects.toThrow(
        /Upload failed: 403 Forbidden/,
      );
    });

    it("rejects when called with no paths", async () => {
      const http = { post: vi.fn() };
      const workspaces = new Workspaces(http as any);

      await expect(workspaces.upload(WORKSPACE_ID)).rejects.toThrow(
        /At least one file path is required/,
      );
    });
  });

  describe("download helpers", () => {
    afterEach(() => {
      vi.restoreAllMocks();
    });

    it("paginates to an exact file and streams it to disk", async () => {
      const destination = join(mkdtempSync(join(tmpdir(), "bu-v4-download-")), "result.csv");
      const url = "https://s3.example/get/reports/result.csv";
      const http = {
        get: vi.fn(async (_path: string, params?: Record<string, unknown>) =>
          params?.cursor === "page-2"
            ? {
                files: [
                  {
                    path: "reports/result.csv",
                    size: 6,
                    lastModified: "2026-01-01T00:00:00Z",
                    url,
                  },
                ],
                nextCursor: null,
                hasMore: false,
              }
            : {
                files: [
                  {
                    path: "reports/result.csv.bak",
                    size: 6,
                    lastModified: "2026-01-01T00:00:00Z",
                    url: null,
                  },
                ],
                nextCursor: "page-2",
                hasMore: true,
              },
        ),
      };
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          new ReadableStream({
            start(controller) {
              controller.enqueue(new TextEncoder().encode("result"));
              controller.close();
            },
          }),
        ),
      );
      const workspaces = new Workspaces(http as any);

      const result = await workspaces.download(WORKSPACE_ID, "reports/result.csv", {
        to: destination,
      });

      expect(result).toBe(destination);
      expect(readFileSync(destination, "utf8")).toBe("result");
      expect(http.get).toHaveBeenNthCalledWith(1, `/workspaces/${WORKSPACE_ID}/files`, {
        prefix: "reports/result.csv",
        includeUrls: true,
        cursor: undefined,
      });
      expect(http.get).toHaveBeenNthCalledWith(2, `/workspaces/${WORKSPACE_ID}/files`, {
        prefix: "reports/result.csv",
        includeUrls: true,
        cursor: "page-2",
      });
    });

    it("bounds downloads and cancels non-success response bodies", async () => {
      const directory = mkdtempSync(join(tmpdir(), "bu-v4-download-status-"));
      const destination = join(directory, "result.csv");
      writeFileSync(destination, "previous");
      const url = "https://s3.example/get/reports/result.csv";
      const signal = new AbortController().signal;
      const timeout = vi.spyOn(AbortSignal, "timeout").mockReturnValue(signal);
      let cancelled = false;
      const response = new Response(
        new ReadableStream({
          cancel() {
            cancelled = true;
          },
        }),
        { status: 503, statusText: "Service Unavailable" },
      );
      const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(response);
      const http = {
        get: vi.fn(async () => ({
          files: [
            {
              path: "reports/result.csv",
              size: 6,
              lastModified: "2026-01-01T00:00:00Z",
              url,
            },
          ],
          nextCursor: null,
          hasMore: false,
        })),
      };
      const workspaces = new Workspaces(http as any);

      await expect(
        workspaces.download(WORKSPACE_ID, "reports/result.csv", { to: destination }),
      ).rejects.toThrow(/Download failed: 503 Service Unavailable/);

      expect(timeout).toHaveBeenCalledWith(60_000);
      expect(fetchMock).toHaveBeenCalledWith(url, { signal });
      expect(cancelled).toBe(true);
      expect(readFileSync(destination, "utf8")).toBe("previous");
      expect(readdirSync(directory).filter((name) => name.endsWith(".tmp"))).toEqual([]);
    });

    it("retries partial file writes until the whole response chunk is saved", async () => {
      const directory = mkdtempSync(join(tmpdir(), "bu-v4-short-write-"));
      const destination = join(directory, "result.csv");
      const probe = await openFile(join(directory, "probe"), "w");
      const fileHandlePrototype = Object.getPrototypeOf(probe) as typeof probe;
      const originalWrite = fileHandlePrototype.write;
      await probe.close();
      let writeCalls = 0;
      vi.spyOn(fileHandlePrototype, "write").mockImplementation(async function (
        buffer: Uint8Array,
        offset = 0,
        length = buffer.byteLength - offset,
        position?: number | null,
      ) {
        writeCalls += 1;
        return originalWrite.call(
          this,
          buffer,
          offset,
          Math.min(length, 2),
          position,
        );
      });
      const url = "https://s3.example/get/reports/result.csv";
      const http = {
        get: vi.fn(async () => ({
          files: [
            {
              path: "reports/result.csv",
              size: 6,
              lastModified: "2026-01-01T00:00:00Z",
              url,
            },
          ],
          nextCursor: null,
          hasMore: false,
        })),
      };
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          new ReadableStream({
            start(controller) {
              controller.enqueue(new TextEncoder().encode("result"));
              controller.close();
            },
          }),
        ),
      );
      const workspaces = new Workspaces(http as any);

      await workspaces.download(WORKSPACE_ID, "reports/result.csv", {
        to: destination,
      });

      expect(readFileSync(destination, "utf8")).toBe("result");
      expect(writeCalls).toBe(3);
    });

    it("preserves the destination and removes the temp file when a write makes no progress", async () => {
      const directory = mkdtempSync(join(tmpdir(), "bu-v4-zero-write-"));
      const destination = join(directory, "result.csv");
      writeFileSync(destination, "previous");
      const probe = await openFile(join(directory, "probe"), "w");
      const fileHandlePrototype = Object.getPrototypeOf(probe) as typeof probe;
      await probe.close();
      vi.spyOn(fileHandlePrototype, "write").mockImplementation(async function (
        buffer: Uint8Array,
      ) {
        return { bytesWritten: 0, buffer };
      });
      const url = "https://s3.example/get/reports/result.csv";
      const http = {
        get: vi.fn(async () => ({
          files: [
            {
              path: "reports/result.csv",
              size: 6,
              lastModified: "2026-01-01T00:00:00Z",
              url,
            },
          ],
          nextCursor: null,
          hasMore: false,
        })),
      };
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          new ReadableStream({
            start(controller) {
              controller.enqueue(new TextEncoder().encode("result"));
              controller.close();
            },
          }),
        ),
      );
      const workspaces = new Workspaces(http as any);

      await expect(
        workspaces.download(WORKSPACE_ID, "reports/result.csv", { to: destination }),
      ).rejects.toThrow(/file write made no progress/);

      expect(readFileSync(destination, "utf8")).toBe("previous");
      expect(readdirSync(directory).filter((name) => name.endsWith(".tmp"))).toEqual([]);
    });

    it("refreshes each URL only after the previous file finished", async () => {
      const destination = mkdtempSync(join(tmpdir(), "bu-v4-download-all-"));
      const firstUrl = "https://s3.example/get/reports/first.csv";
      const secondUrl = "https://s3.example/get/reports/second.csv";
      const events: string[] = [];
      const http = {
        get: vi.fn(async (_path: string, params?: Record<string, unknown>) => {
          if (!params?.includeUrls) {
            events.push("list");
            return {
              files: [
                { path: "reports/first.csv", size: 5, lastModified: "2026-01-01T00:00:00Z" },
                { path: "reports/second.csv", size: 6, lastModified: "2026-01-01T00:00:00Z" },
              ],
              nextCursor: null,
              hasMore: false,
            };
          }
          const path = String(params.prefix);
          events.push(`refresh:${path}`);
          return {
            files: [
              {
                path,
                size: path.endsWith("first.csv") ? 5 : 6,
                lastModified: "2026-01-01T00:00:00Z",
                url: path.endsWith("first.csv") ? firstUrl : secondUrl,
              },
            ],
            nextCursor: null,
            hasMore: false,
          };
        }),
      };
      vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
        const url = String(input);
        const name = url === firstUrl ? "first" : "second";
        events.push(`fetch:${name}`);
        return new Response(
          new ReadableStream({
            pull(controller) {
              events.push(`stream:${name}`);
              controller.enqueue(new TextEncoder().encode(name));
              controller.close();
            },
          }),
        );
      });
      const workspaces = new Workspaces(http as any);

      const result = await workspaces.downloadAll(WORKSPACE_ID, {
        to: destination,
        prefix: "reports/",
      });

      expect(result).toEqual([
        join(destination, "reports/first.csv"),
        join(destination, "reports/second.csv"),
      ]);
      expect(events).toEqual([
        "list",
        "refresh:reports/first.csv",
        "fetch:first",
        "stream:first",
        "refresh:reports/second.csv",
        "fetch:second",
        "stream:second",
      ]);
    });

    it("rejects traversal before requesting a URL", async () => {
      const destination = mkdtempSync(join(tmpdir(), "bu-v4-traversal-"));
      const http = {
        get: vi.fn(async () => ({
          files: [
            { path: "../escape.txt", size: 6, lastModified: "2026-01-01T00:00:00Z" },
          ],
          nextCursor: null,
          hasMore: false,
        })),
      };
      const fetchMock = vi.spyOn(globalThis, "fetch");
      const workspaces = new Workspaces(http as any);

      await expect(
        workspaces.downloadAll(WORKSPACE_ID, { to: destination }),
      ).rejects.toThrow(/Path traversal detected/);

      expect(http.get).toHaveBeenCalledTimes(1);
      expect(fetchMock).not.toHaveBeenCalled();
    });

    it("rejects a symlinked parent before requesting a URL", async () => {
      const destination = mkdtempSync(join(tmpdir(), "bu-v4-symlink-root-"));
      const outside = mkdtempSync(join(tmpdir(), "bu-v4-symlink-outside-"));
      symlinkSync(
        outside,
        join(destination, "linked"),
        process.platform === "win32" ? "junction" : "dir",
      );
      const http = {
        get: vi.fn(async () => ({
          files: [
            { path: "linked/escape.txt", size: 6, lastModified: "2026-01-01T00:00:00Z" },
          ],
          nextCursor: null,
          hasMore: false,
        })),
      };
      const fetchMock = vi.spyOn(globalThis, "fetch");
      const workspaces = new Workspaces(http as any);

      await expect(
        workspaces.downloadAll(WORKSPACE_ID, { to: destination }),
      ).rejects.toThrow(/Path traversal detected/);

      expect(http.get).toHaveBeenCalledTimes(1);
      expect(fetchMock).not.toHaveBeenCalled();
      expect(readdirSync(outside)).toEqual([]);
    });

    it("keeps the old destination and removes temp files after a stream error", async () => {
      const directory = mkdtempSync(join(tmpdir(), "bu-v4-download-error-"));
      const destination = join(directory, "result.csv");
      writeFileSync(destination, "previous");
      const url = "https://s3.example/get/reports/result.csv";
      const http = {
        get: vi.fn(async () => ({
          files: [
            {
              path: "reports/result.csv",
              size: 7,
              lastModified: "2026-01-01T00:00:00Z",
              url,
            },
          ],
          nextCursor: null,
          hasMore: false,
        })),
      };
      vi.spyOn(globalThis, "fetch").mockResolvedValue(
        new Response(
          new ReadableStream({
            start(controller) {
              controller.enqueue(new TextEncoder().encode("partial"));
              controller.error(new Error("connection dropped"));
            },
          }),
        ),
      );
      const workspaces = new Workspaces(http as any);

      await expect(
        workspaces.download(WORKSPACE_ID, "reports/result.csv", { to: destination }),
      ).rejects.toThrow(/connection dropped/);

      expect(readFileSync(destination, "utf8")).toBe("previous");
      expect(readdirSync(directory).filter((name) => name.endsWith(".tmp"))).toEqual([]);
    });
  });
});
