"""
Sessions -- run multiple tasks in the same browser session.

Sessions let you chain tasks that share browser state (cookies, tabs, etc).
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk import AsyncBrowserUse

load_dotenv()


async def main():
    client = AsyncBrowserUse()

    # Create a session with a UK proxy
    session = await client.sessions.create(proxy_country_code="uk")
    print(f"Session: {session.id}")
    print(f"Watch live: {session.live_url}")

    # Run a task in this session
    output1 = await client.run(
        "Go to google.co.uk and search for 'browser automation'",
        session_id=str(session.id),
    )
    print(f"Task 1: {output1}")

    # Run another task in the same session (browser state is preserved)
    output2 = await client.run(
        "Click on the first search result and summarize the page",
        session_id=str(session.id),
    )
    print(f"Task 2: {output2}")

    # Clean up
    await client.sessions.stop(str(session.id))
    await client.sessions.delete(str(session.id))


asyncio.run(main())
