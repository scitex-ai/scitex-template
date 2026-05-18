"""Tests for scitex_template.cli."""

import json

import pytest
from click.testing import CliRunner

from scitex_template.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestListHumanOutput:
    def test_list_templates_exits_zero(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["list-templates"])
        # Assert
        assert result.exit_code == 0

    @pytest.mark.parametrize(
        "tid",
        ["pip-project", "minimal", "cloud-module", "research", "singularity", "paper"],
    )
    def test_list_templates_human_output_contains_template_id(self, runner, tid):
        # Arrange
        # Act
        result = runner.invoke(main, ["list-templates"])
        # Assert
        assert tid in result.output


class TestListJsonOutput:
    def test_list_templates_json_exits_zero(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["list-templates", "--json"])
        # Assert
        assert result.exit_code == 0

    def test_list_templates_json_payload_includes_pip_project_and_research(
        self, runner
    ):
        # Arrange
        result = runner.invoke(main, ["list-templates", "--json"])
        data = json.loads(result.output)
        ids = {row["id"] for row in data}
        # Act
        is_superset = {"pip-project", "research"}.issubset(ids)
        # Assert
        assert is_superset


class TestInfo:
    def test_show_info_for_known_id_exits_zero(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["show-info", "pip-project"])
        # Assert
        assert result.exit_code == 0

    def test_show_info_for_known_id_mentions_template_id_in_output(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["show-info", "pip-project"])
        # Assert
        assert "pip-project" in result.output

    def test_show_info_for_known_id_mentions_version_in_output(self, runner):
        # Arrange
        result = runner.invoke(main, ["show-info", "pip-project"])
        text = result.output.lower()
        # Act
        mentions_version = "version" in text or "0.1.0" in text
        # Assert
        assert mentions_version

    def test_show_info_for_unknown_id_exits_nonzero(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["show-info", "does-not-exist"])
        # Assert
        assert result.exit_code == 1


class TestVersion:
    def test_v_flag_exits_zero(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["-V"])
        # Assert
        assert result.exit_code == 0

    def test_v_flag_emits_non_empty_output(self, runner):
        # Arrange
        # Act
        result = runner.invoke(main, ["-V"])
        # Assert
        assert result.output.strip()
