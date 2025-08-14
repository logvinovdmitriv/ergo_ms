#!/usr/bin/env bash
set -euo pipefail

STACK="${1:-all}"

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

case "$STACK" in
  all)    COMPOSE_FILE="scripts/all/docker-compose.yml" ;;
  api)    COMPOSE_FILE="scripts/api/docker-compose.yml" ;;
  client) COMPOSE_FILE="scripts/client/docker-compose.yml" ;;
  *) echo "Usage: $0 [all|api|client]"; exit 1 ;;
esac

echo "[compose_up] Using: $COMPOSE_FILE"
docker compose -f "$COMPOSE_FILE" up -d

echo "[compose_up] Started. For logs: scripts/ops/compose_logs.sh $STACK api"


