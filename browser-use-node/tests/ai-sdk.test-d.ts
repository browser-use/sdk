import type { InferToolInput, InferToolOutput, Tool, ToolSet } from "ai";
import { expectTypeOf, test } from "vitest";

import { browserUse } from "../src/ai-sdk.js";
import type { BrowserUseToolOutput } from "../src/ai-sdk.js";

test("browserUse() is a Vercel AI SDK tool", () => {
  const tool = browserUse();
  expectTypeOf(tool).toMatchTypeOf<Tool>();
  expectTypeOf({ browserUse: tool }).toMatchTypeOf<ToolSet>();
  expectTypeOf<InferToolInput<typeof tool>>().toEqualTypeOf<{
    task: string;
    sessionId?: string | undefined;
  }>();
  expectTypeOf<InferToolOutput<typeof tool>>().toEqualTypeOf<BrowserUseToolOutput>();
});
