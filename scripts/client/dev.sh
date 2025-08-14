#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../client"

# Ensure API endpoint env vars for local dev (match docker-compose defaults)
export VITE_API_HOST=${VITE_API_HOST:-localhost}
export VITE_API_PORT=${VITE_API_PORT:-8000}

if command -v pnpm >/dev/null 2>&1; then
  PKG=pnpm
elif command -v yarn >/dev/null 2>&1; then
  PKG=yarn
else
  PKG=npm
fi

echo "[dev_client] Installing dependencies using $PKG"
if [ "$PKG" = "pnpm" ]; then
  pnpm install
elif [ "$PKG" = "yarn" ]; then
  yarn install
else
  npm install
fi

echo "[dev_client] Starting client dev server on :8001 (API: ${VITE_API_HOST}:${VITE_API_PORT})..."
if [ "$PKG" = "pnpm" ]; then
  exec pnpm run dev -- --port 8001
elif [ "$PKG" = "yarn" ]; then
  exec yarn dev --port 8001
else
  exec npm run dev -- --port 8001
fi


