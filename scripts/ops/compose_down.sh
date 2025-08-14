#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")"/../.. && pwd)"
cd "$ROOT_DIR"

STACK=${1:-all}

case "$STACK" in
  all)    COMPOSE_FILE="scripts/all/docker-compose.yml" ;;
  api)    COMPOSE_FILE="scripts/api/docker-compose.yml" ;;
  client) COMPOSE_FILE="scripts/client/docker-compose.yml" ;;
  *) echo "Usage: $0 [all|api|client]"; exit 1 ;;
esac

docker compose -f "$COMPOSE_FILE" down -v


