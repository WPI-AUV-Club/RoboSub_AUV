#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JETSON_IP="192.168.1.50"
IMAGE_NAME="auv:latest"
CONTAINER_NAME="auv_core"

usage() {
    cat <<EOF
Usage: $0 [command]

Commands:
  all           Build and deploy container in background (default)
  build         Build image natively on Jetson
  deploy        Build and deploy container in background
  run           Run container with hardware devices
  shell         Enter interactive container
  exec <cmd>    Execute command inside container
  test          Run ROS 2 tests
  stop          Stop container
  logs          Follow container logs
  cross-build   Cross-compile ARM64 image on laptop
  cross-deploy  Cross-compile on laptop, transfer, and deploy
  cross-run     Cross-compile on laptop, deploy, and enter container
  ssh           SSH into Jetson
  network       Configure host USB Ethernet interface
  ssh-setup     Configure passwordless SSH

Options:
  -h, --help    Show this help message
EOF
}

check_network() {
    if ! ping -c 1 -W 2 "$JETSON_IP" >/dev/null 2>&1; then
        "$SCRIPT_DIR/scripts/setup_network.sh"
    fi
}

ensure_context() {
    if ! ssh -o BatchMode=yes -o ConnectTimeout=2 jetson "true" >/dev/null 2>&1; then
        "$SCRIPT_DIR/scripts/setup_ssh.sh"
    fi
    if ! docker context ls -q | grep -q "^jetson$"; then
        docker context create jetson --docker "host=ssh://jetson" >/dev/null
    fi
    docker context use jetson >/dev/null
}

cmd_exec() {
    check_network
    ensure_context

    if [ $# -eq 0 ]; then
        echo "Error: exec requires a command to run" >&2
        exit 1
    fi

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker exec -it "$CONTAINER_NAME" /entrypoint.sh "$@"
    else
        docker run -it --rm \
            --privileged \
            --device=/dev/ttyTHS1:/dev/ttyTHS1 \
            --device=/dev/gpiochip0:/dev/gpiochip0 \
            --device=/dev/gpiochip1:/dev/gpiochip1 \
            --net=host \
            "$IMAGE_NAME" \
            "$@"
    fi
}

ACTION="${1:-all}"
shift || true

case "$ACTION" in
    all|deploy)
        "$SCRIPT_DIR/scripts/deploy.sh"
        ;;
    build)
        "$SCRIPT_DIR/scripts/build.sh"
        ;;
    run|start)
        "$SCRIPT_DIR/scripts/run.sh" "$@"
        ;;
    shell)
        "$SCRIPT_DIR/scripts/shell.sh" "$@"
        ;;
    cross-build)
        "$SCRIPT_DIR/scripts/cross_build.sh"
        ;;
    cross|cross-deploy)
        "$SCRIPT_DIR/scripts/cross_deploy.sh"
        ;;
    cross-run)
        "$SCRIPT_DIR/scripts/cross_build_and_run.sh" "$@"
        ;;
    ssh)
        "$SCRIPT_DIR/scripts/ssh.sh" "$@"
        ;;
    ssh-setup)
        "$SCRIPT_DIR/scripts/setup_ssh.sh"
        ;;
    exec)
        cmd_exec "$@"
        ;;
    test)
        "$SCRIPT_DIR/scripts/test.sh"
        ;;
    stop)
        check_network
        ensure_context
        docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
        ;;
    logs)
        check_network
        ensure_context
        docker logs -f "$CONTAINER_NAME"
        ;;
    network)
        "$SCRIPT_DIR/scripts/setup_network.sh"
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Unknown command: $ACTION" >&2
        usage
        exit 1
        ;;
esac
