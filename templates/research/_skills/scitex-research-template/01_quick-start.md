<!-- 01_quick-start.md -->

# Quick Start — Bootstrap a Research Project

## 1. Create the project

```bash
scitex-template clone research ./my_project      # or create it in SciTeX Hub
cd my_project
```

## 2. Install

```bash
make install            # pip install -r requirements.txt (pinned SciTeX floors)
```

The manuscript step needs a LaTeX toolchain; scitex-writer provides one as
an Apptainer image: `scitex-writer containers install texlive -y`.

## 3. Run the showcase

```bash
make all                # fetch -> train -> stats -> figures -> claims -> paper -> live paper -> verify
make live-paper         # serve the live paper and print a guided tour
make demo-fault         # plant a fault, see where the evidence breaks, restore
```

`make all` needs network once (the MNIST download, ~11 MB, sha256-checked,
and the writer workspace). Everything else runs offline on a CPU.

## 4. Start your own work

```bash
make clean-outputs      # drop the example's outputs (keeps the scripts)
mkdir scripts/my_topic
```

Write `@scitex_session.session` scripts (see
[11_writing-scripts.md](11_writing-scripts.md)), declare the numbers you
report in `config/CLAIMS.yaml`, and write them as `\vclaim{<id>}` in
`manuscript/` (see [12_showcase-flow.md](12_showcase-flow.md)).

## 5. Day-to-day

```bash
make verify             # clew verify --strict + minimal graph per claim
make lint               # scitex-dev linter + ruff
make test               # tests (run the pipeline for real)
```
