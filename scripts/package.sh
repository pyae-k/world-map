#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT="${ROOT}/world-map-upload.zip"
STAGING="${ROOT}/.package-staging"

rm -rf "${STAGING}" "${OUTPUT}"
mkdir -p "${STAGING}/world-map"

rsync -a \
  --exclude '.venv' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude '.DS_Store' \
  --exclude '*.zip' \
  --exclude '.package-staging' \
  --exclude 'world-map.py' \
  "${ROOT}/" "${STAGING}/world-map/"

(
  cd "${STAGING}"
  zip -r "${OUTPUT}" world-map
)

rm -rf "${STAGING}"

echo "Created ${OUTPUT}"
du -h "${OUTPUT}"
