"""Populate ``~/.scitex/template/cache/`` with a shallow clone of
``ywatanabe1989/scitex-template`` so the vendored ``templates/`` subtree is
available locally.

Wheel-installed users don't have ``templates/`` on disk (it's intentionally
excluded from the wheel to keep the download tiny). The first cloner call
triggers ``ensure_cache()`` which populates the cache; subsequent calls
refresh it to the branch tip. A failed refresh is an error, never a silent
fallback to the stale checkout; ``offline=True`` opts into the cache as-is.

Directory names follow general/01_arch_06: ``<pkg-short>`` = ``template``
(``scitex-`` prefix stripped; singular, not plural).
"""

from __future__ import annotations

import shutil
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path
from scitex_config._ecosystem import local_state

MONOREPO_URL = "https://github.com/ywatanabe1989/scitex-template.git"
CACHE_ROOT = local_state.runtime_path("template", "cache")


class CacheRefreshError(RuntimeError):
    """The template cache exists but could not be brought up to date.

    Raised instead of silently serving the stale checkout (issue #81). The
    message names the cached commit, its date and age, and how to opt into
    using it offline.
    """


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def _cached_commit(cache_root: Path) -> str:
    """``<short sha> (<ISO date>, <N> days old)`` for the cache HEAD."""
    result = _git("-C", str(cache_root), "log", "-1", "--format=%h %ct")
    parts = result.stdout.split() if result.returncode == 0 else []
    if len(parts) != 2:
        return "an unknown commit"
    sha, epoch = parts[0], int(parts[1])
    when = datetime.fromtimestamp(epoch, tz=timezone.utc)
    age = (datetime.now(timezone.utc) - when).days
    return f"{sha} ({when.date().isoformat()}, {age} days old)"


def _refresh(cache_root: Path, branch: str) -> None:
    """Move an existing cache to the tip of ``branch``; raise on any failure.

    ``fetch --depth 1`` + ``reset --hard FETCH_HEAD`` works on a shallow
    clone and also switches branches; every return code is checked.
    """
    steps = (
        ("fetch", "--depth", "1", MONOREPO_URL, branch),
        ("reset", "--hard", "FETCH_HEAD"),
        ("clean", "-ffdx"),
    )
    for step in steps:
        result = _git("-C", str(cache_root), *step)
        if result.returncode != 0:
            raise CacheRefreshError(
                f"could not refresh the scitex-template cache at {cache_root} "
                f"(git {step[0]} failed: {result.stderr.strip() or 'no output'}). "
                f"The cache holds {_cached_commit(cache_root)}, which may be "
                f"stale, so it was NOT used. Fix the network/remote and retry, "
                f"or pass --offline (offline=True) to use the cached copy as-is."
            )


def ensure_cache(
    branch: str = "main", force_refresh: bool = False, offline: bool = False
) -> Path:
    """Ensure the scitex-template monorepo is shallow-cloned at ``CACHE_ROOT``.

    Returns the cache root. An existing cache is refreshed to the tip of
    ``branch``; a refresh failure raises :class:`CacheRefreshError` rather
    than serving the possibly stale checkout. ``offline=True`` is the
    explicit opt-in to use an existing cache without contacting the remote
    (a warning names the cached commit and its age). A missing cache, or a
    failed first clone, raises ``RuntimeError``. Pass ``force_refresh=True``
    to wipe and re-clone.
    """
    if offline:
        if force_refresh:
            raise ValueError("offline=True cannot be combined with force_refresh=True")
        if not (CACHE_ROOT / ".git").is_dir():
            raise RuntimeError(
                f"offline mode requested but no scitex-template cache exists at "
                f"{CACHE_ROOT}; run once with network access first."
            )
        warnings.warn(
            f"offline: using the scitex-template cache at {CACHE_ROOT} without "
            f"refreshing it; it holds {_cached_commit(CACHE_ROOT)}.",
            stacklevel=2,
        )
        return CACHE_ROOT

    CACHE_ROOT.parent.mkdir(parents=True, exist_ok=True)

    if force_refresh and CACHE_ROOT.exists():
        shutil.rmtree(CACHE_ROOT)

    if (CACHE_ROOT / ".git").is_dir():
        _refresh(CACHE_ROOT, branch)
        return CACHE_ROOT

    if CACHE_ROOT.exists():
        shutil.rmtree(CACHE_ROOT)
    result = _git(
        "clone", "--depth", "1", "--branch", branch, MONOREPO_URL, str(CACHE_ROOT)
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"failed to shallow-clone {MONOREPO_URL} into {CACHE_ROOT}: "
            f"{result.stderr.strip()}"
        )
    return CACHE_ROOT


def clone_template_from_cache(
    template_id: str,
    target: str | Path,
    branch: str = "main",
    force_refresh: bool = False,
    offline: bool = False,
) -> Path:
    """Populate ``target`` with the contents of ``templates/<template_id>/``.

    Ensures the cache is present/fresh, then copies the subdir via ``cp -r``
    semantics (no symlinks, no .git pollution). Returns the populated target.

    ``offline=True`` uses the existing cache without refreshing it (see
    :func:`ensure_cache`); otherwise a failed refresh raises
    :class:`CacheRefreshError` instead of copying from a stale cache.

    Raises:
        CacheRefreshError: if the cache cannot be refreshed (not offline).
        KeyError: if ``template_id`` is not in the registry.
        FileExistsError: if ``target`` exists and is non-empty.
    """
    from .registry import find_template

    cache_root = ensure_cache(
        branch=branch, force_refresh=force_refresh, offline=offline
    )

    # Refresh the registry from the cache view (not the editable checkout)
    # by importing against cache_root.
    entry = find_template(template_id)
    if entry is None:
        raise KeyError(
            f"template {template_id!r} is not in the registry. "
            f"Available: see scitex_template.registry.load_registry()"
        )

    target_path = Path(target)
    if target_path.exists() and any(target_path.iterdir()):
        raise FileExistsError(f"target {target_path} already exists and is not empty")
    target_path.mkdir(parents=True, exist_ok=True)

    # entry.path resolves against registry_root(). If the editable checkout
    # exists, it wins; otherwise it resolves to CACHE_ROOT/templates/<id>/.
    source = entry.path
    if not source.exists():
        # Registry resolved to editable checkout but that's not the cache.
        # Fall back to cache explicitly.
        source = cache_root / "templates" / template_id

    for child in source.iterdir():
        dst = target_path / child.name
        if child.is_dir() and not child.is_symlink():
            # symlinks=True preserves intra-template symlinks; dangling
            # ones are skipped so a broken link in source doesn't blow up
            # the whole clone.
            shutil.copytree(child, dst, symlinks=True, ignore_dangling_symlinks=True)
        elif child.is_symlink():
            # Recreate the symlink at dst; ok if target doesn't exist yet
            # (e.g. forward reference resolved later in the loop).
            link_target = (
                child.readlink()
                if hasattr(child, "readlink")
                else Path(str(child).join(""))
            )
            dst.symlink_to(link_target)
        else:
            shutil.copy2(child, dst, follow_symlinks=False)

    _write_manifest(target_path, entry, branch=branch, cache_root=cache_root)

    return target_path


def _cache_commit_sha(cache_root: Path) -> str:
    """Best-effort HEAD sha of the cache checkout. ``"unknown"`` if the
    cache is not a git repo (e.g. a test fixture) or git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(cache_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
    except (OSError, ValueError):
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _generator_version() -> str:
    """Installed scitex-template version, or ``"unknown"`` if not resolvable."""
    try:
        from importlib.metadata import version

        return version("scitex-template")
    except Exception:
        return "unknown"


def _write_manifest(target_path: Path, entry, *, branch: str, cache_root: Path) -> Path:
    """Stamp a provenance manifest into the prepared template so a consumer
    can later tell exactly what was pulled and pin it for reproducibility.

    Lives at ``<target>/.scitex/template/MANIFEST.yaml`` — the template
    tool's own ``.scitex/`` home, matching the config-resolution convention.
    """
    import yaml

    manifest = {
        "schema": "scitex-template/manifest@v1",
        "template": {
            "id": entry.id,
            "version": entry.version,
            "description": entry.description,
        },
        "source": {
            "monorepo": MONOREPO_URL,
            "branch": branch,
            "commit": _cache_commit_sha(cache_root),
        },
        "generator": {
            "scitex_template_version": _generator_version(),
        },
        "prepared_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    }

    manifest_dir = target_path / ".scitex" / "template"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "MANIFEST.yaml"
    manifest_path.write_text(
        "# scitex-template provenance — written at clone time. Do not edit by hand.\n"
        + yaml.safe_dump(manifest, sort_keys=False)
    )
    return manifest_path
