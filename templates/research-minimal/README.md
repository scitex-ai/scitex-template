# research-minimal -- minimal clew-ready SciTeX exemplar

A ~14-file alternative to `templates/research/` (which carries the MNIST +
SVM walkthrough and ~40 files of agent guidance). Same canonical layout
(agent-vs-verify split, clean-DAG Makefile, `scitex.session`,
`scitex.clew` claims back-propagating to source data). No torch/sklearn
dependency; `make solve` finishes in seconds.

Use this when you want the **pattern** the
[paper-scitex-clew](https://github.com/ywatanabe1989/paper-scitex-clew)
solver agent imitates -- without the classifier baggage.

## Quick start

```
uv pip install -r requirements.txt    # or python -m pip install
make solve                            # synthesize -> stats -> claims
make verify-claims                    # plain-Python schema check
make clean                            # nuke generated artefacts
```

`make solve` exits 0 and produces `data/results/claims.json`:

```json
{
  "claims": [
    {"question":"n_samples",   "answer":"100",       "answer_type":"number"},
    {"question":"sample_mean", "answer":"0.000000",  "answer_type":"number"},
    {"question":"sample_std",  "answer":"1.000000",  "answer_type":"number"}
  ]
}
```

Each claim is registered via
`scitex_clew.add_claim(file_path=..., claim_type=..., claim_value=...,
source_file=...)` so the Clew validity gate back-propagates from
claims.json through stats.json to raw.npy.

## Layout

```
research-minimal/
|-- Makefile
|-- README.md
|-- requirements.txt
|-- template.yaml
|-- .gitignore
|-- .scitex/clew/.gitkeep              # local-state convention (clew DB)
|-- config/
|   |-- PATH.yaml                      # NO outer `PATH:` wrapper
|   `-- PARAMS.yaml                    # CONFIG.PARAMS namespace
|-- data/
|   |-- intermediate/.gitkeep          # raw.npy, stats.json land here
|   `-- results/.gitkeep               # claims.json (DAG terminus)
`-- scripts/
    |-- agent/                         # @stx.session, inside the Clew DAG
    |   |-- 01_load_data.py            # rng -> raw.npy
    |   |-- 02_compute_stats.py        # raw.npy -> stats.json
    |   `-- 03_register_claims.py      # stats.json -> claims.json + add_claim
    `-- verify/                        # plain Python, outside the agent DAG
        `-- check_schema.py
```

## Canonical patterns (rule-cheat-sheet)

- `@stx.session` (NOT `@stx.session.run` -- that one passes args
  positionally and clobbers `CONFIG=stx.INJECTED` in the current refactor).
- All 5 INJECTED params declared (CONFIG, COLORS, logger, plt, rngg) for
  canon-completeness; current scitex-session only fills CONFIG + logger
  reliably, so `rng` comes from `numpy.random.default_rng` directly.
  Once injection lands upstream, drop the workaround.
- Plain stdlib persistence (`np.save`, `json.dump`) for cross-stage I/O
  -- bypasses the `./output/` per-session sandbox of `stx.io.save`. Only
  `scitex_clew.add_claim` calls matter for the Clew DAG itself.
- `config/PATH.yaml` has NO outer `PATH:` wrapper -- the file IS the
  `CONFIG.PATH` namespace.
- Makefile has NO `SHELL := /bin/bash` (would break `@stx.session` under
  make).
- DAG terminus is a FILE (`data/results/claims.json`), not a script node.

## Refactor caveat (live scitex 2.29 / scitex-session 0.2.0)

`scitex_session._lifecycle._config` calls `stx.io.save(..., track=...)`
on its auto-dumped `CONFIG.pkl` / `CONFIG.yaml`; that kwarg no longer
exists in the SoC-refactored `scitex_io`. Two `ERRO:` log lines fire on
every `@stx.session` lifecycle but are *logged-but-handled* (session
reaches `FINISHED_SUCCESS`, `make solve` exits 0). Cosmetic noise, not
a blocker.

## Relationship to `templates/research/`

This template = the minimal exemplar. `templates/research/` = the
full-featured example with MNIST + SVM, kept for users who want the
classifier walkthrough alongside the pattern. Both are vendored; pick
the one that matches your need.
