#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/lint_python.sh
#
# Lint Python code under scripts/ and tests/ with ruff.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Linting Python code with ruff..."
if command -v ruff >/dev/null 2>&1; then
    ruff check scripts tests --quiet || echo "Ruff found issues"
    echo "Linting complete"
else
    echo "Ruff not found. Install with: pip install ruff"
    exit 1
fi
