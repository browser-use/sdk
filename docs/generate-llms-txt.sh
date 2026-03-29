#!/usr/bin/env bash
# Generates llms.txt and llms-full.txt for cloud and open-source docs.
# Only includes pages listed in docs.json navigation.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="https://docs.browser-use.com"

# Extract all page slugs from docs.json for a given product
get_nav_pages() {
  local product="$1"
  python3 -c "
import json, sys

with open('$SCRIPT_DIR/docs.json') as f:
    d = json.load(f)

def extract_pages(obj):
    pages = []
    if isinstance(obj, str):
        pages.append(obj)
    elif isinstance(obj, dict):
        for p in obj.get('pages', []):
            pages.extend(extract_pages(p))
        if 'openapi' in obj:
            pass  # skip openapi auto-generated pages
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
"
}

generate() {
  local section="$1"
  local product="$2"
  local dir="$SCRIPT_DIR/$section"
  local out_index="$dir/llms.txt"
  local out_full="$dir/llms-full.txt"

  echo "# ${section} docs" > "$out_index"
  echo "" >> "$out_index"

  echo "# Browser Use ${product} — Full Documentation" > "$out_full"
  echo "" >> "$out_full"

  get_nav_pages "$product" | while read -r slug; do
    local file="$SCRIPT_DIR/${slug}.mdx"
    [ -f "$file" ] || continue

    # Extract frontmatter
    title=""
    description=""
    in_frontmatter=false

    while IFS= read -r line; do
      if [[ "$line" == "---" ]]; then
        if $in_frontmatter; then
          break
        else
          in_frontmatter=true
          continue
        fi
      fi
      if $in_frontmatter; then
        if [[ "$line" =~ ^title:[[:space:]]*[\"\']?(.+)[\"\']?$ ]]; then
          title="${BASH_REMATCH[1]}"
          title="${title%\"}"
          title="${title%\'}"
          title="${title#\"}"
          title="${title#\'}"
        elif [[ "$line" =~ ^description:[[:space:]]*[\"\']?(.+)[\"\']?$ ]]; then
          description="${BASH_REMATCH[1]}"
          description="${description%\"}"
          description="${description%\'}"
          description="${description#\"}"
          description="${description#\'}"
        fi
      fi
    done < "$file"

    # llms.txt: index entry
    if [[ -n "$title" ]]; then
      if [[ -n "$description" ]]; then
        echo "- [${title}](${BASE_URL}/${slug}): ${description}" >> "$out_index"
      else
        echo "- [${title}](${BASE_URL}/${slug})" >> "$out_index"
      fi
    fi

    # llms-full.txt: full page content (strip frontmatter)
    echo "" >> "$out_full"
    echo "# ${title:-$slug}" >> "$out_full"
    echo "Source: ${BASE_URL}/${slug}" >> "$out_full"
    echo "" >> "$out_full"
    # Output everything after the closing --- of frontmatter
    awk 'BEGIN{n=0} /^---$/{n++; if(n==2){found=1; next}} found{print}' "$file" >> "$out_full"
    echo "" >> "$out_full"

  done

  echo "Generated $out_index ($(wc -l < "$out_index") lines)"
  echo "Generated $out_full ($(wc -l < "$out_full") lines)"
}

generate "cloud" "Cloud"
generate "open-source" "Open Source"

# Root files mirror cloud (primary product)
cp "$SCRIPT_DIR/cloud/llms.txt" "$SCRIPT_DIR/llms.txt"
cp "$SCRIPT_DIR/cloud/llms-full.txt" "$SCRIPT_DIR/llms-full.txt"
echo "Root llms.txt and llms-full.txt copied from cloud"
