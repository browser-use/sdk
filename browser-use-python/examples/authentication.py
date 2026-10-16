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
        print(result.result)


asyncio.run(main())
