import { expectTypeOf, test } from "vitest";
import type { RunCreateBody, RunCreateRequest, RunSummary } from "../src/v4.js";

test("structured output is part of the public V4 contract", () => {
  expectTypeOf<RunCreateBody>().toHaveProperty("outputSchema");
  expectTypeOf<RunCreateRequest>().toHaveProperty("outputSchema");
  expectTypeOf<RunSummary>().toHaveProperty("output");
  expectTypeOf<RunSummary>().toHaveProperty("outputSchema");
  const body: RunCreateBody = { task: "Extract", outputSchema: { type: "object" } };
  const nullable: RunCreateBody = { task: "Extract", outputSchema: null };
  expectTypeOf(body).toMatchTypeOf<RunCreateBody>();
  expectTypeOf(nullable).toMatchTypeOf<RunCreateBody>();
});
