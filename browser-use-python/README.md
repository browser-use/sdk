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
from browser_use_sdk import BrowserUse

client = BrowserUse(api_key="YOUR_API_KEY")

# Run a task and wait for completion
result = client.run("Go to google.com and search for 'browser use'").complete()
print(result.output)
```

## v2 API (default)

The default import gives you the v2 client with access to all resources:

```python
from browser_use_sdk import BrowserUse, BrowserUseError

client = BrowserUse(api_key="YOUR_API_KEY")

# Run (shortcut -- returns TaskHandle)
handle = client.run("Navigate to example.com and get the title")
result = handle.complete()

# Or use the tasks resource directly
task = client.tasks.create("Navigate to example.com and get the title")
result = client.tasks.get(str(task.id))
client.tasks.stop(str(task.id))

# Sessions
session = client.sessions.create()
sessions = client.sessions.list(page_size=20)
client.sessions.stop(str(session.id))
client.sessions.delete(str(session.id))

# Profiles
profile = client.profiles.create(name="my-profile")
client.profiles.update(str(profile.id), name="renamed")
client.profiles.delete(str(profile.id))

# Browsers
browser = client.browsers.create()
client.browsers.stop(str(browser.id))

# Billing
account = client.billing.account()
print(account.totalCreditsBalanceUsd)

# Skills
skills = client.skills.list()
client.skills.execute(skill_id, input="some input")

# Marketplace
marketplace_skills = client.marketplace.list()

# Files
url_info = client.files.session_url(session_id, file_name="doc.pdf", content_type="application/pdf", size_bytes=1024)
output = client.files.task_output(task_id, file_id)

client.close()
```

## Structured Output

Pass a Pydantic model to get typed results:

```python
from pydantic import BaseModel
from typing import List
from browser_use_sdk import BrowserUse

client = BrowserUse(api_key="YOUR_API_KEY")

class Product(BaseModel):
    name: str
    price: float

handle = client.run("Find the price of the MacBook Air", output_schema=Product)
result = handle.complete()
product = handle.parse_output(result)  # Product instance, fully typed
print(f"{product.name}: ${product.price}")
```

## v3 API (experimental)

The v3 API uses a simplified session-based model:

```python
from browser_use_sdk.v3 import BrowserUse

client = BrowserUse(api_key="YOUR_API_KEY")

# Run and wait for completion
result = client.run("Search for Browser Use on Google").complete()
print(result.output)

# Or use sessions resource directly
session = client.sessions.create("Search for Browser Use on Google")
result = client.sessions.get(str(session.id))
files = client.sessions.files(str(session.id))
client.sessions.stop(str(session.id))

client.close()
```

## Async Usage

Every resource method has an async counterpart:

```python
import asyncio
from browser_use_sdk import AsyncBrowserUse

async def main():
    async with AsyncBrowserUse(api_key="YOUR_API_KEY") as client:
        handle = await client.run("Go to example.com")
        result = await handle.complete()
        print(result.output)

asyncio.run(main())
```

Both v2 and v3 support context managers:

```python
async with AsyncBrowserUse(api_key="YOUR_API_KEY") as client:
    task = await client.tasks.create(task="Go to example.com")
```

## Polling and Streaming

### TaskHandle (v2)

`client.run()` returns a `TaskHandle` for waiting or streaming:

```python
from browser_use_sdk import BrowserUse

client = BrowserUse(api_key="YOUR_API_KEY")

# Block until the task reaches a terminal status
handle = client.run("Scrape the front page of HN")
result = handle.complete(timeout=300, interval=3)
print(result.output)

# Or iterate over intermediate states
handle = client.run("Another task")
for state in handle.stream(interval=5):
    print(state.status)
```

### SessionHandle (v3)

```python
from browser_use_sdk.v3 import BrowserUse

client = BrowserUse(api_key="YOUR_API_KEY")

handle = client.run("Find the weather in SF")
result = handle.complete(timeout=120)
print(result.output)
```

## Error Handling

All non-2xx responses raise `BrowserUseError`:

```python
from browser_use_sdk import BrowserUse, BrowserUseError

client = BrowserUse(api_key="YOUR_API_KEY")

try:
    client.tasks.get("nonexistent-id")
except BrowserUseError as e:
    print(e.status_code)  # 404
    print(e.message)      # "Task not found"
    print(e.detail)       # Full response body (dict or None)
```

Retries are automatic: the SDK retries up to 3 times with exponential backoff
on 429 (rate limit) and 5xx (server error) responses.

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
    api_key="YOUR_API_KEY",
    base_url="https://custom-endpoint.example.com/api/v2",  # override base URL
    timeout=60.0,  # request timeout in seconds (default: 30)
)
```

## License

MIT
