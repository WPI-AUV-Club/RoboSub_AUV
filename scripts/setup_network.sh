#!/usr/bin/env bash
set -euo pipefail

JETSON_IP="192.168.1.50"
HOST_IP="192.168.1.1/24"

IFACE="${1:-}"
if [ -z "$IFACE" ]; then
    for cand in $(ip -o link show | awk -F': ' '{print $2}' | grep -E '^(enu|enx|eth[1-9])'); do
        if [ "$cand" != "lo" ] && [ "$cand" != "eth0" ]; then
            IFACE="$cand"
            break
        fi
    done
fi

if [ -z "$IFACE" ]; then
    echo "Error: USB-to-Ethernet interface not found" >&2
    exit 1
fi

sudo ip link set "$IFACE" up
if ! ip addr show "$IFACE" | grep -q "192.168.1.1"; then
    sudo ip addr add "$HOST_IP" dev "$IFACE"
fi

sudo sysctl -w net.ipv4.ip_forward=1 >/dev/null
OUT_IFACE=$(ip route | grep '^default' | awk '{print $5}' | head -n1 || echo "eth0")
if [ -n "$OUT_IFACE" ]; then
    sudo iptables -t nat -C POSTROUTING -s 192.168.1.0/24 -o "$OUT_IFACE" -j MASQUERADE 2>/dev/null || \
    sudo iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o "$OUT_IFACE" -j MASQUERADE
fi

if ! ping -c 2 -W 2 "$JETSON_IP" >/dev/null 2>&1; then
    echo "Error: Jetson at $JETSON_IP unreachable" >&2
    exit 1
fi

ssh -o BatchMode=yes -o ConnectTimeout=2 "jetson@$JETSON_IP" \
    "sudo ip route replace default via 192.168.1.1 dev enP8p1s0 metric 100 2>/dev/null || true" 2>/dev/null || true
