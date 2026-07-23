"""Pull the live v1 OpenAPI, normalize it for docs rendering, write it where
Mintlify reads the reference.

Now pulls from the REAL deployed /api/v1 (staging by default) instead of the
local mock — the real backend serves its own spec at /api/v1/openapi.json. The
spec route is auth-gated, so a key is required.

    SPEC_URL=... SPEC_KEY=bu_... python export_spec.py

Defaults to staging. Output: docs/cloud/openapi/v1.json (servers -> source;
/api/v1 prefix stripped from paths).
"""

import json
import os
import urllib.request

# Real deployed spec (staging default). Override SPEC_URL for prod.
SPEC_URL = os.environ.get(
    "SPEC_URL",
    "https://api-staging-ufcbwvyv9yifyyvc3.browser-use.com/api/v1/openapi.json",
)
SPEC_KEY = os.environ.get("SPEC_KEY") or os.environ.get("BROWSER_USE_API_KEY")
OUT = "/Users/larsencundric/Documents/browser-use/sdk-wt-v1-docs/docs/cloud/openapi/v1.json"
# The playground calls this server. Strip the trailing /openapi.json to get the base.
SERVER = SPEC_URL.rsplit("/openapi.json", 1)[0]

if not SPEC_KEY:
    raise SystemExit("Set SPEC_KEY (or BROWSER_USE_API_KEY) — the spec route is auth-gated.")

req = urllib.request.Request(SPEC_URL, headers={"X-Browser-Use-API-Key": SPEC_KEY})
spec = json.loads(urllib.request.urlopen(req).read())

# 1. servers entry (relative paths resolve against this in the playground)
spec["servers"] = [{"url": SERVER, "description": "Browser Use API v1 (staging)"}]

# 2. strip the /api/v1 prefix from every path so paths are relative to the server
new_paths = {}
for path, ops in spec["paths"].items():
    stripped = path[len("/api/v1") :] if path.startswith("/api/v1") else path
    new_paths[stripped] = ops
spec["paths"] = new_paths

# 3. tidy info
spec["info"]["title"] = "Browser Use API v1"

json.dump(spec, open(OUT, "w"), indent=2)
print(f"wrote {OUT}: {len(spec['paths'])} paths, {len(spec.get('components', {}).get('schemas', {}))} schemas")
print(f"source: {SPEC_URL}")
print(f"server: {SERVER}")
