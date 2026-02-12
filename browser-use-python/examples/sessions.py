"""
Sessions -- run multiple tasks in the same browser session.

Sessions let you chain tasks that share browser state (cookies, tabs, etc).
"""
import asyncio
from browser_use_sdk import AsyncBrowserUse


async def main():
    client = AsyncBrowserUse()

    # Create a session with a UK proxy
    session = await client.sessions.create(proxy_country_code="uk")
    print(f"Session: {session.id}")
    print(f"Watch live: {session.liveUrl}")

    # Run a task in this session
    handle = await client.run(
        "Go to google.co.uk and search for 'browser automation'",
        session_id=str(session.id),
    )
    result = await handle.complete()
    print(f"Task 1: {result.output}")

    # Run another task in the same session (browser state is preserved)
    handle2 = await client.run(
        "Click on the first search result and summarize the page",
        session_id=str(session.id),
    )
    result2 = await handle2.complete()
    print(f"Task 2: {result2.output}")

    # Clean up
    await client.sessions.stop(str(session.id))
    await client.sessions.delete(str(session.id))


asyncio.run(main())
