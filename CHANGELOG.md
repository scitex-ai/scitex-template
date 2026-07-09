# Changelog

All notable changes to `scitex-template` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project uses
[SemVer](https://semver.org/).

## [0.6.8] – 2026-07-08

### Fixed
- `clone_scitex_minimal`: import the scholar ensure callable explicitly
  (`from scitex_scholar.ensure_workspace import ensure_workspace`). The old
  `from scitex_scholar import ensure_workspace` bound the SUBMODULE (no
  released scitex-scholar 1.2.4/1.3.1/1.4.x re-exports the function at top
  level), so every clone raised `TypeError: 'module' object is not callable`
  and returned False — quarantining all visitor slots on scitex.ai
  prod+staging ("Template clone returned falsy").
- `clone_scitex_minimal`: failure path now logs with `logger.exception`
  (full traceback) instead of `logger.error(str(e))`, so downstream
  consumers (hub `quarantine_reason`) can see the real cause. The bool
  return contract is unchanged (TEMPLATES dispatcher + CLI exit code rely
  on it).

### Added
- `tests/scitex_template/_project/test_clone_scitex_minimal.py`: regression
  suite — asserts the imported ensure callables are functions
  (`inspect.isfunction`) and exercises the clone against hand-rolled fake
  modules mirroring the released scholar/writer package layout.

## [0.5.1] – 2026-04-25

### Fixed
- `_cache.py`: preserve intra-template symlinks when copying from the
  monorepo cache. Research template's `scitex/ai/prompts/{writer,scholar,code,vis}`
  and `.claude/commands/*.md` relative symlinks no longer crash the clone.
  `shutil.copytree(symlinks=True, ignore_dangling_symlinks=True)` for dirs;
  `dst.symlink_to(child.readlink())` for top-level links;
  `shutil.copy2(follow_symlinks=False)` for regular files.

## [0.5.0] – 2026-04-25

### Added
- `[legacy]` optional-dependency group for the scitex umbrella:
  `pip install scitex-template[legacy]` enables the remote-clone fallback
  that still imports `scitex.git` / `scitex.scholar` / `scitex.writer`.
- `_require_scitex_git()` helper raising a clear `ImportError` pointing at
  the legacy extra.

### Changed
- **`scitex` is no longer a hard runtime dependency** (general/01_arch_02
  downstream-dep rule). `dependencies = ["gitpython", "pyyaml"]` only.
  The cache fast-path for registered templates works with zero scitex.*
  imports.
- `from scitex.logging import getLogger` → stdlib `import logging;
  getLogger = logging.getLogger` across 13 files. `.success()` / `.fail()`
  shims installed on `logging.Logger` in `_logging_helpers.py` so existing
  `logger.success(...)` calls keep working.
- `scitex.config.get_scitex_dir` → inline `Path.home() / ".scitex"` with
  `SCITEX_DIR` env var honored (general/01_arch_06).
- `scitex.scholar.ensure_workspace` import guarded with `try/except`
  fallback to `SCHOLAR_SUBDIRS = ["bib_files", "library", "prompts"]`.

### Known issues
- `clone_research` standalone path requires the 0.5.1 symlink fix. Users on
  0.5.0 should upgrade or install with `[legacy]`.

## [0.4.0] – 2026-04-25

### Added
- `templates/paper/` vendored from the archived `paper-template` repo
  (996 KB — LaTeX manuscript scaffold).
- `_MONOREPO_REGISTRY_IDS["paper-template"] = "paper"` for the fast-path.

Consolidation now covers all 6 templates: pip-project, minimal, cloud-module,
research, singularity, paper.

## [0.3.0] – 2026-04-25

### Added
- Fast-path in `_clone_project.py`: when `template_name` maps to a registry
  id (`pip-project`, `minimal`, `cloud-module`, `research`, `singularity`,
  `paper`) and no branch/tag is requested, populate the target from
  `~/.scitex/template/cache/` instead of `git clone`-ing the per-template
  remote repo. Falls through to the legacy remote-clone flow otherwise.

## [0.2.0] – 2026-04-25

### Added
- **Vendoring** — 5 templates consolidated under `templates/`:
  - `pip-project/` (564 KB, from `pip-project-template`)
  - `minimal/` (4.4 MB, from `scitex-minimal-template`)
  - `cloud-module/` (88 KB, from `scitex-template-cloud-module`)
  - `singularity/` (8.1 MB, from `singularity_template`)
  - `research/` (8.3 MB, from `scitex-research-template` minimized — MNIST
    outputs and data excluded via `.gitignore`, regenerable via
    `scripts/mnist/main.sh`)
- `templates/REGISTRY.yaml` + per-template `template.yaml`.
- `scitex_template.registry` — `load_registry()`, `find_template(id)`.
- `scitex_template._cache` — `ensure_cache()` shallow-clones the monorepo
  into `~/.scitex/template/cache/`; `clone_template_from_cache(id, target)`
  copies a subtree from the cache into the user's target.

### Changed
- Hatch build config: `packages = ["src/scitex_template"]`. `templates/` is
  in git but intentionally NOT in the wheel — keeps the PyPI download
  ~100 KB while the git repo stays the single source of truth for template
  payload.

## [0.1.0] – 2026-04-25

### Added
- Initial extraction from `scitex.template` (lived inside `scitex-python`)
  into the standalone `scitex-template` PyPI package.
- `sys.modules` alias shim at `scitex-python/src/scitex/template/__init__.py`
  so every previous import path (including `scitex.template._mcp.handlers`,
  `scitex.template._project.*`) keeps resolving.
- scitex-python `pyproject.toml`: `template = ["scitex-template>=0.1.0"]`
  (general/01_arch_03 §12 compliant); console script relocated to
  `scitex_template.mcp_server:main`.

### Removed
- `tests/scitex/template/` from scitex-python (general/01_arch_03 §13 —
  dead tests at collection break CI).
- Dead `_code/`, `_project/`, `_mcp/`, `_skills/`, `_utils/` subtrees under
  `scitex-python/src/scitex/template/` (~7800 LoC, now living in this repo).
