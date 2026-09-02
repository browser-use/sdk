#!/usr/bin/env bash
# Generates llms.txt and llms-full.txt for cloud and open-source docs.
# Only includes pages listed in docs.json navigation.
# Groups pages by nav structure with section headers.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="https://docs.browser-use.com"

# Extract frontmatter fields from an .mdx file
extract_frontmatter() {
  local file="$1"
  local field="$2"
  local value=""
  local in_frontmatter=false

  while IFS= read -r line; do
    if [[ "$line" == "---" ]]; then
      if $in_frontmatter; then break; else in_frontmatter=true; continue; fi
    fi
    if $in_frontmatter; then
      if [[ "$line" =~ ^${field}:[[:space:]]*[\"\']?(.+)[\"\']?$ ]]; then
        value="${BASH_REMATCH[1]}"
        value="${value%\"}"
        value="${value%\'}"
        value="${value#\"}"
        value="${value#\'}"
      fi
    fi
  done < "$file"
  echo "$value"
}

# Generate grouped llms.txt index from docs.json nav structure
generate_index() {
  local section="$1"
  local product="$2"
  local out="$3"

  python3 -c "
import json

with open('$SCRIPT_DIR/docs.json') as f:
    d = json.load(f)

BASE_URL = '$BASE_URL'
SCRIPT_DIR = '$SCRIPT_DIR'
CLOUD_V3_ONLY = {
    'cloud/tutorials/chat-ui',
    'cloud/tutorials/grow-therapy-compare',
}

def get_frontmatter(slug):
    import os
    filepath = os.path.join(SCRIPT_DIR, slug + '.mdx')
    if not os.path.exists(filepath):
        return None, None
    title = desc = ''
    in_fm = False
    with open(filepath) as f:
        for line in f:
            line = line.rstrip()
            if line == '---':
                if in_fm: break
                else: in_fm = True; continue
            if in_fm:
                if line.startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")
                elif line.startswith('description:'):
                    desc = line.split(':', 1)[1].strip().strip('\"').strip(\"'\")
    return title, desc

def format_entry(slug):
    if '$product'.lower() == 'cloud' and slug in CLOUD_V3_ONLY:
        return None
    title, desc = get_frontmatter(slug)
    if not title:
        return None
    if desc:
        return f'- [{title}]({BASE_URL}/{slug}): {desc}'
    return f'- [{title}]({BASE_URL}/{slug})'

seen_groups = set()

def has_direct_pages(group):
    \"\"\"Check if a group has any direct page slugs (not just sub-groups).\"\"\"
    for page in group.get('pages', []):
        if isinstance(page, str):
            return True
    return False

def process_group(group, indent=0):
    lines = []
    if isinstance(group, str):
        entry = format_entry(group)
        if entry:
            lines.append(entry)
    elif isinstance(group, dict):
        name = group.get('group', '')
        if name and name not in seen_groups:
            # Only emit header if this group has direct pages or is a leaf group
            if has_direct_pages(group):
                seen_groups.add(name)
                lines.append(f'')
                lines.append(f'## {name}')
            elif not any(isinstance(p, dict) and 'openapi' in p for p in group.get('pages', [])):
                # Sub-group container (like Pillars) — skip header but process children
                pass
        # Process direct page slugs first, then sub-groups
        direct = [p for p in group.get('pages', []) if isinstance(p, str)]
        subgroups = [p for p in group.get('pages', []) if isinstance(p, dict)]
        for page in direct:
            lines.extend(process_group(page, indent+1))
        for page in subgroups:
            lines.extend(process_group(page, indent+1))
    return lines

lines = []
for product_nav in d['navigation']['products']:
    if product_nav['product'].lower() == '$product'.lower():
        if 'tabs' in product_nav:
            for tab in product_nav['tabs']:
                if isinstance(tab, dict):
                    tab_name = tab.get('tab', '')
                    if '$product'.lower() == 'cloud' and tab_name == 'API v3':
                        continue
                    # Emit tab header for non-primary tabs to separate API sections
                    if tab_name and tab_name != product_nav['tabs'][0].get('tab', ''):
                        lines.append(f'')
                        lines.append(f'## {tab_name}')
                    for g in tab.get('groups', []):
                        lines.extend(process_group(g))
        if 'groups' in product_nav:
            for g in product_nav['groups']:
                lines.extend(process_group(g))

for line in lines:
    print(line)
" > "$out"

  echo "Generated $out ($(wc -l < "$out") lines)"
}

# Generate llms-full.txt with all page content
generate_full() {
  local section="$1"
  local product="$2"
  local out="$3"

  echo "# Browser Use ${product} — Full Documentation" > "$out"
  echo "" >> "$out"

  python3 -c "
import json

with open('$SCRIPT_DIR/docs.json') as f:
    d = json.load(f)

def extract_pages(obj):
    pages = []
    if isinstance(obj, str):
        pages.append(obj)
    elif isinstance(obj, dict):
        for p in obj.get('pages', []):
            pages.extend(extract_pages(p))
    elif isinstance(obj, list):
        for item in obj:
            pages.extend(extract_pages(item))
    return pages

CLOUD_V3_ONLY = {
    'cloud/tutorials/chat-ui',
    'cloud/tutorials/grow-therapy-compare',
}

for product_nav in d['navigation']['products']:
    if product_nav['product'].lower() == '$product'.lower():
        if 'tabs' in product_nav:
            for tab in product_nav['tabs']:
                if isinstance(tab, dict):
                    if '$product'.lower() == 'cloud' and tab.get('tab') == 'API v3':
                        continue
                    for g in tab.get('groups', []):
                        for p in extract_pages(g):
                            if '$product'.lower() != 'cloud' or p not in CLOUD_V3_ONLY:
                                print(p)
        if 'groups' in product_nav:
            for g in product_nav['groups']:
                for p in extract_pages(g):
                    print(p)
" | while read -r slug; do
    local file="$SCRIPT_DIR/${slug}.mdx"
    [ -f "$file" ] || continue

    local title
    title=$(extract_frontmatter "$file" "title")

    echo "" >> "$out"
    echo "# ${title:-$slug}" >> "$out"
    echo "Source: ${BASE_URL}/${slug}" >> "$out"
    echo "" >> "$out"
    awk 'BEGIN{n=0} /^---$/{n++; if(n==2){found=1; next}} found{print}' "$file" \
      | sed "s|](/cloud/|](${BASE_URL}/cloud/|g" \
      | python3 -c '
import re, sys

base_url = sys.argv[1]
content = sys.stdin.read()

def render_card(match):
    attributes = match.group(1)
    title = re.search(r"\btitle=\"([^\"]+)\"", attributes)
    href = re.search(r"\bhref=\"([^\"]+)\"", attributes)
    if not title or not href:
        return ""
    url = href.group(1)
    if url.startswith("/"):
        url = base_url + url
    return f"[{title.group(1)}]({url})"

sys.stdout.write(re.sub(r"<Card\b([^>]*)>", render_card, content, flags=re.DOTALL))
' "$BASE_URL" \
      | sed -E '/<\/?(CodeGroup|Note|Tip|Warning|Info|Card|Tabs|Tab|Steps|Step|Accordion|AccordionGroup)[^>]*>/d' \
      | sed -E '/^\{\/\* prettier-ignore-(start|end) \*\/\}$/d' \
      | python3 -c '
# Dedent component-nested content without corrupting code indentation:
# fenced code blocks are dedented by their common leading whitespace,
# prose lines lose at most one 4-space nesting level.
import sys, textwrap

block = None
out = []
for line in sys.stdin.read().split("\n"):
    if block is None:
        if line.lstrip().startswith("```"):
            block = [line]
        else:
            out.append(line[4:] if line.startswith("    ") else line)
    else:
        block.append(line)
        if line.lstrip().startswith("```"):
            out.append(textwrap.dedent("\n".join(block)))
            block = None
if block is not None:
    out.append(textwrap.dedent("\n".join(block)))
sys.stdout.write("\n".join(out))
' >> "$out"
  done

  echo "Generated $out ($(wc -l < "$out") lines)"
}

# --- Cloud ---
CLOUD_INDEX="$SCRIPT_DIR/llms.txt"
CLOUD_FULL="$SCRIPT_DIR/llms-full.txt"

# Header
cat > "$CLOUD_INDEX" << 'HEADER'
# Browser Use Cloud

> Browser Use Cloud has two products on the same managed browser
> infrastructure. **Agent** accepts a natural-language goal and completes the
> web task. **Browser** gives Playwright, Puppeteer, and other remote CDP
> clients direct control of a cloud browser. Both include stealth, residential
> proxies, profiles, and live observability. Auth uses
> `X-Browser-Use-API-Key` (keys start with `bu_`).

- Dashboard: https://cloud.browser-use.com
- Create API key: https://cloud.browser-use.com/settings?tab=api-keys&new=1
- Docs: https://docs.browser-use.com
- Product map: https://browser-use.com/llms.txt — Choose between Hosted Agents, Browser Infrastructure, and the Open Source Library.
- Pricing: https://browser-use.com/pricing.md — Current plans, credits, browser and proxy rates, model token prices, and billing behavior.
- OpenAPI spec (v4): https://docs.browser-use.com/cloud/openapi/v4.json
- Open-source repo: https://github.com/browser-use/browser-use — The open-source Python library. Note: the open-source API is different from the Cloud SDK. If you want the easiest path to production with managed infrastructure, use the Cloud SDK below.

**Choose API V4 for hard, high-accuracy tasks.** It is the recommended Agent API for new integrations and works especially well for long, complex workflows.

**Choose API V2 for simple tasks when extremely low cost or predictable speed matters more than accuracy.** V2 accuracy is substantially lower than V4.

Browser Use ranks #1 on the [Odysseys benchmark](https://odysseysbench.com/leaderboard). Use the benchmark when accuracy is the deciding factor.

**Stopping standalone browsers:** Do not use `client.close()`,
`browser.close()`, or a dropped CDP connection as the API V4 stop operation.
Keep the browser session ID returned by `POST /api/v4/browsers`, then call
`PATCH /api/v4/browsers/{id}` with `{"action":"stop"}`. This stops billing and
refunds unused browser time.

**Create and reuse a login profile:** Create one profile per end user, then pass
its ID as top-level `profileId` when creating browsers, or as
`browserSettings.profileId` on agent runs:
```bash
profile=$(curl -sS https://api.browser-use.com/api/v4/profiles \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"My user"}')
export BROWSER_USE_PROFILE_ID=$(echo "$profile" | jq -r .id)

curl -sS https://api.browser-use.com/api/v4/browsers \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"profileId\":\"$BROWSER_USE_PROFILE_ID\",\"proxyCountryCode\":\"us\"}"
```
Log in once in that browser, stop it, then use the same profile ID to start the
next browser already logged in. Full guide:
https://docs.browser-use.com/cloud/guides/authentication

**Current TypeScript SDK typing:** Pass `model` explicitly. Prefer
`gpt-5.6-luna`, the recommended V4 model; if the generated union does not yet
include it, use `grok-4.5` or call `POST /api/v4/runs` directly. Whenever
`browserSettings` is present, also pass `proxyCountryCode`: use `"us"` to keep
the default or `null` to disable the managed proxy. New model strings can reach
REST before the generated TypeScript union. The generated SDK request types do
not yet expose V4 `modelParams`; use REST for that field until the follow-up SDK
release.

Before writing code, check if `browser-use-sdk` is already installed. If so, upgrade to the latest version. If not, install it:
- Python: `pip install --upgrade browser-use-sdk`
- TypeScript: `npm install browser-use-sdk@latest`

Set API key (starts with `bu_`). If the user doesn't have one yet, they can create one in one click at https://cloud.browser-use.com/settings?tab=api-keys&new=1:
```
export BROWSER_USE_API_KEY=bu_your_key_here
```

HEADER

# Append grouped nav entries
generate_index "cloud" "Cloud" "/tmp/cloud_index_body.txt"
cat /tmp/cloud_index_body.txt >> "$CLOUD_INDEX"
echo "Generated $CLOUD_INDEX ($(wc -l < "$CLOUD_INDEX") lines)"

# Full content
generate_full "cloud" "Cloud" "$CLOUD_FULL"

# --- Open Source ---
OS_INDEX="$SCRIPT_DIR/open-source/llms.txt"
OS_FULL="$SCRIPT_DIR/open-source/llms-full.txt"

cat > "$OS_INDEX" << 'HEADER'
# Browser Use Open Source

> Self-hosted Python library for AI browser automation.

- GitHub: https://github.com/browser-use/browser-use
- Docs: https://docs.browser-use.com/open-source/introduction
- Product map: https://browser-use.com/llms.txt — Compare the Open Source Library with Hosted Agents and Browser Infrastructure.

Install: `pip install browser-use`

HEADER

generate_index "open-source" "Open Source" "/tmp/os_index_body.txt"
cat /tmp/os_index_body.txt >> "$OS_INDEX"
echo "Generated $OS_INDEX ($(wc -l < "$OS_INDEX") lines)"

generate_full "open-source" "Open Source" "$OS_FULL"

# Copy cloud files to cloud/ directory (symlinks don't work on Mintlify)
cp "$SCRIPT_DIR/llms.txt" "$SCRIPT_DIR/cloud/llms.txt"
cp "$SCRIPT_DIR/llms-full.txt" "$SCRIPT_DIR/cloud/llms-full.txt"
echo "Copied root llms files to cloud/"
