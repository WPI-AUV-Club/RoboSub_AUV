#!/usr/bin/env bash
set -euo pipefail

docker context use jetson >/dev/null 2>&1 || true

if docker ps --format '{{.Names}}' | grep -q "^auv_core$"; then
    exec docker exec -it auv_core /entrypoint.sh /bin/bash "$@"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    exec "$SCRIPT_DIR/scripts/run.sh" "$@"
fi
