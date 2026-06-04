#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/install_dev.sh
#
# Install development tooling (pytest, ruff, etc.) on top of the runtime deps.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Installing development dependencies..."
pip3 install pytest pytest-cov ruff black isort mypy
echo "Development dependencies installed"
