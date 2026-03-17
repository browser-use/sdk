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

  local prev_group=""

  # Sort by parent directory first, then filename, so files in the same
  # directory are always contiguous (prevents root-level pages from being
  # listed under a nested subdirectory heading).
  find "$dir" -name '*.mdx' -type f | while read -r f; do
    rel="${f#"$dir/"}"
    printf '%s\t%s\n' "$(dirname "$rel")" "$f"
  done | sort -t$'\t' -k1,1 -k2,2 | cut -f2 | while read -r file; do
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

    # Derive group heading from parent directory
    local rel_path="${file#"$dir/"}"
    local group_path
    group_path="$(dirname "$rel_path")"
    if [[ "$group_path" != "$prev_group" ]]; then
      # Convert path like "customize/agent" to "Customize > Agent"
      local heading=""
      IFS='/' read -ra parts <<< "$group_path"
      for part in "${parts[@]}"; do
        # Capitalize first letter, replace hyphens with spaces
        local label
        label="$(echo "$part" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"
        if [[ -n "$heading" ]]; then
          heading="${heading} > ${label}"
        else
          heading="$label"
        fi
      done
      if [[ "$heading" != "." ]]; then
        echo "" >> "$out"
        echo "## ${heading}" >> "$out"
      fi
      prev_group="$group_path"
    fi

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
