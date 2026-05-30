#!/usr/bin/env python3
"""Stage 01 — synthesize a small sample dataset.

Owns the root of the Clew DAG. Persists ``raw.npy`` deterministically
from the configured seed.

Canonical SciTeX/Clew signature declares all 5 INJECTED params
(CONFIG, COLORS, logger, plt, rngg). Current scitex-session (0.2.0)
only injects CONFIG + logger reliably; the unused sentinels stay in
the signature so this template Just Works once injection catches up.

PATH note: ``stx.io.save`` of relative paths is currently redirected
into a per-session ``./output/`` sandbox. For a clean cross-stage
DAG, we resolve ``CONFIG.PATH.X`` against the project root (this
file's grand-parent grandparent) before persisting. Once
``stx.io.save(..., symlink_to=...)`` is stable upstream, switch this
template to the canonical symlink-to-stable-path pattern.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import scitex as stx

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@stx.session
def main(
    CONFIG=stx.INJECTED,
    COLORS=stx.INJECTED,
    logger=stx.INJECTED,
    plt=stx.INJECTED,
    rngg=stx.INJECTED,
):
    rng = np.random.default_rng(int(CONFIG.PARAMS.SEED))
    n = int(CONFIG.PARAMS.N_SAMPLES)
    data = rng.normal(
        loc=float(CONFIG.PARAMS.TRUE_MEAN),
        scale=float(CONFIG.PARAMS.TRUE_STD),
        size=n,
    )
    out = PROJECT_ROOT / CONFIG.PATH.RAW_DATA
    out.parent.mkdir(parents=True, exist_ok=True)
    np.save(out, data)
    logger.info(f"Saved {n} samples -> {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
