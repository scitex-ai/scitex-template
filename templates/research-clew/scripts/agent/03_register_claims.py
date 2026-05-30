#!/usr/bin/env python3
"""Stage 03 — DAG terminus.

Reads ``stats.json`` (DAG node), emits ``data/results/claims.json``
(canonical clew output contract), and registers each claim with
``scitex_clew.add_claim`` so the claim back-propagates through the
Clew DAG to its source data. That back-propagation is the validity
gate the verifier runs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import scitex as stx
import scitex_clew as clew

PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
            {
                "question":    "n_samples",
                "answer":      str(stats["n"]),
                "answer_type": "number",
            },
            {
                "question":    "sample_mean",
                "answer":      f"{stats['mean']:.6f}",
                "answer_type": "number",
            },
            {
                "question":    "sample_std",
                "answer":      f"{stats['std']:.6f}",
                "answer_type": "number",
            },
        ]
    }

    claims_path = PROJECT_ROOT / CONFIG.PATH.CLAIMS
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(json.dumps(claims_payload, indent=2))
    logger.info(
        f"Wrote {len(claims_payload['claims'])} claims -> {claims_path}"
    )

    # --- Clew claims registration (validity gate) ----------------------
    # Each claim references the JSON file it lives in (file_path) and
    # the source data file it derives from (source_file). The DAG that
    # lets `scitex_clew.chain(claim_value)` walk back from a claim to
    # the raw sample is built by these add_claim() entries combined
    # with the session-tracked save() calls in stages 01 and 02.
    rel_claims = os.path.relpath(claims_path, PROJECT_ROOT)
    rel_stats  = os.path.relpath(stats_path,  PROJECT_ROOT)
    for entry in claims_payload["claims"]:
        clew.add_claim(
            file_path=rel_claims,
            # Map output-contract answer_type -> scitex_clew claim_type
            # (vocabulary: 'statistic' | 'figure' | 'table' | 'text' | 'value').
            claim_type={
                'number':   'statistic',
                'interval': 'statistic',
                'string':   'text',
                'list':     'value',
                'bool':     'value',
            }.get(entry['answer_type'], 'value'),
            claim_value=entry["answer"],
            source_file=rel_stats,
        )

    n = len(claims_payload["claims"])
    print(f"DONE n_claims={n}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
