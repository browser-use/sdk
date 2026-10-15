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


async def main():
    async with AsyncBrowserUse() as client:
        # Default proxy (US)
        us = await client.runs.create(TASK)
        print(f"US proxy: {(await client.runs.wait_for_completion(us.id)).result}")

        # Custom proxy -- Germany
        de = await client.runs.create(TASK, browser_settings={"proxyCountryCode": "de"})
        print(f"DE proxy: {(await client.runs.wait_for_completion(de.id)).result}")

        await client.browsers.stop(us.session_id)
        await client.browsers.stop(de.session_id)


asyncio.run(main())
