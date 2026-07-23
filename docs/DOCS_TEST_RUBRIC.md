# Cold-agent docs test — rubric (the AX acceptance gate)

Internal. Delete before publish. The test: a zero-context agent, given ONLY the docs root URL, must accomplish each scenario from the docs alone. Run this after any docs/model change.

## Setup
- `mint dev` serving the docs at localhost:3000. API is NOT live (docs-only test — agent writes the code it would call).
- Agent gets ONLY `http://localhost:3000` + the task. Must discover `/llms.txt`, pages, base URL, auth, everything.

## The 10 scenarios (span the full config surface)
1. Simple run — "top 5 HN titles", get result. (hot path only)
2. Follow-up — run, then continue same thread. (hot path: session_id reuse)
3. Structured JSON output — define a schema, get typed output.
4. Geo proxy — run through Germany.
5. Login via saved profile. (setup: browser-profile)
6. Upload file → process → get output file. (setup + files)
7. Fetch the browser recording after a run.
8. Find + download the browser's downloads.
9. Raw polling — run, poll status to done, read output (no blocking SDK helper).
10. Coding/data task — pick the right agent (browsercode).

## Scoring (per scenario)
- **YES** — done cleanly from docs, minimal calls, no guessing.
- **PARTIAL** — done but with friction (had to hunt, ambiguous field, extra reads).
- **NO** — got stuck, guessed wrong, or 404'd.

## Pass bar
- Scenarios 1, 2, 9 (pure hot path) MUST be YES. If not, the core model failed.
- 3, 4, 10 (run config + agent choice) should be YES.
- 5, 6, 7, 8 (leave the hot path) may be PARTIAL, but the agent must clearly SEE it's leaving the hot path (the "optional setup" quarantine working).

## What we harvest each run
- TOP-5 confusions (→ each becomes a doc fix or explicit DON'T).
- Any hallucinated endpoint/field (→ add a redirect + a DON'T callout).
- Did the core model land (run→ids→reuse) or did sessions/workspaces/browsers confuse.
- Which scenarios forced leaving the hot path + how obvious it was.

## History

### Run 1 (2026-07-17) — 7 YES, 3 PARTIAL, 0 NO
- Core model (run→ids→reuse) PASSED — agent said the model page inoculated it against session/workspace/browser confusion on the hot path.
- PARTIAL: #6 files (broken upload placeholder), #7 recording (v3-sessions vs v1-browsers contradiction), #8 downloads-vs-attachments (never contrasted).
- Findings: legacy v3 bleed (live-preview, FAQ, tutorials use sessions.create/wait_for_recording), 3 conflicting SDK imports, broken /cloud/api-reference link.

### Run 2 (2026-07-17) — 10 YES, 0 PARTIAL, 0 NO
- All three prior PARTIALs (6,7,8) FIXED and verified clean. Core model held throughout.
- Remaining findings: legacy v3 still in FAQ/playwright/tutorials presenting as current; broken api-reference link.
- **Fixes applied after run 2:** playwright import → v1; broken link → /cloud/api-v1-reference; moved FAQ + x402 + 2fa + chat-ui + grow-therapy to the Legacy tab; dropped v1→legacy cross-links (live-preview→chat-ui, authentication→2fa). Verified: current Documentation nav (30 pages) is 100% v3-free.
- Status: core abstraction validated by cold agent (10/10); current surface clean. Next: optional live test via a mock server.
