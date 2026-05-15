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
const result = await client.run("Find the top 3 trending repos on GitHub today");
console.log(result.output);
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

## Example Project

[Browser Use Box](https://github.com/browser-use/bux) is a self-hosted 24/7 agent that uses Browser Use Cloud from a Linux box and Telegram. [Watch the demo](https://www.tiktok.com/@browser_use/video/7639824093721758989).

## License

MIT
