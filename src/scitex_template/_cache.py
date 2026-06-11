"""Populate ``~/.scitex/template/cache/`` with a shallow clone of
``ywatanabe1989/scitex-template`` so the vendored ``templates/`` subtree is
available locally.

Wheel-installed users don't have ``templates/`` on disk (it's intentionally
excluded from the wheel to keep the download tiny). The first cloner call
triggers ``ensure_cache()`` which populates the cache; subsequent calls
``git pull`` to stay current.

Directory names follow general/01_arch_06: ``<pkg-short>`` = ``template``
(``scitex-`` prefix stripped; singular, not plural).
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from scitex_config._ecosystem import local_state

MONOREPO_URL = "https://github.com/ywatanabe1989/scitex-template.git"
CACHE_ROOT = local_state.runtime_path("template", "cache")


def ensure_cache(branch: str = "main", force_refresh: bool = False) -> Path:
    """Ensure the scitex-template monorepo is shallow-cloned at ``CACHE_ROOT``.

    Returns the cache root. Raises ``RuntimeError`` on clone/pull failure.

    Idempotent: subsequent calls ``git pull`` the existing checkout rather
    than re-cloning. Pass ``force_refresh=True`` to wipe and re-clone.
    """
    CACHE_ROOT.parent.mkdir(parents=True, exist_ok=True)

    if force_refresh and CACHE_ROOT.exists():
        shutil.rmtree(CACHE_ROOT)

    if not (CACHE_ROOT / ".git").is_dir():
        CACHE_ROOT.parent.mkdir(parents=True, exist_ok=True)
        if CACHE_ROOT.exists():
            shutil.rmtree(CACHE_ROOT)
        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                branch,
                MONOREPO_URL,
                str(CACHE_ROOT),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"failed to shallow-clone {MONOREPO_URL} into {CACHE_ROOT}: "
                f"{result.stderr.strip()}"
            )
    else:
        result = subprocess.run(
            ["git", "-C", str(CACHE_ROOT), "pull", "--ff-only", "--depth", "1"],
            capture_output=True,
            text=True,
        )
        # pull can fail if the remote rebased; treat as non-fatal and keep
        # existing cache so offline workflows still proceed
        if result.returncode != 0:
            # Try a deeper fetch + reset to recover
            subprocess.run(
                ["git", "-C", str(CACHE_ROOT), "fetch", "origin", branch],
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(CACHE_ROOT), "reset", "--hard", f"origin/{branch}"],
                capture_output=True,
                text=True,
            )

    return CACHE_ROOT


def clone_template_from_cache(
    template_id: str,
    target: str | Path,
    branch: str = "main",
    force_refresh: bool = False,
) -> Path:
    """Populate ``target`` with the contents of ``templates/<template_id>/``.

    Ensures the cache is present/fresh, then copies the subdir via ``cp -r``
    semantics (no symlinks, no .git pollution). Returns the populated target.

    Raises:
        KeyError: if ``template_id`` is not in the registry.
        FileExistsError: if ``target`` exists and is non-empty.
    """
    from .registry import find_template

    cache_root = ensure_cache(branch=branch, force_refresh=force_refresh)

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
