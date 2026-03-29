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

## Docs

[docs.browser-use.com](https://docs.browser-use.com)

## License

MIT
