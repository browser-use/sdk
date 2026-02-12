# Browser Use SDK Generator

This repo generates and maintains the official Browser Use SDKs for TypeScript and Python.

## Project Layout

```
.
├── browser-use-node/        -> published to npm as "browser-use-sdk"
│   └── src/
│       ├── index.ts                 # default = v2
│       ├── v3.ts                    # subpath = v3
│       ├── core/                    # shared http + errors
│       ├── generated/v2/types.ts    # openapi-typescript from v2 spec
│       ├── generated/v3/types.ts    # openapi-typescript from v3 spec
│       ├── v2/                      # client + 8 resource files + helpers
│       └── v3/                      # client + sessions + helpers
├── browser-use-python/      -> published to pypi as "browser-use-sdk"
│   └── src/browser_use_sdk/
│       ├── __init__.py              # default = v2
│       ├── _core/                   # shared http + errors
│       ├── generated/v2/models.py   # datamodel-codegen from v2 spec
│       ├── generated/v3/models.py   # datamodel-codegen from v3 spec
│       ├── v2/                      # client + 8 resource files + helpers
│       └── v3/                      # client + sessions + helpers (import from browser_use_sdk.v3)
├── snapshots/
│   ├── v2.json              # snapshot of OpenAPI spec used for last generation
│   └── v3.json              # snapshot of OpenAPI spec used for last generation
├── spec.md                  -> DX contract (human-authored)
├── Taskfile.yml             -> deterministic operations
├── RUNBOOK.md               -> AI decision guide for updates (phases + learnings)
├── .claude/commands/generate.md -> /sdk entry point
└── .env                     -> paths to cloud repo + API key
```

## How It Works

The SDKs are generated from OpenAPI specs in the **internal cloud repo** (path in `.env`).

```
Internal cloud repo                    This repo (public)
-------------------                    ------------------
backend/spec/api/v2/openapi.json  ->   browser-use-node/src/generated/v2/types.ts
                                  ->   browser-use-python/src/browser_use_sdk/generated/v2/models.py
backend/spec/api/v3/openapi.json  ->   browser-use-node/src/generated/v3/types.ts
                                  ->   browser-use-python/src/browser_use_sdk/generated/v3/models.py
```

## API Versioning

- **v2** (default) -- stable, production. Full API: tasks, sessions, profiles, browsers, skills, marketplace, billing, files.
- **v3** (experimental) -- opt-in via subpath import. Simplified session-based model (5 endpoints).
- Default import = v2. Subpath import (`browser-use-sdk/v3` or `browser_use_sdk.v3`) = v3.

## User Experience

```typescript
// v2 (default)
import { BrowserUse } from "browser-use-sdk";
const client = new BrowserUse({ apiKey: "bu_..." });
const task = await client.tasks.create({ task: "Go to google.com" });
const result = await client.run({ task: "Go to google.com" }).complete();

// v3 (experimental)
import { BrowserUse } from "browser-use-sdk/v3";
const client = new BrowserUse({ apiKey: "bu_..." });
const result = await client.run({ task: "Go to google.com" }).complete();
```

```python
# v2 (default)
from browser_use_sdk import BrowserUse
client = BrowserUse(api_key="bu_...")
result = client.run("Go to google.com").complete()

# v3 (experimental)
from browser_use_sdk.v3 import BrowserUse
client = BrowserUse(api_key="bu_...")
result = client.run("Go to google.com").complete()
```

## SDK Update System

The SDK is updated via `/sdk` — an AI-driven command that follows phases in `RUNBOOK.md`.

```
/sdk                   # full pipeline: discover → types → code → test → docs → version
/sdk discover          # show what changed in the specs
/sdk build             # regenerate types + update SDK code
/sdk test              # run tests, fix failures
/sdk docs              # update docs, drift check
/sdk version           # bump version + commit
```

The system uses **spec snapshots** (`snapshots/v2.json`, `snapshots/v3.json`) to detect what changed between runs. After each successful update, snapshots are refreshed.

See `RUNBOOK.md` for the full decision guide including change classification, version bump rules, and accumulated learnings.

## Mechanical Commands

```bash
task spec:pull          # pull OpenAPI specs from running backend
task gen:types          # generate TS + Python types (v2 + v3)
task check              # type-check both SDKs
task build              # compile both SDKs
task test               # run spec-driven vibe tests (no backend)
task test:live          # run live integration tests (needs backend)
task snapshot:save      # save current specs as snapshots
task snapshot:diff      # diff snapshots vs current specs
task version:bump       # bump both package versions
task publish            # npm + pypi publish
```

## Environment

The `.env` file must be configured:
- `CLOUD_REPO_PATH` -- absolute path to the internal cloud repo
- `BACKEND_URL` -- local backend URL (default: http://localhost:8000)
- `BROWSER_USE_API_KEY` -- API key for vibe tests

## Structured Output (Type-safe)

The SDK supports type-safe structured output parsing.

**Python** — pass a Pydantic `BaseModel` subclass as `output_schema`. The SDK auto-converts it to a JSON schema string for the API and provides `parse_output()` on the handle:

```python
from pydantic import BaseModel
from browser_use_sdk import BrowserUse

class Product(BaseModel):
    name: str
    price: float

client = BrowserUse(api_key="bu_...")
handle = client.run("Find product info", output_schema=Product)
result = handle.complete()
product = handle.parse_output(result)  # Product instance, fully typed
```

**TypeScript** — pass any object with a `.parse()` method (Zod, superstruct, etc.) as `outputSchema`. You must also pass `structuredOutput` (stringified JSON schema) in the request body:

```typescript
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import { BrowserUse } from "browser-use-sdk";

const Product = z.object({ name: z.string(), price: z.number() });
const client = new BrowserUse({ apiKey: "bu_..." });
const handle = client.run(
  { task: "Find product info", structuredOutput: JSON.stringify(zodToJsonSchema(Product)) },
  { outputSchema: Product },
);
const result = await handle.complete();
const product = handle.parseOutput(result); // { name: string, price: number }
```

Key difference: Python auto-converts Pydantic models to JSON schema (built-in `model_json_schema()`). TypeScript requires manual conversion since Zod doesn't have built-in JSON schema export.

**V3 does not support structured output** — it's a v2-only feature.

## Design Principles

1. **1:1 with OpenAPI.** Every endpoint maps to an SDK method. No renaming.
2. **PATCH actions -> named methods.** `tasks.stop()`, `sessions.stop()`, `browsers.stop()`.
3. **Types are deterministic.** Generated by openapi-typescript / datamodel-codegen.
4. **Helpers are minimal.** `complete()` and `stream()` are ~20 lines each.
5. **No wrapper inheritance.** Clean, direct code.
6. **Everything is regeneratable.** Generate, diff, review, ship.
7. **End-to-end type safety.** Python returns Pydantic models. Structured output is parsed into typed objects.

## Testing

Tests are spec-driven: they read OpenAPI specs at runtime and verify every endpoint has a corresponding SDK method.

Run with: `task test`

## Known Issues

- **Pydantic regex fix**: `datamodel-codegen` may generate regex patterns with lookaheads. Add `model_config = ConfigDict(regex_engine="python-re")` to affected models after generation.
- **v3 missing 404 responses**: Backend returns 404 for non-existent sessions but spec only declares 200/422.
