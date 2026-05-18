---
description: |
  [TOPIC] Environment Variables
  [DETAILS] Environment variables read by scitex-template. Currently only
  SCITEX_DIR (ecosystem-wide state-directory override).
tags: [scitex-template-env-vars, scitex-template, scitex-package]
---

# Environment variables

## `SCITEX_DIR`

Overrides the ecosystem's local-state root. Default: `~/.scitex/`.

When set, scitex-template reads/writes its cache at
`$SCITEX_DIR/template/cache/` instead of `~/.scitex/template/cache/`.

Matches general/01_arch_06_local-state-directories.

```bash
export SCITEX_DIR=/fast/ssd/scitex-state
scitex-template clone research ./my-proj   # cache now at /fast/ssd/scitex-state/template/cache/
```

## No other env vars

Per general/01_arch_04, packages read only `SCITEX_<MODULE>_*` or
`SCITEX_DIR`. scitex-template currently has no
`SCITEX_TEMPLATE_*` variables; add them here when they appear.
