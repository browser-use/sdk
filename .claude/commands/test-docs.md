# /test-docs — Documentation Quality Audit

You are a documentation quality auditor for Browser Use Cloud. Your job is to send many parallel agents — each simulating a different developer persona — to stress-test the docs end-to-end. Every agent reports back with a structured score and detailed findings.

## Prerequisites

- Read `.env` for `BROWSER_USE_API_KEY` and `BACKEND_URL`
- Ensure `browser-use-sdk` is installed for both Python and TypeScript (`pip install browser-use-sdk`, `npm install browser-use-sdk`)
- Read `docs/cloud/llms.txt` and `docs/cloud/llms-full.txt` for the doc surface area

## Agent Fleet

Launch **all** of these agents in parallel. Each agent works in an isolated worktree. Each agent must:

1. Read the docs (llms.txt, llms-full.txt, and/or the raw .mdx files) as their persona would
2. Attempt to follow the docs to accomplish their goal
3. Actually run every code snippet they encounter (Python AND TypeScript)
4. Use the real `BROWSER_USE_API_KEY` from `.env` for live API calls
5. Report findings in the structured format below

### Persona 1: "Quick Automator" (AI automation startup founder)
**Goal:** Just wants to automate a simple task ASAP. Reads only llms.txt + quickstart.
- Start from `docs/cloud/llms.txt` only — can you figure out what to do?
- Follow quickstart to run first task (both Python and TS)
- Time how many steps / files it takes to get a working result
- Test: Does `client.run()` actually return output? Is the output format clear?

### Persona 2: "Full Agent Builder" (building a product with live preview)
**Goal:** Build a chat UI with embedded live browser, streaming, follow-ups.
- Clone and set up the chat-ui-example repo from `docs/cloud/tutorials/chat-ui.mdx`
- Test: Can you `git clone`, `npm install`, add API key, and run it? Does localhost work?
- Check every code snippet in the chat-ui tutorial — do they match the actual repo?
- Test streaming with `for await` — does it work as documented?
- Test follow-up tasks in same session
- Test recording download

### Persona 3: "Playwright Power User" (wants stealth browsers for existing Playwright scripts)
**Goal:** Connect Playwright to Browser Use's stealth infrastructure.
- Read `docs/cloud/browser/playwright-puppeteer-selenium.mdx`
- Test WebSocket URL approach (Option 1) with real API key
- Test SDK approach (Option 2) — create browser, get cdp_url, connect Playwright
- Test both Python and TypeScript variants
- Verify query parameters (proxyCountryCode, profileId, timeout, screen size)
- Check: Are the `live_url` / `liveUrl` properties documented and accessible?

### Persona 4: "QA Tester" (wants to do end-to-end testing with natural language)
**Goal:** Use Browser Use for QA testing of a website.
- Read structured output docs (`docs/cloud/agent/structured-output.mdx`)
- Test Pydantic model output (Python) and Zod schema output (TypeScript)
- Verify Zod v4 requirement is clear and correct
- Test: Run a structured extraction task with real API
- Check: Are error messages clear when schema validation fails?

### Persona 5: "Data Extractor" (enterprise, large-scale scraping without login)
**Goal:** Extract data from public websites at scale.
- Test basic data extraction with structured output
- Test follow-up tasks for multi-page scraping
- Check: Is proxy configuration documented clearly?
- Read `docs/cloud/browser/proxies.mdx` and `docs/cloud/browser/stealth.mdx`
- Test: Can you set proxy country? Is the parameter name obvious?

### Persona 6: "File Upload/Download Tester"
**Goal:** Test the workspace/file system end-to-end.
- Read `docs/cloud/agent/workspaces.mdx`
- Create a workspace, upload a CSV file, have agent read it
- Have agent create a file, download it
- Test upload of different file types (csv, json, txt, png)
- Test `download_all` / `downloadAll`
- Test `delete_file` / `deleteFile`
- Check: Are all methods documented? Do return types match?

### Persona 7: "Profile Manager"
**Goal:** Use profiles for persistent browser state.
- Read `docs/cloud/guides/authentication.mdx`
- Create a profile, use it in a session, verify it persists
- Test CRUD operations: create, list, get, update, delete
- Test `query` parameter for searching profiles
- Check: Is the warning about session stop clear?
- Is it intuitive how to find your profile IDs?

### Persona 8: "Sub-Agent Embedder" (wants to embed Browser Use in their main agent)
**Goal:** Use Browser Use as a sub-agent with embedded browser view.
- Read llms.txt to understand the API surface
- Test creating a session with `keepAlive: true`
- Get `liveUrl` and verify it works (can be embedded in iframe)
- Test `for await` streaming to pipe into their own agent
- Check: Is the iframe embedding documented? CSP requirements?
- Read `docs/cloud/browser/live-preview.mdx`

### Persona 9: "API Type Checker"
**Goal:** Verify every API endpoint has correct types.
- Read all code snippets in `docs/cloud/llms-full.txt`
- For each Python snippet: verify it type-checks with `mypy` or at least runs without `TypeError`
- For each TypeScript snippet: verify it compiles with `tsc` or at least runs without type errors
- Check return types: does `result.output` exist? Is `session.live_url` vs `session.liveUrl` consistent across languages?
- Check input parameter names: `session_id` (Python) vs `sessionId` (TypeScript)
- Verify all imports are correct (v3 paths, class names)

### Persona 10: "Link Checker & llms.txt Auditor"
**Goal:** Verify all links work, llms.txt is complete and well-structured.
- Check every URL in `docs/cloud/llms.txt` — are they all valid (HTTP 200)?
- Check every URL in `docs/cloud/llms-full.txt` — are they all valid?
- Check internal links in all `.mdx` files — do the cross-references resolve?
- Do a web search for "best practices llms.txt" and compare against Browser Use's llms.txt
- Score: Is the llms.txt easy to navigate? Is the hierarchy clear? Missing sections?
- Check: Does the llms.txt match the actual docs structure in `docs.json`?
- Verify the "Always use v3" guidance is prominent enough

### Persona 11: "Deterministic Rerun User" (cache_script)
**Goal:** Use cache_script for $0 LLM cost reruns.
- Read `docs/cloud/agent/cache-script.mdx`
- Test: Run a task, get the cache_script, rerun with it
- Check: Are the docs clear about what cache_script is and when to use it?

### Persona 12: "Human-in-the-Loop Builder"
**Goal:** Build a flow where a human can interact with the browser mid-task.
- Read `docs/cloud/agent/human-in-the-loop.mdx`
- Test: Create a session, pause for human, resume
- Check: Is the flow intuitive? Are the SDK methods clear?

## Reporting Format

Each agent MUST produce a report with this structure:

```
## Persona: [Name]
### Score: X/10 (intuitiveness for this persona)
### Time to first success: [steps/files read]

### What worked well
- ...

### Problems found
- [BROKEN_LINK] url — HTTP status or error
- [CODE_ERROR] file:snippet — error message
- [MISSING_DOCS] what's missing
- [UNINTUITIVE] what was confusing and why
- [TYPE_MISMATCH] expected vs actual
- [STALE] outdated information

### Code snippet results
For each snippet tested:
- file.mdx:line — PASS/FAIL — error if FAIL

### Recommendations
- ...
```

## Final Synthesis

After all agents complete, produce a unified report:

### Overall Score Card
| Persona | Score | Time to Success | Critical Issues |
|---------|-------|-----------------|-----------------|

### Top Issues (sorted by severity)
1. ...

### llms.txt Assessment
- Navigation score: X/10
- Completeness: X/10
- LLM-friendliness: X/10
- Specific improvements: ...

### Quick Wins (easy fixes)
- ...

### Strategic Improvements (bigger changes)
- ...
