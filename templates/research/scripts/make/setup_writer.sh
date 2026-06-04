#!/usr/bin/env bash
# Timestamp: "2026-06-04 (proj-scitex-dev)"
# File: ./scripts/make/setup_writer.sh
#
# Clone the writer (LaTeX manuscript) template project. Defers to the
# canonical management script when present; otherwise prints guidance so the
# user knows how to bootstrap a writer project manually.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [ -x ./management/scripts/setup-writer.sh ]; then
    ./management/scripts/setup-writer.sh --git-strategy child "$@"
else
    cat <<'EOF'
setup-writer: no management script installed.

To create a writer (manuscript) project, either:

  1. Provide a management script at ./management/scripts/setup-writer.sh, OR
  2. Use the scitex CLI directly:
       scitex writer clone scitex/writer/my_paper

See README.md ("Writer Shared Resources") for the full procedure.
EOF
fi
