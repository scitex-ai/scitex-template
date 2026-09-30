---
name: scitex-research-template
description: Create and maintain a generic SciTeX research repository with current standalone packages, hidden package resources, measured results, and manuscript integration.
---

# SciTeX research template

Use [the project README](../README.md) and [CLAUDE.md](../CLAUDE.md) for
the supported commands. Verify commands against installed package help
and source before changing them.

- Keep shared resources under `<project>/.scitex/<package>/`; user resources
  belong under `~/.scitex/<package>/`.
- Use `scitex_session.session`, `scitex_io.load/save`, and public standalone
  package APIs. The umbrella package can pin older implementations.
- Use `requirements-develop.txt` for upstream implementations and record
  resolved commits before reporting research results.
- Leave measured data and researcher-defined Sources and Claims intact.
  Missing results must fail; never fabricate metrics to pass verification.
- `.scitex/<package>/runtime/` contains regenerable files, not SQLite stores.
  Managed PostgreSQL state and Cloud user authorization belong to deployment
  configuration. Never give a project a fleet administrator credential.
- A claims schema check establishes file shape only. Verify lineage and
  hashes separately using the actual configured Clew store.

See [quick start](scitex-research-template/01_quick-start.md),
[layout](scitex-research-template/02_structure.md), and
[scripts](scitex-research-template/11_writing-scripts.md).
