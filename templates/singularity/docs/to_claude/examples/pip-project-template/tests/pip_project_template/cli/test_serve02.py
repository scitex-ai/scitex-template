#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-27 09:18:52 (ywatanabe)"
# File: /home/ywatanabe/proj/pip-project-template/tests/minimal_pip_project/cli/test_serve02.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./tests/minimal_pip_project/cli/test_serve02.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Test file for src/cli/serve02.py

import contextlib
import sys
from io import StringIO
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

from pip_project_template.cli.serve02 import create_parser, main


class _Recorder:
    """Records calls instead of performing them — a real callable."""

    def __init__(self):
        self.calls = []

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))


@pytest.fixture
def recorded_run_server():
    """Swap McpServer02.run_server for a _Recorder, then restore it.

    The fixture installs a real callable and removes it again, so the test
    still asserts exactly which kwargs main() forwarded.
    """
    import pip_project_template.mcp_servers.McpServer02 as server_module

    recorder = _Recorder()
    original = server_module.run_server
    server_module.run_server = recorder
    try:
        yield recorder
    finally:
        server_module.run_server = original



class TestServe02:
    """Test suite for cli.serve02"""

    def test_module_imports(self):
        """Test that module imports successfully."""
        import importlib

        module = importlib.import_module("pip_project_template.cli.serve02")
        assert module is not None

    def test_module_has_expected_attributes(self):
        """Test that module has expected structure."""
        import importlib

        module = importlib.import_module("pip_project_template.cli.serve02")

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
        ), f"Module cli.serve02 appears to be empty or malformed"

    def test_module_file_exists(self):
        """Test that the source file exists and is readable."""
        src_file = (
            Path(__file__).parents[3]
            / "src"
            / "pip_project_template"
            / "cli"
            / "serve02.py"
        )
        assert src_file.exists(), f"Source file {src_file} does not exist"
        assert src_file.is_file(), f"Source path {src_file} is not a file"

    def test_create_parser(self):
        """Test serve02 parser creation."""
        parser = create_parser()
        assert parser is not None

        # Test default arguments
        args = parser.parse_args([])
        assert args.port == 8082  # serve02 uses different default port
        assert args.host == "localhost"
        assert args.transport == "stdio"

    def test_main_stdio_transport(self, recorded_run_server):
        """Test main function with stdio transport."""
        with contextlib.redirect_stdout(StringIO()) as captured:
            result = main(["--transport", "stdio"])

        assert result == 0
        assert recorded_run_server.calls == [((), {"transport": "stdio"})]
        output = captured.getvalue()
        assert "Server 02" in output

    def test_main_http_transport(self, recorded_run_server):
        """Test main function with http transport."""
        with contextlib.redirect_stdout(StringIO()) as captured:
            result = main(
                ["--transport", "http", "--host", "test.com", "--port", "9001"]
            )

        assert result == 0
        assert recorded_run_server.calls == [((), {"transport": "http", "host": "test.com", "port": 9001})]
        output = captured.getvalue()
        assert "Server 02" in output
        assert "HTTP" in output

    def test_main_sse_transport(self, recorded_run_server):
        """Test main function with sse transport."""
        with contextlib.redirect_stdout(StringIO()) as captured:
            result = main(["--transport", "sse"])

        assert result == 0
        assert recorded_run_server.calls == [((), {"transport": "sse", "host": "localhost", "port": 8082})]
        output = captured.getvalue()
        assert "Server 02" in output
        assert "SSE" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
