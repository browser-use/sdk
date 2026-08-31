#!/usr/bin/env bash
# Generates llms.txt and llms-full.txt for cloud and open-source docs.
# Only includes pages listed in docs.json navigation.
# Groups pages by nav structure with section headers.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="https://docs.browser-use.com"
GENERATION_DIR=""
RECOVERY_DIR="$SCRIPT_DIR/.llms-generation-recovery"
RECOVERY_STAGING_DIR=""
PUBLISHING=false
PUBLISH_COMPLETE=false
PUBLISH_DESTINATIONS=(
  "$SCRIPT_DIR/llms.txt"
  "$SCRIPT_DIR/llms-full.txt"
  "$SCRIPT_DIR/open-source/llms.txt"
  "$SCRIPT_DIR/open-source/llms-full.txt"
  "$SCRIPT_DIR/cloud/llms.txt"
  "$SCRIPT_DIR/cloud/llms-full.txt"
)

# Hold a kernel lock for the whole generation. The wrapper serializes duplicate
# invocations in this worktree without relying on a PID-file cleanup race; the
# OS releases the lock even after an uncatchable process exit. Separate
# worktrees have separate outputs and therefore separate lock files.
if [[ "${BROWSER_USE_LLMS_GENERATION_LOCKED:-}" != "1" ]]; then
  exec python3 - "$SCRIPT_DIR/.llms-generation.lock" "$SCRIPT_DIR/generate-llms-txt.sh" "$@" <<'PY'
import fcntl
import os
import signal
import subprocess
import sys
import time

lock_path, script, *args = sys.argv[1:]
deadline = time.monotonic() + 60

with open(lock_path, "a+") as lock_file:
    while True:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                print(f"Timed out waiting for {lock_path}", file=sys.stderr)
                raise SystemExit(1)
            time.sleep(0.1)

    env = os.environ.copy()
    env["BROWSER_USE_LLMS_GENERATION_LOCKED"] = "1"
    lock_fd = lock_file.fileno()
    os.set_inheritable(lock_fd, True)
    child = subprocess.Popen(["bash", script, *args], env=env, pass_fds=(lock_fd,))

    def forward(signum, _frame):
        if child.poll() is None:
            child.send_signal(signum)

    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, forward)

    return_code = child.wait()
    raise SystemExit(return_code if return_code >= 0 else 128 - return_code)
PY
fi

restore_interrupted_publish() {
  [[ -d "$RECOVERY_DIR" ]] || return 0
  if [[ ! -f "$RECOVERY_DIR/ready" ]]; then
    echo "Incomplete llms recovery journal: $RECOVERY_DIR" >&2
    return 1
  fi

  local i
  for i in "${!PUBLISH_DESTINATIONS[@]}"; do
    if [[ -f "$RECOVERY_DIR/existed-$i" && -f "$RECOVERY_DIR/backup-$i" ]]; then
      continue
    fi
    if [[ -f "$RECOVERY_DIR/absent-$i" ]]; then
      continue
    fi
    echo "Invalid llms recovery journal entry $i: $RECOVERY_DIR" >&2
    return 1
  done

  for i in "${!PUBLISH_DESTINATIONS[@]}"; do
    if [[ -f "$RECOVERY_DIR/existed-$i" ]]; then
      if ! cp -p -- "$RECOVERY_DIR/backup-$i" "${PUBLISH_DESTINATIONS[$i]}"; then
        echo "Could not restore llms artifact ${PUBLISH_DESTINATIONS[$i]}" >&2
        return 1
      fi
    else
      if ! rm -f -- "${PUBLISH_DESTINATIONS[$i]}"; then
        echo "Could not remove newly created llms artifact ${PUBLISH_DESTINATIONS[$i]}" >&2
        return 1
      fi
    fi
  done
  if ! rm -rf -- "$RECOVERY_DIR"; then
    echo "Could not remove completed llms recovery journal: $RECOVERY_DIR" >&2
    return 1
  fi
  echo "Recovered an interrupted llms artifact publication"
}

cleanup() {
  local exit_code=$?
  trap - EXIT
  trap '' HUP INT TERM
  set +e
  if $PUBLISHING && ! $PUBLISH_COMPLETE; then
    restore_interrupted_publish
  fi
  if [[ -n "$RECOVERY_STAGING_DIR" ]]; then
    rm -rf -- "$RECOVERY_STAGING_DIR"
  fi
  if [[ -n "$GENERATION_DIR" ]]; then
    rm -rf -- "$GENERATION_DIR"
  fi
  exit "$exit_code"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

# A SIGKILL can land between destination renames. The journal lives outside the
# per-run temp directory so the next lock owner can restore the previous set
# before generating again. A staging journal is safe to discard because no
# destination moves begin until its atomic rename to RECOVERY_DIR.
for stale_recovery_staging in "$SCRIPT_DIR"/.llms-generation-recovery.staging.??????; do
  [[ -d "$stale_recovery_staging" ]] || continue
  rm -rf -- "$stale_recovery_staging"
done
restore_interrupted_publish

# The kernel lock guarantees no live generator owns one of these directories.
# Remove residue from an uncatchable prior exit before creating this run's temp.
for stale_generation_dir in "$SCRIPT_DIR"/.llms-generation.??????; do
  [[ -d "$stale_generation_dir" ]] || continue
  [[ "$(basename "$stale_generation_dir")" =~ ^\.llms-generation\.[[:alnum:]]{6}$ ]] || continue
  rm -rf -- "$stale_generation_dir"
done

GENERATION_DIR="$(mktemp -d "$SCRIPT_DIR/.llms-generation.XXXXXX")"

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

def process_group(group, indent=0, section_name=''):
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
        openapi = group.get('openapi')
        if isinstance(openapi, dict) and openapi.get('source'):
            label = f'{section_name} OpenAPI specification' if section_name else (f'{name} OpenAPI specification' if name else 'OpenAPI specification')
            lines.append(f'- [{label}]({BASE_URL}/{openapi[\"source\"]})')
        # Process direct page slugs first, then sub-groups
        direct = [p for p in group.get('pages', []) if isinstance(p, str)]
        subgroups = [p for p in group.get('pages', []) if isinstance(p, dict)]
        for page in direct:
            lines.extend(process_group(page, indent+1, section_name))
        for page in subgroups:
            lines.extend(process_group(page, indent+1, section_name))
    return lines

lines = []
for product_nav in d['navigation']['products']:
    if product_nav['product'].lower() == '$product'.lower():
        if 'tabs' in product_nav:
            for tab in product_nav['tabs']:
                if isinstance(tab, dict):
                    tab_name = tab.get('tab', '')
                    # Emit tab header for non-primary tabs to separate API sections
                    if tab_name and tab_name != product_nav['tabs'][0].get('tab', ''):
                        lines.append(f'')
                        lines.append(f'## {tab_name}')
                    groups = tab.get('groups', [])
                    if any(isinstance(g, dict) and 'openapi' in g for g in groups):
                        start = [g for g in groups if isinstance(g, dict) and g.get('group') == 'Get Started']
                        specs = [g for g in groups if isinstance(g, dict) and 'openapi' in g]
                        rest = [g for g in groups if g not in start and g not in specs]
                        groups = start + specs + rest
                    for g in groups:
                        lines.extend(process_group(g, section_name=tab_name))
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

for product_nav in d['navigation']['products']:
    if product_nav['product'].lower() != '$product'.lower():
        continue
    for tab in product_nav.get('tabs', []):
        if not isinstance(tab, dict):
            continue
        tab_name = tab.get('tab', '')
        for group in tab.get('groups', []):
            openapi = group.get('openapi') if isinstance(group, dict) else None
            if isinstance(openapi, dict) and openapi.get('source'):
                print(f'- {tab_name} OpenAPI specification: $BASE_URL/{openapi[\"source\"]}')
" >> "$out"
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

for product_nav in d['navigation']['products']:
    if product_nav['product'].lower() == '$product'.lower():
        if 'tabs' in product_nav:
            for tab in product_nav['tabs']:
                if isinstance(tab, dict):
                    for g in tab.get('groups', []):
                        for p in extract_pages(g):
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
      | python3 -c '
import re, sys

base_url = sys.argv[1]
source_url = sys.argv[2]
content = sys.stdin.read()
content = re.sub(r"\{/\*\s*prettier-ignore-(?:start|end)\s*\*/\}\s*", "", content)

def normalize_url(url):
    if url.startswith("#"):
        return source_url + url
    if url.startswith("/"):
        return base_url + url
    return url

def render_card(match):
    attributes = match.group(1)
    title = re.search(r"\btitle=\"([^\"]+)\"", attributes)
    href = re.search(r"\bhref=\"([^\"]+)\"", attributes)
    if not title or not href:
        return ""
    url = normalize_url(href.group(1))
    return f"[{title.group(1)}]({url})"

def render_link(match):
    url = normalize_url(match.group(1))
    return f"[{match.group(2)}]({url})"

def render_titled_component(match):
    attributes = match.group(2)
    title = re.search(r"\btitle=(\"|\x27)(.*?)\1", attributes, flags=re.DOTALL)
    if not title:
        return ""
    return f"\n**{title.group(2)}**\n"

content = re.sub(r"<Card\b([^>]*)>", render_card, content, flags=re.DOTALL)
content = re.sub(r"<a\s+href=\"([^\"]+)\"[^>]*>(.*?)</a>", render_link, content, flags=re.DOTALL)
content = re.sub(r"<a\s+id=(?:\"[^\"]*\"|\x27[^\x27]*\x27)\s*/>\s*", "", content)
content = re.sub(r"<(Step|Tab|Accordion)\b([^>]*)>", render_titled_component, content, flags=re.DOTALL)
content = re.sub(r"(<img\b[^>]*\bsrc=(?:\"|\x27))/(?!/)", rf"\1{base_url}/", content, flags=re.DOTALL)
content = re.sub(r"(\]\()/(?!/)", rf"\1{base_url}/", content)
content = re.sub(r"(\]\()#(?=[^)]+)", rf"\1{source_url}#", content)
sys.stdout.write(content)
' "$BASE_URL" "$BASE_URL/$slug" \
      | sed -E 's#<\/?(CodeGroup|Note|Tip|Warning|Info|Callout|Card|Tabs|Tab|Steps|Step|Accordion|AccordionGroup)[^>]*>##g' \
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
rendered = "\n".join(line.rstrip() for line in "\n".join(out).splitlines()).rstrip()
sys.stdout.write(rendered + "\n" if rendered else "")
' >> "$out"
  done

  echo "Generated $out ($(wc -l < "$out") lines)"
}

# --- Cloud ---
CLOUD_INDEX="$GENERATION_DIR/llms.txt"
CLOUD_FULL="$GENERATION_DIR/llms-full.txt"
CLOUD_INDEX_DEST="$SCRIPT_DIR/llms.txt"
CLOUD_FULL_DEST="$SCRIPT_DIR/llms-full.txt"

# Header
cat > "$CLOUD_INDEX" << 'HEADER'
# Browser Use Cloud

> Browser Use Cloud has two products. **Browser Use Agents** accept a
> natural-language goal and complete the web task. **Browser Infrastructure**
> is hosted cloud browser infrastructure for AI agents, controlled through the
> SDK, REST, or CDP. Auth uses
> `X-Browser-Use-API-Key` (keys start with `bu_`).

- Dashboard: https://cloud.browser-use.com
- Create API key: https://cloud.browser-use.com/settings?tab=api-keys&new=1
- Docs: https://docs.browser-use.com
- Developer overview: https://browser-use.com/developers.md — Choose between Browser Use Agents, Browser Infrastructure, and the Open Source Library, and select an interface for a new integration.
- Pricing: https://browser-use.com/pricing.md — Current plans, credits, and usage rates.
- Product map: https://browser-use.com/llms.txt — Canonical machine-readable routes for Browser Use products and documentation.
- Open-source repo: https://github.com/browser-use/browser-use — The self-hosted Python library; its API differs from the Cloud SDK.

The V2, V3, and V4 references remain available below. Use the developer
overview to choose an interface for a new integration.

**TypeScript V4 browser settings:** The generated `RunBrowserSettings` type
currently requires `proxyCountryCode`; pass `"us"` to retain the default
managed residential proxy, or `null` to disable the proxy.

**Stopping standalone browsers:** Do not use `client.close()`,
`browser.close()`, or a dropped CDP connection as the API V4 stop operation.
Keep the browser session ID returned by `POST /api/v4/browsers`, then call
`PATCH /api/v4/browsers/{id}` with `{"action":"stop"}`. See the pricing page
for billing behavior.

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

**SDK typing:** Check the installed SDK types against the API reference. New
schema fields and model IDs can reach REST before a generated SDK release.

Before writing code, check if `browser-use-sdk` is already installed. If so, upgrade to the latest version. If not, install it:
- Python: `pip install --upgrade browser-use-sdk`
- TypeScript: `npm install browser-use-sdk@latest`

Set API key (starts with `bu_`). If the user doesn't have one yet, they can create one in one click at https://cloud.browser-use.com/settings?tab=api-keys&new=1:
```
export BROWSER_USE_API_KEY=bu_your_key_here
```

HEADER

# Append grouped nav entries
generate_index "cloud" "Cloud" "$GENERATION_DIR/cloud-index-body.txt"
cat "$GENERATION_DIR/cloud-index-body.txt" >> "$CLOUD_INDEX"
echo "Generated $CLOUD_INDEX ($(wc -l < "$CLOUD_INDEX") lines)"

# Full content
generate_full "cloud" "Cloud" "$CLOUD_FULL"

# --- Open Source ---
OS_INDEX="$GENERATION_DIR/open-source-llms.txt"
OS_FULL="$GENERATION_DIR/open-source-llms-full.txt"
OS_INDEX_DEST="$SCRIPT_DIR/open-source/llms.txt"
OS_FULL_DEST="$SCRIPT_DIR/open-source/llms-full.txt"

cat > "$OS_INDEX" << 'HEADER'
# Browser Use Open Source

> Self-hosted Python library for AI browser automation.

- GitHub: https://github.com/browser-use/browser-use
- Docs: https://docs.browser-use.com/open-source/introduction
- Product map: https://browser-use.com/llms.txt — Compare the Open Source Library with Browser Use Agents and Browser Infrastructure.

Install: `pip install browser-use`

HEADER

generate_index "open-source" "Open Source" "$GENERATION_DIR/open-source-index-body.txt"
cat "$GENERATION_DIR/open-source-index-body.txt" >> "$OS_INDEX"
echo "Generated $OS_INDEX ($(wc -l < "$OS_INDEX") lines)"

generate_full "open-source" "Open Source" "$OS_FULL"

# Stage the duplicate Cloud copies before publishing. Per-invocation paths keep
# worktrees isolated and the worktree lock prevents generators from
# interleaving. Each destination rename is atomic; if publication is interrupted
# between renames, the EXIT trap restores every previous destination.
cp "$CLOUD_INDEX" "$GENERATION_DIR/cloud-llms.txt"
cp "$CLOUD_FULL" "$GENERATION_DIR/cloud-llms-full.txt"

RECOVERY_STAGING_DIR="$(mktemp -d "$SCRIPT_DIR/.llms-generation-recovery.staging.XXXXXX")"
for i in "${!PUBLISH_DESTINATIONS[@]}"; do
  if [[ -f "${PUBLISH_DESTINATIONS[$i]}" ]]; then
    cp -p -- "${PUBLISH_DESTINATIONS[$i]}" "$RECOVERY_STAGING_DIR/backup-$i"
    touch "$RECOVERY_STAGING_DIR/existed-$i"
  else
    touch "$RECOVERY_STAGING_DIR/absent-$i"
  fi
done
touch "$RECOVERY_STAGING_DIR/ready"
command mv -- "$RECOVERY_STAGING_DIR" "$RECOVERY_DIR"
RECOVERY_STAGING_DIR=""
PUBLISHING=true

command mv -- "$CLOUD_INDEX" "$CLOUD_INDEX_DEST"
command mv -- "$CLOUD_FULL" "$CLOUD_FULL_DEST"
command mv -- "$OS_INDEX" "$OS_INDEX_DEST"
command mv -- "$OS_FULL" "$OS_FULL_DEST"
command mv -- "$GENERATION_DIR/cloud-llms.txt" "$SCRIPT_DIR/cloud/llms.txt"
command mv -- "$GENERATION_DIR/cloud-llms-full.txt" "$SCRIPT_DIR/cloud/llms-full.txt"
PUBLISH_COMPLETE=true
rm -rf -- "$RECOVERY_DIR"

echo "Published complete llms artifacts"
