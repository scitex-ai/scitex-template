#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/clean_all.sh
#
# Clean everything: outputs + data + logs + Python caches + Clew runtime.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

./scripts/make/clean_outputs.sh
./scripts/make/clean_data.sh
./scripts/make/clean_logs.sh
./scripts/make/clean_python.sh
./scripts/make/clean_clew.sh
