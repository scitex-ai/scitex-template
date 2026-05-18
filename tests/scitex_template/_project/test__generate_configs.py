#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: tests/scitex/template/_project/test__generate_configs.py
"""Tests for scitex_template._project._generate_configs."""

import json

import pytest

from scitex_template._project._generate_configs import (
    create_env_template,
    create_paths_config,
    create_project_config,
    create_requirements_file,
)


@pytest.fixture
def metadata():
    return {
        "name": "Test Project",
        "id": 42,
        "description": "Testing configs",
        "created_at": "2026-01-01",
        "owner": "jdoe",
        "progress": 50,
        "hypotheses": "H1: X causes Y",
    }


class TestCreateProjectConfig:
    def test_creates_config_file_on_disk(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_project_config(str(tmp_path), metadata)
        # Assert
        assert out.exists()

    def test_writes_into_config_subdirectory(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_project_config(str(tmp_path), metadata)
        # Assert
        assert out.parent.name == "config"

    def test_yaml_or_json_payload_contains_project_name(self, tmp_path, metadata):
        # Arrange
        out = create_project_config(str(tmp_path), metadata)
        text = out.read_text()
        # Act
        contains_name = "Test Project" in text
        # Assert
        assert contains_name

    def test_creates_config_directory_at_project_root(self, tmp_path, metadata):
        # Arrange
        # Act
        create_project_config(str(tmp_path), metadata)
        # Assert
        assert (tmp_path / "config").is_dir()


class TestCreatePathsConfig:
    def test_writes_paths_json_filename(self, tmp_path):
        # Arrange
        # Act
        out = create_paths_config(str(tmp_path))
        # Assert
        assert out.name == "paths.json"

    def test_paths_json_contains_data_key(self, tmp_path):
        # Arrange
        # Act
        out = create_paths_config(str(tmp_path))
        # Assert
        assert "data" in json.loads(out.read_text())

    def test_paths_json_contains_scripts_key(self, tmp_path):
        # Arrange
        # Act
        out = create_paths_config(str(tmp_path))
        # Assert
        assert "scripts" in json.loads(out.read_text())

    def test_paths_json_uses_absolute_paths_for_scripts(self, tmp_path):
        # Arrange
        # Act
        out = create_paths_config(str(tmp_path))
        # Assert
        assert str(tmp_path) in json.loads(out.read_text())["scripts"]


class TestCreateEnvTemplate:
    def test_writes_dotenv_template_filename(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_env_template(str(tmp_path), metadata)
        # Assert
        assert out.name == ".env.template"

    def test_env_template_contains_project_name(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_env_template(str(tmp_path), metadata)
        # Assert
        assert "Test Project" in out.read_text()

    def test_env_template_contains_project_id(self, tmp_path, metadata):
        # Arrange
        # Act
        out = create_env_template(str(tmp_path), metadata)
        # Assert
        assert "42" in out.read_text()


class TestCreateRequirementsFile:
    def test_writes_requirements_txt_filename(self, tmp_path):
        # Arrange
        # Act
        out = create_requirements_file(str(tmp_path))
        # Assert
        assert out.name == "requirements.txt"

    def test_requirements_lists_numpy(self, tmp_path):
        # Arrange
        # Act
        out = create_requirements_file(str(tmp_path))
        # Assert
        assert "numpy" in out.read_text()

    def test_requirements_lists_pandas(self, tmp_path):
        # Arrange
        # Act
        out = create_requirements_file(str(tmp_path))
        # Assert
        assert "pandas" in out.read_text()


# EOF
