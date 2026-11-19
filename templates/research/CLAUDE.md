# SciTeX Research Project

Scientific research project using the SciTeX framework for reproducible experiment tracking,
automated data management, and manuscript writing.

## Key Conventions

- Every analysis script is a `@scitex_session.session`-decorated `main` (`import scitex_session as sess`)
- All file I/O through `scitex_io` (`sio.load` / `sio.save(..., symlink_from_cwd=True)`) so clew records it
- Parameters in `config/*.yaml` (read via `CONFIG`), paths in `config/PATH.yaml`; no numbers in scripts (STX-S008)
- Scripts go in `scripts/<topic>/` as `NN_<verb>_<object>.py` in execution order
- Outputs land in `<script>_out/` and are linked into `data/`
- Every number reported in the manuscript is a registered claim (`config/CLAIMS.yaml` + `\vclaim{id}`)
- `make verify` (`clew verify --strict`) must pass before a result is called done
- The MNIST showcase (`make all`, `make live-paper`) is the worked example; see README.md

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
- Every script must be reproducible via `@scitex_session.session` with seeds from `config/`.
