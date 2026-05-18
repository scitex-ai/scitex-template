#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__directory_structure.py
"""Tests for scitex_template._project._directory_structure."""

import pytest

from scitex_template._project._directory_structure import (
    PROJECT_STRUCTURE,
    build_directory_tree,
)


class TestProjectStructure:
    def test_top_level_keys_match_expected_set(self):
        # Arrange
        expected = {"config", "data", "scripts", "docs", "results", "temp"}
        # Act
        actual = set(PROJECT_STRUCTURE.keys())
        # Assert
        assert actual == expected


class TestBuildDirectoryTree:
    @pytest.mark.parametrize("dirname", list(PROJECT_STRUCTURE.keys()))
    def test_default_creates_top_level_dir(self, tmp_path, dirname):
        # Arrange
        # Act
        build_directory_tree(str(tmp_path))
        # Assert
        assert (tmp_path / dirname).is_dir()

    def test_custom_structure_creates_src_dir(self, tmp_path):
        # Arrange
        custom = {"src": [], "tests": [], "docs": []}
        # Act
        build_directory_tree(str(tmp_path), structure=custom)
        # Assert
        assert (tmp_path / "src").is_dir()

    def test_custom_structure_creates_tests_dir(self, tmp_path):
        # Arrange
        custom = {"src": [], "tests": [], "docs": []}
        # Act
        build_directory_tree(str(tmp_path), structure=custom)
        # Assert
        assert (tmp_path / "tests").is_dir()

    def test_nested_structure_creates_data_raw_csv(self, tmp_path):
        # Arrange
        nested = {"data": {"raw": ["csv", "json"]}}
        # Act
        build_directory_tree(str(tmp_path), structure=nested)
        # Assert
        assert (tmp_path / "data" / "raw" / "csv").is_dir()

    def test_nested_structure_creates_data_raw_json(self, tmp_path):
        # Arrange
        nested = {"data": {"raw": ["csv", "json"]}}
        # Act
        build_directory_tree(str(tmp_path), structure=nested)
        # Assert
        assert (tmp_path / "data" / "raw" / "json").is_dir()


# EOF
