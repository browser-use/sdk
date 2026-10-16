import { expectTypeOf, test } from "vitest";
import type { RunCreateBody, RunModel } from "../src/v4.js";

test("known V4 models autocomplete and newer model ids still compile", () => {
  expectTypeOf<"gpt-6-luna">().toMatchTypeOf<RunModel>();
  const future: RunCreateBody = { task: "Find pricing", model: "model-from-next-month" };
  void future;
});

test("browserSettings fields with server defaults stay optional", () => {
  const profileOnly: RunCreateBody = { task: "Check my orders", browserSettings: { profileId: "p" } };
  void profileOnly;
});
