# SciTeX Research Project

Scientific research project using the SciTeX framework for reproducible experiment tracking,
automated data management, and manuscript writing.

## Key Conventions

- Use `@stx.session(seed=42)` decorator for all experiment scripts
- Use `stx.io.save(data, path)` and `stx.io.load(path)` for all file I/O (30+ formats)
- Scripts go in `scripts/` with numbered prefixes: `01_preprocess.py`, `02_train.py`, etc.
- Script outputs land in `{script_name}_out/` and are symlinked to `data/` for centralized access
- Use `symlink_to` parameter in `stx.io.save()` to create data provenance links

## Directory Conventions

- `scripts/` -- main workspace for analysis code
- `config/` -- YAML configuration files
- `data/` -- centralized data access (symlinks from script outputs)
- `tests/` -- test suite (mirrors scripts/ structure)
- `scitex/` -- SciTeX-managed resources (writer, scholar, vis, code, ai)
- `management/` -- git-tracked project management (shared with team)
- `GITIGNORED/` -- untracked working files (local drafts, todos, scratch)
- `_skills/` -- DEPRECATED; use `.claude/skills/` instead

## Development

```bash
make check          # format + lint + test (run before committing)
make test           # run test suite only
make format         # format Python (ruff) + Shell (shfmt)
make lint           # lint with ruff
make install-dev    # install dev dependencies (pytest, ruff, etc.)
```

## CLI

```bash
scitex template get <id>       # get code template (session, io, all)
scitex template get session    # session script template
scitex template get io         # I/O operations template
```

## Rules

- No silent fallbacks. Errors must be visible, not hidden.
- No placeholder or stub implementations unless explicitly requested.
- Every script must be reproducible via `@stx.session(seed=42)`.
