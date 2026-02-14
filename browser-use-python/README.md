# browser-use-sdk

Official Python SDK for the [Browser Use](https://browser-use.com) cloud API.

Run AI-powered browser agents, manage sessions, profiles, skills, and more --
all from Python with both sync and async interfaces. Fully typed with Pydantic models.

## Installation

```bash
pip install browser-use-sdk
```

Or with your preferred package manager:

```bash
# uv
uv add browser-use-sdk

# poetry
poetry add browser-use-sdk
```

## Quick Start

```python
from browser_use_sdk import AsyncBrowserUse

client = AsyncBrowserUse()
result = await client.run("Go to google.com and search for 'browser use'")
print(result.output)
print(result.id, result.status)
```

## v2 API (default)

The default import gives you the v2 client with access to all resources:

```python
from browser_use_sdk import AsyncBrowserUse, BrowserUseError

client = AsyncBrowserUse()

result = await client.run("Navigate to example.com and get the title")

# Or use the tasks resource directly
task = await client.tasks.create("Navigate to example.com and get the title")
result = await client.tasks.get(str(task.id))
await client.tasks.stop(str(task.id))

# Sessions
session = await client.sessions.create()
sessions = await client.sessions.list(page_size=20)
await client.sessions.stop(str(session.id))
await client.sessions.delete(str(session.id))

# Profiles
profile = await client.profiles.create(name="my-profile")
await client.profiles.update(str(profile.id), name="renamed")
await client.profiles.delete(str(profile.id))

# Browsers
browser = await client.browsers.create()
await client.browsers.stop(str(browser.id))

# Billing
account = await client.billing.account()
print(account.total_credits_balance_usd)

# Skills
skills = await client.skills.list()
await client.skills.execute(skill_id, input="some input")

# Marketplace
marketplace_skills = await client.marketplace.list()

# Files
url_info = await client.files.session_url(session_id, file_name="doc.pdf", content_type="application/pdf", size_bytes=1024)
output = await client.files.task_output(task_id, file_id)
```

## Structured Output

Pass a Pydantic model to get typed results:

```python
from pydantic import BaseModel
from browser_use_sdk import AsyncBrowserUse

class Product(BaseModel):
    name: str
    price: float

client = AsyncBrowserUse()
result = await client.run("Find the price of the MacBook Air", schema=Product)
print(f"{result.output.name}: ${result.output.price}")
```

## Streaming

`client.run()` returns a dual-purpose handle: `await` it for the output, or `async for` it for step-by-step progress.

```python
from browser_use_sdk import AsyncBrowserUse

client = AsyncBrowserUse()
async for step in client.run("Scrape the front page of HN"):
    print(f"[{step.number}] {step.next_goal} — {step.url}")
```

## v3 API (experimental)

The v3 API uses a simplified session-based model:

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
output = await client.run("Search for Browser Use on Google")
print(output)

# Or use sessions resource directly
session = await client.sessions.create("Search for Browser Use on Google")
result = await client.sessions.get(str(session.id))
files = await client.sessions.files(str(session.id))
await client.sessions.stop(str(session.id))
```

## Sync Usage

A synchronous client is also available:

```python
from browser_use_sdk import BrowserUse

client = BrowserUse()
result = client.run("Go to example.com")

# Streaming (sync)
for step in client.stream("Scrape the front page of HN"):
    print(f"[{step.number}] {step.next_goal} — {step.url}")
```

## Error Handling

All non-2xx responses raise `BrowserUseError`:

```python
from browser_use_sdk import AsyncBrowserUse, BrowserUseError

client = AsyncBrowserUse()
try:
    await client.tasks.get("nonexistent-id")
except BrowserUseError as e:
    print(e.status_code)  # 404
    print(e.message)      # "Task not found"
    print(e.detail)       # Full response body (dict or None)
```

Retries are automatic: the SDK retries up to 3 times with exponential backoff
on 429 (rate limit) responses.

## Resource Methods

### v2

| Resource      | Method              | HTTP                                          |
|---------------|---------------------|-----------------------------------------------|
| billing       | `account()`         | `GET /billing/account`                        |
| tasks         | `create(task, **kw)`| `POST /tasks`                                 |
| tasks         | `list(**kw)`        | `GET /tasks`                                  |
| tasks         | `get(id)`           | `GET /tasks/{id}`                             |
| tasks         | `stop(id)`          | `PATCH /tasks/{id}`                           |
| tasks         | `status(id)`        | `GET /tasks/{id}/status`                      |
| tasks         | `wait(id, **kw)`    | Poll until terminal, return TaskView          |
| tasks         | `logs(id)`          | `GET /tasks/{id}/logs`                        |
| sessions      | `create(**kw)`      | `POST /sessions`                              |
| sessions      | `list(**kw)`        | `GET /sessions`                               |
| sessions      | `get(id)`           | `GET /sessions/{id}`                          |
| sessions      | `stop(id)`          | `PATCH /sessions/{id}`                        |
| sessions      | `delete(id)`        | `DELETE /sessions/{id}`                       |
| sessions      | `get_share(id)`     | `GET /sessions/{id}/public-share`             |
| sessions      | `create_share(id)`  | `POST /sessions/{id}/public-share`            |
| sessions      | `delete_share(id)`  | `DELETE /sessions/{id}/public-share`          |
| files         | `session_url(id)`   | `POST /files/sessions/{id}/presigned-url`     |
| files         | `browser_url(id)`   | `POST /files/browsers/{id}/presigned-url`     |
| files         | `task_output(t, f)` | `GET /files/tasks/{t}/output-files/{f}`       |
| profiles      | `create(**kw)`      | `POST /profiles`                              |
| profiles      | `list(**kw)`        | `GET /profiles`                               |
| profiles      | `get(id)`           | `GET /profiles/{id}`                          |
| profiles      | `update(id, **kw)`  | `PATCH /profiles/{id}`                        |
| profiles      | `delete(id)`        | `DELETE /profiles/{id}`                       |
| browsers      | `create(**kw)`      | `POST /browsers`                              |
| browsers      | `list(**kw)`        | `GET /browsers`                               |
| browsers      | `get(id)`           | `GET /browsers/{id}`                          |
| browsers      | `stop(id)`          | `PATCH /browsers/{id}`                        |
| skills        | `create(**kw)`      | `POST /skills`                                |
| skills        | `list(**kw)`        | `GET /skills`                                 |
| skills        | `get(id)`           | `GET /skills/{id}`                            |
| skills        | `update(id, **kw)`  | `PATCH /skills/{id}`                          |
| skills        | `delete(id)`        | `DELETE /skills/{id}`                         |
| skills        | `cancel(id)`        | `POST /skills/{id}/cancel`                    |
| skills        | `execute(id, **kw)` | `POST /skills/{id}/execute`                   |
| skills        | `refine(id, **kw)`  | `POST /skills/{id}/refine`                    |
| skills        | `rollback(id)`      | `POST /skills/{id}/rollback`                  |
| skills        | `executions(id)`    | `GET /skills/{id}/executions`                 |
| skills        | `execution_output()`| `GET /skills/{id}/executions/{eid}/output`    |
| marketplace   | `list(**kw)`        | `GET /marketplace/skills`                     |
| marketplace   | `get(slug)`         | `GET /marketplace/skills/{slug}`              |
| marketplace   | `clone(id)`         | `POST /marketplace/skills/{id}/clone`         |
| marketplace   | `execute(id, **kw)` | `POST /marketplace/skills/{id}/execute`       |

### v3

| Resource  | Method            | HTTP                             |
|-----------|-------------------|----------------------------------|
| sessions  | `create(task, **kw)` | `POST /sessions`              |
| sessions  | `list(**kw)`      | `GET /sessions`                  |
| sessions  | `get(id)`         | `GET /sessions/{id}`             |
| sessions  | `stop(id)`        | `POST /sessions/{id}/stop`       |
| sessions  | `files(id, **kw)` | `GET /sessions/{id}/files`       |

## Configuration

```python
client = BrowserUse(
    api_key="bu_...",
    base_url="https://custom-endpoint.example.com/api/v2",  # override base URL
    timeout=60.0,  # request timeout in seconds (default: 30)
)
```

## License

MIT
