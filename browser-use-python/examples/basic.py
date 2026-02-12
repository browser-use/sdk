"""
Basic task -- run a task and get the result.
"""
import asyncio
from browser_use_sdk import AsyncBrowserUse


async def main():
    client = AsyncBrowserUse()

    # Option 1: Quick -- run() returns a TaskHandle you can poll
    handle = await client.run(
        "Search for the top 10 Hacker News posts and return the title and url."
    )
    result = await handle.complete()
    print(result.output)

    # Option 2: Direct -- use the tasks resource
    task = await client.tasks.create("What is the current price of Bitcoin?")
    print(f"Task created: {task.id}")

    # Poll for result
    finished = await client.tasks.get(str(task.id))
    print(finished.output)


asyncio.run(main())
