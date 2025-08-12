#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../client"

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

echo "[dev_client] Starting client dev server..."
if [ "$PKG" = "pnpm" ]; then
  exec pnpm run dev
elif [ "$PKG" = "yarn" ]; then
  exec yarn dev
else
  exec npm run dev
fi


