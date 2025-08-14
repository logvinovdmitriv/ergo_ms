param(
  [ValidateSet('all','api','client')]
  [string]$Stack = 'all',
  [string]$Service = 'api'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

$composePath = switch ($Stack) {
  'all'    { 'scripts/all/docker-compose.yml' }
  'api'    { 'scripts/api/docker-compose.yml' }
  'client' { 'scripts/client/docker-compose.yml' }
}

docker compose -f $composePath logs -f $Service


