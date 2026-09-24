#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker context use default >/dev/null 2>&1 || true

cd "$SCRIPT_DIR"
docker build -t auv:latest .
