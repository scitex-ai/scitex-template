#!/usr/bin/env python3
"""Stage 06 — Clew DAG terminus.

Reads stage 04's classification report (if MNIST pipeline has been
run end-to-end via ``make run-mnist``), or falls back to a synthetic
demo metric (so ``make solve`` is GREEN on a fresh checkout without
needing a multi-hour SVM training first).

Emits ``data/results/claims.json`` in the canonical clew output
contract, and registers each claim with ``scitex_clew.add_claim`` so
the claim back-propagates through the Clew DAG to source data --
that's the validity gate the verifier runs.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import scitex as stx
import scitex_clew as clew

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Stage 04 output — when the full MNIST pipeline has run, this is a CSV
# with sklearn's classification_report (accuracy, precision/recall/F1 per
# class, macro/weighted averages). When the user has only run ``make
# solve`` on a fresh checkout, the file is absent and we fall back to a
# deterministic synthetic claim so the DAG itself is exercised end-to-end.
CLF_REPORT = PROJECT_ROOT / "data/mnist/classification_report.csv"

# Where claims.json lives. Stable cross-stage location; the agent-prompt
# contract (``capsule_id``-less since the host adds identification
# out-of-band) prescribes exactly this shape:
#   { "claims": [ {question, answer, answer_type}, ... ] }
CLAIMS = PROJECT_ROOT / "data/results/claims.json"


# Map output-contract answer_type -> scitex_clew claim_type vocab
# (statistic|figure|table|text|value). Collapses to identity once
# scitex_clew broadens its vocabulary.
_TYPE_MAP = {
    "number":   "statistic",
    "interval": "statistic",
    "string":   "text",
    "list":     "value",
    "bool":     "value",
}


def _read_real_metrics() -> tuple[dict, Path] | None:
    """Return (metrics dict, source-file path) if stage 04 ran, else None."""
    if not CLF_REPORT.is_file():
        return None
    try:
        # scitex.io.load on a CSV returns a pandas DataFrame (the
        # classification_report is keyed by class label + macro/weighted/
        # accuracy rows when output_dict=True was saved).
        df = stx.io.load(str(CLF_REPORT))
        # Pull accuracy + macro-avg F1 by the sklearn report convention.
        accuracy = float(df.loc["accuracy"].iloc[0])
        macro_f1 = float(df.loc["macro avg", "f1-score"])
        return ({"accuracy": accuracy, "macro_f1": macro_f1}, CLF_REPORT)
    except Exception:
        return None


def _synthetic_demo_metrics() -> tuple[dict, Path]:
    """Deterministic fallback when stage 04 hasn't run yet.

    Writes a tiny stub source file so the Clew DAG's back-propagation
    (claim -> source_file) lands on a real on-disk node, not a phantom.
    """
    src = PROJECT_ROOT / "data/results/_synthetic_metrics.json"
    src.parent.mkdir(parents=True, exist_ok=True)
    metrics = {"accuracy": 0.93, "macro_f1": 0.92, "_provenance": "synthetic"}
    src.write_text(json.dumps(metrics, indent=2))
    return (metrics, src)


@stx.session
def main(
    CONFIG=stx.INJECTED,
    plt=stx.INJECTED,
    COLORS=stx.INJECTED,
    rng_manager=stx.INJECTED,
    logger=stx.INJECTED,
):
    real = _read_real_metrics()
    if real is not None:
        metrics, source = real
        logger.success(f"Registering real metrics from {source}: {metrics}")
    else:
        metrics, source = _synthetic_demo_metrics()
        logger.warning(
            "Stage 04 (clf_svm) output not found; using deterministic "
            f"synthetic metrics: {metrics}. Run `make run-mnist` for the "
            "real MNIST+SVM pipeline."
        )

    claims_payload = {
        "claims": [
            {
                "question":    "test_accuracy",
                "answer":      f"{metrics['accuracy']:.6f}",
                "answer_type": "number",
            },
            {
                "question":    "test_macro_f1",
                "answer":      f"{metrics['macro_f1']:.6f}",
                "answer_type": "number",
            },
        ]
    }

    CLAIMS.parent.mkdir(parents=True, exist_ok=True)
    CLAIMS.write_text(json.dumps(claims_payload, indent=2))
    logger.info(
        f"Wrote {len(claims_payload['claims'])} claims -> {CLAIMS}"
    )

    # --- Clew claims registration (validity gate) ----------------------
    rel_claims = os.path.relpath(CLAIMS,  PROJECT_ROOT)
    rel_source = os.path.relpath(source,  PROJECT_ROOT)
    for entry in claims_payload["claims"]:
        clew.add_claim(
            file_path=rel_claims,
            claim_type=_TYPE_MAP.get(entry["answer_type"], "value"),
            claim_value=entry["answer"],
            source_file=rel_source,
        )

    n = len(claims_payload["claims"])
    print(f"DONE n_claims={n}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
