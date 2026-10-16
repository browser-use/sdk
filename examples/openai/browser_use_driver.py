"""Connect OpenAI Responses to a dedicated Browser Use Cloud browser."""

from urllib.parse import urlsplit

from openai.lib.browser import BrowserError, BrowserState


def allowed_url(url: str) -> bool:
	"""Keep the example on one HTTPS origin, without URL credentials."""
	try:
		parsed = urlsplit(url)
		return (
			parsed.scheme == 'https'
			and parsed.hostname == 'example.com'
			and parsed.port in (None, 443)
			and parsed.username is None
			and parsed.password is None
		)
	except ValueError:
		return False


class BrowserUseDriver:
	def __init__(self, page):
		self.page = page
		self.text = None

	async def state(self) -> BrowserState:
		if self.page.url != 'about:blank' and not allowed_url(self.page.url):
			raise BrowserError('Tab left the allowed site.')
		return {
			'tabs': [
				{
					'id': 'one',
					'title': await self.page.title(),
					'url': self.page.url,
					'active': True,
				}
			]
		}

	async def navigate(self, args):
		if args['tab_id'] not in (None, 'one') or not allowed_url(args['url']):
			raise BrowserError('Unknown tab or forbidden URL.')
		await self.page.goto(args['url'], wait_until='domcontentloaded', timeout=20000)
		if not allowed_url(self.page.url):
			raise BrowserError('The destination redirected outside the allowed site.')

	async def get_page_text(self, args):
		if args['tab_id'] not in (None, 'one') or not allowed_url(self.page.url):
			raise BrowserError('Reading this tab is not allowed.')
		self.text = await self.page.locator('body').inner_text(timeout=10000)
		return self.text

	async def confirm(self, context):
		return (
			context['member'] == 'navigate'
			and context['arguments']['tab_id'] in (None, 'one')
			and allowed_url(context['arguments']['url'])
		)

	async def url_policy(self, context, url):
		return context['member'] == 'navigate' and allowed_url(url)
