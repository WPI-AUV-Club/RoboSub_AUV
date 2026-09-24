#!/usr/bin/env bash
set -euo pipefail

JETSON_IP="192.168.1.50"
JETSON_USER="jetson"

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

CONFIG_FILE="$HOME/.ssh/config"
if ! grep -q "Host jetson" "$CONFIG_FILE" 2>/dev/null; then
    cat <<EOF >> "$CONFIG_FILE"

Host jetson
    HostName $JETSON_IP
    User $JETSON_USER
    StrictHostKeyChecking accept-new
    ServerAliveInterval 30
    ServerAliveCountMax 3
EOF
    chmod 600 "$CONFIG_FILE"
fi

if ! ssh -o BatchMode=yes jetson "true" >/dev/null 2>&1; then
    echo "Error: SSH connection to Jetson failed" >&2
    exit 1
fi

if command -v docker >/dev/null 2>&1; then
    if ! docker context ls -q | grep -q "^jetson$"; then
        docker context create jetson --docker "host=ssh://jetson" >/dev/null
    fi
    docker context use jetson >/dev/null
fi
