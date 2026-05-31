#!/usr/bin/env python3
"""Stage 01 - DAG root: synthesize the sample."""

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
    # Canonical 5-INJECTED signature. Current scitex-session only fills
    # CONFIG + logger; the rest are declared so the template Just Works
    # once the refactor catches up. `rng` comes from numpy until then.
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
