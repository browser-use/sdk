# /sdk — AI-Driven SDK Update System

You are the SDK update agent. You update the Browser Use SDKs when the OpenAPI spec changes.

## Context Loading (always do this first)

1. Read `.env` in the project root for `CLOUD_REPO_PATH`, `BACKEND_URL`, `BROWSER_USE_API_KEY`
2. Read `RUNBOOK.md` — this is your decision guide. Follow its phases.
3. Read `CLAUDE.md` — project structure and design principles
4. Read `spec.md` — DX contract (what the SDK should look like to users)

## Modes

Parse `$ARGUMENTS` to determine what to do:

| Command | What it does |
|---------|-------------|
| `/sdk` or `/sdk update` | Full pipeline: Phase 0 → 5 |
| `/sdk discover` | Phase 0 only — show what changed, recommend version |
| `/sdk build` | Phase 1 → 2 — regenerate types + update SDK code |
| `/sdk test` | Phase 3 only — run tests, fix failures |
| `/sdk docs` | Phase 4 only — update docs, drift check |
| `/sdk version` | Phase 5 only — bump version + commit |

## Executing the Pipeline

Follow the phases in `RUNBOOK.md`. Key rules:

### Decision Points
- **Phase 0 (Discovery)**: ALWAYS ask the user what to do. Use `AskUserQuestion` with multi-select to present changes and get approval.
- **Phase 5 (Version)**: ALWAYS confirm the version bump with the user before committing.
- **All other phases**: Run autonomously. Only interrupt if something goes wrong (test failures >2x, unexpected errors).

### Reading Specs
- Snapshot specs (what we generated from): `snapshots/v2.json`, `snapshots/v3.json`
- Fresh specs (what the backend now has): `$CLOUD_REPO_PATH/backend/spec/api/v2/openapi.json`, `$CLOUD_REPO_PATH/backend/spec/api/v3/openapi.json`
- Diff these to understand what changed

### Updating Code
- Always read the existing file before modifying it
- Follow patterns already in the codebase
- Update BOTH TypeScript and Python for every change
- Python uses snake_case params → camelCase in request body
- TS uses types from `components["schemas"]["..."]`

### Testing
- `task test` = vibe tests (no backend, fast, spec-driven)
- `task test:live` = live tests (needs backend running on $BACKEND_URL)
- Fix failures up to 3 times, then escalate to user

### After Completion
- Update `snapshots/` with the fresh specs
- Check if `RUNBOOK.md` needs a new learning appended
- Check if `CLAUDE.md` or `spec.md` need updates
- **Do NOT publish** — tell the user to run `task publish` when ready

## Important Facts

- Method naming: `POST /resource → .create()`, `GET /resource → .list()`, `PATCH /resource/{id} → .stop()` (action = named method)
- Package name: `browser-use-sdk` (both npm and PyPI)
- v2 = default import, v3 = subpath import (`browser-use-sdk/v3` / `browser_use_sdk.v3`)
- List endpoints return `{ items, totalItems, pageNumber, pageSize }` — NOT resource-specific names
- V2 has no `failed` task status. Failed = `finished` + `isSuccess: false`
- V3 success = `idle` status
- Max 3 concurrent sessions on test account
