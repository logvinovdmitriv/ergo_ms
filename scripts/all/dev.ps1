# PowerShell: локальный запуск API и клиента одновременно (без Docker)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot

Write-Host '[dev_all] Starting API in background...'
$shell = if (Get-Command pwsh -ErrorAction SilentlyContinue) { 'pwsh' } else { 'powershell' }
$api = Start-Process $shell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',"$scriptDir/../api/dev.ps1") -PassThru -WindowStyle Hidden

try {
  Start-Sleep -Seconds 2
  Write-Host '[dev_all] Starting Client in foreground...'
  & "$scriptDir/../client/dev.ps1"
}
finally {
  if ($api -and -not $api.HasExited) {
    Write-Host "[dev_all] Stopping background API (pid=$($api.Id))"
    try { $api.Kill() } catch {}
  }
}


