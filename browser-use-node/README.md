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
browser-management resource currently lives in the explicit `browser-use-sdk/v3`
entry point; see the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).

## v3 Bring Your Own LLM Key

Add your provider API key in Browser Use project settings, then enable BYOK for v3 agent runs:

```typescript
import { BrowserUse } from "browser-use-sdk/v3";

const client = new BrowserUse({ useOwnKey: true });
const result = await client.run("Find the top 3 trending repos on GitHub today");
console.log(result.output);
```

## Retries

The SDK retries HTTP 429 for all methods and HTTP 502/503/504 for GET requests,
up to three retries by default (`maxRetries: 0` disables retries). It does not
retry other HTTP errors or transport failures. Retries use exponential backoff
starting at one second, capped at ten seconds, with up to 250ms of positive jitter.
A valid `Retry-After` can extend each wait to 60 seconds; longer waits surface the
error immediately instead of retrying early. The `timeout` option remains a
per-attempt timeout, so retry waits add to the total request duration.

## Docs

[docs.browser-use.com](https://docs.browser-use.com)

## License

MIT
