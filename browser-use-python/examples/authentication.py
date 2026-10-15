"""
Authentication -- use profiles to stay logged in across runs.

1. Create a profile
2. Log in once in a run with that profile
3. Future runs with the same profile are already logged in
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk.v4 import AsyncBrowserUse

load_dotenv()

PROFILE_ID = "your-profile-id"  # Create one with client.profiles.create()


async def main():
    async with AsyncBrowserUse() as client:
        # Run with your profile (inherits saved cookies/login state)
        run = await client.runs.create(
            "Go to my LinkedIn profile and get my connection count",
            browser_settings={"profileId": PROFILE_ID},
        )
        result = await client.runs.wait_for_completion(run.id)
        print(result.result)

        await client.browsers.stop(run.session_id)


asyncio.run(main())
