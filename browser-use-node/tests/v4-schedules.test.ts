import { expect, it, vi } from "vitest";

import { BrowserUse, type ScheduleCreateBody, type ScheduleView } from "../src/v4.js";

const id = "00000000-0000-0000-0000-000000000010";
const sessionId = "00000000-0000-0000-0000-000000000020";
const nextRunAt = "2027-03-15T13:00:00Z";
const schedule: ScheduleView = {
  id,
  sessionId,
  enabled: true,
  task: "Read the page title",
  cronExpr: "0 9 * * *",
  runAt: null,
  timezone: "America/New_York",
  nextRunAt,
  createdAt: nextRunAt,
  updatedAt: nextRunAt,
  settings: {},
};

it("creates, lists, reads, updates and deletes schedules and lists their runs", async () => {
  const createBody = {
    task: schedule.task,
    cronExpr: schedule.cronExpr!,
    timezone: schedule.timezone,
    sessionId,
    outputSchema: { type: "object" },
    browserSettings: { proxyCountryCode: null },
    futureField: "pass through",
  } satisfies ScheduleCreateBody & { futureField: string };

  const updated = { ...schedule, cronExpr: null, runAt: nextRunAt, enabled: false };
  const updateBody = {
    enabled: false,
    task: "Check again",
    runAt: nextRunAt,
    timezone: "UTC",
    futureField: "pass through",
  };

  const fetch = vi.fn<typeof globalThis.fetch>()
    .mockResolvedValueOnce(Response.json(schedule, { status: 201 }))
    .mockResolvedValueOnce(Response.json({ schedules: [schedule], nextCursor: "next", hasMore: true }))
    .mockResolvedValueOnce(Response.json(schedule))
    .mockResolvedValueOnce(Response.json(updated))
    .mockResolvedValueOnce(Response.json({ runs: [{ scheduleId: id }], nextCursor: null, hasMore: false }))
    .mockResolvedValueOnce(new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetch);

  try {
    const client = new BrowserUse({ apiKey: "test", baseUrl: "https://api.example.com/api/v4" });

    expect(await client.schedules.create(createBody)).toEqual(schedule);
    expect(await client.schedules.list({ enabled: false, cursor: "prior", limit: 5 })).toEqual({
      schedules: [schedule],
      nextCursor: "next",
      hasMore: true,
    });
    expect(await client.schedules.get(id)).toEqual(schedule);
    expect(await client.schedules.update(id, updateBody)).toEqual(updated);
    const runs = await client.schedules.runs(id, {
      cursor: "prior",
      limit: 3,
      metadata: ["watch", "region=us"],
    });
    expect(runs.runs[0]?.scheduleId).toBe(id);
    expect(await client.schedules.delete(id)).toBeUndefined();

    const [create, list, get, update, listRuns, remove] = fetch.mock.calls.map(([input, init]) => {
      const url = new URL(String(input));
      return {
        method: init?.method,
        path: url.pathname,
        params: url.searchParams,
        body: init?.body ? JSON.parse(String(init.body)) : undefined,
      };
    });
    expect(create).toMatchObject({ method: "POST", path: "/api/v4/schedules", body: createBody });
    expect(list).toMatchObject({ method: "GET", path: "/api/v4/schedules" });
    expect([...list!.params]).toEqual([["enabled", "false"], ["cursor", "prior"], ["limit", "5"]]);
    expect(get).toMatchObject({ method: "GET", path: `/api/v4/schedules/${id}` });
    expect(update).toMatchObject({ method: "PATCH", path: `/api/v4/schedules/${id}`, body: updateBody });
    expect(listRuns).toMatchObject({ method: "GET", path: `/api/v4/schedules/${id}/runs` });
    expect([...listRuns!.params]).toEqual([
      ["cursor", "prior"],
      ["limit", "3"],
      ["metadata", "watch"],
      ["metadata", "region=us"],
    ]);
    expect(remove).toMatchObject({ method: "DELETE", path: `/api/v4/schedules/${id}` });
  } finally {
    vi.unstubAllGlobals();
  }
});
