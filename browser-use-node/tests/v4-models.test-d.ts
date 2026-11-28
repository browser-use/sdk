import { expectTypeOf, test } from "vitest";
import type { CreateAccessTokenBody as V2AccessTokenBody } from "../src/index.js";
import type { CreateAccessTokenBody as V3AccessTokenBody } from "../src/v3.js";
import type { CreateAccessTokenBody, QueueMessageRequest, RunCreateBody, RunModel } from "../src/v4.js";

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

test("an access token body rejects a misspelled field, so a token never loses its life by a typo", () => {
  // @ts-expect-error ttl_seconds is not a field; the API takes ttlSeconds.
  const v4: CreateAccessTokenBody = { ttl_seconds: 60 };
  // @ts-expect-error ttl_seconds is not a field; the API takes ttlSeconds.
  const v3: V3AccessTokenBody = { ttl_seconds: 60 };
  // @ts-expect-error ttl_seconds is not a field; the API takes ttlSeconds.
  const v2: V2AccessTokenBody = { ttl_seconds: 60 };
  void [v4, v3, v2];
});
