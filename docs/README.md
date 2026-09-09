# Mintlify Docs

The public site is built from this directory on `main`.

## AI exports

Mintlify generates `/llms.txt` and `/llms-full.txt` from the documentation and navigation. Do not check in static copies: they override the managed files and become stale. Site-wide AI guidance lives in `markdown.instructions` in `docs.json`. Put detailed guidance in navigable MDX pages so it appears in both human docs and AI exports.

The former `/cloud/llms*.txt` and `/open-source/llms*.txt` URLs serve small compatibility indexes linking to the managed root exports, which cover both products. Mintlify serves `.txt` assets through a static handler that bypasses page redirects; keep these pointers, not duplicated documentation bundles. Use `/llms.txt` for new links. Bux is retired; its old documentation routes redirect to the current product guide.

After publishing, check the normal public URLs (without relying only on a preview): `/llms.txt`, `/llms-full.txt`, the scoped compatibility indexes, and the changed `.md` pages. Mintlify or CDN caches can delay visibility.

## Validation

Run `npx mint validate` and `npx mint broken-links` from this directory. Run `python3 scripts/check_webhook_example.py` from the repository root for the webhook verifier's production-signer fixtures and malformed-input checks.
