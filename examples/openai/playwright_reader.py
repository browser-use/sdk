"""Run OpenAI's reader example on a Browser Use Cloud browser."""

import asyncio
import os

from browser_use_sdk.v4 import AsyncBrowserUse
from openai import AsyncOpenAI
from openai.lib.browser import AsyncBrowserToolset, BrowserError, BrowserState, TabInput
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner
from playwright.async_api import Page, async_playwright


class Reader:
    def __init__(self, page: Page) -> None:
        self.page = page

    async def state(self) -> BrowserState:
        return {
            "tabs": [
                {
                    "id": "one",
                    "url": self.page.url or "about:blank",
                    "title": await self.page.title(),
                    "active": True,
                }
            ]
        }

    async def get_page_text(self, args: TabInput) -> str:
        if args["tab_id"] not in (None, "one"):
            raise BrowserError("Unknown tab.")
        return await self.page.locator("body").inner_text()


async def main() -> None:
    async with (
        AsyncBrowserUse() as cloud,
        AsyncOpenAI() as client,
        async_playwright() as playwright,
    ):
        session = await cloud.browsers.create(timeout=5)
        browser = None
        try:
            if not session.cdp_url:
                raise RuntimeError("Browser Use did not return a CDP URL.")
            browser = await playwright.chromium.connect_over_cdp(session.cdp_url)
            page = await browser.contexts[0].new_page()
            await page.goto("https://example.com", wait_until="domcontentloaded")
            tools = AsyncBrowserToolset(Reader(page), members=["get_page_text"])
            runner = AsyncResponsesToolRunner(browser=tools)
            try:
                response = await runner.run(
                    client,
                    {
                        "model": os.environ["OPENAI_MODEL"],
                        "input": "Read the page. What is its heading, and what is this domain for?",
                        "store": False,
                    },
                    max_steps=3,
                )
                print(response.output_text)
            finally:
                runner.close()
                tools.close()
        finally:
            try:
                if browser is not None:
                    await browser.close()
            finally:
                await cloud.browsers.stop(session.id)


if __name__ == "__main__":
    asyncio.run(main())
