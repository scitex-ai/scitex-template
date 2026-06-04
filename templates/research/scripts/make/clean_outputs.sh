#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/clean_outputs.sh
#
# Remove every `*_out/` directory under scripts/ (per-script outputs).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

find scripts -type d -name '*_out' -prune -exec rm -rf {} + 2>/dev/null || true
