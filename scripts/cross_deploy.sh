#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! ping -c 1 -W 2 192.168.1.50 >/dev/null 2>&1; then
    "$SCRIPT_DIR/scripts/setup_network.sh"
fi

"$SCRIPT_DIR/scripts/cross_build.sh"

ZIP_CMD="gzip -1"
UNZIP_CMD="gzip -d"
if command -v pigz >/dev/null 2>&1 && ssh jetson "command -v pigz" >/dev/null 2>&1; then
    ZIP_CMD="pigz -1"
    UNZIP_CMD="pigz -d"
fi

docker context use default >/dev/null 2>&1 || true
docker save auv:latest | $ZIP_CMD | ssh jetson "$UNZIP_CMD | docker load"

ssh jetson "
    docker rm -f auv_core 2>/dev/null || true
    docker run -d \
        --name auv_core \
        --restart unless-stopped \
        --privileged \
        --device=/dev/ttyTHS1:/dev/ttyTHS1 \
        --device=/dev/gpiochip0:/dev/gpiochip0 \
        --device=/dev/gpiochip1:/dev/gpiochip1 \
        --net=host \
        -e ROS_DOMAIN_ID=0 \
        auv:latest \
        tail -f /dev/null
"
