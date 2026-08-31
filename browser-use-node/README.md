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

This example uses **Browser Use Agents**. **Browser Infrastructure** is hosted
cloud browser infrastructure for AI agents, controlled through the
`browser-use-sdk/v3` browser resource, REST, or CDP. See the
[browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart) and
[developer overview](https://browser-use.com/developers).

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
