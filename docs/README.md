# Mintlify Docs

The public site is built from this directory on `main`.

## AI exports

Mintlify generates `/llms.txt` and `/llms-full.txt` from the documentation and navigation. Do not check in static copies: they override the managed files and become stale. Site-wide AI guidance lives in `markdown.instructions` in `docs.json`. Put detailed guidance in navigable MDX pages so it appears in both human docs and AI exports.

Use `/llms.txt` for the current index and `/.well-known/llms-full.txt` for the managed full bundle. Mintlify supports both root and `.well-known` managed exports on this site. Full bundles may be cached for up to 24 hours; use the index and individual `.md` pages when freshness matters.

Do not restore `/cloud/llms*.txt` or `/open-source/llms*.txt` as static files. This site uses Mintlify Pro, while static `.txt` asset publishing requires Enterprise. Preview assets can work even though production retains a legacy asset. Page redirects also bypass these static routes. Old scoped URLs still serving historical files require Mintlify-side cleanup; neither a normal deploy nor the manual rebuild on September 9 refreshed them. The supported managed exports avoid this limitation without a plan change.

Bux is retired; its old documentation routes redirect to the current product guide.

After publishing, check the normal public URLs (without relying only on a preview): `/llms.txt`, `/.well-known/llms-full.txt`, the Bux redirects, and the changed `.md` pages. Mintlify or CDN caches can delay visibility.

## Validation

Run `npx mint validate` and `npx mint broken-links` from this directory. Run `python3 scripts/check_webhook_example.py` from the repository root for the webhook verifier's production-signer fixtures and malformed-input checks.
