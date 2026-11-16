# Run locally only after the owner confirms the new signing identity.
param([string]$KeyDirectory = (Join-Path $env:LOCALAPPDATA 'GARDA-Signing'))
$ErrorActionPreference = 'Stop'
$keyTool = Get-Command keytool -ErrorAction Stop
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$keyDirectoryFull = [IO.Path]::GetFullPath($KeyDirectory)
if ($keyDirectoryFull.Equals($repoRoot, [StringComparison]::OrdinalIgnoreCase) -or $keyDirectoryFull.StartsWith($repoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Signing material must be outside this repository.'
}
[IO.Directory]::CreateDirectory($keyDirectoryFull) | Out-Null
$keyFile = Join-Path $keyDirectoryFull 'garda-internal.jks'
if (Test-Path -LiteralPath $keyFile) { throw 'Key already exists; reuse it. No overwrite performed.' }
$secure = Read-Host 'New signing password (keep in your password manager)' -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $env:GARDA_NEW_KEY_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    if ($env:GARDA_NEW_KEY_PASSWORD.Length -lt 16) { throw 'Use at least 16 characters.' }
    & $keyTool.Source -genkeypair -keystore $keyFile -storetype JKS -alias garda-internal -keyalg RSA -keysize 3072 -validity 10000 -dname 'CN=GARDA Internal Release' -storepass:env GARDA_NEW_KEY_PASSWORD -keypass:env GARDA_NEW_KEY_PASSWORD
    if ($LASTEXITCODE -ne 0) { throw 'Key generation failed; inspect the target before retrying.' }
    Write-Host "Key created outside Git: $keyFile"
    Write-Host 'Back up this key and password privately. Set GARDA_ANDROID_* variables only for the approved build.'
} finally {
    Remove-Item Env:GARDA_NEW_KEY_PASSWORD -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}
