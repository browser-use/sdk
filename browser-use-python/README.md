# browser-use-sdk

Official Python SDK for [Browser Use Cloud](https://browser-use.com).

## Install

```bash
uv add browser-use-sdk
```

## Quick Start

Get your API key at [cloud.browser-use.com/settings](https://cloud.browser-use.com/settings?tab=api-keys&new=1).

```bash
export BROWSER_USE_API_KEY=your_key
```

```python
from browser_use_sdk import BrowserUse

with BrowserUse() as client:
    run = client.runs.create("Find the top 3 trending repos on GitHub today")
    result = client.runs.wait_for_completion(run.id)
    print(result.result)
```

Since 4.0.0 the default import is the V4 **Browser Use Agents** interface,
including the browser resource; see the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).
`browser_use_sdk.v4` keeps working as an alias.

## Migrating from 3.x

4.0.0 makes V4 the root import. Code that imported the V2 client from the root
(`client.tasks`, `client.run`, `TaskView`, ...) needs one import change and
nothing else; the V2 API itself is unchanged. Without the change, V2-only names
raise an `ImportError` and V2-only client attributes raise an `AttributeError`,
both naming `browser_use_sdk.v2`. `browser_use_sdk.v3` and `browser_use_sdk.v4`
are unchanged.

```diff
-from browser_use_sdk import AsyncBrowserUse
+from browser_use_sdk.v2 import AsyncBrowserUse
```

## v3 Bring Your Own LLM Key

Add your provider API key in Browser Use project settings, then enable BYOK for v3 agent runs:

```python
from browser_use_sdk.v3 import BrowserUse

client = BrowserUse(use_own_key=True)
result = client.run("Find the top 3 trending repos on GitHub today")
print(result.output)
```

## Docs

[docs.browser-use.com](https://docs.browser-use.com)

## License

MIT

## V4 structured output

Pass a JSON Schema dictionary to `runs.create(output_schema=...)`, then read the
parsed JSON value from `runs.get(...).output` or `runs.wait_for_completion(...).output`.
The async client supports the same parameters and fields. `run.result` remains the
text answer; `run.output_schema` echoes the requested schema. Omit `output_schema`
(or pass `None`) for an unstructured run.

```python
from browser_use_sdk.v4 import BrowserUse

with BrowserUse() as client:
    created = client.runs.create(
        "Open https://example.com and return its page title.",
        output_schema={
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        },
    )
    run = client.runs.wait_for_completion(created.id)
    print(run.status, run.output)
```

For Pydantic, pass `MyModel.model_json_schema()` and validate the returned value
with `MyModel.model_validate(run.output)`; model classes are not converted
automatically. See [sync and async examples](examples/v4_structured_output.py).
