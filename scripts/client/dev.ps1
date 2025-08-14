# Powershell dev launcher for Windows client
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$clientPath = Join-Path $root 'client'
Set-Location $clientPath

# Ensure API endpoint env vars for local dev (match docker-compose defaults)
$env:VITE_API_HOST = if ($env:VITE_API_HOST) { $env:VITE_API_HOST } else { 'localhost' }
$env:VITE_API_PORT = if ($env:VITE_API_PORT) { $env:VITE_API_PORT } else { '8000' }

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

Write-Host "[dev_client] Starting dev server on :8001 (API: $($env:VITE_API_HOST):$($env:VITE_API_PORT))"
if ($pm -eq 'pnpm') { pnpm run dev -- --port 8001 }
elseif ($pm -eq 'yarn') { yarn dev --port 8001 }
else { npm run dev -- --port 8001 }


