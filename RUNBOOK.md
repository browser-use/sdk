# SDK Update Runbook

This is the decision guide for the AI-driven SDK update system. When you run `/sdk`, follow these phases in order. This document is the source of truth for how to update the SDK.

## Prerequisites

- Cloud repo available at `$CLOUD_REPO_PATH` (from `.env`)
- OpenAPI specs exist at `$CLOUD_REPO_PATH/backend/spec/api/v2/openapi.json` and `v3`
- Spec snapshots exist at `snapshots/v2.json` and `snapshots/v3.json`
- For live tests: local backend running at `$BACKEND_URL`

## Phase 0: Discovery

**Goal**: Understand what changed and get user approval before doing anything.

### Steps

1. Read `.env` for paths
2. Read the fresh OpenAPI specs from `$CLOUD_REPO_PATH`
3. Read the snapshot specs from `snapshots/v2.json` and `snapshots/v3.json`
4. Diff each pair. For each difference, classify it:

### Change Classification

| Change Type | Description | Version Impact |
|-------------|-------------|----------------|
| `NEW_ENDPOINT` | A path+method that didn't exist before | MINOR |
| `REMOVED_ENDPOINT` | A path+method that no longer exists | **MAJOR** |
| `NEW_REQUIRED_PARAM` | New required field in request body | **MAJOR** |
| `NEW_OPTIONAL_PARAM` | New optional field in request body | PATCH |
| `REMOVED_PARAM` | Field removed from request body | **MAJOR** |
| `NEW_RESPONSE_FIELD` | New field in response schema | PATCH |
| `REMOVED_RESPONSE_FIELD` | Field removed from response schema | **MAJOR** |
| `RENAMED_FIELD` | Field renamed (removed + added with same type) | **MAJOR** |
| `TYPE_CHANGE` | Field type changed | **MAJOR** |
| `DESCRIPTION_ONLY` | Only description/docs changed | no bump |
| `NEW_ENUM_VALUE` | New value added to an enum | PATCH |
| `REMOVED_ENUM_VALUE` | Value removed from an enum | **MAJOR** |

### Version Recommendation

The version bump is the **highest impact** across all changes:
- Any MAJOR change → MAJOR bump
- Any MINOR change (and no MAJOR) → MINOR bump
- Only PATCH changes → PATCH bump
- Only DESCRIPTION_ONLY → no bump needed

### User Checkpoint

Present the changes to the user using `AskUserQuestion` with multi-select:

```
"Here's what changed in the OpenAPI specs:

v2:
- NEW_ENDPOINT: POST /skills/{id}/duplicate
- NEW_OPTIONAL_PARAM: sessions.create now accepts `browserWidth`
- REMOVED_RESPONSE_FIELD: tasks.get no longer returns `legacyField`

v3:
- (no changes)

Recommended version bump: MAJOR (due to removed field)

Which changes should I apply?"
```

Options should include each change + "All changes" + "Skip (just regenerate types)".

If there are **no changes** in the specs, tell the user and ask if they want to proceed anyway (useful for fixing SDK bugs or improving DX without spec changes).

---

## Phase 1: Types (Deterministic)

**Goal**: Regenerate type definitions from the fresh specs.

### Steps

1. Run `task gen:types` — this generates 4 files:
   - `browser-use-node/src/generated/v2/types.ts`
   - `browser-use-node/src/generated/v3/types.ts`
   - `browser-use-python/src/browser_use_sdk/generated/v2/models.py`
   - `browser-use-python/src/browser_use_sdk/generated/v3/models.py`

2. **Pydantic regex fix**: Check Python models for `constr` patterns with lookaheads. If found, add `model_config = ConfigDict(regex_engine="python-re")` to affected model classes.

3. Verify all 4 files were updated (check file modification times or git diff).

### No user interaction needed unless gen:types fails.

---

## Phase 2: SDK Code (AI-Driven)

**Goal**: Update SDK methods to match the new spec. Both TypeScript and Python.

### For Each Change

**NEW_ENDPOINT:**
1. Determine which resource it belongs to (e.g., `/skills/{id}/duplicate` → `skills` resource)
2. Read the existing resource file to understand the pattern
3. Add the new method following the same style:
   - TS: typed params from generated types, proper return type
   - Python: snake_case params, camelCase in body, `Dict[str, Any]` return
4. If it's a new resource entirely, create the resource file + wire it into the client

**MODIFIED_ENDPOINT:**
1. Read the current method
2. Update the signature to match new params/types
3. Update the body mapping if params changed
4. For Python: update the snake_case → camelCase mapping

**REMOVED_ENDPOINT:**
1. Remove the method from the resource file
2. Remove from spec.md resource table
3. Flag this clearly to the user — it's a breaking change

**NEW/REMOVED FIELDS:**
- Usually handled by type regeneration in Phase 1
- But verify: if the SDK has explicit field mappings (Python snake_case → camelCase), update those
- If a Python method has explicit named params and a new required param was added, add it

### Method Naming Convention

```
POST   /resource           →  resource.create()
GET    /resource           →  resource.list()
GET    /resource/{id}      →  resource.get(id)
DELETE /resource/{id}      →  resource.delete(id)
PATCH  /resource/{id}      →  resource.stop(id)   # action endpoints = named methods
GET    /resource/{id}/sub  →  resource.sub(id)
POST   /resource/{id}/act  →  resource.act(id)
```

### Both Languages, Same Patterns

Always update TS and Python together. They should have identical method coverage.

---

## Phase 3: Testing (AI-Driven)

**Goal**: Verify everything works. Fix what doesn't.

### Step 1: Vibe Tests (no backend needed)

```bash
task test
```

These are spec-driven: they read OpenAPI at runtime and verify every endpoint has an SDK method.

**If tests fail:**
1. Read the failure output carefully
2. Classify the failure:
   - **Test bug**: The test expects something that changed in the spec (e.g., test checks for a removed endpoint). Fix the test.
   - **SDK bug**: The SDK is missing a method or has wrong signature. Fix the SDK code.
   - **Type error**: Generated types don't match what the SDK expects. Usually means a type alias needs updating.
3. Fix and re-run. **Max 3 iterations.** If still failing after 3 attempts, interrupt the user with the failure details.

### Step 2: Live Tests (backend required)

Only run if `$BACKEND_URL` is reachable:

```bash
task test:live
```

**If live tests fail:**
1. Same classify + fix loop as above
2. Additional failure modes:
   - **Rate limit**: Too many active sessions. Clean up with stop/delete calls.
   - **Backend bug**: The API returns unexpected errors. Flag to user — this is a backend issue, not SDK.
   - **Auth error**: API key invalid. Flag to user.
3. **Max 3 iterations**, then escalate.

### Smart Checkpoint

Only interrupt the user if:
- Tests fail more than 2 consecutive times on the same issue
- A test failure reveals something unexpected (not related to the spec changes)
- You're unsure whether it's a test bug or SDK bug

---

## Phase 4: Docs

**Goal**: Keep all documentation in sync with the SDK.

### Steps

1. **spec.md**: Update resource tables if endpoints were added/removed/modified
2. **READMEs** (root, browser-use-node, browser-use-python): Update if new resources, new usage patterns, or significant changes
3. **CLAUDE.md**: Update if project structure changed (new files, new resources)
4. **Drift check**: Verify every OpenAPI endpoint has a corresponding SDK method by reading the spec and the resource files. Report any mismatches.

### Drift Check Algorithm

For each path+method in the OpenAPI spec:
1. Determine the expected resource + method name using the naming convention
2. Check it exists in both TS and Python resource files
3. If missing, flag it — either add it (Phase 2 missed it) or document why it's intentionally skipped

---

## Phase 5: Version + Commit

**Goal**: Bump versions, save snapshots, commit. Do NOT publish.

### Steps

1. **Confirm version** with the user:
   ```
   "Changes applied and tested. Recommended bump: MINOR (3.0.0 → 3.1.0).
   Reason: New endpoint POST /skills/{id}/duplicate added.

   Confirm version bump?"
   ```

2. **Bump both packages**:
   - TS: `cd browser-use-node && npm version <bump> --no-git-tag-version`
   - Python: Update version in `pyproject.toml`

3. **Save snapshots**: Copy the fresh specs to `snapshots/v2.json` and `snapshots/v3.json`

4. **Commit** with a descriptive message:
   ```
   sdk: v3.1.0 — add skills.duplicate()

   Changes:
   - Added POST /skills/{id}/duplicate → skills.duplicate()
   - Updated types from latest OpenAPI spec
   ```

5. **Print**: "Ready to publish. Review the commit, then run `task publish` when ready."

---

## Version Bump Rules

```
CHANGE                              BUMP
────────────────────────────────────────────────────
Endpoint removed                    MAJOR (x.0.0)
Required param added                MAJOR
Field removed from response         MAJOR
Field renamed                       MAJOR
Type changed                        MAJOR
Enum value removed                  MAJOR
New endpoint added                  MINOR (x.y.0)
New optional param added            PATCH (x.y.z)
New response field added            PATCH
New enum value added                PATCH
Bug fix in SDK helpers              PATCH
Description/docs only               no bump
```

---

## After Every Run: Self-Update

After completing all phases, check if this RUNBOOK needs updating:

1. Did you discover a new pattern? Add it to the Learnings section below.
2. Did a phase need steps that aren't documented? Add them.
3. Did you hit a gotcha that future runs should know about? Document it.
4. Update CLAUDE.md if the project structure changed.
5. Update the memory file with key learnings.

---

## Learnings

<!-- The AI appends notes here after each run. These persist across sessions. -->

- **List endpoints return `items`/`totalItems`/`pageNumber`/`pageSize`** — NOT resource-specific field names like `tasks` or `sessions`
- **V2 TaskStatus**: `created` | `started` | `finished` | `stopped` — there is no `failed` status. Failed = `finished` + `isSuccess: false`
- **V3 SessionStatus**: `created` | `idle` | `running` | `stopped` | `timed_out` | `error` — success = `idle`
- **V3 sessions.create returns 500 on localhost** — needs cloud infrastructure (Minerva model). Skip this test locally.
- **Pydantic regex**: `datamodel-codegen` generates `constr` patterns with lookaheads that need `ConfigDict(regex_engine="python-re")`
- **Rate limit**: Test account allows max 3 concurrent active sessions. Must clean up between test runs.
- **openapi-typescript**: Generates `components["schemas"]["TypeName"]` pattern, not direct exports. Resource files use local type aliases.
- **Python SDK type safety**: All resource methods return Pydantic model instances (via `model_validate()`), NOT `Dict[str, Any]`. Live tests use attribute access (`result.id`, `result.status`), not dict access (`result["id"]`).
- **Structured output**: V2 supports `structuredOutput` (stringified JSON schema). Python auto-converts Pydantic models via `output_schema` parameter. TS requires manual JSON schema string + `outputSchema` for parsing. V3 does NOT support structured output.
- **Polling uses lightweight endpoint**: `TaskHandle.complete()` polls with `tasks.status()` (lightweight), then fetches full `tasks.get()` on terminal. `stream()` yields `TaskStatusView` objects.
