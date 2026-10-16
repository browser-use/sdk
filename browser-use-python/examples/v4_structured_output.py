"""Request V4 structured output with a JSON Schema and validate it explicitly."""

import asyncio

from pydantic import BaseModel

from browser_use_sdk.v4 import AsyncBrowserUse, BrowserUse


class PageInfo(BaseModel):
    title: str
    url: str


TASK = "Open https://example.com and return its page title and URL."
SCHEMA = PageInfo.model_json_schema()


def sync_example() -> None:
    with BrowserUse() as client:
        created = client.runs.create(TASK, output_schema=SCHEMA)
        run = client.runs.wait_for_completion(created.id)
        if run.status.value != "completed":
            raise RuntimeError(run.error or f"Run ended with {run.status.value}")
        # result remains the text answer; output is the parsed JSON value.
        print(run.result)
        if run.output is not None:
            print(PageInfo.model_validate(run.output))


async def async_example() -> None:
    async with AsyncBrowserUse() as client:
        created = await client.runs.create(TASK, output_schema=SCHEMA)
        run = await client.runs.wait_for_completion(created.id)
        if run.status.value != "completed":
            raise RuntimeError(run.error or f"Run ended with {run.status.value}")
        print(run.result)
        if run.output is not None:
            print(PageInfo.model_validate(run.output))


if __name__ == "__main__":
    # Choose either example. Both read BROWSER_USE_API_KEY from the environment.
    asyncio.run(async_example())
