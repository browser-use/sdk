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

def process_group(group, indent=0):
    lines = []
    if isinstance(group, str):
        entry = format_entry(group)
        if entry:
            lines.append(entry)
    elif isinstance(group, dict):
        name = group.get('group', '')
        if name:
            lines.append(f'')
            lines.append(f'## {name}')
        for page in group.get('pages', []):
            lines.extend(process_group(page, indent+1))
    return lines

lines = []
for product_nav in d['navigation']['products']:
    if product_nav['product'].lower() == '$product'.lower():
        if 'tabs' in product_nav:
            for tab in product_nav['tabs']:
                if isinstance(tab, dict):
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
    awk 'BEGIN{n=0} /^---$/{n++; if(n==2){found=1; next}} found{print}' "$file" >> "$out"
    echo "" >> "$out"
  done

  echo "Generated $out ($(wc -l < "$out") lines)"
}

# --- Cloud ---
CLOUD_INDEX="$SCRIPT_DIR/llms.txt"
CLOUD_FULL="$SCRIPT_DIR/llms-full.txt"

# Header
cat > "$CLOUD_INDEX" << 'HEADER'
# Browser Use Cloud SDK

> The most SOTA browser agent and the most scalable browser infrastructure. Built on the largest AI browser automation open-source library on GitHub with almost 100k stars.

- GitHub: https://github.com/browser-use/browser-use
- Dashboard: https://cloud.browser-use.com
- API key: https://cloud.browser-use.com/settings?tab=api-keys&new=1
- Open Source: https://github.com/browser-use/browser-use
- Docs: https://docs.browser-use.com
- OpenAPI spec (v3): https://docs.browser-use.com/cloud/openapi/v3.json
- Stealth benchmark: https://browser-use.com/posts/stealth-benchmark
- Agent benchmark (online Mind2Web): https://browser-use.com/posts/online-mind2web-benchmark
- Blog: https://browser-use.com/posts
- API v2 Reference: https://docs.browser-use.com/cloud/api-v2-overview

Install:
- Python: `pip install browser-use-sdk`
- TypeScript: `npm install browser-use-sdk`

HEADER

# Append grouped nav entries
generate_index "cloud" "Cloud" "/tmp/cloud_index_body.txt"
cat /tmp/cloud_index_body.txt >> "$CLOUD_INDEX"
echo "" >> "$CLOUD_INDEX"
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

Install: `pip install browser-use`

HEADER

generate_index "open-source" "Open Source" "/tmp/os_index_body.txt"
cat /tmp/os_index_body.txt >> "$OS_INDEX"
echo "" >> "$OS_INDEX"
echo "Generated $OS_INDEX ($(wc -l < "$OS_INDEX") lines)"

generate_full "open-source" "Open Source" "$OS_FULL"

# Copy cloud files to cloud/ directory (symlinks don't work on Mintlify)
cp "$SCRIPT_DIR/llms.txt" "$SCRIPT_DIR/cloud/llms.txt"
cp "$SCRIPT_DIR/llms-full.txt" "$SCRIPT_DIR/cloud/llms-full.txt"
echo "Copied root llms files to cloud/"
