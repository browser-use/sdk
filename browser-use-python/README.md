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
browser-management resource currently lives in the explicit `browser_use_sdk.v3`
namespace; see the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).

HTTP 429 responses and GET responses with status 502, 503, or 504 are retried
up to three times. Retries use exponential backoff with jitter and honor
`Retry-After` values up to 60 seconds. Longer server delays surface the original
error immediately instead of retrying too early. Other failures, including
POST 5xx responses and transport errors, are not automatically retried. The
client's `timeout` applies to each HTTP attempt; retry waits add to elapsed time.

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
