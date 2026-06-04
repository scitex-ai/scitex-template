#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/install.sh
#
# Install runtime Python dependencies from requirements.txt via pip3.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Installing Python dependencies..."
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
    echo "Dependencies installed"
else
    echo "requirements.txt not found"
    exit 1
fi
