#!/usr/bin/env python3
# Timestamp: 2026-07-08
# File: tests/scitex_template/_project/test_clone_scitex_minimal.py

"""Regression tests for ``clone_scitex_minimal`` (scholar ensure import).

Production incident (scitex.ai hub, scitex-template 0.6.7): the clone did
``from scitex_scholar import ensure_workspace`` — but no released
scitex-scholar (1.2.4 / 1.3.1 / 1.4.x) re-exports ``ensure_workspace`` at
top level, so the import bound the SUBMODULE
``scitex_scholar.ensure_workspace``; calling it raised
``TypeError: 'module' object is not callable``, the blanket except returned
``False``, and every visitor slot was quarantined ("Template clone
returned falsy").

PA-306 no-mocks: no ``unittest.mock`` / ``monkeypatch``. The documented
seam here is the lazy in-function import, so the fakes are hand-rolled
``ModuleType`` instances installed into ``sys.modules`` (save/restore in
``finally``), mirroring the REAL package layout: scitex_writer exports a
top-level ``ensure_workspace`` FUNCTION; scitex_scholar only ships an
``ensure_workspace`` SUBMODULE whose inner ``ensure_workspace`` is the
callable.
"""

from __future__ import annotations

import inspect
import logging
import sys
import types
from typing import Any, Dict, List, Tuple

import pytest

from scitex_template._project.clone_scitex_minimal import clone_scitex_minimal

_MISSING = object()

_FAKED_MODULES = (
    "scitex_writer",
    "scitex_scholar",
    "scitex_scholar.ensure_workspace",
)


# ---------------------------------------------------------------------------
# Hand-rolled fake package layout (mirrors released scholar/writer wheels)
# ---------------------------------------------------------------------------


def _install_fake_packages(
    writer_raises: Exception | None = None,
) -> Tuple[Dict[str, Any], List[str], List[Dict[str, Any]]]:
    """Install fake scitex_writer / scitex_scholar into ``sys.modules``.

    Returns ``(saved_modules, scholar_calls, writer_calls)``. Caller must
    pass ``saved_modules`` to :func:`_restore_modules` in a ``finally``.
    """
    saved = {name: sys.modules.get(name, _MISSING) for name in _FAKED_MODULES}

    scholar_calls: List[str] = []
    writer_calls: List[Dict[str, Any]] = []

    # scitex_writer: ensure_workspace IS a top-level function export.
    fake_writer = types.ModuleType("scitex_writer")

    def _writer_ensure_workspace(project_dir, **kwargs):
        if writer_raises is not None:
            raise writer_raises
        writer_calls.append({"project_dir": project_dir, **kwargs})
        return project_dir

    fake_writer.ensure_workspace = _writer_ensure_workspace

    # scitex_scholar: NO top-level ensure_workspace attribute — only the
    # SUBMODULE scitex_scholar.ensure_workspace with the inner function.
    # This is exactly the layout that broke 0.6.7.
    fake_scholar = types.ModuleType("scitex_scholar")
    fake_scholar.__path__ = []  # mark as package so submodule import works
    fake_scholar_ew = types.ModuleType("scitex_scholar.ensure_workspace")

    def _scholar_ensure_workspace(project_dir):
        scholar_calls.append(project_dir)
        return project_dir

    fake_scholar_ew.ensure_workspace = _scholar_ensure_workspace

    sys.modules["scitex_writer"] = fake_writer
    sys.modules["scitex_scholar"] = fake_scholar
    sys.modules["scitex_scholar.ensure_workspace"] = fake_scholar_ew

    return saved, scholar_calls, writer_calls


def _restore_modules(saved: Dict[str, Any]) -> None:
    for name, module in saved.items():
        if module is _MISSING:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module


# ---------------------------------------------------------------------------
# Shared fixtures — run the clone once per scenario, one assert per test
# ---------------------------------------------------------------------------


@pytest.fixture
def clone_outcome(tmp_path) -> Dict[str, Any]:
    """Run clone_scitex_minimal with default args against the fake layout."""
    project_dir = tmp_path / "proj"
    saved, scholar_calls, writer_calls = _install_fake_packages()
    try:
        result = clone_scitex_minimal(str(project_dir))
    finally:
        _restore_modules(saved)
    return {
        "result": result,
        "project_dir": project_dir,
        "scholar_calls": scholar_calls,
        "writer_calls": writer_calls,
    }


@pytest.fixture
def clone_kwargs_outcome(tmp_path) -> Dict[str, Any]:
    """Run clone_scitex_minimal with explicit git/branch/extra kwargs."""
    project_dir = tmp_path / "proj"
    saved, scholar_calls, writer_calls = _install_fake_packages()
    try:
        result = clone_scitex_minimal(
            str(project_dir),
            git_strategy="parent",
            branch="develop",
            tag=None,
            extra_kwarg="forwarded",
        )
    finally:
        _restore_modules(saved)
    return {
        "result": result,
        "project_dir": project_dir,
        "scholar_calls": scholar_calls,
        "writer_calls": writer_calls,
    }


@pytest.fixture
def clone_failure_outcome(tmp_path, caplog) -> Dict[str, Any]:
    """Run clone_scitex_minimal with a writer that raises RuntimeError."""
    project_dir = tmp_path / "proj"
    saved, scholar_calls, writer_calls = _install_fake_packages(
        writer_raises=RuntimeError("boom-from-writer")
    )
    try:
        with caplog.at_level(
            logging.ERROR,
            logger="scitex_template._project.clone_scitex_minimal",
        ):
            result = clone_scitex_minimal(str(project_dir))
    finally:
        _restore_modules(saved)
    error_records = [
        record
        for record in caplog.records
        if "Failed to create scitex_minimal project" in record.message
    ]
    return {
        "result": result,
        "error_records": error_records,
        "caplog_text": caplog.text,
    }


# ---------------------------------------------------------------------------
# Regression: imported ensure callables must be FUNCTIONS, not modules
# ---------------------------------------------------------------------------


class TestEnsureImportsAreCallableFunctions:
    """Would have caught the 0.6.7 module-not-callable bug on its own."""

    def test_scholar_inner_ensure_workspace_is_a_function(self):
        # Arrange
        pytest.importorskip("scitex_scholar")
        # Act
        from scitex_scholar.ensure_workspace import (
            ensure_workspace as ensure_scholar,
        )

        # Assert
        assert inspect.isfunction(ensure_scholar)

    def test_writer_top_level_ensure_workspace_is_a_function(self):
        # Arrange
        pytest.importorskip("scitex_writer")
        # Act
        from scitex_writer import ensure_workspace as ensure_writer

        # Assert
        assert inspect.isfunction(ensure_writer)


# ---------------------------------------------------------------------------
# clone_scitex_minimal against the fake released-package layout
# ---------------------------------------------------------------------------


class TestCloneScitexMinimalWithReleasedLayout:
    """0.6.7 returned False against this exact layout; 0.6.8 must not."""

    def test_clone_returns_true(self, clone_outcome):
        # Arrange
        outcome = clone_outcome
        # Act
        result = outcome["result"]
        # Assert
        assert result is True

    def test_clone_creates_project_directory(self, clone_outcome):
        # Arrange
        outcome = clone_outcome
        # Act
        project_dir = outcome["project_dir"]
        # Assert
        assert project_dir.is_dir()

    def test_clone_calls_scholar_ensure_with_project_dir(self, clone_outcome):
        # Arrange
        outcome = clone_outcome
        # Act
        scholar_calls = outcome["scholar_calls"]
        # Assert
        assert scholar_calls == [str(outcome["project_dir"])]

    def test_clone_calls_writer_ensure_with_project_dir(self, clone_outcome):
        # Arrange
        outcome = clone_outcome
        # Act
        writer_calls = outcome["writer_calls"]
        # Assert
        assert writer_calls[0]["project_dir"] == str(outcome["project_dir"])

    def test_clone_passes_default_child_git_strategy_to_writer(
        self, clone_outcome
    ):
        # Arrange
        outcome = clone_outcome
        # Act
        writer_calls = outcome["writer_calls"]
        # Assert
        assert writer_calls[0]["git_strategy"] == "child"

    def test_clone_forwards_git_strategy_to_writer(self, clone_kwargs_outcome):
        # Arrange
        outcome = clone_kwargs_outcome
        # Act
        writer_calls = outcome["writer_calls"]
        # Assert
        assert writer_calls[0]["git_strategy"] == "parent"

    def test_clone_forwards_branch_to_writer(self, clone_kwargs_outcome):
        # Arrange
        outcome = clone_kwargs_outcome
        # Act
        writer_calls = outcome["writer_calls"]
        # Assert
        assert writer_calls[0]["branch"] == "develop"

    def test_clone_forwards_extra_kwargs_to_writer(self, clone_kwargs_outcome):
        # Arrange
        outcome = clone_kwargs_outcome
        # Act
        writer_calls = outcome["writer_calls"]
        # Assert
        assert writer_calls[0]["extra_kwarg"] == "forwarded"


# ---------------------------------------------------------------------------
# Failure path: bool contract kept, traceback preserved in the log
# ---------------------------------------------------------------------------


class TestCloneScitexMinimalFailureLogging:
    """The hub surfaces this log as quarantine_reason; a bare str(e)
    (0.6.7 behaviour) hid the real cause. The traceback must be logged."""

    def test_failure_is_falsy(self, clone_failure_outcome):
        # Arrange
        outcome = clone_failure_outcome

        # Act
        result = outcome["result"]

        # Assert -- falsy, not `is False`. The template now returns a
        # CloneOutcome so the cause survives the return; __bool__ mirrors .ok,
        # so every `if clone_scitex_minimal(...):` caller is unaffected.
        assert not result

    def test_failure_carries_the_cause(self, clone_failure_outcome):
        # Arrange
        outcome = clone_failure_outcome

        # Act
        result = outcome["result"]

        # Assert -- the whole point: production saw reason=None and
        # quarantined 16 visitor slots with no explanation.
        assert result.reason
        assert "boom-from-writer" in result.reason

    def test_failure_logs_exactly_one_error_record(
        self, clone_failure_outcome
    ):
        # Arrange
        outcome = clone_failure_outcome
        # Act
        error_records = outcome["error_records"]
        # Assert
        assert len(error_records) == 1

    def test_failure_log_message_contains_cause(self, clone_failure_outcome):
        # Arrange
        outcome = clone_failure_outcome
        # Act
        message = outcome["error_records"][0].message
        # Assert
        assert "boom-from-writer" in message

    def test_failure_log_record_carries_exc_info(self, clone_failure_outcome):
        # Arrange
        outcome = clone_failure_outcome
        # Act
        record = outcome["error_records"][0]
        # Assert
        assert record.exc_info is not None

    def test_failure_log_text_contains_traceback_type(
        self, clone_failure_outcome
    ):
        # Arrange
        outcome = clone_failure_outcome
        # Act
        caplog_text = outcome["caplog_text"]
        # Assert
        assert "RuntimeError" in caplog_text

# EOF
