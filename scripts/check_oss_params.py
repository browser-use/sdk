"""Fail when the open-source docs drift from the browser-use 1.0 signatures.

Run it in an environment where browser-use 1.0 is importable:

    uv run --project /path/to/browser-use python scripts/check_oss_params.py

docs/open-source/all-parameters.mdx marks each reference table with an MDX comment:

    {/* signature: Agent.__init__ */}   the table lists every named parameter, in order, with its exact default
    {/* ignored: Agent */}              the list names every 0.x Agent option that is accepted and ignored

The Option tables in agent.mdx, browsers.mdx and domains.mdx may only name real parameters.
"""

import ast
import inspect
import re
import sys
from pathlib import Path

import browser_use
from browser_use import ActionResult, Agent, Browser, ChatAnthropic, ChatBrowserUse, ChatGoogle, ChatOpenAI, Tools
from browser_use.agent import service

DOCS = Path(__file__).resolve().parents[1] / 'docs/open-source'
REFERENCE = DOCS / 'all-parameters.mdx'
TARGETS = {
	'Agent.__init__': Agent.__init__,
	'Agent.run': Agent.run,
	'Agent.run_sync': Agent.run_sync,
	'Agent.add_new_task': Agent.add_new_task,
	'Browser.__init__': Browser.__init__,
	'Browser.stop': Browser.stop,
	'ChatBrowserUse.__init__': ChatBrowserUse.__init__,
	'ChatOpenAI.__init__': ChatOpenAI.__init__,
	'ChatAnthropic.__init__': ChatAnthropic.__init__,
	'ChatGoogle.__init__': ChatGoogle.__init__,
	'Tools.action': Tools.action,
	'ActionResult': ActionResult,
}
# Option tables on the topic pages: they may only name real parameters (or 0.x ones the library accepts).
TOPIC_TABLES = {'agent.mdx': Agent.__init__, 'browsers.mdx': Browser.__init__, 'domains.mdx': Browser.__init__}
REQUIRED = 'required'


def params(fn) -> list[inspect.Parameter]:
	skip = (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
	return [p for p in inspect.signature(fn).parameters.values() if p.name != 'self' and p.kind not in skip]


def table_after(lines: list[str], start: int) -> list[list[str]]:
	"""Rows (cells) of the first Markdown table after line `start`, without the header and separator."""
	i = start
	while i < len(lines) and not lines[i].startswith('|'):
		i += 1
	rows = []
	while i < len(lines) and lines[i].startswith('|'):
		rows.append([c.strip() for c in re.split(r'(?<!\\)\|', lines[i].strip())[1:-1]])
		i += 1
	return rows[2:]


def code(cell: str) -> str | None:
	m = re.match(r'`([^`]+)`', cell)
	return m.group(1) if m else None


def check_signature(name: str, rows: list[list[str]]) -> list[str]:
	errors = []
	real = params(TARGETS[name])
	documented = [(code(r[0]) or r[0], r[1]) for r in rows]
	if [n for n, _ in documented] != [p.name for p in real]:
		missing = [p.name for p in real if p.name not in dict(documented)]
		extra = [n for n, _ in documented if n not in {p.name for p in real}]
		errors.append(f'{name}: documented {[n for n, _ in documented]}, signature {[p.name for p in real]}')
		if missing:
			errors.append(f'{name}: missing {missing}')
		if extra:
			errors.append(f'{name}: not in the signature {extra}')
		return errors
	for p, (_, cell) in zip(real, documented):
		if p.default is inspect.Parameter.empty:
			if cell != REQUIRED:
				errors.append(f'{name}({p.name}): required in the signature, docs say {cell!r}')
			continue
		literal = code(cell)
		try:
			value = ast.literal_eval(literal) if literal is not None else object()
		except (ValueError, SyntaxError):
			value = object()
		# exact type, except a str subclass sentinel such as Browser's 'us'; True == 1 does not count
		same_type = isinstance(p.default, type(value)) and isinstance(value, bool) == isinstance(p.default, bool)
		if value != p.default or not same_type:
			errors.append(f'{name}({p.name}): default {p.default!r}, docs say {cell!r}')
	return errors


def check_reference() -> list[str]:
	lines = REFERENCE.read_text().splitlines()
	errors, seen = [], set()
	for i, line in enumerate(lines):
		if m := re.fullmatch(r'\{/\* signature: (.+?) \*/\}', line.strip()):
			for name in [n.strip() for n in m.group(1).split(',')]:
				if name not in TARGETS:
					errors.append(f'line {i + 1}: unknown signature {name}')
					continue
				seen.add(name)
				errors += check_signature(name, table_after(lines, i + 1))
		elif re.fullmatch(r'\{/\* ignored: Agent \*/\}', line.strip()):
			seen.add('ignored')
			documented = set(re.findall(r'`(\w+)`', lines[i + 1]))
			if documented != set(service.IGNORED):
				errors.append(
					f'Agent ignored options: docs {sorted(documented)}, library {sorted(service.IGNORED)} '
					f'(missing {sorted(set(service.IGNORED) - documented)}, extra {sorted(documented - set(service.IGNORED))})'
				)
	for name in sorted(set(TARGETS) - seen):
		errors.append(f'{REFERENCE.name}: no table for {name}')
	if 'ignored' not in seen:
		errors.append(f'{REFERENCE.name}: no list of ignored Agent options')
	return errors


def check_topic_pages() -> list[str]:
	errors = []
	for page, fn in TOPIC_TABLES.items():
		lines = (DOCS / page).read_text().splitlines()
		names = {p.name for p in params(fn)} | set(service.IGNORED if fn is Agent.__init__ else ())
		for i, line in enumerate(lines):
			if not re.match(r'\|\s*Option\s*\|', line):
				continue
			for row in table_after(lines, i):
				option = re.match(r'`?(\w+)', row[0])
				if option and option.group(1) not in names:
					errors.append(f'{page}: option {option.group(1)!r} is not a parameter of {fn.__qualname__}')
	return errors


def main() -> int:
	version = getattr(browser_use, '__version__', None) or __import__('importlib.metadata').metadata.version('browser-use')
	if int(str(version).split('.')[0]) < 1:
		print(f'browser-use {version} is installed; this check needs 1.0 or newer')
		return 2
	errors = check_reference() + check_topic_pages()
	for e in errors:
		print(f'DRIFT {e}')
	print(f'browser-use {version}: {len(TARGETS)} signatures, {len(errors)} drift(s)')
	return 1 if errors else 0


if __name__ == '__main__':
	sys.exit(main())
