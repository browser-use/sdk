"""A small, single-page Playwright driver for OpenAI's AsyncBrowserToolset."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from secrets import token_hex

from openai.lib.browser import (
    BrowserError,
    BrowserReadV1,
    BrowserState,
    ClickInput,
    ReadPageInput,
    SelectOptionInput,
    TypeInput,
)
from playwright.async_api import ElementHandle, Error, JSHandle, Page

_SNAPSHOT = """({prefix, full}) => {
  const targets = Object.create(null), elements = [], omitted = new Set();
  const clip = (s, n) => String(s ?? '').trim().slice(0, n).toWellFormed();
  const encoder = new TextEncoder();
  for (const el of document.querySelectorAll('button, a[href], input, textarea, select')) {
    if (!el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) ||
        el.matches(':disabled, [aria-disabled="true"]')) continue;
    if (el.tagName === 'INPUT' && !['text', 'search', 'email', 'tel', 'url', 'button', 'submit'].includes(el.type)) continue;
    if (elements.length === 50) { omitted.add('target_limit'); break; }
    const role = el.tagName === 'SELECT' ? 'combobox'
      : el.tagName === 'TEXTAREA' || (el.tagName === 'INPUT' && !['button', 'submit'].includes(el.type)) ? 'textbox' : 'button';
    const labelNode = el.labels?.[0]?.cloneNode(true);
    labelNode?.querySelectorAll('button, input, textarea, select').forEach(control => control.remove());
    const label = clip(el.getAttribute('aria-label') || labelNode?.textContent ||
      (role === 'button' ? el.innerText || el.value : '') || el.getAttribute('placeholder') || el.getAttribute('name'), 64) || role;
    const ref = `${prefix}-${elements.length}`;
    const item = {ref, role, label};
    if (role === 'combobox') {
      item.options = [];
      for (const option of el.options) {
        if (option.disabled || option.closest('optgroup:disabled')) continue;
        if (item.options.length === 32 || encoder.encode(option.value).length > 512 || option.value !== option.value.toWellFormed()) {
          omitted.add('value'); continue;
        }
        item.options.push({label: clip(option.label, 64) || '(blank)', value: option.value});
      }
    }
    elements.push(item);
    targets[ref] = el;
  }
  const body = full ? document.body?.innerText || '' : '';
  if (body.length > 4000) omitted.add('text_limit');
  return {report: {version: 1, text: clip(body, 4000), elements, omitted: [...omitted]}, targets};
}"""


async def _dispose(handle: JSHandle | None) -> None:
    if handle is not None:
        try:
            await handle.dispose()
        except Error:
            pass  # Ignore handles after navigation or page closure.


class PlaywrightBrowser:
    """Adapt one caller-owned Playwright page; do not share it across tasks."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self._snapshot: JSHandle | None = None

    async def state(self) -> BrowserState:
        if self.page.is_closed():
            return {"tabs": []}
        return {
            "tabs": [{"id": "page", "title": await self.page.title(), "url": self.page.url, "active": True}]
        }

    def _check_tab(self, tab_id: str | None) -> None:
        if tab_id not in (None, "page") or self.page.is_closed():
            raise BrowserError("This adapter only controls its open page.")

    async def aclose(self) -> None:
        """Release saved element refs without closing the caller's page."""
        snapshot, self._snapshot = self._snapshot, None
        await _dispose(snapshot)

    async def read_page(self, action: ReadPageInput) -> BrowserReadV1:
        self._check_tab(action["tab_id"])
        await self.aclose()
        self._snapshot = await self.page.evaluate_handle(
            _SNAPSHOT, {"prefix": token_hex(8), "full": action["filter"] == "all"}
        )
        return await self._snapshot.evaluate("snapshot => snapshot.report")

    @asynccontextmanager
    async def _target(self, action: ClickInput | TypeInput) -> AsyncIterator[ElementHandle]:
        self._check_tab(action["tab_id"])
        if not action["target"] or self._snapshot is None:
            raise BrowserError("Read the page and choose an element ref first.")
        try:
            handle = await self._snapshot.evaluate_handle(
                "(snapshot, ref) => snapshot.targets[ref] || null", action["target"]
            )
        except Error:
            raise BrowserError("The page changed. Read it again.") from None
        try:
            element = handle.as_element()
            if element is None:
                raise BrowserError("Unknown element ref. Read the page again.")
            yield element
        finally:
            await _dispose(handle)

    async def click(self, action: ClickInput) -> None:
        async with self._target(action) as element:
            await element.click(timeout=5000)

    async def type(self, action: TypeInput) -> None:
        async with self._target(action) as element:
            await element.fill(action["text"], timeout=5000)

    async def select_option(self, action: SelectOptionInput) -> None:
        async with self._target(action) as element:
            await element.select_option(action["values"], timeout=5000)

