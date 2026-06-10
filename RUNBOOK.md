# SDK Update Runbook

Decision guide for the `/sdk` pipeline. Read this, then go.

## Releasing

1. `task version:bump -- patch` (or `minor` / `major`). Bumps both `browser-use-node/package.json` and `browser-use-python/pyproject.toml`.
2. Commit, open PR, merge to main.
3. Done. The `auto-release-on-version-bump` workflow detects the bump on main and creates a GitHub Release at the bump commit (tag `v$NEW_VERSION`). The Release event fires `publish.yml`, which runs preflight (env protection + version coherence + already-published guard), pauses at the `release` environment approval gate, and on approval publishes to both npm and PyPI via OIDC.

If the publish fails after the Release is created: the Release stays (it's the rollback handle). Investigate, fix on a new patch version, repeat.

Manual `gh release create v$VERSION --generate-notes` from the CLI also works if you want to ship without a bump-PR cycle. It skips the auto-detector and goes straight to `publish.yml`.

`task publish` is intentionally broken. See below for why.

## Release authentication

Both registries use OIDC trusted publishing. **No static tokens, no secrets to rotate.**

- **PyPI**: trusted publishing configured at https://pypi.org/manage/project/browser-use-sdk/settings/publishing/ (Owner: browser-use, Repository: sdk, Workflow: publish.yml, Environment: release).
- **npm**: trusted publishing configured at https://www.npmjs.com/package/browser-use-sdk/access (same four fields, Allowed action: npm publish).
- The `release` environment requires approval from a reviewer other than the release author (`prevent_self_review: true`). Reviewers: gregpr07, LarsenCundric.

If a trusted publisher binding is ever revoked or misconfigured, publishing will fail at the publish step with a clear OIDC error from the registry. The release tag stays cut (you can re-dispatch after re-binding).

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
4. **Bump versions and merge.** Run `task version:bump -- patch` (or `minor` / `major`). Commit both `browser-use-node/package.json` and `browser-use-python/pyproject.toml`. Open a PR. Merge to main.

That's it. The `auto-release-on-version-bump` workflow detects the bump on main and creates a GitHub Release at the bump commit (tag `v$NEW_VERSION`). The Release event fires `publish.yml`, which runs preflight (env protection + version coherence + already-published guard), pauses at the `release` environment approval gate, and on approval publishes to both npm and PyPI via OIDC.

If the publish fails after the Release is created: the Release stays (it's the rollback handle). Investigate, fix on a new patch version, repeat from step 1.

Manual `gh release create v$VERSION --generate-notes` from the CLI also works if you want to ship without a bump-PR cycle. It skips the auto-detector and goes straight to `publish.yml`.

`task publish` is intentionally broken. See RUNBOOK > Release authentication for why.

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
- **docs/openapi dir**: `task snapshot:save` calls `task docs:sync` which requires `docs/openapi/` to exist. Create it with `mkdir -p docs/openapi` if missing (e.g., on fresh clone).
