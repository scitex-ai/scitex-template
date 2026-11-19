# SciTeX Research Template

A starting point for a reproducible research project with
[SciTeX](https://scitex.ai), shipped with a small worked example that runs
the ecosystem end to end:

```
literature -> data -> analysis -> statistics -> figures -> claims -> manuscript -> live paper
 scholar      dataset   ml          stats         figrecipe  clew      writer        live-paper
```

The example compares logistic regression with an RBF support-vector
machine on MNIST. It is small on purpose (about two minutes on a laptop
CPU). What it shows is not the classifier but the record behind every
number: each result in the manuscript is a **registered claim** that points
to the file and the field it was read from, every file points to the run
that wrote it, and the **live paper** shows which of those links still hold.

## Quick start

```bash
scitex-template clone research ./my_project     # or: create a project in SciTeX Hub
cd my_project
make install                                    # SciTeX package version floors
scitex-writer containers install texlive -y     # LaTeX toolchain (once per machine)
make all                                        # the whole showcase
make live-paper                                 # serve it, with a guided tour
```

`make all` needs the network once: the MNIST file (11 MB, from the Keras
mirror, checked against its published SHA-256) and the writer workspace.
The manuscript build also needs a working `yq` on `PATH`, Apptainer for
the LaTeX container, and the Writer tools `latexdiff` and GNU `parallel`.
Install those system tools before running the showcase. Writer 2.44.1
and Clew 0.35.0 or later provide the claim-store integration used here.
Before `make all`, set `SCITEX_STORE_DSN` to a project database provisioned
for you by the deployment (see “Provenance store” below). Record the resolved
package versions when retaining a run; the requirements specify minimum
versions, not an environment lock.

## The live paper

`make live-paper` builds the paper, renders it with
[scitex-live-paper](https://github.com/ywatanabe1989/scitex-live-paper)
using the evidence that scitex-clew exports, and serves it on
http://127.0.0.1:8765/. Guided tour:

1. **Open `paper.html`**: the manuscript with every registered claim
   highlighted by its state. The claims navigator lists the claims that need
   inspection first; after a fresh `make all` there are none.
2. **Click a highlighted claim**, e.g. the SVM accuracy: the evidence panel
   shows its state, the stated vs the source value, the source file and the
   JSON pointer it was read from.
3. **Follow its minimal graph** in the same panel: claim <-
   `data/results/metrics.json` <- the training run <- the arrays <- the MNIST
   file scitex-dataset fetched (pinned as a trusted source by
   `make register-source`). Every claim has a deep link,
   `paper.html#claim-<id>`.
4. **Look for what is not highlighted.** "all 10,000 images of the official
   test set" in the Results was typed by hand and not registered, so it gets
   no verdict: the live paper assesses only registered claims.
5. **Break something**: `make demo-fault` hand-edits the SVM accuracy in
   `metrics.json`, shows that `clew verify --strict` fails, renders the
   faulty live paper to `data/live_paper/site-fault/` (the claims list names
   the claims whose source changed; each graph marks the CHANGED node), then
   restores the file and asserts its SHA-256 equals the original.

### What the live paper does not check

Only registered claims are assessed. A number typed into the text, a
sentence such as "the SVM outperformed logistic regression", or the
`p < 0.001` next to a registered chi-square is not checked. Registering a
number (an entry in `config/CLAIMS.yaml` and `\vclaim{<id>}` in the text)
is what makes it checkable.

## Steps

| `make` | What it does | Package |
|---|---|---|
| `refs` | Resolve and enrich `config/references_seed.bib` (ONLINE, optional; the result is committed) | scitex-scholar |
| `fetch` | Download MNIST once (sha256-checked, cached in `data/raw/`), draw the training subset | scitex-dataset, scitex-repro |
| `register-source` | Pin the downloaded file as a trusted source | scitex-clew |
| `train` | Logistic regression and RBF-SVM; accuracy, balanced accuracy, MCC | scitex-ml |
| `stats` | McNemar's test on the paired test-set outcomes | scitex-stats |
| `figures` | Three panels in mm (SCITEX style), composed from their recipes | figrecipe |
| `notebook` | The same contract in a notebook, executed and verified | scitex-notebook |
| `claims` | Register every number of `config/CLAIMS.yaml` with its locator | scitex-writer -> scitex-clew |
| `paper` | Compile `manuscript/` (linked into the writer workspace) to PDF | scitex-writer |
| `live-paper-build` | Bundle + clew evidence report + static site in `data/live_paper/site/` | scitex-live-paper |
| `verify` | `clew verify --strict`, then `clew slice <claim>` for each claim | scitex-clew |
| `lint` | SciTeX lint rules (research project) + ruff | scitex-dev |
| `test` | The project's tests | pytest |

Every script is a `@scitex_session.session` function; every file goes
through `scitex_io`, so clew records the inputs and outputs of each run
without explicit calls. Every parameter is in `config/*.yaml`, every path
in `config/PATH.yaml`.

## Layout

```
config/            parameters (MNIST, STATS, FIGURE, CLAIMS, SCHOLAR, HPC) and PATH.yaml
scripts/mnist/     00_resolve_references ... 05_register_claims (one step each)
notebooks/         notebook variant of one step
manuscript/        the paper's text (linked into the writer workspace by `make paper-init`)
data/              stable links to script outputs (scripts/**/<script>_out/)
scripts/demo/      the planted-fault demo
scripts/hpc/       optional Slurm dispatch
container/         optional Apptainer definition
tests/             tests of each step
.scitex/           local state: clew runtime, writer workspace (not committed)
```

## Provenance store

scitex-clew records runs and claims in the SciTeX PostgreSQL store:
`SCITEX_STORE_DSN` if set, otherwise the per-host default. To keep a
project's records separate, point `SCITEX_STORE_DSN` at a database of its
own, e.g. `postgresql://<user>@/<db>?host=<socket dir>&port=<port>`.

## Optional: HPC (`make hpc`)

`make hpc HPC_ACCOUNT=<account> HPC_PARTITION=<partition> [HPC_HOST=spartan]`
runs `scripts/mnist/02_train_classifiers.py` on a Slurm cluster through
scitex-hpc (sync, remote venv, `srun`, pull the outputs back). Resources are
in `config/HPC.yaml`.

Known gap: the remote run cannot reach this project's provenance store, so
it runs with recording off and its outputs come back without a recorded
run. `make verify` then reports them as having no lineage. That is the
correct answer until scitex-clew can import a remote run; run `make train`
locally to restore full lineage.

## Optional: container (`make container`)

Builds `container/research.sif` from `container/research.def` with
scitex-container: the project's Python environment as an Apptainer image.

## Submission (`make submit`)

Placeholder. Submission to the SciTeX agentic journal, where reviewers read
the live paper, is under development.

## Starting your own project

Keep the layout and the conventions, replace the example:

1. `make clean-outputs`, then add `scripts/<topic>/NN_<verb>_<object>.py`.
2. Put parameters in `config/<TOPIC>.yaml` and paths in `config/PATH.yaml`.
3. Declare the numbers you report in `config/CLAIMS.yaml` and write them as
   `\vclaim{<id>}` in `manuscript/`.
4. `make verify` before you call a result done.

## License

AGPL-3.0
