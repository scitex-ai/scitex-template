#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/setup.sh
#
# Full project bootstrap: install deps, scaffold the data tree, then verify.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/install.sh

echo "Setting up project..."
mkdir -p data
mkdir -p data/mnist/figures
mkdir -p data/mnist/models
mkdir -p data/mnist/raw
echo "Project setup complete"

./scripts/make/verify.sh

echo ""
echo "To create a writer project, run:"
echo "  make setup-writer"
echo ""
