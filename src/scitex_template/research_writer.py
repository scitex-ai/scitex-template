"""Complete a research template's Writer runtime around its tracked sources."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def _install_missing(source: Path, destination: Path) -> None:
    """Fill missing runtime files without replacing existing entries or following links."""
    for item in source.iterdir():
        if item.name in {".git", ".gitignore"}:
            continue
        target = destination / item.name
        if target.is_symlink():
            continue
        if item.is_symlink():
            if not target.exists():
                target.symlink_to(item.readlink())
        elif item.is_dir():
            if not target.exists():
                target.mkdir(exist_ok=True)
            if target.is_dir():
                _install_missing(item, target)
        elif not target.exists():
            # Source and staging are on the project filesystem. Linking publishes
            # a complete regular file without replacing a user's concurrent edit.
            try:
                os.link(item, target)
            except FileExistsError:
                pass


def initialize_research_writer(project: Path, **writer_options) -> Path:
    """Install the pinned Writer runtime. Manuscript files stay at their Git paths."""
    from scitex_dev import try_import_optional

    writer = try_import_optional("scitex_writer", pkg="scitex-writer")
    if writer is None:
        raise ImportError(
            "Install scitex-template[writer] to initialize the manuscript"
        )

    project = Path(project).resolve()
    workspace = project / ".scitex" / "writer"
    if (project / ".scitex").is_symlink() or workspace.is_symlink():
        raise ValueError("Expected a physical Writer workspace in this project")
    if (
        not (project / "manuscript").is_symlink()
        or (project / "manuscript").resolve() != workspace
    ):
        raise ValueError("Expected the research template's canonical manuscript layout")
    if not workspace.is_dir():
        raise FileNotFoundError(workspace)
    marker = workspace / ".research-runtime-installed"
    if marker.is_file() and (workspace / "compile.sh").is_file():
        return workspace

    with tempfile.TemporaryDirectory(dir=workspace.parent) as scratch:
        seed = Path(
            writer.ensure_workspace(
                Path(scratch), git_strategy="parent", **writer_options
            )
        )
        figures = Path("01_manuscript/contents/figures/caption_and_media")
        tables = Path("01_manuscript/contents/tables/caption_and_media")
        for pattern in (figures / "0[12]_*example*.tex", tables / "01_example_table.*"):
            for example in seed.glob(str(pattern)):
                example.unlink()
        for name, source in (
            (figures / "01_mnist_overview.png", "data/figures/fig1_mnist.png"),
            (
                Path("00_shared/bib_files/references.bib"),
                "data/literature/references.bib",
            ),
        ):
            link = seed / name
            link.unlink(missing_ok=True)
            link.symlink_to(
                os.path.relpath(project / source, (workspace / name).parent)
            )
        _install_missing(seed, workspace)
        # Create the marker last. An interrupted first run can safely retry.
        try:
            marker.touch(exist_ok=False)
        except FileExistsError:
            if marker.is_symlink() or not marker.is_file():
                raise ValueError("Invalid Writer runtime marker")
    return workspace


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    initialize_research_writer(parser.parse_args().project)
