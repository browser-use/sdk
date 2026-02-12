"""
Streaming -- monitor task progress in real time.
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk import AsyncBrowserUse

load_dotenv()


async def main():
    client = AsyncBrowserUse()

    handle = await client.run(
        "Go to wikipedia.org and find the featured article of the day."
    )

    # stream() yields TaskStatusView on each poll
    async for status in handle.stream(interval=2):
        print(f"[{status.status}] Output: {status.output or '(running...)'}")

    # After the stream ends, get the full result
    result = await client.tasks.get(handle.id)
    print(f"\nFinal output: {result.output}")


asyncio.run(main())
