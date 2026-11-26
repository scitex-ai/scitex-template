"""Tests for scitex_template._cache.

PA-306 no-mocks. The previous suite used ``monkeypatch`` to swap
``_cache.CACHE_ROOT`` / ``_cache.ensure_cache`` /
``registry.CACHE_ROOT`` / ``registry._editable_checkout_root`` /
``_cache.subprocess.run`` at module scope. We replace those with
hand-rolled ``_swap_*`` helpers that save the prior attribute and
restore on teardown — no fixture-magic, no
``unittest.mock.patch``.
"""

from pathlib import Path
from typing import Any

import pytest

from scitex_template import _cache, clone_template_from_cache, registry

# ---------------------------------------------------------------------------
# Hand-rolled module-attribute swap helpers (no monkeypatch, no mock).
# ---------------------------------------------------------------------------


_MISSING = object()


def _swap_attr(module: Any, name: str, value: Any):
    """Set ``module.<name> = value``; return a restore() callable."""
    saved = getattr(module, name, _MISSING)
    setattr(module, name, value)

    def _restore():
        if saved is _MISSING:
            try:
                delattr(module, name)
            except AttributeError:
                pass
        else:
            setattr(module, name, saved)

    return _restore


def _make_fake_monorepo(root: Path) -> Path:
    """Create a minimal scitex-template-shaped directory under ``root``."""
    (root / "templates" / "alpha").mkdir(parents=True)
    (root / "templates" / "alpha" / "file.txt").write_text("hello")
    (root / "templates" / "alpha" / "sub").mkdir()
    (root / "templates" / "alpha" / "sub" / "deep.txt").write_text("deep")
    # Intra-template relative symlink — mirrors the real research template
    (root / "templates" / "alpha" / "link").symlink_to("file.txt")
    (root / "templates" / "REGISTRY.yaml").write_text(
        "templates:\n"
        "  - id: alpha\n"
        "    description: test\n"
        '    version: "0.0.1"\n'
        "    path: templates/alpha\n"
    )
    return root


@pytest.fixture
def fake_cache(tmp_path):
    """Yield a populated fake cache root; ``_cache`` + ``registry`` are
    wired to point at it for the duration of the test, then restored."""
    cache = tmp_path / "cache"
    _make_fake_monorepo(cache)

    restores = [
        _swap_attr(_cache, "CACHE_ROOT", cache),
        # Bypass network by returning the populated cache directly.
        _swap_attr(_cache, "ensure_cache", lambda **kw: cache),
        _swap_attr(registry, "_editable_checkout_root", lambda: None),
        _swap_attr(registry, "CACHE_ROOT", cache),
    ]
    try:
        yield cache
    finally:
        for restore in reversed(restores):
            restore()


# ---------------------------------------------------------------------------
# clone_template_from_cache
# ---------------------------------------------------------------------------


class TestCloneTemplateFromCache:
    def test_clone_creates_top_level_file_at_target(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert (target / "file.txt").read_text() == "hello"

    def test_clone_returns_target_path(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        result = clone_template_from_cache("alpha", target)
        # Assert
        assert result == target

    def test_clone_copies_nested_file(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert (target / "sub" / "deep.txt").read_text() == "deep"

    def test_clone_preserves_intra_template_symlink(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert (target / "link").is_symlink()

    def test_clone_symlink_resolves_to_copied_file(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert (target / "link").resolve() == (target / "file.txt").resolve()

    def test_unknown_template_id_raises_key_error(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"

        # Act
        def _call():
            clone_template_from_cache("bogus", target)

        # Assert
        with pytest.raises(KeyError, match="bogus"):
            _call()

    def test_non_empty_target_raises_file_exists_error(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        target.mkdir()
        (target / "existing").write_text("x")

        # Act
        def _call():
            clone_template_from_cache("alpha", target)

        # Assert
        with pytest.raises(FileExistsError):
            _call()


# ---------------------------------------------------------------------------
# Provenance manifest — written into prepared template at clone time
# ---------------------------------------------------------------------------


class TestCloneWritesManifest:
    import yaml as _yaml

    def _manifest(self, target: Path) -> dict:
        path = target / ".scitex" / "template" / "MANIFEST.yaml"
        return self._yaml.safe_load(path.read_text())

    def test_manifest_file_is_written(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert (target / ".scitex" / "template" / "MANIFEST.yaml").is_file()

    def test_manifest_records_template_id(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert self._manifest(target)["template"]["id"] == "alpha"

    def test_manifest_records_template_version(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert self._manifest(target)["template"]["version"] == "0.0.1"

    def test_manifest_records_branch_in_source(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target, branch="develop")
        # Assert
        assert self._manifest(target)["source"]["branch"] == "develop"

    def test_manifest_commit_is_unknown_for_non_git_cache(self, tmp_path, fake_cache):
        # The fake cache fixture has no .git, so the sha is best-effort "unknown"
        # rather than an exception.
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert self._manifest(target)["source"]["commit"] == "unknown"

    def test_manifest_has_schema_tag(self, tmp_path, fake_cache):
        # Arrange
        target = tmp_path / "out"
        # Act
        clone_template_from_cache("alpha", target)
        # Assert
        assert self._manifest(target)["schema"] == "scitex-template/manifest@v1"


# ensure_cache refresh behaviour (real git, no fakes): test__cache_refresh.py
