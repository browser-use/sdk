import { expectTypeOf, test } from "vitest";
import type { RunCreateBody, RunModel } from "../src/v4.js";

test("bu-ultrafast is a typed V4 model and unknown models are not", () => {
  const ultrafast: RunCreateBody = { task: "Find pricing", model: "bu-ultrafast" };
  expectTypeOf<"bu-ultrafast">().toMatchTypeOf<RunModel>();
  // @ts-expect-error unknown models stay a compile error.
  const unknown: RunCreateBody = { task: "Find pricing", model: "bu-slow" };
  void ultrafast;
  void unknown;
});
