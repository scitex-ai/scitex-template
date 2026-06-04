#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/format.sh
#
# Umbrella formatter: Python (ruff) + shell (shfmt + shellcheck).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/format_python.sh
./scripts/make/format_shell.sh

echo ""
echo "All formatting and linting complete!"
