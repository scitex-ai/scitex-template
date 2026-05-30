# research-clew — minimal SciTeX clew-compatible research project

A canonical, **minimal-but-working** SciTeX research-project template that
clew solver-agents imitate. This is what a `/capsule` problem becomes inside
`/workdir` when the solving agent follows the
`scripts/cohorts/_shared/prompts/TRANSLATION_TEMPLATE.md` playbook from
`paper-scitex-clew`.

## Quick start

```bash
make solve              # run the agent DAG → data/results/claims.json
make verify             # plain-Python schema check on claims.json
make clean              # nuke generated artefacts (keeps source)
```

## Layout

```text
research-clew/
├── Makefile                         # clean-DAG dispatcher (no SHELL := /bin/bash)
├── config/
│   ├── PATH.yaml                    # f-string path literals, NO outer `PATH:` wrapper
│   └── PARAMS.yaml                  # knobs (seed, n_samples, …)
├── scripts/
│   ├── agent/                       # @stx.session.run, INSIDE the Clew DAG
│   │   ├── 01_load_data.py          # verb-named, single-purpose
│   │   ├── 02_compute_stats.py
│   │   └── 03_register_claims.py    # DAG terminus → claims.json
│   └── verify/                      # plain Python, OUTSIDE the agent DAG
│       └── check_schema.py
├── data/
│   ├── intermediate/                # cross-stage artefacts (raw.npy, stats.json)
│   └── results/                     # DAG outputs (claims.json)
└── tests/
    └── scripts/                     # mirror of scripts/ for unit-tests (empty in template)
```

## How a solver agent uses it

Inside a `/capsule` apptainer mount, the agent:

1. Reads `/prompts/TRANSLATION_TEMPLATE.md` (the canonical playbook).
2. Scaffolds `/workdir` to match this layout.
3. Writes single-purpose **verb-named** scripts under `scripts/agent/`
   (e.g. `load_data.py`, `compute_stats.py`, `make_figure.py`,
   `register_claims.py`). Each is `@stx.session.run`-decorated and declares
   all five injected params:

```python
@stx.session.run
def main(
    CONFIG=stx.INJECTED,
    COLORS=stx.INJECTED,
    logger=stx.INJECTED,
    plt=stx.INJECTED,
    rngg=stx.INJECTED,
):
    ...
```

4. Saves cross-stage I/O via `stx.io.save(..., symlink_to=eval(CONFIG.PATH.X))`.
5. Registers each claim with `scitex_clew.add_claim(file_path=…, claim_type=…,
   claim_value=…, source_file=…)` so the claim back-propagates through the
   Clew DAG to source data (the validity gate). The DAG terminus is a FILE
   (`data/results/claims.json`), not a script node.

## Worked example

The shipped scripts run a synthetic sampling → summary-statistics → claims
pipeline that requires no external data:

| Stage | Script | Reads | Writes | Claims registered |
|---|---|---|---|---|
| 1 | `scripts/agent/01_load_data.py` | (synthesizes via `rngg`) | `data/intermediate/raw.npy` | — |
| 2 | `scripts/agent/02_compute_stats.py` | `raw.npy` | `data/intermediate/stats.json` | — |
| 3 | `scripts/agent/03_register_claims.py` | `stats.json` | `data/results/claims.json` | `n_samples`, `sample_mean`, `sample_std` (3 claims, each `source_file=stats.json`) |

`make solve` runs all three sequentially. `make verify` schema-checks the
result. Replace the three scripts with your own verb-named analysis steps;
keep the agent-vs-verify split and the file-DAG terminus.

## Constraints (worth repeating — these break things silently)

- **No `SHELL := /bin/bash`** at the top of the Makefile. It breaks
  `@stx.session` under `make`.
- **`PATH.yaml` has NO outer `PATH:` wrapper.** Values are f-string
  literals (`f"{CONFIG.PATH.X}/…"`); the file IS the `CONFIG.PATH` namespace.
- **All five `INJECTED` params declared** in every `@stx.session.run` main
  (CONFIG, COLORS, logger, plt, rngg).
- **Figures via `stx.plt`** / `figrecipe` only — `matplotlib.pyplot.savefig`
  is forbidden (data + style must enter the DAG as data).
- **DAG terminus is a file** (`data/results/claims.json` via `stx.io.save`),
  not a script node.
- **`scripts/verify/` scripts are plain Python**, NOT `@stx.session`-
  decorated, so verifier work doesn't pollute the agent's Clew DAG.

## Origin

Aligned with `paper-scitex-clew/scripts/cohorts/_shared/prompts/TRANSLATION_TEMPLATE.md`.
Vendored under `scitex_template/templates/research-clew/`; clone with
`scitex-template clone research-clew <dest>`.

## Refactor caveats (live scitex 2.29 / scitex-session 0.2.0)

Encountered while dogfooding the in-progress scitex SoC refactor (2026-05-30):

1. `stx.session` injection is incomplete. Of the canonical 5 INJECTED
   params (`CONFIG, COLORS, logger, plt, rngg`), only **`CONFIG` and
   `logger`** are actually populated; the others remain
   `_InjectedSentinel`. This template declares all 5 for canon-
   completeness but only uses `CONFIG`/`logger` functionally;
   randomness comes from `np.random.default_rng` directly.

2. `@stx.session.run` is broken (positional-args path clobbers `CONFIG`
   with the parsed argparse namespace). Use plain `@stx.session` —
   that's the path that goes through `_run_with_session(**filtered_kwargs)`
   and correctly injects `CONFIG`/`logger`.

3. `scitex_session._lifecycle._config` calls `stx.io.save(..., track=...)`
   on its auto-dumped `CONFIG.pkl` / `CONFIG.yaml`. The current
   `scitex_io._save_pickle` / `_save_yaml` no longer accept the `track=`
   kwarg, so two `ERRO: _save_*() got an unexpected keyword argument
   'track'` lines are logged on every session lifecycle. These are
   logged-but-handled — the session still finishes in `FINISHED_SUCCESS`
   and the user's main returns normally. Noise, not a blocker.

4. `stx.io.save(<relative_path>)` redirects under a per-session
   `./output/` sandbox. The agent-vs-verify cross-stage DAG needs a
   stable shared path; until `symlink_to=` is stable upstream, this
   template uses absolute paths derived from `Path(__file__).resolve().parents[2]`
   and stdlib persistence (`numpy.save` / `json.dump`) for the inter-
   stage hand-off.

5. `scitex_clew.add_claim(claim_type=...)` vocabulary is restricted to
   `{statistic, figure, table, text, value}`; the output-contract's
   `answer_type` enum (`{string, number, interval, list, bool}`) is
   wider. Stage 3 maps between them. When upstream broadens the
   `claim_type` vocab, the mapping table in
   `scripts/agent/03_register_claims.py` collapses to identity.

All five surface here for the scitex maintainers' triage — they do
not block this template from running green:

```bash
$ make solve   # rc=0
$ make verify  # rc=0, "OK schema: 3 claims, all required keys present"
$ cat data/results/claims.json   # canonical {claims:[…]} payload
```

