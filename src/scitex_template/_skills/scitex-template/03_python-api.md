---
description: |
  [TOPIC] Python Api
  [DETAILS] Complete public Python API of scitex-template — the cache-based clone path (primary), the legacy per-template clone_* functions (still exported for back-compat), registry enumeration, code-snippet helpers, config generators.
tags: [scitex-template-python-api, scitex-template, scitex-package]
---

# Python API

## Primary path — cache-based

```python
from scitex_template import clone_template_from_cache, load_registry, find_template

# Enumerate
for e in load_registry():
    print(e.id, e.version, e.description, e.path)

# Look up one
find_template("research")   # TemplateEntry | None

# Populate a target
clone_template_from_cache("research", "./my-proj")        # raises on unknown id
clone_template_from_cache("paper", "./paper", branch="main", force_refresh=True)
```

## Legacy path — kept for back-compat

Top-level `clone_<name>` functions still exist and delegate through
`clone_project()`. Under the hood they now use the cache fast-path when
the template name is registered, falling back to per-template remote
clone only with `[legacy]` extra installed.

```python
from scitex_template import (
    clone_research,
    clone_pip_project,
    clone_scitex_minimal,
    clone_singularity,
    clone_module,
    clone_writer_directory,
)

clone_research("./my-proj")
clone_pip_project("./my-pip")
```

## Code snippets

```python
from scitex_template import (
    get_code_template,
    list_code_templates,
    get_all_templates,
    CODE_TEMPLATES,
)

for t in list_code_templates():
    print(f"{t['id']:20}  {t['description']}")

code = get_code_template("session", filepath="./scripts/analysis.py")
```

See [11_code-templates.md](11_code-templates.md) for the 14 snippet IDs.

## Config generators

```python
from scitex_template import (
    create_project_config, create_paths_config,
    create_env_template, create_requirements_file,
    create_minimal_readme, create_project_readme,
    build_directory_tree, PROJECT_STRUCTURE,
    customize_template, customize_minimal_template,
)
```

See [13_config-generators.md](13_config-generators.md).

## Scholar-Writer integration

```python
from scitex_template import setup_scholar_writer_integration, ensure_integration
```

See [14_scholar-writer-integration.md](14_scholar-writer-integration.md).

## Cache control

```python
from scitex_template._cache import ensure_cache, CACHE_ROOT, MONOREPO_URL

ensure_cache()                 # idempotent; pulls existing checkout
ensure_cache(force_refresh=True)  # wipe + re-clone
print(CACHE_ROOT)              # ~/.scitex/template/cache/
```

## Git helpers (optional — via `[legacy]` extra)

When `scitex-template[legacy]` is installed, these re-exports are real
functions; otherwise they raise `ImportError` when called.

```python
from scitex_template import init_git_repo, find_parent_git, create_child_git, remove_child_git
```
