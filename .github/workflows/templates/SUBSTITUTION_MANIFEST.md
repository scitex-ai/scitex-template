# CI Template Substitution Manifest

Source of truth: `scitex-template/.github/workflows/templates/`.

These templates are the canonicalized form of the CI-speedup pilot
applied to `scitex-sh` (PR #11 — `chore(ci): apply L1-L5 speedup
pattern (pilot)`). They are derived **verbatim** from scitex-sh's
post-merge state of `.github/workflows/pr-ci.yml` and
`.github/workflows/release-ci.yml`, with package-specific tokens
replaced by named placeholders.

## Placeholders

| placeholder | example | derivation rule |
|---|---|---|
| `<PKG_NAME>` | `scitex-io` | pyproject `[project].name` verbatim |
| `<PKG_MODULE>` | `scitex_io` | `[project].name` with `-` → `_` |
| `<PYTHON_VERSIONS_JSON>` | `["3.11","3.12","3.13"]` | default fleet matrix; constrain per `[project].requires-python` |
| `<CLI_HELP_BLOCK>` | `- run: PATH=.venv/bin:$PATH scitex-io --help` (× per entrypoint) | one line per `[project.scripts]` key; if no scripts, omit the entire `cli-help` step (these templates currently do not emit a `cli-help` step — the placeholder is reserved for future use) |

### `<PYTHON_VERSIONS_JSON>` literal form

In `pr-ci.yml.tmpl` the placeholder appears inside a `fromJson('…')`
expression, so the substituted value must be a JSON-string literal
suitable for `fromJson` (e.g. `["3.11","3.12","3.13"]`).

In `release-ci.yml.tmpl` the placeholder appears as a YAML sequence
value, so the substituted value must be valid YAML/JSON list syntax
(`["3.11", "3.12", "3.13"]`).

## Jobs emitted by `pr-ci.yml.tmpl`

The following job-IDs and step-`name`s are produced after
substitution. The `name:` strings shown below are the values that
appear as required-status-check contexts in GitHub branch
protection.

- `import-smoke` (job-id) → check name **`import-smoke`**
- `dep-hygiene-smoke` (job-id) → check name **`dep-hygiene-smoke`**
- `tests` (job-id, matrix) → check names
  **`pytest-matrix-on-ubuntu-py3.11`**,
  **`pytest-matrix-on-ubuntu-py3.12`**,
  **`pytest-matrix-on-ubuntu-py3.13`**
  (one per entry in `<PYTHON_VERSIONS_JSON>`)
- `quality` (job-id) → check name **`quality`**

## Jobs emitted by `release-ci.yml.tmpl`

- `tests` (job-id, matrix) → check names
  **`pytest-matrix-on-ubuntu-py3.11`**,
  **`pytest-matrix-on-ubuntu-py3.12`**,
  **`pytest-matrix-on-ubuntu-py3.13`**
- `import-smoke` (job-id) → check name **`import-smoke`**
- `quality` (job-id) → check name **`quality`**

## Branch-protection compatibility rule

Before scitex-dev CLI applies these templates to a target repo, it
**MUST** verify that the repo's `required_status_checks` contexts are
a **SUBSET** of the names listed above (after substitution). If a
required context is missing, the apply **STOPS** — the operator must
either rename the required context or extend the template.

## L5a / L5b fix-forward note

The pilot brief references two fix-forward lessons:

- **L5a**: `uv venv .venv` + `uv pip install --python .venv/bin/python …`
  (instead of `--system`).
- **L5b**: any test step that calls a console-script via subprocess
  prefixes `PATH=.venv/bin:$PATH` (or uses a job-level `env:` block).

The current `scitex-sh` post-merge state (the source of truth) uses
`uv pip install --system` with `actions/setup-python@v5`, which
provides a non-externally-managed Python so `--system` is safe and
no `.venv` is required. These templates inherit that working pattern
verbatim. If a future fix-forward switches `scitex-sh` to
`.venv`-based installs, re-canonicalize from that state and update
this manifest.

## How to apply (manual procedure, until CLI lands)

1. Detect `<PKG_NAME>` and `<PKG_MODULE>` from `pyproject.toml`.
2. Detect `<PYTHON_VERSIONS_JSON>` from `pyproject.requires-python`
   (default `["3.11","3.12","3.13"]`).
3. Detect `<CLI_HELP_BLOCK>` from `pyproject.scripts` (currently
   reserved for future use — see Placeholders).
4. `sed`-substitute into a copy of each `.tmpl`.
5. Drop into target repo's `.github/workflows/pr-ci.yml` and
   `.github/workflows/release-ci.yml`.
6. **DELETE** consolidated standalone workflows that were folded in:
   `import-smoke-*.yml`, `pytest-matrix-*.yml`,
   `dep-hygiene-smoke.yml`, audit/quality workflows.
7. **KEEP**: `cla.yml`, `pypi-publish*.yml`,
   `auto-merge-to-develop.yaml`, `rtd-sphinx-*` (or fold rtd into
   `release-ci`, per-repo discretion).
8. Open PR `chore/ci-speedup`. CI-green self-merge.
