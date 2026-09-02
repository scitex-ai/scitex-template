#!/usr/bin/env python3
"""A failed clone must be able to SAY WHY.

WHY THIS EXISTS — a measured outage, not a hypothetical.

scitex-hub's visitor pool quarantined 14 of its 16 slots on 2026-08-06 and stayed
that way for five days. The entire operator-visible explanation was:

    "reset failed: Template clone returned falsy for default-project"

No follow-up action is available from that sentence. It names no file, no
permission, no missing payload, no version.

The reason was not missing — it was DISCARDED. clone_scitex_minimal catches every
exception and logs the traceback, and the comment above that except block even
names the consumer it is trying to help:

    "preserve the full traceback for downstream consumers
     (e.g. hub slot-reset quarantine_reason)"

But it preserves it to the LOGGER, while that consumer reads the RETURN VALUE. The
author knew exactly who needed the reason and still could not hand it over, because
``-> bool`` has nowhere to put one. That is the defect: not a missing log line, but
a return type too narrow to carry the answer.

Constitution §2: answer in a fixed declared shape, every signal its own named
field, three-valued (true / false / UNKNOWN), and on failure give an actionable
hint naming the offending file, value, or version.

MIGRATION, NOT RENAME. ``clone_template() -> bool`` is a published contract with
live callers (hub, the CLI exit code, and tests asserting ``result is True`` by
identity). It is left exactly as it is; the rich answer arrives beside it.
"""

from __future__ import annotations

import pytest

from scitex_template._project._clone_outcome import CloneOutcome

VISITOR_DIR = "/app/data/users/visitor-001/default-project"
LEGACY_MESSAGE = "Template clone returned falsy for default-project"


def _cloned() -> CloneOutcome:
    return CloneOutcome.cloned(template_id="scitex_minimal", project_dir="/tmp/p")


def _failed(reason: str | None = "PermissionError: [Errno 13] denied") -> CloneOutcome:
    return CloneOutcome.failed(
        template_id="scitex_minimal", project_dir=VISITOR_DIR, reason=reason
    )


class TestSuccessShape:
    def test_cloned_outcome_is_ok(self):
        # Arrange
        template_id = "scitex_minimal"
        # Act
        out = CloneOutcome.cloned(template_id=template_id, project_dir="/tmp/p")
        # Assert
        assert out.ok is True

    def test_cloned_outcome_has_cloned_status(self):
        # Arrange
        template_id = "scitex_minimal"
        # Act
        out = CloneOutcome.cloned(template_id=template_id, project_dir="/tmp/p")
        # Assert
        assert out.status == "cloned"

    def test_cloned_outcome_carries_no_reason(self):
        # Arrange
        template_id = "scitex_minimal"
        # Act
        out = CloneOutcome.cloned(template_id=template_id, project_dir="/tmp/p")
        # Assert
        assert out.reason is None

    def test_cloned_outcome_remembers_the_target_dir(self):
        # Arrange
        project_dir = "/tmp/p"
        # Act
        out = CloneOutcome.cloned(template_id="scitex_minimal", project_dir=project_dir)
        # Assert
        assert out.project_dir == project_dir


class TestFailureShape:
    def test_failed_outcome_is_not_ok(self):
        # Arrange
        expected = False
        # Act
        out = _failed()
        # Assert
        assert out.ok is expected

    def test_failed_outcome_has_failed_status(self):
        # Arrange
        expected = "failed"
        # Act
        out = _failed()
        # Assert
        assert out.status == expected

    def test_failed_outcome_keeps_the_reason(self):
        # Arrange
        reason = "PermissionError: [Errno 13] denied"
        # Act
        out = _failed(reason)
        # Assert
        assert out.reason == reason

    def test_failed_outcome_keeps_the_traceback_detail(self):
        # Arrange
        detail = "Traceback (most recent call last): ..."
        # Act
        out = CloneOutcome.failed(
            template_id="scitex_minimal",
            project_dir=VISITOR_DIR,
            reason="boom",
            detail=detail,
        )
        # Assert
        assert out.detail == detail


class TestUnknownIsItsOwnAnswer:
    """Three-valued: a template that failed WITHOUT saying why must say so."""

    def test_missing_reason_stays_none_rather_than_empty_string(self):
        # Arrange
        no_reason = None
        # Act
        out = CloneOutcome.failed(
            template_id="singularity", project_dir="/tmp/p", reason=no_reason
        )
        # Assert
        assert out.reason is None

    def test_describe_still_names_the_template_when_reason_is_unknown(self):
        # Arrange
        template_id = "singularity"
        # Act
        out = CloneOutcome.failed(
            template_id=template_id, project_dir="/tmp/p", reason=None
        )
        # Assert
        assert template_id in out.describe()

    def test_describe_says_unknown_rather_than_going_quiet(self):
        # Arrange
        # A blank explanation reads like "nothing wrong"; it must not be blank.
        # Act
        out = CloneOutcome.failed(
            template_id="singularity", project_dir="/tmp/p", reason=None
        )
        # Assert
        assert "unknown" in out.describe().lower()


class TestLegacyBoolProtocol:
    """Every existing caller writes `if success:` — that must keep working."""

    def test_cloned_outcome_is_truthy(self):
        # Arrange
        out = _cloned()
        # Act
        truthiness = bool(out)
        # Assert
        assert truthiness is True

    def test_failed_outcome_is_falsy(self):
        # Arrange
        out = _failed()
        # Act
        truthiness = bool(out)
        # Assert
        assert truthiness is False

    def test_not_success_branch_fires_on_failure(self):
        # Arrange
        out = _failed()
        # Act
        took_failure_branch = not out
        # Assert
        assert took_failure_branch is True


class TestDescribeIsActionable:
    def test_describe_names_the_template(self):
        # Arrange
        out = _failed()
        # Act
        message = out.describe()
        # Assert
        assert "scitex_minimal" in message

    def test_describe_names_the_target_directory(self):
        # Arrange
        out = _failed()
        # Act
        message = out.describe()
        # Assert
        assert VISITOR_DIR in message

    def test_describe_names_the_underlying_error(self):
        # Arrange
        out = _failed("FileNotFoundError: template payload missing")
        # Act
        message = out.describe()
        # Assert
        assert "FileNotFoundError" in message


class TestOutcomeIsImmutable:
    def test_reason_cannot_be_rewritten_by_a_later_frame(self):
        # Arrange
        out = _cloned()
        # Act / Assert — a diagnosis a later frame can edit is not a diagnosis.
        # Assert
        with pytest.raises(Exception):
            out.reason = "tampered"  # type: ignore[misc]


class TestTheOutageStringIsNoLongerPossible:
    def test_a_failure_message_is_never_only_returned_falsy(self):
        # Arrange
        out = _failed()
        # Act
        message = out.describe()
        # Assert
        assert message != LEGACY_MESSAGE
