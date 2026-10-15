"""
Profiles -- persist browser state (cookies, logins) across runs.

Create a profile once, then reuse it. Login state carries over.
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk.v4 import AsyncBrowserUse

load_dotenv()


async def main():
    async with AsyncBrowserUse() as client:
        # Create a named profile
        profile = await client.profiles.create(name="My LinkedIn Profile")
        print(f"Profile created: {profile.id}")
        settings = {"profileId": str(profile.id)}

        # First run: log in (profile saves the cookies)
        login = await client.runs.create(
            "Go to linkedin.com and log in with my credentials",
            browser_settings=settings,
        )
        await client.runs.wait_for_completion(login.id)
        await client.browsers.stop(login.session_id)

        # Later run: already logged in from saved profile
        check = await client.runs.create(
            "Go to my LinkedIn profile and get my connection count",
            browser_settings=settings,
        )
        result = await client.runs.wait_for_completion(check.id)
        print(f"Result: {result.result}")

        await client.browsers.stop(check.session_id)

        # List all profiles
        profiles = await client.profiles.list()
        print(f"You have {profiles.total_items} profiles")

        # Clean up
        await client.profiles.delete(profile.id)


asyncio.run(main())
