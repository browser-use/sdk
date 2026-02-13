"""
Stealth mode -- use proxies for geo-specific browsing.

Every session gets a residential proxy. You can choose the country.
Without a session, tasks auto-create one with a US proxy.
"""

import asyncio

from dotenv import load_dotenv
from browser_use_sdk import AsyncBrowserUse

load_dotenv()


async def main():
    client = AsyncBrowserUse()

    # Auto-session (US proxy by default)
    us_output = await client.run("Go to whatismyipaddress.com and tell me my location")
    print(f"US proxy: {us_output}")

    # Custom proxy -- Germany
    de_session = await client.sessions.create(proxy_country_code="de")
    de_output = await client.run(
        "Go to whatismyipaddress.com and tell me my location",
        session_id=str(de_session.id),
        keep_alive=False,
    )
    print(f"DE proxy: {de_output}")

    await client.sessions.stop(str(de_session.id))


asyncio.run(main())
