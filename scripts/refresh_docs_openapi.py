"""Refresh only the public docs from production; SDK generation snapshots stay unchanged."""
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def refresh():
    specs = {}
    for version in (2, 3, 4):
        url = f'https://api.browser-use.com/api/v{version}/openapi.json'
        with urlopen(url, timeout=30) as response:
            spec = json.load(response)
        if not spec.get('openapi') or not spec.get('paths'):
            raise ValueError(f'Invalid OpenAPI response from {url}')
        specs[version] = spec
    # Fetch and parse every version successfully before replacing any local file.
    for version, spec in specs.items():
        for directory, indent in [('docs/openapi', 2), ('docs/cloud/openapi', 4)]:
            (ROOT / directory / f'v{version}.json').write_text(
                json.dumps(spec, indent=indent, ensure_ascii=True) + '\n'
            )
        print(f'V{version}: {len(spec["paths"])} paths from production')


if __name__ == '__main__':
    refresh()
