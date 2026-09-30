"""New research workspaces use hidden package resources without losing edits."""


import pytest

from scitex_template._project._customize import (
    customize_minimal_template,
    customize_template,
)
from scitex_template._project._scholar_writer_integration import (
    setup_scholar_writer_integration,
)


@pytest.mark.parametrize("customize", [customize_template, customize_minimal_template])
def test_hidden_manuscript_takes_precedence_over_legacy(tmp_path, customize):
    hidden = tmp_path / ".scitex/writer/00_shared"
    legacy = tmp_path / "scitex/writer/00_shared"
    for directory in (hidden, legacy):
        directory.mkdir(parents=True)
        (directory / "title.tex").write_text("Original title")
        (directory / "authors.tex").write_text("Original author")
    customize(str(tmp_path), {"name": "New Study", "owner_full_name": "Researcher"})
    assert "New Study" in (hidden / "title.tex").read_text()
    assert "Researcher" in (hidden / "authors.tex").read_text()
    assert (legacy / "title.tex").read_text() == "Original title"
    assert (legacy / "authors.tex").read_text() == "Original author"


@pytest.mark.parametrize("writer", [".scitex/writer/00_shared", "00_shared"])
def test_bibliography_is_shared_under_hidden_scholar(tmp_path, writer):
    bibliography = tmp_path / writer / "bib_files"
    bibliography.mkdir(parents=True)
    result = setup_scholar_writer_integration(tmp_path)
    assert result["success"]
    link = bibliography / "merged_scholar.bib"
    source = tmp_path / ".scitex/scholar/bib_files/merged_scholar.bib"
    assert link.is_symlink()
    assert not link.readlink().is_absolute()
    assert link.resolve() == source.resolve()
    source.write_text("Researcher's bibliography")
    assert link.read_text() == "Researcher's bibliography"
    assert not (tmp_path / "scitex").exists()
    setup_scholar_writer_integration(tmp_path)
    assert source.read_text() == "Researcher's bibliography"


def test_integration_preserves_existing_manuscript_bibliography(tmp_path):
    bibliography = tmp_path / ".scitex/writer/00_shared/bib_files"
    bibliography.mkdir(parents=True)
    existing = bibliography / "merged_scholar.bib"
    existing.write_text("Manually curated entries")
    assert setup_scholar_writer_integration(tmp_path)["success"]
    assert existing.read_text() == "Manually curated entries"
    assert not existing.is_symlink()
