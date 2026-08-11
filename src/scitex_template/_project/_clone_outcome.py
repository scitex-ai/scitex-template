#!/usr/bin/env python3
# Timestamp: 2026-08-11
# File: src/scitex_template/_project/_clone_outcome.py

"""The declared shape a clone answers in.

Every clone function here returns ``bool``. That is enough to decide what to do
and never enough to say WHY — and the difference cost scitex-hub five days.

On 2026-08-06 its visitor pool quarantined 14 of 16 slots. The whole
operator-visible explanation, written verbatim into ``quarantine_reason``, was:

    "reset failed: Template clone returned falsy for default-project"

Nobody could act on that, so nobody did, and every anonymous visitor was funnelled
onto one shared account until 2026-08-11.

The reason existed. ``clone_scitex_minimal`` catches every exception and logs the
traceback, and the comment above that ``except`` even names who needs it:
"preserve the full traceback for downstream consumers (e.g. hub slot-reset
quarantine_reason)". It preserves it to the LOGGER; that consumer reads the RETURN
VALUE. The author knew the consumer and still could not reach it, because ``bool``
has nowhere to put a sentence.

So the fix is not another log line. It is a return type with room for the answer:
one frozen dataclass, each signal its own named field, and a genuinely three-valued
``reason`` where ``None`` means "this template did not say" rather than "fine".

MIGRATION, NOT RENAME. ``clone_template() -> bool`` is published and has live
callers (scitex-hub, the CLI's exit code, and tests asserting ``result is True`` by
identity). It keeps its exact contract. This type is returned by the NEW
``clone_template_result`` beside it, and implements ``__bool__`` so the same object
can be dropped into any legacy ``if success:`` unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

CloneStatus = Literal["cloned", "failed"]


@dataclass(frozen=True)
class CloneOutcome:
    """What happened to one clone attempt, in a shape that can be inspected.

    Attributes
    ----------
    ok : bool
        Whether the template landed. Mirrors the legacy bool exactly.
    status : {"cloned", "failed"}
        The named outcome. Kept alongside ``ok`` so new states (e.g.
        ``already_present``) can be added without re-teaching every caller
        what a bool means.
    template_id : str
        Which template was requested — the resolved id where known.
    project_dir : str
        Where it was being written. Half of any actionable message.
    reason : str, optional
        Short human-readable cause, e.g.
        ``"PermissionError: [Errno 13] Permission denied: '/app/data/...'"``.
        ``None`` means UNKNOWN — the template reported failure without saying
        why. That is deliberately distinguishable from a successful clone
        (which also has no reason) via ``ok``/``status``, and from an empty
        string, which would read like "no problem".
    detail : str, optional
        Full traceback or long-form context, for logs rather than a UI field.
    """

    ok: bool
    status: CloneStatus
    template_id: str
    project_dir: str
    reason: Optional[str] = None
    detail: Optional[str] = None

    @classmethod
    def cloned(cls, *, template_id: str, project_dir: str) -> "CloneOutcome":
        """The template landed."""
        return cls(
            ok=True, status="cloned", template_id=template_id, project_dir=project_dir
        )

    @classmethod
    def failed(
        cls,
        *,
        template_id: str,
        project_dir: str,
        reason: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> "CloneOutcome":
        """It did not land. ``reason=None`` means the template did not say why."""
        return cls(
            ok=False,
            status="failed",
            template_id=template_id,
            project_dir=project_dir,
            reason=reason,
            detail=detail,
        )

    def __bool__(self) -> bool:
        """Legacy protocol: ``if success:`` keeps working against this object."""
        return self.ok

    def describe(self) -> str:
        """One line an operator can act on — or at least act FROM.

        Names the template, the target, and the cause. When the cause is
        unknown it says so out loud rather than going quiet, because a blank
        explanation is what made the original outage unreadable.
        """
        if self.ok:
            return f"cloned template {self.template_id!r} into {self.project_dir}"
        cause = self.reason if self.reason else "unknown (the template reported failure without a reason)"
        return (
            f"failed to clone template {self.template_id!r} into "
            f"{self.project_dir}: {cause}"
        )


__all__ = ["CloneOutcome", "CloneStatus"]

# EOF
