#!/usr/bin/env python3
"""``clone_template_result`` — the dispatcher that reports a cause.

Companion to test__clone_outcome.py (which covers the shape itself). Here the
question is whether the DISPATCHER fills that shape correctly for each way a
template can end: succeed, return falsy without explanation, or raise.

The falsy case is the one that matters. A template that returns ``False`` has
told us nothing, and the outcome must say "unknown" rather than inventing a
cause — the failure being fixed is a message that reads confident and explains
nothing.

The last class is the guard rail: ``clone_template`` is a published contract
(scitex-hub, the CLI exit code, and tests asserting ``is True`` by identity).
Adding the rich API must not have moved it a millimetre.

NO MOCKS. The templates are swapped through ``TEMPLATES`` itself — the registry
this module exports in ``__all__``, i.e. its own documented extension point — by
a fixture that restores the original afterwards. The functions installed are
ordinary Python functions doing exactly what a real template does at that
boundary: return a value, or raise.
"""

from __future__ import annotations

import pytest

from scitex_template._project._clone_outcome import CloneOutcome
from scitex_template._project._clone_template import (
    TEMPLATES,
    clone_template,
    clone_template_result,
)

TARGET = "/tmp/visitor-001/default-project"
SLOT = "scitex_minimal"


@pytest.fixture
def install_template():
    """Install a real function into the public TEMPLATES registry, then restore."""
    sentinel = object()
    original = TEMPLATES.get(SLOT, sentinel)

    def _install(func):
        TEMPLATES[SLOT] = func

    yield _install

    if original is sentinel:
        TEMPLATES.pop(SLOT, None)
    else:
        TEMPLATES[SLOT] = original


def _returns(value):
    def _template(**kwargs):
        return value

    return _template


def _raises(exc):
    def _template(**kwargs):
        raise exc

    return _template


class TestSuccess:
    def test_a_successful_clone_is_ok(self, install_template):
        # Arrange
        install_template(_returns(True))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert out.ok is True

    def test_a_successful_clone_records_the_resolved_template_id(
        self, install_template
    ):
        # Arrange — call through the ALIAS to prove resolution is reported.
        install_template(_returns(True))
        # Act
        out = clone_template_result("minimal", TARGET)
        # Assert
        assert out.template_id == SLOT


class TestFalsyWithoutExplanation:
    """The template failed and said nothing. Say THAT; do not invent a cause."""

    def test_a_falsy_return_is_not_ok(self, install_template):
        # Arrange
        install_template(_returns(False))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert out.ok is False

    def test_a_falsy_return_states_that_no_cause_was_reported(self, install_template):
        # Arrange
        install_template(_returns(False))

        # Act
        out = clone_template_result(SLOT, TARGET)

        # Assert — the class docstring says "say THAT". An ABSENT reason does
        # not say it; it reaches the operator as a blank field, which is how
        # scitex-hub quarantined 16 slots with no explanation on 2026-08-28.
        assert out.reason
        assert "no cause" in out.reason
        assert SLOT in out.reason

    def test_a_falsy_return_does_not_invent_a_cause(self, install_template):
        # Arrange
        install_template(_returns(False))

        # Act
        out = clone_template_result(SLOT, TARGET)

        # Assert — reporting "it did not say" is not the same as naming an
        # error nobody observed. The reason must describe the SILENCE.
        assert "returned falsy" in out.reason
        assert out.detail is None

    def test_a_falsy_return_still_names_the_target_directory(self, install_template):
        # Arrange — the old message named the slug and nothing else.
        install_template(_returns(False))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert TARGET in out.describe()


class TestRaisingTemplate:
    """An exception is the richest case — it must survive to the caller."""

    def test_an_exception_becomes_a_failed_outcome(self, install_template):
        # Arrange
        install_template(_raises(PermissionError(13, "Permission denied")))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert out.ok is False

    def test_an_exception_type_reaches_the_reason(self, install_template):
        # Arrange
        install_template(_raises(PermissionError(13, "Permission denied")))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert "PermissionError" in out.reason

    def test_an_exception_message_reaches_the_reason(self, install_template):
        # Arrange
        install_template(_raises(FileNotFoundError("template payload missing")))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert "template payload missing" in out.reason

    def test_the_traceback_is_kept_in_detail(self, install_template):
        # Arrange
        install_template(_raises(RuntimeError("boom")))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert "Traceback" in out.detail


class TestPassThrough:
    def test_a_template_already_returning_an_outcome_is_not_rewrapped(
        self, install_template
    ):
        # Arrange
        rich = CloneOutcome.failed(
            template_id=SLOT, project_dir=TARGET, reason="disk full"
        )
        install_template(_returns(rich))
        # Act
        out = clone_template_result(SLOT, TARGET)
        # Assert
        assert out is rich


class TestUnknownTemplateIsAProgrammingError:
    def test_an_unknown_template_id_still_raises(self):
        # Arrange
        bogus = "no-such-template"
        # Act / Assert — a typo in the caller is not "a clone that failed".
        # Assert
        with pytest.raises(ValueError):
            clone_template_result(bogus, TARGET)


class TestLegacyContractIsUntouched:
    """clone_template() -> bool must behave exactly as before."""

    def test_clone_template_still_returns_real_true(self, install_template):
        # Arrange — identity, because published callers assert `is True`.
        install_template(_returns(True))
        # Act
        result = clone_template(SLOT, TARGET)
        # Assert
        assert result is True

    def test_clone_template_still_returns_real_false(self, install_template):
        # Arrange
        install_template(_returns(False))
        # Act
        result = clone_template(SLOT, TARGET)
        # Assert
        assert result is False

    def test_clone_template_still_lets_exceptions_propagate(self, install_template):
        # Arrange — hub reports a RAISING template differently from a falsy one;
        # swallowing here would silently merge those two paths.
        install_template(_raises(RuntimeError("boom")))
        # Act / Assert
        # Assert
        with pytest.raises(RuntimeError):
            clone_template(SLOT, TARGET)


class TestCloneTemplateKeepsItsBoolContract:
    """`clone_template` is declared `-> bool` and callers check it by identity.

    This class exists because the change that let templates return CloneOutcome
    broke that contract and NO test noticed. `clone_template` did a bare
    `return func(...)`, so the richer type leaked straight out of the bool API;
    the only failure was in a template-level test, which pointed at the wrong
    layer. These two assert the boundary itself.
    """

    def test_a_failed_outcome_does_not_leak_through_as_an_object(
        self, install_template
    ):
        # Arrange
        install_template(
            _returns(
                CloneOutcome.failed(
                    template_id=SLOT, project_dir=TARGET, reason="boom"
                )
            )
        )

        # Act
        result = clone_template(SLOT, TARGET)

        # Assert -- `is False`, not merely falsy. A CloneOutcome is falsy too,
        # so `assert not result` would pass while the contract was broken.
        assert result is False

    def test_a_cloned_outcome_is_true_by_identity(self, install_template):
        # Arrange
        install_template(
            _returns(
                CloneOutcome.cloned(template_id=SLOT, project_dir=TARGET)
            )
        )

        # Act
        result = clone_template(SLOT, TARGET)

        # Assert
        assert result is True

