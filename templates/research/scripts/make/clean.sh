#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/clean.sh
#
# Umbrella clean: wipes per-script `*_out/` directories produced by scripts/.
# Heavier sweeps live in clean_all.sh / clean_data.sh / clean_logs.sh.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/clean_outputs.sh
