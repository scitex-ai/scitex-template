#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a SciTeX/Clew submission file against the cohort-A shape contract.

Usage
-----
    python validate_submission_file.py path/to/claims.json

Exit codes
----------
- 0  : valid
- 1  : invalid (a reason is printed to stderr)
- 2  : usage error / unsupported format

Shape contract (JSON)
---------------------
::

    {
      "claims": [
        {"question": <str>, "answer": <str>},   # both required strings
        ...
      ],
      "notes": <str>                            # optional, string if present
    }

Rules:

- top-level MUST be a dict containing the key ``claims``
- ``claims`` MUST be a non-empty list of dicts
- each claim MUST have ``question`` and ``answer`` as strings (numbers / lists /
  bools should be serialized to string form)
- extra keys per claim (``evidence``, ``figure_path``, ...) are allowed; the
  validator logs them at INFO level but does not reject them
- top-level ``notes`` is optional; if present it MUST be a string

Forward-compatibility
---------------------
Filename is ``validate_submission_file.py`` (not ``..._json.py``) so future
non-JSON formats (YAML, CSV, msgpack, ...) can land as additional suffix
branches inside :func:`validate` without renaming the script or changing the
CLI surface. Today only ``.json`` is supported.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("validate_submission_file")


# ----------------------------------------------------------------------------
# Format dispatch
# ----------------------------------------------------------------------------
def validate(path: Path) -> tuple[bool, str]:
    """Dispatch to the format-specific validator based on file suffix.

    Returns ``(ok, reason)``. ``reason`` is empty on success, otherwise a
    short human-readable failure description.
    """
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _validate_json(path)
    # Future formats — keep these branches stubbed so the filename's
    # format-agnostic naming holds. Add real handlers as cohorts need them.
    if suffix in {".yaml", ".yml"}:
        raise NotImplementedError(
            "YAML submission validation is not implemented yet; "
            "track via scitex-template issue tracker."
        )
    if suffix == ".csv":
        raise NotImplementedError(
            "CSV submission validation is not implemented yet; "
            "track via scitex-template issue tracker."
        )
    return False, f"unsupported submission suffix: {suffix!r}"


# ----------------------------------------------------------------------------
# JSON validator
# ----------------------------------------------------------------------------
_EXPECTED_CLAIM_KEYS = {"question", "answer"}


def _validate_json(path: Path) -> tuple[bool, str]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except json.JSONDecodeError as exc:
        return False, f"not valid JSON: {exc}"

    if not isinstance(payload, dict):
        return False, "top-level value must be a JSON object (dict)"

    if "claims" not in payload:
        return False, "missing required top-level key 'claims'"

    claims = payload["claims"]
    if not isinstance(claims, list):
        return False, "'claims' must be a list"
    if len(claims) == 0:
        return False, "'claims' list is empty (must contain at least one claim)"

    for idx, claim in enumerate(claims):
        ok, reason = _validate_claim(claim, idx)
        if not ok:
            return False, reason

    notes = payload.get("notes")
    if notes is not None and not isinstance(notes, str):
        return False, f"top-level 'notes' must be a string, got {type(notes).__name__}"

    return True, ""


def _validate_claim(claim: Any, idx: int) -> tuple[bool, str]:
    if not isinstance(claim, dict):
        return False, f"claims[{idx}] must be a dict, got {type(claim).__name__}"
    for required in ("question", "answer"):
        if required not in claim:
            return False, f"claims[{idx}] missing required key {required!r}"
        if not isinstance(claim[required], str):
            return (
                False,
                f"claims[{idx}].{required} must be a string, got "
                f"{type(claim[required]).__name__}",
            )

    extras = set(claim.keys()) - _EXPECTED_CLAIM_KEYS
    if extras:
        # Allowed but worth surfacing so the agent knows the validator saw them.
        logger.info(
            "claims[%d] has extra keys (allowed, ignored): %s",
            idx,
            sorted(extras),
        )
    return True, ""


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(argv) != 2:
        print(
            f"usage: {Path(argv[0]).name} path/to/submission-file",
            file=sys.stderr,
        )
        return 2

    path = Path(argv[1])
    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    try:
        ok, reason = validate(path)
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not ok:
        print(f"INVALID: {reason}", file=sys.stderr)
        return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
