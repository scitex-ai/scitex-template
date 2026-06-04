#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/format_python.sh
#
# Format every Python file under scripts/ and tests/ with ruff.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Formatting Python code with ruff..."
if command -v ruff >/dev/null 2>&1; then
    ruff format scripts tests --quiet || echo "Ruff formatting completed with warnings"
    echo "Python formatting complete"
else
    echo "Ruff not found. Install with: pip install ruff"
    exit 1
fi
