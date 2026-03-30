# Browser Use Docs Audit Report

**Date:** 2026-03-30
**Method:** 12 parallel AI agents with different personas and test objectives
**Scope:** All cloud docs, llms.txt, code snippets, API spec, chat UI example, link integrity

---

## Executive Summary

| Area | Score | Critical Issues |
|------|-------|-----------------|
| **llms.txt** | 7/10 | Marketing-heavy blockquote, missing `## Optional`, Python snippet incomplete |
| **Python Snippets** | 25/26 pass | `proxy_country_code=None` doesn't disable proxies |
| **TypeScript Snippets** | 18/28 pass | **Published SDK (v3.3.1) missing browsers, profiles, upload/download, async iterator** |
| **Chat UI Example** | BROKEN | `npm run build` fails -- `SessionRun` has no `[Symbol.asyncIterator]` in published SDK |
| **API Spec vs Docs** | 12 discrepancies | **Auth header wrong in cURL examples and llms-full.txt** |
| **Broken Links** | 1 broken | `github.com/browser-use/browser-use-cli` is 404 |
| **Persona: AI Startup** | 7.4/10 | No concurrency/parallel docs anywhere |
| **Persona: Sub-agent Embedder** | 7.2/10 | CSP/iframe guidance missing, streaming events undocumented |
| **Persona: QA Tester** | 5.5/10 | No Playwright feature compatibility matrix, no migration guide |
| **Persona: Data Extraction** | 5.8/10 | No "scraping at scale" guide, no rate limits, no parallel examples |
| **Persona: Enterprise** | 5.1/10 | No security/compliance page at all |
| **File Upload/Profiles** | 6.3/10 | Undocumented SDK methods, inconsistent patterns, missing `stop()` in examples |

**Overall Docs Intuitiveness Score: 6.2/10**

---

## P0: Critical / Blocking Issues

### 1. Chat UI Example is Broken
- `npm run build` fails: `SessionRun<string>` has no `[Symbol.asyncIterator]()` in published SDK (v3.2.0)
- The core streaming feature doesn't work -- users cannot clone and run this
- Docs show simplified architecture that doesn't match actual code (SSE route handler missing from tutorial)
- Docs reference `src/lib/session-context.tsx` but actual path is `src/context/session-context.tsx`

### 2. Auth Header Wrong in cURL Examples + llms-full.txt
- OpenAPI spec: `X-Browser-Use-API-Key` header
- `agent/quickstart.mdx` cURL: uses `Authorization: Bearer` -- **WRONG**
- Both `llms-full.txt` files: use `Authorization: Bearer` -- **WRONG**
- Every LLM consuming llms-full.txt will generate broken API calls

### 3. Published TS SDK Missing Major Features
The npm package `browser-use-sdk@3.3.1` does not export features the docs reference:
- `client.browsers` (6 snippets broken)
- `client.profiles` (2 snippets broken)
- `workspaces.upload()`, `.download()`, `.downloadAll()` (3 snippets broken)
- `sessions.waitForRecording()` (1 snippet broken)
- `SessionRun[Symbol.asyncIterator]` (streaming broken)
- **~35% of TS code examples in docs fail with the published package**

### 4. `proxy_country_code=None` Doesn't Disable Proxies
- SDK uses `if proxy_country_code is not None:` guard -- passing `None` just omits the field
- API default (US proxy) still applies
- Docs claim this disables proxies -- it doesn't
- Affects both Python and TS SDKs

---

## P1: High Priority Issues

### 5. Concurrency/Parallel Execution Not Documented Anywhere
- Zero examples of running parallel sessions across entire docs
- No `asyncio.gather()` / `Promise.all()` patterns shown
- No rate limits documented (just "contact support")
- No concurrency caps mentioned
- **Blocks: AI startups, data extraction, QA testing personas**

### 6. Model Values Undocumented
- OpenAPI spec defines `bu-mini`, `bu-max`, `bu-ultra`
- No docs page lists available models or explains the differences
- Users have to guess or read the spec

### 7. SessionResponse Rich Fields Never Documented
- `isTaskSuccessful` -- success/failure boolean
- `totalCostUsd`, `llmCostUsd`, `proxyCostUsd`, `browserCostUsd` -- cost breakdown
- `totalInputTokens`, `totalOutputTokens` -- token usage
- `stepCount`, `lastStepSummary` -- progress tracking
- `screenshotUrl` -- last screenshot
- Users don't know these exist

### 8. No Security/Compliance Page
- No SOC 2, GDPR, DPA documentation
- No data retention policy
- No encryption (at rest/in transit) documentation
- No RBAC or API key scoping
- No audit logging
- TOTP secrets travel as plaintext in prompts
- **Blocks enterprise adoption**

### 9. Task Lifecycle/Status Mapping Never Explained
- Webhook statuses: `running`, `idle`, `stopped` -- but no `completed`?
- `idle` listed as terminal in streaming docs but means "session alive, task done"
- No state diagram showing: created -> running -> idle/stopped/error/timed_out
- Confusing across multiple pages

### 10. `sessions.stop()` Missing From Profile Examples
- Warning says "Always call `sessions.stop()` when done" to persist profile state
- Zero code examples actually call `sessions.stop()`
- Data-loss footgun -- users copy examples, skip stop, lose profile state

---

## P2: Medium Priority Issues

### 11. llms.txt Improvements
- Blockquote too marketing-heavy -- should be technical ("Browser Use Cloud is a managed API for...")
- Missing `## Optional` section -- Legacy/v2 content should go there
- Python quick start missing `asyncio.run()` wrapper
- Duplicate GitHub link (lines 5 and 8)
- No curl example
- No LLM behavioral instructions (e.g., "Always use v3")

### 12. Profile Docs Inconsistencies
- Two-step flow shown when `client.run(..., profile_id=...)` works directly (simpler)
- Workspaces docs use the simpler one-step pattern -- inconsistent
- `user_id` field on `profiles.create()` undocumented (key production pattern)
- No full lifecycle example (create -> login -> save -> reuse later)
- Profile sync page too thin -- doesn't explain what the `curl | sh` script does

### 13. Workspace Docs Gaps
- `workspaces.files()` undocumented -- users can't inspect workspace contents
- `workspaces.delete_file()` undocumented
- `workspaces.size()` undocumented
- `prefix` parameter for directory organization undocumented
- No file size limits or supported types documented
- No explanation of how agent accesses files (mount path?)
- **TS SDK bug**: `download()` doesn't paginate -- fails for workspaces with many files

### 14. QA Testing Gaps
- No Playwright feature compatibility matrix (screenshots? network interception? tracing?)
- No migration guide from existing Playwright tests
- No CI integration guidance (GitHub Actions, Jenkins)
- Network/staging access model undocumented ("Can the browser reach my private server?")
- No parallel browser session docs for test suites

### 15. Data Extraction Gaps
- No "Scraping at Scale" guide
- Proxy rotation across sessions undocumented
- Pagination patterns not covered
- No batch/queue API guidance
- CAPTCHA solving mentioned in quickstart but never explained
- No cost estimation guidance

### 16. Streaming Event Types Undocumented
- `role` and `type` fields mentioned but all possible values never listed
- Developers building UIs must guess what event shapes look like
- No error handling/reconnection patterns for stream failures

### 17. CSP/iframe Embedding Undocumented
- Live preview iframe embedding shown but CSP `frame-ancestors` issues never mentioned
- Guaranteed production blocker for anyone embedding the browser view
- No responsive sizing guidance

### 18. Human-in-the-Loop is CLI-Only
- Examples use `input()` / readline -- only works in CLI
- No web app pattern (webhook, button click, state machine)
- No timeout/cleanup guidance (what if human never resumes?)

---

## P3: Low Priority / Polish

### 19. Broken External Link
- `https://github.com/browser-use/browser-use-cli` in `browser-use-cli.mdx` -- 404

### 20. Orphaned Pages
- `open-source/development.mdx` -- not in navigation, not linked
- `open-source/customize/skills/basics.mdx` -- only referenced from agent params page
- `open-source/development/roadmap.mdx` -- empty ("Big things coming soon!")

### 21. Minor Type Issues
- `browsers.create()` -- OpenAPI codegen makes defaulted fields required instead of optional
- `run.result.output` -- null safety issue (`result` can be null)
- `profileId` type UUID vs string inconsistency between spec and SDK

### 22. Docs vs Chat UI Code Discrepancies
- Docs import only v3, actual code imports both v2 and v3 (profiles not on v3 yet)
- Docs show `for await` in context, actual code uses SSE route handler pattern
- SSE route handler architecture completely absent from tutorial
- `createSession` in actual code accepts many more params than docs show

---

## Persona Scorecards

### AI Automation Startup (15-20 min to first success)
| Page | Clarity | Completeness | Time to Success | Code Quality |
|------|---------|-------------|-----------------|-------------|
| Quickstart | 8 | 6 | 9 | 8 |
| Structured Output | 9 | 7 | 8 | 9 |
| Agent Quickstart | 7 | 5 | 8 | 7 |
| Webhooks | 8 | 7 | 7 | 8 |
| Vibecoding | 6 | 3 | N/A | N/A |
| **Blocking issue:** No concurrent/parallel execution docs |||||

### Sub-agent Embedder (2-4 hours to prototype)
| Page | Score | Notes |
|------|-------|-------|
| Quickstart | 7 | No mention of liveUrl, streaming, or sessions |
| Live Preview | 6 | No CSP guidance, no responsive sizing |
| Streaming | 8 | Best page -- `for await` is the aha moment |
| Human in the Loop | 7 | CLI-only examples |
| Follow-up Tasks | 7 | "Agents don't share context" is alarming, under-explained |
| Chat UI Tutorial | 8 | Ties everything together, but broken in practice |
| **Blocking issue:** CSP, streaming event reference, broken chat UI ||

### QA Tester (2-4 hours basic migration)
| Page | Score | Notes |
|------|-------|-------|
| Quickstart | 5 | Not oriented toward QA use case |
| Playwright/CDP | 8 | Strongest page -- CDP flow crystal clear |
| Stealth | 4 | Low relevance for testing own app |
| Proxies | 5 | Doesn't explain network access model |
| Authentication | 7 | No Playwright-with-profile flow shown |
| Live Preview | 7 | No screenshot support clarity |
| **Blocking issue:** No feature compatibility matrix, no parallel sessions, no CI guide ||

### Data Extraction at Scale
| Page | Score | Notes |
|------|-------|-------|
| Quickstart | 5 | No scale/batch patterns |
| Structured Output | 7 | Good pattern, no failure handling |
| Proxies | 6 | No rotation docs |
| Stealth | 6 | No success rate info |
| Agent Quickstart | 7 | Mentions "thousands of listings" but no example |
| FAQ | 4 | Rate limits = "contact support" |
| **Blocking issue:** No scale guide, no concurrency docs, no pricing ||

### Enterprise Architect (5.1/10 overall)
| Area | Score | Notes |
|------|-------|-------|
| API Key Security | 4 | No RBAC, no key scoping, no rotation docs |
| Data Handling | 3 | No retention policy, no encryption docs |
| Compliance | 1 | No SOC 2, GDPR, DPA -- nothing |
| Webhooks | 8 | Proper HMAC-SHA256 -- best security page |
| Integration | 5 | MCP works, no SSO/SAML |
| Reliability | 3 | No SLA, no status page, no error codes |
| **Blocking issue:** No security page exists at all ||

---

## Top 10 Recommendations (Priority Order)

1. **Publish the SDK** -- browsers, profiles, upload/download, waitForRecording, async iterator all need to ship to npm/PyPI
2. **Fix auth header** in `agent/quickstart.mdx` cURL and both `llms-full.txt` files (use `X-Browser-Use-API-Key`)
3. **Fix chat UI example** -- either publish SDK with async iterator or rewrite to use polling
4. **Add concurrency/parallel docs** -- examples, rate limits, caps. Every persona needs this
5. **Add a security/trust page** -- SOC 2 status, data retention, encryption, DPA availability
6. **Document model values** -- what are `bu-mini`, `bu-max`, `bu-ultra` and when to use each
7. **Document SessionResponse fields** -- cost breakdown, token usage, isTaskSuccessful
8. **Add task lifecycle state diagram** -- created -> running -> idle/stopped/error/timed_out
9. **Fix proxy disable docs** -- `None`/`null` doesn't disable proxies, document the correct way
10. **Add `sessions.stop()` to all profile examples** -- prevent data loss

---

## Methodology

12 AI agents ran in parallel, each with a specific persona or test objective:

| Agent | Duration | Findings |
|-------|----------|----------|
| Chat UI Tester | 4.8 min | Build broken, code/docs mismatch |
| llms.txt Researcher | 3.0 min | 7/10 score, 7 improvements identified |
| Python Snippets | 3.2 min | 26 checked, 1 bug found |
| TS Snippets | 7.5 min | 28 checked, 10 issues (SDK publishing gap) |
| API Types Checker | 3.7 min | 12 discrepancies, auth header critical |
| Link Checker | 7.5 min | 1 broken external link, 3 orphaned pages |
| Persona: AI Startup | 2.7 min | Concurrent execution is #1 gap |
| Persona: Embedder | 2.4 min | CSP and streaming events undocumented |
| Persona: QA | 2.0 min | No Playwright compat matrix |
| Persona: Scraper | 2.3 min | No scale guide |
| Persona: Enterprise | 2.3 min | No security page |
| File/Profiles | 3.0 min | Inconsistent patterns, undocumented methods |
