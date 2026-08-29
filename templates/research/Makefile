# ============================================
# SciTeX Template Research - Makefile
# ============================================
# Scientific research project workflow automation
# Location: /Makefile
#
# Key Features:
# - Script execution and pipeline management
# - Dependency installation and environment setup
# - Output cleaning and data management
# - Code formatting and quality checks
# - Testing automation
#
# Usage:
#   make help                      # Show this help
#   make install                   # Install dependencies
#   make run-mnist                 # Run MNIST example pipeline
#   make clean                     # Clean outputs
#   make format                    # Format code
#   make test                      # Run tests

.PHONY: \
	help \
	install \
	install-dev \
	setup \
	setup-writer \
	run-mnist \
	run-mnist-download \
	run-mnist-plot-digits \
	run-mnist-plot-umap \
	run-mnist-clf-svm \
	run-mnist-conf-mat \
	solve \
	verify-claims \
	clean-clew \
	clean \
	clean-mnist \
	clean-outputs \
	clean-data \
	clean-logs \
	clean-all \
	clean-python \
	clean-writer \
	test \
	test-verbose \
	test-sync \
	format \
	format-python \
	format-shell \
	lint \
	lint-python \
	check \
	info \
	tree \
	verify \
	show-config

.DEFAULT_GOAL := help

# ============================================
# Configuration
# ============================================
PYTHON := python3
PIP := pip3
SCRIPTS_DIR := scripts
MNIST_DIR := $(SCRIPTS_DIR)/mnist
CONFIG_DIR := config
DATA_DIR := data
TESTS_DIR := tests

# ============================================
# Help
# ============================================
help:
	@echo ""
	@echo "############################################################"
	@echo "#      SciTeX Template Research - Makefile                 #"
	@echo "############################################################"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install                       # Install Python dependencies"
	@echo "  make install-dev                   # Install dev dependencies (testing, linting)"
	@echo "  make setup                         # Complete setup (install + verify)"
	@echo "  make setup-writer                  # Clone writer template project (example_paper)"
	@echo ""
	@echo "Running Scripts:"
	@echo "  make run-mnist                     # Run complete MNIST pipeline"
	@echo "  make run-mnist-download            # Download MNIST data"
	@echo "  make run-mnist-plot-digits         # Plot MNIST digits"
	@echo "  make run-mnist-plot-umap           # Create UMAP visualization"
	@echo "  make run-mnist-clf-svm             # Train SVM classifier"
	@echo "  make run-mnist-conf-mat            # Plot confusion matrix"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean                         # Clean script outputs"
	@echo "  make clean-mnist                   # Clean MNIST outputs only"
	@echo "  make clean-outputs                 # Clean all *_out directories"
	@echo "  make clean-data                    # Clean generated data files"
	@echo "  make clean-logs                    # Clean log files"
	@echo "  make clean-writer                  # Remove writer projects (use with caution!)"
	@echo "  make clean-all                     # Clean everything (outputs + data + cache)"
	@echo "  make clean-python                  # Clean Python cache files"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format                        # Format all code (Python + Shell)"
	@echo "  make format-python                 # Format Python with ruff"
	@echo "  make format-shell                  # Format shell with shfmt + shellcheck"
	@echo "  make lint                          # Lint code with ruff"
	@echo "  make check                         # Run format + lint + test"
	@echo ""
	@echo "Testing:"
	@echo "  make test                          # Run all tests"
	@echo "  make test-verbose                  # Run tests with verbose output"
	@echo "  make test-sync                     # Sync test structure with scripts"
	@echo ""
	@echo "Information:"
	@echo "  make info                          # Show project information"
	@echo "  make tree                          # Show project structure"
	@echo "  make verify                        # Verify installation and config"
	@echo "  make show-config                   # Display configuration files (requires yq)"
	@echo ""

# ============================================
# Installation & Setup
# ============================================
install:
	@echo "Installing Python dependencies..."
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
		echo "Dependencies installed"; \
	else \
		echo "requirements.txt not found"; \
		exit 1; \
	fi

install-dev:
	@echo "Installing development dependencies..."
	@$(PIP) install pytest pytest-cov ruff black isort mypy
	@echo "Development dependencies installed"

setup: install
	@echo "Setting up project..."
	@mkdir -p $(DATA_DIR)
	@mkdir -p $(DATA_DIR)/mnist/figures
	@mkdir -p $(DATA_DIR)/mnist/models
	@mkdir -p $(DATA_DIR)/mnist/raw
	@echo "Project setup complete"
	@$(MAKE) verify
	@echo ""
	@echo "To create a writer project, run:"
	@echo "  make setup-writer"
	@echo ""


verify:
	$(MAKE) verify-claims

# ============================================
# Running MNIST Scripts
# ============================================
run-mnist: run-mnist-download run-mnist-plot-digits run-mnist-plot-umap run-mnist-clf-svm run-mnist-conf-mat
	@echo "MNIST pipeline complete."

run-mnist-download:
	$(PYTHON) $(MNIST_DIR)/01_download.py

run-mnist-plot-digits:
	$(PYTHON) $(MNIST_DIR)/02_plot_digits.py

run-mnist-plot-umap:
	$(PYTHON) $(MNIST_DIR)/03_plot_umap_space.py

run-mnist-clf-svm:
	$(PYTHON) $(MNIST_DIR)/04_clf_svm.py

run-mnist-conf-mat:
	$(PYTHON) $(MNIST_DIR)/05_plot_conf_mat.py

# --- Clew DAG terminus (agent target) -----------------------------------
# `make solve` runs the real Clew DAG end-to-end:
#   01_download.py   -> data/mnist/{*_flattened,*_labels}.npy (MNIST source)
#   04_clf_svm.py    -> data/mnist/classification_report.csv (subsample-trained
#                        SVM; set CONFIG.MNIST.SVM_TRAIN_SUBSET to control size)
#   06_register_claims.py -> data/results/claims.json + scitex_clew.add_claim
# The decorative stages (02_plot_digits, 03_plot_umap_space, 05_plot_conf_mat)
# are NOT part of the validity-gate DAG; run them separately via
# `make run-mnist` for the full pipeline including figures.
solve: clean-clew
	@test -L data/mnist/train_flattened.npy || $(PYTHON) $(MNIST_DIR)/01_download.py
	$(PYTHON) $(MNIST_DIR)/04_clf_svm.py
	$(PYTHON) $(MNIST_DIR)/06_register_claims.py

# `make verify` is plain-Python (out-of-band; NOT in the agent's Clew DAG).
verify-claims:
	$(PYTHON) scripts/verify/check_schema.py

clean-clew:
	@rm -f .scitex/clew/runtime/clew.db* 2>/dev/null || true

# ============================================
# Cleaning
# ============================================
clean:
	@$(MGMT_SCRIPTS)/clean.sh

clean-mnist:
	$(MAKE) clean-data clean-outputs

clean-outputs:
	find scripts -type d -name '*_out' -prune -exec rm -rf {} + 2>/dev/null || true

clean-data:
	rm -rf data/mnist 2>/dev/null || true

clean-logs:
	find . -name '*.log' -type f -delete 2>/dev/null || true

clean-all:
	$(MAKE) clean-outputs clean-data clean-logs clean-python clean-clew

clean-python:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true; find . -name '*.pyc' -delete 2>/dev/null || true


# ============================================
# Testing
# ============================================
test:
	@echo "Running tests..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest $(TESTS_DIR) -q; \
	else \
		echo "pytest not installed. Run: make install-dev"; \
		exit 1; \
	fi

test-verbose:
	@echo "Running tests (verbose)..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest $(TESTS_DIR) -v; \
	else \
		echo "pytest not installed. Run: make install-dev"; \
		exit 1; \
	fi

test-sync:
	@echo "Synchronizing test structure with scripts..."
	@$(TESTS_DIR)/sync_tests_with_scripts.sh
	@echo "Test synchronization complete"

# ============================================
# Code Quality
# ============================================
format: format-python format-shell
	@echo ""
	@echo "All formatting and linting complete!"

format-python:
	@echo "Formatting Python code with ruff..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format $(SCRIPTS_DIR) $(TESTS_DIR) --quiet || echo "Ruff formatting completed with warnings"; \
		echo "Python formatting complete"; \
	else \
		echo "Ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi

format-shell:
	@echo "Formatting and linting shell scripts..."
	@if command -v shfmt >/dev/null 2>&1; then \
		find $(SCRIPTS_DIR) $(MGMT_SCRIPTS) -name "*.sh" \
			! -path "*/node_modules/*" \
			! -path "*/.venv/*" \
			-exec shfmt -w -i 4 -bn -ci -sr {} + \
			2>&1 || echo "shfmt formatting completed with warnings"; \
		echo "Shell formatting complete!"; \
	else \
		echo "shfmt not found. Install with: go install mvdan.cc/sh/v3/cmd/shfmt@latest"; \
		echo "Skipping shell formatting..."; \
	fi
	@if command -v shellcheck >/dev/null 2>&1; then \
		find $(SCRIPTS_DIR) $(MGMT_SCRIPTS) -name "*.sh" \
			! -path "*/node_modules/*" \
			! -path "*/.venv/*" \
			-exec shellcheck --severity=error {} + \
			2>&1 || echo "ShellCheck found errors"; \
		echo "Shell linting complete!"; \
	else \
		echo "shellcheck not found. Install with: sudo apt-get install shellcheck"; \
		echo "Skipping shell linting..."; \
	fi

lint: lint-python

lint-python:
	@echo "Linting Python code with ruff..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check $(SCRIPTS_DIR) $(TESTS_DIR) --quiet || echo "Ruff found issues"; \
		echo "Linting complete"; \
	else \
		echo "Ruff not found. Install with: pip install ruff"; \
		exit 1; \
	fi

check: format lint test
	@echo ""
	@echo "All checks passed!"

# ============================================
# Information & Diagnostics
# ============================================
info:
	@echo "Project Information:"
	@echo ""
	@echo "  Project: SciTeX Template Research"
	@echo "  Python: $$($(PYTHON) --version 2>&1)"
	@echo "  Scripts: $$(find $(SCRIPTS_DIR) -name "*.py" | wc -l) Python files"
	@echo "  Config: $$(ls -1 $(CONFIG_DIR)/*.yaml 2>/dev/null | wc -l) YAML files"
	@echo ""
	@echo "  MNIST Scripts:"
	@echo "    - $$(ls -1 $(MNIST_DIR)/*.py 2>/dev/null | wc -l) scripts"
	@echo "    - $$(ls -1d $(MNIST_DIR)/*_out 2>/dev/null | wc -l) output directories"
	@echo ""
	@if [ -d $(DATA_DIR)/mnist/figures ]; then \
		echo "  Generated Figures: $$(ls -1 $(DATA_DIR)/mnist/figures/*.jpg 2>/dev/null | wc -l)"; \
	fi
	@if [ -d $(DATA_DIR)/mnist/models ]; then \
		echo "  Saved Models: $$(ls -1 $(DATA_DIR)/mnist/models/*.pkl 2>/dev/null | wc -l)"; \
	fi

tree:
	@echo "Project Structure:"
	@if command -v tree >/dev/null 2>&1; then \
		tree -L 3 -I '__pycache__|*.pyc|.git|.venv|*.egg-info|.pytest_cache|.ruff_cache|.mypy_cache' -C; \
	else \
		echo "tree command not found. Install with: sudo apt-get install tree"; \
		ls -R; \
	fi

show-config:
	@echo "Configuration Files:"
	@echo ""
	@if command -v yq >/dev/null 2>&1; then \
		for cfg in $(CONFIG_DIR)/*.yaml; do \
			if [ -f "$$cfg" ]; then \
				echo "$$cfg:"; \
				yq -C '.' "$$cfg" 2>/dev/null || cat "$$cfg"; \
				echo ""; \
			fi; \
		done; \
	else \
		echo "yq not installed. Showing raw YAML files:"; \
		echo "(Install yq for colored output: sudo apt-get install yq or brew install yq)"; \
		echo ""; \
		for cfg in $(CONFIG_DIR)/*.yaml; do \
			if [ -f "$$cfg" ]; then \
				echo "$$cfg:"; \
				cat "$$cfg"; \
				echo ""; \
			fi; \
		done; \
	fi

# ============================================
# Utility Targets
# ============================================
.SILENT: help

# EOF
