#!/usr/bin/env bash
set -euo pipefail

docker context use jetson >/dev/null 2>&1 || true

if [ $# -gt 0 ]; then
    docker run -it --rm \
        --privileged \
        --device=/dev/ttyTHS1:/dev/ttyTHS1 \
        --device=/dev/gpiochip0:/dev/gpiochip0 \
        --device=/dev/gpiochip1:/dev/gpiochip1 \
        --net=host \
        -e ROS_DOMAIN_ID=0 \
        auv:latest \
        "$@"
else
    docker run -it --rm \
        --privileged \
        --device=/dev/ttyTHS1:/dev/ttyTHS1 \
        --device=/dev/gpiochip0:/dev/gpiochip0 \
        --device=/dev/gpiochip1:/dev/gpiochip1 \
        --net=host \
        -e ROS_DOMAIN_ID=0 \
        auv:latest \
        /bin/bash
fi
