#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/show_config.sh
#
# Pretty-print every YAML file under config/. Uses `yq` for colour when
# available; falls back to `cat` otherwise.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Configuration Files:"
echo ""
if command -v yq >/dev/null 2>&1; then
    for cfg in config/*.yaml; do
        if [ -f "$cfg" ]; then
            echo "$cfg:"
            yq -C '.' "$cfg" 2>/dev/null || cat "$cfg"
            echo ""
        fi
    done
else
    echo "yq not installed. Showing raw YAML files:"
    echo "(Install yq for colored output: sudo apt-get install yq or brew install yq)"
    echo ""
    for cfg in config/*.yaml; do
        if [ -f "$cfg" ]; then
            echo "$cfg:"
            cat "$cfg"
            echo ""
        fi
    done
fi
