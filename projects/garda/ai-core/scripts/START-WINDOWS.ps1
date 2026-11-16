# Runs capture and API independently. Secrets are process environment only.
param([int]$Port = 8808)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw "First run: .\scripts\INSTALL-WINDOWS.ps1" }
if (-not $env:GARDA_AI_API_KEY -or $env:GARDA_AI_API_KEY.Length -lt 24) {
    throw 'Set $env:GARDA_AI_API_KEY to a random secret with >=24 chars.'
}
if (-not $env:GARDA_CAMERA_PTZ_RTSP) { throw "Set GARDA_CAMERA_PTZ_RTSP in this PowerShell session" }
if (-not $env:GARDA_CAMERA_WIDE_RTSP) { throw "Set GARDA_CAMERA_WIDE_RTSP in this PowerShell session" }
& $Py -m garda_ai check --config config.json
if ($LASTEXITCODE -ne 0) { throw "GARDA config check failed" }
$Api = Start-Process -FilePath $Py -ArgumentList @("-m","garda_ai","api","--listen","127.0.0.1","--port","$Port") -PassThru -NoNewWindow
try {
    Write-Host "GARDA AI API listening locally on 127.0.0.1:$Port"
    Write-Host "Starting RTSP detection (Ctrl+C to stop)..."
    & $Py -m garda_ai run --config config.json
} finally {
    if ($Api -and -not $Api.HasExited) { Stop-Process -Id $Api.Id -Force -ErrorAction SilentlyContinue }
}
