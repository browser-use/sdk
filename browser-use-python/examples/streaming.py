"""
Streaming -- monitor task progress in real time.
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk import AsyncBrowserUse

load_dotenv()


async def main():
    client = AsyncBrowserUse()

    run = client.run(
        "Go to wikipedia.org and find the featured article of the day."
    )

    async for step in run:
        print(f"[Step {step.number}] {step.next_goal} -- {step.url}")

    print(f"\nOutput: {run.result.output}")


asyncio.run(main())
