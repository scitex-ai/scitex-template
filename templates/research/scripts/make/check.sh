#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/check.sh
#
# Run the full quality gate: format -> lint -> test.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/format.sh
./scripts/make/lint.sh
./scripts/make/test.sh

echo ""
echo "All checks passed!"
