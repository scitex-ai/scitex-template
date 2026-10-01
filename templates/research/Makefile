# Run inside the project's virtual environment; override PYTHON if needed.
PYTHON ?= python3
MNIST_DIR := scripts/mnist
.DEFAULT_GOAL := help
.PHONY: help install install-develop install-dev setup setup-writer verify run-mnist run-mnist-download run-mnist-plot-digits run-mnist-plot-umap run-mnist-clf-svm run-mnist-conf-mat solve verify-claims test format lint check clean clean-outputs clean-python clean-clew

help:
	@echo "install / install-develop: install releases / upstream develop packages"
	@echo "setup / setup-writer: initialize environment / manuscript"
	@echo "verify: check package imports"
	@echo "run-mnist / solve: full example / measured claims pipeline"
	@echo "verify-claims: check claims JSON schema (not provenance)"
	@echo "install-dev / check: install development tools / run checks"
	@echo "clean: remove regenerable script outputs and Python caches"

install:
	$(PYTHON) -m pip install -r requirements.txt
install-develop:
	$(PYTHON) -m pip install -r requirements-develop.txt
install-dev:
	$(PYTHON) -m pip install pytest ruff
setup: install verify
setup-writer:
	$(PYTHON) -m scitex_writer create-project . --git-strategy parent --yes
verify:
	$(PYTHON) -c "import scitex_session, scitex_io, scitex_clew, scitex_dev, scitex_writer, figrecipe"

# Explicit sequential calls also work when make is invoked with -j.
run-mnist:
	$(PYTHON) $(MNIST_DIR)/01_download.py
	$(PYTHON) $(MNIST_DIR)/02_plot_digits.py
	$(PYTHON) $(MNIST_DIR)/03_plot_umap_space.py
	$(PYTHON) $(MNIST_DIR)/04_clf_svm.py
	$(PYTHON) $(MNIST_DIR)/05_plot_conf_mat.py
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
solve:
	$(PYTHON) $(MNIST_DIR)/01_download.py
	$(PYTHON) $(MNIST_DIR)/04_clf_svm.py
	$(PYTHON) $(MNIST_DIR)/06_register_claims.py
verify-claims:
	$(PYTHON) scripts/verify/check_schema.py

test:
	$(PYTHON) -m pytest tests -q
format:
	$(PYTHON) -m ruff format scripts tests
lint:
	$(PYTHON) -m ruff check scripts tests
check:
	$(PYTHON) -m ruff format --check scripts tests
	$(PYTHON) -m ruff check scripts tests
	$(PYTHON) -m pytest tests -q

clean: clean-outputs clean-python clean-clew
clean-outputs:
	find scripts -type d -name '*_out' -prune -exec rm -rf {} +
clean-python:
	find scripts tests -type d -name '__pycache__' -prune -exec rm -rf {} +
clean-clew:
	rm -f data/results/clew_dag.html
