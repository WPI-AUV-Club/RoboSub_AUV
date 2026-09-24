#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$SCRIPT_DIR/scripts/cross_deploy.sh"
exec "$SCRIPT_DIR/scripts/shell.sh" "$@"
