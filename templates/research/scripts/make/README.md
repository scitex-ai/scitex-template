# `scripts/make/` — verb-form shell scripts powering every `make <target>`

This directory is the **source of truth** for what each `make` target
actually does. The top-level [`Makefile`](../../Makefile) is intentionally a
thin layer of wrappers; each target's body lives in a single shell script
named `<verb>_<noun>.sh` in this directory.

## Why split this way

- **Discoverability.** A new contributor opens `scripts/make/` and sees, in
  one glance, every operation the template supports. No Makefile syntax to
  parse, no `$(VAR)` indirection, no recipe-vs-shell subtlety.
- **Direct invocation.** Every script runs standalone:
  ```bash
  ./scripts/make/run_mnist.sh    # equivalent to `make run-mnist`
  ./scripts/make/clean.sh        # equivalent to `make clean`
  ./scripts/make/format.sh       # equivalent to `make format`
  ```
  Useful in CI, in pre-commit hooks, when debugging a single step, or when
  you simply prefer shell to make.
- **Extensibility.** Adding a new example pipeline (say, `cifar`) is one
  `.sh` file under `scripts/make/run_cifar.sh` plus a four-line wrapper in
  the Makefile. No deeper refactor.
- **Verb-form naming.** Each filename starts with the verb (`run_…`,
  `clean_…`, `format_…`, `test_…`, `verify_…`, `setup_…`, `install_…`,
  `show_…`). Scripts are *things you do*, not nouns.

## Naming convention — verb_noun.sh, mandatory

Every script in this directory **must** be named `<verb>_<noun>.sh`. The
verb comes first because a script is *an action*; the noun specifies *what
the action operates on*. We do not use noun-led or noun-only names
(`mnist.sh`, `outputs.sh`) — those describe a *thing*, not an *action*,
and quickly become ambiguous as the set of operations grows ("does
`mnist.sh` run it? clean it? both?").

### Allowed verbs (current set)

| Verb | Used when the script… | Examples |
| --- | --- | --- |
| `run_` | executes a pipeline or stage that produces artefacts | `run_all.sh`, `run_mnist.sh`, `run_mnist_clf_svm.sh` |
| `clean_` | removes generated state (outputs, caches, logs) | `clean_all.sh`, `clean_outputs.sh`, `clean_clew.sh` |
| `format_` | rewrites source files in place (lint-fix tier) | `format_python.sh`, `format_shell.sh` |
| `lint_` | reports issues without modifying source | `lint_python.sh` |
| `test_` | runs the test suite or a slice of it | `test.sh`, `test_verbose.sh`, `test_sync.sh` |
| `verify_` | reproducibility checks (clew, claims, schemas) | `verify.sh`, `verify_claims.sh` |
| `install_` | resolves and installs runtime / dev dependencies | `install.sh`, `install_dev.sh` |
| `setup_` | one-shot bootstrap (install + dirs + config) | `setup.sh`, `setup_writer.sh` |
| `show_` | print read-only information to stdout | `show_config.sh` |
| `check_` | umbrella verbs that chain other actions | `check.sh` (= format + lint + test) |
| `tree_` / `info_` | one-screen project snapshots | `tree.sh`, `info.sh` |

If your new script doesn't fit one of these verbs, prefer adopting an
existing verb over inventing a new one — when in doubt, ask in the PR.
Invent a new verb only when the existing set genuinely cannot express the
action (and document it back into this table in the same PR).

### Bare verb is fine when there's no scope

A `<verb>.sh` (no `_<noun>` suffix) is the **umbrella** form — the script
that does the verb across every relevant target. So:

- `clean.sh` is the umbrella for `clean_outputs.sh` + `clean_data.sh` + ….
- `format.sh` is the umbrella for `format_python.sh` + `format_shell.sh`.
- `run_all.sh` is the umbrella for every `run_<example>.sh`.

The asymmetry (`clean.sh` is umbrella, `run_all.sh` is umbrella but uses
`run_all` not bare `run`) is because `run` alone is ambiguous when more
than one pipeline exists — `run_all` is explicit.

### Why this matters for `make`

Because the Makefile is generated mechanically from this directory, every
filename here must correspond to a valid `make` target (`run-mnist`,
`clean-outputs`, etc.) via snake_case → kebab-case translation. Adding a
`mnist.sh` would force a `make mnist` target, which is non-verbal and
collides badly with future `clean_mnist`, `run_mnist`, `verify_mnist`.

## Dual-invocation contract

For every public target `X` declared in the [`Makefile`](../../Makefile),
both invocations are equivalent:

```bash
make X                               # via Makefile wrapper
./scripts/make/<verb>_<noun>.sh      # direct
```

Where `<verb>_<noun>` is the snake_case form of `X` (e.g. `run-mnist` →
`run_mnist.sh`, `clean-outputs` → `clean_outputs.sh`).

## Inventory

### Run the examples
- [`run_all.sh`](run_all.sh) — umbrella; runs every example end-to-end.
  Today this just delegates to `run_mnist.sh`; when more examples land,
  chain them here.
- [`run_mnist.sh`](run_mnist.sh) — full MNIST pipeline, stages 01–06
  (download → plot-digits → plot-umap → SVM → conf-mat → register-claims).
- Per-stage entry points (useful when iterating on a single step):
  - [`run_mnist_download.sh`](run_mnist_download.sh) — stage 01.
  - [`run_mnist_plot_digits.sh`](run_mnist_plot_digits.sh) — stage 02.
  - [`run_mnist_plot_umap.sh`](run_mnist_plot_umap.sh) — stage 03.
  - [`run_mnist_clf_svm.sh`](run_mnist_clf_svm.sh) — stage 04.
  - [`run_mnist_conf_mat.sh`](run_mnist_conf_mat.sh) — stage 05.
  - [`run_mnist_register_claims.sh`](run_mnist_register_claims.sh) — stage 06
    (clew DAG terminus; emits `data/results/claims.json` + the clew DAG HTML).

### Reproducibility
- [`verify_claims.sh`](verify_claims.sh) — verify the clew DAG over the
  registered claims (used as a CI gate).
- [`verify.sh`](verify.sh) — alias / wrapper kept for compatibility.

### Setup & dependencies
- [`install.sh`](install.sh) — install runtime dependencies.
- [`install_dev.sh`](install_dev.sh) — install runtime + development extras.
- [`setup.sh`](setup.sh) — one-shot bootstrap (install + dirs + config).
- [`setup_writer.sh`](setup_writer.sh) — opt-in scitex-writer setup
  (delegates to the per-project `management/scripts/setup-writer.sh` if
  present; otherwise prints guidance).

### Cleanup
- [`clean.sh`](clean.sh) — sane default umbrella (outputs + intermediates).
- [`clean_outputs.sh`](clean_outputs.sh) — script `*_out/` artefacts.
- [`clean_data.sh`](clean_data.sh) — generated `data/` content (raw inputs
  are not touched by default — see the script).
- [`clean_logs.sh`](clean_logs.sh) — `*.log` files under `scripts/` and
  `tests/`.
- [`clean_mnist.sh`](clean_mnist.sh) — MNIST-only cleanup (handy when
  re-running just one example).
- [`clean_clew.sh`](clean_clew.sh) — remove the clew DB
  (`.scitex/clew/runtime/db.sqlite`, plus the legacy
  `.scitex/clew/db.sqlite` path) so the next run starts from a fresh DAG.
- [`clean_python.sh`](clean_python.sh) — `__pycache__/`, `*.pyc`, `.pytest_cache/`.
- [`clean_writer.sh`](clean_writer.sh) — remove the writer artefacts dir
  if present.
- [`clean_all.sh`](clean_all.sh) — combine the above (nuke-and-rebuild).

### Formatting & lint
- [`format.sh`](format.sh) — run every formatter (Python + shell).
- [`format_python.sh`](format_python.sh) — `ruff format`.
- [`format_shell.sh`](format_shell.sh) — `shfmt` on `scripts/`.
- [`lint.sh`](lint.sh) — run every linter.
- [`lint_python.sh`](lint_python.sh) — `ruff check`.
- [`check.sh`](check.sh) — `format` + `lint` + `test`.

### Tests
- [`test.sh`](test.sh) — run the pytest suite.
- [`test_verbose.sh`](test_verbose.sh) — verbose output.
- [`test_sync.sh`](test_sync.sh) — sync `tests/scripts/` against `scripts/`.

### Project info
- [`info.sh`](info.sh) — print a one-screen project status (counts, sizes).
- [`tree.sh`](tree.sh) — print the project tree (ignores common noise).
- [`show_config.sh`](show_config.sh) — show the resolved `CONFIG` (via
  `@stx.session`) for an interactive session.

## Conventions every script in this directory follows

All scripts share the same prologue:

```bash
#!/usr/bin/env bash
# Timestamp: "<YYYY-MM-DD> (proj-scitex-dev)"
# File: ./scripts/make/<verb>_<noun>.sh
#
# <one-line purpose>

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

# <body>
```

Key points:

- **`set -euo pipefail`** — fail fast on errors, undefined variables, and
  broken pipes. If the original Makefile target swallowed errors (e.g. with
  `|| true`), the equivalent `.sh` preserves that with the same suffix.
- **`ROOT_DIR` anchor** — every script `cd`s to `templates/research/` (the
  project root) regardless of the caller's `$PWD`. So both
  `make run-mnist` (invoked from `templates/research/`) and
  `cd /anywhere && /path/to/scripts/make/run_mnist.sh` produce the same
  result.
- **No hidden state** — scripts are idempotent unless explicitly noted
  (e.g. `clean_clew.sh` is destructive by design).

## Adding a new example

Say you want to add a `cifar` example pipeline:

1. Drop pipeline scripts under `scripts/cifar/0X_<step>.py` (mirrors the
   MNIST convention).
2. Create `scripts/make/run_cifar.sh` (mirror `run_mnist.sh`).
3. Add a wrapper to [`Makefile`](../../Makefile):
   ```makefile
   run-cifar:
   	@./scripts/make/run_cifar.sh
   ```
4. Add `run-cifar` to `.PHONY` and to the `help` target's text.
5. Extend `run_all.sh` to chain `run_cifar.sh` after `run_mnist.sh`.

That's it. No restructuring needed; the `scripts/make/` directory absorbs
new examples gracefully.

## See also

- [`../mnist/`](../mnist/) — the actual MNIST pipeline scripts that
  `run_mnist*.sh` invoke.
- [`../../Makefile`](../../Makefile) — the thin wrappers that delegate to
  this directory.
- The `scitexification` skill series (under
  `scitex-dev/_skills/scientific/06_scitexification/`) — guidance on
  translating existing code into the SciTeX idiom this template embodies.
