# Browser Use SDK

Official TypeScript and Python SDKs for the Browser Use cloud API. Published as `browser-use-sdk` on npm and PyPI.

## Project Layout

```
browser-use-node/src/          # TypeScript SDK
  index.ts                     # default = v2
  v3.ts                        # subpath = v3
  core/                        # shared http + errors
  generated/v{2,3}/types.ts    # openapi-typescript output
  v2/                          # client + resource files + helpers
  v3/                          # client + sessions + helpers

browser-use-python/src/browser_use_sdk/   # Python SDK
  __init__.py                  # default = v2
  _core/                       # shared http + errors
  generated/v{2,3}/models.py   # datamodel-codegen output
  v2/                          # client + resource files + helpers
  v3/                          # client + sessions + helpers

snapshots/v{2,3}.json          # last-generated OpenAPI specs
Taskfile.yml                   # mechanical commands
RUNBOOK.md                     # /sdk pipeline guide + learnings
.env                           # CLOUD_REPO_PATH, BACKEND_URL, BROWSER_USE_API_KEY
```

## API Versions

- **v2** (default) — stable, full API surface. `import { BrowserUse } from "browser-use-sdk"` / `from browser_use_sdk import BrowserUse`
- **v3** (experimental) — subpath import. `import { BrowserUse } from "browser-use-sdk/v3"` / `from browser_use_sdk.v3 import BrowserUse`

## SDK Updates

Run `/sdk` to update both SDKs from the OpenAPI specs. See `RUNBOOK.md` for the pipeline phases and accumulated learnings.

## Commands

```bash
task gen:types       # generate TS + Python types from OpenAPI
task check           # type-check both SDKs
task build           # compile both SDKs
task test            # spec-driven vibe tests (no backend)
task test:live       # live integration tests (needs backend)
task snapshot:save   # save current specs as snapshots
task version:bump    # bump package versions
task publish         # npm + pypi publish
```

## Design Principles

1. **1:1 with OpenAPI.** Every endpoint maps to an SDK method.
2. **Types are generated.** `openapi-typescript` + `datamodel-codegen`. Deterministic.
3. **Helpers are minimal.** `complete()` and `stream()` are ~20 lines each.
4. **Python returns Pydantic models.** Full type safety, not dicts.
5. **Everything is regeneratable.** Generate, audit, fix, ship.

## Python SDK Rules

- **Never use `Dict[str, Any]` for typed params.** If the OpenAPI spec defines a schema, use the generated Pydantic model (e.g. `SessionSettings`, `CustomProxy`). Only use `Dict[str, Any]` when the spec literally says `object` with no further schema.
- **Use `X | None`, not `Optional[X]`.** Modern Python union syntax everywhere — hand-written code and generated code (via `--use-union-operator` flag).
