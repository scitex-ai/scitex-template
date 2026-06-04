#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/run_mnist_register_claims.sh
#
# Step 06: Register validity claims (data/results/claims.json) and call
# scitex_clew.add_claim so the Clew DAG terminus is recorded.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

python3 ./scripts/mnist/06_register_claims.py
