#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! ping -c 1 -W 2 192.168.1.50 >/dev/null 2>&1; then
    "$SCRIPT_DIR/scripts/setup_network.sh"
fi

if ! docker context ls -q | grep -q "^jetson$"; then
    "$SCRIPT_DIR/scripts/setup_ssh.sh"
fi
docker context use jetson >/dev/null

cd "$SCRIPT_DIR"
docker build -t auv:latest .
