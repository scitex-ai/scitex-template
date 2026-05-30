#!/usr/bin/env python3
"""Out-of-band schema validity check on ``data/results/claims.json``.

PLAIN PYTHON — no ``@stx.session`` decorator. This script must NOT be
part of the agent's Clew DAG; it's the verifier-side smoke that triages
shape before any oracle scoring runs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "data" / "results" / "claims.json"

ANSWER_TYPES = {"string", "number", "interval", "list", "bool"}


def main() -> int:
    if not CLAIMS.is_file():
        print(f"FAIL: {CLAIMS} missing", file=sys.stderr)
        return 1

    payload = json.loads(CLAIMS.read_text())

    if not isinstance(payload, dict):
        print("FAIL: top level is not a JSON object", file=sys.stderr)
        return 1
    if "claims" not in payload or not isinstance(payload["claims"], list):
        print("FAIL: missing/invalid `claims` array", file=sys.stderr)
        return 1
    if not payload["claims"]:
        print("FAIL: empty `claims` array (scored as malformed)", file=sys.stderr)
        return 1

    for i, c in enumerate(payload["claims"]):
        if not isinstance(c, dict):
            print(f"FAIL: claim[{i}] is not an object", file=sys.stderr)
            return 1
        missing = {"question", "answer"} - c.keys()
        if missing:
            print(f"FAIL: claim[{i}] missing keys {missing}", file=sys.stderr)
            return 1
        at = c.get("answer_type")
        if at is not None and at not in ANSWER_TYPES:
            print(
                f"FAIL: claim[{i}] answer_type={at!r} not in {sorted(ANSWER_TYPES)}",
                file=sys.stderr,
            )
            return 1

    print(f"OK schema: {len(payload['claims'])} claims, all required keys present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
