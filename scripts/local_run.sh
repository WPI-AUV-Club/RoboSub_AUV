#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

docker context use default >/dev/null 2>&1 || true

if ! docker image inspect auv:latest >/dev/null 2>&1; then
    "$SCRIPT_DIR/scripts/local_build.sh"
fi

if [ $# -gt 0 ]; then
    docker run -it --rm \
        --net=host \
        -e ROS_DOMAIN_ID=0 \
        -v "$SCRIPT_DIR/ros2_ws:/workspaces/RoboSub_AUV/ros2_ws:Z" \
        auv:latest \
        "$@"
else
    docker run -it --rm \
        --net=host \
        -e ROS_DOMAIN_ID=0 \
        -v "$SCRIPT_DIR/ros2_ws:/workspaces/RoboSub_AUV/ros2_ws:Z" \
        auv:latest \
        /bin/bash
fi
