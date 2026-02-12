"""
Profiles -- persist browser state (cookies, logins) across sessions.

Create a profile once, then reuse it. Login state carries over.
"""
import asyncio
from browser_use_sdk import AsyncBrowserUse


async def main():
    client = AsyncBrowserUse()

    # Create a named profile
    profile = await client.profiles.create(name="My LinkedIn Profile")
    print(f"Profile created: {profile.id}")

    # First session: log in (profile saves the cookies)
    session1 = await client.sessions.create(profile_id=str(profile.id))
    login_handle = await client.run(
        "Go to linkedin.com and log in with my credentials",
        session_id=str(session1.id),
    )
    await login_handle.complete()
    await client.sessions.stop(str(session1.id))

    # Later session: already logged in from saved profile
    session2 = await client.sessions.create(profile_id=str(profile.id))
    data_handle = await client.run(
        "Go to my LinkedIn profile and get my connection count",
        session_id=str(session2.id),
    )
    result = await data_handle.complete()
    print(f"Result: {result.output}")

    await client.sessions.stop(str(session2.id))

    # List all profiles
    profiles = await client.profiles.list()
    print(f"You have {profiles.totalItems} profiles")

    # Clean up
    await client.profiles.delete(str(profile.id))


asyncio.run(main())
