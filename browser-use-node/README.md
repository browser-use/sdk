# browser-use-sdk

Official TypeScript SDK for [Browser Use Cloud](https://browser-use.com).

## Install

```bash
npm install browser-use-sdk
```

## Quick Start

Get your API key at [cloud.browser-use.com/settings](https://cloud.browser-use.com/settings?tab=api-keys&new=1).

```bash
export BROWSER_USE_API_KEY=your_key
```

```typescript
import { BrowserUse } from "browser-use-sdk";

const client = new BrowserUse();
const run = await client.runs.create({
  task: "Find the top 3 trending repos on GitHub today",
});
const result = await client.runs.waitForCompletion(run.id);
console.log(result.result);
```

Since 4.0.0 the default import is the V4 **Browser Use Agents** interface,
including the browser resource; see the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).
`browser-use-sdk/v4` keeps working as an alias.

## Migrating from 3.x

4.0.0 makes V4 the root import. Code that imported the V2 client from the root
(`client.tasks`, `client.run`, `TaskView`, ...) needs one import change and
nothing else; the V2 API itself is unchanged. Without the change, TypeScript
reports `Property 'tasks' does not exist on type 'BrowserUse'` and plain
JavaScript throws a `TypeError` naming `browser-use-sdk/v2`.
`browser-use-sdk/v3` and `browser-use-sdk/v4` are unchanged.

```diff
-import { BrowserUse } from "browser-use-sdk";
+import { BrowserUse } from "browser-use-sdk/v2";
```

## v3 Bring Your Own LLM Key

Add your provider API key in Browser Use project settings, then enable BYOK for v3 agent runs:

```typescript
import { BrowserUse } from "browser-use-sdk/v3";

const client = new BrowserUse({ useOwnKey: true });
const result = await client.run("Find the top 3 trending repos on GitHub today");
console.log(result.output);
```

## Docs

[docs.browser-use.com](https://docs.browser-use.com)

## License

MIT

## V4 structured output

Pass a JSON Schema object as `outputSchema` to `runs.create`, then read `output`
from `runs.get` or `runs.waitForCompletion`. `result` remains the text answer and
`outputSchema` echoes the requested schema. Omit `outputSchema` (or pass `null`)
for an unstructured run. The output type is `unknown`; validate it before use.

```typescript
import { BrowserUse } from "browser-use-sdk/v4";

const client = new BrowserUse();
const created = await client.runs.create({
  task: "Open https://example.com and return its page title.",
  outputSchema: {
    type: "object",
    properties: { title: { type: "string" } },
    required: ["title"],
  },
});
const run = await client.runs.waitForCompletion(created.id);
console.log(run.status, run.output);
```

For Zod, convert with `z.toJSONSchema(schema)` and validate with
`schema.parse(run.output)`. See the [complete example](examples/v4-structured-output.ts).
