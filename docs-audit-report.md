# Browser Use Docs Audit Report

**Date:** 2026-03-30
**Method:** 14 autonomous agents testing docs from different personas, code snippets, API types, links, llms.txt, and e2e flows.
**Previous audit:** 2026-03-29 (6 agents, 47 issues). This audit is more comprehensive.

---

## Executive Summary

| Area | Score | Status |
|------|-------|--------|
| **Overall Docs Quality** | **6.2/10** | Good foundation, significant gaps |
| **Code Snippets (Python)** | **9.5/10** | 49/49 syntax pass, 1 SDK publish issue |
| **Code Snippets (TypeScript)** | **7.7/10** | 34/44 pass, 4 SDK type bugs, 3 doc bugs |
| **API Reference** | **5/10** | Wrong auth header (critical), many missing descriptions |
| **llms.txt** | **7.5/10** | Good structure, needs less marketing, more params |
| **Broken Links** | **3 found** | 1 internal, 2 external (dead GitHub repos) |
| **Chat UI Example** | **4/10** | BLOCKER: published SDK missing asyncIterator |

---

## BLOCKERS (Fix Before Anything Else)

### 1. Published npm SDK (v3.3.1) missing `Symbol.asyncIterator`
- **Impact:** `for await (const msg of run)` throws "run is not async iterable"
- **Affects:** Chat UI example, streaming docs, every persona that tried streaming
- **Root cause:** Local source has it (`helpers.ts:102`), but published dist is an older build (207 lines vs 451)
- **Fix:** Republish npm package from current source
- **Found by:** Chat UI tester, Automation persona, Embedder persona

### 2. Published PyPI SDK (v3.3.1) missing v3 resources
- **Impact:** `client.browsers`, `client.profiles`, `client.billing` don't exist on published package
- **Affects:** Proxies docs, Playwright integration, profile/auth docs
- **Root cause:** Local source has all 5 resources, published package only has `sessions` + `workspaces`
- **Fix:** Republish PyPI package from current source
- **Found by:** Python snippets tester

### 3. `api-reference.mdx` uses wrong auth header
- **Impact:** Every curl example on the hand-written API reference page fails
- **Current (wrong):** `Authorization: Bearer bu_your_key_here`
- **Correct:** `X-Browser-Use-API-Key: bu_your_key_here`
- **Note:** Auto-generated Mintlify API pages are correct; only the hand-written overview is wrong
- **Found by:** API types checker

---

## Code Snippet Audit

### Python (49 snippets tested)
- **49/49 syntax pass** (100%)
- **9/11 live tests pass** (2 failures were test setup issues, not doc bugs)
- **1 warning:** `browsers.create(custom_proxy=...)` sends snake_case key via `**extra` instead of camelCase `customProxy`. Need to add `custom_proxy` as explicit parameter.

### TypeScript (44 snippets tested)
- **34/44 pass** (77%)
- **4 SDK type bugs:** `browsers.create()` requires `timeout`, `allowResizing`, `enableRecording` as required fields (they have API defaults, should be optional in types)
- **3 doc bugs (wrong property names):**
  - `legacy/agent.mdx`: `upload.presignedUrl` → should be `upload.url`
  - `legacy/agent.mdx`: `output.presignedUrl` → should be `output.downloadUrl`
  - `legacy/public-share.mdx`: `share.url` → should be `share.shareUrl`
- **1 null-safety issue:** `streaming.mdx`: `run.result.output` → should be `run.result!.output` or `run.result?.output`
- **2 expected failures:** External deps (playwright, puppeteer-core) not installed

---

## Broken Links

| Type | File | Link | Issue |
|------|------|------|-------|
| Internal | `cloud/browser/proxies.mdx:7` | `/cloud/api-v3/browsers/create-browser` | 404 — correct: `/cloud/api-v3/browsers/create-browser-session` |
| External | `open-source/browser-use-cli.mdx:274` | `github.com/browser-use/profile-use` | Repo doesn't exist |
| External | `open-source/customize/integrations/mcp-server.mdx:240` | `github.com/browser-use/browser-use/tree/main/examples/mcp` | Directory doesn't exist |

---

## API Reference Discrepancies

| # | Severity | Issue |
|---|----------|-------|
| 1 | **Critical** | Auth header wrong in `api-reference.mdx` (see Blockers) |
| 2 | Should fix | `RunTaskRequest` — 13 fields have no description in OpenAPI spec |
| 3 | Should fix | `SessionResponse` — all fields missing descriptions (titles are just camelCase names) |
| 4 | Should fix | `GET /workspaces/{id}/size` — response schema is `{}` (empty) |
| 5 | Should fix | Default `maxCostUsd` of $20 is undocumented |
| 6 | Nice to have | `totalInputTokens`/`totalOutputTokens` meaning unclear |
| 7 | Nice to have | `agentmailEmail` returned by default but not explained |
| 8 | Nice to have | `output` field typed as "any" in spec but rendered as "object" in docs |

---

## Persona Scorecard

### Persona 1: AI Automation Startup ("just run tasks fast")
| Metric | Score |
|--------|-------|
| Intuitiveness | 7/10 |
| Time-to-value | 8/10 |
| Completeness | 5/10 |

**Journey:** 4 pages to first successful task. `client.run()` is genuinely simple.
**Friction:** Two quickstart pages confuse; streaming broken; no pricing/cost info; no error handling examples.
**Key ask:** Consolidate quickstarts, add pricing section, fix streaming.

### Persona 2: Enterprise User
| Metric | Score |
|--------|-------|
| Security docs | 4/10 |
| Enterprise readiness | 3/10 |
| Clarity | 6/10 |

**Gaps (critical for enterprise):**
- No compliance page (SOC 2, GDPR, data residency)
- No data retention/deletion policy
- No API key scoping, rotation, or RBAC
- No audit logging
- No SLA documentation
- `curl | sh` profile sync is a red flag
- Auth story fragmented across 4 pages with no unifying guide

### Persona 3: Sub-agent Embedder (live browser in app)
| Metric | Score |
|--------|-------|
| Embed docs | 6/10 |
| Streaming docs | 3/10 |
| Overall flow | 5/10 |

**Friction:** Must read 4 pages to assemble the embed pattern. `liveUrl` is null from simple `run()` — not documented. Streaming broken in published SDK.
**Key ask:** Add "Embed in Your App" recipe page showing full flow in one place.

### Persona 4: QA Tester
| Metric | Score |
|--------|-------|
| QA docs | 4/10 |
| Playwright integration | 8/10 |
| Clarity | 6/10 |

**Friction:** No dedicated QA/testing guide. No CI/CD examples. No screenshot example on Playwright page. No parallel session guidance.
**Key ask:** Add a "Testing & QA" guide page with pytest/Jest fixtures, CI/CD patterns, visual regression.

### Persona 5: Data Extraction at Scale
| Metric | Score |
|--------|-------|
| Extraction docs | 4/10 |
| Structured output | 6/10 |
| Proxy docs | 4/10 |

**Friction:** No dedicated extraction guide. No concurrency/parallel execution docs. No pagination guidance. No cost estimation. No complex schema examples.
**Key ask:** Add "Data Extraction at Scale" guide with parallel patterns, pagination, proxy rotation.

---

## llms.txt Evaluation

**Score: 7.5/10**

**What's good:**
- Strong structure, clear hierarchy
- Inline code for quick start (most llms.txt files don't do this)
- v3 callout prevents outdated code generation
- Pointer to llms-full.txt

**What to improve:**
1. Blockquote is too marketing-heavy ("most SOTA", "most scalable") — LLMs need facts, not persuasion
2. Duplicate GitHub link (lines 5 and 8)
3. No `## Optional` section for legacy/v2 content (per llmstxt.org spec)
4. Top-level links are unstructured — should be under `## Resources`
5. No size hint for llms-full.txt (~60KB)
6. Links point to HTML pages, not `.md` variants (if Mintlify supports them)
7. Missing key parameters list for `client.run()`

**llms.txt navigation test (can AI build from it alone?):**
- llms.txt navigability: **8/10** — great sitemap, but not enough to write code beyond basics
- llms-full.txt completeness: **7/10** — good but has zod v4 omission and wrong `client.profiles` examples for TS

---

## Chat UI Example

**Score: 4/10**

**BLOCKER:** Published SDK doesn't have `Symbol.asyncIterator`, so `npm run build` fails with:
```
Type 'SessionRun<string>' must have a '[Symbol.asyncIterator]()' method
```

**Other issues:**
- Docs page has ZERO setup commands (no `git clone`, `npm install`, `npm run dev`)
- It's a conceptual guide, not a tutorial — setup instructions only exist in the GitHub repo README
- Should at minimum include quick-start commands on the docs page

---

## File Upload/Download

**Score: Docs 6/10, Functionality 8/10**

**What works:** All file types upload/download correctly. Round-trip integrity confirmed. Agent can read uploaded files and write new ones.

**What's missing from docs:**
- File size limits
- Supported file types (SDK supports 20+ MIME types, undocumented)
- `prefix` parameter for organizing files
- `delete_file()` method
- `size()` endpoint
- Workspace lifecycle/persistence
- Agent leaves cache artifacts in workspace (undocumented)

---

## Profile System

**Score: Docs 7/10, API 8/10, SDK 9/10**

**Key issue:** Main profiles doc is `authentication.mdx` at URL `/guides/authentication` under sidebar group "Authentication". A user searching for "profiles" won't find it easily.

**Missing:**
- No explanation of what a profile actually stores
- `user_id` field is undocumented
- No curl/raw API examples
- Warning about `sessions.stop()` saving profile state is buried at bottom

---

## Top 10 Recommendations (Priority Order)

### Must Fix Now
1. **Republish npm package** — include `Symbol.asyncIterator` in v3 dist
2. **Republish PyPI package** — include `browsers`, `profiles`, `billing` resources in v3
3. **Fix auth header in `api-reference.mdx`** — change `Authorization: Bearer` to `X-Browser-Use-API-Key`
4. **Fix 3 broken links** (proxies internal link, 2 dead GitHub repos)

### Should Fix Soon
5. **Fix TS doc bugs** — wrong property names in legacy docs (`presignedUrl` → `url`/`downloadUrl`, `share.url` → `share.shareUrl`)
6. **Fix SDK types** — make `CreateBrowserSessionRequest` fields with defaults optional; add `custom_proxy` as explicit param to Python `browsers.create()`
7. **Add setup commands to chat-ui tutorial page** (clone, install, env, run)

### Should Add (New Content)
8. **"Embed in Your App" recipe page** — single page showing full embed flow
9. **"Data Extraction at Scale" guide** — parallel patterns, pagination, complex schemas
10. **"Testing & QA" guide** — pytest/Jest fixtures, CI/CD, screenshots, parallel sessions

### Nice to Have
- Consolidate two quickstart pages into one
- Add OpenAPI field descriptions for RunTaskRequest and SessionResponse
- Add `## Optional` section to llms.txt for legacy content
- Rewrite llms.txt blockquote to be factual, not marketing
- Add pricing/cost section to docs
- Add error handling examples
- Document `maxCostUsd` default of $20
- Document workspace lifecycle and file size limits
- Rename `authentication.mdx` → `profiles.mdx` (or add "Profiles" to sidebar title)
- Add unified "Authentication Architecture" page for enterprise users
- Add compliance/security page for enterprise evaluation
- Document concurrency limits and parallel execution patterns
- Add zod v4 requirement note to structured output docs

---

*Report generated by 14 autonomous agents testing docs from different angles.*
*Full path: `/Users/magnus/.superset/worktrees/sdk/magnus/citrine-function/docs-audit-report.md`*
