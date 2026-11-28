<!-- 12_showcase-flow.md -->

# The MNIST showcase: literature to live paper

The example project runs the SciTeX ecosystem end to end. Each step is one
`make` target and one package; `make all` runs them in order.

| Step | `make` | Script / tool | Package |
|---|---|---|---|
| Literature (online, optional) | `refs` | `scripts/mnist/00_resolve_references.py` | scitex-scholar |
| Data | `fetch` | `scripts/mnist/01_fetch_mnist.py` | scitex-dataset (sha256-checked, cached, recorded) |
| Trust anchor | `register-source` | `clew register-source data/raw/mnist/mnist.npz` | scitex-clew |
| Analysis | `train` | `scripts/mnist/02_train_classifiers.py` | scitex-ml, scitex-repro |
| Statistics | `stats` | `scripts/mnist/03_compare_classifiers.py` | scitex-stats (McNemar) |
| Figures | `figures` | `scripts/mnist/04_plot_figure.py` | figrecipe (mm panels, compose from recipes) |
| Notebook variant | `notebook` | `notebooks/01_count_classes.ipynb` | scitex-notebook, `clew execute-notebook` |
| Claims | `claims` | `scripts/mnist/05_register_claims.py` + `config/CLAIMS.yaml` | scitex-writer -> scitex-clew |
| Manuscript | `paper` | tracked sections in `.scitex/writer/` (alias `manuscript/`) | scitex-writer |
| Live paper | `live-paper` | `scitex-live-paper render` with clew's evidence | scitex-live-paper |
| Gate | `verify` | `clew verify --strict`, `clew slice <claim>` | scitex-clew |
| Demo | `demo-fault` | `scripts/demo/plant_fault.sh` | clew + live-paper |

## Rules the scripts follow

- Every script is `@scitex_session.session`; every read and write goes
  through `scitex_io` (`sio.load` / `sio.save(..., symlink_from_cwd=True)`),
  so clew records inputs, outputs and their SHA-256 without explicit calls.
- Every parameter is in `config/*.yaml` (scitex-dev STX-S008); every path is
  in `config/PATH.yaml`.
- No number in the Results is typed: it is `\vclaim{<id>}`, registered from
  `config/CLAIMS.yaml` with a JSON-pointer locator into the file a recorded
  run wrote. `clew verify --strict` re-reads and compares each value.
- Numbers typed by hand (the dataset sizes in the Methods) are deliberately
  left unregistered; the live paper gives them no verdict.

## Adding a claim

1. Make sure a script writes the value to a JSON file via `sio.save`.
2. Add an entry to `config/CLAIMS.yaml` (ID, SOURCE, POINTER, DIGITS).
3. Write `\vclaim{<ID>}` where the number goes in `manuscript/`.
4. `make claims paper verify`.

## Store

clew records runs in the SciTeX PostgreSQL store: `SCITEX_STORE_DSN` if set,
otherwise the per-host default. For an isolated run, point
`SCITEX_STORE_DSN` at a private database.
