# Project structure

Keep analysis in `scripts/`, parameters in `config/`, inputs and stable output
links in `data/`, and tests in `tests/`. Read the project's README for its
actual pipeline rather than copying results or contracts from an example.

Package-owned project configuration lives in `.scitex/<package>/`; user
configuration lives in `~/.scitex/<package>/`. Writer creates its manuscript
workspace under `.scitex/writer/` only when requested with `make setup-writer`.

Commit configuration and research sources. Ignore generated `runtime/`
contents while retaining `.gitkeep` and `README.md`. Managed state is in
PostgreSQL on port 55432 through `scitex_dev.store`; a local file or directory
must not be used as a substitute store. Cloud deployment owns identity and
per-user read/write grants; the template never provisions them.

Use `config/PATH.yaml` for research data paths and the package's supported
resolver for package state. Do not hardcode a database path into PATH.yaml.
