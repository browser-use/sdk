import asyncio
import os
from pathlib import Path

from browser_use.integrations.openai import Bash, BrowserUse
from openai import AsyncOpenAI
from openai.lib.browser import AsyncBrowserToolset
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner


async def confirm(context):
    return True


async def main():
    model = os.environ["OPENAI_MODEL"]
    async with AsyncOpenAI(timeout=180, max_retries=5) as client, BrowserUse(use_cloud=True) as driver:
        tools = AsyncBrowserToolset(
            driver,
            additional_members=["run_script", "click_at", "hover_at", "drag_path", "hold_keys", "set_checked"],
            confirm=confirm,
        )
        runner = AsyncResponsesToolRunner(browser=tools, functions=[Bash(output_dir=Path("outputs"))])
        try:
            response = await runner.run(
                client,
                {
                    "model": model,
                    "store": False,
                    "input": "Open https://example.com, follow Learn more, and save a source-backed summary in summary.md using Bash.",
                },
                max_steps=30,
            )
            print(response.output_text)
        finally:
            runner.close()
            tools.close()


asyncio.run(main())
