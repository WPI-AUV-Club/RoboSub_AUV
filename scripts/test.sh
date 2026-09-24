#!/usr/bin/env bash
set -euo pipefail

docker context use jetson >/dev/null 2>&1 || true

docker run --rm \
    --privileged \
    --device=/dev/gpiochip0:/dev/gpiochip0 \
    --device=/dev/gpiochip1:/dev/gpiochip1 \
    --device=/dev/ttyTHS1:/dev/ttyTHS1 \
    auv:latest bash -c '
    set -e
    ros2 pkg list | grep auv_
    ros2 interface list | grep auv_motors
    python3 -c "import serial, Jetson.GPIO, simple_pid"
'
