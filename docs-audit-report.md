# Browser Use Cloud SDK Documentation — Full Audit Report

**Date**: 2026-03-29
**Audited by**: 6 parallel agents testing every section, API endpoint, and LLM readability

---

## Executive Summary

- **All API endpoints work** — zero failures across 76+ API calls
- **Core DX is good** — 3-line quickstart, clean SDK, $0.04 for a real task
- **47 issues found** across docs, API spec, and LLM readability
- **Top 3 systemic problems**: no REST/curl examples, undocumented session lifecycle, v2/v3 import confusion

---

## CRITICAL Issues (fix immediately)

### 1. `maxCostUsd` defaults to $20 — UNDOCUMENTED
Every session defaults to a $20 cost cap. A developer could accidentally spend $20 on a single task without knowing. Must be documented prominently.

### 2. POST /sessions returns 201, OpenAPI spec says 200
Code generators and SDK validation will break. Fix the spec.

### 3. Python streaming example has a bug
`sessions.create("task")` should be `sessions.create(task="task")` — string positional arg doesn't match the API.

### 4. Secrets page has two conflicting formats
- Example 1: `{"github.com": "username:password123"}` (domain-keyed)
- Example 2: `{"username": "user@company.com", "password": "password123"}` (field-keyed)
Which is correct? Both? Completely confusing.

### 5. n8n integration references deprecated v2 endpoints
Uses `/api/v2/tasks` — must be updated to v3 sessions API.

---

## HIGH Issues

### Documentation Gaps

| # | Issue | Location |
|---|-------|----------|
| 6 | No REST/curl examples anywhere — every page is SDK-only | All pages |
| 7 | No v3 parameter reference table (run() params scattered across pages) | Agent section |
| 8 | No v3 model/pricing table (bu-mini, bu-max — no costs, no tradeoffs) | Missing entirely |
| 9 | No session lifecycle documentation (statuses, timeouts, transitions) | Missing entirely |
| 10 | No error handling examples anywhere | Missing entirely |
| 11 | Auth header `X-Browser-Use-API-Key` never mentioned in docs (only in OpenAPI spec) | API reference, all pages |
| 12 | Agent introduction is near-duplicate of quickstart — adds nothing new | agent/quickstart.mdx |
| 13 | `agentmailEmail` field in every session response — never documented | Missing |
| 14 | Browser stop REST endpoint undocumented (SDK has it, REST doesn't) | browser docs |
| 15 | Stealth page rated 5/10 — core value prop reads like bullet-point teaser | browser/stealth.mdx |
| 16 | FAQ has 4 broken anchor links | faq.mdx |
| 17 | Webhooks doc doesn't explain where to get the signing secret | webhooks.mdx |

### API Spec Issues

| # | Issue | Location |
|---|-------|----------|
| 18 | RunTaskRequest: zero field descriptions (task, model, sessionId, etc.) | v3.json |
| 19 | SessionResponse: zero field descriptions | v3.json |
| 20 | GET /workspaces/{id}/size response schema is empty `{}` | v3.json |
| 21 | 401 error responses not documented in spec | v3.json |
| 22 | Three different pagination styles across endpoints | v3.json |
| 23 | Messages pagination: `hasMore` is misleading (means "older messages exist", not "newer") | v3.json |
| 24 | Session files tagged as "Files" not "Sessions" — splits sidebar | v3.json |

### Code Issues

| # | Issue | Location |
|---|-------|----------|
| 25 | TypeScript profiles example has duplicate `const profile` declaration | authentication.mdx |
| 26 | CDP URL comment says `ws://` but API returns `https://` | playwright.mdx |
| 27 | `str(session.id)` vs `session.id` inconsistency across pages | Multiple |
| 28 | `output_schema` (Python) vs `schema` (TypeScript) naming not explained | structured-output.mdx |

---

## MEDIUM Issues

| # | Issue | Location |
|---|-------|----------|
| 29 | MCP Server missing VS Code and Cline client configs | mcp-server.mdx |
| 30 | Chat UI uses v2 import for profiles — may be outdated | chat-ui.mdx |
| 31 | Chat UI says "streaming" but implementation is polling | chat-ui.mdx |
| 32 | Playwright/Puppeteer under Authentication grouping in llms.txt | llms.txt |
| 33 | Structured output example uses LinkedIn (requires auth) — bad test example | structured-output.mdx |
| 34 | No mention of message types (browser_action, completion_result, etc.) | streaming.mdx |
| 35 | `screenshotUrl` in messages — undocumented but valuable for UIs | streaming.mdx |
| 36 | Profile sync pipes remote script to shell — no security note | profile-sync.mdx |
| 37 | 1Password URL points to EU domain only (`my.1password.eu`) | 1password.mdx |
| 38 | No mention of recording cost or URL expiration | live-preview.mdx |
| 39 | No connection limits documented for concurrent browsers | playwright.mdx |
| 40 | Vibecoding page is essentially empty (just a link) | vibecoding.mdx |
| 41 | OpenClaw integration is very long relative to importance in llms-full.txt | llms-full.txt |
| 42 | `DELETE /sessions` is soft delete — still accessible after | API behavior |

---

## LOW Issues

| # | Issue | Location |
|---|-------|----------|
| 43 | Title "Introduction Stealth" reads awkwardly | stealth.mdx |
| 44 | `POST /sessions` requires `{}` body even when empty | API behavior |
| 45 | Double redirects (e.g., `/examples` → tips → agent) | docs.json |
| 46 | FAQ uses redirect-based `/cloud/pricing` links | faq.mdx |
| 47 | n8n doc too thin to be useful | n8n.mdx |

---

## LLM Readability (llms.txt / llms-full.txt)

### What's good
- Grouped sections matching nav structure
- Install commands + API key link at top
- Benchmark links for positioning

### What's missing
- No v3 parameter reference table (highest-value addition)
- No error handling patterns
- No sub-agent integration pattern (top ICP use case)
- Benchmark numbers not inlined (LLMs can't click links)
- Missing keywords: "web scraping", "headless browser", "data extraction API"
- No competitor differentiation (vs Browserbase, Playwright, Selenium)
- `<CodeGroup>`, `<Note>` Mintlify tags remain as noise in plain text

### Recommendations
1. Add v3 parameter table with all run() options
2. Add "Using Browser Use as a Sub-Agent" section (10-line pattern)
3. Inline benchmark scores instead of just linking
4. Add "Why Browser Use" section with differentiators
5. Trim OpenClaw details and duplicate API key sections to save tokens

---

## Test Results

### Sub-agent Integration Test
- **27 API calls** for workspace + task + download flow
- **62 seconds** end-to-end
- **$0.04** total cost
- **Zero errors**
- Agent correctly extracted data and saved structured JSON to workspace
- Recording returned valid MP4 URL
- Live URL appeared within 6 seconds

### API Endpoint Test (all v3)
- **All 22 endpoints tested** — all work
- **Profiles**: create, list, search, get, update, delete — all work
- **Workspaces**: create, upload, list files, download, size, delete — all work
- **Browsers**: create, list, get, stop — all work
- **Sessions**: create, get, messages, files, stop, delete — all work
- **Billing**: account info works

---

## Priority Action Items

### P0 (This week)
1. Document `maxCostUsd` default of $20 with a warning
2. Fix OpenAPI spec: POST /sessions → 201
3. Fix Python streaming bug
4. Fix secrets page format confusion
5. Update n8n to v3

### P1 (Next sprint)
6. Add curl/REST examples to quickstart + key pages
7. Add v3 parameter reference table
8. Add session lifecycle documentation
9. Add field descriptions to OpenAPI spec (RunTaskRequest, SessionResponse)
10. Fix FAQ broken anchor links
11. Expand stealth page significantly

### P2 (Backlog)
12. Add error handling examples
13. Add sub-agent integration pattern
14. Add model/pricing table
15. Standardize pagination in API
16. Document agentmailEmail
17. Add VS Code/Cline to MCP server
18. Inline benchmark scores in llms.txt
