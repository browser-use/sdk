"""
Sessions -- run multiple tasks in the same browser session.

Pass a session ID to continue the conversation and workspace. A live browser
is reused when available.
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk.v4 import AsyncBrowserUse

load_dotenv()


async def main():
    async with AsyncBrowserUse() as client:
        session_id = None
        try:
            # A new run creates its session implicitly.
            first = await client.runs.create(
                "Go to google.co.uk and search for 'browser automation'",
                browser_settings={"proxyCountryCode": "uk"},
            )
            session_id = first.session_id
            first_result = await client.runs.wait_for_completion(first.id)
            print(f"Session: {session_id}")
            print(f"Task 1: {first_result.result}")

            # Pass the session ID to continue with the same state.
            follow_up = await client.runs.create(
                "Click the first search result and summarize the page",
                session_id=session_id,
            )
            follow_up_result = await client.runs.wait_for_completion(follow_up.id)
            print(f"Task 2: {follow_up_result.result}")
        finally:
            if session_id:
                await client.browsers.stop(session_id)


asyncio.run(main())
