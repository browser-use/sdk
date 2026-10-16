# V4 structured output verification

Verified on 2026-09-25. The SDK branch starts at main `674d92a`.

## Red to green

The test-only commit `5dc4164` precedes the implementation. Python's new tests
produced 33 failures: `output_schema` leaked onto the wire instead of
`outputSchema`, `RunSummary` discarded `output`, and `RunCreateRequest` rejected
the schema alias. The TypeScript type test failed on the missing public request
and response fields. TypeScript runtime passthrough alone already worked; a
compiler check is necessary to catch this regression.

After implementation:

- Python: `uv run pytest tests/ -m "not live and not prod" -q` — 129 passed,
  22 deselected. Includes existing bounded initial-visibility retry coverage.
- TypeScript: `npm test` — 162 passed, including the new public type contract.
- Python: `uv run --all-extras pyright src/ examples/v4_structured_output.py` —
  zero errors. Optional x402 dependencies are required for the full source check.
- TypeScript: `tsc --noEmit` and `tsc -p examples/tsconfig.json` — passed.
- Python wheel/sdist and TypeScript ESM/CJS/declaration builds — passed.

Tests cover Python sync/async creation, object/array/string/number/boolean/null
outputs through get and wait, null or absent schema/output, empty-schema wire
preservation, original text results, and extra request parameters. An empty
schema is transmitted unchanged; server schema validation remains authoritative.

## Canonical schema and regeneration

The three added properties are copied exactly from the current Cloud V4 OpenAPI:
`RunCreateRequest.outputSchema`, `RunSummary.output`, and
`RunSummary.outputSchema`. The snapshot and both docs references preserve all
other pre-existing schema content, including newer documentation fields.

Generation uses openapi-typescript 7.13.0 and datamodel-code-generator 0.45.0 with
the existing Taskfile options. The V4 Python invocation additionally uses
`--set-default-enum-member` so existing enum defaults are reproducible without
post-generation edits. Output remains arbitrary JSON (`Any` in Python,
`unknown` in TypeScript), with nullable optional schema objects. No automatic
Pydantic class conversion or schema-derived TypeScript inference is added.

## Live verification

The coordinating task ran the patched SDKs against an isolated full Cloud stack
on the existing VM with real GPT-6 Luna provider calls. This was **not a staging
or production deployment**. The task browsed `https://example.com` and extracted
its title, first description sentence, and source URL.

| Client | Completed run | Verified behavior |
| --- | --- | --- |
| Python | `6d6a7e19-e8e4-405c-94eb-13e9f4465684` | `output_schema` create; async wait; sync get and wait; output matches requested schema and text JSON |
| TypeScript | `7a9d63e6-da2c-4383-8df6-8397f3b01e44` | `outputSchema` create; get and wait expose matching parsed output |

Both returned:

```json
{
  "title": "Example Domain",
  "sourceUrl": "https://example.com",
  "firstSentence": "This domain is for use in documentation examples without needing permission."
}
```

The coordinating task also verified a plain unstructured run and a Cloud-side
same-session correction: a test wrapper changed the title to numeric `123`, then
real GPT-6 Luna corrected it without creating another agent session or changing
existing browser tool history. Combined provider cost for the three runs was
$0.006108. That correction belongs to the companion Cloud implementation;
the SDK only transmits the schema and exposes the response.

No merge, publish, deployment, AWS changes, or production changes were made.
