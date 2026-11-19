# ============================================
# SciTeX Research Template - Makefile
# ============================================
# The MNIST showcase runs the SciTeX ecosystem end to end:
#
#   literature -> data -> analysis -> statistics -> figures -> claims
#              -> manuscript -> live paper
#
#   make all          everything below, offline except the first data fetch
#   make live-paper   build the live paper and serve it (guided tour)
#   make verify       clew verify --strict + the minimal graph of each claim
#   make demo-fault   plant a fault, watch the live paper flag it, restore
#
# Provenance store: scitex-clew records runs in the SciTeX PostgreSQL store
# (SCITEX_STORE_DSN, else the per-host default). See README "Provenance store".

.PHONY: \
	help install install-dev \
	all run refs fetch register-source train stats figures notebook claims \
	paper-init paper live-paper-build live-paper verify slice demo-fault \
	hpc container submit \
	lint format test clean clean-outputs clean-paper clean-all info tree

.DEFAULT_GOAL := help
# The pipeline steps are ordered; never run them concurrently (even with -j).
.NOTPARALLEL:

PYTHON     ?= python3
CLEW       ?= clew
WRITER     ?= scitex-writer
LIVE_PAPER ?= scitex-live-paper
LINTER     ?= scitex-dev linter
MNIST_DIR  := scripts/mnist
WORKSPACE  := .scitex/writer
BUNDLE     := data/live_paper/bundle
SITE       := data/live_paper/site
LP_HOST    ?= 127.0.0.1
LP_PORT    ?= 8765
CLAIM_IDS   = $$($(PYTHON) -c "import yaml;print(' '.join(i['ID'] for i in yaml.safe_load(open('config/CLAIMS.yaml'))['ITEMS']))")

help:
	@echo ""
	@echo "SciTeX research template - MNIST showcase"
	@echo ""
	@echo "  make install           Install the pinned SciTeX packages (requirements.txt)"
	@echo "  make all               Run the whole showcase end to end (about 2 min on a CPU)"
	@echo "  make live-paper        Build the live paper and serve it on http://$(LP_HOST):$(LP_PORT)/"
	@echo "  make verify            clew verify --strict, then the minimal graph of each claim"
	@echo "  make demo-fault        Plant a fault, render the live paper of it, restore (hash-checked)"
	@echo ""
	@echo "  Steps:  refs (online, optional) | fetch | register-source | train | stats"
	@echo "          figures | notebook | claims | paper-init | paper | live-paper-build"
	@echo "  Optional: hpc (Slurm via scitex-hpc) | container (Apptainer) | submit (placeholder)"
	@echo "  Quality:  lint | test | format"
	@echo "  Cleanup:  clean-outputs | clean-paper | clean-all"
	@echo ""

# ============================================
# Installation
# ============================================
install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install pytest ruff

# ============================================
# The showcase, end to end
# ============================================
all: run claims paper live-paper-build verify
	@echo ""
	@echo "Done. Next: make live-paper   (then follow the guided tour it prints)"

run: fetch register-source train stats figures notebook

# 0. Literature (ONLINE, optional): resolve + enrich the bibliography with
#    scitex-scholar. Its result is committed, so `make all` does not need it.
refs:
	$(PYTHON) $(MNIST_DIR)/00_resolve_references.py

# 1. Data: scitex-dataset fetch (sha256-checked, cached, recorded)
fetch:
	$(PYTHON) $(MNIST_DIR)/01_fetch_mnist.py

# Pin the downloaded file as a trusted source: claims are then green only if
# their provenance chain reaches it (clew's registered-source gate).
register-source:
	$(CLEW) register-source --yes data/raw/mnist/mnist.npz

# 2-4. Analysis (scitex-ml), statistics (scitex-stats), figures (figrecipe)
train:
	$(PYTHON) $(MNIST_DIR)/02_train_classifiers.py

stats:
	$(PYTHON) $(MNIST_DIR)/03_compare_classifiers.py

figures:
	$(PYTHON) $(MNIST_DIR)/04_plot_figure.py

# Notebook variant of one step (scitex-notebook): executed top to bottom,
# recorded like a script, then its cell DAG is checked.
notebook:
	$(CLEW) execute-notebook notebooks/01_count_classes.ipynb --cwd .
	scitex-notebook check-notebook notebooks/01_count_classes.ipynb
	scitex-notebook verify-notebook notebooks/01_count_classes.ipynb

# 5. Claims: register every number of config/CLAIMS.yaml (writer -> clew)
claims: paper-init
	$(PYTHON) $(MNIST_DIR)/05_register_claims.py

# 6. Manuscript (scitex-writer). paper-init creates the writer workspace once
#    (network), copies the manuscript text from manuscript/ into it (the
#    source of truth is manuscript/: workspace copies are overwritten on every
#    run; writer needs real files there to locate each \vclaim), and links
#    Figure 1 and the resolved bibliography into it.
paper-init:
	@test -d $(WORKSPACE)/00_shared || $(WRITER) create-project . --yes
	@# writer's compile engine needs the workspace inside a git repo (it exits
	@# 128 otherwise); create-project does not always initialise one.
	@git -C $(WORKSPACE) rev-parse --show-toplevel >/dev/null 2>&1 || git -C $(WORKSPACE) init -q
	@cd manuscript && find . -type f -name '*.tex' | while read -r f; do \
		mkdir -p "../$(WORKSPACE)/$$(dirname "$$f")"; \
		rm -f "../$(WORKSPACE)/$$f"; cp -f "$$f" "../$(WORKSPACE)/$$f"; \
	done
	@rm -f $(WORKSPACE)/01_manuscript/contents/figures/caption_and_media/0[12]_*example*.tex \
		$(WORKSPACE)/01_manuscript/contents/figures/caption_and_media/02_another_example.tex \
		$(WORKSPACE)/01_manuscript/contents/tables/caption_and_media/01_example_table.*
	@ln -sfn "$$(realpath data/figures/fig1_mnist.png)" \
		$(WORKSPACE)/01_manuscript/contents/figures/caption_and_media/01_mnist_overview.png
	@ln -sfn "$$(realpath data/literature/references.bib)" \
		$(WORKSPACE)/00_shared/bib_files/references.bib
	@echo "writer workspace ready: $(WORKSPACE)  (manuscript text: manuscript/)"

paper: claims
	$(WRITER) compile-manuscript -p . --yes
	@echo "PDF: $(WORKSPACE)/01_manuscript/manuscript.pdf"

# 7. Live paper (scitex-live-paper, evidence from scitex-clew)
live-paper-build: paper
	@rm -rf $(BUNDLE) $(SITE)
	@mkdir -p $(BUNDLE)/figz
	cp -f $(WORKSPACE)/01_manuscript/manuscript.pdf $(BUNDLE)/manuscript.pdf
	cp -f data/figures/fig1_mnist.png $(BUNDLE)/figz/fig1_mnist.png
	$(CLEW) export-claims --path $(BUNDLE)/claims.json --no-read-only
	$(CLEW) export-evidence --out $(BUNDLE)/evidence-report.json
	$(LIVE_PAPER) validate $(BUNDLE)
	$(LIVE_PAPER) render $(BUNDLE) --out $(SITE) \
		--evidence-report $(BUNDLE)/evidence-report.json \
		--title "MNIST showcase" --project-label "$$(basename "$$PWD")"
	@echo "live paper: $(SITE)/index.html"

live-paper: live-paper-build
	@echo ""
	@echo "Guided tour of the live paper:"
	@echo "  1. Open http://$(LP_HOST):$(LP_PORT)/paper.html -- the manuscript with every"
	@echo "     registered claim highlighted. The claims navigator lists the claims"
	@echo "     that need inspection first (after a fresh 'make all': none)."
	@echo "  2. Click a highlighted claim (e.g. the SVM accuracy): the evidence panel"
	@echo "     shows its state, stated vs source value, file and JSON pointer, and"
	@echo "     its minimal graph: claim <- metrics.json <- training run <- arrays"
	@echo "     <- the MNIST file scitex-dataset fetched (sha256-pinned source)."
	@echo "     Deep link: http://$(LP_HOST):$(LP_PORT)/paper.html#claim-svc_accuracy"
	@echo "  3. '10,000 images of the official test set' in the Results is NOT highlighted:"
	@echo "     it was typed by hand and not registered, so the live paper says nothing about it."
	@echo "  4. Then run 'make demo-fault' and open data/live_paper/site-fault/paper.html:"
	@echo "     the changed claims move to the top, and their graph marks where the"
	@echo "     evidence broke (the CHANGED metrics.json)."
	@echo ""
	cd $(SITE) && $(PYTHON) -m http.server $(LP_PORT) --bind $(LP_HOST)

# ============================================
# Verification
# ============================================
verify:
	$(CLEW) verify --strict
	@$(MAKE) --no-print-directory slice

slice:
	@for id in $(CLAIM_IDS); do \
		echo "== minimal graph of claim $$id"; \
		$(CLEW) slice $$id || exit 1; \
	done

demo-fault:
	PYTHON=$(PYTHON) CLEW=$(CLEW) LIVE_PAPER=$(LIVE_PAPER) bash "$(CURDIR)/scripts/demo/plant_fault.sh"

# ============================================
# Optional: HPC, container, submission
# ============================================
# Run the compute-heavy step (02_train_classifiers.py) on a Slurm cluster
# through scitex-hpc. See README "Optional: HPC" -- the remote run is not yet
# recorded by clew, so `make verify` reports the synced outputs as having no
# lineage until clew can import a remote run.
HPC_HOST ?= spartan
HPC_ACCOUNT ?=
HPC_PARTITION ?=
hpc:
	@test -n "$(HPC_ACCOUNT)" -a -n "$(HPC_PARTITION)" || \
		{ echo "set HPC_ACCOUNT and HPC_PARTITION (e.g. make hpc HPC_ACCOUNT=punim0000 HPC_PARTITION=sapphire)"; exit 2; }
	$(PYTHON) scripts/hpc/run_on_slurm.py --host $(HPC_HOST) \
		--account $(HPC_ACCOUNT) --partition $(HPC_PARTITION)

# Apptainer image with this project's Python environment (scitex-container).
container:
	$(PYTHON) -c "import scitex_container.apptainer as a; print(a.build(def_path='container/research.def', output_dir='container', image_name='research', force=True, cwd='.'))"

submit:
	@echo "make submit: placeholder. Submission to the SciTeX agentic journal"
	@echo "(reviewers read the live paper) is under development; see README."

# ============================================
# Quality
# ============================================
lint:
	$(LINTER) validate-files scripts
	$(LINTER) validate-files tests
	ruff check scripts tests

format:
	ruff format scripts tests

test:
	$(PYTHON) -m pytest tests -q

# ============================================
# Cleanup
# ============================================
clean-outputs:
	find scripts notebooks -type d -name '*_out' ! -name '00_resolve_references_out' -prune -exec rm -rf {} +
	find data/mnist data/results -mindepth 1 ! -name .gitkeep -delete
	rm -rf data/figures data/live_paper

clean-paper:
	rm -rf $(WORKSPACE)

clean-all: clean-outputs clean-paper
	rm -rf data/raw .scitex/clew/runtime

info:
	@echo "Project: $$(basename "$$PWD")"
	@echo "Python:  $$($(PYTHON) --version 2>&1)"
	@echo "Scripts: $$(ls $(MNIST_DIR)/*.py | wc -l) in $(MNIST_DIR)"
	@echo "Claims:  $(CLAIM_IDS)"

tree:
	@tree -L 3 -I '__pycache__|*_out|.git|.venv' 2>/dev/null || ls -R

# EOF
