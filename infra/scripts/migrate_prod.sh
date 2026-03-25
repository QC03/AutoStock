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

echo "[INFO] Running alembic migrations on production backend container..."
docker compose -f docker-compose.prod.yml --env-file "$ENV_FILE" exec -T backend alembic upgrade head

echo "[OK] Migration completed."
