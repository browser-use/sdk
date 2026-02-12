"""
Stealth mode -- use proxies for geo-specific browsing.

Every session gets a residential proxy. You can choose the country.
Without a session, tasks auto-create one with a US proxy.
"""
import asyncio
from browser_use_sdk import AsyncBrowserUse


async def main():
    client = AsyncBrowserUse()

    # Auto-session (US proxy by default)
    us_handle = await client.run(
        "Go to whatismyipaddress.com and tell me my location"
    )
    us_result = await us_handle.complete()
    print(f"US proxy: {us_result.output}")

    # Custom proxy -- Germany
    de_session = await client.sessions.create(proxy_country_code="de")
    de_handle = await client.run(
        "Go to whatismyipaddress.com and tell me my location",
        session_id=str(de_session.id),
    )
    de_result = await de_handle.complete()
    print(f"DE proxy: {de_result.output}")

    await client.sessions.stop(str(de_session.id))


asyncio.run(main())
