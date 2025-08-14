Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Можно использовать один из файлов compose:
# - scripts/all/docker-compose.yml (полный стек)
# - scripts/api/docker-compose.yml (только API + БД + Redis + migrator)
# - scripts/client/docker-compose.yml (API + Client + БД + Redis + migrator)

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

param(
  [ValidateSet('all','api','client')]
  [string]$Stack = 'all'
)

$composePath = switch ($Stack) {
  'all'    { 'scripts/all/docker-compose.yml' }
  'api'    { 'scripts/api/docker-compose.yml' }
  'client' { 'scripts/client/docker-compose.yml' }
}

docker compose -f $composePath down -v


