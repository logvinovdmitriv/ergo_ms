#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../api"

# Ensure env for local dev (non-docker)
export API_DEPLOY_TYPE=${API_DEPLOY_TYPE:-development}
export API_SECRET_KEY=${API_SECRET_KEY:-dev}

if [ ! -d .venv ]; then
  echo "[dev_api] Creating virtualenv .venv"
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip

if [ -f requirements-dev.txt ]; then
  echo "[dev_api] Installing requirements-dev.txt"
  pip install -r requirements-dev.txt
elif [ -f requirements.txt ]; then
  echo "[dev_api] Installing requirements.txt"
  pip install -r requirements.txt
elif [ -f pyproject.toml ]; then
  echo "[dev_api] Installing from pyproject (PEP 517)"
  pip install . || true
fi

echo "[dev_api] Starting Django server on :8000"
exec python src/manage.py runserver 0.0.0.0:8000


