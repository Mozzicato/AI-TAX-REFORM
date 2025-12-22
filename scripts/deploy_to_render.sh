#!/usr/bin/env bash
# Trigger a manual deploy on Render using the RENDER API key
# Usage:
#   export RENDER_API_KEY="<your-key>"
#   export RENDER_SERVICE_ID="srv-xxxxx"
#   ./scripts/deploy_to_render.sh

set -euo pipefail

if [[ -z "${RENDER_API_KEY:-}" || -z "${RENDER_SERVICE_ID:-}" ]]; then
  echo "Missing RENDER_API_KEY or RENDER_SERVICE_ID. Set them as environment vars and try again."
  exit 1
fi

echo "Triggering manual deploy for service $RENDER_SERVICE_ID"

resp=$(curl -s -X POST "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{}')

echo "Response:" 
echo "$resp"

echo "If the response contains a deploy id, the deploy was scheduled. Check your Render dashboard for progress."