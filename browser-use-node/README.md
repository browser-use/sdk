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
import { BrowserUse } from "browser-use-sdk/v4";

const client = new BrowserUse();
const run = await client.runs.create({
  task: "Find the top 3 trending repos on GitHub today",
});
const result = await client.runs.waitForCompletion(run.id);
console.log(result.result);
```

This is the current **Browser Use Agents** interface. Browser Infrastructure's
browser-management resource currently lives in the explicit `browser-use-sdk/v4`
entry point; see the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).

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
