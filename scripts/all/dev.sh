#!/usr/bin/env bash
set -euo pipefail

# Запуск API и клиента локально (без Docker) одновременно

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[dev_all] Starting API in background..."
"$SCRIPT_DIR/../api/dev.sh" &
API_PID=$!

cleanup() {
  echo "[dev_all] Stopping background API (pid=$API_PID)"
  kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Небольшая задержка, чтобы API успел подняться
sleep 2 || true

echo "[dev_all] Starting Client in foreground..."
exec "$SCRIPT_DIR/../client/dev.sh"


