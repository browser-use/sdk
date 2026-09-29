import { expectTypeOf, test } from "vitest";
import type { RunCreateBody, RunModel } from "../src/v4.js";

test("ultrafast presets are typed V4 models", () => {
  const ultrafast: RunCreateBody = { task: "Find pricing", model: "bu-ultrafast" };
  const fast: RunCreateBody = { task: "Find pricing", model: "bu-fast" };
  expectTypeOf(ultrafast).toMatchTypeOf<RunCreateBody>();
  expectTypeOf(fast).toMatchTypeOf<RunCreateBody>();
  expectTypeOf<"bu-ultrafast">().toMatchTypeOf<RunModel>();
  // @ts-expect-error unknown models stay a compile error.
  const unknown: RunCreateBody = { task: "Find pricing", model: "bu-slow" };
  void unknown;
});
