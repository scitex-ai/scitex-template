#!/usr/bin/env python3
"""Tests for template MCP handlers."""

import pytest


class TestListTemplatesHandler:
    """Tests for list_templates_handler."""

    @pytest.mark.asyncio
    async def test_list_templates_handler_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import list_templates_handler

        # Act
        result = await list_templates_handler()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_list_templates_handler_result_has_success_key(self):
        # Arrange
        from scitex_template._mcp.handlers import list_templates_handler

        # Act
        result = await list_templates_handler()
        # Assert
        assert "success" in result

    @pytest.mark.asyncio
    async def test_list_templates_handler_returns_templates_or_error_key(self):
        # Arrange
        from scitex_template._mcp.handlers import list_templates_handler

        # Act
        result = await list_templates_handler()
        # Assert
        assert ("templates" in result) or ("error" in result)


class TestGetTemplateInfoHandler:
    """Tests for get_template_info_handler."""

    @pytest.mark.asyncio
    async def test_get_template_info_for_research_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_template_info_handler

        # Act
        result = await get_template_info_handler("research")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_template_info_for_research_has_success_key(self):
        # Arrange
        from scitex_template._mcp.handlers import get_template_info_handler

        # Act
        result = await get_template_info_handler("research")
        # Assert
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_template_info_for_pip_project_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_template_info_handler

        # Act
        result = await get_template_info_handler("pip_project")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_template_info_for_pip_project_has_success_key(self):
        # Arrange
        from scitex_template._mcp.handlers import get_template_info_handler

        # Act
        result = await get_template_info_handler("pip_project")
        # Assert
        assert "success" in result

    @pytest.mark.asyncio
    async def test_get_template_info_for_invalid_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_template_info_handler

        # Act
        result = await get_template_info_handler("nonexistent_template")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_template_info_for_invalid_has_success_key(self):
        # Arrange
        from scitex_template._mcp.handlers import get_template_info_handler

        # Act
        result = await get_template_info_handler("nonexistent_template")
        # Assert
        assert "success" in result


class TestListGitStrategiesHandler:
    """Tests for list_git_strategies_handler."""

    @pytest.mark.asyncio
    async def test_list_git_strategies_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import list_git_strategies_handler

        # Act
        result = await list_git_strategies_handler()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_list_git_strategies_has_success_key(self):
        # Arrange
        from scitex_template._mcp.handlers import list_git_strategies_handler

        # Act
        result = await list_git_strategies_handler()
        # Assert
        assert "success" in result

    @pytest.mark.asyncio
    async def test_list_git_strategies_returns_strategies_or_error_key(self):
        # Arrange
        from scitex_template._mcp.handlers import list_git_strategies_handler

        # Act
        result = await list_git_strategies_handler()
        # Assert
        assert ("strategies" in result) or ("error" in result)


class TestGetCodeTemplateHandler:
    """Tests for get_code_template_handler."""

    @pytest.mark.asyncio
    async def test_get_code_template_session_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("session")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_code_template_session_succeeds(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("session")
        # Assert
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_get_code_template_session_has_content(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("session")
        # Assert
        assert "content" in result

    @pytest.mark.asyncio
    async def test_get_code_template_all_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("all")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_code_template_all_succeeds(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("all")
        # Assert
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_get_code_template_all_has_content(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("all")
        # Assert
        assert "content" in result

    @pytest.mark.asyncio
    async def test_get_code_template_invalid_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("nonexistent")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_code_template_invalid_reports_failure(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("nonexistent")
        # Assert
        assert result.get("success") is False

    @pytest.mark.asyncio
    async def test_get_code_template_invalid_has_error_message(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("nonexistent")
        # Assert
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_code_template_with_filepath_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("session", filepath="custom_script.py")
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_code_template_with_filepath_succeeds(self):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("session", filepath="custom_script.py")
        # Assert
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_get_code_template_with_filepath_propagates_filepath_into_content(
        self,
    ):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler("session", filepath="custom_script.py")
        # Assert
        assert "custom_script.py" in result.get("content", "")

    @pytest.mark.parametrize(
        "template_id",
        ["plt", "stats", "scholar", "audio", "capture", "diagram", "canvas", "writer"],
    )
    @pytest.mark.asyncio
    async def test_get_code_template_for_module_usage_succeeds(self, template_id):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler(template_id)
        # Assert
        assert result.get("success") is True, f"Failed for template: {template_id}"

    @pytest.mark.parametrize(
        "template_id",
        ["plt", "stats", "scholar", "audio", "capture", "diagram", "canvas", "writer"],
    )
    @pytest.mark.asyncio
    async def test_get_code_template_for_module_usage_has_content(self, template_id):
        # Arrange
        from scitex_template._mcp.handlers import get_code_template_handler

        # Act
        result = await get_code_template_handler(template_id)
        # Assert
        assert "content" in result, f"Missing content for template: {template_id}"


class TestListCodeTemplatesHandler:
    """Tests for list_code_templates_handler."""

    @pytest.mark.asyncio
    async def test_list_code_templates_returns_dict(self):
        # Arrange
        from scitex_template._mcp.handlers import list_code_templates_handler

        # Act
        result = await list_code_templates_handler()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_list_code_templates_succeeds(self):
        # Arrange
        from scitex_template._mcp.handlers import list_code_templates_handler

        # Act
        result = await list_code_templates_handler()
        # Assert
        assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_list_code_templates_has_templates_key(self):
        # Arrange
        from scitex_template._mcp.handlers import list_code_templates_handler

        # Act
        result = await list_code_templates_handler()
        # Assert
        assert "templates" in result

    @pytest.mark.parametrize(
        "expected_id",
        ["session", "io", "config", "plt", "stats", "scholar"],
    )
    @pytest.mark.asyncio
    async def test_list_code_templates_contains_expected_id(self, expected_id):
        # Arrange
        from scitex_template._mcp.handlers import list_code_templates_handler

        result = await list_code_templates_handler()
        template_ids = [t["id"] for t in result.get("templates", [])]
        # Act
        present = expected_id in template_ids
        # Assert
        assert present, f"Template '{expected_id}' not in list"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
