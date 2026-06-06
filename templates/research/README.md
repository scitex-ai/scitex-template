# SciTeX Research Template

A boilerplate template for scientific research projects using the [SciTeX](https://scitex.ai) framework.

## What is This?

This is a **template project** designed to be used as a starting point for your research. It demonstrates the standard SciTeX workflow with an MNIST example pipeline.

Part of the [scitex](https://github.com/ywatanabe1989/scitex-code) package (`scitex.template` module).

## Prerequisites

```bash
# Install scitex package
pip install scitex

# Verify installation
scitex --version
```

**Requirements:**
- Python >= 3.10
- scitex >= 2.0.0

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ywatanabe1989/scitex-research-template.git
cd scitex-research-template
make install    # Install project dependencies
make setup      # Full setup (install + verify)

# Run example pipeline
make run-mnist
```

## Project Structure

```
scitex-research-template/
├── .claude/             # AI agent configuration
│   ├── commands/        # Custom slash commands
│   └── skills/          # Domain-specific agent guidance
├── config/              # YAML configuration files
├── data/                # Centralized data storage (symlinked from scripts/*_out/)
├── scripts/             # Analysis scripts
│   ├── mnist/           # MNIST example pipeline
│   └── template.py      # Template for new scripts
├── tests/               # Test suite
├── scitex/              # SciTeX managed resources
│   ├── writer/          # Manuscript projects (LaTeX)
│   ├── scholar/         # Research notes & bibliography
│   ├── vis/             # Figure management
│   ├── code/            # Code templates
│   ├── ai/              # AI prompts & conversations
│   └── uploads/         # File uploads
├── management/          # Project management scripts
├── externals/           # External dependencies
├── docs/                # Documentation
├── GITIGNORED/          # Untracked working files (task tracking, agent notes)
├── .venv -> ~/.venv     # Python virtual environment (symlink)
└── Makefile             # Automation commands
```

## Using as a Template

1. **Clone or fork** this repository
2. **Remove MNIST example** if not needed: `make clean-mnist`
3. **Add your scripts** to `scripts/your_project/`
4. **Configure** paths in `config/PATH.yaml`
5. **Run** your analysis with `make run-your-script`

## Available Commands

<details>
<summary><strong>Setup & Installation</strong></summary>

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make install-dev` | Install with dev dependencies |
| `make setup` | Full setup (install + verify) |
| `make setup-writer` | Initialize manuscript project |
| `make verify` | Verify installation |

</details>

<details>
<summary><strong>Running Analysis</strong></summary>

| Command | Description |
|---------|-------------|
| `make run-mnist` | Run full MNIST pipeline |
| `make run-mnist-download` | Download MNIST data |
| `make run-mnist-plot-digits` | Plot sample digits |
| `make run-mnist-plot-umap` | Generate UMAP visualization |
| `make run-mnist-clf-svm` | Train SVM classifier |
| `make run-mnist-conf-mat` | Plot confusion matrix |

</details>

<details>
<summary><strong>Development</strong></summary>

| Command | Description |
|---------|-------------|
| `make test` | Run test suite |
| `make test-verbose` | Run tests with verbose output |
| `make format` | Format code (Python + Shell) |
| `make lint` | Run linters |
| `make check` | Format + lint + test |

</details>

<details>
<summary><strong>Cleanup</strong></summary>

| Command | Description |
|---------|-------------|
| `make clean` | Clean temporary files |
| `make clean-mnist` | Remove MNIST outputs |
| `make clean-outputs` | Remove all script outputs |
| `make clean-data` | Remove downloaded data |
| `make clean-logs` | Remove log files |
| `make clean-all` | Full cleanup |
| `make clean-python` | Remove Python cache |
| `make clean-writer` | Clean writer build files |

</details>

<details>
<summary><strong>Information</strong></summary>

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make info` | Show project information |
| `make tree` | Display directory tree |
| `make show-config` | Show configuration |

</details>

## SciTeX Directory (`scitex/`)

The `scitex/` directory integrates with [SciTeX Cloud](https://scitex.ai):

| Directory | Purpose | Setup |
|-----------|---------|-------|
| `writer/` | LaTeX manuscripts (00_shared, 01_manuscript, 02_supplementary, 03_revision) | `make setup-writer` |
| `scholar/` | Bibliography management and research library | Auto |
| `vis/` | Visualization workspace - figures, gallery templates | Auto |
| `code/` | Code templates and AI-assisted coding | Auto |
| `ai/` | AI prompts and conversation history | Auto |
| `uploads/` | File upload staging area | Auto |

## Manuscript Setup (Writer)


<details>
<summary><strong>Initialize Writer Project</strong></summary>

```bash
# Quick setup (recommended)
make setup-writer

# Or with specific git strategy
./management/scripts/setup-writer.sh --git-strategy child
```

**Git Strategies:**
| Strategy | Description |
|----------|-------------|
| `parent` | Use parent repository (default) |
| `child` | Create isolated git in writer directory |
| `origin` | Preserve template's original git history |
| `none` | No git initialization |

**After initialization:**
```
scitex/writer/
├── 00_shared/           # Shared resources (title, authors, bibliography)
├── 01_manuscript/       # Main manuscript
├── 02_supplementary/    # Supplementary materials
├── 03_revision/         # Revision responses
└── compile.sh           # LaTeX compilation script
```

**Compile manuscript:**
```bash
cd scitex/writer
./compile.sh manuscript    # or: scitex writer compile manuscript
```

</details>

## Symlink Architecture

This template uses symbolic links for DRY (Don't Repeat Yourself) principles and data provenance.

<details>
<summary><strong>Environment Symlinks</strong> - Shared user configurations</summary>

```
.venv -> ~/.venv          # Shared Python virtual environment
```

Points to user-level virtual environment, making the template portable across projects.

</details>

<details>
<summary><strong>AI Prompts Centralization</strong> - Single access point for all prompts</summary>

```
scitex/ai/prompts/
├── writer  -> ../../writer/ai/prompts
├── scholar -> ../../scholar/ai/prompts
├── code    -> ../../code/ai/prompts
└── vis     -> ../../vis/ai/prompts
```

All AI prompts are accessible from a central location while being organized by module.

</details>

<details>
<summary><strong>Writer Shared Resources</strong> - Edit once, sync everywhere (after <code>make setup-writer</code>)</summary>

```
scitex/writer/                       # Created by: make setup-writer
├── 00_shared/                       # Single source of truth
│   ├── title.tex
│   ├── authors.tex
│   ├── bibliography.bib
│   ├── keywords.tex
│   └── latex_styles/
├── 01_manuscript/contents/
│   ├── title.tex        -> ../../00_shared/title.tex
│   ├── authors.tex      -> ../../00_shared/authors.tex
│   └── bibliography.bib -> ../../00_shared/bibliography.bib
├── 02_supplementary/contents/       # Same symlinks
└── 03_revision/contents/            # Same symlinks
```

Edit `00_shared/` once, and all manuscript sections stay synchronized.

</details>

<details>
<summary><strong>Script Output to Data Links</strong> - Provenance tracking</summary>

```
data/mnist/
├── train_flattened.npy -> ../../scripts/mnist/download_out/data/mnist/train_flattened.npy
├── test_labels.npy     -> ../../scripts/mnist/download_out/data/mnist/test_labels.npy
├── models/
│   └── mnist_svm.pkl   -> ../../../scripts/mnist/clf_svm_out/data/mnist/models/mnist_svm.pkl
└── figures/
    └── umap.jpg        -> ../../../scripts/mnist/plot_umap_space_out/data/mnist/figures/umap.jpg
```

Script outputs (`*_out/`) are symlinked to `data/`, providing:
- **Provenance**: Know which script generated each file
- **Central access**: All data accessible from `data/` directory
- **Reproducibility**: Re-run script to regenerate linked output

</details>

## Creating New Scripts

<details>
<summary><strong>Script Template & Conventions</strong></summary>

Use the template as a starting point:

```bash
# Copy template
cp scripts/template.py scripts/my_analysis/01_preprocess.py

# Edit and run
python scripts/my_analysis/01_preprocess.py
```

**Conventions:**
- Numbered prefix for execution order: `01_`, `02_`, etc.
- Output directory: `{script_name}_out/`
- Use `main.sh` to orchestrate multiple steps

**MNIST Example Pipeline:**
```
scripts/mnist/
├── 01_download.py         # Download MNIST dataset
├── 02_plot_digits.py      # Visualize sample digits
├── 03_plot_umap_space.py  # UMAP dimensionality reduction
├── 04_clf_svm.py          # Train SVM classifier
├── 05_plot_conf_mat.py    # Plot confusion matrix
└── main.sh                # Run all steps sequentially
```

</details>

## Core Modules for Reproducibility

This template is powered by two essential SciTeX modules that ensure reproducible, standardized research.

<details>
<summary><strong>scitex.io</strong> - Universal I/O with automatic symlinks</summary>

**Philosophy**: "Load and save anything with one function"

```python
import scitex as stx

# Universal interface - format auto-detected from extension
data = stx.io.load("data.csv")      # DataFrame
model = stx.io.load("model.pth")    # PyTorch state
config = stx.io.load("config.yaml") # Dict

# Save with automatic directory creation
stx.io.save(df, "results.parquet")
stx.io.save(fig, "figure.png", dpi=300, auto_crop=True)
```

**Automatic Path Resolution:**

When using relative paths, `stx.io.save()` automatically organizes outputs under `{script_name}_out/`:

```python
# File: scripts/mnist/01_download.py

stx.io.save(train_data, "data/mnist/train.npy")
#                        ↓ Relative path
# Actual save location:  scripts/mnist/download_out/data/mnist/train.npy
#                        ^^^^^^^^^^^^^^^^^^^^^^^^^ Auto-generated from script name
```

**Symlink Parameters for Data Centralization:**

```python
# In scripts/mnist/01_download.py
stx.io.save(
    train_data,
    "data/mnist/train.npy",           # Saved to: scripts/mnist/download_out/data/mnist/train.npy
    symlink_to="../../data/mnist/"    # Symlinked to: ./data/mnist/train.npy (relative to script_out)
)
```

| Parameter | Description |
|-----------|-------------|
| `symlink_to` | Create symlink at specified path (relative to output location) |
| `symlink_from_cwd` | Create symlink from current working directory |

**Path Resolution Rules:**
1. **Relative path** (e.g., `"data/file.npy"`) → Saves to `{script}_out/{path}`
2. **Absolute path** (e.g., `"/tmp/file.npy"`) → Saves to exact path
3. **With `@stx.session`** → Saves under session directory (e.g., `script_out/RUNNING/A7K2/`)

This enables the provenance-tracking symlink architecture shown above.

**Supported Formats (27+):**
- Data: csv, tsv, parquet, json, yaml, pkl, joblib
- Arrays: npy, npz, hdf5, zarr, mat, nc
- ML: pth, pt, cbm (CatBoost), optuna
- Documents: txt, md, pdf, docx, xml, bib
- Images: png, jpg, tiff, gif (with auto-crop, metadata embedding)
- Bundles: figz, pltz, statsz

</details>

<details>
<summary><strong>scitex.session</strong> - Experiment lifecycle management</summary>

**Philosophy**: "Every run is reproducible and traceable"

```python
import scitex as stx

@stx.session(seed=42)
def main(
    CONFIG=stx.INJECTED,      # Session metadata (ID, paths, timestamps)
    plt=stx.INJECTED,         # Configured matplotlib
    COLORS=stx.INJECTED,      # Color palette
    rng_manager=stx.INJECTED, # Reproducible RNG (numpy, torch, random)
    logger=stx.INJECTED,      # Auto-logging to files
):
    print(f"Session: {CONFIG['ID']}")  # e.g., "A7K2"

    # All stdout/stderr captured to logs/
    # Random seeds fixed across all libraries
    # Output directory auto-managed

if __name__ == "__main__":
    main()
```

**Session Directory Structure:**

```
script.py
script_out/
├── RUNNING/              # Active sessions
│   └── A7K2/             # 4-char session ID
│       ├── logs/
│       │   ├── stdout.log
│       │   └── stderr.log
│       ├── CONFIGS/
│       │   └── CONFIG.yaml
│       └── [your outputs]
├── FINISHED_SUCCESS/     # Completed successfully
└── FINISHED_ERROR/       # Completed with errors
```

**Features:**
- Unique session IDs for every run
- Automatic stdout/stderr capture
- Fixed random seeds (numpy, torch, random, os)
- Runtime tracking and timestamps
- Exit status classification

</details>

<details>
<summary><strong>How They Work Together</strong> - Complete workflow</summary>

```
┌─────────────────────────────────────────────────────────────────┐
│  scripts/mnist/01_download.py                                   │
│                                                                  │
│  @stx.session(seed=42)                                          │
│  def main(CONFIG, plt, ...):                                    │
│      data = download_mnist()                                    │
│      stx.io.save(data, "data/mnist/train.npy",                 │
│                  symlink_to="../../data/mnist/")               │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  scripts/mnist/download_out/                                     │
│  └── FINISHED_SUCCESS/                                          │
│      └── A7K2/                    <- Session tracking           │
│          ├── logs/                                              │
│          │   ├── stdout.log       <- All prints captured        │
│          │   └── stderr.log                                     │
│          ├── CONFIGS/                                           │
│          │   └── CONFIG.yaml      <- Reproducibility record     │
│          └── data/mnist/                                        │
│              └── train.npy        <- Actual file                │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ symlink
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  data/mnist/                                                     │
│  └── train.npy -> ../../scripts/mnist/download_out/.../train.npy│
│                                                                  │
│  Central access with provenance tracking                        │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- **Provenance**: Every file traces back to its generating script and session
- **Reproducibility**: Re-run with same seed = same results
- **Central Access**: All data accessible from `./data/`
- **Logging**: Complete record of every run

</details>

## Key Features

- **Standardized structure** for reproducible research
- **Automated workflows** via Makefile
- **Manuscript management** with LaTeX compilation
- **Testing framework** included
- **Figure provenance** tracking via symlinks
- **AI integration** for coding assistance

## AI Agent Integration

This template supports AI coding agents (e.g., Claude Code) out of the box:

- **`CLAUDE.md`** at the project root provides project context and instructions to the agent.
- **`.claude/skills/`** contains domain-specific guidance files that agents can load for specialized tasks.
- **`.claude/commands/`** contains custom slash commands for common workflows.
- **`GITIGNORED/`** is where agents store task tracking, working notes, and intermediate files. This directory is gitignored and not committed.

> **Note:** The `_skills/` directory is deprecated. Domain-specific agent guidance has moved to `.claude/skills/`.

## Documentation

- [SciTeX Documentation](https://scitex.ai)
- [SciTeX GitHub](https://github.com/ywatanabe1989/scitex-code)
- [MNIST Example README](scripts/mnist/README.md)

**scitex-code Examples (for deeper understanding):**
- [`examples/session/demo_session_plt_io.py`](https://github.com/ywatanabe1989/scitex-code/blob/main/examples/session/demo_session_plt_io.py) - Complete session + io + symlink demo
- [`examples/session/COMPARISON.md`](https://github.com/ywatanabe1989/scitex-code/blob/main/examples/session/COMPARISON.md) - Manual vs decorator comparison
- [`src/scitex/io/README.md`](https://github.com/ywatanabe1989/scitex-code/blob/main/src/scitex/io/README.md) - Full I/O documentation
- [`src/scitex/session/README.md`](https://github.com/ywatanabe1989/scitex-code/blob/main/src/scitex/session/README.md) - Session management details

## License

AGPL-3.0

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)


## Clew-aware MNIST pipeline (validated 2026-05-30 by end-to-end run)

This template's MNIST example is now a clew-aware, validity-gated DAG:
each metric in `data/results/claims.json` back-propagates through the
Clew DAG to source data on disk. `make solve` actually runs the
pipeline (no synthetic shortcuts) and produces real claims.

### Layout (after this PR)

```
templates/research/
├── .gitignore
├── .scitex/clew/        # local-state convention — Clew DB / runtime
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE
├── Makefile
├── README.md
├── _skills/             # agent guidance (unchanged)
├── config/
│   ├── MNIST.yaml       # CONFIG.MNIST namespace (BATCH_SIZE, NORMALIZE,
│   │                    #   RANDOM_STATE, SVM_TRAIN_SUBSET, ...)
│   └── PATH.yaml        # CONFIG.PATH namespace (no outer `PATH:` wrapper)
├── data/
│   ├── mnist/           # populated by 01_download.py
│   └── results/         # claims.json (DAG terminus)
├── docs/
├── externals/
├── requirements.txt     # NEW — scitex / torch / sklearn / umap-learn / ...
├── scripts/
│   ├── mnist/           # 5 existing verb-named stages + 06_register_claims (NEW)
│   │   ├── 01_download.py
│   │   ├── 02_plot_digits.py
│   │   ├── 03_plot_umap_space.py
│   │   ├── 04_clf_svm.py             # +SVM_TRAIN_SUBSET subsample + metrics.json
│   │   ├── 05_plot_conf_mat.py
│   │   ├── 06_register_claims.py     # NEW — DAG terminus + scitex_clew.add_claim
│   │   └── main.sh
│   └── verify/                       # NEW — agent-vs-verify split
│       └── check_schema.py
├── template.yaml
└── tests/
```

### `make solve` flow

```bash
make solve              # downloads MNIST (once), trains SVM, emits claims.json
make verify-claims      # plain-Python schema check on claims.json
make clean-clew         # drop the Clew SQLite DB only
```

The recipe (`solve: clean-clew`):

1. Idempotent guard: if `data/mnist/train_flattened.npy` is missing,
   run `01_download.py` (downloads ~9.5 MB MNIST → flattens → saves
   ~400 MB of npy/pkl into `output/data/mnist/` with stable symlinks
   under `data/mnist/`).
2. Always run `04_clf_svm.py`: trains a subsample-size RBF SVM
   (controlled by `CONFIG.MNIST.SVM_TRAIN_SUBSET`, default 500 in this
   template — full MNIST + RBF is hours). Writes
   `data/mnist/classification_report.csv` (writer-friendly) AND
   `data/mnist/metrics.json` (the clew-DAG node consumed downstream).
3. `06_register_claims.py` reads `data/mnist/metrics.json`, writes the
   canonical `data/results/claims.json` ({claims:[...]} contract), and
   registers each claim via `scitex_clew.add_claim(file_path=...,
   claim_type=..., source_file=...)`.

### What `make solve` actually produces (verified)

```bash
$ time make solve
…
SUCC: Registering real metrics from …/data/mnist/metrics.json:
    {'accuracy': 0.8711, 'macro_f1': 0.86935046024982}
INFO: Wrote 2 claims -> …/data/results/claims.json
DONE n_claims=2
INFO: Congratulations! The script completed: FINISHED_SUCCESS/…
make solve rc=0 wall=23s

$ make verify-claims
OK schema: 2 claims, all required keys present

$ cat data/results/claims.json
{
  "claims": [
    {"question":"test_accuracy", "answer":"0.871100", "answer_type":"number"},
    {"question":"test_macro_f1", "answer":"0.869350", "answer_type":"number"}
  ]
}
```

### Bugs the dogfooding surfaced (and fixed in the template)

1. `make install` referenced a missing `requirements.txt` → added.
2. The Makefile recipes did `cd $(MNIST_DIR) && python …` — scitex
   then looked for `scripts/mnist/config/` and couldn't find it
   (`'DotDict' object has no attribute 'MNIST'`). Fix: run python
   from the project root via `python3 $(MNIST_DIR)/0X_*.py`.
2.   The `management/scripts/run-mnist.sh` dispatcher previously
   masked this by setting `MNIST_DIR` via `GIT_ROOT` — once
   `management/` was removed (operator brief), the latent bug
   surfaced. The new Makefile recipes do the right thing inline.
3. Stage 04's `classification_report.csv` is dataframe-shaped (columns
   are class labels + macro/weighted/accuracy; rows are
   precision/recall/f1/support; no row index). Stage 06's CSV-keyed
   lookup (`df.loc["accuracy"]`) silently failed → fell back to
   synthetic. Fix: stage 04 now ALSO writes a compact
   `metrics.json` (`{accuracy, macro_f1}`) as the stable clew DAG
   node; stage 06 reads that JSON directly. The CSV stays for the
   writer / paper.
4. Full MNIST + RBF SVM trains for hours. Fix:
   `CONFIG.MNIST.SVM_TRAIN_SUBSET` (default 500) slices the train
   set for `make solve` smokes; set to None / unset for full
   training on a long-running CI host.

### Refactor caveats (NOT fixed; scitex source is read-only)

`scitex_session._lifecycle._config` calls `stx.io.save(..., track=...)`
on the auto-dumped `CONFIG.pkl` / `CONFIG.yaml`. The `track=` kwarg was
removed from `scitex_io._save_pickle` / `_save_yaml` in the SoC refactor.
Result: two `ERRO: _save_*() got an unexpected keyword argument 'track'`
log lines on every `@stx.session` lifecycle. They are
**logged-but-handled** — the session reaches `FINISHED_SUCCESS` and the
script exits 0. Surfaced for the refactor owners; no template change
required.

