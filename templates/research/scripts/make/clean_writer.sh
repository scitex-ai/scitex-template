#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/clean_writer.sh
#
# Remove cloned writer projects (LaTeX manuscript scaffolds under
# scitex/writer/). Use with caution — this destroys local manuscript work that
# hasn't been pushed.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ -d scitex/writer ]; then
    echo "Removing scitex/writer/ ..."
    rm -rf scitex/writer
    echo "Writer projects removed."
else
    echo "No scitex/writer/ directory present; nothing to clean."
fi
