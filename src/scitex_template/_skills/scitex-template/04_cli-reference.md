---
description: |
  [TOPIC] Cli Reference
  [DETAILS] Every scitex-template CLI subcommand — list-templates, show-info, clone, refresh-cache, version — with flags, exit codes, and output format.
tags: [scitex-template-cli-reference, scitex-template, scitex-package]
---

# CLI reference

Entry point: `scitex-template` (also `python -m scitex_template.cli`).

```
scitex-template [-h|--help] [-V|--version] COMMAND [ARGS...]
```

## `list-templates`

```
scitex-template list-templates [--json]
```

Enumerate registered templates.

- Human output: one line per template, columns `id  version  description`.
- `--json`: array of `{id, version, description, path}` objects.

Exit code: 0.

## `show-info <template_id>`

Show metadata for a single template.

```
scitex-template show-info research
```

Prints `id`, `version`, `description`, `path`.

Exit code: 1 on unknown id.

## `clone <template_id> <target>`

Populate `<target>` with the contents of `<template_id>` from the cache.

```
scitex-template clone pip-project ./my-pip
scitex-template clone research ./my-experiment --force-refresh
scitex-template clone paper ./paper --branch main
```

Flags:

| flag | default | meaning |
|---|---|---|
| `--branch` | `main` | Monorepo branch to track in the cache |
| `--force-refresh` | `false` | Wipe + re-clone cache before copying |

Exit codes: 0 success, 1 unknown id, 2 target exists and non-empty.

## `refresh-cache`

```
scitex-template refresh-cache [--branch main]
```

Force-refresh `~/.scitex/template/cache/` (wipes it, re-clones the
scitex-template monorepo shallowly).

Use when the monorepo has new templates you haven't seen, or to recover
from a diverged cache.

## `--version` / `-V`

```
scitex-template --version
scitex-template -V
```

Prints the installed package version. The bare `version` subcommand was
removed (per audit-cli §1b — banned bare leaf); use the `--version` flag
on the top level instead.

## Deprecated aliases

The following names exit non-zero with a redirect message and will be
removed in a future release:

| old | new |
|---|---|
| `list` | `list-templates` |
| `info` | `show-info` |
| `cache-refresh` | `refresh-cache` |

## Examples

```bash
# Start a new research project
scitex-template clone research ~/proj/my-eeg-study
cd ~/proj/my-eeg-study
bash scripts/mnist/main.sh      # regenerate the MNIST example outputs

# Scaffold a new scitex-* pip package
scitex-template clone minimal ~/proj/scitex-foo
cd ~/proj/scitex-foo
pip install -e .

# List everything, machine-readable
scitex-template list-templates --json | jq '.[] | .id'
```
