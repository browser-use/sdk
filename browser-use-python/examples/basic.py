"""
Basic task -- run a task and get the result.
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk import AsyncBrowserUse

load_dotenv()


async def main():
    client = AsyncBrowserUse()

    result = await client.run(
        "Search for the top 10 Hacker News posts and return the title and url."
    )
    print(result.output)
    print(result.id, result.status, len(result.steps))


asyncio.run(main())
