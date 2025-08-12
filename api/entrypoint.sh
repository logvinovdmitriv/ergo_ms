#!/usr/bin/env sh
set -e

cd /app

export PYTHONPATH="/app:${PYTHONPATH:-}"

# Safe defaults for local/dev
export API_SECRET_KEY=${API_SECRET_KEY:-dev}
export API_DEPLOY_TYPE=${API_DEPLOY_TYPE:-development}

if [ "${AUTO_MIGRATE:-0}" = "1" ]; then
  echo "[api] Checking unapplied migrations..."
  # Optionally generate migrations (use ONLY in dev/staging)
  if [ "${AUTO_MAKEMIGRATIONS:-0}" = "1" ]; then
    echo "[api] AUTO_MAKEMIGRATIONS=1: generating migrations"
    python src/manage.py makemigrations --noinput || true
  else
    echo "[api] AUTO_MAKEMIGRATIONS=0: skipping makemigrations"
  fi
  # Apply migrations
  python src/manage.py migrate --noinput || true
else
  echo "[api] AUTO_MIGRATE disabled (set AUTO_MIGRATE=1 to enable)."
fi

exec "$@"


