#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/format_shell.sh
#
# Format + lint every *.sh under scripts/ using shfmt and shellcheck.
# Both tools are optional — missing binaries are reported, not fatal.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Formatting and linting shell scripts..."
if command -v shfmt >/dev/null 2>&1; then
    find scripts -name "*.sh" \
        ! -path "*/node_modules/*" \
        ! -path "*/.venv/*" \
        -exec shfmt -w -i 4 -bn -ci -sr {} + \
        2>&1 || echo "shfmt formatting completed with warnings"
    echo "Shell formatting complete!"
else
    echo "shfmt not found. Install with: go install mvdan.cc/sh/v3/cmd/shfmt@latest"
    echo "Skipping shell formatting..."
fi

if command -v shellcheck >/dev/null 2>&1; then
    find scripts -name "*.sh" \
        ! -path "*/node_modules/*" \
        ! -path "*/.venv/*" \
        -exec shellcheck --severity=error {} + \
        2>&1 || echo "ShellCheck found errors"
    echo "Shell linting complete!"
else
    echo "shellcheck not found. Install with: sudo apt-get install shellcheck"
    echo "Skipping shell linting..."
fi
