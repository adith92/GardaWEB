param(
    [Parameter(Mandatory=$true)][string]$CameraIp,
    [ValidateSet("check","in","out")][string]$Action = "check",
    [int]$OnvifPort = 8899,
    [double]$Seconds = 0.35,
    [double]$Speed = 0.5
)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root
$Py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) { throw "Run .\scripts\INSTALL-WINDOWS.ps1 first." }
if (-not $env:GARDA_ONVIF_USER) { throw "Set GARDA_ONVIF_USER" }
if ($null -eq $env:GARDA_ONVIF_PASS) { throw "Set GARDA_ONVIF_PASS" }
& $Py -m garda_ai.zoom_cli --host $CameraIp --port $OnvifPort --action $Action --seconds $Seconds --speed $Speed
if ($LASTEXITCODE -ne 0) { throw "PTZ zoom operation failed. Firmware support must be checked." }
