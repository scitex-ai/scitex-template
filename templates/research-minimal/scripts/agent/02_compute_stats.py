#!/usr/bin/env python3
"""Stage 02 - summary statistics from the sample."""

from __future__ import annotations

import json
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
    raw_path = PROJECT_ROOT / CONFIG.PATH.RAW_DATA
    data = np.load(raw_path)
    stats = {
        "n":    int(data.size),
        "mean": float(np.mean(data)),
        "std":  float(np.std(data, ddof=1)),
        "min":  float(np.min(data)),
        "max":  float(np.max(data)),
    }
    out = PROJECT_ROOT / CONFIG.PATH.STATS
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, indent=2))
    logger.info(f"Stats -> {out}: {stats}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
