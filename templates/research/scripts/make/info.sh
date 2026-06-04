#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/info.sh
#
# Print a small summary of the project: Python version, script counts,
# config file counts, generated figure/model counts.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "Project Information:"
echo ""
echo "  Project: SciTeX Template Research"
echo "  Python: $(python3 --version 2>&1)"
echo "  Scripts: $(find scripts -name "*.py" | wc -l) Python files"
echo "  Config: $(ls -1 config/*.yaml 2>/dev/null | wc -l) YAML files"
echo ""
echo "  MNIST Scripts:"
echo "    - $(ls -1 scripts/mnist/*.py 2>/dev/null | wc -l) scripts"
echo "    - $(ls -1d scripts/mnist/*_out 2>/dev/null | wc -l) output directories"
echo ""
if [ -d data/mnist/figures ]; then
    echo "  Generated Figures: $(ls -1 data/mnist/figures/*.jpg 2>/dev/null | wc -l)"
fi
if [ -d data/mnist/models ]; then
    echo "  Saved Models: $(ls -1 data/mnist/models/*.pkl 2>/dev/null | wc -l)"
fi
