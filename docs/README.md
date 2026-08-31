# Mintlify Docs

This repository contains the Browser Use Open Source and Cloud documentation,
including Browser Use Agents and Browser Infrastructure.

## Machine-readable documentation

Navigation in `docs.json` is the source list for the tracked `llms.txt` and
`llms-full.txt` files. After changing a page, its description, or navigation,
regenerate all six artifacts from the repository root:

```bash
task docs:llms
```

CI runs the same generator and fails if the tracked artifacts drift.
