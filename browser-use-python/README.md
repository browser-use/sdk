# browser-use-sdk

Official Python SDK for [Browser Use Cloud](https://browser-use.com).

## Install

```bash
uv add browser-use-sdk
```

## Quick Start

Eligible new Google, GitHub, or Microsoft signups receive a one-time $15 Cloud credit. No credit card is required. Email/password signups are not eligible; the credit does not renew. Start with the default V4 model (`gpt-5.6-luna`); paid-only models require a top-up. See [pricing](https://browser-use.com/pricing.md) for current eligibility and rates.

Get your API key at [cloud.browser-use.com/settings](https://cloud.browser-use.com/settings?tab=api-keys&new=1).

```bash
export BROWSER_USE_API_KEY=your_key
```

```python
from browser_use_sdk.v4 import BrowserUse

with BrowserUse() as client:
    run = client.runs.create("Find the top 3 trending repos on GitHub today")
    result = client.runs.wait_for_completion(run.id)
    if result.status != "completed":
        raise RuntimeError(f"Run {result.id}: {result.status}")
    print(result.result)
```

This is the current **Browser Use Agents** interface. SDK 3.11.3 or newer also
exposes `client.browsers.create` and `client.browsers.stop` in `browser_use_sdk.v4`.
Always stop standalone browsers explicitly; closing a client or disconnecting
CDP does not stop billing. See the [browser quickstart](https://docs.browser-use.com/cloud/browser/quickstart).
Existing V2/V3 integrations can keep their versioned imports.

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
