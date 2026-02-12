"""
Authentication -- use profiles to stay logged in across sessions.

1. Create a profile
2. Log in once in a session with that profile
3. Future sessions with the same profile are already logged in
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk import AsyncBrowserUse

load_dotenv()

PROFILE_ID = "your-profile-id"  # Create one with client.profiles.create()


async def main():
    client = AsyncBrowserUse()

    # Create a session with your profile (inherits saved cookies/login state)
    session = await client.sessions.create(profile_id=PROFILE_ID)

    # Run an authenticated task
    handle = await client.run(
        "Go to my LinkedIn profile and get my connection count",
        session_id=str(session.id),
    )
    result = await handle.complete()
    print(result.output)

    await client.sessions.stop(str(session.id))


asyncio.run(main())
