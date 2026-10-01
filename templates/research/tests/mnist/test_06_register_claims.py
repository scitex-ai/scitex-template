"""A missing measurement must never produce a successful synthetic claim."""

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def stage(tmp_path):
    script = Path(__file__).resolve().parents[2] / "scripts/mnist/06_register_claims.py"
    spec = importlib.util.spec_from_file_location("register_mnist_claims", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.METRICS_JSON = tmp_path / "metrics.json"
    module.CLAIMS = tmp_path / "claims.json"
    return module


def test_missing_measurements_do_not_create_claims(stage):
    with pytest.raises(FileNotFoundError, match="Run stage 04 first"):
        stage._read_real_metrics()
    assert not stage.CLAIMS.exists()
    assert not stage.METRICS_JSON.exists()


@pytest.mark.parametrize(
    "accuracy", [True, "0.9", -0.1, 1.1, float("nan"), float("inf")]
)
def test_invalid_measurements_stop_claim_registration(stage, accuracy):
    stage.METRICS_JSON.write_text(json.dumps({"accuracy": accuracy, "macro_f1": 0.8}))
    with pytest.raises(ValueError):
        stage._read_real_metrics()
    assert not stage.CLAIMS.exists()


def test_measured_values_are_read_without_replacing_source(stage):
    measured = {"accuracy": 0.812345, "macro_f1": 0.765432}
    original = json.dumps(measured)
    stage.METRICS_JSON.write_text(original)
    assert stage._read_real_metrics() == measured
    assert stage.METRICS_JSON.read_text() == original
