# SDK DX Contract

This document defines the developer experience for the Browser Use SDK. It is the source of truth for how the SDK should feel to use.

## Versions

The SDK ships two API versions in a single package:

- **v2** -- default, stable, production. Full API surface.
- **v3** -- experimental, opt-in via subpath import. Simplified session model.

## V2 DX Contract

### Import and Setup

```typescript
import { BrowserUse } from "browser-use-sdk";
const client = new BrowserUse({ apiKey: "bu_..." });
```

```python
from browser_use_sdk import BrowserUse
client = BrowserUse(api_key="bu_...")
```

### Core Workflow: Tasks

The primary v2 workflow is task-based:

```typescript
// Create a task
const task = await client.tasks.create({ task: "Go to google.com and find the weather" });

// Poll until complete
const handle = client.run({ task: "Go to google.com" });
const result = await handle.complete();
console.log(result);

// Or stream progress
for await (const state of handle.stream()) {
  console.log(state.status);
}
```

```python
from browser_use_sdk.v2.helpers import TaskHandle

task = client.tasks.create(task="Go to google.com")
handle = TaskHandle(task, client.tasks)
result = handle.complete()

# Or stream
for state in handle.stream():
    print(state.status)
```

### All V2 Resources

| Resource | Method | HTTP | Description |
|----------|--------|------|-------------|
| billing | account() | GET /billing/account | Account info + credit balance |
| tasks | create(body) | POST /tasks | Create and start a task |
| tasks | list(params?) | GET /tasks | List tasks with filtering |
| tasks | get(id) | GET /tasks/{id} | Get task details |
| tasks | stop(id) | PATCH /tasks/{id} | Stop a running task |
| tasks | status(id) | GET /tasks/{id}/status | Lightweight status for polling |
| tasks | logs(id) | GET /tasks/{id}/logs | Download URL for task logs |
| sessions | create(body?) | POST /sessions | Create a session |
| sessions | list(params?) | GET /sessions | List sessions |
| sessions | get(id) | GET /sessions/{id} | Get session details |
| sessions | stop(id) | PATCH /sessions/{id} | Stop session |
| sessions | delete(id) | DELETE /sessions/{id} | Delete session |
| sessions | getShare(id) / get_share(id) | GET /sessions/{id}/public-share | Get share link |
| sessions | createShare(id) / create_share(id) | POST /sessions/{id}/public-share | Create share link |
| sessions | deleteShare(id) / delete_share(id) | DELETE /sessions/{id}/public-share | Remove share link |
| files | sessionUrl(id, body) / session_url(id) | POST /files/sessions/{id}/presigned-url | Upload URL for session |
| files | browserUrl(id, body) / browser_url(id) | POST /files/browsers/{id}/presigned-url | Upload URL for browser |
| files | taskOutput(taskId, fileId) / task_output(id, fid) | GET /files/tasks/{id}/output-files/{fid} | Task output download URL |
| profiles | create(body?) | POST /profiles | Create browser profile |
| profiles | list(params?) | GET /profiles | List profiles |
| profiles | get(id) | GET /profiles/{id} | Get profile |
| profiles | update(id, body) | PATCH /profiles/{id} | Update profile |
| profiles | delete(id) | DELETE /profiles/{id} | Delete profile |
| browsers | create(body) | POST /browsers | Create browser session |
| browsers | list(params?) | GET /browsers | List browser sessions |
| browsers | get(id) | GET /browsers/{id} | Get browser session |
| browsers | stop(id) | PATCH /browsers/{id} | Stop browser session |
| skills | create(body) | POST /skills | Create skill |
| skills | list(params?) | GET /skills | List skills |
| skills | get(id) | GET /skills/{id} | Get skill |
| skills | update(id, body) | PATCH /skills/{id} | Update skill metadata |
| skills | delete(id) | DELETE /skills/{id} | Delete skill |
| skills | cancel(id) | POST /skills/{id}/cancel | Cancel generation |
| skills | execute(id, body) | POST /skills/{id}/execute | Execute skill |
| skills | refine(id, body) | POST /skills/{id}/refine | Refine skill |
| skills | rollback(id) | POST /skills/{id}/rollback | Rollback to previous |
| skills | executions(id, params?) | GET /skills/{id}/executions | List executions |
| skills | executionOutput(id, execId) / execution_output(id, eid) | GET /skills/{id}/executions/{eid}/output | Execution output |
| marketplace | list(params?) | GET /marketplace/skills | List public skills |
| marketplace | get(slug) | GET /marketplace/skills/{slug} | Get by slug |
| marketplace | clone(id) | POST /marketplace/skills/{id}/clone | Clone skill |
| marketplace | execute(id, body) | POST /marketplace/skills/{id}/execute | Execute marketplace skill |

## V3 DX Contract

### Import and Setup

```typescript
import { BrowserUse } from "browser-use-sdk/v3";
const client = new BrowserUse({ apiKey: "bu_..." });
```

```python
from browser_use_sdk.v3 import BrowserUse
client = BrowserUse(api_key="bu_...")
```

### Core Workflow: Sessions

V3 uses a unified session model:

```typescript
const session = await client.sessions.create({ task: "Go to google.com" });
const handle = client.run({ task: "Go to google.com" });
const result = await handle.complete();
```

```python
from browser_use_sdk.v3.helpers import SessionHandle

session = client.sessions.create(task="Go to google.com")
handle = SessionHandle(session, client.sessions)
result = handle.complete()
```

### All V3 Resources

| Resource | Method | HTTP | Description |
|----------|--------|------|-------------|
| sessions | create(body) | POST /sessions | Create session and run task |
| sessions | list(params?) | GET /sessions | List sessions |
| sessions | get(id) | GET /sessions/{id} | Get session details |
| sessions | stop(id) | POST /sessions/{id}/stop | Stop session |
| sessions | files(id, params?) | GET /sessions/{id}/files | List session files |

## Error Handling

All errors throw/raise `BrowserUseError`:

```typescript
import { BrowserUseError } from "browser-use-sdk";
try {
  await client.tasks.get("nonexistent");
} catch (err) {
  if (err instanceof BrowserUseError) {
    err.statusCode; // 404
    err.message;    // "Task not found"
    err.detail;     // raw error body
  }
}
```

```python
from browser_use_sdk import BrowserUseError
try:
    client.tasks.get("nonexistent")
except BrowserUseError as e:
    e.status_code  # 404
    e.message      # "Task not found"
    e.detail       # raw error body
```

## Client Options

| Option | TS Name | Python Name | Default | Description |
|--------|---------|-------------|---------|-------------|
| API Key | apiKey | api_key | (required) | Authentication key |
| Base URL | baseUrl | base_url | version-specific | API base URL |
| Timeout | timeout | timeout | 30000ms / 30.0s | Request timeout |
| Max Retries | maxRetries | (not exposed) | 3 | Retry attempts on 429/5xx |

## Naming Conventions

- TypeScript: camelCase methods, PascalCase types
- Python: snake_case methods, sync + async variants
- PATCH action endpoints -> named methods (stop, not update)
- Sub-resource endpoints -> method on parent (sessions.getShare, not shares.get)
