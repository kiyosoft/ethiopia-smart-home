#!/usr/bin/env bash
# Install one or more Ethiopian Smart Home integrations onto Home Assistant.
#
# Usage:
#   # All integrations
#   HA_HOST=192.168.100.245 HA_USER=root ./scripts/install-to-ha.sh
#
#   # Single integration (independently installable)
#   INTEGRATIONS=ethiopia_power HA_HOST=192.168.100.245 HA_USER=root ./scripts/install-to-ha.sh
#
#   # Several
#   INTEGRATIONS="ethiopia_core ethiopia_religion" HA_CONFIG_DIR=$HOME/.homeassistant ./scripts/install-to-ha.sh
#
# Each folder under custom_components/ is self-contained — no other Ethiopia
# integration is required at install or runtime (optional entity linking only).

set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/custom_components"
ALL=(ethiopia_core ethiopia_religion ethiopia_power ethiopia_water ethiopia_voice)

if [[ -n "${INTEGRATIONS:-}" ]]; then
  # shellcheck disable=SC2206
  SELECTED=($INTEGRATIONS)
else
  SELECTED=("${ALL[@]}")
fi

for name in "${SELECTED[@]}"; do
  if [[ ! -d "$SRC/$name" ]]; then
    echo "Unknown integration: $name" >&2
    echo "Available: ${ALL[*]}" >&2
    exit 1
  fi
done

sync_one() {
  local name="$1"
  local dest_root="$2"
  mkdir -p "$dest_root"
  rsync -a --delete "$SRC/$name/" "$dest_root/$name/"
  echo "  synced $name → $dest_root/$name"
}

if [[ -n "${HA_CONFIG_DIR:-}" ]]; then
  DEST="$HA_CONFIG_DIR/custom_components"
  echo "Installing to local config: $DEST"
  echo "Integrations: ${SELECTED[*]}"
  for name in "${SELECTED[@]}"; do
    sync_one "$name" "$DEST"
  done
elif [[ -n "${HA_HOST:-}" ]]; then
  USER="${HA_USER:-root}"
  PORT="${HA_PORT:-22}"
  DEST="${HA_REMOTE_DIR:-/config/custom_components}"
  echo "Installing over SSH to ${USER}@${HA_HOST}:${DEST}"
  echo "Integrations: ${SELECTED[*]}"
  ssh -p "$PORT" "${USER}@${HA_HOST}" "mkdir -p '$DEST'"
  for name in "${SELECTED[@]}"; do
    rsync -a --delete -e "ssh -p $PORT" "$SRC/$name/" "${USER}@${HA_HOST}:${DEST}/${name}/"
    echo "  synced $name"
  done
  echo
  echo "Restart Home Assistant:"
  echo "  ssh -p $PORT ${USER}@${HA_HOST} 'ha core restart'"
else
  cat <<'EOF'
Set one of:

  HA_HOST=homeassistant.local HA_USER=root ./scripts/install-to-ha.sh
  HA_CONFIG_DIR=/path/to/config ./scripts/install-to-ha.sh

Optional:
  INTEGRATIONS=ethiopia_power          # install only one (or space-separated list)
  HA_PORT=22
  HA_REMOTE_DIR=/config/custom_components

Examples:
  INTEGRATIONS=ethiopia_core HA_HOST=192.168.100.245 HA_USER=root ./scripts/install-to-ha.sh
  INTEGRATIONS="ethiopia_power ethiopia_water" HA_CONFIG_DIR=$HOME/.homeassistant ./scripts/install-to-ha.sh
EOF
  exit 1
fi

echo
echo "Done. Add only the integration(s) you installed via Settings → Devices & services."
