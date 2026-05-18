#!/usr/bin/env python3
# Timestamp: 2026-02-08
# File: tests/scitex/template/test_clone_template.py

"""Tests for the unified clone_template dispatcher.

PA-306 no-mocks. We swap the production ``TEMPLATES`` dict entry
for a hand-rolled callable that records its kwargs; restore at
teardown. No ``unittest.mock`` / ``monkeypatch`` — the dispatcher's
own dict IS the documented seam.

The "xfail" suites that targeted non-existent
``scitex.scholar.ensure`` / ``scitex.writer.ensure`` APIs (and
needed heavy mocking to pretend they existed) are removed — they
asserted nothing real about production code.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from scitex_template._project._clone_template import (
    ALIASES,
    TEMPLATES,
    clone_template,
    get_all_template_ids,
    get_template_ids,
)


# ---------------------------------------------------------------------------
# Hand-rolled fake callable + _swap_template helper
# ---------------------------------------------------------------------------


class _RecordingClone:
    """Callable that records every kwargs and returns ``return_value``."""

    def __init__(self, return_value: bool = True) -> None:
        self.return_value = return_value
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> bool:
        self.calls.append(kwargs)
        return self.return_value


def _swap_template(template_id: str, fake: Any):
    """Replace ``TEMPLATES[template_id]`` with ``fake``; return restore fn."""
    saved = TEMPLATES.get(template_id, _MISSING)
    TEMPLATES[template_id] = fake

    def _restore():
        if saved is _MISSING:
            TEMPLATES.pop(template_id, None)
        else:
            TEMPLATES[template_id] = saved

    return _restore


_MISSING = object()


# ---------------------------------------------------------------------------
# Dispatch — canonical IDs
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_research():
    """Swap TEMPLATES['research'] for a recording fake; restore on teardown."""
    fake = _RecordingClone(return_value=True)
    restore = _swap_template("research", fake)
    try:
        yield fake
    finally:
        restore()


class TestCloneTemplateDispatch:
    """Canonical template IDs dispatch to their function."""

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_canonical_id_returns_true_when_clone_returns_true(self, template_id):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template(template_id, fake)
        try:
            # Act
            result = clone_template(
                template_id=template_id,
                project_dir="/tmp/test-project",
            )
            # Assert
            assert result is True
        finally:
            restore()

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_canonical_id_invokes_clone_exactly_once(self, template_id):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template(template_id, fake)
        try:
            # Act
            clone_template(template_id=template_id, project_dir="/tmp/test-project")
            # Assert
            assert len(fake.calls) == 1
        finally:
            restore()

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_canonical_id_forwards_project_dir(self, template_id):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template(template_id, fake)
        try:
            # Act
            clone_template(template_id=template_id, project_dir="/tmp/test-project")
            # Assert
            assert fake.calls[0]["project_dir"] == "/tmp/test-project"
        finally:
            restore()

    @pytest.mark.parametrize("template_id", list(TEMPLATES.keys()))
    def test_canonical_id_defaults_git_strategy_to_child(self, template_id):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template(template_id, fake)
        try:
            # Act
            clone_template(template_id=template_id, project_dir="/tmp/test-project")
            # Assert
            assert fake.calls[0]["git_strategy"] == "child"
        finally:
            restore()


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------


class TestAliasResolution:
    """Aliases resolve to canonical IDs."""

    @pytest.mark.parametrize("alias,canonical", list(ALIASES.items()))
    def test_alias_dispatches_to_canonical_clone_function(self, alias, canonical):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template(canonical, fake)
        try:
            # Act
            clone_template(template_id=alias, project_dir="/tmp/test-alias")
            # Assert
            assert len(fake.calls) == 1
        finally:
            restore()

    @pytest.mark.parametrize("alias,canonical", list(ALIASES.items()))
    def test_alias_returns_clone_return_value(self, alias, canonical):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template(canonical, fake)
        try:
            # Act
            result = clone_template(template_id=alias, project_dir="/tmp/test-alias")
            # Assert
            assert result is True
        finally:
            restore()


# ---------------------------------------------------------------------------
# Error paths and kwargs forwarding
# ---------------------------------------------------------------------------


class TestCloneTemplateErrors:
    def test_unknown_template_id_raises_value_error(self):
        # Arrange
        bogus_id = "nonexistent"

        # Act
        def _call():
            clone_template(template_id=bogus_id, project_dir="/tmp/test")

        # Assert
        with pytest.raises(ValueError, match="Unknown template"):
            _call()


class TestKwargsForwarding:
    def test_git_strategy_origin_is_forwarded(self, fake_research):
        # Arrange
        # (fixture provides recording fake at TEMPLATES['research'])
        # Act
        clone_template(
            template_id="research",
            project_dir="/tmp/test",
            git_strategy="origin",
            branch="develop",
            tag=None,
        )
        # Assert
        assert fake_research.calls[0]["git_strategy"] == "origin"

    def test_branch_is_forwarded(self, fake_research):
        # Arrange
        # Act
        clone_template(
            template_id="research",
            project_dir="/tmp/test",
            git_strategy="origin",
            branch="develop",
        )
        # Assert
        assert fake_research.calls[0]["branch"] == "develop"

    def test_tag_is_forwarded(self, fake_research):
        # Arrange
        # Act
        clone_template(
            template_id="research",
            project_dir="/tmp/test",
            tag="v1.2.3",
        )
        # Assert
        assert fake_research.calls[0]["tag"] == "v1.2.3"

    def test_git_strategy_none_is_forwarded_as_none(self, fake_research):
        # Arrange
        # Act
        clone_template(
            template_id="research",
            project_dir="/tmp/test",
            git_strategy=None,
        )
        # Assert
        assert fake_research.calls[0]["git_strategy"] is None


class TestReturnValuePropagation:
    def test_false_return_from_clone_function_is_propagated(self):
        # Arrange
        fake = _RecordingClone(return_value=False)
        restore = _swap_template("research", fake)
        try:
            # Act
            result = clone_template(template_id="research", project_dir="/tmp/test")
            # Assert
            assert result is False
        finally:
            restore()


# ---------------------------------------------------------------------------
# Template-id helpers
# ---------------------------------------------------------------------------


class TestTemplateIdHelpers:
    """Helper functions for template IDs."""

    def test_get_template_ids_includes_research(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "research" in ids

    def test_get_template_ids_includes_research_minimal(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "research_minimal" in ids

    def test_get_template_ids_includes_scitex_minimal(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "scitex_minimal" in ids

    def test_get_template_ids_includes_pip_project(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "pip_project" in ids

    def test_get_template_ids_includes_singularity(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "singularity" in ids

    def test_get_template_ids_includes_paper_directory(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "paper_directory" in ids

    def test_get_template_ids_excludes_alias_minimal(self):
        # Arrange
        # Act
        ids = get_template_ids()
        # Assert
        assert "minimal" not in ids

    def test_get_all_template_ids_includes_canonical_research(self):
        # Arrange
        # Act
        ids = get_all_template_ids()
        # Assert
        assert "research" in ids

    def test_get_all_template_ids_includes_alias_minimal(self):
        # Arrange
        # Act
        ids = get_all_template_ids()
        # Assert
        assert "minimal" in ids

    def test_get_all_template_ids_includes_alias_pip_project_hyphenated(self):
        # Arrange
        # Act
        ids = get_all_template_ids()
        # Assert
        assert "pip-project" in ids

    def test_get_all_template_ids_includes_alias_paper(self):
        # Arrange
        # Act
        ids = get_all_template_ids()
        # Assert
        assert "paper" in ids

    def test_minimal_alias_resolves_to_scitex_minimal(self):
        # Arrange
        # Act
        target = ALIASES["minimal"]
        # Assert
        assert target == "scitex_minimal"


# ---------------------------------------------------------------------------
# include_dirs / extra kwargs forwarding
# ---------------------------------------------------------------------------


class TestIncludeDirsForwarding:
    """``include_dirs`` and other extra kwargs flow through the dispatcher."""

    def test_include_dirs_kwarg_is_forwarded_to_research_minimal(self):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template("research_minimal", fake)
        try:
            # Act
            clone_template(
                template_id="research_minimal",
                project_dir="/tmp/test",
                include_dirs=["00_shared", "01_manuscript"],
            )
            # Assert
            assert fake.calls[0]["include_dirs"] == ["00_shared", "01_manuscript"]
        finally:
            restore()

    def test_use_cache_kwarg_is_forwarded_to_research(self, fake_research):
        # Arrange
        # Act
        clone_template(
            template_id="research",
            project_dir="/tmp/test",
            use_cache=False,
        )
        # Assert
        assert fake_research.calls[0]["use_cache"] is False


# ---------------------------------------------------------------------------
# _filter_to_include_dirs — pure filesystem behaviour
# ---------------------------------------------------------------------------


class TestFilterToIncludeDirs:
    """The ``_filter_to_include_dirs`` helper prunes a real directory tree."""

    def test_removes_dir_not_in_include_list(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared", "01_manuscript"])
        # Assert
        assert not (tmp_path / "02_supplementary").exists()

    def test_keeps_dir_listed_in_include(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared", "01_manuscript"])
        # Assert
        assert (tmp_path / "00_shared").exists()

    def test_preserves_readme_even_when_not_listed(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "README.md").write_text("readme")
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared"])
        # Assert
        assert (tmp_path / "README.md").exists()

    def test_preserves_license_even_when_not_listed(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "LICENSE").write_text("license")
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared"])
        # Assert
        assert (tmp_path / "LICENSE").exists()

    def test_preserves_dotfile_gitignore(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / ".gitignore").write_text("*.pyc")
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared"])
        # Assert
        assert (tmp_path / ".gitignore").exists()

    def test_preserves_dot_git_dir(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / ".git").mkdir()
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared"])
        # Assert
        assert (tmp_path / ".git").exists()

    def test_removes_unlisted_top_level_file(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "pyproject.toml").write_text("[project]")
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared"])
        # Assert
        assert not (tmp_path / "pyproject.toml").exists()

    def test_keeps_top_level_file_when_listed(self, tmp_path):
        # Arrange
        from scitex_template._project._clone_project import _filter_to_include_dirs

        (tmp_path / "00_shared").mkdir()
        (tmp_path / "compile.sh").write_text("#!/bin/bash")
        # Act
        _filter_to_include_dirs(tmp_path, ["00_shared", "compile.sh"])
        # Assert
        assert (tmp_path / "compile.sh").exists()


# ---------------------------------------------------------------------------
# MINIMAL_INCLUDE_DIRS constant
# ---------------------------------------------------------------------------


class TestMinimalIncludeDirs:
    """MINIMAL_INCLUDE_DIRS exports the documented minimal layout."""

    @pytest.mark.parametrize(
        "expected_dir",
        ["00_shared", "01_manuscript", "scripts", "compile.sh", "Makefile", "config"],
    )
    def test_minimal_include_dirs_contains_expected_entry(self, expected_dir):
        # Arrange
        from scitex_template import MINIMAL_INCLUDE_DIRS

        # Act
        present = expected_dir in MINIMAL_INCLUDE_DIRS
        # Assert
        assert present

    def test_minimal_include_dirs_contains_supplementary(self):
        # Arrange
        from scitex_template import MINIMAL_INCLUDE_DIRS

        # Act
        present = "02_supplementary" in MINIMAL_INCLUDE_DIRS
        # Assert
        assert present

    def test_minimal_include_dirs_contains_revision(self):
        # Arrange
        from scitex_template import MINIMAL_INCLUDE_DIRS

        # Act
        present = "03_revision" in MINIMAL_INCLUDE_DIRS
        # Assert
        assert present

    def test_minimal_include_dirs_excludes_src(self):
        # Arrange
        from scitex_template import MINIMAL_INCLUDE_DIRS

        # Act
        present = "src" in MINIMAL_INCLUDE_DIRS
        # Assert
        assert not present

    def test_minimal_include_dirs_excludes_tests(self):
        # Arrange
        from scitex_template import MINIMAL_INCLUDE_DIRS

        # Act
        present = "tests" in MINIMAL_INCLUDE_DIRS
        # Assert
        assert not present


# ---------------------------------------------------------------------------
# clone_research_minimal passes include_dirs through clone_project
# ---------------------------------------------------------------------------


class _RecordingCloneProject:
    """Callable that records kwargs and returns True."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, *args: Any, **kwargs: Any) -> bool:
        self.calls.append(kwargs)
        return True


def _swap_clone_project_in_module(module, fake):
    """Replace ``module.clone_project`` with ``fake``; return restore fn."""
    saved = module.clone_project
    module.clone_project = fake

    def _restore():
        module.clone_project = saved

    return _restore


class TestCloneResearchMinimalIncludeDirsForwarding:
    """``clone_research_minimal`` forwards ``include_dirs`` to ``clone_project``."""

    def test_clone_research_minimal_passes_minimal_include_dirs(self):
        # Arrange
        from scitex_template._project import clone_research_minimal as crm
        from scitex_template._project.clone_research_minimal import (
            MINIMAL_INCLUDE_DIRS,
            clone_research_minimal,
        )

        fake = _RecordingCloneProject()
        restore = _swap_clone_project_in_module(crm, fake)
        try:
            # Act
            clone_research_minimal("/tmp/test-minimal")
            # Assert
            assert fake.calls[0]["include_dirs"] == MINIMAL_INCLUDE_DIRS
        finally:
            restore()


# ---------------------------------------------------------------------------
# customize_minimal_template — real filesystem
# ---------------------------------------------------------------------------


class TestCustomizeMinimalPaths:
    """customize_minimal_template finds files in both flat and nested layouts."""

    def test_direct_clone_layout_writes_project_name_to_title(self, tmp_path):
        # Arrange
        from scitex_template._project._customize import customize_minimal_template

        shared = tmp_path / "00_shared"
        shared.mkdir()
        (shared / "title.tex").write_text("\\title{Old Title}")
        (shared / "authors.tex").write_text("\\author{Old Author}")
        # Act
        customize_minimal_template(
            str(tmp_path),
            {"name": "My Project", "owner": "testuser", "owner_full_name": "Test User"},
        )
        # Assert
        assert "My Project" in (shared / "title.tex").read_text()

    def test_direct_clone_layout_writes_owner_full_name_to_authors(self, tmp_path):
        # Arrange
        from scitex_template._project._customize import customize_minimal_template

        shared = tmp_path / "00_shared"
        shared.mkdir()
        (shared / "title.tex").write_text("\\title{Old Title}")
        (shared / "authors.tex").write_text("\\author{Old Author}")
        # Act
        customize_minimal_template(
            str(tmp_path),
            {"name": "My Project", "owner": "testuser", "owner_full_name": "Test User"},
        )
        # Assert
        assert "Test User" in (shared / "authors.tex").read_text()

    def test_nested_scitex_writer_layout_writes_project_name_to_title(self, tmp_path):
        # Arrange
        from scitex_template._project._customize import customize_minimal_template

        nested = tmp_path / "scitex" / "writer" / "00_shared"
        nested.mkdir(parents=True)
        (nested / "title.tex").write_text("\\title{Old}")
        # Act
        customize_minimal_template(str(tmp_path), {"name": "Nested Project"})
        # Assert
        assert "Nested Project" in (nested / "title.tex").read_text()


# ---------------------------------------------------------------------------
# Package re-exports
# ---------------------------------------------------------------------------


class TestImportFromPackage:
    """clone_template + friends are importable from ``scitex_template``."""

    def test_clone_template_is_importable_from_scitex_template(self):
        # Arrange
        from scitex_template import clone_template as ct

        # Act
        is_callable = callable(ct)
        # Assert
        assert is_callable

    def test_clone_template_is_in_scitex_template_dunder_all(self):
        # Arrange
        import scitex_template

        # Act
        present = "clone_template" in scitex_template.__all__
        # Assert
        assert present

    def test_minimal_include_dirs_is_in_scitex_template_dunder_all(self):
        # Arrange
        import scitex_template

        # Act
        present = "MINIMAL_INCLUDE_DIRS" in scitex_template.__all__
        # Assert
        assert present

    def test_clone_scitex_minimal_is_in_scitex_template_dunder_all(self):
        # Arrange
        import scitex_template

        # Act
        present = "clone_scitex_minimal" in scitex_template.__all__
        # Assert
        assert present


# ---------------------------------------------------------------------------
# scitex_minimal dispatch
# ---------------------------------------------------------------------------


class TestScitexMinimalDispatch:
    def test_scitex_minimal_is_registered_in_TEMPLATES(self):
        # Arrange
        # Act
        present = "scitex_minimal" in TEMPLATES
        # Assert
        assert present

    def test_scitex_minimal_dispatches_to_its_clone_function(self):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template("scitex_minimal", fake)
        try:
            # Act
            result = clone_template(
                template_id="scitex_minimal",
                project_dir="/tmp/test-scitex-minimal",
            )
            # Assert
            assert result is True
        finally:
            restore()

    def test_minimal_alias_dispatches_to_scitex_minimal_clone_function(self):
        # Arrange
        fake = _RecordingClone(return_value=True)
        restore = _swap_template("scitex_minimal", fake)
        try:
            # Act
            clone_template(
                template_id="minimal",
                project_dir="/tmp/test-minimal-alias",
            )
            # Assert
            assert len(fake.calls) == 1
        finally:
            restore()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
