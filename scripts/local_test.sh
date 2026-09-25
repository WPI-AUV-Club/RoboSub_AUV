#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker context use default >/dev/null 2>&1 || true

if ! docker image inspect auv:latest >/dev/null 2>&1; then
    "$SCRIPT_DIR/scripts/local_build.sh"
fi

docker run --rm \
    -v "$SCRIPT_DIR/ros2_ws:/workspaces/RoboSub_AUV/ros2_ws:Z" \
    auv:latest bash -c '
    set -e
    ros2 pkg list | grep auv_
    ros2 interface list | grep auv_motors
    python3 -c "import serial, simple_pid"
'
