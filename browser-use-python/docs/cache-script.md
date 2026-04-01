# Script Caching — Zero-LLM Reruns

Run a task once with a browser agent, then re-execute the same task instantly with **$0 LLM cost**. The agent creates a deterministic Python script on the first call. Subsequent calls with the same task template skip the agent entirely and run the cached script.

## Quick Start

```python
from browser_use_sdk.v3 import BrowserUse

client = BrowserUse()
ws = client.workspaces.create(name="my-scraper")

# First call — agent explores, creates script (~$0.10, ~60s)
result = client.run(
    "Get the top {{5}} stories from https://news.ycombinator.com as JSON",
    workspace_id=str(ws.id),
)

# Second call — same template, different value → cached script ($0, ~5s)
result2 = client.run(
    "Get the top {{10}} stories from https://news.ycombinator.com as JSON",
    workspace_id=str(ws.id),
)
```

## How It Works

Use **double curly brackets** `{{value}}` in your task to mark parameters:

```
"Get prices from {{https://example.com}} for {{electronics}}"
                  ├── param 1 ──────────┘     ├── param 2 ──┘
```

The system:
1. Strips the values from brackets → creates a **template**: `"Get prices from {{}} for {{}}"`
2. Hashes the template → unique script identifier (e.g. `a7f3b2c1`)
3. Checks workspace for `scripts/a7f3b2c1.py`
   - **Not found**: runs the full agent, which creates and saves the script
   - **Found**: executes the cached script directly with the new parameter values

### Auto-Detection

Caching activates **automatically** when:
- The task contains `{{` and `}}`
- A `workspace_id` is provided

No extra flags needed. You can override with `cache_script=True` (force on) or `cache_script=False` (force off).

## Examples

### Parameterized scraping
```python
# Agent figures out how to scrape intro.co on first call
result = client.run(
    "Go to {{https://intro.co/marketplace}} and get all {{logistics}} experts as JSON",
    workspace_id=str(ws.id),
)

# Instant reruns with different keywords — $0 LLM
for keyword in ["marketing", "CEO", "finance", "e-commerce"]:
    result = client.run(
        f"Go to {{{{https://intro.co/marketplace}}}} and get all {{{{{keyword}}}}} experts as JSON",
        workspace_id=str(ws.id),
    )
    print(f"{keyword}: {len(result.output)} experts")
```

### No parameters (cache exact task)
```python
# Append empty brackets {{}} to signal "cache this exact task"
result = client.run(
    "Get the current Bitcoin price from coinmarketcap.com {{}}",
    workspace_id=str(ws.id),
)

# Re-running the exact same task — cached, $0
result2 = client.run(
    "Get the current Bitcoin price from coinmarketcap.com {{}}",
    workspace_id=str(ws.id),
)
```

### Multiple parameters
```python
result = client.run(
    "Go to {{https://help.netflix.com}} and get subscription prices for {{Germany,France,Japan}}",
    workspace_id=str(ws.id),
)

# Different countries, same template → cached
result2 = client.run(
    "Go to {{https://help.netflix.com}} and get subscription prices for {{US,UK,Brazil}}",
    workspace_id=str(ws.id),
)
```

### Force-enable without brackets
```python
# cache_script=True forces caching even without {{brackets}}
result = client.run(
    "Get the top stories from Hacker News",
    workspace_id=str(ws.id),
    cache_script=True,
)

# Exact same task string → cached
result2 = client.run(
    "Get the top stories from Hacker News",
    workspace_id=str(ws.id),
    cache_script=True,
)
```

### Force-disable
```python
# cache_script=False skips caching even if brackets are present
result = client.run(
    "Explain what {{templates}} means in Jinja",
    workspace_id=str(ws.id),
    cache_script=False,  # don't treat {{templates}} as a parameter
)
```

## How the Cached Script Works

The agent creates a standalone Python script that:
- Accepts parameters as a JSON array via `sys.argv[1]`
- Uses `requests` for simple HTTP or `playwright` for JavaScript-heavy / Cloudflare-protected sites
- Prints JSON to stdout
- Contains no AI/LLM calls — purely deterministic
- Is stored in the workspace at `scripts/{hash}.py`

You can download and inspect the script:
```python
files = client.workspaces.files(ws.id, prefix="scripts/")
for f in files.files:
    print(f.path, f.size)

# Download a script
client.workspaces.download(ws.id, "scripts/a7f3b2c1.py", to="./my_script.py")
```

## `cache_script` Parameter

| Value | Behavior |
|-------|----------|
| `None` (default) | Auto-detect: enabled when task has `{{}}` brackets AND workspace is attached |
| `True` | Force-enable caching. Requires `workspace_id` |
| `False` | Force-disable caching, even if brackets are present |

## Cost

| Call | LLM Cost | Time |
|------|----------|------|
| First (agent creates script) | Normal (~$0.05–1.00) | ~30–120s |
| Subsequent (cached script) | **$0** | ~3–10s |
