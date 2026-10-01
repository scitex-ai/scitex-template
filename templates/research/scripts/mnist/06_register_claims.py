#!/usr/bin/env python3
"""Register researcher-defined MNIST claims from stage 04's measured results.

Missing, malformed, or out-of-range results stop the run. The claims JSON is
an example artifact contract; its schema check does not verify provenance.
"""

from __future__ import annotations

import math
from pathlib import Path

import scitex_clew as clew
import scitex_io as io
import scitex_session as session

PROJECT_ROOT = Path(__file__).resolve().parents[2]
METRICS_JSON = PROJECT_ROOT / "data/mnist/metrics.json"
CLAIMS = PROJECT_ROOT / "data/results/claims.json"
CLEW_DAG_HTML = PROJECT_ROOT / "data/results/clew_dag.html"


def _read_real_metrics() -> dict[str, float]:
    if not METRICS_JSON.is_file():
        raise FileNotFoundError(f"Run stage 04 first: {METRICS_JSON} is missing")
    measured = io.load(str(METRICS_JSON))
    metrics = {}
    for key in ("accuracy", "macro_f1"):
        value = measured[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a measured number")
        value = float(value)
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{key} must be finite and between 0 and 1")
        metrics[key] = value
    return metrics


@session.session
def main(logger=session.INJECTED):
    metrics = _read_real_metrics()
    payload = {
        "claims": [
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
    }
    # Public IO records this stage's measured input and generated output.
    io.save(payload, str(CLAIMS))
    for entry in payload["claims"]:
        clew.add_claim(
            file_path=str(CLAIMS),
            claim_type="statistic",
            claim_value=entry["answer"],
            source_file=str(METRICS_JSON),
            claim_id=f"{CLAIMS}:{entry['question']}",
        )
    # Scope the preview to this metric artifact, rather than all host claims.
    clew.render_dag(
        output_path=CLEW_DAG_HTML,
        target_file=str(METRICS_JSON),
        title="MNIST metric dependencies",
    )
    logger.info(f"Registered {len(payload['claims'])} measured claims: {CLAIMS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
