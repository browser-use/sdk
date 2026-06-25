# Excalidraw Schema Plan for Browser Use Cloud Docs

This document is a full pass over the authored docs in `/docs`, with a specific goal:

- identify where diagrams would materially improve comprehension,
- prioritize the most important placements,
- avoid adding diagrams where code/tables already do the job,
- provide ASCII mocks that can be turned into Excalidraw 1:1.

The most important page is the main Cloud lander:

- `/docs/introduction.mdx`

I also reviewed every authored docs page referenced in `docs.json`, plus the nav structure itself.

## Overall recommendation

The docs are already code-first and fairly concise. The best diagram opportunities are not "decorate every page"; they are:

1. pages where the user must choose between product surfaces,
2. pages where state persists across runs or sessions,
3. pages where there is an async or multi-party flow,
4. pages where trust boundaries matter,
5. pages where several concepts are introduced before code.

The biggest visual gap today is the conceptual layer:

- what Cloud actually is on the lander,
- how the four product surfaces differ,
- how sessions/profiles/workspaces relate,
- how auth choices differ,
- how v3 is more session-centric,
- how integrations fit into a real app loop.

## Design rules for the future Excalidraw set

1. **Put diagrams before the first serious code block.**
   If the page opens with code immediately, the reader skips the mental model.

2. **Prefer one strong diagram over several decorative ones.**
   Each diagram should answer one question clearly.

3. **Use the same visual vocabulary across pages.**
   Reuse shapes:
   - rounded boxes for product primitives (`Task`, `Session`, `Profile`, `Workspace`)
   - dashed boxes for persisted state
   - arrows for data/control flow
   - shaded/trust boxes for credentials or secure systems

4. **Keep recipe pages light.**
   Tips pages should get miniature flow diagrams only when the flow is non-obvious.

5. **Use the lander + overview pages to establish the whole map.**
   Other pages should zoom in, not reinvent the system.

## Priority tiers

### P0 — should absolutely get diagrams

- `/docs/introduction.mdx`
- `/docs/guides/overview.mdx`
- `/docs/guides/tasks.mdx`
- `/docs/guides/sessions.mdx`
- `/docs/guides/skills.mdx`
- `/docs/guides/authentication.mdx`
- `/docs/new-features/api-v3.mdx`
- `/docs/tutorials/chat-ui.mdx`

### P1 — strong improvement, very worth doing

- `/docs/guides/workspaces.mdx`
- `/docs/guides/browser-api.mdx`
- `/docs/guides/proxies-and-stealth.mdx`
- `/docs/guides/mcp-server.mdx`
- `/docs/guides/webhooks.mdx`
- `/docs/tips/live-view/human-takeover.mdx`
- `/docs/tips/parallel/shared-config.mdx`
- `/docs/tips/data/structured-output.mdx`
- `/docs/tips/data/file-downloads.mdx`
- `/docs/tips/integrations/n8n.mdx`

### P2 — nice to have, only if the above are done

- `/docs/pricing.mdx`
- `/docs/tips/authentication/profiles-and-secrets.mdx`
- `/docs/tips/authentication/1password-2fa.mdx`
- `/docs/tips/authentication/social-media.mdx`
- `/docs/tips/live-view/iframe-embed.mdx`
- `/docs/tips/parallel/concurrent-extraction.mdx`
- `/docs/tips/data/geo-scraping.mdx`
- `/docs/tips/data/streaming.mdx`
- `/docs/tips/integrations/playwright.mdx`

### No diagram needed right now

- `/docs/llm-quickstart.mdx`
- `/docs/faq.mdx`
- `/docs/open-source.mdx`

Why:

- `llm-quickstart` is intentionally a giant paste blob; visuals would just interrupt copy-paste utility.
- `faq` is a scan page for quick fixes.
- `open-source` is only a redirect stub.

## Full page-by-page placement plan

| Page | Recommendation | Placement | Diagram |
| --- | --- | --- | --- |
| `introduction.mdx` | Yes, P0 | After the opening card group and browser capabilities sentence, before "1. Install & configure" | D1 |
| `introduction.mdx` | Yes, P0 | Before "5. Add profiles, proxies, and 1Password" | D2 |
| `llm-quickstart.mdx` | No | None | None |
| `pricing.mdx` | Optional | After "Pricing Overview" table | D15 |
| `faq.mdx` | No | None | None |
| `open-source.mdx` | No | None | None |
| `new-features/api-v3.mdx` | Yes, P0 | After "What is it?" and before "Quick start" | D10 |
| `guides/overview.mdx` | Yes, P0 | Replace the current `<Frame><img ... /></Frame>` visual | D3 |
| `guides/overview.mdx` | Yes, P0 | After "When to use what" table | D4 |
| `guides/tasks.mdx` | Yes, P0 | After opening paragraph and before `run()` | D5 |
| `guides/tasks.mdx` | Yes, P1 | At start of "Files" section | D6 |
| `guides/sessions.mdx` | Yes, P0 | After opening paragraph and before first code block | D7 |
| `guides/workspaces.mdx` | Yes, P1 | After "What are workspaces?" and before "Create a workspace" | D8 |
| `guides/browser-api.mdx` | Yes, P1 | After opening paragraph and before "Create a browser session" | D9 |
| `guides/proxies-and-stealth.mdx` | Yes, P1 | After "Stealth by default" list and before "Country proxies" | D11 |
| `guides/skills.mdx` | Yes, P0 | After "How skills work" and before "Create a skill" | D12 |
| `guides/authentication.mdx` | Yes, P0 | After opening paragraph and before "Sync Local Cookies to Cloud" | D13 |
| `guides/authentication.mdx` | Yes, P1 | At start of "1Password Integration" | D14 |
| `guides/mcp-server.mdx` | Yes, P1 | After opening paragraph and before client-specific config blocks | D16 |
| `guides/webhooks.mdx` | Yes, P1 | After opening sentence and before "Events" | D17 |
| `tutorials/chat-ui.mdx` | Yes, P0 | After the "The app has two pages" list and before "Setup: SDK Clients" | D18 |
| `tips/authentication/profiles-and-secrets.mdx` | Light, P2 | After opening paragraph | Reuse D13 |
| `tips/authentication/1password-2fa.mdx` | Light, P2 | After opening paragraph | Reuse D14 |
| `tips/authentication/social-media.mdx` | Yes, P2 | After the setup list and before code | D19 |
| `tips/live-view/iframe-embed.mdx` | Light, P2 | After opening paragraph | D20 |
| `tips/live-view/human-takeover.mdx` | Yes, P1 | After "Flow" list and before code | Reuse D18 (cropped) |
| `tips/parallel/concurrent-extraction.mdx` | Light, P2 | After opening paragraph | D21 |
| `tips/parallel/shared-config.mdx` | Yes, P1 | After opening paragraph and before code | D22 |
| `tips/data/structured-output.mdx` | Yes, P1 | After opening paragraph and before code | D23 |
| `tips/data/file-downloads.mdx` | Yes, P1 | After opening paragraph and before code | Reuse D6 |
| `tips/data/geo-scraping.mdx` | Light, P2 | After opening paragraph and before code | D24 |
| `tips/data/streaming.mdx` | Light, P2 | After opening paragraph and before code | Reuse D5 |
| `tips/integrations/playwright.mdx` | Light, P2 | After opening paragraph | Reuse D9 |
| `tips/integrations/n8n.mdx` | Yes, P1 | After opening paragraph and before tip | D25 |

## Important note on the existing Overview visual

`/docs/guides/overview.mdx` currently references:

- `/images/concepts-overview.png`

That is the natural place to swap in an Excalidraw replacement. It is also the only explicit conceptual diagram reference in the current authored docs, so it is the best anchor for starting the visual system.

---

# Diagram library

These ASCII mocks are designed as direct input sketches for Excalidraw recreation.

## D1 — Cloud lander mental model

**Use on:** `introduction.mdx`

**Purpose:** Answer "what does Cloud add?" before the reader sees install steps.

```text
+----------------------------------------------------------------------------------+
|                               Browser Use Cloud                                  |
+----------------------------------------------------------------------------------+

   +-------------------+            +-----------------------------+
   | Your app / script |            | Optional inputs            |
   | - prompt          |----------->| - schema                  |
   | - SDK call        |            | - profile                 |
   | - API key         |            | - proxy country           |
   +-------------------+            | - 1Password vault         |
            |                       | - allowed domains         |
            |                       +-----------------------------+
            v
   +-------------------+
   | Cloud API         |
   +-------------------+
      |        |        \
      |        |         \
      v        v          v
 +---------+ +---------+ +------------------+
 | Task    | | Skill   | | Browser API/CDP  |
 | run()   | | execute | | create browser   |
 +---------+ +---------+ +------------------+
      \        |          /
       \       |         /
        v      v        v
     +--------------------------------------+
     | Stealth browser infrastructure        |
     | - anti-detect                         |
     | - CAPTCHA solving                     |
     | - ad/cookie blocking                  |
     | - residential proxies                 |
     +--------------------------------------+
                       |
                       v
               +------------------+
               | Target websites  |
               +------------------+
                       |
         +-------------+-------------+------------------+
         |                           |                  |
         v                           v                  v
 +------------------+       +------------------+ +------------------+
 | typed output     |       | liveUrl / share  | | saved state      |
 | text / JSON      |       | debug / embed    | | profile / files  |
 +------------------+       +------------------+ +------------------+
```

## D2 — Session add-ons stack

**Use on:** `introduction.mdx`

**Purpose:** Make section 5 feel like composable building blocks, not a random parameter dump.

```text
                    +----------------------+
                    | Base session         |
                    | browser + liveUrl    |
                    +----------------------+
                              |
          +-------------------+-------------------+-------------------+
          |                   |                   |                   |
          v                   v                   v                   v
 +----------------+  +----------------+  +----------------+  +------------------+
 | Profile        |  | Proxy          |  | 1Password      |  | Allowed domains  |
 | saved login    |  | geo-routing    |  | creds + TOTP   |  | navigation fence |
 +----------------+  +----------------+  +----------------+  +------------------+
          \                   |                   |                   /
           \                  |                   |                  /
            \                 |                   |                 /
             v                v                   v                v
                   +--------------------------------------+
                   | Safer, more reliable agent task      |
                   | on logged-in / geo-specific websites |
                   +--------------------------------------+
```

## D3 — Four product surfaces map

**Use on:** `guides/overview.mdx`

**Purpose:** Replace the current conceptual image with a durable decision map.

```text
                                   MORE CONTROL
                                        ^
                                        |
                                        |
              +---------------------------------------------------+
              | Browser Infrastructure                            |
              | - You write Playwright/Puppeteer/Selenium code    |
              | - Raw CDP access                                  |
              | - Stealth infra underneath                        |
              +---------------------------------------------------+
                                        |
                                        |
 +---------------------------------------------------+------------+---------------------------------------------------+
 | Tasks                                             |            | Open Source + Cloud                               |
 | - "Do this for me"                                |            | - Keep your existing agent code                   |
 | - Natural language in                             |            | - Swap in cloud browsers                          |
 | - Fastest path to value                           |            | - Best when already using browser-use OSS         |
 +---------------------------------------------------+            +---------------------------------------------------+
                                        |
                                        |
              +---------------------------------------------------+
              | Skills                                            |
              | - Repeated extraction / deterministic endpoint    |
              | - Create once, call many times                    |
              | - Best for production APIs                        |
              +---------------------------------------------------+
                                        |
                                        v
                                  MORE ABSTRACTION
```

## D4 — "When should I use what?" progression

**Use on:** `guides/overview.mdx`

**Purpose:** Show the migration path between product surfaces.

```text
   New problem
       |
       v
 +-------------+
 | Start here  |
 |   TASKS     |
 +-------------+
       |
       | repeated workflow / need stable endpoint
       v
 +-------------+
 |   SKILLS    |
 +-------------+
       |
       | need low-level browser control
       v
 +----------------------+
 | BROWSER API / CDP    |
 +----------------------+

 Separate path:

 +----------------------+
 | Already use browser- |
 | use open source?     |
 +----------------------+
           |
           v
 +----------------------+
 | OSS + Cloud Browsers |
 +----------------------+
```

## D5 — Task lifecycle

**Use on:** `guides/tasks.mdx`

**Purpose:** Clarify what `run()` actually wraps.

```text
 +-------------------+
 | run(task, opts)   |
 +-------------------+
          |
          v
 +------------------------------+
 | Session chosen               |
 | - auto-create OR             |
 | - reuse session_id           |
 +------------------------------+
          |
          v
 +------------------------------+
 | Agent executes steps         |
 | - browse                     |
 | - reason                     |
 | - click / type / extract     |
 +------------------------------+
          |
    +-----+----------------------+-------------------+
    |                            |                   |
    v                            v                   v
 +---------+              +-------------+     +--------------+
 | stream  |              | liveUrl     |     | output files |
 | steps   |              | debug view  |     | optional     |
 +---------+              +-------------+     +--------------+
    |
    v
 +----------------------+
 | final TaskResult     |
 | text or typed output |
 +----------------------+
```

## D6 — Task file flow

**Use on:** `guides/tasks.mdx`, `tips/data/file-downloads.mdx`

**Purpose:** Make upload/download mechanics much easier to grok.

```text
 Upload path:

 Local file
    |
    v
 +-----------------------+
 | get presigned URL     |
 | files.session_url()   |
 +-----------------------+
    |
    v
 +-----------------------+
 | PUT file bytes        |
 +-----------------------+
    |
    v
 +-----------------------+
 | Session sees file     |
 | agent can read it     |
 +-----------------------+

 Download path:

 +-----------------------+
 | Task finishes         |
 +-----------------------+
    |
    v
 +-----------------------+
 | tasks.get(task_id)    |
 | -> output_files       |
 +-----------------------+
    |
    v
 +-----------------------+
 | files.task_output()   |
 | -> presigned URL      |
 +-----------------------+
    |
    v
 +-----------------------+
 | Download to app       |
 +-----------------------+
```

## D7 — Session and profile lifecycle

**Use on:** `guides/sessions.mdx`

**Purpose:** Explain persistent browser state and the important "save on stop" behavior.

```text
                     +----------------------+
                     | Profile              |
                     | cookies/localStorage |
                     | persisted state      |
                     +----------------------+
                               |
                               | loaded into
                               v
 +----------------------+   +----------------------+   +----------------------+
 | Session A            |   | Session B            |   | Session C            |
 | liveUrl              |   | same profile         |   | same profile later   |
 | task 1, task 2       |   | already logged in    |   | already logged in    |
 +----------------------+   +----------------------+   +----------------------+
            |                           |                           |
            | stop() saves state        | stop() saves state        |
            +---------------------------+---------------------------+
                                        |
                                        v
                              +----------------------+
                              | Updated profile      |
                              | new cookies/state    |
                              +----------------------+

 Auto-session path:
 run() -> temporary session -> task finishes -> session cleaned up

 Manual-session path:
 sessions.create() -> multiple run() calls -> stop() -> delete()
```

## D8 — Workspace shared storage

**Use on:** `guides/workspaces.mdx`

**Purpose:** Show that workspaces persist across sessions, unlike a single task's output.

```text
                 +----------------------------------+
                 | Workspace                        |
                 | persistent shared file storage   |
                 | e.g. input.csv, output.csv       |
                 +----------------------------------+
                    ^                ^             ^
                    |                |             |
                    | attached to    | attached to | attached to
                    |                |             |
          +----------------+  +----------------+  +----------------+
          | Session / task |  | Session / task |  | Session / task |
          | reads inputs   |  | writes outputs |  | follow-up job   |
          +----------------+  +----------------+  +----------------+

 Timeline:
 create workspace -> run task -> files remain -> later session reuses them
```

## D9 — Browser API / CDP architecture

**Use on:** `guides/browser-api.mdx`, `tips/integrations/playwright.mdx`

**Purpose:** Make it immediately obvious that the user writes the browser logic, not the agent.

```text
 +------------------------+
 | Your automation code   |
 | Playwright/Puppeteer   |
 | Selenium               |
 +------------------------+
            |
            | connect via cdpUrl
            v
 +------------------------+
 | Browser Use browser    |
 | stealth cloud browser  |
 | liveUrl available      |
 +------------------------+
            |
            v
 +------------------------+
 | Residential/custom     |
 | proxy routing          |
 +------------------------+
            |
            v
 +------------------------+
 | Target website         |
 +------------------------+

 Browser API flow:
 browsers.create() -> receive cdpUrl/liveUrl -> connect -> automate -> browsers.stop()
```

## D10 — v3 session-centric model

**Use on:** `new-features/api-v3.mdx`

**Purpose:** Explain the conceptual shift toward sessions/messages/workspaces/files.

```text
                         +----------------------+
                         | v3 Session           |
                         | the central object   |
                         +----------------------+
                            |       |        |
            +---------------+       |        +----------------+
            |                       |                         |
            v                       v                         v
   +----------------+     +--------------------+     +------------------+
   | run task       |     | messages()         |     | workspace/files  |
   | output         |     | conversation log   |     | persistent data  |
   +----------------+     +--------------------+     +------------------+
            |                       |                         |
            +-----------------------+-------------------------+
                                    |
                                    v
                           +------------------+
                           | live_url         |
                           | status / cost    |
                           +------------------+
```

## D11 — Stealth + proxy routing

**Use on:** `guides/proxies-and-stealth.mdx`, `tips/data/geo-scraping.mdx`

**Purpose:** Separate always-on stealth from optional routing choice.

```text
 +-------------------+
 | Your task/session |
 +-------------------+
          |
          v
 +------------------------------+
 | Browser Use stealth browser  |
 | - anti-detect                |
 | - CAPTCHA solving            |
 | - block ads/cookie banners   |
 +------------------------------+
          |
          | optional route choice
     +----+--------------------------+
     |                               |
     v                               v
 +----------------------+   +----------------------+
 | Browser Use proxy    |   | Custom proxy         |
 | residential country  |   | HTTP / SOCKS5        |
 +----------------------+   +----------------------+
     |                               |
     +---------------+---------------+
                     |
                     v
             +------------------+
             | Target website   |
             | sees chosen geo  |
             +------------------+
```

## D12 — Skills pipeline

**Use on:** `guides/skills.mdx`

**Purpose:** Explain goal vs demonstration vs execution, which is the trickiest concept on the page.

```text
 +-----------------------+      +--------------------------+
 | Goal                  |      | Demonstration            |
 | full contract         |      | one example of HOW       |
 | params + outputs      |      | to trigger the workflow  |
 +-----------------------+      +--------------------------+
             \                         /
              \                       /
               v                     v
              +-------------------------+
              | Skill generation        |
              | builds reusable logic   |
              +-------------------------+
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
 +---------------------+           +---------------------+
 | execute(parameters) |           | refine(feedback)    |
 | cheap repeated call |           | update skill        |
 +---------------------+           +---------------------+
          |                                 |
          +---------------+-----------------+
                          |
                          v
                 +------------------+
                 | stable API use   |
                 +------------------+
```

## D13 — Authentication decision map

**Use on:** `guides/authentication.mdx`, `tips/authentication/profiles-and-secrets.mdx`

**Purpose:** Help readers choose the right auth mode quickly.

```text
 Need login?
    |
    v
 +-------------------------------+
 | Are you already logged in     |
 | locally in your own browser?  |
 +-------------------------------+
    | yes                                   | no
    v                                       v
 +----------------------+          +-------------------------------+
 | Profile Sync         |          | Need raw credentials only?    |
 | easiest              |          +-------------------------------+
 | best default         |             | yes                    | no / has 2FA
 +----------------------+             v                        v
           |                    +----------------+     +------------------+
           |                    | Secrets        |     | 1Password        |
           |                    | domain-scoped  |     | creds + TOTP     |
           |                    +----------------+     +------------------+
           |                              \               /
           |                               \             /
           +--------------------------------v-----------v----------------+
                                            | allowed_domains fence      |
                                            +----------------------------+
                                                            |
                                                            v
                                                   +------------------+
                                                   | authenticated    |
                                                   | agent task       |
                                                   +------------------+
```

## D14 — 1Password trust boundary

**Use on:** `guides/authentication.mdx`, `tips/authentication/1password-2fa.mdx`

**Purpose:** Show why this is safer than pasting credentials.

```text
 +-----------------------+         +-----------------------+
 | 1Password vault       |         | Browser Use Cloud     |
 | usernames/passwords   |-------->| integration bridge    |
 | TOTP seeds            |         | secure retrieval      |
 +-----------------------+         +-----------------------+
                                               |
                                               | fills form fields
                                               | without exposing raw values
                                               v
                                    +-----------------------+
                                    | Browser session       |
                                    | login form + 2FA form |
                                    +-----------------------+
                                               |
                                               v
                                    +-----------------------+
                                    | Target website        |
                                    +-----------------------+

 AI model visibility:
 [has access to credential]   !=   [sees secret value]
```

## D15 — Pricing model snapshot

**Use on:** `pricing.mdx` if a visual is added later

**Purpose:** Show that different products meter on different axes.

```text
 +------------------+     +----------------------+     +----------------------+
 | Tasks            |     | Browser sessions     |     | Skills               |
 | init + step cost |     | time-based billing   |     | create once + run    |
 +------------------+     +----------------------+     +----------------------+
          |                         |                               |
          v                         v                               v
   $0.01 + model step       hourly/minute usage             creation + per call

 Separate meter:

 +------------------+
 | Proxy data       |
 | billed per GB    |
 +------------------+
```

## D16 — MCP integration map

**Use on:** `guides/mcp-server.mdx`

**Purpose:** Explain the relationship between MCP clients and Browser Use tools.

```text
 +------------------+   +------------------+   +------------------+
 | Claude           |   | Cursor           |   | Windsurf / other |
 +------------------+   +------------------+   +------------------+
           \                 |                 /
            \                |                /
             v               v               v
              +----------------------------------+
              | Browser Use MCP server           |
              | https://api.browser-use.com/mcp  |
              +----------------------------------+
                   |           |           |
                   v           v           v
             +-----------+ +-----------+ +--------------------+
             | browser_  | | execute_  | | monitor / cookies /|
             | task      | | skill     | | profiles tools     |
             +-----------+ +-----------+ +--------------------+
```

## D17 — Webhook delivery flow

**Use on:** `guides/webhooks.mdx`

**Purpose:** Make the async callback pattern visually obvious.

```text
 +------------------+          +------------------+          +------------------+
 | Your app         |          | Browser Use      |          | Your webhook     |
 | creates task     |--------->| runs task        |--------->| endpoint         |
 +------------------+          +------------------+          +------------------+
                                      |
                                      | status changes
                                      v
                             +----------------------+
                             | signed event         |
                             | X-Webhook-Signature  |
                             +----------------------+
                                      |
                                      v
                             +----------------------+
                             | verify signature     |
                             | update your system   |
                             +----------------------+
```

## D18 — Session-driven app loop

**Use on:** `tutorials/chat-ui.mdx`, `tips/live-view/human-takeover.mdx`

**Purpose:** Show the UX loop around a session.

```text
 +------------------+
 | Home page        |
 | user enters task |
 +------------------+
          |
          v
 +------------------+
 | create session   |
 | keepAlive=true   |
 +------------------+
          |
          v
 +------------------+        polls         +------------------+
 | Session page     |<-------------------->| Browser Use API  |
 | chat + live view |--------------------->| messages/status  |
 +------------------+      follow-ups      +------------------+
          |
          | optional human takeover via liveUrl
          v
 +------------------+
 | Human edits      |
 | browser state    |
 +------------------+
          |
          v
 +------------------+
 | next task uses   |
 | same session     |
 +------------------+
```

## D19 — Social platform bootstrap pattern

**Use on:** `tips/authentication/social-media.mdx`

**Purpose:** Explain why same profile + same country matters.

```text
 Step 1: bootstrap

 +------------------+     +------------------+     +------------------+
 | Blank profile    | --> | Session with US  | --> | Human / 1Password|
 | for one account  |     | proxy (example)  |     | logs in once     |
 +------------------+     +------------------+     +------------------+
                                                        |
                                                        v
                                               +------------------+
                                               | stop session     |
                                               | save cookies     |
                                               +------------------+

 Step 2: repeatable runs

 +------------------+     +------------------+     +------------------+
 | Same profile     | --> | Same proxy       | --> | Lower detection  |
 | same account     |     | same country     |     | stable identity  |
 +------------------+     +------------------+     +------------------+
```

## D20 — Live view embed

**Use on:** `tips/live-view/iframe-embed.mdx`

**Purpose:** Show how little is required to embed it.

```text
 +------------------+       +------------------+       +------------------+
 | sessions.create  | ----> | receive liveUrl  | ----> | iframe in app    |
 +------------------+       +------------------+       +------------------+
```

## D21 — Parallel fan-out / fan-in

**Use on:** `tips/parallel/concurrent-extraction.mdx`

**Purpose:** Show independent auto-sessions per task.

```text
                    +------------------+
                    | URL list / jobs  |
                    +------------------+
                              |
             +----------------+----------------+----------------+
             |                |                |                |
             v                v                v                v
      +------------+   +------------+   +------------+   +------------+
      | run(job 1) |   | run(job 2) |   | run(job 3) |   | run(job N) |
      | session A  |   | session B  |   | session C  |   | session N  |
      +------------+   +------------+   +------------+   +------------+
             \                |                |                /
              \               |                |               /
               +--------------+----------------+--------------+
                              |
                              v
                    +------------------+
                    | gathered results |
                    +------------------+
```

## D22 — Shared-profile snapshot caveat

**Use on:** `tips/parallel/shared-config.mdx`

**Purpose:** Explain the warning about concurrent sessions not seeing live changes.

```text
                     +----------------------+
                     | Profile snapshot     |
                     | state at start time  |
                     +----------------------+
                         |       |       |
                         v       v       v
                  +--------+ +--------+ +--------+
                  | Sess A | | Sess B | | Sess C |
                  +--------+ +--------+ +--------+
                      |          |          |
                      | changes   | changes  | reads
                      v          v          v

   Important:
   Sess A does NOT stream live cookie/state changes into Sess B or Sess C.

   Good for:
   - read-heavy parallel work

   Risky for:
   - flows that mutate auth/profile state mid-run
```

## D23 — Structured output contract

**Use on:** `tips/data/structured-output.mdx`

**Purpose:** Show why schema mode is different from plain text output.

```text
 +------------------+      +------------------+      +------------------+
 | Natural language | ---> | Agent extracts   | ---> | Validate against |
 | request          |      | fields from web  |      | schema           |
 +------------------+      +------------------+      +------------------+
                                                         |
                                    +--------------------+--------------------+
                                    |                                         |
                                    v                                         v
                           +------------------+                      +------------------+
                           | typed object     |                      | validation error |
                           | app-ready data   |                      | retry / fix      |
                           +------------------+                      +------------------+
```

## D24 — Geo comparison pattern

**Use on:** `tips/data/geo-scraping.mdx`

**Purpose:** Show region-based comparison as the core use case.

```text
                 +----------------------+
                 | Same task            |
                 | same product/page    |
                 +----------------------+
                      |        |        |
                      v        v        v
                  +------+ +------+ +------+
                  | US   | | JP   | | DE   |
                  | proxy| | proxy| | proxy|
                  +------+ +------+ +------+
                      |        |        |
                      v        v        v
                  +------+ +------+ +------+
                  | price| | price| | price|
                  | text | | text | | text |
                  +------+ +------+ +------+
                      \        |        /
                       \       |       /
                        v      v      v
                    +----------------------+
                    | compare by region    |
                    +----------------------+
```

## D25 — n8n orchestration pattern

**Use on:** `tips/integrations/n8n.mdx`

**Purpose:** Show the two valid completion strategies: polling or webhook.

```text
 +------------------+
 | n8n HTTP node    |
 | POST /tasks      |
 +------------------+
          |
          v
 +------------------+
 | Browser Use task |
 +------------------+
          |
     +----+---------------------------+
     |                                |
     v                                v
 +------------------+        +----------------------+
 | Poll GET /tasks  |        | Webhook event        |
 | until finished   |        | push to your system  |
 +------------------+        +----------------------+
     |                                |
     +---------------+----------------+
                     |
                     v
             +------------------+
             | continue workflow|
             +------------------+
```

---

# Implementation notes per page

These notes are about where the visual should sit relative to the current narrative.

## `introduction.mdx`

- Add **D1** before any install instructions.
- The current page jumps straight from feature cards into install; the user still has to infer the product model.
- Add **D2** right before the profiles/proxies/1Password section to make those parameters feel like modular upgrades to a base session.

## `guides/overview.mdx`

- Replace the current frame/image slot with **D3**.
- Then place **D4** after the comparison table.
- This page is the best "map page" in the entire docs and should carry the strongest conceptual visual language.

## `guides/tasks.mdx`

- Add **D5** near the top; it is the most important missing diagram on the task docs.
- Add **D6** at the start of the Files section; presigned upload/download flows are easy to understand visually and slightly annoying to parse in prose.

## `guides/sessions.mdx`

- Add **D7** near the top.
- The critical thing to communicate is that profiles are persisted state and are only safely updated when the session ends.

## `guides/workspaces.mdx`

- Add **D8** after the intro.
- This page benefits from a diagram because workspaces sound similar to task output files unless the reader sees the persistence boundary.

## `guides/browser-api.mdx`

- Add **D9** immediately after the intro.
- This page should visually emphasize: "no agent, your code is in charge."

## `guides/proxies-and-stealth.mdx`

- Add **D11** after the stealth bullets.
- That placement helps distinguish:
  - stealth = always on,
  - proxy routing = configurable.

## `guides/skills.mdx`

- Add **D12** after the explanation of Goal vs Demonstration.
- This is arguably the most conceptually subtle page in the docs, and a diagram would make it much easier to internalize.

## `guides/authentication.mdx`

- Add **D13** at the top to orient the reader before they enter setup details.
- Add **D14** at the start of the 1Password section to clarify the secret boundary and why this mode is safer.

## `guides/mcp-server.mdx`

- Add **D16** right after the first sentence.
- The current page is config-heavy; a top diagram would frame what all of those JSON snippets are actually wiring together.

## `guides/webhooks.mdx`

- Add **D17** before the event table.
- This page wants a very small but very clear async flow diagram.

## `tutorials/chat-ui.mdx`

- Add **D18** after the "Home / Session" page split.
- This tutorial is one of the best candidates for a diagram because it has app state, API polling, follow-ups, and live view all at once.

## `new-features/api-v3.mdx`

- Add **D10** near the top.
- The v3 page becomes much easier to understand when the reader sees that the session is the center of gravity.

## Reuse suggestions for smaller tips pages

- `tips/authentication/profiles-and-secrets.mdx` -> reuse **D13**
- `tips/authentication/1password-2fa.mdx` -> reuse **D14**
- `tips/live-view/human-takeover.mdx` -> crop **D18** down to the agent-human-agent loop
- `tips/data/file-downloads.mdx` -> reuse **D6**
- `tips/data/streaming.mdx` -> reuse the upper half of **D5**
- `tips/integrations/playwright.mdx` -> reuse **D9**

## Final recommendation on rollout order

If only a few diagrams get designed first, do them in this order:

1. **D1** — lander mental model
2. **D3** — four product surfaces map
3. **D5** — task lifecycle
4. **D7** — session/profile lifecycle
5. **D12** — skills pipeline
6. **D13** — authentication decision map
7. **D10** — v3 session-centric model
8. **D18** — session-driven app loop

That set would cover the biggest conceptual gaps in the docs with the fewest visuals.
