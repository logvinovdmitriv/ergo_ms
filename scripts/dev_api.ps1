# Powershell dev launcher for Windows
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$apiPath = Join-Path $root 'api'
Set-Location $apiPath

# Pick Python
function Pick-Python {
  if (Get-Command py -ErrorAction SilentlyContinue) { return 'py -3' }
  elseif (Get-Command python -ErrorAction SilentlyContinue) { return 'python' }
  elseif (Get-Command python3 -ErrorAction SilentlyContinue) { return 'python3' }
  else { throw 'Python 3 is required (py/python/python3 not found)' }
}
$py = Pick-Python

if (-not (Test-Path '.venv')) {
  Write-Host "[dev_api] Creating virtualenv .venv"
  iex "$py -m venv .venv"
}

& .\.venv\Scripts\Activate.ps1
iex "$py -m pip install --upgrade pip"

if (Test-Path 'requirements-dev.txt') {
  Write-Host '[dev_api] Installing requirements-dev.txt'
  pip install -r requirements-dev.txt
} elseif (Test-Path 'requirements.txt') {
  Write-Host '[dev_api] Installing requirements.txt'
  pip install -r requirements.txt
} elseif (Test-Path 'pyproject.toml') {
  Write-Host '[dev_api] Installing from pyproject'
  pip install .
}

Write-Host '[dev_api] Starting Django server on :8000'
iex "$py src/manage.py runserver 0.0.0.0:8000"


