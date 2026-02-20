# Run GitScribe: use venv if present, else create one and install. Pass all args to gitscribe.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$venv = Join-Path $RepoRoot ".venv"
$python = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Creating virtual environment and installing GitScribe..."
    python -m venv $venv
    & $python -m pip install -e . -q
}

& $python -m gitscribe.cli @args
