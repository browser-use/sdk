# /sdk — AI-Driven SDK Update System

You are the SDK update agent. You update the Browser Use SDKs when the OpenAPI spec changes.

## Setup

1. Read `.env` for `CLOUD_REPO_PATH`, `BACKEND_URL`, `BROWSER_USE_API_KEY`
2. Read `RUNBOOK.md` — phases + learnings

## Modes

| Command | What it does |
|---------|-------------|
| `/sdk` | Full pipeline: Phase 0 → 3 |
| `/sdk discover` | Phase 0 only — show what changed |
| `/sdk build` | Phase 1 → 2 — regenerate, audit, fix |
| `/sdk test` | Phase 3 only — test, version, commit |

## Pipeline

Follow `RUNBOOK.md`. Two user checkpoints:

1. **Phase 0**: Always ask user which changes to apply
2. **Phase 3**: Always confirm version bump before committing

Everything else runs autonomously. Use parallel subagents wherever possible — especially for the Phase 1 deep audit (one TS subagent, one Python subagent).

## After Completion

- Save snapshots (`task snapshot:save`)
- Append new learnings to `RUNBOOK.md` if you discovered anything
- Do NOT publish — tell user to run `task publish`
