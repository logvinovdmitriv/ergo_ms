# Powershell dev launcher for Windows client
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$clientPath = Join-Path $root 'client'
Set-Location $clientPath

function Pick-PM {
  if (Get-Command pnpm -ErrorAction SilentlyContinue) { return 'pnpm' }
  elseif (Get-Command yarn -ErrorAction SilentlyContinue) { return 'yarn' }
  else { return 'npm' }
}
$pm = Pick-PM

Write-Host "[dev_client] Installing dependencies using $pm"
if ($pm -eq 'pnpm') { pnpm install }
elseif ($pm -eq 'yarn') { yarn install }
else { npm install }

Write-Host '[dev_client] Starting dev server'
if ($pm -eq 'pnpm') { pnpm run dev }
elseif ($pm -eq 'yarn') { yarn dev }
else { npm run dev }


