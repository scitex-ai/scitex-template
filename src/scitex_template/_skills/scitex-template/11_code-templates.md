---
description: |
  [TOPIC] Code Templates
  [DETAILS] Retrieve ready-to-use Python code snippets for @stx.session scripts, I/O, config, modules, and each major stx module (plt, stats, scholar, etc.).
tags: [scitex-template-code-templates, scitex-template, scitex-package]
---

# Code Templates

`CODE_TEMPLATES` is a registry of 14 ready-to-use Python (and YAML) code
snippets. Each template has a string `content` with `{timestamp}`,
`{filepath}`, `{filename}`, `{filename_stem}`, and `{docstring}` format
placeholders that are filled in at retrieval time.

## Listing Available Templates

```python
import scitex

templates = scitex.template.list_code_templates()
# Returns list of dicts: id, name, description, filename, usage
for t in templates:
    print(f"{t['id']:20s}  {t['description']}")
```

The 14 IDs:

| group     | IDs                                                        |
|-----------|------------------------------------------------------------|
| session   | session, session-minimal, session-plot, session-stats     |
| storage   | io, config                                                 |
| module    | module                                                     |
| stx-modules | plt, stats, scholar, audio, capture, diagram, canvas, writer |

## Retrieving a Single Template

```python
def get_code_template(
    template_id: str,
    filepath: Optional[str] = None,
    docstring: Optional[str] = None,
) -> str
```

- `template_id`: one of the IDs listed above
- `filepath`: inserted into the file header comment (defaults to template's own `filename`)
- `docstring`: replaces the default `"Description of this script/module"`
- Raises `ValueError` if `template_id` is unknown

```python
# Minimal session — paste into a new .py file
code = scitex.template.get_code_template("session-minimal")

# Full session with custom path and docstring
code = scitex.template.get_code_template(
    "session",
    filepath="./scripts/analysis.py",
    docstring="Run primary analysis pipeline.",
)
print(code)
```

## Getting All Templates at Once

```python
all_code = scitex.template.get_all_templates()
# Returns one string: header + each template's usage note + fenced code block
```

Priority order: `session`, `io`, `config`, `session-minimal`,
`session-plot`, `session-stats`, `module`, `plt`, `stats`, `scholar`,
`audio`, `capture`, `diagram`, `canvas`, `writer`.

## Quick Reference: which template injects what

| template          | injects                                         |
|-------------------|-------------------------------------------------|
| session           | CONFIG, plt, COLORS, rng, logger                |
| session-minimal   | CONFIG, logger                                  |
| session-plot      | CONFIG, plt, logger (+ savefig with CSV export) |
| session-stats     | CONFIG, logger (+ stats helpers)                |

Key injected paths every session-style template exposes:
- `CONFIG.SDIR_OUT` — output root (pass to `scitex.io.save`)
- `CONFIG.SDIR_RUN` — session run dir (logs, config snapshots)
- `CONFIG.ID` — session ID string like `2025Y-01M-20D-10h30m00s_XyZ1`

## Module-specific snippets

The `plt`, `stats`, `scholar`, `audio`, `capture`, `diagram`, `canvas`,
and `writer` templates each demonstrate the canonical first-call pattern
for that subpackage — the snippet you'd paste into a fresh script to get
a quick win without reading docs.

For the actual snippet bodies, read the source:
`src/scitex_template/_code/code_templates.py`. Single source of truth so
this doc doesn't drift when the snippets evolve.
