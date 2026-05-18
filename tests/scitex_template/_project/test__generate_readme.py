#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__generate_readme.py
"""Tests for scitex_template._project._generate_readme."""

import pytest

from scitex_template._project._generate_readme import (
    create_minimal_readme,
    create_project_readme,
)


@pytest.fixture
def metadata():
    return {
        "name": "My Research",
        "created_at": "2026-01-15",
        "owner": "jdoe",
        "owner_full_name": "Jane Doe",
        "description": "A test project",
        "hypotheses": "H1: X > Y",
        "progress": 75,
        "id": 42,
        "updated_at": "2026-02-01",
    }


class TestCreateMinimalReadme:
    def test_minimal_readme_file_is_created_on_disk(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_minimal_readme(str(tmp_path), metadata)
        # Assert
        assert out.exists()

    def test_minimal_readme_filename_is_README_md(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_minimal_readme(str(tmp_path), metadata)
        # Assert
        assert out.name == "README.md"

    def test_minimal_readme_body_contains_project_name(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_minimal_readme(str(tmp_path), metadata)
        # Assert
        assert "# My Research" in out.read_text()

    def test_minimal_readme_body_contains_owner_full_name(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_minimal_readme(str(tmp_path), metadata)
        # Assert
        assert "Jane Doe" in out.read_text()


class TestCreateProjectReadme:
    def test_project_readme_file_is_created_on_disk(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_project_readme(str(tmp_path), metadata)
        # Assert
        assert out.exists()

    def test_project_readme_body_contains_hypotheses(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_project_readme(str(tmp_path), metadata)
        # Assert
        assert "H1: X > Y" in out.read_text()

    def test_project_readme_body_contains_progress_percentage(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_project_readme(str(tmp_path), metadata)
        # Assert
        assert "75%" in out.read_text()

    def test_project_readme_body_contains_project_id(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_project_readme(str(tmp_path), metadata)
        # Assert
        assert "42" in out.read_text()


# EOF
