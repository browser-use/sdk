"""
Streaming -- monitor run progress by polling its events.
"""
import asyncio

from dotenv import load_dotenv
from browser_use_sdk.v4 import AsyncBrowserUse

load_dotenv()


async def main():
    async with AsyncBrowserUse() as client:
        run = await client.runs.create(
            "Go to wikipedia.org and find the featured article of the day."
        )

        # Read status before events so the last page is fetched after the run ended.
        after = None
        while True:
            status = (await client.runs.status(run.id)).status.value
            page = await client.runs.events(run.id, after=after)
            for event in page.events:
                print(event.type, event.data)
            after = page.next_after if page.next_after is not None else after

            if status in {"completed", "failed", "cancelled"} and not page.has_more:
                break
            await asyncio.sleep(2)

        result = await client.runs.get(run.id)
        print(f"\nOutput: {result.result}")


asyncio.run(main())
