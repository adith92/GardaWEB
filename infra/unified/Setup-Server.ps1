param(
    [Parameter(Mandatory=$true)][string]$HostIP,
    [string]$RecordingRoot='D:\GARDA-Recordings',
    [string]$DataRoot='D:\GARDA-Server-Data',
    [int]$RetentionDays=1,
    [string]$Python='python'
)
$ErrorActionPreference='Stop'
$work=$PSScriptRoot
$engine=Join-Path $work 'bin\mediamtx.exe'
$manifest=Get-Content -LiteralPath (Join-Path $work 'bin\engine.json') -Raw | ConvertFrom-Json
if ((Get-FileHash -LiteralPath $engine -Algorithm SHA256).Hash.ToLower() -ne $manifest.sha256) { throw 'Engine checksum mismatch' }
Push-Location -LiteralPath $work
try {
    & $Python -m venv .venv
    if ($LASTEXITCODE) { throw 'Python 3.11+ is required' }
    $runtime=Join-Path $work '.venv\Scripts\python.exe'
    & $runtime -m pip install -r requirements-unified.txt 'fast-alpr[onnx]==0.4.0'
    if ($LASTEXITCODE) { throw 'Dependency installation failed' }
    & $runtime -m garda_ai.server provision-ai --data $DataRoot
    if ($LASTEXITCODE) { throw 'Model provisioning failed' }
    & $runtime -m garda_ai.server configure-nvr --data $DataRoot --nvr-binary $engine --recordings-root $RecordingRoot --retention-days $RetentionDays
    if ($LASTEXITCODE) { throw 'NVR configuration failed' }
    & $runtime -m garda_ai.server configure-https --data $DataRoot --host $HostIP --port 8843 --web-root (Join-Path $work 'web')
    if ($LASTEXITCODE) { throw 'HTTPS configuration failed' }
    Write-Host "Ready: https://${HostIP}:8843/workspace"
    Write-Host "Client CA: $DataRoot\tls\site-ca.pem (install only the public certificate on clients)."
    Write-Host "Start: `"$runtime`" -m garda_ai.server serve --data `"$DataRoot`""
    Write-Host 'For startup before Windows login, run Install-WindowsStartup.ps1 as Administrator.'
} finally { Pop-Location }
