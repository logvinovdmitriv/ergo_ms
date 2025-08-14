#!/usr/bin/env bash
set -euo pipefail

# Запуск полного стека (API + Client + DB + Redis + Celery) через Docker Compose

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

echo "[all/up] Using compose file: $COMPOSE_FILE"
docker compose -f "$COMPOSE_FILE" up -d

echo "[all/up] Stack is starting in detached mode. Для логов: scripts/ops/compose_logs.sh all api"


