#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/clean_clew.sh
#
# Reset the Clew runtime sqlite database. Removes both the legacy location
# (.scitex/clew/db.sqlite) and the current location
# (.scitex/clew/runtime/db.sqlite) so subsequent `make solve`-class flows
# (now run-mnist with 06_register_claims) start from a clean ledger.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

rm -f .scitex/clew/db.sqlite .scitex/clew/runtime/db.sqlite 2>/dev/null || true
