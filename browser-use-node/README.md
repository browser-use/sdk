# browser-use-sdk

Official TypeScript SDK for [Browser Use Cloud](https://browser-use.com).

## Install

```bash
npm install browser-use-sdk
```

## Quick Start

Eligible new Google, GitHub, or Microsoft signups receive a one-time $15 Cloud credit. No credit card is required. Email/password signups are not eligible; the credit does not renew. Start with the default V4 model (`gpt-5.6-luna`); paid-only models require a top-up. See [pricing](https://browser-use.com/pricing.md) for current eligibility and rates.

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
if (result.status !== "completed") {
  throw new Error(`Run ${result.id}: ${result.status}`);
}
console.log(result.result);
```

This is the current **Browser Use Agents** interface. SDK 3.11.3 or newer also
exposes `client.browsers.create` and `client.browsers.stop` in `browser-use-sdk/v4`.
Always stop standalone browsers explicitly; closing a client or disconnecting
CDP does not stop billing. See the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).
Existing V2/V3 integrations can keep their versioned imports.

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
