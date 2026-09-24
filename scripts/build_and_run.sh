#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$SCRIPT_DIR/scripts/build.sh"
exec "$SCRIPT_DIR/scripts/run.sh" "$@"
