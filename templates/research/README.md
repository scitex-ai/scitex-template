# SciTeX Research Template

A reusable research-project scaffold with an optional MNIST example. Clone it,
replace the example with your research, and commit the code, configuration,
data references, manuscript sources, and environment lock together.

## Start a project

```bash
pip install scitex-template
scitex-template clone research my-research -y
cd my-research
python -m venv .venv
. .venv/bin/activate
make install
make verify
```

The template payload is maintained in
[scitex-ai/scitex-template](https://github.com/scitex-ai/scitex-template/tree/develop/templates/research).
Use `make install-develop` to install the current standalone SciTeX packages
from their `develop` branches. After validation, freeze the resolved versions
and source commits in your project's environment lock. Branches move; a
recorded commit identifies the implementation used for a result.

The example imports standalone packages. The umbrella package currently pins
older leaf releases, so installing it together with these requirements can
produce a dependency conflict or downgrade the working packages.

## Layout

```text
my-research/
├── .scitex/             # package-owned project configuration and workspaces
│   ├── clew/runtime/    # regenerable file outputs; not a database
│   └── template/       # clone provenance manifest; runtime/ for cache files
├── config/              # analysis parameters and data paths
├── data/                # inputs and stable links to generated outputs
├── docs/                # project documentation
├── externals/           # external research resources
├── scripts/             # analysis code and script starter
├── tests/               # tests for this project's analysis
├── _skills/             # bundled guidance for this template
├── requirements.txt
├── requirements-develop.txt
└── Makefile
```

Use `<project-root>/.scitex/<package>/` for project settings and
`~/.scitex/<package>/` for user settings. Packages resolve these scopes through
their supported APIs. Keep project configuration in git; ignore generated
`runtime/` files while retaining their directory seeds. See
[.scitex/README.md](.scitex/README.md) for the storage and access-control boundary.
The template does not create user configuration or include deployment secrets.

## Run the optional example

```bash
make run-mnist          # download, analyze, and plot MNIST
make solve              # download, fit SVM, and register measured claims
make verify-claims      # validate the generated claim-file schema
```

The SVM example uses `config/MNIST.yaml` and `config/PATH.yaml`. Missing measured
metrics are an error: claim registration never substitutes synthetic results.
Schema validation checks the file shape; it does not establish provenance or
scientific correctness. Use the current Clew verification API to inspect the
recorded claim-to-source chain.

## Write research code

Copy `scripts/template.py` and use numbered stages for your own pipeline.

```python
import scitex_io as io
import scitex_session as session

@session.session(seed=42)
def main(CONFIG=session.INJECTED, logger=session.INJECTED):
    data = io.load("data/input.csv")
    io.save(data, "results.csv")
    return 0

if __name__ == "__main__":
    main()
```

The session decorator and I/O package record execution and file dependencies.
Use FigRecipe for figures whose data and styling remain separate. Check the
installed packages' API and CLI help when extending the workflow.

## Manuscript workspace

```bash
make setup-writer       # explicitly create .scitex/writer/ in this project
scitex-writer compile manuscript --project .
```

Writer owns `.scitex/writer/`, including `00_shared/`, `01_manuscript/`,
`02_supplementary/`, and `03_revision/`. The template clones no manuscript
until requested. An optional `paper -> .scitex/writer` symlink is a project
choice, not required by this scaffold.

## Managed state and Cloud access

Packages that adopt the ecosystem store use `scitex_dev.store`, backed by
managed PostgreSQL on port `55432`. `.scitex/` directories hold configuration,
research files, and regenerable file outputs; deleting one does not reset
that database. `make clean-clew` removes only the generated DAG visualization.

Database provisioning belongs to the deployment. On SciTeX Hub/Cloud, the
authenticated user's stable identity must select an authorized store, and
read/write grants must be enforced before access. A shared PostgreSQL writer
role does not establish user isolation. Missing identity or grants must deny
access; unavailable authorization data must fail visibly. Do not expose the
host fleet store or copy administrator credentials into a research project.
Cross-user denial must be tested in the deployment before store access is
opened to Cloud users.

## Development

```bash
make install-dev
make test
make lint
make check
```

Use this template as a starting point. Benchmark submission rules, oracle
paths, host deployment settings, and published research results belong to
the consuming project, not this shared scaffold.
