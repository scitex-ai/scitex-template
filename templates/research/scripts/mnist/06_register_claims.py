#!/usr/bin/env python3
"""Stage 06 — Clew DAG terminus.

Reads stage 04's ``data/mnist/metrics.json`` through ``stx.io.load`` (so
the read is recorded as an input of this run) and turns each metric into
a claim. If stage 04 has not run, this stage fails loudly: a claim is
only ever made from a number the pipeline actually computed — never from
a placeholder.

Emits under ``data/results/``:

1. ``claims.json`` — the ``{"claims": [{question, answer, answer_type}]}``
   output contract read by ``scripts/verify/check_schema.py``. Saved via
   ``stx.io.save`` so Clew records it as an output of this run.
2. One Clew claim per metric via ``scitex_clew.add_claim(...,
   source_file=<metrics.json>)``. Because stage 04 wrote ``metrics.json``
   with ``stx.io.save`` inside its ``@stx.session``, each claim
   back-traces through the recorded runs to the source data.
3. ``clew_dag.html`` — interactive Mermaid.js view of the registered-claims
   DAG (``scitex_clew.render_dag``): ``claim -> source_file -> raw inputs``.
"""

from __future__ import annotations

from pathlib import Path

import scitex as stx
import scitex_clew as clew

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Stage 04 output: compact ``{accuracy, macro_f1}`` written by
# ``04_clf_svm.py`` with ``stx.io.save(..., symlink_from_cwd=True)``.
METRICS_JSON = PROJECT_ROOT / "data/mnist/metrics.json"

# Stable path of this stage's claims (a symlink created by stx.io.save).
CLAIMS_JSON = PROJECT_ROOT / "data/results/claims.json"

# Visualised clew DAG (interactive HTML via Mermaid.js).
CLEW_DAG_HTML = PROJECT_ROOT / "data/results/clew_dag.html"

# Map output-contract answer_type -> scitex_clew claim_type vocab
# (statistic|figure|table|text|value).
_TYPE_MAP = {
    "number": "statistic",
    "interval": "statistic",
    "string": "text",
    "list": "value",
    "bool": "value",
}


def load_metrics(path: Path = METRICS_JSON) -> dict:
    """Load stage 04's metrics; raise if stage 04 has not produced them.

    No fallback: a missing or malformed upstream output is an error the
    researcher must see, not something to paper over with made-up values.
    """
    if not path.is_file():
        raise FileNotFoundError(
            f"Upstream output missing: {path}. Stage 06 registers claims "
            "only from metrics the pipeline computed. Run stage 04 first "
            "(`python scripts/mnist/04_clf_svm.py`, or `make solve`)."
        )
    metrics = stx.io.load(str(path))
    missing = {"accuracy", "macro_f1"} - set(metrics)
    if missing:
        raise KeyError(f"{path} lacks required metric(s): {sorted(missing)}")
    return {
        "accuracy": float(metrics["accuracy"]),
        "macro_f1": float(metrics["macro_f1"]),
    }


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    metrics = load_metrics()
    logger.success(f"Registering metrics from {METRICS_JSON}: {metrics}")

    claims = [
        {
            "question": "test_accuracy",
            "answer": f"{metrics['accuracy']:.6f}",
            "answer_type": "number",
        },
        {
            "question": "test_macro_f1",
            "answer": f"{metrics['macro_f1']:.6f}",
            "answer_type": "number",
        },
    ]

    # Saved through stx.io so this run records claims.json as its output;
    # The file lands in this script's _out/ dir; symlink_from_cwd=True adds
    # the stable link data/results/claims.json (run from the project root).
    stx.io.save({"claims": claims}, "./data/results/claims.json", symlink_from_cwd=True)
    logger.info(f"Wrote {len(claims)} claims -> {CLAIMS_JSON}")

    # --- Clew claims registration (validity gate) ----------------------
    # source_file is the stx.io-saved output of stage 04, so each claim
    # resolves to the run that produced it (no NO_LINEAGE warning).
    for entry in claims:
        clew.add_claim(
            file_path=str(CLAIMS_JSON),
            claim_type=_TYPE_MAP[entry["answer_type"]],
            claim_value=entry["answer"],
            source_file=str(METRICS_JSON),
        )

    # --- Clew DAG visualization (human-inspectable artefact) -----------
    clew.render_dag(
        output_path=CLEW_DAG_HTML,
        claims=True,
        title="MNIST — clew claims DAG",
    )
    logger.info(f"Rendered clew DAG -> {CLEW_DAG_HTML}")

    print(f"DONE n_claims={len(claims)}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
