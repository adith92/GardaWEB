# Download unmodified upstream ClearCam as an isolated GPL-3.0 repository.
# Windows support is NOT claimed: upstream README lists FFmpeg fix needed.
$ErrorActionPreference = 'Stop'
$vendor = Join-Path $PSScriptRoot '..\vendor'
$target = Join-Path $vendor 'clearcam'
New-Item -ItemType Directory -Force -Path $vendor | Out-Null
if (Test-Path $target) { throw "Refusing to overwrite $target" }
git clone https://github.com/roryclear/clearcam.git $target
Push-Location $target
try { git checkout --detach 553be39ba6f20ce055a7418ed54636b32059b4ad }
finally { Pop-Location }
Write-Output 'ClearCam cloned separately; review LICENSE.md and Windows limitations before execution.'
