#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_FILE="${ENV_FILE:-$INFRA_DIR/.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] env file not found: $ENV_FILE"
  exit 1
fi

cd "$INFRA_DIR"

echo "[INFO] Starting/Updating production stack..."
docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" up -d --build

"$SCRIPT_DIR/migrate_prod.sh"

echo "[INFO] Current service status:"
docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" ps

echo "[OK] Stage8 deploy finished."
