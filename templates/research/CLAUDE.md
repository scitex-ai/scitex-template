# SciTeX Research Project

This is a reusable template. Keep shared instructions generic; research
results and benchmark contracts belong to the project that consumes it.

- Analysis code lives in `scripts/`, parameters in `config/`, and data in `data/`.
- Use `scitex_session.session` and `scitex_io.load` / `scitex_io.save` to record
  execution and dependencies. Use FigRecipe for data/style-separated figures.
- Project package files belong in `<project-root>/.scitex/<package>/`;
  user package settings belong in `~/.scitex/<package>/`.
- Commit configuration and research sources. Ignore generated `runtime/`
  files, preserving `.gitkeep` and `README.md`.
- Managed database state uses `scitex_dev.store` (PostgreSQL on port 55432).
  Resolve it through the package's public API; a directory is not a DSN.
- Deployment owns provisioning and user ACLs. Cloud access must use an
  authenticated stable identity and fail closed for missing grants. Never
  copy an admin credential into a project or authorize a shared fleet store.
- Inspect current source and executable behavior when documentation differs.
  `requirements-develop.txt` selects current `scitex-ai` development sources;
  freeze validated commits before using them for a research measurement.
- Missing inputs or metrics must raise; never create substitute evidence.
- `make setup-writer` creates the optional `.scitex/writer/` workspace.
- `make clean-clew` removes a generated visualization, never the managed store.

Read [README.md](README.md) for the runnable workflow and
[.scitex/README.md](.scitex/README.md) for the storage boundary.
