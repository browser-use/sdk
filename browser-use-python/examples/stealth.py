"""
Stealth mode -- use proxies for geo-specific browsing.

Every run's browser gets a residential proxy. You can choose the country;
the default is US.
"""

import asyncio

from dotenv import load_dotenv
from browser_use_sdk.v4 import AsyncBrowserUse

load_dotenv()

TASK = "Go to whatismyipaddress.com and tell me my location"


async def run_task(client: AsyncBrowserUse, **settings) -> str | None:
    """Run TASK, stop its browsers, and return the result."""
    run = await client.runs.create(TASK, **settings)
    try:
        result = await client.runs.wait_for_completion(run.id)
    finally:
        # session_id is the agent session; each of its browsers has its own id.
        browsers = await client.browsers.list(
            agent_session_id=run.session_id, filter_by="active"
        )
        for b in browsers.items:
            await client.browsers.stop(b.id)
    if result.status.value != "completed":
        raise RuntimeError(f"Run {result.status.value}: {result.error}")
    return result.result


async def main():
    async with AsyncBrowserUse() as client:
        # Default proxy (US)
        print(f"US proxy: {await run_task(client)}")

        # Custom proxy -- Germany
        print(f"DE proxy: {await run_task(client, browser_settings={'proxyCountryCode': 'de'})}")


asyncio.run(main())
