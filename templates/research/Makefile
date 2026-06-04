# ============================================
# SciTeX Template Research - Makefile
# ============================================
# Scientific research project workflow automation.
#
# Target bodies live in verb-form shell scripts under scripts/make/.
# Every target below is a thin wrapper around ./scripts/make/<verb>_<noun>.sh,
# so both `make <target>` and `./scripts/make/<verb>_<noun>.sh` produce the
# same behaviour. Edit the .sh files; do not bury logic in this Makefile.
#
# Usage:
#   make help                      # Show this help
#   make install                   # Install dependencies
#   make run-all                   # Run every example pipeline end-to-end
#   make run-mnist                 # Run the MNIST example pipeline (01-06)
#   make clean                     # Clean outputs
#   make format                    # Format code
#   make test                      # Run tests

.PHONY: \
	help \
	install \
	install-dev \
	setup \
	setup-writer \
	run-all \
	run-mnist \
	run-mnist-download \
	run-mnist-plot-digits \
	run-mnist-plot-umap \
	run-mnist-clf-svm \
	run-mnist-conf-mat \
	run-mnist-register-claims \
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
	@echo "  make run-all                       # Run every example pipeline end-to-end"
	@echo "  make run-mnist                     # Run complete MNIST pipeline (01-06, incl. claims)"
	@echo "  make run-mnist-download            # Download MNIST data"
	@echo "  make run-mnist-plot-digits         # Plot MNIST digits"
	@echo "  make run-mnist-plot-umap           # Create UMAP visualization"
	@echo "  make run-mnist-clf-svm             # Train SVM classifier"
	@echo "  make run-mnist-conf-mat            # Plot confusion matrix"
	@echo "  make run-mnist-register-claims     # Register validity claims (Clew DAG terminus)"
	@echo "  make verify-claims                 # Verify claims.json schema (out-of-band)"
	@echo ""
	@echo "Cleaning:"
	@echo "  make clean                         # Clean script outputs"
	@echo "  make clean-mnist                   # Clean MNIST outputs only"
	@echo "  make clean-outputs                 # Clean all *_out directories"
	@echo "  make clean-data                    # Clean generated data files"
	@echo "  make clean-logs                    # Clean log files"
	@echo "  make clean-writer                  # Remove writer projects (use with caution!)"
	@echo "  make clean-clew                    # Reset the Clew runtime sqlite ledger"
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
	@./scripts/make/install.sh

install-dev:
	@./scripts/make/install_dev.sh

setup:
	@./scripts/make/setup.sh

setup-writer:
	@./scripts/make/setup_writer.sh

verify:
	@./scripts/make/verify.sh

# ============================================
# Running MNIST Scripts
# ============================================
run-all:
	@./scripts/make/run_all.sh

run-mnist:
	@./scripts/make/run_mnist.sh

run-mnist-download:
	@./scripts/make/run_mnist_download.sh

run-mnist-plot-digits:
	@./scripts/make/run_mnist_plot_digits.sh

run-mnist-plot-umap:
	@./scripts/make/run_mnist_plot_umap.sh

run-mnist-clf-svm:
	@./scripts/make/run_mnist_clf_svm.sh

run-mnist-conf-mat:
	@./scripts/make/run_mnist_conf_mat.sh

run-mnist-register-claims:
	@./scripts/make/run_mnist_register_claims.sh

# `make verify-claims` is plain-Python (out-of-band; NOT in the agent's Clew
# DAG). It validates data/results/claims.json against the expected schema.
verify-claims:
	@./scripts/make/verify_claims.sh

clean-clew:
	@./scripts/make/clean_clew.sh

# ============================================
# Cleaning
# ============================================
clean:
	@./scripts/make/clean.sh

clean-mnist:
	@./scripts/make/clean_mnist.sh

clean-outputs:
	@./scripts/make/clean_outputs.sh

clean-data:
	@./scripts/make/clean_data.sh

clean-logs:
	@./scripts/make/clean_logs.sh

clean-all:
	@./scripts/make/clean_all.sh

clean-python:
	@./scripts/make/clean_python.sh

clean-writer:
	@./scripts/make/clean_writer.sh

# ============================================
# Testing
# ============================================
test:
	@./scripts/make/test.sh

test-verbose:
	@./scripts/make/test_verbose.sh

test-sync:
	@./scripts/make/test_sync.sh

# ============================================
# Code Quality
# ============================================
format:
	@./scripts/make/format.sh

format-python:
	@./scripts/make/format_python.sh

format-shell:
	@./scripts/make/format_shell.sh

lint:
	@./scripts/make/lint.sh

lint-python:
	@./scripts/make/lint_python.sh

check:
	@./scripts/make/check.sh

# ============================================
# Information & Diagnostics
# ============================================
info:
	@./scripts/make/info.sh

tree:
	@./scripts/make/tree.sh

show-config:
	@./scripts/make/show_config.sh

# ============================================
# Utility Targets
# ============================================
.SILENT: help

# EOF
