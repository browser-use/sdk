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
from browser_use_sdk.v4 import BrowserUse

with BrowserUse() as client:
    run = client.runs.create("Find the top 3 trending repos on GitHub today")
    result = client.runs.wait_for_completion(run.id)
    print(result.result)
```

This is the current **Browser Use Agents** interface. Browser Infrastructure's
browser-management resource currently lives in the explicit `browser_use_sdk.v4`
namespace; see the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).

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
