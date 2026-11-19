"""Shared helpers for the MNIST showcase tests."""

import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = PROJECT_ROOT / "scripts" / "mnist"


def load_script(name):
    """Import scripts/mnist/<name>.py as a module (names start with digits)."""
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"mnist_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT
