param(
  [ValidateSet('all','api','client')]
  [string]$Stack = 'all'
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

Write-Host "[compose_up] Using: $composePath"
docker compose -f $composePath up -d

Write-Host "[compose_up] Started. For logs: scripts/ops/compose_logs.ps1 -Stack $Stack -Service api"


