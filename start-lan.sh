#!/usr/bin/env bash
# Pixel Works: opt-in home-LAN mode (local subnet, no internet router changes).
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export PIXEL_WORKS_LAN_IP="${PIXEL_WORKS_LAN_IP:-192.168.0.8}"
printf 'Pixel Works på hemnätet: http://%s:8765\n' "$PIXEL_WORKS_LAN_IP"
printf 'Spelpreview: http://%s:8766\n' "$PIXEL_WORKS_LAN_IP"
if [[ "${1:-}" == '--protected' ]]; then
    read -r -s -p 'Välj LAN-lösenord (minst 12 tecken): ' PIXEL_WORKS_LAN_PASSWORD
    printf '\n'
    if (( ${#PIXEL_WORKS_LAN_PASSWORD} < 12 )); then
        echo 'Avbrutet: lösenordet måste innehålla minst 12 tecken.' >&2
        exit 1
    fi
    export PIXEL_WORKS_LAN_PASSWORD
    unset PIXEL_WORKS_LAN_TRUSTED
elif [[ $# -eq 0 ]]; then
    # An explicit, opt-in trusted-subnet setting; no credentials on home LAN.
    unset PIXEL_WORKS_LAN_PASSWORD
    export PIXEL_WORKS_LAN_TRUSTED=1
    printf 'Hemma-LAN utan inloggning: alla enheter på ditt betrodda LAN får åtkomst.\n'
else
    echo 'Använd: bash start-lan.sh [--protected]' >&2
    exit 2
fi
exec python3 backend/server.py start
