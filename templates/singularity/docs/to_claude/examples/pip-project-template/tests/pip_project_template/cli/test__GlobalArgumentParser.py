#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-27 10:37:16 (ywatanabe)"
# File: /home/ywatanabe/proj/pip-project-template/tests/pip_project_template/cli/test__CentralArgumentParser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./tests/pip_project_template/cli/test__CentralArgumentParser.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

# Test file for src/cli/_GlobalArgumentParser.py

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from pip_project_template.cli._GlobalArgumentParser import GlobalArgumentParser


class TestCentralargumentparser:
    """Test suite for cli._GlobalArgumentParser"""

    def test_module_imports(self):
        """Test that module imports successfully."""
        import importlib

        module = importlib.import_module(
            "pip_project_template.cli._GlobalArgumentParser"
        )
        assert module is not None

    def test_module_has_expected_attributes(self):
        """Test that module has expected structure."""
        import importlib

        module = importlib.import_module(
            "pip_project_template.cli._GlobalArgumentParser"
        )

        # Check that module has a docstring or __all__ or callable functions
        has_content = (
            hasattr(module, "__doc__")
            and module.__doc__
            or hasattr(module, "__all__")
            or any(
                callable(getattr(module, attr))
                for attr in dir(module)
                if not attr.startswith("_")
            )
        )
        assert (
            has_content
        ), f"Module cli._GlobalArgumentParser appears to be empty or malformed"

    def test_module_file_exists(self):
        """Test that the source file exists and is readable."""
        src_file = (
            Path(__file__).parents[3]
            / "src"
            / "pip_project_template"
            / "cli"
            / "_GlobalArgumentParser.py"
        )
        assert src_file.exists(), f"Source file {src_file} does not exist"
        assert src_file.is_file(), f"Source path {src_file} is not a file"

    def test_get_command_parsers(self):
        """Test command parser discovery."""
        parsers, descriptions = GlobalArgumentParser.get_command_parsers()

        # Should discover parsers from CLI modules
        assert isinstance(parsers, dict)
        assert isinstance(descriptions, dict)

        # Should have at least some parsers from our CLI modules
        expected_commands = ["calculate", "info", "serve01", "serve02"]
        for command in expected_commands:
            assert (
                command in parsers
            ), f"Expected command '{command}' not found in parsers"

    def test_get_main_parser(self):
        """Test main parser creation."""
        parser, subparsers_dict = GlobalArgumentParser.get_main_parser()

        # Should return an ArgumentParser and dict
        assert hasattr(parser, "parse_args")  # ArgumentParser interface
        assert isinstance(subparsers_dict, dict)

    def test_get_command_parsers_exception_handling(self, tmp_path):
        """A module that fails to import is skipped; a good one is loaded.

        Uses a REAL package on disk instead of patching pkgutil / importlib /
        hasattr: real discovery, a real ImportError, real underscore-to-hyphen
        naming. The mocked version this replaces asserted against fakes and had
        stopped exercising anything -- it returned an empty dict and failed.
        """
        pkg = tmp_path / "fake_cli_pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "good_module.py").write_text(
            "import argparse\n"
            "def create_parser():\n"
            "    return argparse.ArgumentParser(description='Test parser')\n"
        )
        (pkg / "bad_module.py").write_text("raise ImportError('Module not found')\n")

        sys.path.insert(0, str(tmp_path))
        try:
            parsers, descriptions = GlobalArgumentParser.get_command_parsers(
                package_path=str(pkg), package_name="fake_cli_pkg"
            )
        finally:
            sys.path.remove(str(tmp_path))

        assert "good-module" in parsers
        assert "bad-module" not in parsers

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
