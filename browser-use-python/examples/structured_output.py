"""
Structured output -- get typed results using Pydantic models.

The SDK automatically converts your Pydantic model to a JSON schema
for the API, and parse_output() deserialises the response back into
your model.
"""
import asyncio
from typing import List

from pydantic import BaseModel
from browser_use_sdk import AsyncBrowserUse


class HackerNewsPost(BaseModel):
    title: str
    url: str
    score: int


class SearchResult(BaseModel):
    posts: List[HackerNewsPost]


async def main():
    client = AsyncBrowserUse()

    # Pass output_schema -- the SDK handles the rest
    handle = await client.run(
        "Find the top 10 Hacker News posts. Return title, url, and score for each.",
        output_schema=SearchResult,
    )

    result = await handle.complete()

    # parse_output() returns a fully typed SearchResult instance
    parsed = handle.parse_output(result)
    if parsed is not None:
        for post in parsed.posts:
            print(f"{post.score} - {post.title}")
            print(f"  {post.url}\n")


asyncio.run(main())
