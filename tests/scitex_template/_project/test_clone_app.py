"""Execute generated app imports against the physical SDK App implementation."""
from __future__ import annotations

import importlib
import json
import sys

import pytest

from scitex_template._project.clone_app import clone_app

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10: supplied by the required Dev dependency.
    import tomli as tomllib


@pytest.fixture
def generated_app(tmp_path):
    root = tmp_path / "sdk_consumer_probe"
    if not clone_app(str(root), git_strategy=None):
        pytest.fail("The actual app scaffold failed")
    sys.path.insert(0, str(root / "src"))
    try:
        yield root
    finally:
        sys.path.remove(str(root / "src"))
        for name in list(sys.modules):
            if name == "sdk_consumer_probe" or name.startswith("sdk_consumer_probe."):
                del sys.modules[name]


def test_generated_app_uses_the_real_sdk_config(generated_app):
    # Arrange
    from scitex_sdk.app._django import ScitexAppConfig

    # Act
    generated = importlib.import_module("sdk_consumer_probe._django.apps")
    # Assert
    assert issubclass(generated.SdkConsumerProbeConfig, ScitexAppConfig)


def test_generated_app_declares_the_owning_distribution(generated_app):
    # Arrange
    metadata = tomllib.loads((generated_app / "pyproject.toml").read_text())
    # Act
    dependencies = metadata["project"]["dependencies"]
    # Assert
    assert dependencies == ["scitex-sdk>=0.3.0"]


def test_generated_manifest_is_parseable_with_the_bridge_contract(generated_app):
    # Arrange
    path = generated_app / "src/sdk_consumer_probe/_django/manifest.json"
    # Act
    manifest = json.loads(path.read_text())
    # Assert
    assert manifest["bridge"] == {"entry": "src/bridge/bridge-init.ts", "source_root": "src"}


def test_generated_editor_ping_returns_a_json_serializable_result(generated_app):
    # Arrange
    editor = importlib.import_module("sdk_consumer_probe._editor").Editor()
    # Act
    result = json.loads(json.dumps(editor.ping()))
    # Assert
    assert result == {"status": "ok"}
