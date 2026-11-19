"""The whole showcase, run for real in a copy of this project.

Opt-in, because it needs a provenance store you are willing to write to,
the network once (MNIST, writer workspace) and a LaTeX toolchain:

    SCITEX_TEMPLATE_E2E_DSN='postgresql://<user>@/<empty db>?host=<dir>&port=<p>' \\
        python -m pytest tests/scripts/mnist/test_pipeline_end_to_end.py

It runs `make all` (fetch ... live paper, then `clew verify --strict`) and
`make demo-fault` (the planted fault must be caught and the restore must be
byte-identical). The subprocess gets an explicit, minimal environment.
"""

import os
import shutil
import subprocess

import pytest
from conftest import PROJECT_ROOT

DSN = os.environ.get("SCITEX_TEMPLATE_E2E_DSN")
COPY_IGNORE = shutil.ignore_patterns(
    "*_out", "__pycache__", ".scitex", "data", ".git", "*.sif"
)
pytestmark = pytest.mark.skipif(
    not DSN, reason="set SCITEX_TEMPLATE_E2E_DSN to an empty store to run the showcase"
)


def make_env():
    keep = ("PATH", "HOME", "LANG", "TMPDIR", "SSL_CERT_FILE")
    env = {k: os.environ[k] for k in keep if k in os.environ}
    env["SCITEX_STORE_DSN"] = DSN
    return env


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    root = tmp_path_factory.mktemp("showcase") / "project"
    shutil.copytree(PROJECT_ROOT, root, ignore=COPY_IGNORE, symlinks=True)
    # the committed bibliography (the one online step's output) travels along
    literature = PROJECT_ROOT / "scripts/mnist/00_resolve_references_out"
    shutil.copytree(literature, root / literature.relative_to(PROJECT_ROOT))
    shutil.copytree(
        PROJECT_ROOT / "data/literature", root / "data/literature", symlinks=True
    )
    return root


@pytest.fixture(scope="module")
def make_all(project):
    return subprocess.run(
        ["make", "PYTHON=python", "all"],
        cwd=project,
        env=make_env(),
        capture_output=True, check=False,
        text=True,
    )


@pytest.fixture(scope="module")
def demo_fault(project, make_all):
    return subprocess.run(
        ["make", "PYTHON=python", "demo-fault"],
        cwd=project,
        env=make_env(),
        capture_output=True, check=False,
        text=True,
    )


def test_make_all_runs_every_step_and_verifies(make_all):
    # Arrange: `make all` ran in the fixture
    # Act
    code = make_all.returncode
    # Assert
    assert code == 0, make_all.stdout[-3_000:] + make_all.stderr[-3_000:]


def test_make_all_renders_the_live_paper(project, make_all):
    # Arrange
    site = project / "data/live_paper/site/index.html"
    # Act
    exists = site.is_file()
    # Assert
    assert exists


def test_demo_fault_catches_the_fault_and_restores_byte_identical(demo_fault):
    # Arrange: `make demo-fault` ran in the fixture
    # Act
    code = demo_fault.returncode
    # Assert
    assert code == 0, demo_fault.stdout[-3_000:] + demo_fault.stderr[-3_000:]
