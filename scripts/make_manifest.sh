#!/usr/bin/env bash
# Writes MANIFEST.sha256 for every tracked-type file except run outputs and caches.
set -euo pipefail
cd "$(dirname "$0")/.."
find . -type f \
  ! -path './.git/*' ! -path './runs/*' ! -path '*/__pycache__/*' ! -path './.pytest_cache/*' \
  ! -name 'MANIFEST.sha256' ! -name '*.zip' ! -name '*.pyc' \
  | LC_ALL=C sort | xargs sha256sum > MANIFEST.sha256
echo "MANIFEST.sha256: $(wc -l < MANIFEST.sha256) files"
