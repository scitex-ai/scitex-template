#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/run_mnist_plot_digits.sh
#
# Step 02: Plot a grid of MNIST digit thumbnails.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 ./scripts/mnist/02_plot_digits.py
