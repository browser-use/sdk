<p align="center">
  <img src="static/sdks-banner.png" alt="Browser Use SDKs" />
</p>

# Browser Use SDKs

Official SDKs for the [Browser Use](https://browser-use.com) cloud API.

## Packages

| Package | Language | Registry | Version |
|---------|----------|----------|---------|
| [browser-use-sdk](browser-use-node/) | TypeScript | npm | 3.0.2 |
| [browser-use-sdk](browser-use-python/) | Python | PyPI | 3.0.2 |

Both packages support **v2** (default, stable) and **v3** (experimental, via subpath import).

## Quick Start

### TypeScript

```bash
npm install browser-use-sdk
```

```typescript
import { BrowserUse } from "browser-use-sdk";

const client = new BrowserUse();
const output = await client.run("Go to google.com");
```

### Python

```bash
pip install browser-use-sdk
```

```python
from browser_use_sdk import AsyncBrowserUse

client = AsyncBrowserUse()
output = await client.run("Go to google.com")
```



## V3 (Experimental)

```typescript
import { BrowserUse } from "browser-use-sdk/v3";
```

```python
from browser_use_sdk.v3 import BrowserUse
```

## Development

Requires [Task](https://taskfile.dev) runner.

```bash
task gen:types   # regenerate types from OpenAPI specs
task build       # build both SDKs
task check       # type-check both SDKs
task test        # run tests
```

See [RUNBOOK.md](RUNBOOK.md) for the full update workflow.
