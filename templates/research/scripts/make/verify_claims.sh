#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/verify_claims.sh
#
# Out-of-band claim schema verification (plain Python; NOT part of the agent
# Clew DAG). Validates data/results/claims.json against the expected schema.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 ./scripts/verify/check_schema.py
