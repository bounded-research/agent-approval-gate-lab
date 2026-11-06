#!/usr/bin/env bash
# Creates the unprivileged agent user for enforced mode (Linux). Run once, as root.
# What it does: adds system user 'labagent' with no login shell and no home. Nothing else.
# Undo: sudo userdel labagent
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "run as root: sudo bash scripts/setup_enforced.sh" >&2; exit 1; }
command -v runuser >/dev/null || [[ -x /usr/sbin/runuser ]] || { echo "runuser not found (util-linux)" >&2; exit 1; }
if id labagent >/dev/null 2>&1; then echo "labagent exists: $(id labagent)"; else
  useradd --system --no-create-home --shell /usr/sbin/nologin labagent
  echo "created: $(id labagent)"
fi
echo "Note: macOS has no runuser; use a Linux VM or container mode."
