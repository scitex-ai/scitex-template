#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__customize.py
"""Tests for scitex_template._project._customize."""

import pathlib

import pytest

from scitex_template._project._customize import (
    customize_minimal_template,
    customize_template,
)


@pytest.fixture
def project_dir(tmp_path):
    """Create a fake project directory with template files."""
    (tmp_path / "README.md").write_text(
        "# SciTeX Example Research Project\nThis is an example research project"
    )
    paper = tmp_path / "paper" / "manuscript" / "src"
    paper.mkdir(parents=True)
    (paper / "title.tex").write_text("\\title{Template Title}")
    (paper / "authors.tex").write_text("\\author{Template Author}")
    return str(tmp_path)


@pytest.fixture
def minimal_dir(tmp_path):
    """Create a fake minimal template directory."""
    shared = tmp_path / "scitex" / "writer" / "00_shared"
    shared.mkdir(parents=True)
    (shared / "title.tex").write_text("\\title{Placeholder}")
    (shared / "authors.tex").write_text("\\author{Placeholder}")
    return str(tmp_path)


@pytest.fixture
def metadata():
    return {
        "name": "My Research",
        "description": "A test project",
        "owner": "jdoe",
        "owner_full_name": "Jane Doe",
    }


class TestCustomizeTemplate:
    def test_updates_readme_title_to_project_name(self, project_dir, metadata):
        # Arrange
        # (fixtures provide project tree + metadata)
        # Act
        customize_template(project_dir, metadata)
        # Assert
        readme = (pathlib.Path(project_dir) / "README.md").read_text()
        assert "# My Research" in readme

    def test_updates_readme_body_to_description(self, project_dir, metadata):
        # Arrange
        # Act
        customize_template(project_dir, metadata)
        # Assert
        readme = (pathlib.Path(project_dir) / "README.md").read_text()
        assert "A test project" in readme

    def test_updates_title_tex_to_project_name(self, project_dir, metadata):
        # Arrange
        # Act
        customize_template(project_dir, metadata)
        # Assert
        title = (
            pathlib.Path(project_dir) / "paper" / "manuscript" / "src" / "title.tex"
        ).read_text()
        assert "My Research" in title

    def test_updates_authors_tex_to_owner_full_name(self, project_dir, metadata):
        # Arrange
        # Act
        customize_template(project_dir, metadata)
        # Assert
        authors = (
            pathlib.Path(project_dir) / "paper" / "manuscript" / "src" / "authors.tex"
        ).read_text()
        assert "Jane Doe" in authors

    def test_missing_files_does_not_raise(self, tmp_path, metadata):
        # Arrange
        empty_dir = str(tmp_path)
        # Act
        customize_template(empty_dir, metadata)
        # Assert
        assert (tmp_path).exists()


class TestCustomizeMinimalTemplate:
    def test_updates_title_to_project_name(self, minimal_dir, metadata):
        # Arrange
        # Act
        customize_minimal_template(minimal_dir, metadata)
        # Assert
        title = (
            pathlib.Path(minimal_dir) / "scitex" / "writer" / "00_shared" / "title.tex"
        ).read_text()
        assert "My Research" in title

    def test_updates_authors_to_owner_full_name(self, minimal_dir, metadata):
        # Arrange
        # Act
        customize_minimal_template(minimal_dir, metadata)
        # Assert
        authors = (
            pathlib.Path(minimal_dir)
            / "scitex"
            / "writer"
            / "00_shared"
            / "authors.tex"
        ).read_text()
        assert "Jane Doe" in authors

    def test_uses_owner_username_when_no_full_name_provided(self, minimal_dir):
        # Arrange
        meta = {"name": "Test", "owner": "jdoe"}
        # Act
        customize_minimal_template(minimal_dir, meta)
        # Assert
        authors = (
            pathlib.Path(minimal_dir)
            / "scitex"
            / "writer"
            / "00_shared"
            / "authors.tex"
        ).read_text()
        assert "jdoe" in authors


# EOF
