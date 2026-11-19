<!-- 11_writing-scripts.md -->

# Writing Experiment Scripts

Every analysis script is a `@scitex_session.session`-decorated `main`.
The decorator loads `config/*.yaml` into `CONFIG`, sets up logging and
matplotlib, and opens the provenance record; scitex-io then records every
file the script reads or writes.

## Minimal skeleton

```python
#!/usr/bin/env python3
# File: scripts/my_topic/01_calc_summary.py
"""Docstring becomes --help text."""

import scitex_io as sio
import scitex_session as sess


@sess.session
def main(
    CONFIG=sess.INJECTED,   # ./config/*.yaml, keys upper-cased
    plt=sess.INJECTED,
    COLORS=sess.INJECTED,
    rngg=sess.INJECTED,
    logger=sess.INJECTED,
):
    data = sio.load(CONFIG.PATH.MY_TOPIC.INPUT)          # recorded input
    summary = {"mean": float(data.mean()), "n": int(len(data))}
    sio.save(summary, CONFIG.PATH.MY_TOPIC.SUMMARY,      # recorded output
             symlink_from_cwd=True)                      # + stable data/ link
    return 0


if __name__ == "__main__":
    main()
```

## Rules

- Parameters (thresholds, sizes, seeds) live in `config/*.yaml`, never as
  numbers in the script (scitex-dev STX-S008). Paths live in
  `config/PATH.yaml`.
- All I/O goes through `scitex_io`; raw `open`/`np.save`/`df.to_csv` is
  invisible to provenance.
- A relative `sio.save` path is anchored to `<script>_out/`;
  `symlink_from_cwd=True` adds the link at the same path under the project
  root. Run scripts from the project root (as `make` does).
- Declare which inputs an output used with `derived_from=[...]` when a
  script reads more than the output needs (tighter `clew slice --level 2`).
- Figures: figrecipe with sizes in mm and the SCITEX style; compose panels
  from their recipes (`fr.compose`), never rescale rendered images.
- Statistics: scitex-stats (no raw scipy).
- Seeds: `scitex_repro.RandomStateManager(seed=CONFIG...)`.

## Output layout

```
scripts/my_topic/01_calc_summary_out/
├── data/my_topic/summary.json            # the output (data/ links here)
└── FINISHED_SUCCESS/<session_id>/
    ├── logs/{stdout,stderr}.log
    └── CONFIGS/CONFIG.yaml               # frozen config + provenance record
```

Name scripts `NN_<verb>_<object>.py` in execution order; tests mirror them
under `tests/`.
