---
description: |
  [TOPIC] Environment Variables
  [DETAILS] SCITEX_DIR resource settings and the shared SCITEX_LOGGING_*
  output settings read by scitex-template.
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

## Shared logging settings

`SCITEX_LOGGING_LEVEL`, `SCITEX_LOGGING_FORMAT`, and
`SCITEX_LOGGING_FORCE_COLOR` configure the shared logger. Human CLI results
use stdout; status and failure diagnostics use stderr. JSON, MCP frames,
and shell completion output stay plain and independent of the human log
threshold. Configure the environment before importing logging.

## Package-specific env vars

Per general/01_arch_04, packages read only `SCITEX_<MODULE>_*` or
`SCITEX_DIR`. scitex-template currently has no
`SCITEX_TEMPLATE_*` variables; add them here when they appear.
