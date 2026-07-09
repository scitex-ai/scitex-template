#!/usr/bin/env python3
# File: tests/scitex_template/_project/test__clone_scitex_minimal.py

"""Regression tests for clone_scitex_minimal's scholar import.

Guards the 2026-07-09 visitor-slot outage: clone_scitex_minimal did
``from scitex_scholar import ensure_workspace as ensure_scholar``. On
scitex-scholar >=1.4 the top-level name ``scitex_scholar.ensure_workspace``
resolves to the SUBMODULE (a module object, not callable), so calling it
raised "'module' object is not callable" — which clone_scitex_minimal
swallows into a falsy return, quarantining every SciTeX-Hub visitor slot.
The callable lives at ``scitex_scholar.ensure_workspace.ensure_workspace``.

No mocks (PA-306): the source-inspection tests read real source, the
callable test imports the real package.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

from scitex_template._project import clone_scitex_minimal


def _scholar_import_statements():
    """Actual ``from scitex_scholar...`` import lines (excludes comments/prose)."""
    src = inspect.getsource(clone_scitex_minimal)
    return [
        line.strip()
        for line in src.splitlines()
        if line.lstrip().startswith("from scitex_scholar")
    ]


def test_scholar_import_uses_submodule_form():
    # Arrange
    import_lines = _scholar_import_statements()
    # Act
    uses_submodule = any(
        line.startswith("from scitex_scholar.ensure_workspace import")
        for line in import_lines
    )
    # Assert
    assert uses_submodule, (
        "clone_scitex_minimal must import ensure_workspace from the "
        "scitex_scholar.ensure_workspace submodule (the callable's real home)"
    )


def test_scholar_import_avoids_toplevel_form():
    # Arrange
    import_lines = _scholar_import_statements()
    # Act
    uses_bare_toplevel = any(
        line.startswith("from scitex_scholar import ensure_workspace")
        for line in import_lines
    )
    # Assert
    assert not uses_bare_toplevel, (
        "the bare top-level import binds the submodule (not callable) on "
        "scholar >=1.4 and re-breaks visitor-slot cloning"
    )


@pytest.fixture
def scholar_ensure_module():
    """The scitex_scholar.ensure_workspace submodule, or skip if absent."""
    try:
        return importlib.import_module("scitex_scholar.ensure_workspace")
    except Exception as exc:  # pragma: no cover - env without scholar
        pytest.skip(f"scitex_scholar not importable: {exc}")


def test_scholar_submodule_exposes_callable(scholar_ensure_module):
    # Arrange
    fn = getattr(scholar_ensure_module, "ensure_workspace", None)
    # Act
    fn_is_callable = callable(fn)
    # Assert
    assert fn_is_callable, (
        "scitex_scholar.ensure_workspace.ensure_workspace must be a callable "
        "for clone_scitex_minimal to scaffold the scholar workspace"
    )
