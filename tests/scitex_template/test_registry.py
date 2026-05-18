"""Tests for scitex_template.registry.

PA-306 no-mocks. The previous suite used ``monkeypatch`` to swap
``registry._editable_checkout_root`` / ``registry.CACHE_ROOT``;
replaced with hand-rolled ``_swap_attr`` helpers.
"""

from pathlib import Path
from typing import Any

import pytest

from scitex_template import registry


_MISSING = object()


def _swap_attr(module: Any, name: str, value: Any):
    """Set ``module.<name> = value``; return restore() callable."""
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


class TestRegistryRoot:
    def test_editable_checkout_is_preferred_over_cache(self):
        # Arrange
        # Act
        root = registry.registry_root()
        # Assert
        assert root is not None

    def test_editable_checkout_root_contains_REGISTRY_yaml(self):
        # Arrange
        # Act
        root = registry.registry_root()
        # Assert
        assert (root / "templates" / "REGISTRY.yaml").is_file()

    def test_returns_none_when_no_editable_checkout_and_cache_missing(self, tmp_path):
        # Arrange
        restores = [
            _swap_attr(registry, "_editable_checkout_root", lambda: None),
            _swap_attr(registry, "CACHE_ROOT", tmp_path / "nonexistent"),
        ]
        try:
            # Act
            result = registry.registry_root()
            # Assert
            assert result is None
        finally:
            for restore in reversed(restores):
                restore()

    def test_returns_cache_root_when_no_editable_checkout_but_cache_present(
        self, tmp_path
    ):
        # Arrange
        fake_cache = tmp_path / "cache"
        (fake_cache / "templates").mkdir(parents=True)
        (fake_cache / "templates" / "REGISTRY.yaml").write_text("templates: []\n")
        restores = [
            _swap_attr(registry, "_editable_checkout_root", lambda: None),
            _swap_attr(registry, "CACHE_ROOT", fake_cache),
        ]
        try:
            # Act
            result = registry.registry_root()
            # Assert
            assert result == fake_cache
        finally:
            for restore in reversed(restores):
                restore()


class TestLoadRegistry:
    def test_loaded_registry_ids_match_expected_six_templates(self):
        # Arrange
        expected = {
            "pip-project",
            "minimal",
            "cloud-module",
            "research",
            "singularity",
            "paper",
        }
        # Act
        ids = {e.id for e in registry.load_registry()}
        # Assert
        assert ids == expected

    def test_every_entry_has_non_empty_id(self):
        # Arrange
        entries = list(registry.load_registry())
        # Act
        all_have_id = all(bool(e.id) for e in entries)
        # Assert
        assert all_have_id

    def test_every_entry_has_non_empty_description(self):
        # Arrange
        entries = list(registry.load_registry())
        # Act
        all_have_desc = all(bool(e.description) for e in entries)
        # Assert
        assert all_have_desc

    def test_every_entry_has_non_empty_version(self):
        # Arrange
        entries = list(registry.load_registry())
        # Act
        all_have_version = all(bool(e.version) for e in entries)
        # Assert
        assert all_have_version

    def test_every_entry_path_is_pathlib_path(self):
        # Arrange
        entries = list(registry.load_registry())
        # Act
        all_path = all(isinstance(e.path, Path) for e in entries)
        # Assert
        assert all_path

    def test_load_registry_raises_when_no_editable_and_no_cache(self, tmp_path):
        # Arrange
        restores = [
            _swap_attr(registry, "_editable_checkout_root", lambda: None),
            _swap_attr(registry, "CACHE_ROOT", tmp_path / "nope"),
        ]

        # Act
        def _call():
            registry.load_registry()

        # Assert
        try:
            with pytest.raises(FileNotFoundError):
                _call()
        finally:
            for restore in reversed(restores):
                restore()


class TestFindTemplate:
    def test_find_template_known_id_returns_entry_with_matching_id(self):
        # Arrange
        # Act
        entry = registry.find_template("pip-project")
        # Assert
        assert entry is not None and entry.id == "pip-project"

    def test_find_template_unknown_id_returns_none(self):
        # Arrange
        # Act
        entry = registry.find_template("does-not-exist")
        # Assert
        assert entry is None
