#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/run_mnist.sh
#
# Run the complete MNIST example pipeline end-to-end (01 through 06):
#   01_download.py          -> raw MNIST data + flattened npy
#   02_plot_digits.py       -> digit thumbnails
#   03_plot_umap_space.py   -> UMAP visualization
#   04_clf_svm.py           -> SVM training + classification report
#   05_plot_conf_mat.py     -> confusion matrix figure
#   06_register_claims.py   -> claims.json + scitex_clew.add_claim

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/run_mnist_download.sh
./scripts/make/run_mnist_plot_digits.sh
./scripts/make/run_mnist_plot_umap.sh
./scripts/make/run_mnist_clf_svm.sh
./scripts/make/run_mnist_conf_mat.sh
./scripts/make/run_mnist_register_claims.sh

echo "MNIST pipeline complete."
