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
from browser_use_sdk import AsyncBrowserUse

client = AsyncBrowserUse()
result = await client.run("Find the top 3 trending repos on GitHub today")
print(result.output)
```

## Docs

[docs.browser-use.com](https://docs.browser-use.com)

## License

MIT
