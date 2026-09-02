#!/usr/bin/env python3
# Timestamp: 2026-02-17
# File: src/scitex/template/_project/clone_scitex_minimal.py

"""Create a minimal scitex project (writer + scholar).

Composes ensure calls for each module workspace:
- scitex.writer.ensure() -> {project_dir}/scitex/writer/ (full scitex-writer clone)
- scitex.scholar.ensure() -> {project_dir}/scitex/scholar/ (directory scaffold)

Then sets up bibliography sharing between writer and scholar.
"""

from __future__ import annotations

import sys
from pathlib import Path
import traceback
from typing import Optional

from ._clone_outcome import CloneOutcome

import logging

getLogger = logging.getLogger

logger = getLogger(__name__)


def clone_scitex_minimal(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs,
) -> "bool | CloneOutcome":
    """Create a minimal scitex project with writer and scholar workspaces.

    Returns ``True`` on success, and on failure a falsy :class:`CloneOutcome`
    carrying the cause. ``CloneOutcome.__bool__`` mirrors ``.ok``, so legacy
    ``if clone_scitex_minimal(...):`` callers and the CLI exit code are
    unaffected, while ``clone_template_result`` passes the outcome through and
    the operator finally sees WHY.

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created).
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', 'origin', None).
    branch : str, optional
        Specific branch of the writer template to clone.
    tag : str, optional
        Specific tag/release of the writer template to clone.
    **kwargs
        Additional keyword arguments forwarded to writer ensure.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    try:
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        # Ensure writer workspace (full scitex-writer clone).
        # scitex_writer exports ensure_workspace as a top-level FUNCTION.
        from scitex_writer import ensure_workspace as ensure_writer

        ensure_writer(
            str(project_path),
            git_strategy=git_strategy,
            branch=branch,
            tag=tag,
            **kwargs,
        )

        # Ensure scholar workspace (directory scaffold).
        # IMPORTANT: scitex_scholar does NOT re-export ensure_workspace at
        # top level (verified 1.2.4/1.3.1/1.4.x) — ``from scitex_scholar
        # import ensure_workspace`` binds the SUBMODULE, and calling it
        # raised ``TypeError: 'module' object is not callable``, silently
        # failing every scitex_minimal clone. Import the inner callable
        # explicitly from the submodule.
        from scitex_scholar.ensure_workspace import (
            ensure_workspace as ensure_scholar,
        )

        ensure_scholar(str(project_path))

        # Set up bibliography sharing symlink
        from ._scholar_writer_integration import ensure_integration

        ensure_integration(project_path)

        logger.info(f"Created scitex_minimal project at {project_path}")
        return True

    except Exception as e:
        # Carry the cause in the RETURN VALUE, not only in the log.
        #
        # This used to `return False` with a comment claiming it preserved the
        # traceback "for downstream consumers (e.g. hub slot-reset
        # quarantine_reason)". It did not: logger.exception writes to the LOG,
        # while the caller received a bare False. One frame up,
        # clone_template_result saw falsy and could only report reason=None —
        # which is exactly what scitex-hub quarantined 16 visitor slots with on
        # 2026-08-28, and the five-day blindness of 2026-08-06 before that.
        #
        # CloneOutcome is falsy (__bool__ mirrors .ok), so every legacy
        # `if clone_scitex_minimal(...):` caller and the CLI exit code behave
        # exactly as before, while clone_template_result's pass-through branch
        # hands the real cause to the operator.
        logger.exception(f"Failed to create scitex_minimal project: {e}")
        return CloneOutcome.failed(
            template_id="scitex_minimal",
            project_dir=str(project_dir),
            reason=f"{type(e).__name__}: {e}",
            detail=traceback.format_exc(),
        )


def main(args: list = None) -> None:
    """Command-line interface for clone_scitex_minimal."""
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m scitex clone_scitex_minimal <project-dir>")
        print("")
        print("Creates a minimal scitex project with writer + scholar.")
        sys.exit(1)

    success = clone_scitex_minimal(args[0])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
