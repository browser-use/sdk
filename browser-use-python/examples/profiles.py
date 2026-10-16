"""
Profiles -- persist browser state (cookies, logins) across runs.

Create a profile once, then reuse it. Login state carries over.
"""

import asyncio

from dotenv import load_dotenv
from browser_use_sdk.v4 import AsyncBrowserUse

load_dotenv()


async def run_task(client: AsyncBrowserUse, task: str, settings: dict) -> str | None:
    """Run a task, stop its browsers (which saves the profile), and return the result."""
    run = await client.runs.create(task, browser_settings=settings)
    try:
        result = await client.runs.wait_for_completion(run.id)
    finally:
        # session_id is the agent session, not a browser id.
        browsers = await client.browsers.list(
            agent_session_id=run.session_id, filter_by="active"
        )
        for b in browsers.items:
            await client.browsers.stop(b.id)
    if result.status.value != "completed":
        raise RuntimeError(f"Run {result.status.value}: {result.error}")
    return result.result


async def main():
    async with AsyncBrowserUse() as client:
        # Create a named profile
        profile = await client.profiles.create(name="My LinkedIn Profile")
        print(f"Profile created: {profile.id}")
        settings = {"profileId": str(profile.id)}

        try:
            # First run: log in (profile saves the cookies)
            await run_task(client, "Go to linkedin.com and log in with my credentials", settings)

            # Later run: already logged in from saved profile
            result = await run_task(
                client, "Go to my LinkedIn profile and get my connection count", settings
            )
            print(f"Result: {result}")

            # List all profiles
            profiles = await client.profiles.list()
            print(f"You have {profiles.total_items} profiles")
        finally:
            await client.profiles.delete(profile.id)


asyncio.run(main())
