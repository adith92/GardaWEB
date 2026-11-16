# Run in PowerShell from anywhere. No admin privileges required.
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher (py) missing. Install trusted Python 3.11-3.13 first."
}
py -3.11 -m venv .venv
$Python = Join-Path $Root ".venv\Scripts\python.exe"
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
& $Python -m pip install -r requirements.txt -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "Dependencies failed to install" }
if (-not (Test-Path "config.json")) {
    Copy-Item "config.example.json" "config.json"
}
Write-Host "GARDA Python installed. Configure RTSP env, model files, API key."
Write-Host "Next: .\scripts\START-WINDOWS.ps1"
