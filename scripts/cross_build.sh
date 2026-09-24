#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! docker buildx inspect default 2>/dev/null | grep -q "linux/arm64"; then
    docker run --privileged --rm tonistiigi/binfmt --install arm64 >/dev/null
fi

cd "$SCRIPT_DIR"
docker context use default >/dev/null 2>&1 || true
docker buildx build --platform linux/arm64 -t auv:latest --load .
