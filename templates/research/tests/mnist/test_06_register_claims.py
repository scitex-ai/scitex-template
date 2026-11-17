"""Stage 06 must never fabricate evidence.

Runs the real scripts as subprocesses in a scratch copy of this project:

* With no stage-04 output, stage 06 fails loudly and writes nothing.
* After a real upstream run (an ``@stx.session`` stage that saves real
  handwritten-digit data via ``stx.io.save``, then the real
  ``04_clf_svm.py``), stage 06 registers its claims through scitex-clew
  with lineage back to the stage-04 run.

Both scenarios record runs in a Clew store, so they require an explicit,
disposable store via ``SCITEX_STORE_DSN`` (never the host's default store).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.skipif(
    not os.environ.get("SCITEX_STORE_DSN"),
    reason="needs a disposable Clew store: set SCITEX_STORE_DSN",
)

# Real data, real session: sklearn's bundled handwritten digits (8x8),
# saved under the PATH.yaml locations that stage 04 loads.
_UPSTREAM_STAGE = """
import scitex as stx
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split


@stx.session
def main(CONFIG=stx.session.INJECTED, logger=stx.session.INJECTED):
    X, y = load_digits(return_X_y=True)
    X = X / 16.0
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=0, stratify=y
    )
    for obj, name in [
        (X_tr, "train_flattened.npy"),
        (X_te, "test_flattened.npy"),
        (y_tr, "train_labels.npy"),
        (y_te, "test_labels.npy"),
    ]:
        stx.io.save(obj, "./data/mnist/" + name, symlink_from_cwd=True)
    return 0


if __name__ == "__main__":
    main()
"""


def _copy_project(dst: Path) -> Path:
    for name in ("config", "scripts"):
        shutil.copytree(
            PROJECT_ROOT / name,
            dst / name,
            ignore=shutil.ignore_patterns("*_out", "__pycache__"),
        )
    (dst / "data").mkdir()
    return dst


def _run(project: Path, script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, script],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )


@pytest.fixture(scope="module")
def missing_upstream(tmp_path_factory):
    """Stage 06 run in a project where stage 04 never ran."""
    project = _copy_project(tmp_path_factory.mktemp("missing") / "proj")
    proc = _run(project, "scripts/mnist/06_register_claims.py")
    return project, proc, proc.stdout + proc.stderr


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory):
    """Real upstream stage -> real 04_clf_svm.py -> 06_register_claims.py."""
    project = _copy_project(tmp_path_factory.mktemp("pipeline") / "proj")
    (project / "scripts/mnist/00_digits_fixture.py").write_text(_UPSTREAM_STAGE)
    procs = {}
    for script in (
        "scripts/mnist/00_digits_fixture.py",
        "scripts/mnist/04_clf_svm.py",
        "scripts/mnist/06_register_claims.py",
    ):
        procs[script] = proc = _run(project, script)
        if proc.returncode != 0:
            pytest.fail(f"{script} failed\n{proc.stdout}\n{proc.stderr}")
    return project, procs["scripts/mnist/06_register_claims.py"]


# Clew scopes records to the project (``.scitex/clew/project-id``), so the
# store is queried from inside the scratch project, as a researcher would.
_CLEW_PROBE = """
import json, sys
from pathlib import Path
import scitex_clew as clew

claims_file = str(Path("data/results/claims.json").resolve())
claims = clew.list_claims(file_path=claims_file)
chain = clew.chain(claims_file)
print(json.dumps({
    "claims": [
        {"value": c.claim_value, "source_file": c.source_file,
         "source_session": c.source_session}
        for c in claims
    ],
    "chain_scripts": [str(getattr(r, "script_path", r)) for r in chain.runs],
}))
"""


@pytest.fixture(scope="module")
def clew_view(pipeline):
    """What the Clew store says about the pipeline's claims.json."""
    project, _ = pipeline
    proc = subprocess.run(
        [sys.executable, "-c", _CLEW_PROBE],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        pytest.fail(f"clew probe failed\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def registered(clew_view):
    return clew_view["claims"]


# --- missing upstream -> loud failure, nothing fabricated -------------------


def test_missing_upstream_exits_nonzero(missing_upstream):
    # Arrange
    _, proc, output = missing_upstream
    # Act
    returncode = proc.returncode
    # Assert
    assert returncode != 0, output


def test_missing_upstream_names_the_missing_file(missing_upstream):
    # Arrange
    _, _, output = missing_upstream
    # Act
    message_found = "Upstream output missing" in output and "metrics.json" in output
    # Assert
    assert message_found, output


def test_missing_upstream_writes_no_claims_file(missing_upstream):
    # Arrange
    project, _, _ = missing_upstream
    # Act
    written = list(project.rglob("claims.json"))
    # Assert
    assert written == []


def test_missing_upstream_writes_no_placeholder_metrics(missing_upstream):
    # Arrange
    project, _, _ = missing_upstream
    # Act
    stray = [p for p in project.rglob("*.json") if "config" not in p.parts]
    # Assert
    assert stray == []


# --- real upstream -> claims registered via clew with lineage ---------------


def test_pipeline_reports_two_claims(pipeline):
    # Arrange
    _, proc = pipeline
    # Act
    stdout = proc.stdout
    # Assert
    assert "DONE n_claims=2" in stdout


def test_pipeline_emits_no_lineage_warning(pipeline):
    # Arrange
    _, proc = pipeline
    # Act
    output = proc.stdout + proc.stderr
    # Assert
    assert "NO_LINEAGE" not in output


def test_claims_json_is_a_stx_io_output_of_stage_06(pipeline):
    # Arrange
    project, _ = pipeline
    # Act
    target = (project / "data/results/claims.json").resolve()
    # Assert
    assert "06_register_claims_out" in target.parts, target


def test_claims_json_answers_equal_stage_04_metrics(pipeline):
    # Arrange
    project, _ = pipeline
    metrics = json.loads((project / "data/mnist/metrics.json").read_text())
    payload = json.loads((project / "data/results/claims.json").read_text())
    # Act
    answers = {c["question"]: c["answer"] for c in payload["claims"]}
    # Assert
    assert answers == {
        "test_accuracy": f"{metrics['accuracy']:.6f}",
        "test_macro_f1": f"{metrics['macro_f1']:.6f}",
    }


def test_clew_store_holds_the_claimed_values(pipeline, registered):
    # Arrange
    project, _ = pipeline
    payload = json.loads((project / "data/results/claims.json").read_text())
    # Act
    stored = sorted(c["value"] for c in registered)
    # Assert
    assert stored == sorted(c["answer"] for c in payload["claims"])


def test_clew_claims_cite_stage_04_metrics_file(pipeline, registered):
    # Arrange
    project, _ = pipeline
    metrics_file = str((project / "data/mnist/metrics.json").resolve())
    # Act
    sources = {c["source_file"] for c in registered}
    # Assert
    assert sources == {metrics_file}


def test_clew_claims_resolve_to_a_recorded_session(registered):
    # Arrange
    claims = registered
    # Act
    sessions = [c["source_session"] for c in claims]
    # Assert
    assert claims and all(sessions), sessions


def test_claims_json_back_traces_to_stage_04(clew_view):
    # Arrange
    runs = clew_view["chain_scripts"]
    # Act
    scripts = " ".join(runs)
    # Assert
    assert "04_clf_svm.py" in scripts and "06_register_claims.py" in scripts, runs
