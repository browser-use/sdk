# /api/v1 Docs — design principles (governs the restructure)

The docs are the launch surface. An agent (and a human) must understand the whole platform and write correct code first-try, from the docs alone. This file is the checklist the nav + pages must satisfy. Not shipped — internal, delete before publish.

## A. Information architecture (top nav)

Goal: a clean top tab bar. API reference is PROMINENT and top-level. Legacy is ONE collapsed thing, never 4 tabs.

Target top-level tabs (pending research confirmation):
1. **Guides** (or "Documentation") — conceptual + task pages. Quickstart first.
2. **API Reference** — its own top-level tab, auto-generated from `v1.json`. First-class, visible.
3. **Legacy** — ONE tab or version-switcher, holding v2/v3/v4 references collapsed. Backwards-compat only.

Anti-pattern we are fixing: the current bar shows `Cloud | Legacy | Legacy API v4 | Legacy API v3 | Legacy API v2` (5 tabs, 4 legacy). Kill that.

## B. The platform mental model (settled with Larsen)

One sentence: **"Browsers and their profiles. Agents and their workspaces. You run agents; runs use browsers and workspaces by id."**

- You only ever CREATE runs (`POST /agents/{agent}/runs`). Session + workspace are minted by the run and returned as ids. Implicit is the golden path.

### What a SESSION is (settled — the answer to "should you create it explicitly?")
A session is **a made-up construct: a name for a thread of runs — a conversation.** It is NOT a resource you build. It has no substance of its own; it's just the label meaning "these runs belong together."
- Docs line: *"A session is just a name for a thread of runs — a conversation. Your first run starts one and hands you its `session_id`; pass that back to keep the thread going. You never create a session; it's simply what we call your runs when they belong together."*
- Why no `POST /sessions`: you don't "create a conversation" before saying anything — the first message IS the conversation starting. Explicit creation adds no capability (you already get the id from the first run), only a mandatory empty step.
- Why it's not even buildable that way: **v4/browscode has NO session table** — a session there is literally `public_session_id` shared across runs (verified). Forcing explicit creation would require inventing a table + migration. v2 has a row (for title/proxy_cost/config) but conceptually it's the same: a name for a thread.
- Implementation truth (keep-sessions decision): browser-use session is a real row carrying title + proxy_cost (NOT derivable from runs → must expose GET). browscode session = lens over runs, the ONLY session-owned state is the pending queue (`v4_session_input`). So: sessions stay as thin header endpoints (list/get + `busy`); the run-thread is `GET /runs?session_id=`; queue endpoints only for browscode. "busy" is derived (no stored flag) in both; v2 has no queue (409/400-rejects), v4 queues.
- Session ≠ session pre-creation. Contrast agent-workspaces, which CAN be pre-created (real setup: pre-load files). Sessions have no pre-load equivalent, so no explicit create.

### Output & files model (settled — the "make workspaces intuitive" fix)
Grounded in real v4 code (v4_run.result is a ≤4000-char string; GET /workspaces/{id}/files lists S3 workspace contents; /runs/{id}/attachments returns INPUT uploads only).

- **Every run has a short `result` string** (a summary answer, small).
- **browser-use**: small structured output comes back **inline** via `structured_output` schema → typed `run.output`.
- **browscode**: real/large/structured output is **files in the workspace** (prompt "save the result to output.json"). You fetch files, not an inline field.
- **Golden path to get outputs = `GET /runs/{id}/files`** returning THIS run's files tagged `kind: input | output`. Answers "what did this run produce" on the id you already have — filter `kind=output`. This REPLACES the narrow `/runs/{id}/attachments` (which only showed input metadata and buried outputs — the exact cold-agent confusion).
- **`GET /agent-workspaces/{id}/files`** = advanced whole-disk view: every file across all runs in the workspace (for reuse / multi-run / shared workspace). Not the golden path.
- Mental model: **"the workspace is the agent's disk. You put files on it (upload → pass the ref), the agent reads/writes files on it, you read files off it. output.json is just a file the agent wrote."**
- **CLOUD IMPLEMENTATION REQUIREMENT (gap):** v4 does NOT currently track agent-written OUTPUTS as first-class listable files — `/attachments` is inputs-only and `/workspaces/{id}/files` lists raw S3 (agent must write into the listed prefix). The mock encodes the INTENDED contract (outputs are tracked + returned with kind=output). Real backend must add output tracking to satisfy this.

### What a WORKSPACE is (settled — same test, different answer)
A workspace is a **real container with substance** (files in S3; real `v4_workspace`/`v4_upload` rows) — NOT a made-up construct like a session. That's why it gets a hybrid the session doesn't.
- **The rule that covers both:** *explicit creation exists only when there's real state to set up before the first run.* Workspaces have it (files). Sessions don't (nothing to pre-load).
- Golden path (implicit): a run mints a workspace and returns `workspace_id`; files in via `attached_file_ids`, out via `/attachments`. 90% never call `POST /agent-workspaces`.
- Explicit create IS justified (unlike sessions): pre-load a large dataset before the first run → `POST /agent-workspaces`, upload, then pass `workspace_id` on the first run. Escape hatch for pre-loading, not the normal path.
- Docs line: *"You don't have to create a workspace — a run makes one and hands back the `workspace_id`. But a workspace can hold files, so to upload a big dataset before your first run, you CAN create one first and pre-load it. That's the only reason the explicit endpoint exists."*
- Explicit `POST /browsers`, `POST /agent-workspaces`, `POST /browser-profiles` exist but are ADVANCED escape hatches (pre-load files, drive a browser over CDP) — NOT first-read.
- Follow-ups: pass `session_id` back. Files: pass `workspace_id` / `attached_file_ids`. No pre-creation required.
- Two agents: `browser-use` (browser, files; disposable session) and `browsercode` (browser, code, terminal, files; durable session).
- `agent-workspaces` is a top-level resource but domain-prefixed (state FOR agents), like `browser-profiles` is state FOR browsers. A browser is portable (usable outside our agents, CDP); a workspace is not — hence the prefix.
- Lifecycle = named action `/stop` everywhere (runs AND browsers). Never PATCH a status.
- `browser-use` browser ≡ session lifetime (stop browser = close session). `browscode` session outlives its browsers.

## C. Reagan's agent-navigation learnings (HARD constraints, measured)

1. **Flat structure wins.** Agent path: root → `/llms.txt` (flat list of page titles) → find a title → fetch → act. Titles must be things an agent GUESSES: `create-browser`, `run-a-task`, `stop-a-run`. Keep them flat and literal.
2. **Anything not in `/llms.txt` is invisible.** Every page an agent needs must be in the index.
3. **Redirect bad guesses — agents guess poorly and a LOT.** Add redirects for every plausible alias: `workspaces`→`files`, `sessions`, `cancel`→`stop`, `tasks`→`run-a-task`, `profiles`→`browser-profiles`, etc. A 404 on a guess sends the agent to fetch `/llms-full.txt` (bad).
4. **Avoid `/llms-full.txt`.** WebFetch summarizes it → info lost, methods hallucinated (e.g. `POST /stop` guessed wrong). Keep `/llms.txt` complete enough that agents don't fall through to full.
5. **One code block per task.** e.g. create → connect → act → stop as ONE block. Copy-paste-first.
6. **Explicit DON'Ts.** Run agents against docs, catalog hallucinations, and write explicit "DON'T do this" corrections. Known ones to pre-empt:
   - No `BrowserUseCloud` class (hallucinated). The class is `BrowserUse`.
   - No `PATCH` to change status / stop anything. Use `POST /{id}/stop`.
   - No `POST /sessions` or `POST /workspaces` on the golden path — runs mint them.
   - No `browser_id` input on a run — a run provisions its own browser.
7. **Give SDK structure / field casing.** `cdp_url` (REST + Python) vs `cdpUrl` (TS) must be documented — it was undocumented and guessed wrong. Do this for every cased field.

## D. Naming to log as guess-risks (alias/redirect, monitor in the test)

- `agent-workspaces` — agents will guess `workspaces`, `files`, `agent-files`. Redirect them. (Our conceptual page is `files` precisely for guessability.)
- `browsercode` — agents may not guess this for a coding task. The registry (`GET /agents`) must carry the routing so they never have to guess the name. Watch in the test.
- `browser-profiles` — agents guess `profiles`. Redirect.

## E. The test loop (docs-first, the whole point)

1. Serve docs locally (mint dev) + a live mock `/api/v1` (FastAPI, generated from the same contract) so the agent gets real 200s/404s.
2. Cold agent (browser-harness, zero context), given ONLY the docs root URL + a task. Scenarios: scrape→CSV, book a flight, standalone CDP browser, a follow-up, upload+process a file.
3. Catalog every wrong guess / hallucination / 404.
4. Each finding → a doc fix, an explicit DON'T, or a redirect. Iterate. This is faster than building the real API first.

## F. Definition of done for the nav restructure

- [ ] Top bar: Guides + API Reference + Legacy (3 clean tabs), no 4-legacy-tab clutter.
- [ ] API Reference is top-level and auto-generated from v1.json.
- [ ] Legacy v2/v3/v4 collapsed into one tab/version-switcher, still reachable.
- [ ] `/llms.txt` leads with the v1 model + registry; flat guessable titles; complete enough to avoid llms-full.
- [ ] Redirects for all guess-aliases in D + C3.
- [ ] Every task page = one copy-paste code block, Python/TS/curl.
- [ ] Explicit DON'T callouts for the C6 hallucinations.
