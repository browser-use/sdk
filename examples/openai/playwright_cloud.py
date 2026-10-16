"""Run OpenAI browser actions through Playwright and Browser Use Cloud."""

import asyncio
import os

from browser_use_sdk.v4 import AsyncBrowserUse
from openai import AsyncOpenAI
from openai.lib.browser import AsyncBrowserToolset
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner
from playwright.async_api import async_playwright

from playwright_browser import PlaywrightBrowser


async def confirm(context):
    return True


async def main() -> None:
    async with (
        AsyncBrowserUse() as cloud,
        AsyncOpenAI(timeout=180, max_retries=5) as client,
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
            driver = PlaywrightBrowser(page)
            tools = AsyncBrowserToolset(
                driver, members=["read_page", "click", "type", "select_option"], confirm=confirm
            )
            runner = AsyncResponsesToolRunner(browser=tools)
            try:
                response = await runner.run(
                    client,
                    {
                        "model": os.environ["OPENAI_MODEL"],
                        "input": "Read the page, click Learn more, and summarize the destination.",
                        "store": False,
                    },
                    max_steps=10,
                )
                print(response.output_text)
            finally:
                runner.close()
                tools.close()
                await driver.aclose()
        finally:
            try:
                if browser is not None:
                    await browser.close()
            finally:
                await cloud.browsers.stop(session.id)


if __name__ == "__main__":
    asyncio.run(main())
