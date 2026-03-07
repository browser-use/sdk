# SDK Update Runbook

Decision guide for the `/sdk` pipeline. Read this, then go.

## Phase 0: Discover

Diff the fresh OpenAPI specs (`$CLOUD_REPO_PATH/backend/spec/api/v{2,3}/openapi.json`) against the snapshots (`snapshots/v{2,3}.json`). Classify each change:

| Change | Version Impact |
|--------|---------------|
| New endpoint | MINOR |
| Removed endpoint / required param / response field / enum value | **MAJOR** |
| New optional param / response field / enum value | PATCH |
| Description only | none |

Present findings to user via `AskUserQuestion`. Get approval before proceeding.

If no spec changes, ask user if they want to proceed anyway (useful for fixing SDK bugs).

## Phase 1: Regenerate & Audit

1. Run `task gen:types` — regenerates all 4 type files (TS v2/v3 + Python v2/v3)
2. Post-gen fix: patch enum string literal defaults → enum members (datamodel-codegen bug)
3. Post-gen fix: check Python models for regex lookaheads, add `ConfigDict(regex_engine="python-re")` if needed
4. **Deep audit with 2 parallel subagents:**
   - **TS auditor**: Read the OpenAPI specs + every SDK file in `browser-use-node/src/v2/` and `v3/`. Compare every route, parameter, type, and response field against the spec. Check the git diff from type regeneration to understand what changed. Report everything that's missing, wrong, or outdated.
   - **Python auditor**: Same for `browser-use-python/src/browser_use_sdk/v2/` and `v3/`.

The audit reports become the fix plan for Phase 2.

## Phase 2: Fix

Take the audit reports and fix everything in both SDKs. Update both TypeScript and Python together — they must have identical method coverage.

Follow existing patterns in the codebase. Read before writing.

## Phase 3: Test & Ship

1. Run `task test`. Fix failures (max 3 attempts, then escalate).
2. Optionally run `task test:live` if backend is reachable.
3. Confirm version bump with user → bump both packages → save snapshots → commit.
4. Do NOT publish. Tell user to run `task publish`.

---

## Quick Reference

- Method naming: `POST → .create()`, `GET → .list()`, `GET /{id} → .get()`, `DELETE → .delete()`, `PATCH → .stop()` (named methods for actions)
- Package: `browser-use-sdk` (npm + PyPI)
- v2 = default import, v3 = subpath import
- Python: snake_case params → camelCase in request body
- TS: types from `components["schemas"]["..."]`
- List responses: `{ items, totalItems, pageNumber, pageSize }`
- V2 no `failed` status. Failed = `finished` + `isSuccess: false`
- V3 success = `idle` status
- Max 3 concurrent sessions on test account

## Learnings

<!-- AI appends notes here after each run -->

- **Pydantic regex**: `datamodel-codegen` generates `constr` patterns with lookaheads that need `ConfigDict(regex_engine="python-re")`
- **Enum defaults**: `datamodel-codegen` (all versions) outputs string literals for enum defaults. Must patch to enum members post-generation or pyright fails.
- **datamodel-codegen version**: Pin to 0.45.0 via `uv tool install`. Version 0.53.0 also has the enum bug + generates `Optional[]` vs `| None` inconsistently.
- **System python3 is 3.9**: Use `uv run python` instead of `python3` for anything needing 3.11+ features (tomllib, etc.)
- **pnpm lockfile**: May go stale when package.json is updated. Run `pnpm install` before `pnpm install --frozen-lockfile`.
- **openapi-typescript**: Generates `components["schemas"]["TypeName"]` pattern, not direct exports. Resource files use local type aliases.
- **Python SDK type safety**: All resource methods return Pydantic model instances (via `model_validate()`), NOT dicts.
- **Structured output**: V2 only. Python auto-converts Pydantic models via `output_schema`. TS uses Zod schemas via `{ schema }` option.
- **Polling**: `await client.run()` polls `tasks.status()` (lightweight). `for await`/`for step in client.stream()` polls full `tasks.get()` and yields new `TaskStepView` steps.
