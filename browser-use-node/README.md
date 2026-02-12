# browser-use-sdk

Official TypeScript SDK for the [Browser Use](https://browser-use.com) API -- run AI-powered browser agents in the cloud.

## Installation

```bash
npm install browser-use-sdk
# or
pnpm add browser-use-sdk
# or
yarn add browser-use-sdk
# or
bun add browser-use-sdk
```

## Quick Start (v2)

The default import exposes the **v2** API client.

```ts
import { BrowserUse } from "browser-use-sdk";

const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

// Run a task and wait for completion
const result = await client.run({ task: "Find the top post on Hacker News" }).complete();
console.log(result.output);
```

## V3 (Experimental)

The v3 API uses a unified session model. Import from `browser-use-sdk/v3`:

```ts
import { BrowserUse } from "browser-use-sdk/v3";

const client = new BrowserUse({ apiKey: process.env.BROWSER_USE_API_KEY! });

const result = await client.run({ task: "Find the top post on HN" }).complete();
console.log(result.output);
```

## Client Options

```ts
const client = new BrowserUse({
  apiKey: "bu_...",           // Required
  baseUrl: "https://...",     // Override API base URL
  maxRetries: 3,              // Retry on 429/5xx (default: 3)
  timeout: 30_000,            // Request timeout in ms (default: 30s)
});
```

## Polling and Streaming

Both `client.run()` (v2) and `client.run()` (v3) return a handle with two patterns:

### Wait for Completion

```ts
const handle = client.run({ task: "Search for AI news" });
const result = await handle.complete({ timeout: 120_000, interval: 3_000 });
```

### Stream Progress

```ts
const handle = client.run({ task: "Search for AI news" });

for await (const state of handle.stream({ interval: 2_000 })) {
  console.log(`Status: ${state.status}`);
}
```

## V2 API Reference

### Billing

| Method                | Description                          |
|-----------------------|--------------------------------------|
| `billing.account()`  | Get account info and credit balance  |

### Tasks

| Method                       | Description                             |
|------------------------------|-----------------------------------------|
| `tasks.create(body)`        | Create and start a new task             |
| `tasks.list(params?)`       | List tasks with optional filtering      |
| `tasks.get(taskId)`         | Get detailed task information           |
| `tasks.stop(taskId)`        | Stop a running task                     |
| `tasks.status(taskId)`      | Lightweight status for polling          |
| `tasks.logs(taskId)`        | Get download URL for task logs          |

### Sessions

| Method                             | Description                          |
|------------------------------------|--------------------------------------|
| `sessions.create(body?)`          | Create a new session                 |
| `sessions.list(params?)`          | List sessions                        |
| `sessions.get(sessionId)`         | Get session details                  |
| `sessions.stop(sessionId)`        | Stop session and running tasks       |
| `sessions.delete(sessionId)`      | Delete session and all tasks         |
| `sessions.getShare(sessionId)`    | Get public share info                |
| `sessions.createShare(sessionId)` | Create public share link             |
| `sessions.deleteShare(sessionId)` | Remove public share                  |

### Files

| Method                                  | Description                            |
|-----------------------------------------|----------------------------------------|
| `files.sessionUrl(sessionId, body)`    | Presigned URL for session file upload  |
| `files.browserUrl(sessionId, body)`    | Presigned URL for browser file upload  |
| `files.taskOutput(taskId, fileId)`     | Download URL for task output file      |

### Profiles

| Method                            | Description                  |
|-----------------------------------|------------------------------|
| `profiles.create(body?)`         | Create a browser profile     |
| `profiles.list(params?)`         | List profiles                |
| `profiles.get(profileId)`        | Get profile details          |
| `profiles.update(profileId, body)` | Update a profile           |
| `profiles.delete(profileId)`     | Delete a profile             |

### Browsers

| Method                        | Description                        |
|-------------------------------|------------------------------------|
| `browsers.create(body)`      | Create a browser session           |
| `browsers.list(params?)`     | List browser sessions              |
| `browsers.get(sessionId)`    | Get browser session details        |
| `browsers.stop(sessionId)`   | Stop a browser session             |

### Skills

| Method                                         | Description                          |
|------------------------------------------------|--------------------------------------|
| `skills.create(body)`                         | Create a skill via generation        |
| `skills.list(params?)`                        | List skills                          |
| `skills.get(skillId)`                         | Get skill details                    |
| `skills.delete(skillId)`                      | Delete a skill                       |
| `skills.update(skillId, body)`                | Update skill metadata                |
| `skills.cancel(skillId)`                      | Cancel in-progress generation        |
| `skills.execute(skillId, body)`               | Execute a skill                      |
| `skills.refine(skillId, body)`                | Refine a skill with feedback         |
| `skills.rollback(skillId)`                    | Rollback to previous version         |
| `skills.executions(skillId, params?)`         | List skill executions                |
| `skills.executionOutput(skillId, executionId)` | Download execution output           |

### Marketplace

| Method                              | Description                         |
|-------------------------------------|-------------------------------------|
| `marketplace.list(params?)`        | List public marketplace skills      |
| `marketplace.get(skillSlug)`       | Get marketplace skill by slug       |
| `marketplace.clone(skillId)`       | Clone a marketplace skill           |
| `marketplace.execute(skillId, body)` | Execute a marketplace skill       |

## V3 API Reference

### Sessions

| Method                               | Description                          |
|--------------------------------------|--------------------------------------|
| `sessions.create(body)`             | Create session and run a task        |
| `sessions.list(params?)`            | List sessions                        |
| `sessions.get(sessionId)`           | Get session details                  |
| `sessions.stop(sessionId)`          | Stop a session                       |
| `sessions.files(sessionId, params?)` | List files in session workspace     |

## Error Handling

All API errors throw `BrowserUseError`:

```ts
import { BrowserUse, BrowserUseError } from "browser-use-sdk";

try {
  await client.tasks.get("nonexistent-id");
} catch (err) {
  if (err instanceof BrowserUseError) {
    console.error(err.statusCode); // 404
    console.error(err.message);    // "Task not found"
    console.error(err.detail);     // Raw error body
  }
}
```

The client automatically retries on `429` (rate limit) and `5xx` (server errors) with exponential backoff.

## TypeScript

Types are re-exported from `browser-use-sdk` and `browser-use-sdk/v3`. The SDK ships with full type definitions for all request/response shapes.

```ts
import type { CreateTaskRequest, TaskView } from "browser-use-sdk";
```

## License

MIT
