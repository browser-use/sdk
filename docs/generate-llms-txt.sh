#!/usr/bin/env bash
# Generates llms.txt files for open-source and cloud docs.
# Each entry: - [Title](https://docs.browser-use.com/<slug>): Description

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="https://docs.browser-use.com"

generate() {
  local section="$1"
  local dir="$SCRIPT_DIR/$section"
  local out="$dir/llms.txt"

  echo "# ${section} docs" > "$out"
  echo "" >> "$out"

  find "$dir" -name '*.mdx' -type f | sort | while read -r file; do
    # Extract frontmatter title and description
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

    # Build slug from file path (strip base dir and .mdx extension)
    slug="${file#"$SCRIPT_DIR/"}"
    slug="${slug%.mdx}"

    if [[ -n "$title" ]]; then
      if [[ -n "$description" ]]; then
        echo "- [${title}](${BASE_URL}/${slug}): ${description}" >> "$out"
      else
        echo "- [${title}](${BASE_URL}/${slug})" >> "$out"
      fi
    fi
  done

  echo "Generated $out"
}

generate "open-source"
generate "cloud"
