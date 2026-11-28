"""A fresh research workspace contains one editable, versioned manuscript."""

from pathlib import Path
from shutil import copytree
from types import SimpleNamespace

import sys

from scitex_template.research_writer import initialize_research_writer


def test_research_writer_preserves_edits_and_resolves_inputs(tmp_path, monkeypatch):
    # Arrange
    project = tmp_path / "project"
    template = Path(__file__).resolve().parents[2] / "templates" / "research"
    copytree(template, project, symlinks=True)
    seed = tmp_path / "seed"
    (seed / "00_shared/bib_files").mkdir(parents=True)
    figs = Path("01_manuscript/contents/figures/caption_and_media")
    (seed / figs).mkdir(parents=True)
    (seed / "compile.sh").write_text("# runtime")
    rel = Path("01_manuscript/contents/abstract.tex")
    (seed / rel).write_text("generic sample")
    monkeypatch.setitem(
        sys.modules,
        "scitex_writer",
        SimpleNamespace(ensure_workspace=lambda *a, **kw: seed),
    )
    source = project / "manuscript" / rel
    original = source.read_text()

    # Act
    ws = initialize_research_writer(project)
    initial = (ws / rel).read_text()
    (ws / rel).write_text("Edited in Writer")
    initialize_research_writer(project)

    # Assert
    assert (
        initial,
        source.read_text(),
        (ws / figs / "01_mnist_overview.png").resolve(),
    ) == (original, "Edited in Writer", project / "data/figures/fig1_mnist.png")
