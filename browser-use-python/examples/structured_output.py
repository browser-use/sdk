"""
Structured output -- get typed results using Pydantic models.

Pass output_schema to run() and the SDK handles JSON schema conversion
and response parsing automatically.
"""

import asyncio

from dotenv import load_dotenv
from pydantic import BaseModel
from browser_use_sdk import AsyncBrowserUse

load_dotenv()


class HackerNewsPost(BaseModel):
    title: str
    url: str
    score: int


class SearchResult(BaseModel):
    posts: list[HackerNewsPost]


async def main():
    client = AsyncBrowserUse()

    # await run() with output_schema returns a fully typed Pydantic model
    parsed = await client.run(
        "Find the top 10 Hacker News posts. Return title, url, and score for each.",
        output_schema=SearchResult,
    )

    if parsed is not None:
        for post in parsed.posts:
            print(f"{post.score} - {post.title}")
            print(f"  {post.url}\n")


asyncio.run(main())
