#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/run_all.sh
#
# Run the full pipeline across all example workflows in this research project.
# Today the only example is MNIST; when future examples land, chain them here.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/run_mnist.sh

echo "Full pipeline (run-all) complete."
