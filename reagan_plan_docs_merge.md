# Docs Merge Plan: Unified Mintlify Site

## Current State
- **Cloud docs** (`docs/`): hosted at `docs.cloud.browser-use.com`, orange (#FE750E)
- **Open source docs** (`docs/open-source/`): hosted at `docs.browser-use.com`, blue (#2563EB)
- Both use `versions` dropdown with stubs redirecting to the other site
- They compete for the same SEO keywords

## Target State
- **Single site** on `docs.browser-use.com` using Mintlify **products** (dropdown)
- Two products: "Open Source" and "Cloud", each with their own color scheme
- File structure: `docs/open-source/...` and `docs/cloud/...`
- Shared assets at root: `docs/logo/`, `docs/favicon.ico`, `docs/style.css`
- Auto-generated `llms.txt` per product

## Steps

### Phase 1: Restructure Files

1. **Move cloud docs into `docs/cloud/` subfolder**
   - Move: `introduction.mdx`, `llm-quickstart.mdx`, `pricing.mdx`, `faq.mdx`
   - Move: `guides/`, `tips/`, `new-features/`
   - Move: `openapi/` (v2.json, v3.json)
   - Move: `images/cloud-banner-dark.png`, `images/concepts-overview.png`
   - Keep at root: `logo/`, `favicon.ico`, `style.css`, `docs.json`

2. **Move open-source docs into proper `docs/open-source/` subfolder** (already done)
   - Files are already in `docs/open-source/`
   - Need to remove OS-specific: `docs.json`, `favicon.ico`, `favicon.svg`, `logo/`

3. **Delete redirect stub pages**
   - `docs/open-source.mdx` (was just a meta redirect)
   - `docs/open-source/cloud.mdx` (was just a meta redirect)
   - `docs/open-source/use-cloud.mdx` (was just a meta redirect)

### Phase 2: Unified `docs.json`

Create a single `docs.json` using Mintlify `products` instead of `versions`:

```json
{
  "products": [
    {
      "name": "Open Source",
      "icon": "code",
      "colors": { "primary": "#2563EB" },
      "tabs": [
        {
          "tab": "Docs",
          "groups": [/* OS navigation from open-source/docs.json, prefixed with open-source/ */]
        }
      ]
    },
    {
      "name": "Cloud",
      "icon": "cloud",
      "colors": { "primary": "#FE750E" },
      "tabs": [
        {
          "tab": "Docs",
          "groups": [/* Cloud navigation, prefixed with cloud/ */]
        },
        {
          "tab": "API Reference",
          "groups": [/* OpenAPI groups */]
        }
      ]
    }
  ]
}
```

### Phase 3: Fix Links & Redirects

1. **Internal links in cloud docs**: Add `cloud/` prefix to all relative hrefs
2. **Internal links in OS docs**: Add `open-source/` prefix to all relative hrefs
3. **Cross-product links**: Update OS→Cloud and Cloud→OS links to use internal paths instead of external URLs
4. **Redirects**: Merge both redirect lists, update for new paths:
   - Old `docs.cloud.browser-use.com/*` → `cloud/*`
   - Old `docs.browser-use.com/*` → `open-source/*`
   - Keep existing redirect chains working

### Phase 4: Cleanup

1. Remove duplicate shared assets from `docs/open-source/` (logo, favicon, README)
2. Remove old `docs/open-source/docs.json`
3. Delete `docs/open-source.mdx` stub page

### Phase 5: llms.txt Script

- Script to auto-generate `open-source/llms.txt` and `cloud/llms.txt`
- Crawls each product's mdx files and generates a summary

## Open Questions
- Should the merged site live at `docs.browser-use.com` (Mintlify's recommendation)?
- Do we need to update DNS/Mintlify config for the domain change?
- Should `docs.cloud.browser-use.com` become a redirect to `docs.browser-use.com/cloud`?
