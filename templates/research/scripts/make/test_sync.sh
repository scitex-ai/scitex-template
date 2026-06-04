#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/test_sync.sh
#
# Mirror the structure of scripts/ into tests/ so every script has a matching
# (possibly stub) test file. Delegates to tests/sync_tests_with_scripts.sh.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Synchronizing test structure with scripts..."
./tests/sync_tests_with_scripts.sh
echo "Test synchronization complete"
