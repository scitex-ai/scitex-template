# Create a research project

```bash
scitex-template clone research ./my_project -y
cd my_project
python3 -m venv .venv
source .venv/bin/activate
make install-develop
make verify
make install-dev
make check
```

Use `make install` instead of `make install-develop` for published releases.
Record installed versions and source commits before an experiment.

The optional MNIST example is `make run-mnist`. `make solve` produces
measured claims and requires the configured managed PostgreSQL store.
`make verify-claims` checks the JSON schema only.

```bash
mkdir -p scripts/my_experiment
cp scripts/template.py scripts/my_experiment/01_analyze.py
make setup-writer
```

The manuscript lives under `.scitex/writer/`. `make clean` removes generated
script outputs, Python caches, and the DAG preview; it does not erase store
history or raw data. Remove optional example scripts deliberately if they
are not part of the new research project.
