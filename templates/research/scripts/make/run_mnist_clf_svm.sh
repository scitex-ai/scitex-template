#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/run_mnist_clf_svm.sh
#
# Step 04: Train the SVM classifier on subsampled MNIST and dump the
# classification report CSV. Subsample size is controlled by
# CONFIG.MNIST.SVM_TRAIN_SUBSET.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 ./scripts/mnist/04_clf_svm.py
