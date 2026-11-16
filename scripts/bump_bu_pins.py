"""Bump every `browser-use==X.Y.Z` pin in docs/ to the latest PyPI release. Prints the new version if anything changed."""
import json, re, sys, urllib.request
from pathlib import Path

latest = json.load(urllib.request.urlopen("https://pypi.org/pypi/browser-use/json", timeout=30))["info"]["version"]
if not re.fullmatch(r"\d+\.\d+\.\d+", latest):
    sys.exit(f"skip pre-release {latest}")
pin = re.compile(r"((?:browser-use(?:\[[a-z,]+\])?)?==)(\d+\.\d+\.\d+)")
changed = 0
for f in Path("docs").rglob("*.mdx"):
    s = f.read_text()
    # only touch pins on browser-use (or the bare `==X.Y.Z` pin note next to it in mcp.mdx)
    new = re.sub(r"(browser-use(?:\[[a-z,]+\])?==)\d+\.\d+\.\d+", rf"\g<1>{latest}", s)
    new = re.sub(r"(exact `==)\d+\.\d+\.\d+(` pin)", rf"\g<1>{latest}\g<2>", new)
    if new != s:
        f.write_text(new); changed += 1
print(latest if changed else "", end="")
