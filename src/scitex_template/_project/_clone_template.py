#!/usr/bin/env python3
# Timestamp: 2026-02-08
# File: src/scitex/template/_project/_clone_template.py

"""
Unified template cloning dispatcher.

Single entry point for all template cloning operations.
Django, MCP, and CLI all delegate to this function.
"""

from __future__ import annotations

import traceback
from typing import Any, Optional

from ._clone_outcome import CloneOutcome
from .clone_app import clone_app
from .clone_module import clone_module
from .clone_pip_project import clone_pip_project
from .clone_research import clone_research
from .clone_research_minimal import clone_research_minimal
from .clone_scitex_minimal import clone_scitex_minimal
from .clone_singularity import clone_singularity
from .clone_writer_directory import clone_writer_directory

TEMPLATES = {
    "research": clone_research,
    "research_minimal": clone_research_minimal,
    "scitex_minimal": clone_scitex_minimal,
    "pip_project": clone_pip_project,
    "singularity": clone_singularity,
    "paper_directory": clone_writer_directory,
    "module": clone_module,
    "scitex_app": clone_app,
}

ALIASES = {
    "minimal": "scitex_minimal",
    "pip-project": "pip_project",
    "paper": "paper_directory",
    "stx-module": "module",
    "app": "scitex_app",
}


def clone_template(
    template_id: str,
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs: Any,
) -> bool:
    """
    Clone a project template by ID.

    Unified dispatcher that resolves template IDs (including aliases)
    and delegates to the appropriate clone function.

    Parameters
    ----------
    template_id : str
        Template identifier. Canonical IDs: research, research_minimal,
        scitex_minimal, pip_project, singularity, paper_directory,
        module, scitex_app.
        Aliases: minimal (->scitex_minimal), pip-project, paper,
        stx-module, app (->scitex_app).
    project_dir : str
        Path to project directory (will be created).
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', 'origin', None).
    branch : str, optional
        Specific branch to clone.
    tag : str, optional
        Specific tag to clone.
    **kwargs
        Additional keyword arguments forwarded to the clone function
        (e.g. ``include_dirs`` for research_minimal).

    Returns
    -------
    bool
        True if successful, False otherwise.

    Raises
    ------
    ValueError
        If template_id is unknown.
    """
    _resolved_id, func = _resolve_template(template_id)
    return func(
        project_dir=project_dir,
        git_strategy=git_strategy,
        branch=branch,
        tag=tag,
        **kwargs,
    )


def _resolve_template(template_id: str):
    """Resolve an id (or alias) to ``(canonical_id, clone_function)``.

    Shared by both entry points so the alias table cannot drift between them.
    """
    resolved_id = ALIASES.get(template_id, template_id)
    func = TEMPLATES.get(resolved_id)
    if not func:
        raise ValueError(
            f"Unknown template: {template_id}. Available: {list(TEMPLATES)}"
        )
    return resolved_id, func


def clone_template_result(
    template_id: str,
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs: Any,
) -> CloneOutcome:
    """Clone a template and report WHY if it did not work.

    Same dispatch as :func:`clone_template`; the difference is the answer. This
    returns a :class:`CloneOutcome` carrying ``status`` / ``template_id`` /
    ``project_dir`` / ``reason`` / ``detail`` instead of a bare bool, so a caller
    can put the actual cause in front of an operator.

    That is not hypothetical. scitex-hub wrote this function's bool straight into
    ``VisitorAllocation.quarantine_reason``, so 14 dead visitor slots were
    explained for five days as "Template clone returned falsy for
    default-project" — a sentence with no possible follow-up. See
    ``_clone_outcome.py`` for the full account.

    :func:`clone_template` is UNCHANGED and still returns ``bool``: it is a
    published contract with live callers, and a contract change is a migration,
    not a rename. Prefer this function in new code.

    Notes
    -----
    Exception policy differs DELIBERATELY. ``clone_template`` lets a template's
    exception propagate; callers such as hub's workspace reset catch it and
    report it separately. This function converts an exception into a ``failed``
    outcome carrying the type, message and traceback — because its whole purpose
    is that the caller never has to reconstruct the cause. An unknown
    ``template_id`` still RAISES ``ValueError`` in both: that is a programming
    error in the caller, not a clone that failed.
    """
    resolved_id, func = _resolve_template(template_id)

    try:
        raw = func(
            project_dir=project_dir,
            git_strategy=git_strategy,
            branch=branch,
            tag=tag,
            **kwargs,
        )
    except Exception as exc:
        return CloneOutcome.failed(
            template_id=resolved_id,
            project_dir=project_dir,
            reason=f"{type(exc).__name__}: {exc}",
            detail=traceback.format_exc(),
        )

    # A template that already speaks the richer contract passes straight through.
    if isinstance(raw, CloneOutcome):
        return raw

    if raw:
        return CloneOutcome.cloned(
            template_id=resolved_id, project_dir=project_dir
        )

    # Falsy from a bool-returning template. The cause was discarded one frame
    # below, so it genuinely is not available here — but "unknown" must be
    # REPORTED, not left absent. An empty reason reaches an operator as a dead
    # end (scitex-hub quarantined 16 visitor slots with one on 2026-08-28), so
    # say what IS known: which template, and that it returned falsy without
    # raising. `ok`/`status` still carry the three-valued signal; this only
    # stops the human-facing field being blank.
    return CloneOutcome.failed(
        template_id=resolved_id,
        project_dir=project_dir,
        reason=(
            f"template {resolved_id!r} returned falsy without raising, so it "
            f"reported no cause; its clone function still returns a bare bool "
            f"and discards the reason. Check that template's logs for the "
            f"underlying error."
        ),
    )


def get_template_ids():
    """Return list of all canonical template IDs."""
    return list(TEMPLATES.keys())


def get_all_template_ids():
    """Return list of all template IDs including aliases."""
    return list(TEMPLATES.keys()) + list(ALIASES.keys())


__all__ = [
    "clone_template",
    "clone_template_result",
    "CloneOutcome",
    "TEMPLATES",
    "ALIASES",
    "get_template_ids",
    "get_all_template_ids",
]

# EOF
