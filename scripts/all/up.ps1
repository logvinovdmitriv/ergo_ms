Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Запуск полного стека (API + Client + DB + Redis + Celery) через Docker Compose

$composeFile = Join-Path $PSScriptRoot 'docker-compose.yml'

Write-Host "[all\up] Using compose file: $composeFile"
docker compose -f $composeFile up -d

Write-Host "[all\up] Stack is starting in detached mode. Use scripts/ops/compose_logs.ps1 -Stack all -Service api для логов."


