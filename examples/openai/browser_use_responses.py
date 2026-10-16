"""Connect OpenAI Responses to a dedicated Browser Use Cloud browser."""

import asyncio
import os

from browser_use_driver import BrowserUseDriver, allowed_url
from browser_use_sdk.v4 import AsyncBrowserUse
from openai import AsyncOpenAI
from openai.lib.browser import AsyncBrowserToolset
from openai.lib.responses_tool_runner import AsyncResponsesToolRunner
from playwright.async_api import async_playwright


async def read_example_page(client, page, model):
	driver = BrowserUseDriver(page)
	tools = AsyncBrowserToolset(
		driver,
		members=['navigate', 'get_page_text'],
		confirm=driver.confirm,
		url_policy=driver.url_policy,
	)
	runner = AsyncResponsesToolRunner(browser=tools)
	try:
		response = await runner.run(
			client,
			{
				'model': model,
				'store': False,
				'input': (
					'Use browser_navigate to open https://example.com/ and '
					'browser_get_page_text to read it. What is the heading, '
					'and what does the page say this domain is for?'
				),
			},
			max_steps=5,
		)
		if not driver.text or not allowed_url(page.url):
			raise RuntimeError('The model did not read the allowed page.')
		return response
	finally:
		runner.close()
		tools.close()


async def main():
	provider_key = os.environ['BROWSER_USE_API_KEY']
	model = os.environ['OPENAI_MODEL']
	async with (
		AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'], timeout=30, max_retries=0) as client,
		AsyncBrowserUse(api_key=provider_key) as provider,
		async_playwright() as playwright,
	):
		session = await provider.browsers.create(timeout=2, proxy_country_code=None, enable_recording=False)
		browser = None
		try:
			if not session.cdp_url:
				raise RuntimeError('Browser Use did not return a CDP URL.')
			browser = await playwright.chromium.connect_over_cdp(session.cdp_url, timeout=20000)
			if not browser.contexts:
				raise RuntimeError('Browser Use returned no browser context.')
			page = await browser.contexts[0].new_page()
			try:

				async def route_request(route):
					if allowed_url(route.request.url):
						await route.continue_()
					else:
						await route.abort()

				await page.route('**/*', route_request)
				response = await read_example_page(client, page, model)
				print(response.output_text)
			finally:
				await page.close()
		finally:
			try:
				if browser is not None:
					await browser.close()
			finally:
				await provider.browsers.stop(session.id)


if __name__ == '__main__':
	asyncio.run(main())
