#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/test.sh
#
# Run the pytest suite under tests/ (quiet output).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Running tests..."
if command -v pytest >/dev/null 2>&1; then
    pytest tests -q
else
    echo "pytest not installed. Run: make install-dev"
    exit 1
fi
