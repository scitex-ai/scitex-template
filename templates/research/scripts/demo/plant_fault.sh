#!/bin/bash
# File: scripts/demo/plant_fault.sh
#
# Planted-fault demo (`make demo-fault`): show the live paper flagging a
# changed source, then put everything back exactly as it was.
#
#   1. back up the REAL file behind data/results/metrics.json
#   2. edit the SVM accuracy in it by hand (what a careless edit would do)
#   3. `clew verify --strict` must now FAIL; render the live paper of the
#      faulty state into data/live_paper/site-fault/
#   4. restore the file and ASSERT its SHA-256 equals the original
#   5. `clew verify --strict` must PASS again
#
# The restore runs from an EXIT trap, so it also happens when a step fails.
# This is a demo tool, not an analysis step: it must not record itself as a
# run, so it is a shell script outside @scitex_session.session.

set -euo pipefail

PYTHON="${PYTHON:-python3}"
CLEW="${CLEW:-clew}"
LIVE_PAPER="${LIVE_PAPER:-scitex-live-paper}"
TARGET="data/results/metrics.json"
POINTER_KEY="SVC"
BUNDLE="data/live_paper/bundle"
SITE_FAULT="data/live_paper/site-fault"
BACKUP_DIR="data/live_paper/fault-backup"

real="$(realpath "$TARGET")"
mkdir -p "$BACKUP_DIR"
backup="$BACKUP_DIR/$(basename "$real")"
sha_before="$(sha256sum "$real" | cut -d' ' -f1)"
cp -f "$real" "$backup"

restore() {
    cp -f "$backup" "$real"
    sha_after="$(sha256sum "$real" | cut -d' ' -f1)"
    if [ "$sha_after" != "$sha_before" ]; then
        echo "RESTORE FAILED: $real sha256 $sha_after != original $sha_before" >&2
        exit 1
    fi
    echo "restored $TARGET (sha256 $sha_before, verified)"
}
trap restore EXIT

echo "== planting a fault: hand-editing $POINTER_KEY accuracy in $TARGET"
"$PYTHON" - "$real" "$POINTER_KEY" <<'PY'
import json, sys
path, key = sys.argv[1], sys.argv[2]
with open(path) as f:
    metrics = json.load(f)
before = metrics[key]["accuracy"]
metrics[key]["accuracy"] = round(before - 0.05, 4)
with open(path, "w") as f:
    json.dump(metrics, f, indent=4)
print(f"   {key}.accuracy {before} -> {metrics[key]['accuracy']}")
PY

echo "== clew verify --strict (expected to FAIL)"
if "$CLEW" verify --strict; then
    echo "ERROR: clew verify passed on a planted fault" >&2
    exit 1
fi

echo "== rendering the faulty state -> $SITE_FAULT"
rm -rf "$SITE_FAULT"
"$CLEW" export-evidence --out "$BUNDLE/evidence-report.json"
"$LIVE_PAPER" render "$BUNDLE" --out "$SITE_FAULT" \
    --evidence-report "$BUNDLE/evidence-report.json" \
    --title "MNIST showcase (planted fault)"
echo "   open $SITE_FAULT/index.html: the needs-inspection list names the"
echo "   claims whose source changed; each graph marks the CHANGED node."

trap - EXIT
restore

echo "== clew verify --strict (expected to PASS after restore)"
"$CLEW" verify --strict
echo "== re-exporting the evidence of the restored state"
"$CLEW" export-evidence --out "$BUNDLE/evidence-report.json"

# EOF
