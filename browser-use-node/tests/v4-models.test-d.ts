import { expectTypeOf, test } from "vitest";
import type { QueueMessageRequest, RunCreateBody, RunModel } from "../src/v4.js";

test("known V4 models autocomplete and newer model ids still compile", () => {
  expectTypeOf<"gpt-6-luna">().toMatchTypeOf<RunModel>();
  const future: RunCreateBody = { task: "Find pricing", model: "model-from-next-month" };
  void future;
});

test("browserSettings fields with server defaults stay optional", () => {
  const profileOnly: RunCreateBody = { task: "Check my orders", browserSettings: { profileId: "p" } };
  void profileOnly;
});

test("interface-typed queue messages from 3.12 still compile", () => {
  interface OldMessage { text: string; interrupt: boolean }
  expectTypeOf<OldMessage>().toMatchTypeOf<QueueMessageRequest>();
  expectTypeOf<{ confirmInputId: number }>().toMatchTypeOf<QueueMessageRequest>();
});
