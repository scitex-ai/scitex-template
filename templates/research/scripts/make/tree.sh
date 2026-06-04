#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/tree.sh
#
# Render the project tree (depth 3) excluding caches and venv dirs.
# Falls back to `ls -R` if the `tree` binary is missing.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Project Structure:"
if command -v tree >/dev/null 2>&1; then
    tree -L 3 -I '__pycache__|*.pyc|.git|.venv|*.egg-info|.pytest_cache|.ruff_cache|.mypy_cache' -C
else
    echo "tree command not found. Install with: sudo apt-get install tree"
    ls -R
fi
