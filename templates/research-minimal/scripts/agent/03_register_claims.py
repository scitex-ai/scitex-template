#!/usr/bin/env python3
"""Stage 03 - DAG terminus + Clew validity gate."""

from __future__ import annotations

import json
import os
from pathlib import Path

import scitex as stx
import scitex_clew as clew

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Map output-contract answer_type (string|number|interval|list|bool) onto
# scitex_clew's narrower claim_type vocab. Collapses to identity once
# scitex_clew broadens upstream.
_TYPE_MAP = {
    "number":   "statistic",
    "interval": "statistic",
    "string":   "text",
    "list":     "value",
    "bool":     "value",
}


@stx.session
def main(
    CONFIG=stx.INJECTED,
    COLORS=stx.INJECTED,
    logger=stx.INJECTED,
    plt=stx.INJECTED,
    rngg=stx.INJECTED,
):
    stats_path = PROJECT_ROOT / CONFIG.PATH.STATS
    stats = json.loads(stats_path.read_text())

    claims_payload = {
        "claims": [
            {"question": "n_samples",   "answer": str(stats["n"]),
             "answer_type": "number"},
            {"question": "sample_mean", "answer": f"{stats['mean']:.6f}",
             "answer_type": "number"},
            {"question": "sample_std",  "answer": f"{stats['std']:.6f}",
             "answer_type": "number"},
        ]
    }

    claims_path = PROJECT_ROOT / CONFIG.PATH.CLAIMS
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(json.dumps(claims_payload, indent=2))
    logger.info(f"Wrote {len(claims_payload['claims'])} claims -> {claims_path}")

    rel_claims = os.path.relpath(claims_path, PROJECT_ROOT)
    rel_stats  = os.path.relpath(stats_path,  PROJECT_ROOT)
    for entry in claims_payload["claims"]:
        clew.add_claim(
            file_path=rel_claims,
            claim_type=_TYPE_MAP.get(entry["answer_type"], "value"),
            claim_value=entry["answer"],
            source_file=rel_stats,
        )

    n = len(claims_payload["claims"])
    print(f"DONE n_claims={n}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
