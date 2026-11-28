#!/usr/bin/env python3
"""The research template ships its manuscript where scitex-writer looks.

scitex-writer (and the SciTeX Hub's Writer app) resolve a project's writer
workspace at ``<project>/.scitex/writer``. The research template used to keep
the text in ``manuscript/`` and copy it into a generated workspace on every
``make paper-init``, so the Hub found no workspace (HTTP 404) and every
re-initialisation overwrote edits made in the editor. These tests pin the
layout that removes both failures: one committed copy of the text in the
workspace, no engine shipped, and links into ``data/`` that are relative.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from scitex_template import customize_template

RESEARCH = Path(__file__).resolve().parents[2] / "templates" / "research"
WORKSPACE = RESEARCH / ".scitex" / "writer"
FIGURE_LINK = (
    WORKSPACE / "01_manuscript/contents/figures/caption_and_media/01_mnist_overview.png"
)
BIB_LINK = WORKSPACE / "00_shared/bib_files/references.bib"


def _ignored(relpath: str) -> bool:
    """git's own verdict on the research .gitignore, independent of the index."""
    result = subprocess.run(
        ["git", "-C", str(RESEARCH), "check-ignore", "--no-index", "-q", relpath],
        capture_output=True,
    )
    return result.returncode == 0


def test_the_manuscript_text_is_a_real_file_in_the_writer_workspace():
    # Arrange
    results = WORKSPACE / "01_manuscript" / "contents" / "results.tex"
    # Act
    is_real_file = results.is_file() and not results.is_symlink()
    # Assert
    assert is_real_file


def test_the_workspace_itself_is_a_real_directory():
    # Arrange
    # (the template tree under test)
    # Act
    is_real_dir = WORKSPACE.is_dir() and not WORKSPACE.is_symlink()
    # Assert
    assert is_real_dir


def test_manuscript_is_an_alias_of_the_writer_workspace():
    # Arrange
    alias = RESEARCH / "manuscript"
    # Act
    target = os.readlink(alias)
    # Assert
    assert target == ".scitex/writer"


def test_the_template_ships_no_writer_engine():
    # Arrange
    # (the engine belongs to the installed scitex-writer)
    # Act
    shipped = (WORKSPACE / "scripts").exists() or (WORKSPACE / "compile.sh").exists()
    # Assert
    assert not shipped


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        (FIGURE_LINK, RESEARCH / "data" / "figures" / "fig1_mnist.png"),
        (BIB_LINK, RESEARCH / "data" / "literature" / "references.bib"),
    ],
)
def test_data_links_are_relative_and_point_into_data(link, expected):
    # Arrange
    target = os.readlink(link)
    # Act
    lands = (not os.path.isabs(target), os.path.normpath(link.parent / target))
    # Assert
    assert lands == (True, os.path.normpath(expected))


@pytest.mark.parametrize(
    "relpath",
    [
        ".scitex/writer/00_shared/title.tex",
        ".scitex/writer/00_shared/bib_files/references.bib",
        ".scitex/writer/01_manuscript/contents/results.tex",
        ".scitex/writer/01_manuscript/contents/figures/caption_and_media/01_mnist_overview.tex",
    ],
)
def test_the_manuscript_text_is_not_git_ignored(relpath):
    # Arrange
    # (the research template's own .gitignore)
    # Act
    ignored = _ignored(relpath)
    # Assert
    assert not ignored


@pytest.mark.parametrize(
    "relpath",
    [
        ".scitex/writer/scripts/shell/compile_manuscript.sh",
        ".scitex/writer/01_manuscript/base.tex",
        ".scitex/writer/01_manuscript/manuscript.pdf",
        ".scitex/writer/00_shared/latex_styles/packages.tex",
        ".scitex/writer/01_manuscript/contents/wordcounts/results_count.txt",
    ],
)
def test_the_installed_engine_and_build_outputs_are_git_ignored(relpath):
    # Arrange
    # (paths scitex-writer installs or the compile writes)
    # Act
    ignored = _ignored(relpath)
    # Assert
    assert ignored


def test_customize_template_titles_the_research_manuscript(tmp_path):
    # Arrange
    project = tmp_path / "project"
    shutil.copytree(RESEARCH, project, symlinks=True)
    metadata = {
        "name": "My Study",
        "description": "",
        "owner": "a",
        "owner_full_name": "",
    }
    # Act
    customize_template(str(project), metadata, "research")
    # Assert
    assert "My Study" in (project / ".scitex/writer/00_shared/title.tex").read_text()


# EOF
