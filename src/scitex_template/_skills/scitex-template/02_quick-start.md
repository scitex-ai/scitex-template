---
description: |
  [TOPIC] Quick Start
  [DETAILS] Minute-long introduction to scitex-template — install, list the 6 templates, clone one. Points at the other skills for details.
tags: [scitex-template-quick-start, scitex-template, scitex-package]
---

# Quick start

```bash
pip install scitex-template

# See what's available
scitex-template list-templates

# Clone one
scitex-template clone research ./my-experiment
cd my-experiment
```

That's it. The first `clone` triggers a one-time shallow-clone of the
scitex-template monorepo into `~/.scitex/template/cache/` (~23 MB); every
subsequent clone copies from that local cache.

## Python API equivalent

```python
from scitex_template import clone_template_from_cache, load_registry

clone_template_from_cache("research", "./my-experiment")

for entry in load_registry():
    print(entry.id, entry.version, entry.description)
```

## Next

- [03_python-api.md](03_python-api.md) — Full Python surface
- [04_cli-reference.md](04_cli-reference.md) — Every CLI subcommand + flag
- [05_mcp-tools.md](05_mcp-tools.md) — Agent integration
- [10_project-templates.md](10_project-templates.md) — Per-template details
- [11_code-templates.md](11_code-templates.md) — Ready-to-use scitex code snippets
