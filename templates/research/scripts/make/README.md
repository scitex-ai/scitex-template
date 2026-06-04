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
