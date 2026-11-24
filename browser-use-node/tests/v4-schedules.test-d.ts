import { expectTypeOf, test } from "vitest";

import type {
  RunSummary,
  ScheduleBrowserSettings,
  ScheduleCreateBody,
  ScheduleSecretBinding,
  ScheduleRunsParams,
  ScheduleSettings,
} from "../src/v4.js";

test("schedule types preserve timing choices and optional settings", () => {
  expectTypeOf<{ task: string; cronExpr: string }>().toMatchTypeOf<ScheduleCreateBody>();
  expectTypeOf<{ task: string; runAt: string }>().toMatchTypeOf<ScheduleCreateBody>();
  expectTypeOf<{
    task: string;
    cronExpr: string;
    runAt: string;
  }>().not.toMatchTypeOf<ScheduleCreateBody>();
  expectTypeOf<{}>().toMatchTypeOf<ScheduleSettings>();
  expectTypeOf<Extract<keyof ScheduleBrowserSettings, "customProxy">>().toBeNever();
  expectTypeOf<ScheduleSecretBinding["source"]["type"]>().toEqualTypeOf<"onepassword">();
  expectTypeOf<Extract<keyof ScheduleRunsParams, "sessionId">>().toBeNever();
  expectTypeOf<RunSummary["scheduleId"]>().toEqualTypeOf<string | undefined>();
});
