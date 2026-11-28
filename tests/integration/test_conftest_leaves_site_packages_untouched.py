"""Regression test: importing tests/conftest.py must not touch site-packages.

Subprocess coverage is configured declaratively in pyproject.toml via
coverage.py's subprocess patch, so collecting tests must neither install
.pth files nor overwrite caller-owned coverage environment variables.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path


def test_conftest_leaves_site_packages_untouched():
    # Arrange
    conftest = Path(__file__).resolve().parents[1] / "conftest.py"
    code = textwrap.dedent(
        """\
        import os
        import runpy
        import site
        import sys


        def snapshot():
            snap = {}
            dirs = list(site.getsitepackages())
            try:
                dirs.append(site.getusersitepackages())
            except Exception:
                pass
            for d in dirs:
                try:
                    snap[d] = sorted(os.listdir(d))
                except OSError:
                    snap[d] = []
            return snap


        os.environ["COVERAGE_PROCESS_START"] = "SENTINEL_PROCESS_START"
        os.environ["COVERAGE_FILE"] = "SENTINEL_COVERAGE_FILE"
        before = snapshot()
        runpy.run_path(sys.argv[1], run_name="conftest_under_test")
        after = snapshot()
        assert before == after, "conftest.py modified site-packages directories"
        assert os.environ["COVERAGE_PROCESS_START"] == "SENTINEL_PROCESS_START"
        assert os.environ["COVERAGE_FILE"] == "SENTINEL_COVERAGE_FILE"
        """
    )

    # Act
    result = subprocess.run(
        [sys.executable, "-c", code, str(conftest)],
        capture_output=True,
        text=True,
    )

    # Assert
    assert result.returncode == 0, result.stderr
