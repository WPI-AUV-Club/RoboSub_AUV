#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$SCRIPT_DIR/scripts/build.sh"

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
